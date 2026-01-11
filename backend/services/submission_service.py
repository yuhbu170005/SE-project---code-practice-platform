from backend.database import get_db_connection
import json


def save_submission_to_db(
    user_id,
    problem_id,
    code,
    language,
    status,
    test_cases_passed=0,
    total_test_cases=0,
    execution_time=None,
    memory_used=None,
    test_case_results=None,
):
    """Save submission result to database"""
    conn = get_db_connection()
    if not conn:
        return False

    cursor = conn.cursor()
    try:
        # Convert test_case_results to JSON if provided
        test_case_results_json = None
        if test_case_results:
            test_case_results_json = json.dumps(test_case_results)

        cursor.execute(
            """
            INSERT INTO submissions (
                user_id, problem_id, code, language, status, 
                test_cases_passed, total_test_cases,
                execution_time, memory_used, test_case_results,
                submitted_at
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """,
            (
                user_id,
                problem_id,
                code,
                language,
                status,
                test_cases_passed,
                total_test_cases,
                execution_time,
                memory_used,
                test_case_results_json,
            ),
        )
        conn.commit()
        submission_id = cursor.lastrowid
        return True, submission_id
    except Exception as e:
        print(f"Error saving submission: {e}")
        conn.rollback()
        return False, None
    finally:
        cursor.close()
        conn.close()


def get_user_submissions(user_id, page=1, per_page=10):
    """Get paginated submissions for a specific user"""
    conn = get_db_connection()
    if not conn:
        return [], 0

    try:
        cursor = conn.cursor(dictionary=True)

        # Count total submissions
        cursor.execute(
            "SELECT COUNT(*) as total FROM submissions WHERE user_id = %s", (user_id,)
        )
        total_count = cursor.fetchone()["total"]

        # Get paginated submissions
        offset = (page - 1) * per_page
        cursor.execute(
            """
            SELECT 
                s.submission_id,
                s.user_id,
                s.problem_id,
                p.title,
                p.slug,
                s.status,
                s.submitted_at,
                s.code
            FROM submissions s
            JOIN problems p ON s.problem_id = p.problem_id
            WHERE s.user_id = %s
            ORDER BY s.submitted_at DESC
            LIMIT %s OFFSET %s
        """,
            (user_id, per_page, offset),
        )
        submissions = cursor.fetchall()
        return submissions, total_count
    except Exception as e:
        print(f"Error fetching user submissions: {e}")
        return [], 0
    finally:
        cursor.close()
        conn.close()


def get_submission_detail(submission_id):
    """Get detailed information about a submission"""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT 
                s.submission_id,
                s.user_id,
                s.problem_id,
                s.code,
                s.status,
                s.submitted_at,
                s.test_cases_passed,
                s.total_test_cases,
                s.execution_time,
                s.memory_used,
                s.test_case_results,
                p.title,
                p.slug,
                u.username
            FROM submissions s
            JOIN problems p ON s.problem_id = p.problem_id
            JOIN users u ON s.user_id = u.user_id
            WHERE s.submission_id = %s
        """,
            (submission_id,),
        )
        result = cursor.fetchone()

        # Parse test_case_results JSON if present
        if result and result.get("test_case_results"):
            try:
                result["test_case_results"] = json.loads(result["test_case_results"])
            except:
                result["test_case_results"] = None

        return result
    except Exception as e:
        print(f"Error fetching submission detail: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
