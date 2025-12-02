from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
from mysql.connector import Error
from dotenv import load_dotenv
from backend.database import get_db_connection
from backend.routes import auth_bp, problem_bp, user_bp

load_dotenv()

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(problem_bp)
app.register_blueprint(user_bp)

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Hiển thị danh sách tất cả problems"""
    conn = get_db_connection()
    if not conn:
        return render_template('index.html', problems=[], error="Không thể kết nối database")
    
    cursor = conn.cursor(dictionary=True)
    
    difficulty = request.args.get('difficulty', '')
    tag = request.args.get('tag', '')
    search = request.args.get('search', '')
    
    # Xây dựng query với filter
    query = """
        SELECT p.*, GROUP_CONCAT(t.tag_name) as tags
        FROM problems p
        LEFT JOIN problem_tags pt ON p.problem_id = pt.problem_id
        LEFT JOIN tags t ON pt.tag_id = t.tag_id
        WHERE 1=1
    """
    params = []
    
    if difficulty:
        query += " AND p.difficulty = %s"
        params.append(difficulty)
    
    if tag:
        query += " AND t.tag_name = %s"
        params.append(tag)
    
    if search:
        query += " AND (p.title LIKE %s OR p.description LIKE %s)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param])
    
    query += " GROUP BY p.problem_id ORDER BY p.problem_id DESC"
    
    cursor.execute(query, params)
    problems = cursor.fetchall()
    
    # Get all tags for filter dropdown
    cursor.execute("SELECT DISTINCT tag_name FROM tags ORDER BY tag_name")
    all_tags = [row['tag_name'] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template('index.html', problems=problems, all_tags=all_tags,
                         difficulty=difficulty, tag=tag, search=search)

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Tạo problem mới"""
    if request.method == 'POST':
        title = request.form.get('title')
        slug = request.form.get('slug')
        description = request.form.get('description')
        difficulty = request.form.get('difficulty')
        time_limit = request.form.get('time_limit', 1000)
        memory_limit = request.form.get('memory_limit', 256)
        tags = request.form.getlist('tags')
        
        conn = get_db_connection()
        if not conn:
            return render_template('create.html', error="Không thể kết nối database"), 500
        
        cursor = conn.cursor()
        try:
            query = """INSERT INTO problems (title, slug, description, difficulty, time_limit, memory_limit) 
                      VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (title, slug, description, difficulty, time_limit, memory_limit))
            problem_id = cursor.lastrowid
            
            for tag_id in tags:
                cursor.execute("INSERT INTO problem_tags (problem_id, tag_id) VALUES (%s, %s)",
                             (problem_id, tag_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('index'))
        except Error as e:
            cursor.close()
            conn.close()
            return render_template('create.html', error=f"Lỗi: {e}"), 500
    
    # Get all tags for selection
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT tag_id, tag_name FROM tags ORDER BY tag_name")
    tags = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('create.html', tags=tags)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """Chỉnh sửa problem"""
    conn = get_db_connection()
    if not conn:
        return render_template('edit.html', error="Không thể kết nối database"), 500
    
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        title = request.form.get('title')
        slug = request.form.get('slug')
        description = request.form.get('description')
        difficulty = request.form.get('difficulty')
        time_limit = request.form.get('time_limit', 1000)
        memory_limit = request.form.get('memory_limit', 256)
        tags = request.form.getlist('tags')
        
        try:
            query = """UPDATE problems SET title=%s, slug=%s, description=%s, 
                      difficulty=%s, time_limit=%s, memory_limit=%s WHERE problem_id=%s"""
            cursor.execute(query, (title, slug, description, difficulty, 
                                 time_limit, memory_limit, id))
            
            cursor.execute("DELETE FROM problem_tags WHERE problem_id=%s", (id,))
            for tag_id in tags:
                cursor.execute("INSERT INTO problem_tags (problem_id, tag_id) VALUES (%s, %s)",
                             (id, tag_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('index'))
        except Error as e:
            cursor.close()
            conn.close()
            return render_template('edit.html', error=f"Lỗi: {e}"), 500
    
    # GET request - lấy problem để hiển thị
    cursor.execute("""
        SELECT p.*, GROUP_CONCAT(pt.tag_id) as tag_ids
        FROM problems p
        LEFT JOIN problem_tags pt ON p.problem_id = pt.problem_id
        WHERE p.problem_id = %s
        GROUP BY p.problem_id
    """, (id,))
    problem = cursor.fetchone()
    
    # Get all tags
    cursor.execute("SELECT tag_id, tag_name FROM tags ORDER BY tag_name")
    tags = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    if not problem:
        return redirect(url_for('index'))
    
    # Parse selected tags
    selected_tags = problem['tag_ids'].split(',') if problem['tag_ids'] else []
    
    return render_template('edit.html', problem=problem, tags=tags, selected_tags=selected_tags)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    """Xóa problem"""
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('index'))
    
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM problems WHERE problem_id = %s", (id,))
        conn.commit()
    except Error as e:
        print(f"Lỗi xóa: {e}")
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('index'))

@app.route('/api/problems', methods=['GET'])
def api_problems():
    """API lấy danh sách problems (JSON)"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    difficulty = request.args.get('difficulty', '')
    tag = request.args.get('tag', '')
    search = request.args.get('search', '')
    
    query = """
        SELECT p.*, GROUP_CONCAT(t.tag_name) as tags
        FROM problems p
        LEFT JOIN problem_tags pt ON p.problem_id = pt.problem_id
        LEFT JOIN tags t ON pt.tag_id = t.tag_id
        WHERE 1=1
    """
    params = []
    
    if difficulty:
        query += " AND p.difficulty = %s"
        params.append(difficulty)
    if tag:
        query += " AND t.tag_name = %s"
        params.append(tag)
    if search:
        query += " AND (p.title LIKE %s OR p.description LIKE %s)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param])
    
    query += " GROUP BY p.problem_id"
    
    cursor.execute(query, params)
    problems = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(problems)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
