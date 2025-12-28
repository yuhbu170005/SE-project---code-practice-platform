from backend.database import get_db_connection


def get_all_tags():
    """Get all tags ordered by name"""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT tag_id, tag_name FROM tags ORDER BY tag_name")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching all tags: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def get_tag_names():
    """Get list of all tag names"""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT tag_name FROM tags ORDER BY tag_name")
        return [row["tag_name"] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error fetching tag names: {e}")
        return []
    finally:
        cursor.close()
        conn.close()
