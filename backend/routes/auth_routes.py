from flask import Blueprint, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from mysql.connector import Error

from backend.database import get_db_connection

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def prefers_html() -> bool:
    fmt = (request.args.get("format") or "").lower()
    if fmt == "html":
        return True
    if fmt == "json":
        return False
    accept_html = request.accept_mimetypes.get("text/html", 0) if hasattr(request.accept_mimetypes, 'get') else request.accept_mimetypes["text/html"] or 0
    accept_json = request.accept_mimetypes.get("application/json", 0) if hasattr(request.accept_mimetypes, 'get') else request.accept_mimetypes["application/json"] or 0
    return accept_html >= accept_json and not request.is_json


def validate_email(email: str) -> bool:
    return "@" in email and "." in email


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    def render_register_page(error=None, message=None, user=None, status_code=200):
        return render_template(
            "register.html",
            error=error,
            message=message,
            user=user,
            title="Register",
            header_title="Create account",
            header_subtitle="Use the form or POST JSON to /auth/register.",
        ), status_code

    if request.method == "GET":
        return render_register_page()

    wants_html = prefers_html()
    data = request.get_json(silent=True) or request.form

    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""
    confirm_password = data.get("confirm_password") or ""
    full_name = (data.get("full_name") or "").strip()

    if not username or not email or not password or not confirm_password:
        if wants_html:
            return render_register_page(
                error="username, email, password, confirm_password are required.",
                status_code=400,
            )
        return jsonify({
            "success": False,
            "message": "username, email, password, confirm_password are required."
        }), 400

    if not validate_email(email):
        if wants_html:
            return render_register_page(error="Invalid email format.", status_code=400)
        return jsonify({
            "success": False,
            "message": "Invalid email format."
        }), 400

    if password != confirm_password:
        if wants_html:
            return render_register_page(error="Passwords do not match.", status_code=400)
        return jsonify({
            "success": False,
            "message": "Passwords do not match."
        }), 400

    if len(password) < 6:
        if wants_html:
            return render_register_page(
                error="Password must be at least 6 characters.",
                status_code=400,
            )
        return jsonify({
            "success": False,
            "message": "Password must be at least 6 characters."
        }), 400

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT user_id FROM users WHERE username = %s OR email = %s",
            (username, email),
        )
        if cursor.fetchone():
            if wants_html:
                return render_register_page(
                    error="Username or email already exists.",
                    status_code=409,
                )
            return jsonify({
                "success": False,
                "message": "Username or email already exists."
            }), 409

        password_hash = generate_password_hash(password)

        cursor.execute(
            """
            INSERT INTO users (username, email, password_hash, full_name)
            VALUES (%s, %s, %s, %s)
            """,
            (username, email, password_hash, full_name or None),
        )
        conn.commit()
        user_id = cursor.lastrowid

        user_payload = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "full_name": full_name,
        }

        if wants_html:
            return render_register_page(
                message="Registration successful.",
                user=user_payload,
                status_code=201,
            )

        return jsonify({
            "success": True,
            "message": "Registration successful.",
            "user": user_payload,
        }), 201

    except Error as e:
        print("DB Error (register):", e)
        if wants_html:
            return render_register_page(error="Internal server error.", status_code=500)
        return jsonify({
            "success": False,
            "message": "Internal server error."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    def render_login_page(error=None, message=None, user=None, status_code=200):
        return render_template(
            "login.html",
            error=error,
            message=message,
            user=user,
            title="Login",
            header_title="Welcome back",
            header_subtitle="Submit via form or POST JSON to /auth/login.",
        ), status_code

    if request.method == "GET":
        return render_login_page()

    wants_html = prefers_html()
    data = request.get_json(silent=True) or request.form

    username_or_email = (data.get("username_or_email")
                         or data.get("username")
                         or data.get("email")
                         or "").strip()
    password = data.get("password") or ""

    if not username_or_email or not password:
        if wants_html:
            return render_login_page(
                error="username/email and password are required.",
                status_code=400,
            )
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
            (username_or_email, username_or_email),
        )
        user = cursor.fetchone()

        if not user:
            if wants_html:
                return render_login_page(error="User not found.", status_code=404)
            return jsonify({
                "success": False,
                "message": "User not found."
            }), 404

        if not check_password_hash(user["password_hash"], password):
            if wants_html:
                return render_login_page(error="Incorrect password.", status_code=401)
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

        if wants_html:
            return render_login_page(
                message="Login successful.",
                user=user_data,
                status_code=200,
            )

        return jsonify({
            "success": True,
            "message": "Login successful.",
            "user": user_data
        }), 200

    except Error as e:
        print("DB Error (login):", e)
        if wants_html:
            return render_login_page(error="Internal server error.", status_code=500)
        return jsonify({
            "success": False,
            "message": "Internal server error."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
