from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from mysql.connector import Error
from backend.database import get_db_connection

# 1. Tạo Blueprint
problem_bp = Blueprint("problem", __name__)

# ==================== VIEW ROUTES (Giao diện) ====================


# Đường dẫn: /problems (Danh sách bài tập)
@problem_bp.route("/problems")
def list_problems():
    conn = get_db_connection()
    if not conn:
        return render_template(
            "problems.html", problems=[], error="Database connection failed"
        )

    cursor = conn.cursor(dictionary=True)

    difficulty = request.args.get("difficulty", "")
    tag = request.args.get("tag", "")
    search = request.args.get("search", "")

    # Thay đổi logic nhận tags dạng list nếu bạn đã sửa frontend
    tags_filter = request.args.getlist("tag")

    query = """
        SELECT p.*, GROUP_CONCAT(t.tag_name) as tags
        FROM problems p
        LEFT JOIN problem_tags pt ON p.problem_id = pt.problem_id
        LEFT JOIN tags t ON pt.tag_id = t.tag_id
        WHERE 1=1
    """
    params = []

    if difficulty:
        query += " AND p.difficulty = %s"
        params.append(difficulty)

    if search:
        query += " AND (p.title LIKE %s OR p.description LIKE %s)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param])

    # Xử lý lọc nhiều tags
    if tags_filter:
        placeholders = ", ".join(["%s"] * len(tags_filter))
        query += f" AND t.tag_name IN ({placeholders})"
        params.extend(tags_filter)

    query += " GROUP BY p.problem_id ORDER BY p.problem_id ASC"

    cursor.execute(query, params)
    problems = cursor.fetchall()

    cursor.execute("SELECT DISTINCT tag_name FROM tags ORDER BY tag_name")
    all_tags = [row["tag_name"] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return render_template(
        "problems.html",
        problems=problems,
        all_tags=all_tags,
        difficulty=difficulty,
        search=search,
        selected_tags_list=tags_filter,  # Truyền list tags sang HTML
    )


# Đường dẫn: /problems/create
@problem_bp.route("/problems/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        title = request.form.get("title")
        slug = request.form.get("slug")
        description = request.form.get("description")
        difficulty = request.form.get("difficulty")
        time_limit = request.form.get("time_limit", 1000)
        memory_limit = request.form.get("memory_limit", 256)
        tags = request.form.getlist("tags")

        conn = get_db_connection()
        if not conn:
            return render_template("create.html", error="Database Error"), 500

        cursor = conn.cursor()
        try:
            query = """INSERT INTO problems (title, slug, description, difficulty, time_limit, memory_limit) 
                       VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(
                query, (title, slug, description, difficulty, time_limit, memory_limit)
            )
            problem_id = cursor.lastrowid

            for tag_id in tags:
                cursor.execute(
                    "INSERT INTO problem_tags (problem_id, tag_id) VALUES (%s, %s)",
                    (problem_id, tag_id),
                )

            conn.commit()
            # Redirect về danh sách bài tập (chú ý: 'problem.list_problems')
            return redirect(url_for("problem.list_problems"))
        except Error as e:
            return render_template("create.html", error=f"Error: {e}"), 500
        finally:
            cursor.close()
            conn.close()

    # GET request
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT tag_id, tag_name FROM tags ORDER BY tag_name")
    tags = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("create.html", tags=tags)


# Đường dẫn: /problems/edit/<id>
@problem_bp.route("/problems/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db_connection()
    if not conn:
        return "Database Error", 500
    cursor = conn.cursor(dictionary=True)

    # --- XỬ LÝ POST (Lưu sửa đổi) ---
    if request.method == "POST":
        title = request.form.get("title")
        slug = request.form.get("slug")
        description = request.form.get("description")
        difficulty = request.form.get("difficulty")
        time_limit = request.form.get("time_limit", 1000)
        memory_limit = request.form.get("memory_limit", 256)
        tags = request.form.getlist("tags")

        try:
            # Update bảng problems
            query = """UPDATE problems SET title=%s, slug=%s, description=%s, 
                       difficulty=%s, time_limit=%s, memory_limit=%s WHERE problem_id=%s"""
            cursor.execute(
                query,
                (title, slug, description, difficulty, time_limit, memory_limit, id),
            )

            # Update bảng tags (Xóa hết cũ -> Thêm mới)
            cursor.execute("DELETE FROM problem_tags WHERE problem_id=%s", (id,))
            for tag_id in tags:
                cursor.execute(
                    "INSERT INTO problem_tags (problem_id, tag_id) VALUES (%s, %s)",
                    (id, tag_id),
                )

            conn.commit()
            cursor.close()
            conn.close()

            # SỬA LỖI 1: Redirect đúng tên blueprint
            return redirect(url_for("problem.list_problems"))

        except Error as e:
            cursor.close()
            conn.close()
            return (
                render_template(
                    "edit.html", error=f"Error: {e}", problem={"problem_id": id}
                ),
                500,
            )

    # --- XỬ LÝ GET (Hiển thị form) ---

    # 1. Lấy thông tin bài tập + danh sách tag ID đã chọn (dạng chuỗi "1,2,3")
    cursor.execute(
        """
        SELECT p.*, GROUP_CONCAT(pt.tag_id) as tag_ids
        FROM problems p
        LEFT JOIN problem_tags pt ON p.problem_id = pt.problem_id
        WHERE p.problem_id = %s
        GROUP BY p.problem_id
    """,
        (id,),
    )
    problem = cursor.fetchone()

    # 2. Lấy toàn bộ Tags để hiển thị checkbox
    cursor.execute("SELECT tag_id, tag_name FROM tags ORDER BY tag_name")
    tags = cursor.fetchall()

    cursor.close()
    conn.close()

    if not problem:
        return redirect(url_for("problem.list_problems"))

    # SỬA LỖI 2: Xử lý tag_ids thành list để HTML dùng
    # Ví dụ DB trả về "1,2" -> Python đổi thành ['1', '2']
    selected_tags = str(problem["tag_ids"]).split(",") if problem["tag_ids"] else []

    # Gửi đủ 3 biến sang HTML
    return render_template(
        "edit.html", problem=problem, tags=tags, selected_tags=selected_tags
    )


# Đường dẫn: /problems/delete/<id>
@problem_bp.route("/problems/delete/<int:id>", methods=["POST"])
def delete(id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM problems WHERE problem_id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(url_for("problem.list_problems"))


# ==================== API ROUTES (JSON) ====================


@problem_bp.route("/api/problems", methods=["GET"])
def api_problems():
    # ... (Copy logic if needed) ...
    pass


@problem_bp.route("/problem/<int:id>", methods=["GET"])
def view_problem(id):
    conn = get_db_connection()
    if not conn:
        return "Database Error", 500

    cursor = conn.cursor(dictionary=True)

    # 1. Lấy thông tin bài tập
    cursor.execute(
        """
        SELECT p.*, GROUP_CONCAT(t.tag_name) as tags
        FROM problems p
        LEFT JOIN problem_tags pt ON p.problem_id = pt.problem_id
        LEFT JOIN tags t ON pt.tag_id = t.tag_id
        WHERE p.problem_id = %s
        GROUP BY p.problem_id
    """,
        (id,),
    )

    problem = cursor.fetchone()
    cursor.close()
    conn.close()

    # Nếu không tìm thấy bài tập thì báo lỗi 404
    if not problem:
        return render_template("404.html"), 404

    # Xử lý tags thành list
    if problem["tags"]:
        problem["tags"] = problem["tags"].split(",")
    else:
        problem["tags"] = []

    # Render ra giao diện làm bài
    return render_template("problem_detail.html", problem=problem)
