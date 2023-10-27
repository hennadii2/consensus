import socket
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse

import redis
from common.time.convert import TimeUnit, datetime_to_unix
from loguru import logger

# NOTE To connect to redis instance:
# - ssh to the compute engine instance redis-forwarder
# - use redis-cli command line to connect to redis instance host and por
# - once connected run [AUTH password], you can find password in gcloud

SECONDS_IN_MIN = 60
SECONDS_IN_DAY = 60 * 60 * 24

ALLOWED_SEARCH_ENGINE_DOMAINS = [
    # Bing
    # https://blogs.bing.com/webmaster/2012/08/31/how-to-verify-that-bingbot-is-bingbot/
    ".search.msn.com",
    # Google
    # https://developers.google.com/search/docs/crawling-indexing/verifying-googlebot
    ".googlebot.com",
    ".google.com",
    # Yandex
    # https://yandex.com/support/webmaster/robot-workings/check-yandex-robots.html
    # ".yandex.com",
    # ".yandex.ru",
    # ".yandex.net",
    # Neeva
    # https://neeva.com/neevabot
    ".neevabot.com",
    # You.com
    # No information found on bots, so use domain directly as best guess
    ".you.com",
    # DuckDuckGo (domains don't resolve, so using hardcoded IP addresses)
    # https://help.duckduckgo.com/duckduckgo-help-pages/results/duckduckbot/
    "20.191.45.212",
    "40.88.21.235",
    "40.76.173.151",
    "40.76.163.7",
    "20.185.79.47",
    "52.142.26.175",
    "20.185.79.15",
    "52.142.24.149",
    "40.76.162.208",
    "40.76.163.23",
    "40.76.162.191",
    "40.76.162.247",
    # Twitter.com (seen in logs)
    # https://developer.twitter.com/en/docs/twitter-for-websites/cards/guides/getting-started#crawling
    ".twttr.com",
    # Semrush
    ".bot.semrush.com",
]


@dataclass(frozen=True)
class Limits:
    minute: int
    day: int


@dataclass(frozen=True)
class PageRateLimit:
    # Rate limits for a logged in user
    logged_in: Limits
    # Rate limits for an anonymous user
    anonymous: Limits


RATE_LIMITS: dict[str, PageRateLimit] = {
    "search": PageRateLimit(
        logged_in=Limits(minute=20, day=300),
        anonymous=Limits(minute=5, day=15),
    ),
    "details": PageRateLimit(
        logged_in=Limits(minute=30, day=500),
        anonymous=Limits(minute=15, day=100),
    ),
    "sitemap": PageRateLimit(
        logged_in=Limits(minute=10, day=100),
        anonymous=Limits(minute=5, day=25),
    ),
    "unit_test": PageRateLimit(
        logged_in=Limits(minute=5, day=10),
        anonymous=Limits(minute=5, day=10),
    ),
}


def _get_rate_limits(url: str, user: Optional[str]) -> Optional[tuple[str, Limits]]:
    parsed_url = urlparse(url)
    url_path = parsed_url.path.split("/")[1]
    # TODO(meganvw): Hard code skipped rate limit for chat gpt open graph, but
    # this should be replaced with a sharing link going forward.
    if url_path == "details" and parsed_url.query == "&utm_source=chatgpt":
        return None
    if url_path not in RATE_LIMITS:
        return None
    if user:
        return (url_path, RATE_LIMITS[url_path].logged_in)
    else:
        return (url_path, RATE_LIMITS[url_path].anonymous)


def _is_search_index_crawler(ip_address: str) -> bool:
    hostname = socket.getfqdn(ip_address)

    # Valid bots will always resolve reverse and forward lookups, so fail if not
    try:
        forward_lookup_to_verify = socket.gethostbyname(hostname)
        if forward_lookup_to_verify != ip_address:
            return False
    except Exception:
        # Will fail if ip address is a username
        return False

    # Check whether the ip address comes from an allowed domain
    for allowed_domain in ALLOWED_SEARCH_ENGINE_DOMAINS:
        if hostname.endswith(allowed_domain):
            return True

    return False


def _is_denied_by_rate_limit(
    redis: redis.Redis,
    key: str,
    page_name: str,
    limits: Limits,
    minutes: int,
    days: int,
    read_only: bool,
) -> bool:
    cache_key_prefix = f"rate_limit:{key}_{page_name}"
    minute_key = f"{cache_key_prefix}_{minutes}"
    day_key = f"{cache_key_prefix}_{days}"
    blocked_for_day_key = f"{cache_key_prefix}_day_blocked"
    blocked_for_min_key = f"{cache_key_prefix}_min_blocked"

    minute_cache = 0
    day_cache = 0
    if read_only:
        minute_value = redis.get(name=minute_key)
        minute_cache = 0 if minute_value is None else int(minute_value)
        day_value = redis.get(name=day_key)
        day_cache = 0 if day_value is None else int(day_value)
    else:
        minute_cache = redis.incrby(name=minute_key, amount=1)
        redis.expire(name=minute_key, time=SECONDS_IN_MIN)
        day_cache = redis.incrby(name=day_key, amount=1)
        redis.expire(name=day_key, time=SECONDS_IN_DAY)

    exceeded_min_limit = minute_cache > limits.minute
    exceeded_day_limit = day_cache > limits.day

    blocked_for_day = redis.get(name=blocked_for_day_key) is not None
    if exceeded_day_limit or blocked_for_day:
        logger.info(f"Blocked by day rate limit: {blocked_for_day_key}")
        if not read_only:
            # If a blocked user makes another request, extend blocked status expiry
            redis.set(name=blocked_for_day_key, value="blocked", ex=SECONDS_IN_DAY)

    blocked_for_min = redis.get(name=blocked_for_min_key) is not None
    if exceeded_min_limit or blocked_for_min:
        logger.info(f"Blocked by minute rate limit: {blocked_for_min_key}")
        if not read_only:
            # If a blocked user makes another request, extend blocked status expiry
            redis.set(name=blocked_for_min_key, value="blocked", ex=SECONDS_IN_MIN)

    return exceeded_day_limit or exceeded_min_limit or blocked_for_day or blocked_for_min


def denied_by_rate_limit(
    redis: redis.Redis,
    url: str,
    user: Optional[str],
    ip_address: Optional[str],
    timestamp_utc: Optional[datetime] = None,
) -> bool:
    """
    Returns true if a user request should be denied for exceeding a request
    rate limit, false otherwise.
    """
    if ip_address is None:
        # TODO(meganvw): Ideally we will fail here, but skip for now to understand
        # which URLs do not have an IP address attached.
        logger.error(f"Failed to rate limit: missing IP: {url}")
        return False

    # Allow all requests to URLs that we have not registered rate limits for
    limits_or_none_if_unregistered = _get_rate_limits(url=url, user=user)
    if limits_or_none_if_unregistered is None:
        return False
    page_name, page_limits = limits_or_none_if_unregistered

    # Always allow "good bot" search index crawlers to skip rate limiting, because
    # we want them to crawl our site and they crawl at rates that our site can
    # handle.
    if _is_search_index_crawler(ip_address):
        return False

    ts = datetime.now(timezone.utc) if timestamp_utc is None else timestamp_utc
    seconds = datetime_to_unix(ts, unit=TimeUnit.SECONDS)
    minutes = int(seconds / 60)
    days = int(minutes / 60 / 24)

    user_denied = (
        False
        if user is None
        else _is_denied_by_rate_limit(
            redis=redis,
            key=user,
            page_name=page_name,
            limits=page_limits,
            minutes=minutes,
            days=days,
            read_only=False,
        )
    )
    ip_address_denied = _is_denied_by_rate_limit(
        redis=redis,
        key=ip_address,
        page_name=page_name,
        limits=page_limits,
        minutes=minutes,
        days=days,
        read_only=user is not None,
    )

    # For now, we skip blocking on IP rate limiting for logged in users
    if user and ip_address_denied:
        logger.info(f"[Soft] Request rate limited: id {user}: ip {ip_address}: url {url}")
        ip_address_denied = False

    return user_denied or ip_address_denied
