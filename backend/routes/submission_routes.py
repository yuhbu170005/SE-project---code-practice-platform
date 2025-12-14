# 1. Tạo Blueprint
from flask import Blueprint, redirect, render_template, session, url_for

from backend.database import get_db_connection


submission_bp = Blueprint("submission", __name__)
# ==================== SUBMISSIONS ROUTES ====================


@submission_bp.route("/submissions")
def list_submissions():
    """Hiển thị danh sách submissions của user hiện tại"""
    if "user_id" not in session:
        return redirect(url_for("auth.view_login"))

    user_id = session["user_id"]
    conn = get_db_connection()
    if not conn:
        return (
            render_template(
                "submissions.html", submissions=[], error="Database connection failed"
            ),
            500,
        )

    cursor = conn.cursor(dictionary=True)

    # Lấy danh sách submissions kèm tên problem
    cursor.execute(
        """
        SELECT 
            s.submission_id,
            s.user_id,
            s.problem_id,
            p.title,
            p.slug,
            s.status,
            s.submitted_at,
            s.code
        FROM submissions s
        JOIN problems p ON s.problem_id = p.problem_id
        WHERE s.user_id = %s
        ORDER BY s.submitted_at DESC
    """,
        (user_id,),
    )

    submissions = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("submissions.html", submissions=submissions)


@submission_bp.route("/submission/<int:submission_id>")
def view_submission(submission_id):
    """Xem chi tiết một submission"""
    if "user_id" not in session:
        return redirect(url_for("auth.view_login"))

    user_id = session["user_id"]
    conn = get_db_connection()
    if not conn:
        return "Database connection failed", 500

    cursor = conn.cursor(dictionary=True)

    # Lấy thông tin submission
    cursor.execute(
        """
        SELECT 
            s.submission_id,
            s.user_id,
            s.problem_id,
            s.code,
            s.status,
            s.submitted_at,
            p.title,
            p.slug,
            u.username
        FROM submissions s
        JOIN problems p ON s.problem_id = p.problem_id
        JOIN users u ON s.user_id = u.user_id
        WHERE s.submission_id = %s
    """,
        (submission_id,),
    )

    submission = cursor.fetchone()

    if not submission or (
        submission["user_id"] != user_id and user_id != 1
    ):  # user_id 1 là admin
        cursor.close()
        conn.close()
        return "Submission not found or access denied", 404

    # Lấy danh sách test cases (chỉ sample cases)
    cursor.execute(
        """
        SELECT test_case_id, input, expected_output, is_hidden
        FROM test_cases
        WHERE problem_id = %s
        ORDER BY test_case_id ASC
    """,
        (submission["problem_id"],),
    )

    test_cases = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        "submission_result.html", submission=submission, test_cases=test_cases
    )
