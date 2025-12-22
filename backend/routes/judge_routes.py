from flask import Blueprint, request, jsonify, session
from backend.database import get_db_connection

# Import hàm chấm bài qua Piston API từ utils
from backend.utils import run_code_external
from backend.services.testcase_service import get_public_test_cases, get_all_test_cases
from backend.services.submission_service import save_submission_to_db

judge_bp = Blueprint("judge", __name__)


# --- API 1: RUN CODE (Chấm thử - Trả về chi tiết từng case) ---
@judge_bp.route("/api/run", methods=["POST"])
def run_code():
    data = request.json
    code = data.get("code")
    problem_id = data.get("problem_id")
    # Lấy ngôn ngữ (nếu frontend không gửi thì mặc định Python)
    language = data.get("language", "Python")

    if not code or not problem_id:
        return (
            jsonify(
                {
                    "final_status": "Error",
                    "message": "Thiếu dữ liệu code hoặc problem_id",
                }
            ),
            400,
        )

    test_cases = get_public_test_cases(problem_id)

    if not test_cases:
        return jsonify(
            {"final_status": "Error", "message": "Chưa có test case nào cho bài này."}
        )

    results = []
    final_status = "Accepted"

    for i, case in enumerate(test_cases):
        # GỌI HÀM CHẤM BÀI TỪ UTILS (PISTON)
        res = run_code_external(code, language, case["input"])

        result_item = {"case": i + 1, "status": "Passed"}

        # Chuẩn hóa output để so sánh (xóa khoảng trắng thừa và đồng bộ xuống dòng)
        actual_output = res.get("output", "").replace("\r\n", "\n").strip()
        expected_output = case["expected_output"].replace("\r\n", "\n").strip()

        # 1. Nếu code bị lỗi (Compile Error, Runtime Error)
        if not res["success"]:
            # Lấy status từ utils trả về (VD: Runtime Error)
            status = res.get("status_label", "Runtime Error")

            result_item["status"] = status
            result_item["error"] = res["error"]
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


# --- API 2: SUBMIT CODE (Chấm chính thức - Lưu kết quả vào DB) ---
@judge_bp.route("/api/submit", methods=["POST"])
def submit_code():
    user_id = session.get("user_id", 1)  # Mặc định 1 nếu chưa login

    data = request.get_json(silent=True) or request.form
    code = data.get("code")
    problem_id = data.get("problem_id")
    language = data.get("language", "Python")

    if not code or not problem_id:
        return (
            jsonify({"status": "error", "message": "Missing code or problem_id"}),
            400,
        )

    test_cases = get_all_test_cases(problem_id)

    final_status = "Accepted"
    failed_case_index = 0

    # Biến lưu lỗi để debug (nếu bạn muốn lưu vào DB sau này)
    error_message_log = ""

    for i, case in enumerate(test_cases):
        # GỌI PISTON API
        res = run_code_external(code, language, case["input"])

        actual_output = res.get("output", "").replace("\r\n", "\n").strip()
        expected_output = case["expected_output"].replace("\r\n", "\n").strip()

        # Case lỗi Runtime/Compile
        if not res["success"]:
            final_status = res.get("status_label", "Runtime Error")
            error_message_log = res.get("error", "")
            failed_case_index = i + 1
            break

        # Case sai kết quả
        if actual_output != expected_output:
            final_status = "Wrong Answer"
            failed_case_index = i + 1
            break

    save_success = save_submission_to_db(
        user_id, problem_id, code, language, final_status, error_message_log
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
            "failed_case": failed_case_index,
        }
    )
