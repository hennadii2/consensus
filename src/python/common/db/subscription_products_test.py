from datetime import datetime, timedelta, timezone

import pytest  # type: ignore
from common.db.subscription_products import SubscriptionProducts
from common.db.test.connect import MainDbTestClient


@pytest.fixture
def connection():
    with MainDbTestClient() as connection:
        yield connection


def test_write_subscription_product(connection) -> None:
    db = SubscriptionProducts(connection)
    db.write_latest_subscription_products(
        products=[
            {
                "product_id": "10",
                "json_data": "{'billing cycle': '1111111-22222'}",
            }
        ],
        timestamp=datetime.now(timezone.utc),
        commit=True,
    )

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM subscription_products")
        results = cursor.fetchall()

        assert len(results) == 2

        actual_version_tracker = results[0]
        assert actual_version_tracker["id"] == 1
        assert actual_version_tracker["stripe_product_id"] == "version-tracker-product-id"
        assert actual_version_tracker["stripe_json_data"] == ""

        actual = results[1]
        assert actual["id"] == 2
        assert actual["stripe_product_id"] == "10"
        assert actual["stripe_json_data"] == "{'billing cycle': '1111111-22222'}"


def test_read_by_product_id(connection) -> None:
    db = SubscriptionProducts(connection)
    db.write_latest_subscription_products(
        products=[
            {
                "product_id": "10",
                "json_data": "{'billing cycle': '1111111-22222'}",
            }
        ],
        timestamp=datetime.now(timezone.utc),
        commit=True,
    )

    actual = db.read_by_product_id(product_id="10")
    assert actual is not None
    assert actual.stripe_json_data == "{'billing cycle': '1111111-22222'}"


def test_update_subscription_product(connection) -> None:
    db = SubscriptionProducts(connection)
    versions1 = db.write_latest_subscription_products(
        products=[
            {
                "product_id": "10",
                "json_data": "{'billing cycle': '1111111-22222'}",
            }
        ],
        timestamp=datetime.now(timezone.utc),
        commit=True,
    )
    assert len(versions1) == 1
    version1 = versions1[0]

    actual = db.read_by_product_id(product_id="10")
    assert actual is not None
    assert actual.version == version1.version
    assert actual.stripe_product_id == version1.stripe_product_id
    assert actual.stripe_json_data == version1.stripe_json_data
    assert actual.stripe_json_data == "{'billing cycle': '1111111-22222'}"

    versions2 = db.write_latest_subscription_products(
        products=[
            {
                "product_id": "10",
                "json_data": "{'billing cycle': '2222-3333'}",
            }
        ],
        timestamp=datetime.now(timezone.utc) + timedelta(1),
        commit=True,
    )
    assert len(versions2) == 1
    version2 = versions2[0]

    actual = db.read_by_product_id(product_id="10")
    assert actual is not None
    assert actual.version == version2.version
    assert actual.stripe_product_id == version2.stripe_product_id
    assert actual.stripe_json_data == version2.stripe_json_data
    assert actual.stripe_json_data == "{'billing cycle': '2222-3333'}"


def test_read_all(connection) -> None:
    db = SubscriptionProducts(connection)
    version1 = db.write_latest_subscription_products(
        products=[
            {
                "product_id": "10",
                "json_data": "{'billing cycle': '10'}",
            },
            {
                "product_id": "12",
                "json_data": "{'billing cycle': '12'}",
            },
        ],
        timestamp=datetime.now(timezone.utc),
        commit=True,
    )
    version2 = db.write_latest_subscription_products(
        products=[
            {
                "product_id": "10",
                "json_data": "{'billing cycle': '100'}",
            },
            {
                "product_id": "20",
                "json_data": "{'billing cycle': '20'}",
            },
        ],
        timestamp=datetime.now(timezone.utc) + timedelta(1),
        commit=True,
    )

    actual = db.read_all(version=None)
    assert version2 != version1
    assert actual == version2
    assert len(actual) == 2
    assert actual[0].stripe_product_id == "10"
    assert actual[0].stripe_json_data == "{'billing cycle': '100'}"
    assert actual[1].stripe_product_id == "20"
    assert actual[1].stripe_json_data == "{'billing cycle': '20'}"


def test_read_all_by_version(connection) -> None:
    db = SubscriptionProducts(connection)
    timestamp1 = datetime.strptime("05/24/2023 11:59:59", "%m/%d/%Y %H:%M:%S")
    version1 = db.write_latest_subscription_products(
        products=[
            {
                "product_id": "10",
                "json_data": "{'billing cycle': '10'}",
            },
            {
                "product_id": "12",
                "json_data": "{'billing cycle': '12'}",
            },
        ],
        timestamp=timestamp1,
        commit=True,
    )
    timestamp2 = datetime.strptime("05/25/2023 11:59:59", "%m/%d/%Y %H:%M:%S")
    version2 = db.write_latest_subscription_products(
        products=[
            {
                "product_id": "10",
                "json_data": "{'billing cycle': '100'}",
            },
            {
                "product_id": "20",
                "json_data": "{'billing cycle': '20'}",
            },
        ],
        timestamp=timestamp2,
        commit=True,
    )

    actual = db.read_all(version="05/24/2023 11:59:59")
    assert len(actual) == 2
    assert actual == version1
    assert actual[0].stripe_product_id == "10"
    assert actual[0].stripe_json_data == "{'billing cycle': '10'}"
    assert actual[1].stripe_product_id == "12"
    assert actual[1].stripe_json_data == "{'billing cycle': '12'}"

    actual = db.read_all(version="05/25/2023 11:59:59")
    assert len(actual) == 2
    assert actual == version2
    assert actual[0].stripe_product_id == "10"
    assert actual[0].stripe_json_data == "{'billing cycle': '100'}"
    assert actual[1].stripe_product_id == "20"
    assert actual[1].stripe_json_data == "{'billing cycle': '20'}"
