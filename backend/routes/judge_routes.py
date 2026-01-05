from flask import Blueprint, request, jsonify, session
from backend.utils import run_code_external, wrap_user_code
from backend.services.testcase_service import get_public_test_cases, get_all_test_cases
from backend.services.submission_service import save_submission_to_db
from backend.services.problem_service import get_problem_by_id
from backend.validators import validate_code_submission

judge_bp = Blueprint("judge", __name__)


@judge_bp.route("/api/run", methods=["POST"])
def run_code():
    """Run code against public test cases (for testing)"""
    data = request.json
    code = data.get("code")
    problem_id = data.get("problem_id")
    language = data.get("language", "python")

    # Validate input
    is_valid, errors, normalized = validate_code_submission(code, language, problem_id)

    if not is_valid:
        first_error = next(iter(errors.values()))
        return (
            jsonify(
                {"final_status": "Error", "message": first_error, "errors": errors}
            ),
            400,
        )

    # Use normalized values
    code = normalized["code"]
    language = normalized["language"]
    problem_id = normalized["problem_id"]

    # Get problem to check for wrapper_template
    problem = get_problem_by_id(problem_id)
    if not problem:
        return jsonify({"final_status": "Error", "message": "Problem not found"}), 404

    # Wrap user code with template if available
    wrapper_template = problem.get("wrapper_template")
    if wrapper_template:
        code = wrap_user_code(code, wrapper_template, language)

    # Get test cases
    test_cases = get_public_test_cases(problem_id)

    if not test_cases:
        return jsonify(
            {"final_status": "Error", "message": "Chưa có test case nào cho bài này."}
        )

    results = []
    final_status = "Accepted"

    for i, case in enumerate(test_cases):
        # Run code using Piston API
        res = run_code_external(code, language, case["input"])

        result_item = {"case": i + 1, "status": "Passed"}

        # Chuẩn hóa output để so sánh (xóa khoảng trắng thừa và đồng bộ xuống dòng)
        actual_output = res.get("output", "").replace("\r\n", "\n").strip()
        expected_output = case["expected_output"].replace("\r\n", "\n").strip()

        # 1. Nếu code bị lỗi (Compile Error, Runtime Error, hoặc Timeout)
        if not res["success"]:
            # Lấy status từ utils trả về (VD: Runtime Error, Time Limit Exceeded)
            status = res.get("status_label", "Runtime Error")

            result_item["status"] = status
            result_item["error"] = res["error"]
            result_item["input"] = case["input"]
            result_item["expected"] = expected_output
            result_item["actual"] = actual_output if actual_output else "N/A"
            final_status = status

        # 2. Nếu code chạy xong nhưng ra kết quả sai
        elif actual_output != expected_output:
            status = "Wrong Answer"
            result_item["status"] = status
            result_item["input"] = case["input"]
            result_item["expected"] = expected_output
            result_item["actual"] = actual_output
            final_status = status

        results.append(result_item)

    return jsonify({"final_status": final_status, "results": results})


@judge_bp.route("/api/submit", methods=["POST"])
def submit_code():
    """Submit code for official judging and save to database"""
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"status": "error", "message": "User not authenticated"}), 401

    data = request.get_json(silent=True) or request.form
    code = data.get("code")
    problem_id = data.get("problem_id")
    language = data.get("language", "python")

    # Validate input
    is_valid, errors, normalized = validate_code_submission(code, language, problem_id)

    if not is_valid:
        first_error = next(iter(errors.values()))
        return (
            jsonify({"status": "error", "message": first_error, "errors": errors}),
            400,
        )

    # Use normalized values
    code = normalized["code"]
    language = normalized["language"]
    problem_id = normalized["problem_id"]

    # Get problem to check time and memory limits
    problem = get_problem_by_id(problem_id)
    if not problem:
        return (
            jsonify({"status": "error", "message": "Problem not found"}),
            404,
        )

    time_limit_ms = problem.get("time_limit", 1000)  # Default 1000ms
    memory_limit_mb = problem.get("memory_limit", 256)  # Default 256MB

    # Wrap user code with template if available
    wrapper_template = problem.get("wrapper_template")
    executable_code = code  # Keep original for saving to DB
    if wrapper_template:
        executable_code = wrap_user_code(code, wrapper_template, language)

    # Thêm buffer cho network latency (Piston API round-trip time)
    # Actual check = time_limit + 2000ms buffer
    actual_time_limit = time_limit_ms + 2000  # Thêm 2s cho network

    # Get all test cases
    test_cases = get_all_test_cases(problem_id)

    if not test_cases:
        return (
            jsonify(
                {"status": "error", "message": "No test cases found for this problem"}
            ),
            404,
        )

    final_status = "Accepted"
    failed_case_index = 0
    failed_case_detail = None  # Lưu chi tiết test case fail đầu tiên
    test_cases_passed = 0
    total_test_cases = len(test_cases)

    # Track execution time and memory (max value from all test cases)
    max_execution_time = 0
    max_code_execution_time = 0  # Thời gian code thực tế (đã trừ network)
    max_memory_used = 0

    for i, case in enumerate(test_cases):
        # Run code using Piston API (use wrapped/executable code)
        res = run_code_external(executable_code, language, case["input"])

        actual_output = res.get("output", "").replace("\r\n", "\n").strip()
        expected_output = case["expected_output"].replace("\r\n", "\n").strip()

        # Track execution time (total time - dùng cho TLE check)
        exec_time = res.get("execution_time")
        if exec_time is not None:
            max_execution_time = max(max_execution_time, exec_time)

        # Track code execution time (đã trừ network - dùng cho display)
        code_exec_time = res.get("code_execution_time")
        if code_exec_time is not None:
            max_code_execution_time = max(max_code_execution_time, code_exec_time)

        memory = res.get("memory_used")
        if memory is not None:
            max_memory_used = max(max_memory_used, memory)

        # Case lỗi Runtime/Compile - Break ngay vì code không chạy được
        # NHƯNG nếu là timeout thì KHÔNG break, xử lý như TLE bên dưới
        if not res["success"] and not res.get("is_timeout", False):
            final_status = res.get("status_label", "Runtime Error")
            if failed_case_index == 0:  # Lưu test case đầu tiên fail
                failed_case_index = i + 1
                failed_case_detail = {
                    "input": case["input"],
                    "expected_output": expected_output,
                    "actual_output": actual_output if actual_output else "N/A",
                    "error": res.get("error", "Unknown error"),
                }
            break  # Break vì code lỗi, không thể chạy tiếp

        # Nếu là timeout, xử lý như TLE (không break, set status và tiếp tục)
        if res.get("is_timeout", False):
            if final_status == "Accepted":
                final_status = "Time Limit Exceeded"
            if failed_case_index == 0:
                failed_case_index = i + 1
                failed_case_detail = {
                    "input": case["input"],
                    "error": res.get("error", "Time Limit Exceeded"),
                }
            # Không break - tiếp tục chạy test case khác
            continue

        # Check Time Limit Exceeded (dùng code_execution_time thay vì total time)
        # code_execution_time đã trừ network latency, chính xác hơn
        if code_exec_time and code_exec_time > time_limit_ms:
            if final_status == "Accepted":  # Chỉ đổi status nếu chưa có lỗi khác
                final_status = "Time Limit Exceeded"
            if failed_case_index == 0:
                failed_case_index = i + 1
                failed_case_detail = {
                    "input": case["input"],
                    "time_used": code_exec_time,
                    "time_limit": time_limit_ms,
                }
            # Không break - tiếp tục chạy các test case khác

        # Check Memory Limit Exceeded (convert MB to KB for comparison)
        elif memory and memory > (memory_limit_mb * 1024):
            if final_status == "Accepted":
                final_status = "Memory Limit Exceeded"
            if failed_case_index == 0:
                failed_case_index = i + 1
                failed_case_detail = {
                    "input": case["input"],
                    "memory_used": memory / 1024,  # Convert to MB
                    "memory_limit": memory_limit_mb,
                }
            # Không break - tiếp tục chạy các test case khác

        # Case sai kết quả
        elif actual_output != expected_output:
            if final_status == "Accepted":
                final_status = "Wrong Answer"
            if failed_case_index == 0:
                failed_case_index = i + 1
                failed_case_detail = {
                    "input": case["input"],
                    "expected_output": expected_output,
                    "actual_output": actual_output,
                }
            # Không break - tiếp tục chạy các test case khác để đếm số test pass
        else:
            # Case đúng - tăng số test pass
            test_cases_passed += 1

    # Save to database (lưu total execution time)
    # Lưu chỉ failed test case đầu tiên (dạng array 1 item)
    test_case_results_to_save = None
    if final_status == "Wrong Answer" and failed_case_detail:
        test_case_results_to_save = [failed_case_detail]

    save_success, submission_id = save_submission_to_db(
        user_id=user_id,
        problem_id=problem_id,
        code=code,
        language=language,
        status=final_status,
        test_cases_passed=test_cases_passed,
        total_test_cases=total_test_cases,
        execution_time=(
            max_code_execution_time if max_code_execution_time > 0 else None
        ),  # Lưu code time
        memory_used=max_memory_used if max_memory_used > 0 else None,
        test_case_results=test_case_results_to_save,
    )
    if not save_success:
        return (
            jsonify({"status": "error", "message": "Lỗi khi lưu kết quả vào DB"}),
            500,
        )

    return jsonify(
        {
            "status": "success",
            "final_status": final_status,
            "failed_case_detail": failed_case_detail,  # Chi tiết case fail
            "test_cases_passed": test_cases_passed,
            "total_test_cases": total_test_cases,
            "execution_time": (
                max_code_execution_time if max_code_execution_time > 0 else None
            ),  # Trả về code time
            "memory_used": max_memory_used if max_memory_used > 0 else None,
            "submission_id": submission_id,
        }
    )
