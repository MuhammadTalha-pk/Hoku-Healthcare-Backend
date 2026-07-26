"""
Application-wide constants for the HOKU Health Care backend.
"""

# User Roles
ROLE_PATIENT = "patient"
ROLE_DOCTOR = "doctor"
ROLE_ADMIN = "admin"

VALID_ROLES = [ROLE_PATIENT, ROLE_DOCTOR, ROLE_ADMIN]

# Appointment Statuses
STATUS_PENDING = "pending"
STATUS_CONFIRMED = "confirmed"
STATUS_COMPLETED = "completed"
STATUS_CANCELLED = "cancelled"

VALID_APPOINTMENT_STATUSES = [
    STATUS_PENDING,
    STATUS_CONFIRMED,
    STATUS_COMPLETED,
    STATUS_CANCELLED,
]

# Reminder Frequencies
FREQUENCY_DAILY = "daily"
FREQUENCY_WEEKLY = "weekly"
FREQUENCY_MONTHLY = "monthly"

VALID_FREQUENCIES = [FREQUENCY_DAILY, FREQUENCY_WEEKLY, FREQUENCY_MONTHLY]

# Days of the Week
DAYS_OF_WEEK = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

# Pagination Defaults
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
