import json
from datetime import datetime, timezone

import pytest  # type: ignore
from common.beam.records.base_record import RecordDataHash, RecordStatus, hash_data_string
from common.db.records.abstract_records import AbstractRecord, AbstractRecords
from common.db.test.connect import MainDbTestClient


def valid_data_hash() -> RecordDataHash:
    return RecordDataHash(
        input_data_hash="input_data_hash",
        method_version_hash="method_version_hash",
        output_data_hash="output_data_hash",
    )


@pytest.fixture
def connection():
    with MainDbTestClient() as connection:
        yield connection


def test_write_succeeds(connection) -> None:
    timestamp = datetime.now(timezone.utc)

    records = AbstractRecords(connection)
    actual = records.write_record(
        paper_id="paper_id",
        version="version_1",
        gcs_abstract_url="abstract_url",
        status=RecordStatus.ACTIVE,
        status_msg=None,
        method_version_hash="method_version_hash",
        input_data_hash="input_data_hash",
        job_name="job_name",
        timestamp=timestamp,
        commit=True,
    )
    actual_read = records.read_by_id(
        paper_id="paper_id",
        active_only=False,
        max_version=None,
    )
    expected = AbstractRecord(
        row_id=1,
        paper_id="paper_id",
        gcs_abstract_url="abstract_url",
        status=RecordStatus.ACTIVE,
        status_msg=None,
        data_hash=RecordDataHash(
            method_version_hash="method_version_hash",
            input_data_hash="input_data_hash",
            output_data_hash=hash_data_string("abstract_url"),
        ),
        created_at=timestamp,
        created_by="job_name",
        version="version_1",
    )
    assert actual == actual_read
    assert actual == expected


def test_read_by_id_succeeds(connection) -> None:
    timestamp = datetime.now(timezone.utc)
    data_hash = valid_data_hash()

    row_id = 0
    with connection.cursor() as cursor:
        cursor.execute(
            """
             INSERT INTO abstract_records (
               paper_id,
               gcs_abstract_url,
               status,
               status_msg,
               data_hash,
               created_at,
               created_by,
               version
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
             RETURNING row_id
            """,
            {
                "paper_id": "paper_id",
                "gcs_abstract_url": "gcs_path",
                "status": RecordStatus.ACTIVE.value,
                "status_msg": None,
                "data_hash": json.dumps(data_hash.dict()),
                "created_at": timestamp,
                "created_by": "job_name",
                "version": "version_1",
            },
        )
        row_id = cursor.fetchone()["row_id"]

    expected = AbstractRecord(
        row_id=row_id,
        paper_id="paper_id",
        gcs_abstract_url="gcs_path",
        status=RecordStatus.ACTIVE,
        status_msg=None,
        data_hash=data_hash,
        created_at=timestamp,
        created_by="job_name",
        version="version_1",
    )

    records = AbstractRecords(connection)
    actual = records.read_by_id(paper_id=expected.paper_id, active_only=False, max_version=None)
    assert actual == expected


def test_read_by_id_latest_by_max_version(connection) -> None:
    timestamp = datetime.now(timezone.utc)

    records = AbstractRecords(connection)
    record1 = records.write_record(
        paper_id="paper_id",
        version="version_1",
        gcs_abstract_url="path_1",
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
        gcs_abstract_url="path_2",
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

    records = AbstractRecords(connection)
    record1 = records.write_record(
        paper_id="paper_id",
        version="version_1",
        gcs_abstract_url="path_1",
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
        gcs_abstract_url="path_2",
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
        gcs_abstract_url="path_2",
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
