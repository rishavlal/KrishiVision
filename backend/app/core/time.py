"""UTC storage and Indian local-time display helpers."""

from datetime import datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo

INDIA_TIMEZONE = ZoneInfo("Asia/Kolkata")


def as_utc(value: datetime) -> datetime:
    """Treat naive database timestamps as UTC and normalize aware values to UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def utc_isoformat(value: Optional[datetime]) -> str:
    """Serialize a timestamp as an unambiguous UTC ISO-8601 value."""
    if value is None:
        return ""
    return as_utc(value).isoformat().replace("+00:00", "Z")


def format_india_datetime(value: Optional[datetime]) -> str:
    """Format a UTC database timestamp for Indian users."""
    if value is None:
        return "Date unavailable"
    return as_utc(value).astimezone(INDIA_TIMEZONE).strftime("%d %b %Y, %I:%M %p")
