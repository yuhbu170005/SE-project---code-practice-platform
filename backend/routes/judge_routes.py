from flask import Blueprint, request, jsonify, session
import sys
import subprocess
from backend.database import get_db_connection

judge_bp = Blueprint("judge", __name__)


# --- HÀM HỖ TRỢ CHẠY CODE ---
def execute_python_code(code, input_data):
    """
    Hàm này chạy code Python với input đầu vào và trả về output/lỗi.
    """
    try:
        # Chạy process python, timeout 2 giây để tránh treo máy
        process = subprocess.run(
            [sys.executable, "-c", code],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=2,
        )
        return {
            "success": process.returncode == 0,
            "output": process.stdout.strip(),  # Xóa khoảng trắng thừa đầu đuôi
            "error": process.stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Time Limit Exceeded"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# --- API 1: RUN CODE (Chấm thử - Trả về chi tiết từng case) ---
@judge_bp.route("/api/run", methods=["POST"])
def run_code():
    data = request.json
    code = data.get("code")
    problem_id = data.get("problem_id")

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

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # [SỬA QUAN TRỌNG]: Dùng đúng tên cột 'test_case_id'
    cursor.execute(
        """
        SELECT test_case_id, input, expected_output, is_hidden 
        FROM test_cases 
        WHERE problem_id = %s AND is_hidden = FALSE
    """,
        (problem_id,),
    )

    test_cases = cursor.fetchall()
    conn.close()

    if not test_cases:
        return jsonify(
            {"final_status": "Error", "message": "Chưa có test case nào cho bài này."}
        )

    results = []
    final_status = "Accepted"

    for i, case in enumerate(test_cases):
        # Chạy code
        res = execute_python_code(code, case["input"])

        result_item = {"case": i + 1, "status": "Passed"}

        # 1. Nếu code bị lỗi (Runtime/Timeout)
        if not res["success"]:
            if res["error"] == "Time Limit Exceeded":
                status = "Time Limit Exceeded"
            else:
                status = "Runtime Error"

            result_item["status"] = status
            result_item["error"] = res["error"]
            final_status = status  # Cập nhật trạng thái tổng

        # 2. Nếu code chạy xong nhưng ra kết quả sai
        elif res["output"] != case["expected_output"].strip():
            status = "Wrong Answer"
            result_item["status"] = status
            result_item["input"] = case["input"]
            result_item["expected"] = case["expected_output"]
            result_item["actual"] = res["output"]
            final_status = status

        results.append(result_item)

    return jsonify({"final_status": final_status, "results": results})


# --- API 2: SUBMIT CODE (Chấm chính thức - Lưu kết quả vào DB) ---
@judge_bp.route("/api/submit", methods=["POST"])
def submit_code():
    # Lấy user từ session (fallback = 1 nếu chưa login)
    user_id = session.get("user_id", 1)

    data = request.get_json(silent=True) or request.form
    code = data.get("code")
    problem_id = data.get("problem_id")
    language = data.get("language", "Python")

    if not code or not problem_id:
        return (
            jsonify({"status": "error", "message": "Missing code or problem_id"}),
            400,
        )

    conn = get_db_connection()
    if not conn:
        return (
            jsonify({"status": "error", "message": "Database connection error."}),
            500,
        )

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT input, expected_output 
            FROM test_cases 
            WHERE problem_id = %s 
            ORDER BY test_case_id ASC
            """,
            (problem_id,),
        )
        test_cases = cursor.fetchall()
    except Exception as e:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass
        return (
            jsonify(
                {"status": "error", "message": f"DB error when reading test cases: {e}"}
            ),
            500,
        )

    final_status = "Accepted"
    failed_case_index = 0

    for i, case in enumerate(test_cases):
        res = execute_python_code(code, case["input"])

        if not res["success"]:
            final_status = (
                "Time Limit Exceeded"
                if res["error"] == "Time Limit Exceeded"
                else "Runtime Error"
            )
            failed_case_index = i + 1
            break

        if res["output"] != case["expected_output"].strip():
            final_status = "Wrong Answer"
            failed_case_index = i + 1
            break

    # Lưu submission (bổ sung language)
    try:
        cursor.execute(
            "INSERT INTO submissions (user_id, problem_id, code, language, status) VALUES (%s, %s, %s, %s, %s)",
            (user_id, problem_id, code, language, final_status),
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return (
            jsonify({"status": "error", "message": f"Failed to save submission: {e}"}),
            500,
        )

    cursor.close()
    conn.close()

    return jsonify(
        {
            "status": "success",
            "final_status": final_status,
            "failed_case": failed_case_index,
        }
    )
