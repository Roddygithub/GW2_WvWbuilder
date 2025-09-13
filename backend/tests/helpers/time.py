"""Time-related test helpers."""
import datetime
from contextlib import contextmanager
from unittest.mock import patch

from freezegun import freeze_time


@contextmanager
def mock_datetime_utcnow(mock_dt):
    """Mock datetime.utcnow() with a specific datetime.
    
    Args:
        mock_dt: The datetime to use for utcnow()
    """
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.utcnow.return_value = mock_dt
        mock_datetime.now.return_value = mock_dt
        mock_datetime.fromtimestamp.side_effect = lambda *args, **kw: datetime.datetime.fromtimestamp(*args, **kw)
        mock_datetime.side_effect = lambda *args, **kw: datetime.datetime(*args, **kw)
        yield mock_datetime


@contextmanager
def mock_time(time_to_freeze=None):
    """Freeze time for testing time-dependent code.
    
    Args:
        time_to_freeze: Time to freeze (datetime or str), defaults to now
    """
    if time_to_freeze is None:
        time_to_freeze = datetime.datetime.utcnow()
    
    with freeze_time(time_to_freeze) as frozen_time:
        yield frozen_time


def datetime_utc(**kwargs) -> datetime.datetime:
    """Create a UTC datetime with the given components.
    
    Args:
        **kwargs: Components to set (year, month, day, hour, minute, second, microsecond)
        
    Returns:
        A timezone-aware datetime in UTC
    """
    dt = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    
    for key, value in kwargs.items():
        if hasattr(dt, key):
            dt = dt.replace(**{key: value})
    
    return dt


def datetime_utc_iso(**kwargs) -> str:
    """Create an ISO-formatted UTC datetime string.
    
    Args:
        **kwargs: Components to set (year, month, day, hour, minute, second, microsecond)
        
    Returns:
        ISO-formatted datetime string in UTC
    """
    return datetime_utc(**kwargs).isoformat()


def datetime_utc_timestamp(**kwargs) -> float:
    """Create a UTC timestamp.
    
    Args:
        **kwargs: Components to set (year, month, day, hour, minute, second, microsecond)
        
    Returns:
        Timestamp (seconds since epoch)
    """
    return datetime_utc(**kwargs).timestamp()


def datetime_utc_offset(days=0, hours=0, minutes=0, seconds=0) -> datetime.datetime:
    """Create a datetime offset from now.
    
    Args:
        days: Days to add (can be negative)
        hours: Hours to add (can be negative)
        minutes: Minutes to add (can be negative)
        seconds: Seconds to add (can be negative)
        
    Returns:
        A timezone-aware datetime in UTC
    """
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    return now + datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


def assert_datetime_approx_equal(
    dt1: datetime.datetime,
    dt2: datetime.datetime,
    delta_seconds: float = 1.0
) -> None:
    """Assert that two datetimes are approximately equal.
    
    Args:
        dt1: First datetime
        dt2: Second datetime
        delta_seconds: Maximum allowed difference in seconds
    """
    if dt1.tzinfo is None:
        dt1 = dt1.replace(tzinfo=datetime.timezone.utc)
    if dt2.tzinfo is None:
        dt2 = dt2.replace(tzinfo=datetime.timezone.utc)
    
    diff = abs((dt1 - dt2).total_seconds())
    assert diff <= delta_seconds, (
        f"Datetimes differ by {diff} seconds (max {delta_seconds} allowed): "
        f"{dt1} != {dt2}"
    )


@contextmanager
def assert_timing(lo=0.0, hi=1.0):
    """Context manager to assert that code runs within a time range.
    
    Args:
        lo: Minimum expected runtime in seconds
        hi: Maximum allowed runtime in seconds
    """
    import time
    start = time.time()
    try:
        yield
    finally:
        end = time.time()
        duration = end - start
        assert lo <= duration <= hi, f"Code ran in {duration:.3f}s, expected {lo:.3f}-{hi:.3f}s"
