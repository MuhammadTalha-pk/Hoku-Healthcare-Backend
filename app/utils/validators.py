"""
Custom validators for the HOKU Health Care backend.
"""

import re
from datetime import date, time


def validate_email(email: str) -> bool:
    """Validate an email address format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate a phone number.
    Accepts formats like: +923001234567, 03001234567, 0300-1234567
    """
    pattern = r"^(\+?\d{1,3}[-.\s]?)?\d{10,14}$"
    return bool(re.match(pattern, phone))


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    Returns (is_valid, message).
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    return True, "Password is strong"


def validate_appointment_date(appointment_date: date) -> tuple[bool, str]:
    """Validate that the appointment date is not in the past."""
    if appointment_date < date.today():
        return False, "Appointment date cannot be in the past"
    return True, "Valid date"


def validate_time_range(start_time: time, end_time: time) -> tuple[bool, str]:
    """Validate that start_time is before end_time."""
    if start_time >= end_time:
        return False, "Start time must be before end time"
    return True, "Valid time range"


def validate_rating(rating: int) -> tuple[bool, str]:
    """Validate that rating is between 1 and 5."""
    if not 1 <= rating <= 5:
        return False, "Rating must be between 1 and 5"
    return True, "Valid rating"
