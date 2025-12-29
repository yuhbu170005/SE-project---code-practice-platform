from flask import (
    Blueprint,
    redirect,
    request,
    jsonify,
    render_template,
    session,
    url_for,
)
from backend.services.auth_service import (
    check_user_exists,
    create_user,
    authenticate_user,
)
from backend.validators import validate_signup_data

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET"])
def view_login():
    return render_template("login.html")


@auth_bp.route("/signup", methods=["GET"])
def view_signup():
    return render_template("signup.html")


@auth_bp.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json(silent=True) or request.form

    # Get and trim inputs
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    full_name = (data.get("full_name") or "").strip()

    # Comprehensive validation
    is_valid, errors = validate_signup_data(username, email, password, full_name)

    if not is_valid:
        # Return first error for simplicity, or all errors
        first_error = next(iter(errors.values()))
        return (
            jsonify(
                {
                    "success": False,
                    "message": first_error,
                    "errors": errors,  # Frontend can show all errors if needed
                }
            ),
            400,
        )

    # Check if user exists
    user_exists = check_user_exists(username, email)

    if user_exists is None:
        return jsonify({"success": False, "message": "Database connection error."}), 500

    if user_exists:
        return (
            jsonify({"success": False, "message": "Username or email already exists."}),
            409,
        )

    # Create user
    if create_user(username, email, password, full_name):
        return jsonify({"success": True, "message": "Registration successful!"}), 201
    else:
        return jsonify({"success": False, "message": "Failed to create user."}), 500


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

    # Authenticate user
    user = authenticate_user(username_or_email, password)

    if user:
        session["user_id"] = user["user_id"]
        session["username"] = user["username"]
        session["role"] = user["role"]
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Login successful.",
                    "user": {
                        "username": user["username"],
                        "id": user["user_id"],
                        "role": user["role"],
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


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.home"))
