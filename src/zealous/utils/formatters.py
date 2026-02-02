"""Formatting utilities - MOSTLY UNTESTED."""

from datetime import timedelta
from typing import Optional


def format_duration(seconds: int) -> str:
    """Format duration in human-readable format - TESTED."""
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
    """Format currency amount - NOT TESTED."""
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
    """Format percentage - NOT TESTED."""
    formatted = f"{value:.{decimal_places}f}%"

    if include_sign and value > 0:
        return f"+{formatted}"

    return formatted


def format_file_size(bytes_size: int) -> str:
    """Format file size in human-readable format - NOT TESTED."""
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
    """Format large numbers - NOT TESTED."""
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
    """Format timedelta in human-readable format - NOT TESTED."""
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
    """Truncate text to max length - NOT TESTED."""
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix
