"""Tests for validators - COMPREHENSIVE COVERAGE."""

import pytest
from datetime import datetime, timedelta
from zealous.utils.validators import (
    validate_email,
    validate_url,
    validate_date_range,
    validate_password_strength,
    validate_phone_number,
    validate_username,
)


class TestValidators:
    """Test validation utilities."""

    def test_validate_email_valid(self):
        """Test valid emails."""
        assert validate_email("test@example.com") is True
        assert validate_email("user.name@domain.co.uk") is True
        assert validate_email("user+tag@example.org") is True

    def test_validate_email_invalid(self):
        """Test invalid emails."""
        assert validate_email("") is False
        assert validate_email("notanemail") is False
        assert validate_email("missing@domain") is False
        assert validate_email("@nodomain.com") is False

    def test_validate_email_none(self):
        """Test None email."""
        assert validate_email(None) is False

    def test_validate_url_valid(self):
        """Test valid URLs."""
        assert validate_url("http://example.com") is True
        assert validate_url("https://example.com") is True
        assert validate_url("https://example.com/path") is True
        assert validate_url("https://sub.domain.example.com/path?query=value") is True

    def test_validate_url_invalid(self):
        """Test invalid URLs."""
        assert validate_url("") is False
        assert validate_url("notaurl") is False
        assert validate_url("ftp://example.com") is False
        assert validate_url(None) is False

    def test_validate_date_range_both_none(self):
        """Test date range when both dates are None."""
        is_valid, error = validate_date_range(None, None)
        assert is_valid is True
        assert error is None

    def test_validate_date_range_valid_order(self):
        """Test date range with valid start and end dates."""
        start = datetime.utcnow() + timedelta(days=1)
        end = datetime.utcnow() + timedelta(days=5)
        is_valid, error = validate_date_range(start, end)
        assert is_valid is True
        assert error is None

    def test_validate_date_range_invalid_order(self):
        """Test date range with start after end."""
        start = datetime.utcnow() + timedelta(days=5)
        end = datetime.utcnow() + timedelta(days=1)
        is_valid, error = validate_date_range(start, end)
        assert is_valid is False
        assert error == "Start date must be before end date"

    def test_validate_date_range_past_end_date(self):
        """Test date range with end date in the past."""
        start = None
        end = datetime.utcnow() - timedelta(days=1)
        is_valid, error = validate_date_range(start, end)
        assert is_valid is False
        assert error == "End date cannot be in the past"

    def test_validate_date_range_only_start(self):
        """Test date range with only start date."""
        start = datetime.utcnow() + timedelta(days=1)
        is_valid, error = validate_date_range(start, None)
        assert is_valid is True
        assert error is None

    def test_validate_password_strength_valid(self):
        """Test valid strong password."""
        is_valid, error = validate_password_strength("StrongP@ss1")
        assert is_valid is True
        assert error is None

    def test_validate_password_strength_too_short(self):
        """Test password that's too short."""
        is_valid, error = validate_password_strength("Short1!")
        assert is_valid is False
        assert error == "Password must be at least 8 characters"

    def test_validate_password_strength_no_uppercase(self):
        """Test password without uppercase letter."""
        is_valid, error = validate_password_strength("weakpass1!")
        assert is_valid is False
        assert error == "Password must contain at least one uppercase letter"

    def test_validate_password_strength_no_lowercase(self):
        """Test password without lowercase letter."""
        is_valid, error = validate_password_strength("WEAKPASS1!")
        assert is_valid is False
        assert error == "Password must contain at least one lowercase letter"

    def test_validate_password_strength_no_digit(self):
        """Test password without digit."""
        is_valid, error = validate_password_strength("WeakPass!")
        assert is_valid is False
        assert error == "Password must contain at least one digit"

    def test_validate_password_strength_no_special_char(self):
        """Test password without special character."""
        is_valid, error = validate_password_strength("WeakPass1")
        assert is_valid is False
        assert error == "Password must contain at least one special character"

    def test_validate_phone_number_valid(self):
        """Test valid phone numbers."""
        assert validate_phone_number("1234567890") is True
        assert validate_phone_number("+11234567890") is True
        assert validate_phone_number("+44 20 1234 5678") is True
        assert validate_phone_number("(123) 456-7890") is True
        assert validate_phone_number("123.456.7890") is True

    def test_validate_phone_number_invalid(self):
        """Test invalid phone numbers."""
        assert validate_phone_number("") is False
        assert validate_phone_number("123") is False
        assert validate_phone_number("abcdefghij") is False
        assert validate_phone_number(None) is False

    def test_validate_username_valid(self):
        """Test valid usernames."""
        is_valid, error = validate_username("john_doe")
        assert is_valid is True
        assert error is None

        is_valid, error = validate_username("user123")
        assert is_valid is True
        assert error is None

    def test_validate_username_none_or_empty(self):
        """Test None or empty username."""
        is_valid, error = validate_username(None)
        assert is_valid is False
        assert error == "Username is required"

        is_valid, error = validate_username("")
        assert is_valid is False
        assert error == "Username is required"

    def test_validate_username_too_short(self):
        """Test username that's too short."""
        is_valid, error = validate_username("ab")
        assert is_valid is False
        assert error == "Username must be at least 3 characters"

    def test_validate_username_too_long(self):
        """Test username that's too long."""
        is_valid, error = validate_username("a" * 31)
        assert is_valid is False
        assert error == "Username must be at most 30 characters"

    def test_validate_username_invalid_format(self):
        """Test username with invalid format."""
        is_valid, error = validate_username("123user")
        assert is_valid is False
        assert error == "Username must start with a letter and contain only letters, numbers, and underscores"

        is_valid, error = validate_username("user-name")
        assert is_valid is False
        assert error == "Username must start with a letter and contain only letters, numbers, and underscores"
