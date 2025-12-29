"""
Application constants and configuration values
Centralized place for all magic numbers and strings
"""

# ==================== USER & AUTHENTICATION ====================
SUPER_ADMIN_USER_ID = 1  # User ID 1 is super admin
DEFAULT_USER_ROLE = "user"
ADMIN_ROLE = "admin"

# ==================== PAGINATION ====================
DEFAULT_PAGE = 1
PROBLEMS_PER_PAGE = 7
MIN_PAGE_NUMBER = 1

# ==================== CODE EXECUTION ====================
# Piston API configuration
PISTON_API_URL = "https://emkc.org/api/v2/piston/execute"
PISTON_TIMEOUT = 5  # seconds
CODE_RUN_TIMEOUT = 3  # seconds

# Supported languages
LANGUAGE_CONFIG = {
    "python": {"language": "python", "version": "3.10.0"},
    "java": {"language": "java", "version": "15.0.2"},
    "cpp": {"language": "cpp", "version": "10.2.0"},
    "c++": {"language": "cpp", "version": "10.2.0"},
    "javascript": {"language": "javascript", "version": "18.15.0"},
    "js": {"language": "javascript", "version": "18.15.0"},
}

# ==================== VALIDATION LIMITS ====================
# Username
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 20

# Email
MAX_EMAIL_LENGTH = 254  # RFC 5321

# Password
MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 128

# Full name
MIN_FULLNAME_LENGTH = 2
MAX_FULLNAME_LENGTH = 100

# Code submission
MIN_CODE_LENGTH = 1
MAX_CODE_LENGTH = 50000  # 50KB

# Problem
MAX_PROBLEM_TITLE_LENGTH = 200
MAX_PROBLEM_DESCRIPTION_LENGTH = 10000

# ==================== DATABASE ====================
DEFAULT_TIME_LIMIT = 1000  # milliseconds
DEFAULT_MEMORY_LIMIT = 256  # MB

# ==================== HTTP STATUS CODES ====================
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_CONFLICT = 409
HTTP_INTERNAL_ERROR = 500

# ==================== ERROR MESSAGES ====================
ERROR_DB_CONNECTION = "Database connection error"
ERROR_DB_QUERY = "Database query failed"
ERROR_INVALID_INPUT = "Invalid input data"
ERROR_UNAUTHORIZED = "Unauthorized access"
ERROR_FORBIDDEN = "Access forbidden"
ERROR_NOT_FOUND = "Resource not found"
ERROR_USER_EXISTS = "Username or email already exists"
ERROR_INVALID_CREDENTIALS = "Invalid username/email or password"

# ==================== SUCCESS MESSAGES ====================
SUCCESS_USER_CREATED = "Registration successful!"
SUCCESS_LOGIN = "Login successful"
SUCCESS_LOGOUT = "Logged out successfully"
SUCCESS_PROBLEM_CREATED = "Problem created successfully"
SUCCESS_PROBLEM_UPDATED = "Problem updated successfully"
SUCCESS_PROBLEM_DELETED = "Problem deleted successfully"
SUCCESS_CODE_SUBMITTED = "Code submitted successfully"
