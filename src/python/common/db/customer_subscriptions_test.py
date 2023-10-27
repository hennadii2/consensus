from datetime import datetime, timedelta, timezone

import pytest  # type: ignore
from common.db.customer_subscriptions import CustomerSubscriptions
from common.db.test.connect import MainDbTestClient


@pytest.fixture
def connection():
    with MainDbTestClient() as connection:
        yield connection


def test_read_by_stripe_customer_id(connection) -> None:
    db = CustomerSubscriptions(connection)
    db.write_subscription_by_stripe_customer_id(
        stripe_customer_id="customer_id",
        stripe_json_data="user_subscription_data",
        timestamp=datetime.now(timezone.utc),
        commit=True,
    )

    actual = db.read_by_stripe_customer_id("customer_id")
    assert actual is not None
    assert actual.stripe_json_data == "user_subscription_data"


def test_write_user_subscription_by_stripe_customer_id(connection) -> None:
    db = CustomerSubscriptions(connection)
    db.write_subscription_by_stripe_customer_id(
        stripe_customer_id="customer_id",
        stripe_json_data="user_subscription_data",
        timestamp=datetime.now(timezone.utc),
        commit=True,
    )

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM customer_subscriptions")
        results = cursor.fetchall()

        assert len(results) == 1

        actual = results[0]

        assert actual["id"] == 1
        assert actual["stripe_customer_id"] == "customer_id"
        assert actual["stripe_json_data"] == "user_subscription_data"


def test_write_and_read_new_version(connection) -> None:
    db = CustomerSubscriptions(connection)
    customer_id = "customer_id"
    user_version_1 = db.write_subscription_by_stripe_customer_id(
        stripe_customer_id=customer_id,
        stripe_json_data="user_subscription_data",
        timestamp=datetime.now(timezone.utc),
        commit=True,
    )
    actual = db.read_by_stripe_customer_id(customer_id)
    assert actual is not None
    assert actual.stripe_json_data == "user_subscription_data"
    assert actual == user_version_1

    user_version_2 = db.write_subscription_by_stripe_customer_id(
        stripe_customer_id=customer_id,
        stripe_json_data="user_subscription_data2",
        timestamp=datetime.now(timezone.utc) + timedelta(1),
        commit=True,
    )
    actual = db.read_by_stripe_customer_id(customer_id)
    assert actual is not None
    assert actual.stripe_json_data == "user_subscription_data2"
    assert actual == user_version_2
    assert user_version_1 != user_version_2
