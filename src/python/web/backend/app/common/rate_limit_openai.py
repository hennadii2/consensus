from datetime import datetime, timedelta, timezone
from typing import Optional

import pytz
import redis

DEFAULT_DAILY_LIMIT = 12500


def denied_by_daily_cost_limit(
    redis: redis.Redis,
    cost_units: Optional[int] = None,
    timestamp_utc: Optional[datetime] = None,
    daily_limit: Optional[int] = None,
) -> bool:
    cost = 1 if cost_units is None else cost_units

    # Restart bucket daily usage count at 7am ET, so consider (ET - 7 hours) midnight
    ts_utc = datetime.now(timezone.utc) if timestamp_utc is None else timestamp_utc
    ts_etc_7am = ts_utc.astimezone(pytz.timezone("US/Eastern")) - timedelta(hours=7)

    daily_cache_key = f"openai_daily:{ts_etc_7am.strftime('%Y%m%d')}"
    daily_usage = redis.incrby(name=daily_cache_key, amount=cost)

    max_requests = DEFAULT_DAILY_LIMIT if daily_limit is None else daily_limit
    exceeded_cache = daily_usage > max_requests
    return exceeded_cache
