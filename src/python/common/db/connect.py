from dataclasses import dataclass
from enum import Enum
from typing import Optional
from urllib.parse import urlparse

import psycopg2
from common.config.secret_manager import SecretId, access_secret
from loguru import logger
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool


class DbEnv(Enum):
    """
    All supported DB environments.
    """

    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"
    PROD_INGEST = "prod-ingest"
    LOCAL = "local"


@dataclass(frozen=True)
class DbEnvInfo:
    db_env: DbEnv
    db_host_override: Optional[str] = None
    db_port_override: Optional[int] = None

    def __init__(
        self,
        db_env: str,
        db_host_override: Optional[str] = None,
        db_port_override: Optional[int] = None,
    ):
        object.__setattr__(self, "db_env", DbEnv(db_env))
        object.__setattr__(self, "db_host_override", db_host_override)
        object.__setattr__(self, "db_port_override", db_port_override)


@dataclass(frozen=True)
class DbConnectionInfo:
    dbname: Optional[str]
    host: Optional[str]
    port: Optional[int]
    user: Optional[str]
    password: Optional[str]


def get_connection_info(env: DbEnv, validate: bool) -> DbConnectionInfo:
    """
    Returns a dataclass with parsed postgres connection fields for the
    environment or throws an error.

    Raises:
        ValueError: if environment is not supported
        ValueError: if validation of normally required fields failed
    """

    def get_uri() -> str:
        if env == DbEnv.LOCAL:
            return access_secret(SecretId.POSTGRES_URI_LOCAL, use_env_var=True)
        elif env == DbEnv.DEV:
            return access_secret(SecretId.POSTGRES_URI_DEV)
        elif env == DbEnv.STAGING:
            return access_secret(SecretId.POSTGRES_URI_STAGING)
        elif env == DbEnv.PROD:
            return access_secret(SecretId.POSTGRES_URI_PROD)
        elif env == DbEnv.PROD_INGEST:
            return access_secret(SecretId.POSTGRES_URI_PROD_INGEST)
        else:
            raise ValueError(f"Failed to get DB connection URI: unknown env {env}")

    connection_uri = get_uri()
    parsed_connection_uri = urlparse(connection_uri)
    info = DbConnectionInfo(
        dbname=parsed_connection_uri.path[1:],
        host=parsed_connection_uri.hostname,
        port=parsed_connection_uri.port,
        user=parsed_connection_uri.username,
        password=parsed_connection_uri.password,
    )

    if validate:
        config_error = "Failed to connect to postgres for env {0}: {1}"
        if not info.dbname:
            raise ValueError(config_error.format(env, "dbname is none"))
        if not info.host:
            raise ValueError(config_error.format(env, "host is none"))
        if not info.port:
            raise ValueError(config_error.format(env, "port is none"))
        if not info.user:
            raise ValueError(config_error.format(env, "user is none"))
        if not info.password:
            raise ValueError(config_error.format(env, "password is none"))

    return info


@dataclass(frozen=True)
class JdbcConnectionInfo:
    url: Optional[str]
    user: Optional[str]
    password: Optional[str]


def get_jdbc_connection_info(env: DbEnv) -> JdbcConnectionInfo:
    """
    Returns the JDBC URL for the environment.

    Raises:
        ValueError: if environment is not supported
    """

    def get_uri() -> str:
        if env == DbEnv.LOCAL:
            return access_secret(SecretId.POSTGRES_JDBC_URI_LOCAL)
        elif env == DbEnv.DEV:
            return access_secret(SecretId.POSTGRES_JDBC_URI_DEV)
        elif env == DbEnv.PROD:
            return access_secret(SecretId.POSTGRES_JDBC_URI_PROD)
        else:
            raise ValueError(f"Failed to get JDBC connection URI: unknown env {env}")

    jdbc_url = get_uri()
    info = get_connection_info(env, validate=False)
    return JdbcConnectionInfo(
        url=jdbc_url,
        user=info.user,
        password=info.password,
    )


# TODO(cvarano): replace args with DbEnvInfo, and update existing pipelines
def MainDbClient(
    env: DbEnv, host_override: Optional[str] = None, port_override: Optional[int] = None
) -> psycopg2.extensions.connection:
    """
    Connects to the main postgres DB.

    Can optionally specify override host and port for local testing with Cloud SQL Proxy.

    Raises:
        ValueError: if postgres secret config is not available
    """

    info = get_connection_info(env, validate=True)
    host = host_override if host_override else info.host
    port = port_override if port_override else info.port
    logger.info(f"Connecting to {env.value} DB: {info.dbname} {host} {port} {info.user}")
    connection = psycopg2.connect(
        database=info.dbname,
        user=info.user,
        password=info.password,
        host=host,
        port=port,
        cursor_factory=RealDictCursor,
    )
    return connection


def MainDbClientPool(env: DbEnv, max_connections: int) -> SimpleConnectionPool:
    """
    Connects to the main postgres DB.

    Raises:
        ValueError: if postgres secret config is not available
    """

    info = get_connection_info(env, validate=True)
    logger.info(
        f"Connecting to {env.value} DB pool: {info.dbname} {info.host} {info.port} {info.user}"
    )
    connection = SimpleConnectionPool(
        minconn=1,
        maxconn=max_connections,
        database=info.dbname,
        user=info.user,
        password=info.password,
        host=info.host,
        port=info.port,
        cursor_factory=RealDictCursor,
    )
    return connection
