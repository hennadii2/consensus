from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import NAMESPACE_DNS, uuid5

import psycopg2
from pydantic import BaseModel

_TABLE_NAME = "bookmark_lists"
_COLUMN_ID = "id"
_COLUMN_CLERK_USER_ID = "clerk_user_id"
_COLUMN_TEXT_LABEL = "text_label"
_COLUMN_CREATED_AT = "created_at"
_COLUMN_DELETED_AT = "deleted_at"

_BOOKMARK_LIST_ID_NAMESPACE = NAMESPACE_DNS


class BookmarkList(BaseModel):
    id: str
    text_label: str
    created_at: datetime
    deleted_at: Optional[datetime]


def row_to_model(row: Any) -> BookmarkList:
    return BookmarkList(
        id=row[_COLUMN_ID],
        text_label=row[_COLUMN_TEXT_LABEL],
        created_at=row[_COLUMN_CREATED_AT],
        deleted_at=row[_COLUMN_DELETED_AT],
    )


class BookmarkLists:
    """
    Interface class for reading/writing subscriptions stored in a DB.
    """

    def __init__(self, connection: psycopg2.extensions.connection):
        self.connection = connection

    def read_by_clerk_customer_id(self, clerk_user_id: str) -> list[BookmarkList]:
        """
        Reads all non-deleted bookmarks for a customer into a dict by list id.
        """

        sql = f"""
          SELECT * FROM {_TABLE_NAME}
            WHERE {_COLUMN_CLERK_USER_ID} = %(clerk_user_id)s
              AND {_COLUMN_DELETED_AT} is null
            ORDER BY {_COLUMN_CREATED_AT} DESC
        """
        data = {
            "clerk_user_id": clerk_user_id,
        }

        bookmark_lists = []
        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            results = cursor.fetchall()
            for result in results:
                bookmark_lists.append(row_to_model(result))
        return bookmark_lists

    def read_by_id(self, bookmark_list_id: str) -> Optional[BookmarkList]:
        """
        Reads all non-deleted bookmarks for a customer into a dict by list id.
        """

        sql = f"""
          SELECT * FROM {_TABLE_NAME}
            WHERE {_COLUMN_ID} = %(bookmark_list_id)s
              AND {_COLUMN_DELETED_AT} is null
            ORDER BY {_COLUMN_CREATED_AT} DESC
        """
        data = {
            "bookmark_list_id": bookmark_list_id,
        }

        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            results = cursor.fetchall()
            if len(results) == 0:
                return None
            return row_to_model(results[0])

    def create_bookmark_list(
        self,
        clerk_user_id: str,
        text_label: str,
        commit: bool,
    ) -> BookmarkList:
        """
        Writes a new bookmark to the database.

        Raises:
            ValueError: if user fails validation of required fields
        """

        timestamp = datetime.now(tz=timezone.utc)

        new_id = uuid5(_BOOKMARK_LIST_ID_NAMESPACE, f"{clerk_user_id}:{timestamp}").hex
        bookmark_list = BookmarkList(
            id=new_id,
            text_label=text_label,
            created_at=timestamp,
            deleted_at=None,
        )

        sql = f"""
          INSERT INTO {_TABLE_NAME} (
            {_COLUMN_ID},
            {_COLUMN_CLERK_USER_ID},
            {_COLUMN_TEXT_LABEL},
            {_COLUMN_CREATED_AT}
          ) VALUES (
            %(id)s,
            %(clerk_user_id)s,
            %(text_label)s,
            %(created_at)s
          )
        """
        data = {
            "id": bookmark_list.id,
            "clerk_user_id": clerk_user_id,
            "text_label": text_label,
            "created_at": timestamp,
        }

        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)

        if commit:
            self.connection.commit()

        return bookmark_list

    def delete_bookmark_list(
        self,
        bookmark_list_id: str,
        commit: bool,
    ) -> BookmarkList:
        """
        Deletes a bookmark list from the database.

        Raises:
            ValueError: if user fails validation of required fields
        """

        timestamp = datetime.now(tz=timezone.utc)

        sql = f"""
        UPDATE {_TABLE_NAME}
          SET {_COLUMN_DELETED_AT} = %(timestamp)s
          WHERE {_COLUMN_ID} = %(id)s
          RETURNING *
        """
        data = {
            "timestamp": timestamp,
            "id": bookmark_list_id,
        }

        updated_bookmark_list_data = {}
        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            updated_bookmark_list_data = cursor.fetchone()

        if commit:
            self.connection.commit()

        if updated_bookmark_list_data is None:
            raise ValueError(f"Failed delete_bookmark_list: unknown id: {bookmark_list_id}")

        return row_to_model(updated_bookmark_list_data)

    def update_bookmark_list(
        self,
        bookmark_list_id: str,
        new_text_label: str,
        commit: bool,
    ) -> BookmarkList:
        """
        Update a bookmark list text label to the database.

        Raises:
            ValueError: if user fails validation of required fields
        """

        sql = f"""
        UPDATE {_TABLE_NAME}
          SET {_COLUMN_TEXT_LABEL} = %(text_label)s
          WHERE {_COLUMN_ID} = %(id)s
          RETURNING *
        """
        data = {
            "text_label": new_text_label,
            "id": bookmark_list_id,
        }

        updated_bookmark_list_data = {}
        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            updated_bookmark_list_data = cursor.fetchone()

        if commit:
            self.connection.commit()

        if updated_bookmark_list_data is None:
            raise ValueError(f"Failed update_bookmark_list: unknown id: {bookmark_list_id}")

        return row_to_model(updated_bookmark_list_data)
