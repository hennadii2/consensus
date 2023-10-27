from datetime import datetime, timezone

from common.time.convert import TimeUnit, datetime_to_unix, unix_to_datetime


def test_datetime_to_unix_ts_succeeds() -> None:
    expected = 1539065539013988
    dt = datetime(
        year=2018,
        month=10,
        day=9,
        hour=6,
        minute=12,
        second=19,
        microsecond=13988,
        tzinfo=timezone.utc,
    )

    usec = datetime_to_unix(dt, TimeUnit.MICROSECONDS)
    assert usec == expected

    msec = datetime_to_unix(dt, TimeUnit.MILLISECONDS)
    assert msec == round(expected / 1e3)
    assert msec == 1539065539014

    sec = datetime_to_unix(dt, TimeUnit.SECONDS)
    assert sec == round(expected / 1e6)
    assert sec == 1539065539


def test_unix_ts_to_datetime_succeeds() -> None:
    expected = datetime(
        year=2018,
        month=10,
        day=9,
        hour=6,
        minute=12,
        second=19,
        microsecond=13988,
        tzinfo=timezone.utc,
    )
    usec = datetime_to_unix(expected, TimeUnit.MICROSECONDS)
    actual = unix_to_datetime(usec, TimeUnit.MICROSECONDS)
    assert actual == expected

    expected = datetime(
        year=2018,
        month=10,
        day=9,
        hour=6,
        minute=12,
        second=19,
        microsecond=13000,
        tzinfo=timezone.utc,
    )
    msec = datetime_to_unix(expected, TimeUnit.MILLISECONDS)
    actual = unix_to_datetime(msec, TimeUnit.MILLISECONDS)
    assert actual == expected

    expected = datetime(
        year=2018,
        month=10,
        day=9,
        hour=6,
        minute=12,
        second=19,
        tzinfo=timezone.utc,
    )
    sec = datetime_to_unix(expected, TimeUnit.SECONDS)
    actual = unix_to_datetime(sec, TimeUnit.SECONDS)
    assert actual == expected
