from backend.database import get_db_connection


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
):
    """Save submission result to database"""
    conn = get_db_connection()
    if not conn:
        return False

    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO submissions (
                user_id, problem_id, code, language, status, 
                test_cases_passed, total_test_cases,
                execution_time, memory_used
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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


def get_user_submissions(user_id):
    """Get all submissions for a specific user"""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
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
        """,
            (user_id,),
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching user submissions: {e}")
        return []
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
        return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching submission detail: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
