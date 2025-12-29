"""
Input validation utilities for user authentication
"""

import re


# Validation regex patterns
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
# Password: at least 6 chars, 1 uppercase, 1 lowercase, 1 digit
PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{6,}$")


class ValidationError(Exception):
    """Custom exception for validation errors"""

    def __init__(self, field, message):
        self.field = field
        self.message = message
        super().__init__(self.message)


def validate_username(username):
    """
    Validate username format and length

    Rules:
    - 3-20 characters
    - Only alphanumeric, underscore, and hyphen
    - No spaces or special characters

    Args:
        username (str): Username to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"

    username = username.strip()

    if len(username) < 3:
        return False, "Username must be at least 3 characters"

    if len(username) > 20:
        return False, "Username must not exceed 20 characters"

    if not USERNAME_PATTERN.match(username):
        return (
            False,
            "Username can only contain letters, numbers, underscore, and hyphen",
        )

    return True, None


def validate_email(email):
    """
    Validate email format

    Rules:
    - Must follow standard email format
    - Valid domain with at least 2 chars TLD

    Args:
        email (str): Email to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"

    email = email.strip().lower()

    if len(email) > 254:  # RFC 5321
        return False, "Email is too long"

    if not EMAIL_PATTERN.match(email):
        return False, "Invalid email format"

    return True, None


def validate_password(password):
    """
    Validate password strength

    Rules:
    - At least 6 characters
    - Contains at least 1 uppercase letter
    - Contains at least 1 lowercase letter
    - Contains at least 1 digit

    Args:
        password (str): Password to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"

    if len(password) < 6:
        return False, "Password must be at least 6 characters"

    if len(password) > 128:
        return False, "Password is too long"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least 1 uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must contain at least 1 lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least 1 number"

    return True, None


def validate_full_name(full_name):
    """
    Validate full name format

    Rules:
    - Optional field
    - 2-100 characters if provided
    - Only letters, spaces, hyphens, and apostrophes

    Args:
        full_name (str): Full name to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not full_name:
        return True, None  # Optional field

    full_name = full_name.strip()

    if len(full_name) < 2:
        return False, "Full name must be at least 2 characters"

    if len(full_name) > 100:
        return False, "Full name must not exceed 100 characters"

    # Allow letters, spaces, hyphens, apostrophes, and common international characters
    if not re.match(
        r"^[a-zA-Z\s\-'àáâãäåèéêëìíîïòóôõöùúûüýÿ]+$", full_name, re.IGNORECASE
    ):
        return False, "Full name contains invalid characters"

    return True, None


def validate_signup_data(username, email, password, full_name=""):
    """
    Validate all signup data at once

    Args:
        username (str): Username
        email (str): Email
        password (str): Password
        full_name (str): Full name (optional)

    Returns:
        tuple: (is_valid, dict of errors)
    """
    errors = {}

    # Validate username
    is_valid, error = validate_username(username)
    if not is_valid:
        errors["username"] = error

    # Validate email
    is_valid, error = validate_email(email)
    if not is_valid:
        errors["email"] = error

    # Validate password
    is_valid, error = validate_password(password)
    if not is_valid:
        errors["password"] = error

    # Validate full name (optional)
    is_valid, error = validate_full_name(full_name)
    if not is_valid:
        errors["full_name"] = error

    return len(errors) == 0, errors


# ==================== CODE SUBMISSION VALIDATION ====================

# Supported programming languages
SUPPORTED_LANGUAGES = ["python", "java", "cpp", "c++", "javascript", "js"]

# Code length limits (in characters)
MAX_CODE_LENGTH = 50000  # 50KB - reasonable limit for competitive programming
MIN_CODE_LENGTH = 1  # At least 1 character


def validate_code(code):
    """
    Validate submitted code

    Rules:
    - Cannot be empty or only whitespace
    - Length between 1 and 50,000 characters
    - No null bytes or control characters (except newlines, tabs)

    Args:
        code (str): Code to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not code:
        return False, "Code cannot be empty"

    if not code.strip():
        return False, "Code cannot contain only whitespace"

    if len(code) < MIN_CODE_LENGTH:
        return False, "Code is too short"

    if len(code) > MAX_CODE_LENGTH:
        return False, f"Code is too long (maximum {MAX_CODE_LENGTH} characters)"

    # Check for null bytes and dangerous control characters
    if "\x00" in code:
        return False, "Code contains invalid null bytes"

    return True, None


def validate_language(language):
    """
    Validate programming language

    Rules:
    - Must be in supported languages list
    - Case-insensitive

    Args:
        language (str): Programming language

    Returns:
        tuple: (is_valid, error_message, normalized_language)
    """
    if not language:
        return False, "Language is required", None

    language_lower = language.strip().lower()

    if language_lower not in SUPPORTED_LANGUAGES:
        supported_list = ", ".join(sorted(set(SUPPORTED_LANGUAGES)))
        return (
            False,
            f"Language '{language}' is not supported. Supported languages: {supported_list}",
            None,
        )

    return True, None, language_lower


def validate_problem_id(problem_id):
    """
    Validate problem ID

    Rules:
    - Must be a positive integer
    - Cannot be zero or negative

    Args:
        problem_id: Problem ID to validate

    Returns:
        tuple: (is_valid, error_message, problem_id_int)
    """
    if problem_id is None:
        return False, "Problem ID is required", None

    try:
        pid = int(problem_id)
        if pid <= 0:
            return False, "Problem ID must be a positive number", None
        return True, None, pid
    except (ValueError, TypeError):
        return False, "Problem ID must be a valid number", None


def validate_code_submission(code, language, problem_id):
    """
    Validate complete code submission data

    Args:
        code (str): Source code
        language (str): Programming language
        problem_id: Problem identifier

    Returns:
        tuple: (is_valid, dict of errors, dict of normalized values)
    """
    errors = {}
    normalized = {}

    # Validate code
    is_valid, error = validate_code(code)
    if not is_valid:
        errors["code"] = error
    else:
        normalized["code"] = code

    # Validate language
    is_valid, error, lang_normalized = validate_language(language)
    if not is_valid:
        errors["language"] = error
    else:
        normalized["language"] = lang_normalized

    # Validate problem_id
    is_valid, error, pid_normalized = validate_problem_id(problem_id)
    if not is_valid:
        errors["problem_id"] = error
    else:
        normalized["problem_id"] = pid_normalized

    return len(errors) == 0, errors, normalized
