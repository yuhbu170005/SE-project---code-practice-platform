from functools import wraps
from flask import session, redirect, url_for, abort


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.view_login"))
        # Cho phép admin theo role, hoặc giữ quyền cho user_id 1 nếu bạn muốn super-admin
        if session.get("role") != "admin" and session.get("user_id") != 1:
            return abort(403)  # trả HTTP 403 Forbidden
        return f(*args, **kwargs)

    return decorated
