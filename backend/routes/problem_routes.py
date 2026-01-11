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
from backend.services.tag_service import get_all_tags, get_tag_names, get_problem_tags
from backend.services.testcase_service import (
    get_public_test_cases,
    save_test_cases,
    get_all_test_cases_with_flags,
)
from backend.validators import validate_problem_input
import json

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
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", "").strip()
        description = request.form.get("description", "").strip()
        difficulty = request.form.get("difficulty", "").strip()
        time_limit = request.form.get("time_limit", 1000)
        memory_limit = request.form.get("memory_limit", 256)
        tags = request.form.getlist("tags")
        test_cases_json = request.form.get("test_cases_json")

        # Get new fields (optional)
        starter_code = request.form.get("starter_code") or None
        wrapper_template = request.form.get("wrapper_template") or None
        function_name = request.form.get("function_name") or None

        # Check if it's an AJAX request
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

        # Parse test cases
        test_cases = []
        if test_cases_json:
            try:
                test_cases = json.loads(test_cases_json)
            except json.JSONDecodeError:
                return (
                    jsonify(
                        {"success": False, "message": "Invalid test cases JSON format"}
                    ),
                    400,
                )

        # Validate input
        is_valid, errors, normalized = validate_problem_input(
            title, slug, description, difficulty, test_cases, time_limit, memory_limit
        )

        if not is_valid:
            # Format error messages
            error_messages = "\n".join([f"• {msg}" for msg in errors.values()])
            return jsonify({"success": False, "message": error_messages}), 400

        # Use normalized values
        success, result = create_problem(
            normalized["title"],
            normalized["slug"],
            normalized["description"],
            normalized["difficulty"],
            normalized.get("time_limit", 1000),
            normalized.get("memory_limit", 256),
            tags,
            starter_code,
            wrapper_template,
            function_name,
        )

        if success:
            problem_id = result

            # Handle test cases if provided
            if test_cases:
                try:
                    save_test_cases(problem_id, test_cases)
                except Exception as e:
                    print(f"Error saving test cases: {e}")

            return (
                jsonify(
                    {
                        "success": True,
                        "message": "Problem created successfully!",
                        "problem_id": problem_id,
                    }
                ),
                200,
            )
        else:
            return jsonify({"success": False, "message": f"Error: {result}"}), 500

    # GET request - show form with tags
    tags = get_all_tags()
    return render_template("create.html", tags=tags)


@problem_bp.route("/problems/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit(id):
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", "").strip()
        description = request.form.get("description", "").strip()
        difficulty = request.form.get("difficulty", "").strip()
        time_limit = request.form.get("time_limit", 1000)
        memory_limit = request.form.get("memory_limit", 256)
        tags = request.form.getlist("tags")
        test_cases_json = request.form.get("test_cases_json")

        # Get new fields (optional)
        starter_code = request.form.get("starter_code") or None
        wrapper_template = request.form.get("wrapper_template") or None
        function_name = request.form.get("function_name") or None

        # Check if it's an AJAX request
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

        # Parse test cases
        test_cases = []
        if test_cases_json:
            try:
                test_cases = json.loads(test_cases_json)
            except json.JSONDecodeError:
                return (
                    jsonify(
                        {"success": False, "message": "Invalid test cases JSON format"}
                    ),
                    400,
                )

        # Validate input
        is_valid, errors, normalized = validate_problem_input(
            title, slug, description, difficulty, test_cases, time_limit, memory_limit
        )

        if not is_valid:
            # Format error messages
            error_messages = "\n".join([f"• {msg}" for msg in errors.values()])
            return jsonify({"success": False, "message": error_messages}), 400

        # Use normalized values
        success = update_problem(
            id,
            normalized["title"],
            normalized["slug"],
            normalized["description"],
            normalized["difficulty"],
            normalized.get("time_limit", 1000),
            normalized.get("memory_limit", 256),
            tags,
            starter_code,
            wrapper_template,
            function_name,
        )

        if success:
            # Handle test cases if provided
            if test_cases:
                try:
                    save_test_cases(id, test_cases)
                except Exception as e:
                    print(f"Error saving test cases: {e}")

            return (
                jsonify({"success": True, "message": "Problem updated successfully!"}),
                200,
            )
        else:
            return (
                jsonify({"success": False, "message": "Failed to update problem"}),
                500,
            )

    # GET request - show form
    problem = get_problem_by_id(id)
    if not problem:
        return redirect(url_for("problem.list_problems"))

    tags = get_all_tags()
    selected_tags = str(problem["tag_ids"]).split(",") if problem["tag_ids"] else []

    # Get existing test cases
    test_cases = get_all_test_cases_with_flags(id)

    return render_template(
        "edit.html",
        problem=problem,
        tags=tags,
        selected_tags=selected_tags,
        test_cases=test_cases,
    )


@problem_bp.route("/problems/delete/<int:id>", methods=["POST"])
@admin_required
def delete(id):
    success = delete_problem(id)
    if success:
        return (
            jsonify({"success": True, "message": "Problem deleted successfully!"}),
            200,
        )
    else:
        return jsonify({"success": False, "message": "Failed to delete problem."}), 500


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

    # Get tags for this problem
    tags = get_problem_tags(problem["problem_id"])

    # Pass starter_code to template (fallback to default if null)
    starter_code = problem.get("starter_code")

    # Check if starter_code is JSON (multi-language support)
    if starter_code and starter_code.strip().startswith("{"):
        try:
            import json

            starter_codes = json.loads(starter_code)
            # Convert to JavaScript object for frontend
            starter_code = starter_codes
        except (json.JSONDecodeError, ValueError):
            # Not JSON, use as-is
            pass

    # Get function name (fallback to 'solve' if not provided)
    function_name = problem.get("function_name") or "solve"

    # Fallback to default Python code if no starter_code
    if not starter_code:
        starter_code = f"class Solution:\n    def {function_name}(self, input_str):\n        # Your code here\n        pass"

    return render_template(
        "problem_detail.html",
        problem=problem,
        sample_cases=sample_cases,
        test_cases=test_cases,
        starter_code=starter_code,
        function_name=function_name,
        tags=tags,
    )
