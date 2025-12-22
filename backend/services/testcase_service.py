from backend.database import get_db_connection


def get_public_test_cases(problem_id):
    """Lấy test case công khai để người dùng chạy thử (Run Code)"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT input, expected_output 
            FROM test_cases 
            WHERE problem_id = %s AND is_hidden = FALSE
        """,
            (problem_id,),
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching public test cases: {e}")
        return []
    finally:
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
        conn.close()
