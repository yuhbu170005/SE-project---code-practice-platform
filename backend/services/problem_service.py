from backend.database import get_db_connection  # Import hàm kết nối DB của bạn


def get_problem_detail_by_slug(slug):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        # 1. Lấy thông tin bài tập
        cursor.execute("SELECT * FROM problems WHERE slug = %s", (slug,))
        problem = cursor.fetchone()

        if not problem:
            return None, None  # Không tìm thấy bài

        # 2. Lấy test case mẫu
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

        # 2. Lấy test case mẫu
        cursor.execute(
            """
            SELECT test_case_id, input, expected_output 
            FROM test_cases 
            WHERE problem_id = %s AND is_hidden = FALSE
            ORDER BY test_case_id ASC
            """,
            (problem["problem_id"],),
        )

        test_cases = cursor.fetchall()

        return problem, sample_cases, test_cases

    finally:
        # Luôn đảm bảo đóng kết nối dù có lỗi hay không
        if conn.is_connected():
            cursor.close()
            conn.close()
