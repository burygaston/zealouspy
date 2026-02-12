"""Formatting utilities for displaying data in human-readable formats.

Provides functions to format durations, currencies, percentages, file sizes,
numbers, and text truncation.
"""

from datetime import timedelta
from typing import Optional


def format_duration(seconds: int) -> str:
    """Format duration in human-readable format.

    Automatically selects appropriate units (seconds, minutes, hours, days)
    and shows up to two levels of units for clarity.

    Examples:
        - 45 seconds -> "45s"
        - 90 seconds -> "1m 30s"
        - 3665 seconds -> "1h 1m"
        - 86400 seconds -> "1d"

    Args:
        seconds: Duration in seconds (negative values return "0s").

    Returns:
        Human-readable duration string.
    """
    if seconds < 0:
        return "0s"

    if seconds < 60:
        return f"{seconds}s"

    minutes = seconds // 60
    if minutes < 60:
        remaining_seconds = seconds % 60
        if remaining_seconds:
            return f"{minutes}m {remaining_seconds}s"
        return f"{minutes}m"

    hours = minutes // 60
    if hours < 24:
        remaining_minutes = minutes % 60
        if remaining_minutes:
            return f"{hours}h {remaining_minutes}m"
        return f"{hours}h"

    days = hours // 24
    remaining_hours = hours % 24
    if remaining_hours:
        return f"{days}d {remaining_hours}h"
    return f"{days}d"


def format_currency(
    amount: float,
    currency: str = "USD",
    locale: str = "en_US",
) -> str:
    """Format currency amount with appropriate symbol and decimal places.

    Supports multiple currencies and locales with different formatting conventions.

    Args:
        amount: Monetary amount to format.
        currency: Currency code (USD, EUR, GBP, JPY, INR).
        locale: Locale string affecting number format (en_US, de_DE).

    Returns:
        Formatted currency string with symbol.

    Examples:
        - format_currency(1234.56, "USD") -> "$1,234.56"
        - format_currency(1234.56, "EUR", "de_DE") -> "1.234,56 €"
        - format_currency(1234, "JPY") -> "¥1,234"
    """
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "INR": "₹",
    }

    symbol = symbols.get(currency, currency + " ")

    if currency == "JPY":
        # Japanese Yen doesn't use decimal places
        return f"{symbol}{int(amount):,}"

    if locale == "de_DE":
        # German format: 1.234,56
        formatted = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{formatted} {symbol}"

    return f"{symbol}{amount:,.2f}"


def format_percentage(
    value: float,
    decimal_places: int = 1,
    include_sign: bool = False,
) -> str:
    """Format a percentage value.

    Args:
        value: Percentage value (e.g., 25.5 for 25.5%).
        decimal_places: Number of decimal places to show (default: 1).
        include_sign: Whether to include '+' for positive values (default: False).

    Returns:
        Formatted percentage string.

    Examples:
        - format_percentage(25.5) -> "25.5%"
        - format_percentage(25.5, decimal_places=0) -> "26%"
        - format_percentage(25.5, include_sign=True) -> "+25.5%"
    """
    formatted = f"{value:.{decimal_places}f}%"

    if include_sign and value > 0:
        return f"+{formatted}"

    return formatted


def format_file_size(bytes_size: int) -> str:
    """Format file size in human-readable format with appropriate units.

    Automatically selects the best unit (B, KB, MB, GB, TB, PB) to display
    the size concisely.

    Args:
        bytes_size: File size in bytes (negative values return "0 B").

    Returns:
        Human-readable file size string.

    Examples:
        - format_file_size(1024) -> "1.00 KB"
        - format_file_size(1536) -> "1.50 KB"
        - format_file_size(1048576) -> "1.00 MB"
    """
    if bytes_size < 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(bytes_size)
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"

    return f"{size:.2f} {units[unit_index]}"


def format_number(
    value: int,
    abbreviate: bool = False,
) -> str:
    """Format large numbers with thousands separators or abbreviations.

    Args:
        value: Integer value to format.
        abbreviate: Whether to use K/M/B abbreviations for large numbers.

    Returns:
        Formatted number string.

    Examples:
        - format_number(1234567) -> "1,234,567"
        - format_number(1234567, abbreviate=True) -> "1.2M"
        - format_number(1500, abbreviate=True) -> "1.5K"
    """
    if not abbreviate:
        return f"{value:,}"

    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"

    return str(value)


def format_timedelta(delta: timedelta) -> str:
    """Format a timedelta object in human-readable format.

    Shows all non-zero time components with proper pluralization.

    Args:
        delta: timedelta object to format (negative values return "0 seconds").

    Returns:
        Human-readable duration string with comma-separated components.

    Examples:
        - timedelta(seconds=45) -> "45 seconds"
        - timedelta(hours=2, minutes=30) -> "2 hours, 30 minutes"
        - timedelta(days=1, hours=3) -> "1 day, 3 hours"
    """
    total_seconds = int(delta.total_seconds())

    if total_seconds < 0:
        return "0 seconds"

    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    parts = []
    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds or not parts:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

    return ", ".join(parts)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to a maximum length with optional suffix.

    Args:
        text: Text string to truncate.
        max_length: Maximum length including suffix.
        suffix: String to append when truncating (default: "...").

    Returns:
        Original text if within max_length, otherwise truncated text with suffix.

    Examples:
        - truncate_text("Hello World", 20) -> "Hello World"
        - truncate_text("Hello World", 8) -> "Hello..."
        - truncate_text("Hello World", 8, ">>") -> "Hello >>"
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix
