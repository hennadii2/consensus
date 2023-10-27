import hashlib
import json
from datetime import datetime, timezone

import pytest  # type: ignore
from common.beam.records.base_record import RecordDataHash, RecordStatus
from common.db.records.paper_records import PaperRecord, PaperRecords
from common.db.test.connect import MainDbTestClient
from google.protobuf.json_format import MessageToJson
from paper_metadata_pb2 import PaperMetadata, PaperProvider


def valid_paper_metadata(provider_id: str = "providerId1") -> PaperMetadata:
    metadata = PaperMetadata()
    metadata.title = "title1"
    metadata.doi = "doi1"
    metadata.publish_year = 2022
    metadata.language = "en"
    metadata.author_names.append("author1")
    metadata.journal_name = "journal1"
    metadata.provider = PaperProvider.SEMANTIC_SCHOLAR
    metadata.provider_id = provider_id
    metadata.provider_url = "url"
    return metadata


@pytest.fixture
def connection():
    with MainDbTestClient() as connection:
        yield connection


def test_write_succeeds(connection) -> None:
    timestamp = datetime.now(timezone.utc)
    metadata = valid_paper_metadata()
    data_hash = RecordDataHash(
        input_data_hash="input_data_hash",
        method_version_hash="method_version_hash",
        output_data_hash=hashlib.sha256(
            MessageToJson(metadata, preserving_proto_field_name=True).encode()
        ).hexdigest()[:8],
    )

    records = PaperRecords(connection)
    actual = records.write_record(
        paper_id="paper_id",
        version="version_1",
        metadata=metadata,
        status=RecordStatus.ACTIVE,
        status_msg=None,
        input_data_hash="input_data_hash",
        method_version_hash="method_version_hash",
        job_name="job_name",
        timestamp=timestamp,
        commit=True,
    )
    actual_read = records.read_by_id(
        paper_id="paper_id",
        active_only=False,
        max_version=None,
    )
    expected = PaperRecord(
        row_id=1,
        paper_id="paper_id",
        metadata=metadata,
        status=RecordStatus.ACTIVE,
        status_msg=None,
        data_hash=data_hash,
        created_at=timestamp,
        created_by="job_name",
        version="version_1",
    )
    assert actual == actual_read
    assert actual == expected


def test_read_by_id_succeeds(connection) -> None:
    timestamp = datetime.now(timezone.utc)
    metadata = valid_paper_metadata()
    data_hash = RecordDataHash(
        input_data_hash="input_data_hash",
        method_version_hash="method_version_hash",
        output_data_hash="output_data_hash",
    )

    row_id = 0
    with connection.cursor() as cursor:
        cursor.execute(
            """
             INSERT INTO paper_records (
               paper_id,
               metadata,
               status,
               status_msg,
               data_hash,
               created_at,
               created_by,
               version
             ) VALUES (
               %(paper_id)s,
               %(metadata)s,
               %(status)s,
               %(status_msg)s,
               %(data_hash)s,
               %(created_at)s,
               %(created_by)s,
               %(version)s
             )
             RETURNING row_id
            """,
            {
                "paper_id": "paper_id",
                "metadata": MessageToJson(metadata, preserving_proto_field_name=True),
                "status": RecordStatus.ACTIVE.value,
                "status_msg": None,
                "data_hash": json.dumps(data_hash.dict()),
                "created_at": timestamp,
                "created_by": "job_name",
                "version": "version_1",
            },
        )
        row_id = cursor.fetchone()["row_id"]

    expected = PaperRecord(
        row_id=row_id,
        paper_id="paper_id",
        metadata=metadata,
        status=RecordStatus.ACTIVE,
        status_msg=None,
        data_hash=data_hash,
        created_at=timestamp,
        created_by="job_name",
        version="version_1",
    )

    records = PaperRecords(connection)
    actual = records.read_by_id(
        paper_id=expected.paper_id,
        active_only=False,
        max_version=None,
    )
    assert actual == expected


def test_read_by_id_latest_by_max_version(connection) -> None:
    timestamp = datetime.now(timezone.utc)
    metadata = valid_paper_metadata()

    records = PaperRecords(connection)
    record1 = records.write_record(
        paper_id="paper_id",
        version="version_1",
        metadata=metadata,
        status=RecordStatus.ACTIVE,
        status_msg=None,
        input_data_hash="input_data_hash",
        method_version_hash="method_version_hash",
        job_name="job_name",
        timestamp=timestamp,
        commit=True,
    )
    record2 = records.write_record(
        paper_id="paper_id",
        version="version_2",
        metadata=metadata,
        status=RecordStatus.ACTIVE,
        status_msg=None,
        input_data_hash="input_data_hash",
        method_version_hash="method_version_hash",
        job_name="job_name",
        timestamp=timestamp,
        commit=True,
    )

    actual = records.read_by_id(
        paper_id="paper_id",
        active_only=False,
        max_version=None,
    )
    assert actual == record2
    assert record1 != record2

    actual = records.read_by_id(
        paper_id="paper_id",
        active_only=False,
        max_version="version_1",
    )
    assert actual == record1


def test_read_by_id_latest_by_active_only(connection) -> None:
    timestamp = datetime.now(timezone.utc)
    metadata = valid_paper_metadata()

    records = PaperRecords(connection)
    record1 = records.write_record(
        paper_id="paper_id",
        version="version_1",
        metadata=metadata,
        status=RecordStatus.ACTIVE,
        status_msg=None,
        input_data_hash="input_data_hash",
        method_version_hash="method_version_hash",
        job_name="job_name",
        timestamp=timestamp,
        commit=True,
    )
    record2 = records.write_record(
        paper_id="paper_id",
        version="version_2",
        metadata=metadata,
        status=RecordStatus.DELETED,
        status_msg=None,
        input_data_hash="input_data_hash",
        method_version_hash="method_version_hash",
        job_name="job_name",
        timestamp=timestamp,
        commit=True,
    )

    actual = records.read_by_id(
        paper_id="paper_id",
        active_only=False,
        max_version=None,
    )
    assert actual == record2
    assert record1 != record2

    actual = records.read_by_id(
        paper_id="paper_id",
        active_only=True,
        max_version=None,
    )
    assert actual is None

    record3 = records.write_record(
        paper_id="paper_id",
        version="version_3",
        metadata=metadata,
        status=RecordStatus.ACTIVE,
        status_msg=None,
        input_data_hash="input_data_hash",
        method_version_hash="method_version_hash",
        job_name="job_name",
        timestamp=timestamp,
        commit=True,
    )
    actual = records.read_by_id(
        paper_id="paper_id",
        active_only=True,
        max_version=None,
    )
    assert actual == record3
