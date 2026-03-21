"""
Shared utilities for output consumers.

Provides formatting, statistics calculations, and helper functions
used across all output consumer implementations.
"""

from typing import Dict, Any, List
from datetime import datetime


def format_value(value: Any, decimals: int = 2) -> str:
    """
    Format a numeric value for display.

    Args:
        value: Value to format
        decimals: Number of decimal places

    Returns:
        Formatted string
    """
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.{decimals}f}"
    except (TypeError, ValueError):
        return str(value)


def format_statistics(stats: Dict[str, Any]) -> str:
    """
    Format statistics dictionary as readable string.

    Args:
        stats: Statistics dict from BaseOutputConsumer.get_statistics()

    Returns:
        Formatted string suitable for console display
    """
    lines = [
        "─" * 50,
        "RUNNING STATISTICS",
        "─" * 50,
        f"  Count:    {stats['count']:>10}",
        f"  Current:  {format_value(stats['current']):>10}",
        f"  Average:  {format_value(stats['average']):>10}",
        f"  Min:      {format_value(stats['min']):>10}",
        f"  Max:      {format_value(stats['max']):>10}",
        f"  Duration: {format_duration(stats['duration']):>10}",
        "─" * 50,
    ]
    return "\n".join(lines)


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string like "1m 23s" or "45s"
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def format_timestamp() -> str:
    """
    Get current timestamp formatted for display.

    Returns:
        Formatted string like "2026-03-17 14:30:45"
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def create_table_row(columns: List[str], widths: List[int]) -> str:
    """
    Create a formatted table row.

    Args:
        columns: List of column values
        widths: List of column widths

    Returns:
        Formatted row string
    """
    formatted = []
    for col, width in zip(columns, widths):
        formatted.append(str(col).ljust(width))
    return "│ " + " │ ".join(formatted) + " │"


def create_table_separator(widths: List[int]) -> str:
    """
    Create a table separator line.

    Args:
        widths: List of column widths

    Returns:
        Separator line string
    """
    seps = ["─" * (w + 2) for w in widths]
    return "├" + "┼".join(seps) + "┤"


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp value between min and max.

    Args:
        value: Value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))
