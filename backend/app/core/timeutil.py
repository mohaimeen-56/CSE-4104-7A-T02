from datetime import date, datetime, timedelta
from typing import Optional, Tuple
from zoneinfo import ZoneInfo

# SalesIQ's business timezone. All sale_datetime values are stored as
# timezone-aware UTC (Postgres TIMESTAMPTZ semantics) but time-of-day inputs
# from users/CSV are interpreted as local Dhaka time.
APP_TIMEZONE = ZoneInfo("Asia/Dhaka")


def parse_time_of_day(raw: str) -> Optional[Tuple[int, int, int]]:
    """Parse 'HH:MM' or 'HH:MM:SS' into (hour, minute, second). Returns None if invalid."""
    if not raw or not raw.strip():
        return None
    parts = raw.strip().split(":")
    if len(parts) not in (2, 3):
        return None
    try:
        hh = int(parts[0])
        mm = int(parts[1])
        ss = int(parts[2]) if len(parts) == 3 else 0
        if not (0 <= hh <= 23 and 0 <= mm <= 59 and 0 <= ss <= 59):
            return None
        return hh, mm, ss
    except ValueError:
        return None


def build_sale_datetime(sale_date: date, sale_time: Optional[str]) -> Tuple[datetime, bool]:
    """
    Combine a sale_date with an optional time-of-day string into a timezone-aware
    sale_datetime, per SalesIQ's server-authoritative timestamp policy:

    - If a valid sale_time is supplied, use it exactly (captured, not estimated).
    - If sale_time is missing/invalid, fall back to the server's current time-of-day
      (never a client-supplied clock) applied to the given sale_date, and flag the
      row as an estimate so data-quality reporting can distinguish it from a real
      captured timestamp.
    """
    parsed = parse_time_of_day(sale_time) if sale_time else None
    if parsed:
        hh, mm, ss = parsed
        return datetime(sale_date.year, sale_date.month, sale_date.day, hh, mm, ss, tzinfo=APP_TIMEZONE), False

    now_local = datetime.now(APP_TIMEZONE)
    dt = datetime(
        sale_date.year, sale_date.month, sale_date.day,
        now_local.hour, now_local.minute, now_local.second,
        tzinfo=APP_TIMEZONE,
    )
    return dt, True


DATE_RANGE_PRESETS = [
    "today", "yesterday", "this_week", "last_7_days", "this_month", "last_month", "custom",
]


def resolve_date_range_preset(preset: str) -> Tuple[Optional[date], Optional[date]]:
    """Resolve a named preset (Today/Yesterday/This Week/Last 7 Days/This Month/Last Month)
    into a (start_date, end_date) pair, evaluated against the current date in Asia/Dhaka.
    'custom'/unknown presets return (None, None) - caller supplies explicit dates instead."""
    today = datetime.now(APP_TIMEZONE).date()

    if preset == "today":
        return today, today
    if preset == "yesterday":
        y = today - timedelta(days=1)
        return y, y
    if preset == "this_week":
        start = today - timedelta(days=today.weekday())  # Monday
        return start, today
    if preset == "last_7_days":
        return today - timedelta(days=6), today
    if preset == "this_month":
        return date(today.year, today.month, 1), today
    if preset == "last_month":
        first_of_this_month = date(today.year, today.month, 1)
        last_month_end = first_of_this_month - timedelta(days=1)
        last_month_start = date(last_month_end.year, last_month_end.month, 1)
        return last_month_start, last_month_end

    return None, None
