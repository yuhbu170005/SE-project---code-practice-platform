from flask import Blueprint, request, jsonify, render_template
from mysql.connector import Error

from backend.database import get_db_connection

problem_bp = Blueprint("problems", __name__, url_prefix="/api")


def _query_problems(q: str, difficulty: str, tag: str, limit: int | None, offset: int | None):
    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                p.problem_id,
                p.title,
                p.slug,
                p.difficulty,
                GROUP_CONCAT(DISTINCT t.tag_name ORDER BY t.tag_name) AS tags
            FROM problems p
            LEFT JOIN problem_tags pt ON p.problem_id = pt.problem_id
            LEFT JOIN tags t ON pt.tag_id = t.tag_id
        """

        where_clauses = []
        params = []

        if q:
            where_clauses.append("(p.title LIKE %s OR p.description LIKE %s)")
            pattern = f"%{q}%"
            params.extend([pattern, pattern])

        if difficulty:
            where_clauses.append("p.difficulty = %s")
            params.append(difficulty)

        if tag:
            where_clauses.append("t.tag_name = %s")
            params.append(tag)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += " GROUP BY p.problem_id ORDER BY p.created_at DESC"
        if limit is not None and offset is not None:
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        problems = []
        for row in rows:
            tags_str = row.get("tags")
            problems.append({
                "problem_id": row["problem_id"],
                "title": row["title"],
                "slug": row["slug"],
                "difficulty": row["difficulty"],
                "tags": tags_str.split(",") if tags_str else []
            })
        return problems
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@problem_bp.route("/problems", methods=["GET"])
def search_problems():
    """Search and list problems with filters"""
    q = (request.args.get("q") or "").strip()
    difficulty = (request.args.get("difficulty") or "").strip()
    tag = (request.args.get("tag") or "").strip()
    try:
        limit = int(request.args.get("limit") or 20)
        offset = int(request.args.get("offset") or 0)
    except ValueError:
        return jsonify({"success": False, "message": "limit/offset must be integers."}), 400

    try:
        problems = _query_problems(q, difficulty, tag, limit, offset)
        return jsonify({
            "success": True,
            "problems": problems,
            "count": len(problems)
        }), 200
    except Error as e:
        print("DB Error (search_problems):", e)
        return jsonify({"success": False, "message": "Internal server error."}), 500


@problem_bp.route("/problems/page", methods=["GET"])
def problems_page():
    """Render HTML page with problems"""
    q = (request.args.get("q") or "").strip()
    difficulty = (request.args.get("difficulty") or "").strip()
    tag = (request.args.get("tag") or "").strip()

    try:
        problems = _query_problems(q, difficulty, tag, limit=None, offset=None)
        return render_template("problems.html", problems=problems)
    except Error as e:
        print("DB Error (problems_page):", e)
        return "Internal server error", 500
