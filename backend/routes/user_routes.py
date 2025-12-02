from flask import Blueprint, request, jsonify, render_template
from mysql.connector import Error

from backend.database import get_db_connection

user_bp = Blueprint("users", __name__, url_prefix="/api")


def prefers_html() -> bool:
    fmt = (request.args.get("format") or "").lower()
    if fmt == "html":
        return True
    if fmt == "json":
        return False
    accept_html = request.accept_mimetypes.get("text/html", 0)
    accept_json = request.accept_mimetypes.get("application/json", 0)
    return accept_html >= accept_json and not request.is_json


@user_bp.route("/users/<int:user_id>/submissions", methods=["GET"])
def get_user_submissions(user_id):
    """Fetch submission history for a user"""
    wants_html = prefers_html()

    problem_id = request.args.get("problem_id")
    status = (request.args.get("status") or "").strip()
    try:
        limit = int(request.args.get("limit") or 50)
        offset = int(request.args.get("offset") or 0)
    except ValueError:
        if wants_html:
            return render_template(
                "submissions.html",
                user_id=user_id,
                submissions=[],
                count=0,
                error="limit/offset must be integers.",
                title="Submissions",
                header_title="User submissions",
            ), 400
        return jsonify({"success": False, "message": "limit/offset must be integers."}), 400

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                s.submission_id,
                s.problem_id,
                p.title AS problem_title,
                s.language,
                s.status,
                s.execution_time,
                s.memory_used,
                s.test_cases_passed,
                s.total_test_cases,
                s.submitted_at
            FROM submissions s
            JOIN problems p ON s.problem_id = p.problem_id
            WHERE s.user_id = %s
        """
        params = [user_id]

        if problem_id:
            query += " AND s.problem_id = %s"
            params.append(int(problem_id))

        if status:
            query += " AND s.status = %s"
            params.append(status)

        query += " ORDER BY s.submitted_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        submissions = []
        for row in rows:
            submitted_at = row["submitted_at"].isoformat() if row["submitted_at"] else None
            submissions.append({
                "submission_id": row["submission_id"],
                "problem_id": row["problem_id"],
                "problem_title": row["problem_title"],
                "language": row["language"],
                "status": row["status"],
                "execution_time": row["execution_time"],
                "memory_used": row["memory_used"],
                "test_cases_passed": row["test_cases_passed"],
                "total_test_cases": row["total_test_cases"],
                "submitted_at": submitted_at
            })

        if wants_html:
            return render_template(
                "submissions.html",
                user_id=user_id,
                submissions=submissions,
                count=len(submissions),
                title="Submissions",
                header_title="User submissions",
            )

        return jsonify({
            "success": True,
            "submissions": submissions,
            "count": len(submissions)
        }), 200

    except Error as e:
        print("DB Error (get_user_submissions):", e)
        if wants_html:
            return render_template(
                "submissions.html",
                user_id=user_id,
                submissions=[],
                count=0,
                error="Internal server error.",
                title="Submissions",
                header_title="User submissions",
            ), 500
        return jsonify({"success": False, "message": "Internal server error."}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
