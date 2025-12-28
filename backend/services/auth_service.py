from backend.database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash


def check_user_exists(username, email):
    """Check if username or email already exists"""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT user_id FROM users WHERE username = %s OR email = %s",
            (username, email),
        )
        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        print(f"Error checking user exists: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def create_user(username, email, password, full_name):
    """Create a new user with hashed password"""
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        hashed_pw = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, full_name) VALUES (%s, %s, %s, %s)",
            (username, email, hashed_pw, full_name),
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def authenticate_user(username_or_email, password):
    """Authenticate user and return user data if valid"""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT user_id, username, password_hash, role FROM users WHERE username = %s OR email = %s",
            (username_or_email, username_or_email),
        )
        user = cursor.fetchone()

        if user and check_password_hash(user["password_hash"], password):
            return {
                "user_id": user["user_id"],
                "username": user["username"],
                "role": user.get("role", "user"),
            }
        return None
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
