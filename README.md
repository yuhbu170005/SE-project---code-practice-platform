# SE-project---code-practice-platform
A software engineering project with topic: Build a coding practice system like Hakerrank/ Leetcode

## Features

- **Home Page**: Welcome page with feature overview
- **Problems List**: Browse coding problems by difficulty (Easy, Medium, Hard)
- **Problem Details**: View problem descriptions and examples
- **Submit Code**: Write and submit solutions in multiple languages
- **Submissions**: View submission history and results

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yuhbu170005/SE-project---code-practice-platform.git
cd SE-project---code-practice-platform
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## Database

The application uses SQLite for data storage. The database is automatically initialized on first run with sample problems and submissions.

## Tech Stack

- **Backend**: Flask 3.0.0
- **Database**: SQLite
- **Templates**: Jinja2
- **Styling**: Inline CSS

## Project Structure

```
.
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── coding_platform.db     # SQLite database (auto-generated)
└── templates/             # HTML templates
    ├── base.html          # Base template
    ├── home.html          # Home page
    ├── problems.html      # Problems list
    ├── problem_detail.html # Problem details
    ├── submit.html        # Submit code
    ├── submissions.html   # All submissions
    └── submission_result.html # Submission result
```

## Development

This is a basic prototype for educational purposes. For production use:
- Disable debug mode in `app.py`
- Use a production WSGI server (e.g., gunicorn)
- Implement actual code execution and testing
- Add user authentication
- Use a production database (PostgreSQL, MySQL) or SQLite
