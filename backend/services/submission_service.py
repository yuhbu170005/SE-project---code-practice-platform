from backend.database import get_db_connection


def save_submission_to_db(
    user_id, problem_id, code, language, status, error_message=""
):
    """Lưu kết quả bài nộp vào Database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO submissions (user_id, problem_id, code, language, status, error_message) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
            (user_id, problem_id, code, language, status, error_message),
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving submission: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
