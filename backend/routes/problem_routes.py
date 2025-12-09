from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    session,
)
from mysql.connector import Error
from backend.database import get_db_connection
from backend.utils import admin_required

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

    # Params
    difficulty = request.args.get("difficulty", "").strip()
    search = request.args.get("search", "").strip()
    selected_tags = request.args.getlist("tag")

    # Pagination params
    try:
        page = int(request.args.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    per_page = 7
    offset = (page - 1) * per_page

    # Base query and params (we will use EXISTS for tag filtering)
    base_where = " WHERE 1=1 "
    params = []

    if difficulty:
        base_where += " AND p.difficulty = %s"
        params.append(difficulty)

    if search:
        s = search[:100]
        search_param = f"%{s}%"
        base_where += " AND p.title LIKE %s"
        params.append(search_param)

    # If selected_tags -> add EXISTS filter (safer than HAVING)
    tag_exists_clause = ""
    tag_params = []
    if selected_tags:
        placeholders = ", ".join(["%s"] * len(selected_tags))
        tag_exists_clause = f""" AND EXISTS (
            SELECT 1 FROM problem_tags pt2
            JOIN tags t2 ON pt2.tag_id = t2.tag_id
            WHERE pt2.problem_id = p.problem_id AND t2.tag_name IN ({placeholders})
        )"""
        tag_params = selected_tags

    # Count total distinct problems matching filters
    count_query = f"""
        SELECT COUNT(DISTINCT p.problem_id) AS total
        FROM problems p
        LEFT JOIN problem_tags pt ON p.problem_id = pt.problem_id
        LEFT JOIN tags t ON pt.tag_id = t.tag_id
        {base_where}
        {tag_exists_clause}
    """
    try:
        cursor.execute(count_query, params + tag_params)
        total_count_row = cursor.fetchone()
        total_count = total_count_row["total"] if total_count_row else 0
    except Exception as e:
        cursor.close()
        conn.close()
        return render_template("problems.html", problems=[], error=f"DB error: {e}")

    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1

    # Main query: fetch paged results (group and concat tags)
    main_query = f"""
        SELECT p.*, GROUP_CONCAT(t.tag_name) as tags
        FROM problems p
        LEFT JOIN problem_tags pt ON p.problem_id = pt.problem_id
        LEFT JOIN tags t ON pt.tag_id = t.tag_id
        {base_where}
        {tag_exists_clause}
        GROUP BY p.problem_id
        ORDER BY p.problem_id ASC
        LIMIT %s OFFSET %s
    """
    try:
        final_params = params + tag_params + [per_page, offset]
        cursor.execute(main_query, final_params)
        problems = cursor.fetchall()
    except Exception as e:
        cursor.close()
        conn.close()
        return render_template("problems.html", problems=[], error=f"DB error: {e}")

    # Lấy danh sách tất cả Tags để hiển thị menu
    cursor.execute("SELECT DISTINCT tag_name FROM tags ORDER BY tag_name")
    all_tags = [row["tag_name"] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    # Convert tags string -> list for template if present
    for p in problems or []:
        if p.get("tags"):
            p["tags"] = p["tags"].split(",")
        else:
            p["tags"] = []

    pagination = {
        "page": page,
        "per_page": per_page,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages,
    }

    return render_template(
        "problems.html",
        problems=problems,
        all_tags=all_tags,
        difficulty=difficulty,
        search=search,
        selected_tags=selected_tags,
        pagination=pagination,
    )


# Đường dẫn: /problems/create
@problem_bp.route("/problems/create", methods=["GET", "POST"])
@admin_required
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
@admin_required
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

    # 1. Lấy thông tin bài tập + danh sách tag ID đã chọn
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

    # 2. Lấy toàn bộ Tags
    cursor.execute("SELECT tag_id, tag_name FROM tags ORDER BY tag_name")
    tags = cursor.fetchall()

    cursor.close()
    conn.close()

    if not problem:
        return redirect(url_for("problem.list_problems"))

    selected_tags = str(problem["tag_ids"]).split(",") if problem["tag_ids"] else []

    return render_template(
        "edit.html", problem=problem, tags=tags, selected_tags=selected_tags
    )


# Đường dẫn: /problems/delete/<id>
@problem_bp.route("/problems/delete/<int:id>", methods=["POST"])
@admin_required
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

    # 2. LẤY TESTCASES MẪU (SỬA TÊN BẢNG VÀ TÊN CỘT)
    # Bảng: test_cases | Cột: input
    cursor.execute(
        """
        SELECT input, expected_output 
        FROM test_cases 
        WHERE problem_id = %s AND is_hidden = FALSE 
        LIMIT 3
        """,
        (id,),
    )
    sample_testcases = cursor.fetchall()

    cursor.close()
    conn.close()

    if not problem:
        return render_template("404.html"), 404

    if problem["tags"]:
        problem["tags"] = problem["tags"].split(",")
    else:
        problem["tags"] = []

    return render_template(
        "problem_detail.html", problem=problem, testcases=sample_testcases
    )


# backend/routes/problem_routes.py


@problem_bp.route("/problems/<string:slug>")
def problem_detail(slug):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM problems WHERE slug = %s", (slug,))
    problem = cursor.fetchone()

    if not problem:
        return "Problem not found", 404

    # --- SỬA TẠI ĐÂY: Đổi case_id thành test_case_id ---
    cursor.execute(
        """
        SELECT test_case_id, input, expected_output 
        FROM test_cases 
        WHERE problem_id = %s AND is_sample = TRUE
        ORDER BY test_case_id ASC
    """,
        (problem["problem_id"],),
    )
    sample_cases = cursor.fetchall()

    conn.close()

    return render_template(
        "problem_detail.html", problem=problem, testcases=sample_cases
    )
