from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Iterator, Optional

import psycopg2
from common.db.papers_util import (
    encode_clean_data_hash,
    paper_provider_proto_enum_to_string,
    validate_metadata,
)
from common.db.records.abstract_records import AbstractRecord, AbstractRecords
from common.db.records.paper_records import PaperRecord, PaperRecords
from common.time.convert import TimeUnit, datetime_to_unix
from google.protobuf.json_format import MessageToJson, ParseDict
from loguru import logger
from paper_metadata_pb2 import PaperMetadata, PaperProvider
from paper_pb2 import Paper, PaperStatus

PAPERS_TABLE = "papers"
PAPERS_COLUMN_ID = "id"
PAPERS_COLUMN_RAW_DATA_URL = "raw_data_url"
PAPERS_COLUMN_CLEAN_DATA_URL = "clean_data_url"
PAPERS_COLUMN_CLEAN_DATA_HASH = "clean_data_hash"
PAPERS_COLUMN_STATUS = "status"
PAPERS_COLUMN_METADATA = "metadata"
PAPERS_COLUMN_PROVIDER_METADATA = "provider_metadata"
PAPERS_COLUMN_CREATED_AT = "created_at"
PAPERS_COLUMN_LAST_UPDATED_AT = "last_updated_at"


def papers_row_to_proto(row: Any) -> Paper:
    paper = Paper()
    paper.id = row[PAPERS_COLUMN_ID]
    # Create a string represenation of current int paper ID
    paper.paper_id = str(paper.id)
    paper.status.CopyFrom(ParseDict(row[PAPERS_COLUMN_STATUS], PaperStatus()))

    paper.metadata.CopyFrom(ParseDict(row[PAPERS_COLUMN_METADATA], PaperMetadata()))
    provider_metadata = row[PAPERS_COLUMN_PROVIDER_METADATA]
    if provider_metadata is not None:
        paper.provider_metadata = json.dumps(row[PAPERS_COLUMN_PROVIDER_METADATA])
    paper.raw_data_url = row[PAPERS_COLUMN_RAW_DATA_URL]
    clean_data_url = row[PAPERS_COLUMN_CLEAN_DATA_URL]
    if clean_data_url is not None:
        paper.clean_data_url = clean_data_url
    clean_data_hash = row[PAPERS_COLUMN_CLEAN_DATA_HASH]
    if clean_data_hash is not None:
        paper.clean_data_hash = clean_data_hash
    paper.created_at_usec = datetime_to_unix(row[PAPERS_COLUMN_CREATED_AT], TimeUnit.MICROSECONDS)
    paper.last_updated_at_usec = datetime_to_unix(
        row[PAPERS_COLUMN_LAST_UPDATED_AT], TimeUnit.MICROSECONDS
    )
    return paper


def _v2_records_to_proto(
    paper_record: PaperRecord,
    abstract_record: AbstractRecord,
) -> Paper:
    paper = Paper()
    paper.id = paper_record.row_id
    paper.paper_id = paper_record.paper_id
    paper.metadata.CopyFrom(paper_record.metadata)
    paper.clean_data_url = abstract_record.gcs_abstract_url
    paper.created_at_usec = datetime_to_unix(paper_record.created_at, TimeUnit.MICROSECONDS)
    return paper


class Papers:
    """
    Interface class for reading/writing papers stored in a DB.
    """

    def __init__(self, connection: psycopg2.extensions.connection, use_v2=False):
        self.connection = connection
        self.use_v2 = use_v2
        if use_v2:
            self.paper_records_for_v2 = PaperRecords(connection)
            self.abstract_records_for_v2 = AbstractRecords(connection)

    def read_all_with_status(self, status: PaperStatus.Status.V) -> Iterator[Paper]:
        """Reads all rows in the papers table using a server side cursor."""
        if self.use_v2:
            raise NotImplementedError("Papers.read_all_with_status not implemented for use_v2")

        sql = f""" SELECT * FROM {PAPERS_TABLE} """
        with self.connection.cursor("server_side_cursor") as cursor:
            cursor.execute(sql)
            for row in cursor:
                paper = papers_row_to_proto(row)
                if paper.status.status == status:
                    yield paper

    def read_by_id(
        self,
        paper_id: int | str,
    ) -> Optional[Paper]:
        """
        Reads a paper from the database for the given ID or returns None if not found.

        Raises:
            ValueError: if more than 1 paper is found
        """
        if self.use_v2:
            paper_record = self.paper_records_for_v2.read_by_id(
                paper_id=str(paper_id),
                active_only=True,
                max_version=None,
            )
            if paper_record is None:
                logger.error(f"Missing v2 paper record for {paper_id}")
                return None

            abstract_record = self.abstract_records_for_v2.read_by_id(
                paper_id=str(paper_id),
                active_only=True,
                max_version=None,
            )
            if abstract_record is None:
                logger.error(f"Missing v2 abstract record for {paper_id}")
                return None

            return _v2_records_to_proto(
                paper_record=paper_record,
                abstract_record=abstract_record,
            )
        else:
            sql = f"""
              SELECT * FROM {PAPERS_TABLE} WHERE {PAPERS_COLUMN_ID} = %(id)s
            """
            data = {"id": paper_id}
            with self.connection.cursor() as cursor:
                cursor.execute(sql, data)
                results = cursor.fetchall()
                if not len(results):
                    return None
                if len(results) > 1:
                    raise ValueError(
                        "Failed to read paper by id: found {} results, expected 1".format(
                            len(results)
                        )
                    )
                row = results[0]
                paper = papers_row_to_proto(row)
                return paper

    def read_by_provider_id(self, provider: PaperProvider.V, provider_id: str) -> Optional[Paper]:
        """
        Reads a paper from the database for the given provider or returns None if not found.
        Raises:
            ValueError: if more than 1 paper is found
        """
        if self.use_v2:
            raise NotImplementedError("Papers.read_by_provider_id not implemented for use_v2")

        sql = f"""
          SELECT * FROM {PAPERS_TABLE}
          WHERE ({PAPERS_COLUMN_METADATA}->>'provider_id') = %(provider_id)s
            AND ({PAPERS_COLUMN_METADATA}->>'provider') = %(provider_string)s
        """
        data = {
            "provider_id": provider_id,
            "provider_string": paper_provider_proto_enum_to_string(provider),
        }
        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            results = cursor.fetchall()
            if not len(results):
                return None
            if len(results) > 1:
                raise ValueError(
                    "Failed to read paper by provider id: found {} results, expected 1".format(
                        len(results)
                    )
                )
            row = results[0]
            paper = papers_row_to_proto(row)
            return paper

    def write_paper(
        self,
        raw_data_url: str,
        metadata: PaperMetadata,
        provider_metadata: Optional[dict],
        job_name: str,
        timestamp: Optional[datetime],
        commit: bool,
        update_if_exists: bool,
    ) -> Paper:
        """
        Writes a paper to the database with a newly generated ID and fails
        if its provider ID already exists.

        Raises:
            ValueError: if paper fails validation of required fields
        """
        if self.use_v2:
            raise NotImplementedError("Papers.write_paper not implemented for use_v2")

        validate_metadata(metadata)

        paper = self.read_by_provider_id(metadata.provider, metadata.provider_id)
        if paper:
            if update_if_exists:
                return self.update_metadata(
                    paper_id=paper.id,
                    raw_data_url=raw_data_url,
                    metadata=metadata,
                    provider_metadata=provider_metadata,
                    job_name=job_name,
                    timestamp=timestamp,
                    commit=commit,
                )
            raise ValueError("Failed to write paper: provider ID already exists")

        if not timestamp:
            timestamp = datetime.now(timezone.utc)
        timestamp_usec = datetime_to_unix(timestamp, TimeUnit.MICROSECONDS)

        status = PaperStatus()
        status.status = PaperStatus.Status.INGESTED
        status.ingested_by = job_name
        status.last_ingested_usec = timestamp_usec

        sql = f"""
          INSERT INTO {PAPERS_TABLE} (
            {PAPERS_COLUMN_RAW_DATA_URL},
            {PAPERS_COLUMN_CLEAN_DATA_URL},
            {PAPERS_COLUMN_CLEAN_DATA_HASH},
            {PAPERS_COLUMN_STATUS},
            {PAPERS_COLUMN_METADATA},
            {PAPERS_COLUMN_PROVIDER_METADATA},
            {PAPERS_COLUMN_CREATED_AT},
            {PAPERS_COLUMN_LAST_UPDATED_AT}
          ) VALUES (
            %(raw_data_url)s,
            %(clean_data_url)s,
            %(clean_data_hash)s,
            %(status)s,
            %(metadata)s,
            %(provider_metadata)s,
            %(created_at)s,
            %(last_updated_at)s
          )
          RETURNING {PAPERS_COLUMN_ID}
        """
        data = {
            "raw_data_url": raw_data_url,
            "clean_data_url": None,
            "clean_data_hash": None,
            "status": MessageToJson(status, preserving_proto_field_name=True),
            "metadata": MessageToJson(metadata, preserving_proto_field_name=True),
            "provider_metadata": None
            if provider_metadata is None
            else json.dumps(provider_metadata),
            "created_at": timestamp,
            "last_updated_at": timestamp,
        }

        paper = Paper()
        paper.metadata.CopyFrom(metadata)
        if provider_metadata is not None:
            paper.provider_metadata = json.dumps(provider_metadata)
        paper.status.CopyFrom(status)
        paper.raw_data_url = raw_data_url
        paper.created_at_usec = timestamp_usec
        paper.last_updated_at_usec = timestamp_usec

        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            paper.id = cursor.fetchone()[PAPERS_COLUMN_ID]
            paper.paper_id = str(paper.id)

        if commit:
            self.connection.commit()

        return paper

    def update_metadata(
        self,
        paper_id: int,
        raw_data_url: str,
        metadata: PaperMetadata,
        provider_metadata: Optional[dict],
        job_name: str,
        timestamp: Optional[datetime],
        commit: bool,
    ) -> Paper:
        """
        Updates metadata and ingestion fields on the paper.

        Raises:
            ValueError: if paper fails validation of required fields
        """
        if self.use_v2:
            raise NotImplementedError("Papers.update_metadata not implemented for use_v2")

        paper = self.read_by_id(paper_id=paper_id)
        if not paper:
            raise ValueError(f"Failed to update paper metadata: paper {paper_id} not found")

        if not timestamp:
            timestamp = datetime.now(timezone.utc)
        timestamp_usec = datetime_to_unix(timestamp, TimeUnit.MICROSECONDS)

        status = paper.status
        status.status = PaperStatus.Status.INGESTED
        status.ingested_by = job_name
        status.last_ingested_usec = timestamp_usec

        # Avoid overwriting abstract length since we are not updating the abstract here
        # TODO(meganvw): Move abstract_length to column instead of metadata
        metadata.abstract_length = paper.metadata.abstract_length

        sql = f"""
          UPDATE {PAPERS_TABLE}
          SET
            {PAPERS_COLUMN_STATUS} = %(status)s,
            {PAPERS_COLUMN_RAW_DATA_URL} = %(raw_data_url)s,
            {PAPERS_COLUMN_METADATA} = %(metadata)s,
            {PAPERS_COLUMN_PROVIDER_METADATA} = %(provider_metadata)s,
            {PAPERS_COLUMN_LAST_UPDATED_AT} = %(timestamp)s
          WHERE {PAPERS_COLUMN_ID} = %(paper_id)s
        """
        data = {
            "status": MessageToJson(status, preserving_proto_field_name=True),
            "raw_data_url": raw_data_url,
            "metadata": MessageToJson(metadata, preserving_proto_field_name=True),
            "provider_metadata": None
            if provider_metadata is None
            else json.dumps(provider_metadata),
            "timestamp": timestamp,
            "paper_id": paper_id,
        }
        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)

        if commit:
            self.connection.commit()

        paper.raw_data_url = raw_data_url
        paper.metadata.CopyFrom(metadata)
        if provider_metadata is not None:
            paper.provider_metadata = json.dumps(provider_metadata)
        paper.status.CopyFrom(status)
        paper.last_updated_at_usec = timestamp_usec

        return paper

    def update_clean_data_url(
        self,
        paper_id: int,
        clean_data_url: str,
        abstract: str,
        job_name: str,
        timestamp: Optional[datetime],
        commit: bool,
    ) -> Paper:
        """
        Updates the clean data URL for a paper.

        Raises:
            ValueError: if paper fails validation of required fields
        """
        if self.use_v2:
            raise NotImplementedError("Papers.update_clean_data_url not implemented for use_v2")

        paper = self.read_by_id(paper_id)
        if not paper:
            raise ValueError(f"Failed to update clean data url: paper {paper_id} not found")

        if not timestamp:
            timestamp = datetime.now(timezone.utc)
        timestamp_usec = datetime_to_unix(timestamp, TimeUnit.MICROSECONDS)

        status = paper.status
        status.status = PaperStatus.Status.CLEANED
        status.cleaned_by = job_name
        status.last_cleaned_usec = timestamp_usec

        # TODO(meganvw): Move abstract_length to column instead of metadata
        metadata = paper.metadata
        metadata.abstract_length = len(abstract)

        clean_data_hash = encode_clean_data_hash(abstract)

        sql = f"""
          UPDATE {PAPERS_TABLE}
          SET
            {PAPERS_COLUMN_CLEAN_DATA_URL} = %(clean_data_url)s,
            {PAPERS_COLUMN_CLEAN_DATA_HASH} = %(clean_data_hash)s,
            {PAPERS_COLUMN_METADATA} = %(metadata)s,
            {PAPERS_COLUMN_STATUS} = %(status)s,
            {PAPERS_COLUMN_LAST_UPDATED_AT} = %(timestamp)s
          WHERE {PAPERS_COLUMN_ID} = %(paper_id)s
        """
        data = {
            "clean_data_url": clean_data_url,
            "clean_data_hash": clean_data_hash,
            "metadata": MessageToJson(metadata, preserving_proto_field_name=True),
            "status": MessageToJson(status, preserving_proto_field_name=True),
            "timestamp": timestamp,
            "paper_id": paper_id,
        }
        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)

        if commit:
            self.connection.commit()

        paper.clean_data_url = clean_data_url
        paper.clean_data_hash = clean_data_hash
        paper.metadata.CopyFrom(metadata)
        paper.status.CopyFrom(status)
        paper.last_updated_at_usec = timestamp_usec

        return paper
