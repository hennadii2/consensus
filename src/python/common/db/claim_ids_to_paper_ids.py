from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

import psycopg2
from common.time.convert import validate_datetime
from pydantic import BaseModel

_TABLE_NAME = "claim_ids_to_paper_ids"
_COLUMN_ROW_ID = "row_id"
_COLUMN_CLAIM_ID = "claim_id"
_COLUMN_PAPER_ID = "paper_id"
_COLUMN_CREATED_AT = "created_at"
_COLUMN_CREATED_BY = "created_by"


class ClaimIdToPaperId(BaseModel):
    row_id: int
    claim_id: str
    paper_id: str


def _db_row_to_model(row: Any) -> ClaimIdToPaperId:
    return ClaimIdToPaperId(
        row_id=row[_COLUMN_ROW_ID],
        claim_id=row[_COLUMN_CLAIM_ID],
        paper_id=row[_COLUMN_PAPER_ID],
    )


class ClaimIdsToPaperIds:
    """
    Interface class for reading/writing claim to paper ID mappings stored in a DB.
    """

    def __init__(self, connection: psycopg2.extensions.connection):
        self.connection = connection

    def read_by_claim_id(self, claim_id: str) -> Optional[ClaimIdToPaperId]:
        """
        Returns an paper ID mapping for the claim id, or None if not found.

        Raises:
            ValueError: if more than 1 takeaway is found
        """

        sql = f"""
          SELECT * FROM {_TABLE_NAME}
            WHERE {_COLUMN_CLAIM_ID} = %(id)s
          ORDER BY {_COLUMN_CREATED_AT} DESC
        """
        data = {"id": claim_id}
        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            results = cursor.fetchall()
            if not len(results):
                return None
            row = results[0]
            return _db_row_to_model(row)

    def write_claim_id_to_paper_id(
        self,
        paper_id: str,
        claim_id: str,
        job_name: str,
        timestamp: Optional[datetime] = None,
        commit=False,
    ) -> ClaimIdToPaperId:
        """
        Writes a mapping of a claim id to its paper id to the database.
        """

        if not timestamp:
            timestamp = datetime.now(timezone.utc)
        validate_datetime(timestamp)

        sql = f"""
          INSERT INTO {_TABLE_NAME} (
            {_COLUMN_CLAIM_ID},
            {_COLUMN_PAPER_ID},
            {_COLUMN_CREATED_AT},
            {_COLUMN_CREATED_BY}
          ) VALUES (
            %(claim_id)s,
            %(paper_id)s,
            %(created_at)s,
            %(created_by)s
          )
          RETURNING {_COLUMN_ROW_ID}
        """
        data = {
            "claim_id": claim_id,
            "paper_id": paper_id,
            "created_at": timestamp,
            "created_by": job_name,
        }

        model = ClaimIdToPaperId(
            row_id=0,
            claim_id=claim_id,
            paper_id=paper_id,
        )

        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            model.row_id = cursor.fetchone()[_COLUMN_ROW_ID]

        if commit:
            self.connection.commit()

        return model
