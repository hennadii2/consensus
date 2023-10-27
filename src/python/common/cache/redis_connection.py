from dataclasses import dataclass
from enum import Enum
from typing import Optional
from urllib.parse import urlparse

import redis
from common.config.secret_manager import SecretId, access_secret
from loguru import logger


class RedisEnv(Enum):
    """
    All supported Redis cache environments.
    """

    DEV = "dev"
    PROD = "prod"
    LOCAL = "local"


@dataclass(frozen=True)
class RedisConnectionInfo:
    db: Optional[int]
    host: Optional[str]
    port: Optional[int]
    password: Optional[str]


def get_connection_info(env: RedisEnv) -> RedisConnectionInfo:
    """
    Returns a dataclass with parsed redis connection fields for the
    environment or throws an error.

    Raises:
        ValueError: if environment is not supported
        ValueError: if validation of normally required fields failed
    """

    def get_uri() -> str:
        if env == RedisEnv.LOCAL:
            return access_secret(SecretId.REDIS_CACHE_URI_LOCAL, use_env_var=True)
        elif env == RedisEnv.DEV:
            return access_secret(SecretId.REDIS_CACHE_URI_DEV)
        elif env == RedisEnv.PROD:
            return access_secret(SecretId.REDIS_CACHE_URI_PROD)
        else:
            raise ValueError(f"Failed to get redis connection URI: unknown env {env}")

    connection_uri = get_uri()
    parsed_connection_uri = urlparse(connection_uri)
    info = RedisConnectionInfo(
        db=int(parsed_connection_uri.path[1:]),
        host=parsed_connection_uri.hostname,
        port=parsed_connection_uri.port,
        password=parsed_connection_uri.password,
    )

    return info


def RedisConnection(env: RedisEnv) -> redis.Redis:
    """
    Connects to the redis cache.

    Raises:
        ValueError: if redis secret config is not available
    """

    info = get_connection_info(env)
    logger.info(f"Connecting to {env.value} redis: {info.db} {info.host} {info.port}")

    config_error = "Failed to connect to redis for env {0}: {1}"
    if info.db is None:
        raise ValueError(config_error.format(env, "db is none"))
    if info.host is None:
        raise ValueError(config_error.format(env, "host is none"))
    if info.port is None:
        raise ValueError(config_error.format(env, "port is none"))
    if info.password is None:
        raise ValueError(config_error.format(env, "password is none"))

    connection = redis.Redis(
        host=info.host,
        port=info.port,
        db=info.db,
        password=info.password,
    )
    return connection
