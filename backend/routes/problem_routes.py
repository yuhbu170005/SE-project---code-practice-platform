from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    session,
)
from backend.utils import admin_required
from backend.services.problem_service import (
    get_problem_detail_by_slug,
    get_problems_list,
    create_problem,
    update_problem,
    delete_problem,
    get_problem_by_id,
)
from backend.services.tag_service import get_all_tags, get_tag_names
from backend.services.testcase_service import get_public_test_cases

problem_bp = Blueprint("problem", __name__)

# Constants
PER_PAGE = 7


@problem_bp.route("/problems")
def list_problems():
    # Get filter params
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

    # Get problems from service
    problems, total_count = get_problems_list(
        difficulty=difficulty if difficulty else None,
        search=search if search else None,
        tags=selected_tags if selected_tags else None,
        page=page,
        per_page=PER_PAGE,
    )

    if problems is None:
        return render_template(
            "problems.html", problems=[], error="Database connection failed"
        )

    # Get all tags for filter menu
    all_tags = get_tag_names()

    # Calculate pagination
    total_pages = (total_count + PER_PAGE - 1) // PER_PAGE if total_count > 0 else 1
    pagination = {
        "page": page,
        "per_page": PER_PAGE,
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

        success, result = create_problem(
            title, slug, description, difficulty, time_limit, memory_limit, tags
        )

        if success:
            return redirect(url_for("problem.list_problems"))
        else:
            return render_template("create.html", error=f"Error: {result}"), 500

    # GET request - show form with tags
    tags = get_all_tags()
    return render_template("create.html", tags=tags)


@problem_bp.route("/problems/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit(id):
    if request.method == "POST":
        title = request.form.get("title")
        slug = request.form.get("slug")
        description = request.form.get("description")
        difficulty = request.form.get("difficulty")
        time_limit = request.form.get("time_limit", 1000)
        memory_limit = request.form.get("memory_limit", 256)
        tags = request.form.getlist("tags")

        success = update_problem(
            id, title, slug, description, difficulty, time_limit, memory_limit, tags
        )

        if success:
            return redirect(url_for("problem.list_problems"))
        else:
            return (
                render_template(
                    "edit.html",
                    error="Failed to update problem",
                    problem={"problem_id": id},
                ),
                500,
            )

    # GET request - show form
    problem = get_problem_by_id(id)
    if not problem:
        return redirect(url_for("problem.list_problems"))

    tags = get_all_tags()
    selected_tags = str(problem["tag_ids"]).split(",") if problem["tag_ids"] else []

    return render_template(
        "edit.html", problem=problem, tags=tags, selected_tags=selected_tags
    )


@problem_bp.route("/problems/delete/<int:id>", methods=["POST"])
@admin_required
def delete(id):
    delete_problem(id)
    return redirect(url_for("problem.list_problems"))


# ==================== API ROUTES (JSON) ====================


@problem_bp.route("/api/problems", methods=["GET"])
def api_problems():
    pass


@problem_bp.route("/problems/<string:slug>")
def problem_detail(slug):
    problem, sample_cases, test_cases = get_problem_detail_by_slug(slug)

    # Xử lý logic hiển thị
    if not problem:
        return "Problem not found", 404
        # Hoặc dùng: abort(404)

    return render_template(
        "problem_detail.html",
        problem=problem,
        sample_cases=sample_cases,
        test_cases=test_cases,
    )
