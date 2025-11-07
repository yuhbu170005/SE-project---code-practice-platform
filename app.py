from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.config['DATABASE'] = 'coding_platform.db'

def get_db_connection():
    """Get a database connection."""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with schema and dummy data."""
    conn = get_db_connection()
    
    # Create problems table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            examples TEXT
        )
    ''')
    
    # Create submissions table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            language TEXT NOT NULL,
            status TEXT NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (problem_id) REFERENCES problems (id)
        )
    ''')
    
    # Check if we need to add dummy data
    cursor = conn.execute('SELECT COUNT(*) FROM problems')
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Insert dummy problems
        problems = [
            ('Two Sum', 
             'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
             'Easy',
             'Example 1: Input: nums = [2,7,11,15], target = 9\nOutput: [0,1]'),
            ('Reverse String',
             'Write a function that reverses a string. The input string is given as an array of characters.',
             'Easy',
             'Example 1: Input: s = ["h","e","l","l","o"]\nOutput: ["o","l","l","e","h"]'),
            ('Binary Search',
             'Given an array of integers nums which is sorted in ascending order, and an integer target, write a function to search target in nums.',
             'Medium',
             'Example 1: Input: nums = [-1,0,3,5,9,12], target = 9\nOutput: 4'),
            ('Valid Parentheses',
             'Given a string s containing just the characters "(", ")", "{", "}", "[" and "]", determine if the input string is valid.',
             'Medium',
             'Example 1: Input: s = "()"\nOutput: true'),
            ('Merge Two Sorted Lists',
             'You are given the heads of two sorted linked lists list1 and list2. Merge the two lists into one sorted list.',
             'Hard',
             'Example 1: Input: list1 = [1,2,4], list2 = [1,3,4]\nOutput: [1,1,2,3,4,4]')
        ]
        
        conn.executemany('INSERT INTO problems (title, description, difficulty, examples) VALUES (?, ?, ?, ?)', problems)
        
        # Insert some dummy submissions
        submissions = [
            (1, 'def twoSum(nums, target):\n    for i in range(len(nums)):\n        for j in range(i+1, len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]', 'Python', 'Accepted'),
            (2, 'def reverseString(s):\n    s.reverse()\n    return s', 'Python', 'Accepted'),
            (3, 'def search(nums, target):\n    left, right = 0, len(nums) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if nums[mid] == target:\n            return mid\n        elif nums[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1', 'Python', 'Accepted'),
            (1, 'def twoSum(nums, target):\n    return [0, 1]', 'Python', 'Wrong Answer')
        ]
        
        conn.executemany('INSERT INTO submissions (problem_id, code, language, status) VALUES (?, ?, ?, ?)', submissions)
    
    conn.commit()
    conn.close()

@app.route('/')
def home():
    """Home page route."""
    return render_template('home.html')

@app.route('/problems')
def problems():
    """Problem list page route."""
    conn = get_db_connection()
    problems = conn.execute('SELECT * FROM problems ORDER BY id').fetchall()
    conn.close()
    return render_template('problems.html', problems=problems)

@app.route('/problem/<int:problem_id>')
def problem_detail(problem_id):
    """Problem detail page route."""
    conn = get_db_connection()
    problem = conn.execute('SELECT * FROM problems WHERE id = ?', (problem_id,)).fetchone()
    conn.close()
    if problem is None:
        return "Problem not found", 404
    return render_template('problem_detail.html', problem=problem)

@app.route('/submit/<int:problem_id>', methods=['GET', 'POST'])
def submit(problem_id):
    """Submit code page route."""
    conn = get_db_connection()
    problem = conn.execute('SELECT * FROM problems WHERE id = ?', (problem_id,)).fetchone()
    
    if request.method == 'POST':
        code = request.form['code']
        language = request.form['language']
        
        # Simulate evaluation - in a real system, this would run the code
        # For now, we'll just mark it as "Pending"
        status = 'Pending'
        
        conn.execute('INSERT INTO submissions (problem_id, code, language, status) VALUES (?, ?, ?, ?)',
                    (problem_id, code, language, status))
        conn.commit()
        
        # Get the submission ID
        submission_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.close()
        
        return redirect(url_for('submission_result', submission_id=submission_id))
    
    conn.close()
    return render_template('submit.html', problem=problem)

@app.route('/submissions')
def submissions():
    """View all submissions route."""
    conn = get_db_connection()
    submissions = conn.execute('''
        SELECT s.*, p.title 
        FROM submissions s
        JOIN problems p ON s.problem_id = p.id
        ORDER BY s.submitted_at DESC
    ''').fetchall()
    conn.close()
    return render_template('submissions.html', submissions=submissions)

@app.route('/submission/<int:submission_id>')
def submission_result(submission_id):
    """View submission result route."""
    conn = get_db_connection()
    submission = conn.execute('''
        SELECT s.*, p.title, p.description
        FROM submissions s
        JOIN problems p ON s.problem_id = p.id
        WHERE s.id = ?
    ''', (submission_id,)).fetchone()
    conn.close()
    
    if submission is None:
        return "Submission not found", 404
    
    return render_template('submission_result.html', submission=submission)

if __name__ == '__main__':
    # Initialize database
    if not os.path.exists(app.config['DATABASE']):
        init_db()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
