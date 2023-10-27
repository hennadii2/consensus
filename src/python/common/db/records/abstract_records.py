from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

import psycopg2
from common.beam.records.base_record import RecordDataHash, RecordStatus, hash_data_string
from common.time.convert import validate_datetime
from pydantic import BaseModel

_TABLE_NAME = "abstract_records"
_COL_ROW_ID = "row_id"
_COL_PAPER_ID = "paper_id"
_COL_VERSION = "version"
_COL_GCS_ABSTRACT_URL = "gcs_abstract_url"
_COL_STATUS = "status"
_COL_STATUS_MSG = "status_msg"
_COL_DATA_HASH = "data_hash"
_COL_CREATED_AT = "created_at"
_COL_CREATED_BY = "created_by"


class AbstractRecord(BaseModel):
    row_id: int
    paper_id: str
    gcs_abstract_url: str
    status: RecordStatus
    status_msg: Optional[str]
    data_hash: RecordDataHash
    created_at: datetime
    created_by: str
    version: str


def db_row_to_model(row: Any) -> AbstractRecord:
    return AbstractRecord(
        row_id=row[_COL_ROW_ID],
        paper_id=row[_COL_PAPER_ID],
        gcs_abstract_url=row[_COL_GCS_ABSTRACT_URL],
        status=RecordStatus(row[_COL_STATUS]),
        status_msg=row[_COL_STATUS_MSG],
        data_hash=row[_COL_DATA_HASH],
        created_at=row[_COL_CREATED_AT],
        created_by=row[_COL_CREATED_BY],
        version=row[_COL_VERSION],
    )


class AbstractRecords:
    """
    Interface class for reading/writing paper records stored in a DB.
    """

    def __init__(self, connection: psycopg2.extensions.connection):
        self.connection = connection

    def read_by_id(
        self,
        paper_id: str,
        active_only: bool,
        max_version: Optional[str],
    ) -> Optional[AbstractRecord]:
        """
        Reads the latest abstract record from the database for the given ID or returns
        None if not found. If max_version is set then the latest version will
        be limited to versions equal to or less than the value.

        Raises:
            ValueError: if more than 1 paper is found
        """

        sql = f"""
          SELECT * FROM {_TABLE_NAME}
            WHERE {_COL_PAPER_ID} = %(id)s
          ORDER BY {_COL_VERSION} DESC
        """
        data = {"id": paper_id}

        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            results = cursor.fetchall()
            if not len(results):
                return None
            for result in results:
                if max_version is not None and result[_COL_VERSION] > max_version:
                    continue
                if active_only and result[_COL_STATUS] != RecordStatus.ACTIVE.value:
                    return None
                paper = db_row_to_model(result)
                return paper
            return None

    def write_record(
        self,
        paper_id: str,
        version: str,
        gcs_abstract_url: str,
        status: RecordStatus,
        status_msg: Optional[str],
        input_data_hash: Optional[str],
        method_version_hash: Optional[str],
        job_name: str,
        timestamp: datetime,
        commit: bool,
    ) -> AbstractRecord:
        """
        Writes an abstract record to the database.

        Raises:
            ValueError: if paper fails validation of required fields
        """
        validate_datetime(timestamp)

        data_hash = RecordDataHash(
            method_version_hash=method_version_hash,
            input_data_hash=input_data_hash,
            output_data_hash=hash_data_string(gcs_abstract_url),
        )

        record = AbstractRecord(
            row_id=0,
            paper_id=paper_id,
            gcs_abstract_url=gcs_abstract_url,
            status=status,
            status_msg=status_msg,
            data_hash=data_hash,
            created_at=timestamp,
            created_by=job_name,
            version=version,
        )

        with self.connection.cursor() as cursor:
            cursor.execute(
                f"""
                  INSERT INTO {_TABLE_NAME} (
                    {_COL_PAPER_ID},
                    {_COL_GCS_ABSTRACT_URL},
                    {_COL_STATUS},
                    {_COL_STATUS_MSG},
                    {_COL_DATA_HASH},
                    {_COL_CREATED_AT},
                    {_COL_CREATED_BY},
                    {_COL_VERSION}
                  ) VALUES (
                    %(paper_id)s,
                    %(gcs_abstract_url)s,
                    %(status)s,
                    %(status_msg)s,
                    %(data_hash)s,
                    %(created_at)s,
                    %(created_by)s,
                    %(version)s
                  )
                  RETURNING {_COL_ROW_ID}
                """,
                {
                    "paper_id": record.paper_id,
                    "gcs_abstract_url": record.gcs_abstract_url,
                    "status": record.status.value,
                    "status_msg": record.status_msg,
                    "data_hash": record.data_hash.json(),
                    "created_at": record.created_at,
                    "created_by": record.created_by,
                    "version": record.version,
                },
            )
            record.row_id = cursor.fetchone()[_COL_ROW_ID]

        if commit:
            self.connection.commit()

        return record
