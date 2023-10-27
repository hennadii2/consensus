from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional

import psycopg2
from common.time.convert import validate_datetime
from pydantic import BaseModel

_TABLE_NAME = "abstract_takeaways"
_COLUMN_ROW_ID = "row_id"
_COLUMN_PAPER_ID = "paper_id"
_COLUMN_TAKEAWAY = "takeaway"
_COLUMN_METRICS = "metrics"
_COLUMN_CREATED_AT = "created_at"
_COLUMN_CREATED_BY = "created_by"


class AbstractTakeaway(BaseModel):
    row_id: int
    paper_id: str
    takeaway: str
    is_valid_for_product: bool


class TakeawayMetrics(BaseModel):
    takeaway_to_title_abstract_r1r: Optional[float]
    takeaway_length: int
    takeaway_distinct_pct: Optional[float]
    takeaway_non_special_char_pct: Optional[float]
    abstract_length: int
    abstract_distinct_pct: Optional[float]
    abstract_non_special_char_pct: Optional[float]


def _is_valid_for_product(metrics: TakeawayMetrics) -> bool:
    if (
        metrics.abstract_non_special_char_pct is None
        or metrics.abstract_distinct_pct is None
        or metrics.takeaway_to_title_abstract_r1r is None
        or metrics.takeaway_distinct_pct is None
        or metrics.takeaway_non_special_char_pct is None
    ):
        return False

    return (
        metrics.abstract_non_special_char_pct > 0.6
        and metrics.abstract_distinct_pct > 0.3
        and metrics.takeaway_to_title_abstract_r1r > 0.5
        and metrics.takeaway_length > 65
        and metrics.takeaway_distinct_pct > 0.55
        and metrics.takeaway_non_special_char_pct > 0.8
    )


def _db_row_to_model(row: Any) -> AbstractTakeaway:
    metrics = TakeawayMetrics(**row[_COLUMN_METRICS])
    return AbstractTakeaway(
        row_id=row[_COLUMN_ROW_ID],
        paper_id=row[_COLUMN_PAPER_ID],
        takeaway=row[_COLUMN_TAKEAWAY],
        is_valid_for_product=_is_valid_for_product(metrics),
    )


class AbstractTakeaways:
    """
    Interface class for reading/writing abstract takeaways stored in a DB.
    """

    def __init__(self, connection: psycopg2.extensions.connection):
        self.connection = connection

    def read_by_id(self, paper_id: str) -> Optional[AbstractTakeaway]:
        """
        Returns an abstract takeaway for the paper ID, or None if not found.

        Raises:
            ValueError: if more than 1 takeaway is found
        """

        sql = f"""
          SELECT * FROM {_TABLE_NAME}
            WHERE {_COLUMN_PAPER_ID} = %(id)s
          ORDER BY {_COLUMN_CREATED_AT} DESC
        """
        data = {"id": paper_id}
        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            results = cursor.fetchall()
            if not len(results):
                return None
            row = results[0]
            return _db_row_to_model(row)

    def write_takeaway(
        self,
        paper_id: str,
        takeaway: str,
        metrics: TakeawayMetrics,
        job_name: str,
        timestamp: Optional[datetime] = None,
        commit=False,
    ) -> AbstractTakeaway:
        """
        Writes an abstract takeaway to the database with a newly generated ID.
        """

        if not timestamp:
            timestamp = datetime.now(timezone.utc)
        validate_datetime(timestamp)

        sql = f"""
          INSERT INTO {_TABLE_NAME} (
            {_COLUMN_PAPER_ID},
            {_COLUMN_TAKEAWAY},
            {_COLUMN_METRICS},
            {_COLUMN_CREATED_AT},
            {_COLUMN_CREATED_BY}
          ) VALUES (
            %(paper_id)s,
            %(takeaway)s,
            %(metrics)s,
            %(created_at)s,
            %(created_by)s
          )
          RETURNING {_COLUMN_ROW_ID}
        """
        data = {
            "paper_id": paper_id,
            "takeaway": takeaway,
            "metrics": json.dumps(metrics.dict()),
            "created_at": timestamp,
            "created_by": job_name,
        }

        model = AbstractTakeaway(
            row_id=0,
            paper_id=paper_id,
            takeaway=takeaway,
            is_valid_for_product=_is_valid_for_product(metrics),
        )

        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            model.row_id = cursor.fetchone()[_COLUMN_ROW_ID]

        if commit:
            self.connection.commit()

        return model
