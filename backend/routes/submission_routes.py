from flask import Blueprint, redirect, render_template, session, url_for
from backend.services.submission_service import (
    get_user_submissions,
    get_submission_detail,
)
from backend.services.testcase_service import get_all_test_cases

submission_bp = Blueprint("submission", __name__)


@submission_bp.route("/submissions")
def list_submissions():
    """Hiển thị danh sách submissions của user hiện tại"""
    if "user_id" not in session:
        return redirect(url_for("auth.view_login"))

    user_id = session["user_id"]
    submissions = get_user_submissions(user_id)

    if submissions is None:
        return (
            render_template(
                "submissions.html", submissions=[], error="Database connection failed"
            ),
            500,
        )

    return render_template("submissions.html", submissions=submissions)


@submission_bp.route("/submission/<int:submission_id>")
def view_submission(submission_id):
    """Xem chi tiết một submission"""
    if "user_id" not in session:
        return redirect(url_for("auth.view_login"))

    user_id = session["user_id"]
    submission = get_submission_detail(submission_id)

    if not submission:
        return "Database connection failed or submission not found", 500

    # Check access permission
    if submission["user_id"] != user_id and user_id != 1:
        return "Submission not found or access denied", 404

    # Get test cases for the problem
    test_cases = get_all_test_cases(submission["problem_id"])

    return render_template(
        "submission_result.html", submission=submission, test_cases=test_cases
    )
