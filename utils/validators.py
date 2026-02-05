"""Input validation utilities."""

import re
from typing import Tuple


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, "Password meets requirements"


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username format.
    
    Requirements:
    - 3-30 characters
    - Alphanumeric and underscores only
    - Must start with a letter
    
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 30:
        return False, "Username must not exceed 30 characters"
    
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
        return False, "Username must start with a letter and contain only letters, numbers, and underscores"
    
    return True, "Username is valid"


def sanitize_text_input(text: str) -> str:
    """
    Sanitize text input to prevent XSS and other injection attacks.
    
    Args:
        text: Raw input text
        
    Returns:
        Sanitized text safe for display and storage
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    
    # Escape special HTML characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    return text.strip()


def validate_age(age: int) -> Tuple[bool, str]:
    """Validate age input."""
    if age < 13:
        return False, "You must be at least 13 years old to use this app"
    if age > 120:
        return False, "Please enter a valid age"
    return True, "Age is valid"


def validate_sleep_hours(hours: float) -> Tuple[bool, str]:
    """Validate sleep hours input."""
    if hours < 0:
        return False, "Sleep hours cannot be negative"
    if hours > 24:
        return False, "Sleep hours cannot exceed 24"
    return True, "Sleep hours are valid"
