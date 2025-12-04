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

# 1. Tạo Blueprint (Thay thế cho app)
auth_bp = Blueprint("auth", __name__)

# ================= QUẢN LÝ GIAO DIỆN (GET) =================


@auth_bp.route("/login", methods=["GET"])
def view_login():
    return render_template("login.html")


@auth_bp.route("/signup", methods=["GET"])
def view_signup():
    return render_template("signup.html")


# ================= QUẢN LÝ API (POST) =================


@auth_bp.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json() or request.form

    # Lấy dữ liệu
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")

    # Validate cơ bản
    if not username or not password:
        return jsonify({"success": False, "message": "Missing required fields!"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection error."}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        # Kiểm tra trùng
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return (
                jsonify({"success": False, "message": "Username already exists."}),
                409,
            )

        # Hash password và Lưu
        hashed_pw = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, full_name) VALUES (%s, %s, %s, %s)",
            (username, email, hashed_pw, full_name),
        )
        conn.commit()

        return jsonify({"success": True, "message": "Registration successful!"}), 201

    except Exception as e:
        print(e)
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or request.form
    username = data.get("username")  # Khớp với frontend
    password = data.get("password")

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database connection error."}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        # Tìm user
        cursor.execute(
            "SELECT * FROM users WHERE username = %s OR email = %s",
            (username, username),
        )
        user = cursor.fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            return (
                jsonify(
                    {
                        "success": True,
                        "message": "Login successful.",
                        "user": {"username": user["username"], "id": user["user_id"]},
                    }
                ),
                200,
            )
        else:
            return (
                jsonify({"success": False, "message": "Invalid username or password."}),
                401,
            )

    finally:
        cursor.close()
        conn.close()


@auth_bp.route("/logout")
def logout():
    # Xóa sạch dữ liệu trong phiên đăng nhập
    session.clear()

    # Chuyển hướng về trang chủ
    return redirect(url_for("main.home"))
