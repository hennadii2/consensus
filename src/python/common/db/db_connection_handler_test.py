import psycopg2
from common.db.db_connection_handler import DbConnectionHandler, is_unrecoverable_db_error
from common.db.test.connect import MainDbPoolTestClient


def test_db_connection_handler_rotates_connections() -> None:
    with MainDbPoolTestClient(max_connections=2) as pool:
        db_connection_handler = DbConnectionHandler(pool)
        connection1 = db_connection_handler().connection
        connection2 = db_connection_handler().connection
        connection1_rotated = db_connection_handler().connection
        connection2_rotated = db_connection_handler().connection
        assert connection1_rotated == connection1
        assert connection2_rotated == connection2
        assert connection1_rotated != connection2_rotated


def test_db_connection_handles_one_connection() -> None:
    with MainDbPoolTestClient(max_connections=1) as pool:
        db_connection_handler = DbConnectionHandler(pool)
        connection1 = db_connection_handler().connection
        connection1_rotated = db_connection_handler().connection
        assert connection1_rotated == connection1


def test_db_connection_handler_callback_closes_connection_to_reopen() -> None:
    with MainDbPoolTestClient(max_connections=1) as pool:
        db_connection_handler = DbConnectionHandler(pool)

        db1 = db_connection_handler()
        assert not db1.connection.closed
        db1.close_connection()
        assert db1.connection.closed

        db2 = db_connection_handler()
        assert not db2.connection.closed


def test_db_connection_handler_close_succeeds() -> None:
    with MainDbPoolTestClient(max_connections=3) as pool:
        db_connection_handler = DbConnectionHandler(pool)

        assert not pool.closed
        db_connection_handler.close()
        assert pool.closed


def test_is_unrecoverable_db_error_succeeds() -> None:
    error1 = ValueError("not a psycopg2 error")
    error2 = psycopg2.InterfaceError("unrecoverable psycopg2 error")
    error3 = psycopg2.OperationalError("unrecoverable psycopg2 error")

    assert not is_unrecoverable_db_error(error1)
    assert is_unrecoverable_db_error(error2)
    assert is_unrecoverable_db_error(error3)
