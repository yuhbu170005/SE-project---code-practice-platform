# LiteCode - Code Practice Platform

A modern coding practice platform similar to LeetCode and HackerRank, built with Flask. This is a Software Engineering project that provides an online judge system for practicing algorithms and data structures.

## 🚀 Features

### Core Features
- **Problem Management**
  - Browse problems by difficulty (Easy, Medium, Hard)
  - Filter problems by tags and search by title
  - View detailed problem descriptions with examples and constraints
  - Admin can create, edit, and delete problems

- **Code Editor & Execution**
  - Integrated Monaco Editor (VS Code editor in browser)
  - Multi-language support: Python, Java, C++, JavaScript
  - Run code against test cases
  - Submit solutions for evaluation
  - Real-time code execution using Piston API

- **Submissions**
  - View submission history
  - Detailed submission results with test case outcomes
  - Execution time and memory usage statistics
  - Status tracking (Accepted, Wrong Answer, Runtime Error, etc.)

- **User Authentication**
  - User registration and login
  - Session management
  - Role-based access control (Admin/User)

- **Admin Features**
  - Create and edit problems
  - Manage test cases (sample and hidden)
  - Multi-language starter code support
  - JSON-based test case import/export

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask 3.0.0
- **Database**: MySQL (via mysql-connector-python)
- **API**: Piston API for code execution
- **Authentication**: Flask sessions

### Frontend
- **Templates**: Jinja2
- **CSS Framework**: Bootstrap 5.3.0
- **Icons**: Font Awesome 6.0.0
- **Code Editor**: Monaco Editor 0.36.1
- **Notifications**: SweetAlert2
- **Custom CSS/JS**: Organized in `static/` folder

## 📋 Prerequisites

- Python 3.8+
- MySQL Server
- pip (Python package manager)

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yuhbu170005/SE-project---code-practice-platform.git
   cd SE-project---code-practice-platform
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DB_HOST=localhost
   DB_USER=your_db_username
   DB_PASSWORD=your_db_password
   DB_NAME=your_database_name
   ```

5. **Set up the database**
   
   Create a MySQL database and update the `.env` file with your database credentials.
   
   The database schema will be automatically initialized when you run the application for the first time.

6. **Run the application**
   ```bash
   python3 run.py
   ```

7. **Access the application**
   
   Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## 📁 Project Structure

```
SE-project---code-practice-platform/
├── backend/                    # Backend application code
│   ├── routes/                # Flask route handlers
│   │   ├── auth_routes.py     # Authentication routes
│   │   ├── main_routes.py     # Home page routes
│   │   ├── problem_routes.py  # Problem management routes
│   │   ├── submission_routes.py # Submission routes
│   │   └── judge_routes.py    # Code execution routes
│   ├── services/              # Business logic layer
│   │   ├── auth_service.py    # Authentication logic
│   │   ├── problem_service.py # Problem management logic
│   │   ├── submission_service.py # Submission logic
│   │   ├── tag_service.py     # Tag management
│   │   └── testcase_service.py # Test case management
│   ├── constants.py           # Application constants
│   ├── database.py            # Database connection and initialization
│   ├── utils.py               # Utility functions
│   └── validators.py          # Input validation
│
├── static/                    # Static files
│   ├── css/
│   │   └── style.css          # Custom styles
│   ├── js/                    # JavaScript files (organized)
│   │   ├── main.js            # Global scripts
│   │   ├── problem_detail.js  # Problem detail page logic
│   │   ├── create.js          # Create problem page logic
│   │   ├── edit.js            # Edit problem page logic
│   │   ├── problems.js        # Problems list page logic
│   │   ├── login.js           # Login page logic
│   │   └── signup.js          # Signup page logic
│   └── images/
│       └── logo.png           # Application logo
│
├── templates/                 # HTML templates
│   ├── base.html              # Base template
│   ├── home.html              # Home page
│   ├── login.html             # Login page
│   ├── signup.html            # Signup page
│   ├── problems.html          # Problems list
│   ├── problem_detail.html    # Problem detail with editor
│   ├── create.html            # Create problem (admin)
│   ├── edit.html              # Edit problem (admin)
│   ├── submissions.html       # Submission list
│   └── submission_result.html # Submission details
│
├── config.py                  # Configuration file
├── run.py                     # Application entry point
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🎯 Key Features Details

### Code Execution
- Uses Piston API for secure code execution
- Supports multiple programming languages
- Time and memory limit enforcement
- Test case validation

### Problem Management
- Rich text problem descriptions (Markdown supported)
- Multiple test cases (sample and hidden)
- Starter code templates for multiple languages
- Tag-based categorization

### User Interface
- Responsive design with Bootstrap
- Modern code editor with syntax highlighting
- Real-time feedback on code execution
- Toast notifications for user actions

## 🔐 Default Admin Account

After initial setup, you can create an admin account through the registration page. The first user (ID: 1) is automatically assigned admin privileges.

## 🚦 Usage

1. **As a User**:
   - Register/Login to your account
   - Browse problems from the Problems page
   - Select a problem to view details
   - Write your solution in the code editor
   - Run your code to test against sample cases
   - Submit your solution for final evaluation
   - View your submission history and results

2. **As an Admin**:
   - All user features, plus:
   - Create new problems from the Problems page
   - Edit existing problems
   - Manage test cases and starter code
   - Delete problems

## 🧪 Development

### Running in Development Mode
```bash
# Set DEBUG=True in .env file
python run.py
```

### Code Organization
- **Backend**: Follows MVC pattern with routes, services, and database layers
- **Frontend**: Separated JavaScript files for maintainability
- **Templates**: Jinja2 templates with block inheritance

## 📝 Notes

- This is an educational project for Software Engineering course
- For production deployment:
  - Disable debug mode
  - Use a production WSGI server (e.g., Gunicorn)
  - Set up proper SSL/HTTPS
  - Use environment variables for sensitive data
  - Implement proper error logging
  - Add database backup strategy

## 🤝 Contributing

This is a course project. For contributions or questions, please contact the project maintainers.

## 📄 License

This project is created for educational purposes as part of a Software Engineering course.

## 👥 Authors

Software Engineering Project Team

---

**Built with ❤️ using Flask and modern web technologies**
