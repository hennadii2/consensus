from __future__ import annotations

from datetime import datetime
from typing import Any, Optional, TypedDict

import psycopg2
from loguru import logger
from pydantic import BaseModel

_TABLE_NAME = "subscription_products"
_COLUMN_ID = "id"
_COLUMN_STRIPE_PRODUCT_ID = "stripe_product_id"
_COLUMN_STRIPE_JSON_DATA = "stripe_json_data"
_COLUMN_VERSION_CREATED_AT = "version_created_at"

# A known fake product that is written everytime we update the subscription
# products set. This is used to lookup the latest version timestamp to
# query against, and as a workaround to avoid blindly selecting the latest versions
# of all subscriptions, which do not account for subscriptions that were deleted
# between versions.
VERSION_TRACKER_PRODUCT_ID = "version-tracker-product-id"
VERSION_DATETIME_FORMAT = "%m/%d/%Y %H:%M:%S"


class SubscriptionProduct(BaseModel):
    id: int
    stripe_product_id: str
    stripe_json_data: str
    version: str


class PartialSubscriptionProduct(TypedDict):
    product_id: str
    json_data: str


def _row_to_model(row: Any) -> SubscriptionProduct:
    return SubscriptionProduct(
        id=row[_COLUMN_ID],
        stripe_product_id=row[_COLUMN_STRIPE_PRODUCT_ID],
        stripe_json_data=row[_COLUMN_STRIPE_JSON_DATA],
        version=row[_COLUMN_VERSION_CREATED_AT].strftime(VERSION_DATETIME_FORMAT),
    )


class SubscriptionProducts:
    """
    Interface class for reading/writing subscription_products stored in a DB.
    """

    def __init__(self, connection: psycopg2.extensions.connection):
        self.connection = connection

    def read_all(self, version: Optional[str]) -> list[SubscriptionProduct]:
        """
        Reads the latest versions of all subscription_products.

        If version is not None then that version of products will be returned.
        """
        if version is None:
            version_tracking = self.read_by_product_id(
                product_id=VERSION_TRACKER_PRODUCT_ID,
            )
            if version_tracking is None:
                raise ValueError("Missing expected version tracking, unable to find latest")
            version = version_tracking.version
            assert version is not None

        sql = f"""
          SELECT * FROM {_TABLE_NAME}
            WHERE {_COLUMN_VERSION_CREATED_AT} = %(version)s
            AND {_COLUMN_STRIPE_PRODUCT_ID} != %(version_tracker_product_id)s
        """
        data = {
            "version": datetime.strptime(version, VERSION_DATETIME_FORMAT),
            "version_tracker_product_id": VERSION_TRACKER_PRODUCT_ID,
        }
        latest_products: list[SubscriptionProduct] = []
        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            results = cursor.fetchall()
            for row in results:
                subscription_product = _row_to_model(row)
                latest_products.append(subscription_product)
        return latest_products

    def read_by_product_id(self, product_id: str) -> Optional[SubscriptionProduct]:
        """
        Reads the latest subscription product verions from the database
        for the given ID or returns None if not found.
        """

        sql = f"""
          SELECT * FROM {_TABLE_NAME}
            WHERE {_COLUMN_STRIPE_PRODUCT_ID} = %(id)s
          ORDER BY {_COLUMN_VERSION_CREATED_AT} DESC
        """
        data = {"id": product_id}
        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            results = cursor.fetchall()
            if not len(results):
                return None
            row = results[0]
            subscription_product = _row_to_model(row)
            return subscription_product

    def _write_subscription_product(
        self,
        product_id: str,
        json_data: str,
        timestamp: datetime,
        commit: bool,
    ) -> SubscriptionProduct:
        """
        Writes a subscription product to the database with a newly generated ID and fails
        if its product ID already exists.
        """

        sql = f"""
          INSERT INTO {_TABLE_NAME} (
            {_COLUMN_STRIPE_PRODUCT_ID},
            {_COLUMN_STRIPE_JSON_DATA},
            {_COLUMN_VERSION_CREATED_AT}
          ) VALUES (
            %(product_id)s,
            %(json_data)s,
            %(version_created_at)s
          )
          RETURNING {_COLUMN_ID}
        """
        data = {
            "product_id": product_id,
            "json_data": json_data,
            "version_created_at": timestamp,
        }

        subscription_product = SubscriptionProduct(
            id=0,
            stripe_product_id=product_id,
            stripe_json_data=json_data,
            version=timestamp.strftime(VERSION_DATETIME_FORMAT),
        )

        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            subscription_product.id = cursor.fetchone()[_COLUMN_ID]

        if commit:
            self.connection.commit()

        return subscription_product

    def write_latest_subscription_products(
        self,
        products: list[PartialSubscriptionProduct],
        timestamp: datetime,
        commit: bool,
    ) -> list[SubscriptionProduct]:
        """
        Writes all latest subscription products together as single set with
        a shared timestamp.
        """
        clamped_timestamp = datetime.strptime(
            timestamp.strftime(VERSION_DATETIME_FORMAT), VERSION_DATETIME_FORMAT
        )
        version_tracker = self._write_subscription_product(
            product_id=VERSION_TRACKER_PRODUCT_ID,
            json_data="",
            timestamp=clamped_timestamp,
            commit=commit,
        )

        latest_products = []
        for product in products:
            latest_product = self._write_subscription_product(
                product_id=product["product_id"],
                json_data=product["json_data"],
                timestamp=clamped_timestamp,
                commit=commit,
            )
            latest_products.append(latest_product)

        logger.info(f"Wrote latest subscription products: {version_tracker.version}")
        return latest_products
