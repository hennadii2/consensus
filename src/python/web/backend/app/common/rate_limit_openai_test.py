from datetime import datetime

import pytest  # type: ignore
import pytz
from web.backend.app.common.rate_limit_openai import denied_by_daily_cost_limit
from web.backend.app.common.test.redis_connection import RedisTestConnection


@pytest.fixture
def redis():
    with RedisTestConnection() as redis:
        yield redis


def test_denied_by_openai_rate_limit_resets_at_7am_est(redis) -> None:
    ts = datetime(year=2022, month=10, day=1, hour=6, minute=0, tzinfo=pytz.timezone("US/Eastern"))
    assert not denied_by_daily_cost_limit(
        redis=redis,
        cost_units=1,
        timestamp_utc=ts,
        daily_limit=1,
    )
    assert denied_by_daily_cost_limit(
        redis=redis,
        cost_units=1,
        timestamp_utc=ts,
        daily_limit=1,
    )

    ts = datetime(
        year=2022, month=10, day=1, hour=6, minute=59, tzinfo=pytz.timezone("US/Eastern")
    )
    assert denied_by_daily_cost_limit(
        redis=redis,
        cost_units=1,
        timestamp_utc=ts,
        daily_limit=1,
    )

    ts = datetime(year=2022, month=10, day=1, hour=7, minute=0, tzinfo=pytz.timezone("US/Eastern"))
    assert not denied_by_daily_cost_limit(
        redis=redis,
        cost_units=1,
        timestamp_utc=ts,
        daily_limit=1,
    )

    ts = datetime(year=2022, month=10, day=2, hour=7, minute=0, tzinfo=pytz.timezone("US/Eastern"))
    assert not denied_by_daily_cost_limit(
        redis=redis,
        cost_units=1,
        timestamp_utc=ts,
        daily_limit=1,
    )
