from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, Union

import psycopg2
from common.time.convert import validate_datetime
from pydantic import BaseModel

_TABLE_NAME = "bookmark_items"
_COLUMN_ID = "id"
_COLUMN_CLERK_USER_ID = "clerk_user_id"
_COLUMN_BOOKMARK_LIST_ID = "bookmark_list_id"
_COLUMN_BOOKMARK_TYPE = "bookmark_type"
_COLUMN_PAPER_ID = "paper_id"
_COLUMN_SEARCH_URL = "search_url"
_COLUMN_CREATED_AT = "created_at"
_COLUMN_DELETED_AT = "deleted_at"


class BookmarkType(Enum):
    PAPER = "paper"
    SEARCH = "search"


class PaperBookmark(BaseModel):
    paper_id: str


class SearchBookmark(BaseModel):
    search_url: str


class BookmarkItem(BaseModel):
    id: int
    clerk_user_id: str
    bookmark_list_id: str
    bookmark_type: BookmarkType
    bookmark_data: Union[PaperBookmark, SearchBookmark]
    created_at: datetime
    deleted_at: Optional[datetime]


def _create_bookmark_data(
    bookmark_type: BookmarkType,
    paper_id: Optional[str],
    search_url: Optional[str],
) -> PaperBookmark | SearchBookmark:
    if bookmark_type == BookmarkType.SEARCH:
        if search_url is None or search_url == "":
            raise ValueError("Invalid search_url for search bookmark: {search_url}")
        return SearchBookmark(search_url=search_url)
    elif bookmark_type == BookmarkType.PAPER:
        if paper_id is None or paper_id == "":
            raise ValueError("Invalid paper_id for paper bookmark: {paper_id}")
        return PaperBookmark(paper_id=paper_id)
    raise NotImplementedError("Failed to create bookmark: unknown type: {bookmark_type}")


def row_to_model(row: Any) -> BookmarkItem:
    bookmark_type = BookmarkType(row[_COLUMN_BOOKMARK_TYPE])
    bookmark_data = _create_bookmark_data(
        bookmark_type=bookmark_type,
        paper_id=row[_COLUMN_PAPER_ID],
        search_url=row[_COLUMN_SEARCH_URL],
    )
    return BookmarkItem(
        id=row[_COLUMN_ID],
        clerk_user_id=row[_COLUMN_CLERK_USER_ID],
        bookmark_list_id=row[_COLUMN_BOOKMARK_LIST_ID],
        bookmark_type=bookmark_type,
        bookmark_data=bookmark_data,
        created_at=row[_COLUMN_CREATED_AT],
        deleted_at=row[_COLUMN_DELETED_AT],
    )


class BookmarkItems:
    """
    Interface class for reading/writing subscriptions stored in a DB.
    """

    def __init__(self, connection: psycopg2.extensions.connection):
        self.connection = connection

    def read_by_clerk_customer_id(
        self, clerk_user_id: str
    ) -> Optional[dict[str, list[BookmarkItem]]]:
        """
        Reads all non-deleted bookmarks for a customer into a dict by list id.
        """

        sql = f"""
          SELECT * FROM {_TABLE_NAME}
            WHERE {_COLUMN_CLERK_USER_ID} = %(clerk_user_id)s
              AND {_COLUMN_DELETED_AT} is null
        """
        data = {"clerk_user_id": clerk_user_id}

        bookmark_dict: dict[str, list[BookmarkItem]] = {}
        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            results = cursor.fetchall()
            if not len(results):
                return {}
            for row in results:
                bookmark = row_to_model(row)
                if bookmark.bookmark_list_id not in bookmark_dict:
                    bookmark_dict[bookmark.bookmark_list_id] = []
                bookmark_dict[bookmark.bookmark_list_id].append(bookmark)
        return bookmark_dict

    def _read_bookmark(
        self,
        bookmark_list_id: str,
        bookmark_data: Union[PaperBookmark, SearchBookmark],
    ) -> Optional[BookmarkItem]:
        if isinstance(bookmark_data, PaperBookmark):
            if bookmark_data.paper_id is None or len(bookmark_data.paper_id) == 0:
                return None

            sql = f"""
              SELECT * FROM {_TABLE_NAME}
              WHERE {_COLUMN_BOOKMARK_LIST_ID} = %(bookmark_list_id)s AND
                    {_COLUMN_PAPER_ID} = %(paper_id)s
            """
            data = {
                "bookmark_list_id": bookmark_list_id,
                "paper_id": bookmark_data.paper_id,
            }
            with self.connection.cursor() as cursor:
                cursor.execute(sql, data)
                results = cursor.fetchall()
                if len(results) > 0:
                    bookmark = row_to_model(results[0])
                    return bookmark
            return None
        elif isinstance(bookmark_data, SearchBookmark):
            if bookmark_data.search_url is None or len(bookmark_data.search_url) == 0:
                return None

            sql = f"""
              SELECT * FROM {_TABLE_NAME}
                WHERE {_COLUMN_BOOKMARK_LIST_ID} = %(bookmark_list_id)s AND
                      {_COLUMN_SEARCH_URL} = %(search_url)s
            """
            data = {
                "bookmark_list_id": bookmark_list_id,
                "search_url": bookmark_data.search_url,
            }
            with self.connection.cursor() as cursor:
                cursor.execute(sql, data)
                results = cursor.fetchall()
                if len(results) > 0:
                    bookmark = row_to_model(results[0])
                    return bookmark
            return None
        else:
            raise NotImplementedError("Failed to read bookmark: unknown type: {bookmark_type}")

    def write_bookmark(
        self,
        clerk_user_id: str,
        bookmark_list_id: str,
        bookmark_data: Union[PaperBookmark, SearchBookmark],
        commit: bool,
    ) -> BookmarkItem:
        """
        Writes a new bookmark to the database.

        Raises:
            ValueError: if user fails validation of required fields
        """
        timestamp = datetime.now(timezone.utc)
        validate_datetime(timestamp)

        bookmark = self._read_bookmark(bookmark_list_id, bookmark_data)
        if bookmark is not None:
            sql = f"""
            UPDATE {_TABLE_NAME}
            SET
                {_COLUMN_CREATED_AT} = %(timestamp)s,
                {_COLUMN_DELETED_AT} = null
            WHERE {_COLUMN_ID} = %(id)s
            """
            data = {
                "timestamp": timestamp,
                "id": bookmark.id,
            }
            with self.connection.cursor() as cursor:
                cursor.execute(sql, data)

            if commit:
                self.connection.commit()

            bookmark.created_at = timestamp
            bookmark.deleted_at = None
            return bookmark

        sql = ""
        data = {}
        if isinstance(bookmark_data, PaperBookmark):
            bookmark_type = BookmarkType.PAPER
            sql = f"""
            INSERT INTO {_TABLE_NAME} (
                {_COLUMN_CLERK_USER_ID},
                {_COLUMN_BOOKMARK_LIST_ID},
                {_COLUMN_BOOKMARK_TYPE},
                {_COLUMN_PAPER_ID},
                {_COLUMN_CREATED_AT}
            ) VALUES (
                %(clerk_user_id)s,
                %(bookmark_list_id)s,
                %(bookmark_type)s,
                %(paper_id)s,
                %(created_at)s
            )
            RETURNING {_COLUMN_ID}
            """
            data = {
                "clerk_user_id": clerk_user_id,
                "bookmark_list_id": bookmark_list_id,
                "bookmark_type": bookmark_type.value,
                "paper_id": bookmark_data.paper_id,
                "created_at": timestamp,
            }
        elif isinstance(bookmark_data, SearchBookmark):
            bookmark_type = BookmarkType.SEARCH
            sql = f"""
            INSERT INTO {_TABLE_NAME} (
                {_COLUMN_CLERK_USER_ID},
                {_COLUMN_BOOKMARK_LIST_ID},
                {_COLUMN_BOOKMARK_TYPE},
                {_COLUMN_SEARCH_URL},
                {_COLUMN_CREATED_AT}
            ) VALUES (
                %(clerk_user_id)s,
                %(bookmark_list_id)s,
                %(bookmark_type)s,
                %(search_url)s,
                %(created_at)s
            )
            RETURNING {_COLUMN_ID}
            """
            data = {
                "clerk_user_id": clerk_user_id,
                "bookmark_list_id": bookmark_list_id,
                "bookmark_type": bookmark_type.value,
                "search_url": bookmark_data.search_url,
                "created_at": timestamp,
            }

        bookmark = BookmarkItem(
            id=0,
            clerk_user_id=clerk_user_id,
            bookmark_list_id=bookmark_list_id,
            bookmark_type=bookmark_type,
            bookmark_data=bookmark_data,
            created_at=timestamp,
            deleted_at=None,
        )

        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            bookmark.id = cursor.fetchone()[_COLUMN_ID]

        if commit:
            self.connection.commit()

        return bookmark

    def delete_bookmark_by_id(
        self,
        id: int,
        commit: bool,
    ) -> bool:
        """
        Mark bookmark item as deleted by id
        """
        timestamp = datetime.now(timezone.utc)
        validate_datetime(timestamp)

        sql = f"""
          UPDATE {_TABLE_NAME}
          SET {_COLUMN_DELETED_AT} = %(timestamp)s
          WHERE {_COLUMN_ID} = %(bookmark_id)s
        """
        data = {
            "timestamp": timestamp,
            "bookmark_id": id,
        }

        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)

        if commit:
            self.connection.commit()

        return True

    def delete_bookmark_items_by_list_id(
        self,
        list_id: str,
        commit: bool,
    ) -> bool:
        """
        Mark bookmark items as deleted by list id
        """
        timestamp = datetime.now(timezone.utc)
        validate_datetime(timestamp)

        sql = f"""
          UPDATE {_TABLE_NAME}
          SET {_COLUMN_DELETED_AT} = %(timestamp)s
          WHERE {_COLUMN_BOOKMARK_LIST_ID} = %(bookmark_list_id)s
        """
        data = {
            "timestamp": timestamp,
            "bookmark_list_id": list_id,
        }

        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)

        if commit:
            self.connection.commit()

        return True
