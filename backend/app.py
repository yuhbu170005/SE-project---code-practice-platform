from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error

from config import DB_CONFIG  # lấy DB_CONFIG từ backend/config.py

app = Flask(__name__)
CORS(app)  # cho phép gọi từ front-end khác port


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def validate_email(email: str) -> bool:
    return "@" in email and "." in email


# =========== REGISTER ===========

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json() or request.form

    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""
    confirm_password = data.get("confirm_password") or ""
    full_name = (data.get("full_name") or "").strip()

    if not username or not email or not password or not confirm_password:
        return jsonify({
            "success": False,
            "message": "username, email, password, confirm_password are required."
        }), 400

    if not validate_email(email):
        return jsonify({
            "success": False,
            "message": "Invalid email format."
        }), 400

    if password != confirm_password:
        return jsonify({
            "success": False,
            "message": "Passwords do not match."
        }), 400

    if len(password) < 6:
        return jsonify({
            "success": False,
            "message": "Password must be at least 6 characters."
        }), 400

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # kiểm tra trùng username hoặc email
        cursor.execute(
            "SELECT user_id FROM users WHERE username = %s OR email = %s",
            (username, email)
        )
        if cursor.fetchone():
            return jsonify({
                "success": False,
                "message": "Username or email already exists."
            }), 409

        # hash password
        password_hash = generate_password_hash(password)

        # insert user
        cursor.execute(
            """
            INSERT INTO users (username, email, password_hash, full_name)
            VALUES (%s, %s, %s, %s)
            """,
            (username, email, password_hash, full_name or None)
        )
        conn.commit()
        user_id = cursor.lastrowid

        return jsonify({
            "success": True,
            "message": "Registration successful.",
            "user": {
                "user_id": user_id,
                "username": username,
                "email": email,
                "full_name": full_name
            }
        }), 201

    except Error as e:
        print("DB Error (register):", e)
        return jsonify({
            "success": False,
            "message": "Internal server error."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =========== LOGIN ===========

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or request.form

    username_or_email = (data.get("username_or_email")
                         or data.get("username")
                         or data.get("email")
                         or "").strip()
    password = data.get("password") or ""

    if not username_or_email or not password:
        return jsonify({
            "success": False,
            "message": "username/email and password are required."
        }), 400

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT user_id, username, email, password_hash, full_name, total_solved
            FROM users
            WHERE username = %s OR email = %s
            LIMIT 1
            """,
            (username_or_email, username_or_email)
        )
        user = cursor.fetchone()

        if not user:
            return jsonify({
                "success": False,
                "message": "User not found."
            }), 404

        if not check_password_hash(user["password_hash"], password):
            return jsonify({
                "success": False,
                "message": "Incorrect password."
            }), 401

        user_data = {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "total_solved": user["total_solved"],
        }

        return jsonify({
            "success": True,
            "message": "Login successful.",
            "user": user_data
        }), 200

    except Error as e:
        print("DB Error (login):", e)
        return jsonify({
            "success": False,
            "message": "Internal server error."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
# =========== SEARCH / LIST PROBLEMS ===========

@app.route("/api/problems", methods=["GET"])
def search_problems():
    """
    Tìm kiếm / liệt kê problems.

    Query params (optional):
      - q: keyword trong title/description
      - difficulty: Easy | Medium | Hard
      - tag: tên tag (vd: "Array")
      - limit: số dòng (default 20)
      - offset: offset (default 0)
    """
    q = (request.args.get("q") or "").strip()
    difficulty = (request.args.get("difficulty") or "").strip()
    tag = (request.args.get("tag") or "").strip()
    try:
        limit = int(request.args.get("limit") or 20)
        offset = int(request.args.get("offset") or 0)
    except ValueError:
        return jsonify({"success": False, "message": "limit/offset must be integers."}), 400

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

        query += " GROUP BY p.problem_id ORDER BY p.created_at DESC LIMIT %s OFFSET %s"
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

        return jsonify({
            "success": True,
            "problems": problems,
            "count": len(problems)
        }), 200

    except Error as e:
        print("DB Error (search_problems):", e)
        return jsonify({"success": False, "message": "Internal server error."}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
# =========== USER SUBMISSION HISTORY ===========

@app.route("/api/users/<int:user_id>/submissions", methods=["GET"])
def get_user_submissions(user_id):
    """
    Lấy lịch sử submissions của 1 user.

    Query params (optional):
      - problem_id: filter theo problem
      - status: filter theo status (vd: Accepted)
      - limit, offset
    """
    problem_id = request.args.get("problem_id")
    status = (request.args.get("status") or "").strip()
    try:
        limit = int(request.args.get("limit") or 50)
        offset = int(request.args.get("offset") or 0)
    except ValueError:
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
                "submitted_at": row["submitted_at"].isoformat() if row["submitted_at"] else None
            })

        return jsonify({
            "success": True,
            "submissions": submissions,
            "count": len(submissions)
        }), 200

    except Error as e:
        print("DB Error (get_user_submissions):", e)
        return jsonify({"success": False, "message": "Internal server error."}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
# =========== RUN APP ===========
if __name__ == "__main__":
    print(">>> backend/app.py has started")  # thêm dòng này
    # dùng port khác 5000 để khỏi đụng app.py SQLite
    app.run(host="0.0.0.0", port=5001, debug=True)
