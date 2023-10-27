from __future__ import annotations

from datetime import datetime
from typing import Any, Iterator, Optional

import psycopg2
from pydantic import BaseModel

_TABLE_NAME = "customer_subscriptions"
_COLUMN_ID = "id"
_COLUMN_STRIPE_CUSTOMER_ID = "stripe_customer_id"
_COLUMN_STRIPE_JSON_DATA = "stripe_json_data"
_COLUMN_VERSION_CREATED_AT = "version_created_at"


class CustomerSubscription(BaseModel):
    id: int
    stripe_customer_id: str
    stripe_json_data: str
    version: datetime


def row_to_model(row: Any) -> CustomerSubscription:
    return CustomerSubscription(
        id=row[_COLUMN_ID],
        stripe_customer_id=row[_COLUMN_STRIPE_CUSTOMER_ID],
        stripe_json_data=row[_COLUMN_STRIPE_JSON_DATA],
        version=row[_COLUMN_VERSION_CREATED_AT],
    )


class CustomerSubscriptions:
    """
    Interface class for reading/writing subscriptions stored in a DB.
    """

    def __init__(self, connection: psycopg2.extensions.connection):
        self.connection = connection

    def read_all(self) -> Iterator[CustomerSubscription]:
        """Reads all rows in the subscription_products table using a server side cursor."""

        sql = f""" SELECT * FROM {_TABLE_NAME} """
        with self.connection.cursor("server_side_cursor") as cursor:
            cursor.execute(sql)
            for row in cursor:
                user = row_to_model(row)
                yield user

    def read_by_stripe_customer_id(
        self, stripe_customer_id: str
    ) -> Optional[CustomerSubscription]:
        """
        Reads latest user verson from the database for
        the given stripe_customer_id or returns None if not found.
        """

        sql = f"""
          SELECT * FROM {_TABLE_NAME}
            WHERE {_COLUMN_STRIPE_CUSTOMER_ID} = %(id)s
          ORDER BY {_COLUMN_VERSION_CREATED_AT} DESC
        """
        data = {"id": stripe_customer_id}
        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            results = cursor.fetchall()
            if not len(results):
                return None
            row = results[0]
            user = row_to_model(row)
            return user

    def write_subscription_by_stripe_customer_id(
        self,
        stripe_customer_id: str,
        stripe_json_data: str,
        timestamp: datetime,
        commit: bool,
    ) -> CustomerSubscription:
        """
        Writes a new subscription verison for a stripe customer to the database.

        Raises:
            ValueError: if user fails validation of required fields
        """

        sql = f"""
          INSERT INTO {_TABLE_NAME} (
            {_COLUMN_STRIPE_CUSTOMER_ID},
            {_COLUMN_STRIPE_JSON_DATA},
            {_COLUMN_VERSION_CREATED_AT}
          ) VALUES (
            %(stripe_customer_id)s,
            %(stripe_json_data)s,
            %(version_created_at)s
          )
          RETURNING {_COLUMN_ID}
        """
        data = {
            "stripe_customer_id": stripe_customer_id,
            "stripe_json_data": stripe_json_data,
            "version_created_at": timestamp,
        }

        subscription = CustomerSubscription(
            id=0,
            stripe_customer_id=stripe_customer_id,
            stripe_json_data=stripe_json_data,
            version=timestamp,
        )

        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            subscription.id = cursor.fetchone()[_COLUMN_ID]

        if commit:
            self.connection.commit()

        return subscription

    def remove_subscription_by_stripe_customer_id(
        self,
        stripe_customer_id: str,
        commit: bool,
    ) -> bool:
        """
        Remove user subscription by stripe customer id
        """

        sql = f"""
          DELETE FROM {_TABLE_NAME}
          WHERE {_COLUMN_STRIPE_CUSTOMER_ID} = %(id)s
        """
        data = {
            "id": stripe_customer_id,
        }

        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)

        if commit:
            self.connection.commit()

        return True
