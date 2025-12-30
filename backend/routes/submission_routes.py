from flask import Blueprint, redirect, render_template, session, url_for, request
from backend.services.submission_service import (
    get_user_submissions,
    get_submission_detail,
)
from backend.services.testcase_service import get_all_test_cases
import math

submission_bp = Blueprint("submission", __name__)


@submission_bp.route("/submissions")
def list_submissions():
    """Hiển thị danh sách submissions của user hiện tại với pagination"""
    if "user_id" not in session:
        return redirect(url_for("auth.view_login"))

    user_id = session["user_id"]
    page = request.args.get("page", 1, type=int)
    per_page = 10

    submissions, total_count = get_user_submissions(user_id, page, per_page)

    if submissions is None:
        return (
            render_template(
                "submissions.html", submissions=[], error="Database connection failed"
            ),
            500,
        )

    # Calculate pagination info
    total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1
    pagination = {
        "page": page,
        "per_page": per_page,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages,
    }

    return render_template(
        "submissions.html", submissions=submissions, pagination=pagination
    )


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

    # Get only SAMPLE test cases for display
    from backend.services.testcase_service import get_sample_test_cases

    sample_cases = get_sample_test_cases(submission["problem_id"])

    return render_template(
        "submission_result.html", submission=submission, test_cases=sample_cases
    )
