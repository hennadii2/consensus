from dataclasses import dataclass
from functools import partial

import psycopg2
from loguru import logger
from psycopg2.pool import SimpleConnectionPool


@dataclass(frozen=True)
class DbConnection:
    # An active DB connection object.
    connection: psycopg2.extensions.connection
    # This should be called from an 'Exception catch block' if an unrecoverable
    # psycopg2 error has been caught.
    close_connection: partial[None]


def is_unrecoverable_db_error(e: Exception) -> bool:
    """
    Returns true if the exception indicates an unrecoverable psycopg2 connection error.
    """
    if isinstance(e, psycopg2.InterfaceError):
        return True
    if isinstance(e, psycopg2.OperationalError):
        return True
    return False


def _close_db_pool_connection(
    db_pool: SimpleConnectionPool,
    connection: psycopg2.extensions.connection,
    connection_id: str,
) -> None:
    """
    Closes the connection.
    """
    db_pool.putconn(
        conn=connection,
        key=connection_id,
        close=True,
    )


class DbConnectionHandler:
    """
    Dependency injectable class that returns a DB connection from a rotating pool
    and provides a callback to enable reconnection on an unrecoverable failure.

    Connection objects are rotated, which means that callers will share DB
    connection objects if more callers are active than the number of max
    connections in the DB pool.
    """

    def __init__(self, db_pool: SimpleConnectionPool):
        self.next_connection = 1
        self.db_pool = db_pool

    def __call__(self):
        connection_id = str(self.next_connection)
        if self.next_connection < self.db_pool.maxconn:
            self.next_connection = self.next_connection + 1
        else:
            self.next_connection = 1

        # Get the next rotating connection object.
        connection = self.db_pool.getconn(key=connection_id)

        # On psycopg2 exceptions we should close the conection so that
        # it will be reopened next time around. This is necessary because
        # psycopg2 has no reconnection logic, so once a connection fails once
        # it will not reconnect unless it is explicitly recreated.
        close_connection = partial(
            _close_db_pool_connection,
            db_pool=self.db_pool,
            connection=connection,
            connection_id=connection_id,
        )

        return DbConnection(connection, close_connection)

    def close(self):
        logger.info("Closing all db pool connections in DbConnectionHandler.")
        self.db_pool.closeall()
