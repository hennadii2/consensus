from datetime import datetime, timezone
from enum import Enum


class TimeUnit(Enum):
    MICROSECONDS = 1
    MILLISECONDS = 2
    SECONDS = 3


TIME_UNIT_BASE = {
    TimeUnit.MICROSECONDS: 1e6,
    TimeUnit.MILLISECONDS: 1e3,
    TimeUnit.SECONDS: 1,
}


def validate_datetime(dt: datetime) -> None:
    if dt.tzinfo != timezone.utc:
        raise ValueError(f"Datetime must be in timezone UTC, found: {dt.tzinfo}")


def datetime_to_unix(dt: datetime, unit: TimeUnit) -> int:
    """Converts a datetime object into a unix epoch integer."""
    validate_datetime(dt)
    base = TIME_UNIT_BASE[unit]
    return round(datetime.timestamp(dt) * base)


def unix_to_datetime(unix_ts: int, unit: TimeUnit) -> datetime:
    """Converts a unix epoch integer into a datetime object."""
    base = TIME_UNIT_BASE[unit]
    dt = datetime.fromtimestamp(unix_ts / base, tz=timezone.utc)
    validate_datetime(dt)
    return dt
