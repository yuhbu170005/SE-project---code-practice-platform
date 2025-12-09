from flask import (
    Blueprint,
    redirect,
    request,
    jsonify,
    render_template,
    session,
    url_for,
)
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database import get_db_connection
import re

auth_bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


@auth_bp.route("/login", methods=["GET"])
def view_login():
    return render_template("login.html")


@auth_bp.route("/signup", methods=["GET"])
def view_signup():
    return render_template("signup.html")


@auth_bp.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json(silent=True) or request.form

    # Trim inputs
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""
    full_name = (data.get("full_name") or "").strip()

    # Basic validation
    if not username or not password or not email:
        return jsonify({"success": False, "message": "Missing required fields!"}), 400

    if not EMAIL_RE.match(email):
        return jsonify({"success": False, "message": "Invalid email format."}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection error."}), 500

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)

        # Check username or email already exists
        cursor.execute(
            "SELECT user_id FROM users WHERE username = %s OR email = %s",
            (username, email),
        )
        if cursor.fetchone():
            return (
                jsonify(
                    {"success": False, "message": "Username or email already exists."}
                ),
                409,
            )

        # Hash password and insert
        hashed_pw = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, full_name) VALUES (%s, %s, %s, %s)",
            (username, email, hashed_pw, full_name),
        )
        conn.commit()

        return jsonify({"success": True, "message": "Registration successful!"}), 201

    except Exception as e:
        # Optionally log e
        try:
            conn.rollback()
        except Exception:
            pass
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        conn.close()


@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or request.form
    username_or_email = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username_or_email or not password:
        return (
            jsonify(
                {"success": False, "message": "Missing username/email or password."}
            ),
            400,
        )

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection error."}), 500

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT user_id, username, password_hash, role FROM users WHERE username = %s OR email = %s",
            (username_or_email, username_or_email),
        )
        user = cursor.fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["role"] = user.get("role", "user")
            print("DEBUG SESSION:", dict(session))  # <-- THÊM DÒNG NÀY
            return (
                jsonify(
                    {
                        "success": True,
                        "message": "Login successful.",
                        "user": {
                            "username": user["username"],
                            "id": user["user_id"],
                            "role": session["role"],
                        },
                    }
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {"success": False, "message": "Invalid username/email or password."}
                ),
                401,
            )

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        conn.close()


@auth_bp.route("/logout")
def logout():
    session.clear()
    session.pop("role", None)
    return redirect(url_for("main.home"))
