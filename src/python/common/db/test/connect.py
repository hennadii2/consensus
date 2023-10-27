from contextlib import contextmanager
from typing import Generator
from urllib.parse import urlparse

import psycopg2
from common.config.constants import REPO_PATH_MAIN_SQL
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from testcontainers.postgres import PostgresContainer  # type: ignore


@contextmanager
def MainDbTestClient() -> Generator[psycopg2.extensions.connection, None, None]:
    """Connects to the test postgres DB."""

    with PostgresContainer() as postgres:
        result = urlparse(postgres.get_connection_url())
        connection = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port,
            cursor_factory=RealDictCursor,
        )

        # Initialize DB with main.sql tables
        with connection.cursor() as cursor:
            with open(REPO_PATH_MAIN_SQL) as f:
                sql = f.read()
                cursor.execute(sql)

        try:
            yield connection
        finally:
            connection.close()


@contextmanager
def MainDbPoolTestClient(max_connections: int) -> Generator[SimpleConnectionPool, None, None]:
    """Connects to the test postgres DB."""

    with PostgresContainer() as postgres:
        result = urlparse(postgres.get_connection_url())
        pool = SimpleConnectionPool(
            minconn=1,
            maxconn=max_connections,
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port,
            cursor_factory=RealDictCursor,
        )

        try:
            yield pool
        finally:
            if not pool.closed:
                pool.closeall()
