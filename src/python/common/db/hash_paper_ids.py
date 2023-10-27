from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

import psycopg2
from common.time.convert import validate_datetime
from pydantic import BaseModel

_TABLE_NAME = "hash_paper_ids"
_COL_PAPER_ID = "paper_id"
_COL_HASH_PAPER_ID = "hash_paper_id"
_COL_CREATED_AT = "created_at"
_COL_CREATED_BY = "created_by"


class HashPaperId(BaseModel):
    paper_id: str
    hash_paper_id: str
    created_at: datetime
    created_by: str


def db_row_to_model(row: Any) -> HashPaperId:
    return HashPaperId(
        paper_id=row[_COL_PAPER_ID],
        hash_paper_id=row[_COL_HASH_PAPER_ID],
        created_at=row[_COL_CREATED_AT],
        created_by=row[_COL_CREATED_BY],
    )


class HashPaperIds:
    """
    Interface class for reading/writing hash paper id mappings stored in a DB.
    """

    def __init__(self, connection: psycopg2.extensions.connection):
        self.connection = connection

    def read_paper_id(
        self,
        hash_paper_id: str,
    ) -> Optional[str]:
        """
        Reads the paper_id for a given hash_paper_id.

        Raises:
            ValueError: if more than 1 mapping is found
        """

        sql = f"""
          SELECT * FROM {_TABLE_NAME}
            WHERE {_COL_HASH_PAPER_ID} = %(id)s
        """
        data = {"id": hash_paper_id}

        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            results = cursor.fetchall()
            if not len(results):
                return None
            if len(results) != 1:
                raise ValueError(f"Failed to read_paper_id: found > 1 result for: {hash_paper_id}")
            model = db_row_to_model(results[0])
            return model.paper_id

    def read_hash_paper_id(
        self,
        paper_id: str,
    ) -> Optional[str]:
        """
        Reads the hash_paper_id for a given paper_id.

        Raises:
            ValueError: if more than 1 mapping is found
        """

        sql = f"""
          SELECT * FROM {_TABLE_NAME}
            WHERE {_COL_PAPER_ID} = %(id)s
        """
        data = {"id": paper_id}

        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            results = cursor.fetchall()
            if not len(results):
                return None
            if len(results) != 1:
                raise ValueError(f"Failed to read_hash_paper_id: found > 1 result for: {paper_id}")
            model = db_row_to_model(results[0])
            return model.hash_paper_id

    def write_mapping(
        self,
        paper_id: str,
        hash_paper_id: str,
        job_name: str,
        timestamp: datetime,
        commit: bool,
    ) -> HashPaperId:
        """
        Writes an abstract record to the database.

        Raises:
            ValueError: if paper fails validation of required fields
        """
        validate_datetime(timestamp)

        record = HashPaperId(
            paper_id=paper_id,
            hash_paper_id=hash_paper_id,
            created_at=timestamp,
            created_by=job_name,
        )

        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""
                  INSERT INTO {_TABLE_NAME} (
                    {_COL_PAPER_ID},
                    {_COL_HASH_PAPER_ID},
                    {_COL_CREATED_AT},
                    {_COL_CREATED_BY}
                  ) VALUES (
                    %(paper_id)s,
                    %(hash_paper_id)s,
                    %(created_at)s,
                    %(created_by)s
                  )
                """,
                {
                    "paper_id": record.paper_id,
                    "hash_paper_id": record.hash_paper_id,
                    "created_at": record.created_at,
                    "created_by": record.created_by,
                },
            )

        if commit:
            self.connection.commit()

        return record
