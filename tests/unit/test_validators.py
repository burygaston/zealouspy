"""Tests for validators - PARTIAL COVERAGE."""

import pytest
from zealous.utils.validators import validate_email


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

    # NOTE: validate_url, validate_date_range, validate_password_strength,
    # validate_phone_number, validate_username are NOT tested
