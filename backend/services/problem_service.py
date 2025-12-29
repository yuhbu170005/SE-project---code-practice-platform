from backend.database import get_db_connection


def get_problem_detail_by_slug(slug):
    """Get problem details by slug with sample test cases"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        # Get problem information
        cursor.execute("SELECT * FROM problems WHERE slug = %s", (slug,))
        problem = cursor.fetchone()

        if not problem:
            return None, None, None

        # Get sample test cases for display in description (Examples)
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

        # Get public test cases for "Test Cases" tab (non-sample, visible)
        cursor.execute(
            """
            SELECT test_case_id, input, expected_output 
            FROM test_cases 
            WHERE problem_id = %s AND is_hidden = FALSE AND is_sample = FALSE
            ORDER BY test_case_id ASC
            """,
            (problem["problem_id"],),
        )
        test_cases = cursor.fetchall()

        return problem, sample_cases, test_cases

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def get_problems_list(difficulty=None, search=None, tags=None, page=1, per_page=7):
    """Get paginated list of problems with filters"""
    conn = get_db_connection()
    if not conn:
        return [], 0

    try:
        cursor = conn.cursor(dictionary=True)

        # Build WHERE clause
        base_where = " WHERE 1=1 "
        params = []

        if difficulty:
            base_where += " AND p.difficulty = %s"
            params.append(difficulty)

        if search:
            search_param = f"%{search[:100]}%"
            base_where += " AND p.title LIKE %s"
            params.append(search_param)

        # Tag filtering
        tag_exists_clause = ""
        tag_params = []
        if tags:
            placeholders = ", ".join(["%s"] * len(tags))
            tag_exists_clause = f""" AND EXISTS (
                SELECT 1 FROM problem_tags pt2
                JOIN tags t2 ON pt2.tag_id = t2.tag_id
                WHERE pt2.problem_id = p.problem_id AND t2.tag_name IN ({placeholders})
            )"""
            tag_params = tags

        # Count total
        count_query = f"""
            SELECT COUNT(DISTINCT p.problem_id) AS total
            FROM problems p
            LEFT JOIN problem_tags pt ON p.problem_id = pt.problem_id
            LEFT JOIN tags t ON pt.tag_id = t.tag_id
            {base_where}
            {tag_exists_clause}
        """
        cursor.execute(count_query, params + tag_params)
        total_count = cursor.fetchone()["total"]

        # Get problems
        offset = (page - 1) * per_page
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
        cursor.execute(main_query, params + tag_params + [per_page, offset])
        problems = cursor.fetchall()

        # Process tags
        for p in problems:
            p["tags"] = p["tags"].split(",") if p.get("tags") else []

        return problems, total_count
    except Exception as e:
        print(f"Error fetching problems list: {e}")
        return [], 0
    finally:
        cursor.close()
        conn.close()


def get_problem_by_id(problem_id):
    """Get problem with tags by ID"""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT p.*, GROUP_CONCAT(pt.tag_id) as tag_ids
            FROM problems p
            LEFT JOIN problem_tags pt ON p.problem_id = pt.problem_id
            WHERE p.problem_id = %s
            GROUP BY p.problem_id
        """,
            (problem_id,),
        )
        return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching problem by ID: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def create_problem(
    title, slug, description, difficulty, time_limit, memory_limit, tags
):
    """Create a new problem with tags"""
    conn = get_db_connection()
    if not conn:
        return False, "Database connection error"

    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO problems (title, slug, description, difficulty, time_limit, memory_limit) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (title, slug, description, difficulty, time_limit, memory_limit),
        )
        problem_id = cursor.lastrowid

        # Insert tags
        for tag_id in tags:
            cursor.execute(
                "INSERT INTO problem_tags (problem_id, tag_id) VALUES (%s, %s)",
                (problem_id, tag_id),
            )

        conn.commit()
        return True, problem_id
    except Exception as e:
        conn.rollback()
        print(f"Error creating problem: {e}")
        return False, str(e)
    finally:
        cursor.close()
        conn.close()


def update_problem(
    problem_id, title, slug, description, difficulty, time_limit, memory_limit, tags
):
    """Update existing problem"""
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE problems SET title=%s, slug=%s, description=%s, 
               difficulty=%s, time_limit=%s, memory_limit=%s WHERE problem_id=%s""",
            (
                title,
                slug,
                description,
                difficulty,
                time_limit,
                memory_limit,
                problem_id,
            ),
        )

        # Update tags
        cursor.execute("DELETE FROM problem_tags WHERE problem_id=%s", (problem_id,))
        for tag_id in tags:
            cursor.execute(
                "INSERT INTO problem_tags (problem_id, tag_id) VALUES (%s, %s)",
                (problem_id, tag_id),
            )

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error updating problem: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def delete_problem(problem_id):
    """Delete a problem"""
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM problems WHERE problem_id = %s", (problem_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error deleting problem: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
