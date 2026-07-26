"""
Helper utilities for the HOKU Health Care backend.
"""

from datetime import datetime, date, time


def format_datetime(dt: datetime) -> str:
    """Format a datetime object into a human-readable string."""
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_date(d: date) -> str:
    """Format a date object into a human-readable string."""
    if d is None:
        return ""
    return d.strftime("%Y-%m-%d")


def format_time(t: time) -> str:
    """Format a time object into a human-readable 12-hour string."""
    if t is None:
        return ""
    return t.strftime("%I:%M %p")


def paginate_query(query, page: int = 1, page_size: int = 20):
    """
    Apply pagination to a SQLAlchemy query.

    Args:
        query: SQLAlchemy query object.
        page: Page number (1-indexed).
        page_size: Number of items per page.

    Returns:
        Paginated query results.
    """
    if page < 1:
        page = 1
    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size)


def generate_slug(text: str) -> str:
    """Generate a URL-friendly slug from a text string."""
    import re
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug
