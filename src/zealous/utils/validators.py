"""Validation utilities - PARTIALLY TESTED."""

import re
from datetime import datetime
from typing import Optional, Tuple


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email or not isinstance(email, str):
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """Validate URL format - NOT TESTED."""
    if not url or not isinstance(url, str):
        return False

    pattern = r'^https?://[a-zA-Z0-9.-]+(?:/[a-zA-Z0-9._~:/?#\[\]@!$&\'()*+,;=-]*)?$'
    return bool(re.match(pattern, url))


def validate_date_range(
    start_date: Optional[datetime],
    end_date: Optional[datetime],
) -> Tuple[bool, Optional[str]]:
    """Validate date range - NOT TESTED."""
    if start_date is None and end_date is None:
        return True, None

    if start_date is not None and end_date is not None:
        if start_date > end_date:
            return False, "Start date must be before end date"

    if end_date is not None and end_date < datetime.utcnow():
        return False, "End date cannot be in the past"

    return True, None


def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """Validate password strength - NOT TESTED."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"

    return True, None


def validate_phone_number(phone: str) -> bool:
    """Validate phone number format - NOT TESTED."""
    if not phone or not isinstance(phone, str):
        return False

    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)

    # Check if it's a valid phone number (10-15 digits, optionally starting with +)
    pattern = r'^\+?\d{10,15}$'
    return bool(re.match(pattern, cleaned))


def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """Validate username - NOT TESTED."""
    if not username or not isinstance(username, str):
        return False, "Username is required"

    if len(username) < 3:
        return False, "Username must be at least 3 characters"

    if len(username) > 30:
        return False, "Username must be at most 30 characters"

    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
        return False, "Username must start with a letter and contain only letters, numbers, and underscores"

    return True, None
