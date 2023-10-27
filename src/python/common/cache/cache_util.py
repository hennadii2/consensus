import json
from dataclasses import dataclass
from typing import Callable, Generic, Optional, Type, TypeVar

import redis
from loguru import logger
from pydantic import BaseModel

CachedModel = TypeVar("CachedModel", bound=BaseModel)


@dataclass(frozen=True)
class Cache(Generic[CachedModel]):
    read: Callable[[redis.Redis], Optional[CachedModel]]
    write: Callable[[redis.Redis, CachedModel], None]


@dataclass(frozen=True)
class CacheWithDefault(Generic[CachedModel]):
    read: Callable[[redis.Redis], CachedModel]
    write: Callable[[redis.Redis, CachedModel], None]


def read_from_cache(
    cache_key: str, model: Type[CachedModel], redis: redis.Redis
) -> Optional[CachedModel]:
    """
    Best effort attempt to read data from cache. Returns None if read failed,
    otherwise returns the cache contents.
    """
    try:
        cached = redis.get(cache_key)
        if cached is None:
            return None
        else:
            response = model(**json.loads(cached))
            return response
    except Exception as e:
        logger.error(e)
        logger.error(f"Failed to parse cache response: {cache_key}")
        return None


def read_from_cache_with_default(
    cache_key: Optional[str], model: Type[CachedModel], default: CachedModel, redis: redis.Redis
) -> CachedModel:
    """
    Best effort attempt to read data from cache. Returns given default if read failed.
    """
    if cache_key is None:
        return default
    cached = read_from_cache(redis=redis, cache_key=cache_key, model=model)
    return default if cached is None else cached


def write_to_cache(cache_key: str, redis: redis.Redis, data: BaseModel) -> None:
    """
    Best effort attempt to write data to cache. If write fails, an error is logged.
    """
    try:
        redis.set(cache_key, str(data.json()))
    except Exception as e:
        logger.error(e)
        logger.error(f"Failed to add cache data: {cache_key}")
    return None
