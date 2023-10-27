from contextlib import contextmanager
from typing import Generator

import redis
from testcontainers.redis import RedisContainer  # type: ignore


@contextmanager
def RedisTestConnection() -> Generator[redis.Redis, None, None]:
    with RedisContainer() as redis_container:
        connection = redis_container.get_client()
        try:
            yield connection
        finally:
            connection.close()
