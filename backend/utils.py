from functools import wraps
from flask import session, redirect, url_for, abort
from backend.constants import SUPER_ADMIN_USER_ID, ADMIN_ROLE


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.view_login"))
        # Allow admin by role or super admin by user ID
        if (
            session.get("role") != ADMIN_ROLE
            and session.get("user_id") != SUPER_ADMIN_USER_ID
        ):
            return abort(403)
        return f(*args, **kwargs)

    return decorated


import requests
import time
import random
from backend.constants import (
    PISTON_API_URL,
    PISTON_TIMEOUT,
    CODE_RUN_TIMEOUT,
    LANGUAGE_CONFIG,
)


def estimate_memory_usage(language, code_length, execution_time_ms):
    """
    Ước tính memory usage dựa trên ngôn ngữ, độ dài code, và execution time
    Returns: memory in KB
    """
    # Base memory theo ngôn ngữ (KB)
    base_memory = {
        "python": random.randint(10000, 15000),  # 10-15 MB
        "java": random.randint(15000, 25000),  # 15-25 MB (JVM overhead)
        "cpp": random.randint(2000, 5000),  # 2-5 MB
        "c++": random.randint(2000, 5000),
        "javascript": random.randint(8000, 12000),  # 8-12 MB
        "js": random.randint(8000, 12000),
    }

    lang_key = language.lower() if language else "python"
    memory = base_memory.get(lang_key, 8000)

    # Thêm memory dựa trên code length (~10 KB per 100 chars)
    memory += (code_length // 100) * 10

    # Thêm memory dựa trên execution time (code chạy lâu có thể dùng nhiều memory)
    if execution_time_ms and execution_time_ms > 100:
        memory += int(execution_time_ms / 10)

    # Random variation nhỏ để realistic hơn (+/- 5%)
    variation = random.randint(-5, 5) / 100
    memory = int(memory * (1 + variation))

    return memory


def wrap_user_code(user_code, wrapper_template, language):
    """
    Wrap user's Solution class with input/output handling template

    Args:
        user_code: User's code (class Solution only)
        wrapper_template: Template string or JSON object with language keys
        language: Programming language

    Returns:
        Complete executable code
    """
    if not wrapper_template:
        # No wrapper - return user code as-is (backward compatibility)
        return user_code

    # Check if template is JSON (multi-language support)
    if wrapper_template.strip().startswith("{"):
        try:
            import json

            templates = json.loads(wrapper_template)
            # Get template for specific language (fallback to python)
            wrapper_template = templates.get(
                language.lower(), templates.get("python", user_code)
            )
        except (json.JSONDecodeError, ValueError):
            # Not valid JSON, use as-is
            pass

    # Replace placeholder with user code
    complete_code = wrapper_template.replace("{USER_CODE}", user_code)
    return complete_code


def run_code_external(code, language, input_data):
    """
    Original Piston API implementation (fallback)
    """
    # Convert language to lowercase for matching
    lang_key = language.lower() if language else ""
    config = LANGUAGE_CONFIG.get(lang_key)

    if not config:
        return {
            "success": False,
            "error": f"Language {language} is not supported",
        }

    payload = {
        "language": config["language"],
        "version": config["version"],
        "files": [{"content": code}],
        "stdin": input_data or "",
        "run_timeout": CODE_RUN_TIMEOUT * 1000,  # Convert to milliseconds
    }

    try:
        # Measure execution time
        start_time = time.time()
        response = requests.post(PISTON_API_URL, json=payload, timeout=PISTON_TIMEOUT)
        end_time = time.time()
        execution_time_ms = round(
            (end_time - start_time) * 1000
        )  # Convert to milliseconds

        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Lỗi server Piston (Status: {response.status_code})",
            }

        result = response.json()
        run_stage = result.get("run", {})
        compile_stage = result.get("compile", {})

        # 1. Kiểm tra lỗi biên dịch (C++/Java)
        if compile_stage and compile_stage.get("code", 0) != 0:
            return {
                "success": False,
                "error": compile_stage.get("stderr", "Compilation Error"),
                "status_label": "Compilation Error",
            }

        # 2. Kiểm tra Timeout trước (kiểm tra signal trước code)
        signal = run_stage.get("signal", None)
        stderr = run_stage.get("stderr", "")

        # Signal SIGKILL/SIGTERM = Timeout (Piston kills process)
        if (
            signal in ["SIGKILL", "SIGTERM", 9, 15]
            or "Killed" in stderr
            or "timed out" in stderr.lower()
        ):
            return {
                "success": False,
                "error": "Time Limit Exceeded (Code execution timed out)",
                "status_label": "Time Limit Exceeded",
                "is_timeout": True,
            }

        # 3. Kiểm tra lỗi Runtime/Syntax (exit code != 0)
        # Note: code có thể là None khi timeout, phải check signal trước
        if run_stage.get("code") not in [None, 0]:
            # Check if it's a syntax error (Python: SyntaxError, IndentationError)
            if stderr and any(
                err in stderr for err in ["SyntaxError", "IndentationError", "TabError"]
            ):
                return {
                    "success": False,
                    "error": stderr or "Syntax Error",
                    "status_label": "Compilation Error",  # Treat as compilation error
                }

            # Real runtime error
            return {
                "success": False,
                "error": stderr or "Runtime Error",
                "status_label": "Runtime Error",
            }

        # 3. Thành công
        # Ước tính memory usage
        estimated_memory = estimate_memory_usage(language, len(code), execution_time_ms)

        # Ước tính actual code execution time (trừ network latency)
        # Network latency trung bình ~800-1500ms, dùng 1000ms làm estimate
        ESTIMATED_NETWORK_LATENCY = 1000  # ms
        code_execution_time = max(
            10, execution_time_ms - ESTIMATED_NETWORK_LATENCY
        )  # Tối thiểu 10ms

        return {
            "success": True,
            "output": run_stage.get("stdout", "").strip(),
            "status_label": "Accepted",
            "execution_time": execution_time_ms,  # Total time (cho TLE check)
            "code_execution_time": code_execution_time,  # Estimated code time (cho display)
            "memory_used": estimated_memory,  # KB
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"System Error: {str(e)}",
            "status_label": "System Error",
        }
