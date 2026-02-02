"""Tests for formatters - MINIMAL COVERAGE."""

import pytest
from zealous.utils.formatters import format_duration


class TestFormatters:
    """Test formatting utilities."""

    def test_format_duration_seconds(self):
        """Test formatting seconds."""
        assert format_duration(30) == "30s"
        assert format_duration(0) == "0s"

    def test_format_duration_minutes(self):
        """Test formatting minutes."""
        assert format_duration(60) == "1m"
        assert format_duration(90) == "1m 30s"
        assert format_duration(300) == "5m"

    def test_format_duration_hours(self):
        """Test formatting hours."""
        assert format_duration(3600) == "1h"
        assert format_duration(5400) == "1h 30m"

    def test_format_duration_days(self):
        """Test formatting days."""
        assert format_duration(86400) == "1d"
        assert format_duration(90000) == "1d 1h"

    def test_format_duration_negative(self):
        """Test negative duration."""
        assert format_duration(-10) == "0s"

    # NOTE: format_currency, format_percentage, format_file_size,
    # format_number, format_timedelta, truncate_text are NOT tested
