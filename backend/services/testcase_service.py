from backend.database import get_db_connection


def get_sample_test_cases(problem_id):
    """Lấy sample test cases để hiển thị kết quả trong submission detail"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT test_case_id, input, expected_output, is_sample, is_hidden
            FROM test_cases 
            WHERE problem_id = %s AND is_sample = TRUE
            ORDER BY test_case_id ASC
        """,
            (problem_id,),
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching sample test cases: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def get_public_test_cases(problem_id):
    """Lấy test case công khai để người dùng chạy thử (Run Code) - không bao gồm sample cases"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT input, expected_output 
            FROM test_cases 
            WHERE problem_id = %s AND is_hidden = FALSE AND is_sample = FALSE
        """,
            (problem_id,),
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching public test cases: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def get_all_test_cases(problem_id):
    """Lấy toàn bộ test case để chấm điểm (Submit Code)"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT input, expected_output 
            FROM test_cases 
            WHERE problem_id = %s 
            ORDER BY test_case_id ASC
        """,
            (problem_id,),
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching all test cases: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def get_all_test_cases_with_flags(problem_id):
    """Get all test cases with is_sample and is_hidden flags for editing"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT test_case_id, input, expected_output, is_sample, is_hidden
            FROM test_cases 
            WHERE problem_id = %s 
            ORDER BY test_case_id ASC
        """,
            (problem_id,),
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching test cases with flags: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def save_test_cases(problem_id, test_cases):
    """Save test cases for a problem (replaces all existing test cases)"""
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # Delete existing test cases
        cursor.execute("DELETE FROM test_cases WHERE problem_id = %s", (problem_id,))

        # Insert new test cases
        for tc in test_cases:
            cursor.execute(
                """INSERT INTO test_cases (problem_id, input, expected_output, is_sample, is_hidden) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (
                    problem_id,
                    tc.get("input", ""),
                    tc.get("expected_output", ""),
                    tc.get("is_sample", False),
                    tc.get("is_hidden", False),
                ),
            )

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error saving test cases: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
