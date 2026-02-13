"""Tests for formatters - EXPANDED COVERAGE."""

import pytest
from datetime import timedelta
from zealous.utils.formatters import (
    format_duration,
    format_currency,
    format_percentage,
    format_file_size,
    format_number,
    format_timedelta,
    truncate_text,
)


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


class TestFormatCurrency:
    """Test currency formatting - NEW TESTS."""

    def test_format_currency_usd_default(self):
        """Test formatting USD with default locale."""
        assert format_currency(1234.56) == "$1,234.56"
        assert format_currency(0.99) == "$0.99"

    def test_format_currency_usd_large_amount(self):
        """Test formatting large USD amount."""
        assert format_currency(1000000.00) == "$1,000,000.00"

    def test_format_currency_eur(self):
        """Test formatting EUR."""
        assert format_currency(1234.56, "EUR") == "€1,234.56"

    def test_format_currency_gbp(self):
        """Test formatting GBP."""
        assert format_currency(999.99, "GBP") == "£999.99"

    def test_format_currency_jpy(self):
        """Test formatting JPY without decimals."""
        assert format_currency(1234.56, "JPY") == "¥1,234"
        assert format_currency(1000, "JPY") == "¥1,000"

    def test_format_currency_inr(self):
        """Test formatting INR."""
        assert format_currency(5000.50, "INR") == "₹5,000.50"

    def test_format_currency_unknown(self):
        """Test formatting unknown currency."""
        result = format_currency(100.00, "XYZ")
        assert "100.00" in result
        assert "XYZ" in result

    def test_format_currency_german_locale(self):
        """Test formatting with German locale."""
        result = format_currency(1234.56, "EUR", "de_DE")
        assert "1.234,56" in result

    def test_format_currency_zero(self):
        """Test formatting zero amount."""
        assert format_currency(0.0) == "$0.00"


class TestFormatPercentage:
    """Test percentage formatting - NEW TESTS."""

    def test_format_percentage_default(self):
        """Test formatting percentage with default settings."""
        assert format_percentage(50.5) == "50.5%"
        assert format_percentage(0.0) == "0.0%"

    def test_format_percentage_no_decimals(self):
        """Test formatting percentage with no decimal places."""
        assert format_percentage(75.8, decimal_places=0) == "76%"

    def test_format_percentage_multiple_decimals(self):
        """Test formatting percentage with multiple decimal places."""
        assert format_percentage(33.333333, decimal_places=2) == "33.33%"
        assert format_percentage(66.666666, decimal_places=3) == "66.667%"

    def test_format_percentage_with_positive_sign(self):
        """Test formatting positive percentage with sign."""
        assert format_percentage(25.5, include_sign=True) == "+25.5%"

    def test_format_percentage_negative(self):
        """Test formatting negative percentage."""
        assert format_percentage(-10.5) == "-10.5%"
        assert format_percentage(-10.5, include_sign=True) == "-10.5%"

    def test_format_percentage_zero_with_sign(self):
        """Test formatting zero with sign."""
        assert format_percentage(0.0, include_sign=True) == "0.0%"


class TestFormatFileSize:
    """Test file size formatting - NEW TESTS."""

    def test_format_file_size_bytes(self):
        """Test formatting bytes."""
        assert format_file_size(0) == "0 B"
        assert format_file_size(500) == "500 B"
        assert format_file_size(1023) == "1023 B"

    def test_format_file_size_kilobytes(self):
        """Test formatting kilobytes."""
        assert format_file_size(1024) == "1.00 KB"
        assert format_file_size(2048) == "2.00 KB"
        assert format_file_size(1536) == "1.50 KB"

    def test_format_file_size_megabytes(self):
        """Test formatting megabytes."""
        assert format_file_size(1048576) == "1.00 MB"
        assert format_file_size(5242880) == "5.00 MB"

    def test_format_file_size_gigabytes(self):
        """Test formatting gigabytes."""
        assert format_file_size(1073741824) == "1.00 GB"
        assert format_file_size(2147483648) == "2.00 GB"

    def test_format_file_size_terabytes(self):
        """Test formatting terabytes."""
        assert format_file_size(1099511627776) == "1.00 TB"

    def test_format_file_size_petabytes(self):
        """Test formatting petabytes."""
        assert format_file_size(1125899906842624) == "1.00 PB"

    def test_format_file_size_negative(self):
        """Test formatting negative size."""
        assert format_file_size(-100) == "0 B"

    def test_format_file_size_fractional(self):
        """Test formatting fractional units."""
        result = format_file_size(1536000)
        assert "MB" in result


class TestFormatNumber:
    """Test number formatting - NEW TESTS."""

    def test_format_number_default(self):
        """Test formatting number without abbreviation."""
        assert format_number(1000) == "1,000"
        assert format_number(1000000) == "1,000,000"
        assert format_number(123456789) == "123,456,789"

    def test_format_number_small(self):
        """Test formatting small numbers."""
        assert format_number(0) == "0"
        assert format_number(999) == "999"

    def test_format_number_abbreviate_thousands(self):
        """Test abbreviating thousands."""
        assert format_number(1000, abbreviate=True) == "1.0K"
        assert format_number(5500, abbreviate=True) == "5.5K"
        assert format_number(999000, abbreviate=True) == "999.0K"

    def test_format_number_abbreviate_millions(self):
        """Test abbreviating millions."""
        assert format_number(1000000, abbreviate=True) == "1.0M"
        assert format_number(2500000, abbreviate=True) == "2.5M"
        assert format_number(999000000, abbreviate=True) == "999.0M"

    def test_format_number_abbreviate_billions(self):
        """Test abbreviating billions."""
        assert format_number(1000000000, abbreviate=True) == "1.0B"
        assert format_number(5500000000, abbreviate=True) == "5.5B"

    def test_format_number_abbreviate_small(self):
        """Test abbreviating small numbers (no abbreviation)."""
        assert format_number(999, abbreviate=True) == "999"
        assert format_number(100, abbreviate=True) == "100"


class TestFormatTimedelta:
    """Test timedelta formatting - NEW TESTS."""

    def test_format_timedelta_seconds(self):
        """Test formatting seconds timedelta."""
        assert format_timedelta(timedelta(seconds=30)) == "30 seconds"
        assert format_timedelta(timedelta(seconds=1)) == "1 second"

    def test_format_timedelta_minutes(self):
        """Test formatting minutes timedelta."""
        assert format_timedelta(timedelta(minutes=5)) == "5 minutes"
        assert format_timedelta(timedelta(minutes=1)) == "1 minute"

    def test_format_timedelta_hours(self):
        """Test formatting hours timedelta."""
        assert format_timedelta(timedelta(hours=2)) == "2 hours"
        assert format_timedelta(timedelta(hours=1)) == "1 hour"

    def test_format_timedelta_days(self):
        """Test formatting days timedelta."""
        assert format_timedelta(timedelta(days=3)) == "3 days"
        assert format_timedelta(timedelta(days=1)) == "1 day"

    def test_format_timedelta_combined(self):
        """Test formatting combined units."""
        delta = timedelta(days=2, hours=3, minutes=15, seconds=45)
        result = format_timedelta(delta)
        assert "2 days" in result
        assert "3 hours" in result
        assert "15 minutes" in result
        assert "45 seconds" in result

    def test_format_timedelta_zero(self):
        """Test formatting zero timedelta."""
        assert format_timedelta(timedelta(seconds=0)) == "0 seconds"

    def test_format_timedelta_negative(self):
        """Test formatting negative timedelta."""
        assert format_timedelta(timedelta(seconds=-100)) == "0 seconds"

    def test_format_timedelta_only_days_and_hours(self):
        """Test formatting with only days and hours."""
        delta = timedelta(days=1, hours=6)
        result = format_timedelta(delta)
        assert "1 day" in result
        assert "6 hours" in result
        assert "minute" not in result


class TestTruncateText:
    """Test text truncation - NEW TESTS."""

    def test_truncate_text_no_truncation(self):
        """Test text shorter than max length."""
        text = "Short text"
        assert truncate_text(text, 20) == "Short text"

    def test_truncate_text_exact_length(self):
        """Test text exactly at max length."""
        text = "Exactly twenty chars"
        assert truncate_text(text, 20) == text

    def test_truncate_text_needs_truncation(self):
        """Test text longer than max length."""
        text = "This is a very long text that needs to be truncated"
        result = truncate_text(text, 20)
        assert len(result) == 20
        assert result.endswith("...")

    def test_truncate_text_custom_suffix(self):
        """Test truncation with custom suffix."""
        text = "This is too long"
        result = truncate_text(text, 10, suffix=" [more]")
        assert result.endswith(" [more]")
        assert len(result) == 10

    def test_truncate_text_empty_suffix(self):
        """Test truncation with empty suffix."""
        text = "This is a long text"
        result = truncate_text(text, 10, suffix="")
        assert len(result) == 10
        assert not result.endswith("...")

    def test_truncate_text_very_short_limit(self):
        """Test truncation with very short limit."""
        text = "Hello World"
        result = truncate_text(text, 5)
        assert len(result) == 5
        assert result == "He..."

    def test_truncate_text_unicode(self):
        """Test truncating Unicode text."""
        text = "Hello 世界! This is a test"
        result = truncate_text(text, 15)
        assert len(result) == 15
        assert result.endswith("...")
