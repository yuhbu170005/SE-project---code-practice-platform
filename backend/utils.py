from functools import wraps
from flask import session, redirect, url_for, abort


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.view_login"))
        # Cho phép admin theo role, hoặc giữ quyền cho user_id 1 nếu bạn muốn super-admin
        if session.get("role") != "admin" and session.get("user_id") != 1:
            return abort(403)  # trả HTTP 403 Forbidden
        return f(*args, **kwargs)

    return decorated


import requests
from functools import wraps
from flask import session, redirect, url_for, abort

# URL của Piston API
PISTON_API_URL = "https://emkc.org/api/v2/piston/execute"

# Cấu hình: Key nên để chữ thường để dễ map dữ liệu
LANGUAGE_CONFIG = {
    "python": {"language": "python", "version": "3.10.0"},
    "java": {"language": "java", "version": "15.0.2"},
    "cpp": {"language": "cpp", "version": "10.2.0"},
    "c++": {"language": "cpp", "version": "10.2.0"},  # Hỗ trợ cả c++
    "javascript": {"language": "javascript", "version": "18.15.0"},
    "js": {"language": "javascript", "version": "18.15.0"},
}


def run_code_external(code, language, input_data):
    # Chuyển language về chữ thường trước khi get
    lang_key = language.lower() if language else ""
    config = LANGUAGE_CONFIG.get(lang_key)

    if not config:
        return {
            "success": False,
            "error": f"Ngôn ngữ {language} chưa được hỗ trợ trên hệ thống",
        }

    payload = {
        "language": config["language"],
        "version": config["version"],
        "files": [{"content": code}],
        "stdin": input_data or "",
        "run_timeout": 3000,
    }

    try:
        response = requests.post(
            PISTON_API_URL, json=payload, timeout=5
        )  # Thêm timeout cho request

        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Lỗi server Piston (Status: {response.status_code})",
            }

        result = response.json()
        run_stage = result.get("run", {})
        compile_stage = result.get("compile", {})

        # 1. Kiểm tra lỗi biên dịch (C++/Java)
        # Piston trả về compile_stage nếu ngôn ngữ đó cần biên dịch
        if compile_stage and compile_stage.get("code", 0) != 0:
            return {
                "success": False,
                "error": compile_stage.get("stderr", "Compilation Error"),
                "status_label": "Compilation Error",
            }

        # 2. Kiểm tra lỗi Runtime
        if run_stage.get("code", 0) != 0:
            return {
                "success": False,
                "error": run_stage.get("stderr", "Runtime Error"),
                "status_label": "Runtime Error",
            }

        # 3. Thành công
        return {
            "success": True,
            "output": run_stage.get("stdout", "").strip(),
            "status_label": "Accepted",
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"System Error: {str(e)}",
            "status_label": "System Error",
        }
