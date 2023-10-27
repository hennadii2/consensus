from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import pytest  # type: ignore
from web.backend.app.common.rate_limit import denied_by_rate_limit
from web.backend.app.common.test.redis_connection import RedisTestConnection

TEST_URL = "http://backend:8080/unit_test/extra/params"


@dataclass(frozen=True)
class CacheKeys:
    blocked_for_min: str
    blocked_for_day: str


def get_cache_keys(user_or_ip: str, url: str) -> CacheKeys:
    parsed_url = urlparse(url)
    url_path = parsed_url.path.split("/")[1]
    prefix = f"rate_limit:{user_or_ip}_{url_path}"
    return CacheKeys(
        blocked_for_min=f"{prefix}_min_blocked",
        blocked_for_day=f"{prefix}_day_blocked",
    )


@pytest.fixture
def redis():
    with RedisTestConnection() as redis:
        yield redis


def test_denied_by_rate_limit_allows_different_users(redis) -> None:
    user1 = "user1"
    ip1 = "localhost"
    user2 = "user2"
    ip2 = "0.0.0.0"

    ts = datetime(year=2022, month=10, day=1, hour=1, minute=30, second=0, tzinfo=timezone.utc)
    for i in range(0, 5):
        assert not denied_by_rate_limit(
            redis=redis,
            user=user1,
            ip_address=ip1,
            url=TEST_URL,
            timestamp_utc=ts + timedelta(seconds=i),
        )

    # Confirm that 1st user becomes blocked
    assert denied_by_rate_limit(
        redis=redis,
        user=user1,
        ip_address=ip1,
        url=TEST_URL,
        timestamp_utc=ts + timedelta(seconds=59),
    )
    assert denied_by_rate_limit(
        redis=redis,
        user=user1,
        ip_address=ip1,
        url=TEST_URL,
        timestamp_utc=ts + timedelta(seconds=62),
    )

    # Confirm that 2nd user is still not blocked
    assert not denied_by_rate_limit(
        redis=redis,
        user=user2,
        ip_address=ip2,
        url=TEST_URL,
        timestamp_utc=ts + timedelta(seconds=59),
    )
    assert not denied_by_rate_limit(
        redis=redis,
        user=user2,
        ip_address=ip2,
        url=TEST_URL,
        timestamp_utc=ts + timedelta(seconds=62),
    )


def test_denied_by_rate_limit_blocks_different_user_same_ip(redis) -> None:
    user1 = "user1"
    user2 = "user2"
    ip_addr = "localhost"

    ts = datetime(year=2022, month=10, day=1, hour=1, minute=30, second=0, tzinfo=timezone.utc)
    for i in range(0, 5):
        assert not denied_by_rate_limit(
            redis=redis,
            user=user1,
            ip_address=ip_addr,
            url=TEST_URL,
            timestamp_utc=ts + timedelta(seconds=i),
        )

    # Confirm that 2nd user with same IP address is NOT blocked ( for now )
    assert not denied_by_rate_limit(
        redis=redis,
        user=user2,
        ip_address=ip_addr,
        url=TEST_URL,
        timestamp_utc=ts + timedelta(seconds=59),
    )


def test_denied_by_rate_limit_blocks_same_user_different_ip(redis) -> None:
    user = "user1"
    ip_addr1 = "0.0.0.0"
    ip_addr2 = "localhost"

    ts = datetime(year=2022, month=10, day=1, hour=1, minute=30, second=0, tzinfo=timezone.utc)
    for i in range(0, 5):
        assert not denied_by_rate_limit(
            redis=redis,
            user=user,
            ip_address=ip_addr1,
            url=TEST_URL,
            timestamp_utc=ts + timedelta(seconds=i),
        )

    # Confirm that 2nd IP address for the same user becomes blocked
    assert denied_by_rate_limit(
        redis=redis,
        user=user,
        ip_address=ip_addr2,
        url=TEST_URL,
        timestamp_utc=ts + timedelta(seconds=59),
    )


def test_denied_by_rate_limit_allows_all_search_index_bots(redis) -> None:
    ts = datetime(year=2022, month=10, day=1, hour=1, minute=30, second=0, tzinfo=timezone.utc)
    for i in range(0, 20):
        assert not denied_by_rate_limit(
            redis=redis,
            user=None,
            ip_address="20.191.45.212",
            url=TEST_URL,
            timestamp_utc=ts + timedelta(seconds=i),
        )
        is_non_search_index_denied = denied_by_rate_limit(
            redis=redis,
            user=None,
            ip_address="localhost",
            url=TEST_URL,
            timestamp_utc=ts + timedelta(seconds=i),
        )
        if i < 5:
            assert not is_non_search_index_denied
        else:
            assert is_non_search_index_denied


def test_denied_by_rate_limit_allows_user_across_minutes(redis) -> None:
    ts = datetime(year=2022, month=10, day=1, hour=1, minute=30, second=0, tzinfo=timezone.utc)
    for i in range(0, 5):
        assert not denied_by_rate_limit(
            redis=redis,
            user="test",
            ip_address="localhost",
            url=TEST_URL,
            timestamp_utc=ts + timedelta(seconds=i),
        )
    # On the next run in the a different minute, we do not go over a single
    # minute limit so we are allowed
    assert not denied_by_rate_limit(
        redis=redis,
        user="test",
        ip_address="localhost",
        url=TEST_URL,
        timestamp_utc=ts + timedelta(seconds=61),
    )
    assert not denied_by_rate_limit(
        redis=redis,
        user="test",
        ip_address="localhost",
        url=TEST_URL,
        timestamp_utc=ts + timedelta(seconds=62),
    )


def test_denied_by_rate_limit_blocks_user_once_reaching_min_limit(redis) -> None:
    ts = datetime(year=2022, month=10, day=1, hour=1, minute=30, second=0, tzinfo=timezone.utc)
    for i in range(0, 5):
        assert not denied_by_rate_limit(
            redis=redis,
            user="test",
            ip_address="localhost",
            url=TEST_URL,
            timestamp_utc=ts + timedelta(seconds=i),
        )
    # On the next run in the same minute, we are denied by the rate limiter
    assert denied_by_rate_limit(
        redis=redis,
        user="test",
        ip_address="localhost",
        url=TEST_URL,
        timestamp_utc=ts + timedelta(seconds=59),
    )
    # If we try again even on the next min we are still blocked
    assert denied_by_rate_limit(
        redis=redis,
        user="test",
        ip_address="localhost",
        url=TEST_URL,
        timestamp_utc=ts + timedelta(seconds=61),
    )

    # Deleting the blocked key will allow us
    user_cache = get_cache_keys(user_or_ip="test", url=TEST_URL)
    ip_cache = get_cache_keys(user_or_ip="localhost", url=TEST_URL)
    redis.delete(user_cache.blocked_for_min)
    redis.delete(ip_cache.blocked_for_min)
    assert not denied_by_rate_limit(
        redis=redis,
        user="test",
        ip_address="localhost",
        url=TEST_URL,
        timestamp_utc=ts + timedelta(seconds=61),
    )


def test_denied_by_rate_limit_allows_user_across_days(redis) -> None:
    ts = datetime(year=2022, month=10, day=1, hour=1, minute=30, second=0, tzinfo=timezone.utc)
    for i in range(0, 10):
        assert not denied_by_rate_limit(
            redis=redis,
            user="test",
            ip_address="localhost",
            url=TEST_URL,
            timestamp_utc=ts + timedelta(minutes=i),
        )
    # On the next run in the a different day, we do not go over a single
    # day limit so we are allowed
    assert not denied_by_rate_limit(
        redis=redis,
        user="test",
        ip_address="localhost",
        url=TEST_URL,
        timestamp_utc=ts + timedelta(days=1),
    )


def test_denied_by_rate_limit_blocks_user_once_reaching_day_limit(redis) -> None:
    ts = datetime(year=2022, month=10, day=1, hour=1, minute=30, second=0, tzinfo=timezone.utc)
    for i in range(0, 10):
        assert not denied_by_rate_limit(
            redis=redis,
            user="test",
            ip_address="localhost",
            url=TEST_URL,
            timestamp_utc=ts + timedelta(minutes=i),
        )
    # On the next run, we are denied by the rate limiter
    assert denied_by_rate_limit(
        redis=redis,
        user="test",
        ip_address="localhost",
        url=TEST_URL,
        timestamp_utc=ts + timedelta(minutes=201),
    )

    # If we try again even on the next day we are still blocked
    assert denied_by_rate_limit(
        redis=redis,
        user="test",
        ip_address="localhost",
        url=TEST_URL,
        timestamp_utc=ts + timedelta(days=1),
    )

    # Deleting the blocked key will allow us
    user_cache = get_cache_keys(user_or_ip="test", url=TEST_URL)
    ip_cache = get_cache_keys(user_or_ip="localhost", url=TEST_URL)
    redis.delete(user_cache.blocked_for_day)
    redis.delete(ip_cache.blocked_for_day)
    assert not denied_by_rate_limit(
        redis=redis,
        user="test",
        ip_address="localhost",
        url=TEST_URL,
        timestamp_utc=ts + timedelta(days=1),
    )
