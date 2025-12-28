"""
Test cases for input validators
Run: python -m pytest test_validators.py
"""

from backend.validators import (
    validate_username,
    validate_email,
    validate_password,
    validate_full_name,
    validate_signup_data,
)


def test_username_validation():
    """Test username validation rules"""
    # Valid usernames
    assert validate_username("john_doe")[0] == True
    assert validate_username("user123")[0] == True
    assert validate_username("test-user")[0] == True

    # Invalid usernames
    assert validate_username("ab")[0] == False  # Too short
    assert validate_username("a" * 21)[0] == False  # Too long
    assert validate_username("user name")[0] == False  # Contains space
    assert validate_username("user@123")[0] == False  # Invalid char
    assert validate_username("")[0] == False  # Empty


def test_email_validation():
    """Test email validation rules"""
    # Valid emails
    assert validate_email("test@example.com")[0] == True
    assert validate_email("user.name@domain.co.uk")[0] == True
    assert validate_email("user+tag@example.org")[0] == True

    # Invalid emails
    assert validate_email("invalid")[0] == False
    assert validate_email("@example.com")[0] == False
    assert validate_email("user@")[0] == False
    assert validate_email("user@domain")[0] == False
    assert validate_email("")[0] == False


def test_password_validation():
    """Test password validation rules"""
    # Valid passwords
    assert validate_password("Password123")[0] == True
    assert validate_password("MyP@ssw0rd")[0] == True
    assert validate_password("Abcd1234")[0] == True

    # Invalid passwords
    assert validate_password("short1A")[0] == False  # Too short
    assert validate_password("alllowercase123")[0] == False  # No uppercase
    assert validate_password("ALLUPPERCASE123")[0] == False  # No lowercase
    assert validate_password("NoNumbers")[0] == False  # No digit
    assert validate_password("")[0] == False  # Empty


def test_full_name_validation():
    """Test full name validation rules"""
    # Valid names
    assert validate_full_name("John Doe")[0] == True
    assert validate_full_name("Mary-Jane")[0] == True
    assert validate_full_name("O'Brien")[0] == True
    assert validate_full_name("")[0] == True  # Optional field

    # Invalid names
    assert validate_full_name("A")[0] == False  # Too short
    assert validate_full_name("John123")[0] == False  # Contains number
    assert validate_full_name("User@Name")[0] == False  # Invalid char


def test_signup_data_validation():
    """Test complete signup data validation"""
    # Valid signup
    is_valid, errors = validate_signup_data(
        "testuser", "test@example.com", "Password123", "Test User"
    )
    assert is_valid == True
    assert len(errors) == 0

    # Invalid signup - multiple errors
    is_valid, errors = validate_signup_data(
        "ab",  # Too short
        "invalid-email",  # Bad format
        "weak",  # Weak password
        "X",  # Name too short
    )
    assert is_valid == False
    assert "username" in errors
    assert "email" in errors
    assert "password" in errors
    assert "full_name" in errors


if __name__ == "__main__":
    print("Running validator tests...")

    test_username_validation()
    print("✓ Username validation tests passed")

    test_email_validation()
    print("✓ Email validation tests passed")

    test_password_validation()
    print("✓ Password validation tests passed")

    test_full_name_validation()
    print("✓ Full name validation tests passed")

    test_signup_data_validation()
    print("✓ Signup data validation tests passed")

    print("\n✅ All tests passed!")
