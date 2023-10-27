import json
from datetime import datetime, timezone

import pytest  # type: ignore
from common.beam.records.base_record import RecordStatus
from common.db.papers import PAPERS_TABLE, Papers
from common.db.papers_util import encode_clean_data_hash
from common.db.records.abstract_records import AbstractRecords
from common.db.records.paper_records import PaperRecords
from common.db.test.connect import MainDbTestClient
from google.protobuf.json_format import MessageToDict, MessageToJson
from paper_metadata_pb2 import PaperMetadata, PaperProvider
from paper_pb2 import PaperStatus


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


def test_read_by_id_succeeds(connection) -> None:
    timestamp = datetime.now(timezone.utc)
    timestamp_usec = int(timestamp.timestamp() * 1000000)

    old_status = PaperStatus()
    old_status.status = PaperStatus.Status.INGESTED
    old_status.ingested_by = "ingested_by_test"
    old_status.last_ingested_usec = timestamp_usec

    metadata = valid_paper_metadata()

    paper_id = None
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
             INSERT INTO {PAPERS_TABLE} (
               raw_data_url,
               clean_data_url,
               status,
               metadata,
               created_at,
               last_updated_at
             ) VALUES (
               %(raw_data_url)s,
               %(clean_data_url)s,
               %(status)s,
               %(metadata)s,
               %(created_at)s,
               %(last_updated_at)s
             )
             RETURNING id
            """,
            {
                "raw_data_url": "raw_data_url",
                "clean_data_url": "clean_data_url",
                "status": MessageToJson(old_status, preserving_proto_field_name=True),
                "metadata": MessageToJson(metadata, preserving_proto_field_name=True),
                "created_at": timestamp,
                "last_updated_at": timestamp,
            },
        )
        paper_id = cursor.fetchone()["id"]

    papers = Papers(connection)
    actual = papers.read_by_id(paper_id)

    assert actual is not None
    assert actual.id == paper_id
    assert actual.metadata == metadata
    assert actual.provider_metadata == ""


def test_read_by_id_returns_none_if_unknown_id(connection) -> None:
    papers = Papers(connection)
    actual = papers.read_by_id(5)
    assert actual is None


def test_read_by_id_succeeds_for_str_represenation_of_int_id(connection) -> None:
    papers = Papers(connection)

    timestamp1 = datetime.now(timezone.utc)
    metadata = valid_paper_metadata()
    metadata.provider = PaperProvider.SEMANTIC_SCHOLAR
    metadata.provider_id = "providerId1"

    paper = papers.write_paper(
        raw_data_url="raw_data_url",
        metadata=metadata,
        provider_metadata=None,
        job_name="ingested_by",
        timestamp=timestamp1,
        commit=False,
        update_if_exists=False,
    )
    assert paper.paper_id == "1"

    actual = papers.read_by_id("1")
    assert actual == paper
    actual = papers.read_by_id(1)
    assert actual == paper


def test_read_by_provider_id_succeeds(connection) -> None:
    timestamp1 = datetime.now(timezone.utc)

    papers = Papers(connection)
    metadata = valid_paper_metadata()
    metadata.provider = PaperProvider.SEMANTIC_SCHOLAR
    metadata.provider_id = "providerId1"

    paper = papers.write_paper(
        raw_data_url="raw_data_url",
        metadata=metadata,
        provider_metadata=None,
        job_name="ingested_by",
        timestamp=timestamp1,
        commit=False,
        update_if_exists=False,
    )

    actual = papers.read_by_provider_id(metadata.provider, metadata.provider_id)

    assert actual is not None
    assert actual.id == paper.id
    assert actual.metadata == metadata
    assert actual.metadata.provider == PaperProvider.SEMANTIC_SCHOLAR
    assert actual.metadata.provider_id == "providerId1"


def test_read_by_provider_id_returns_none_if_unknown_id(connection) -> None:
    timestamp1 = datetime.now(timezone.utc)

    papers = Papers(connection)
    metadata = valid_paper_metadata()
    metadata.provider = PaperProvider.SEMANTIC_SCHOLAR
    metadata.provider_id = "providerId1"

    papers.write_paper(
        raw_data_url="raw_data_url",
        metadata=metadata,
        provider_metadata=None,
        job_name="ingested_by",
        timestamp=timestamp1,
        commit=False,
        update_if_exists=False,
    )

    actual = papers.read_by_provider_id(metadata.provider, "unknown")

    assert actual is None


def test_read_all_with_status_succeeds(connection) -> None:
    timestamp = datetime.now(timezone.utc)
    ingested_by = "test_write_paper_succeeds"

    papers = Papers(connection)
    paper1 = papers.write_paper(
        raw_data_url="raw_data_url_1",
        metadata=valid_paper_metadata("providerId1"),
        job_name=ingested_by,
        provider_metadata=None,
        timestamp=None,
        commit=False,
        update_if_exists=False,
    )
    paper2 = papers.write_paper(
        raw_data_url="raw_data_url_2",
        metadata=valid_paper_metadata("providerId2"),
        job_name=ingested_by,
        provider_metadata=None,
        timestamp=None,
        commit=False,
        update_if_exists=False,
    )
    paper3 = papers.write_paper(
        raw_data_url="raw_data_url_3",
        metadata=valid_paper_metadata("providerId3"),
        job_name=ingested_by,
        provider_metadata=None,
        timestamp=None,
        commit=False,
        update_if_exists=False,
    )

    actual = []
    for paper in papers.read_all_with_status(PaperStatus.Status.INGESTED):
        actual.append(paper)
    assert len(actual) == 3
    assert actual[0] == paper1
    assert actual[1] == paper2
    assert actual[2] == paper3

    paper1 = papers.update_clean_data_url(
        paper_id=paper1.id,
        clean_data_url="clean_data_url1",
        abstract="",
        job_name="cleaned_by_job1",
        timestamp=timestamp,
        commit=False,
    )
    actual = []
    for paper in papers.read_all_with_status(PaperStatus.Status.INGESTED):
        actual.append(paper)
    assert len(actual) == 2
    assert actual[0] == paper2
    assert actual[1] == paper3
    actual = []
    for paper in papers.read_all_with_status(PaperStatus.Status.CLEANED):
        actual.append(paper)
    assert len(actual) == 1
    assert actual[0] == paper1


def test_read_all_with_status_on_empty_db_succeeds(connection) -> None:
    papers = Papers(connection)

    actual = []
    for paper in papers.read_all_with_status(PaperStatus.Status.INGESTED):
        actual.append(paper)

    assert len(actual) == 0


def test_write_paper_succeeds(connection) -> None:
    timestamp = datetime.now(timezone.utc)
    old_status = PaperStatus()
    old_status.status = PaperStatus.Status.INGESTED
    old_status.ingested_by = "test_write_paper_succeeds"
    old_status.last_ingested_usec = int(timestamp.timestamp() * 1000000)

    metadata = valid_paper_metadata()

    papers = Papers(connection)
    paper = papers.write_paper(
        raw_data_url="raw_data_url",
        metadata=metadata,
        job_name=old_status.ingested_by,
        provider_metadata=None,
        timestamp=timestamp,
        commit=False,
        update_if_exists=False,
    )

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {PAPERS_TABLE}")
        results = cursor.fetchall()

        assert len(results) == 1

        actual = results[0]

        assert actual["id"] == paper.id
        assert actual["raw_data_url"] == "raw_data_url"
        assert actual["clean_data_url"] is None
        assert actual["clean_data_hash"] is None
        assert actual["status"] == MessageToDict(old_status, preserving_proto_field_name=True)
        assert actual["metadata"] == MessageToDict(metadata, preserving_proto_field_name=True)
        assert actual["created_at"] == actual["last_updated_at"]


def test_write_paper_throws_error_if_metadata_is_invalid(connection) -> None:
    metadata = valid_paper_metadata()
    metadata.ClearField("title")

    papers = Papers(connection)

    with pytest.raises(ValueError, match="PaperMetadata is invalid: missing title"):
        papers.write_paper(
            raw_data_url="raw_data_url",
            metadata=metadata,
            job_name="throws_error",
            provider_metadata=None,
            timestamp=None,
            commit=False,
            update_if_exists=False,
        )


def test_write_paper_throws_error_if_provider_id_exists(connection) -> None:
    metadata = valid_paper_metadata()
    papers = Papers(connection)
    papers.write_paper(
        raw_data_url="raw_data_url",
        metadata=metadata,
        job_name="throws_error",
        provider_metadata=None,
        timestamp=None,
        commit=False,
        update_if_exists=False,
    )
    with pytest.raises(ValueError, match="Failed to write paper: provider ID already exists"):
        papers.write_paper(
            raw_data_url="raw_data_url",
            metadata=metadata,
            job_name="throws_error",
            provider_metadata=None,
            timestamp=None,
            commit=False,
            update_if_exists=False,
        )


def test_write_paper_updates_if_provider_id_exists_if_option_enabled(connection) -> None:
    metadata = valid_paper_metadata()
    papers = Papers(connection)
    paper = papers.write_paper(
        raw_data_url="raw_data_url",
        metadata=metadata,
        job_name="created",
        provider_metadata=None,
        timestamp=None,
        commit=False,
        update_if_exists=True,
    )
    assert paper.created_at_usec == paper.last_updated_at_usec
    assert paper.status.ingested_by == "created"

    paper = papers.write_paper(
        raw_data_url="raw_data_url",
        metadata=metadata,
        job_name="updated",
        provider_metadata=None,
        timestamp=None,
        commit=False,
        update_if_exists=True,
    )
    assert paper.created_at_usec != paper.last_updated_at_usec
    assert paper.status.ingested_by == "updated"


def test_update_metadata(connection) -> None:
    timestamp1 = datetime.now(timezone.utc)
    timestamp1_usec = int(timestamp1.timestamp() * 1000000)

    papers = Papers(connection)
    metadata = valid_paper_metadata()
    paper = papers.write_paper(
        raw_data_url="raw_data_url",
        metadata=metadata,
        provider_metadata=None,
        job_name="ingested_by",
        timestamp=timestamp1,
        commit=False,
        update_if_exists=False,
    )

    actual = papers.read_by_id(paper.id)
    expected = paper
    assert actual is not None
    assert actual == expected
    assert actual.clean_data_url == ""
    assert actual.clean_data_hash == ""
    assert actual.provider_metadata == ""
    assert actual.status.status == PaperStatus.Status.INGESTED
    assert actual.status.ingested_by == "ingested_by"
    assert actual.created_at_usec == timestamp1_usec
    assert actual.last_updated_at_usec == timestamp1_usec

    # Test that a call to update_metadata succeeds
    timestamp2 = datetime.now(timezone.utc)
    timestamp2_usec = int(timestamp2.timestamp() * 1000000)
    updated_metadata = valid_paper_metadata(provider_id="new_provider_id")
    assert updated_metadata != metadata
    provider_metadata = {"key1": "value1"}
    papers.update_metadata(
        paper_id=paper.id,
        raw_data_url="raw_data_url_2",
        metadata=updated_metadata,
        provider_metadata=provider_metadata,
        job_name="updated_by_job_2",
        timestamp=timestamp2,
        commit=False,
    )
    actual = papers.read_by_id(paper.id)

    expected.raw_data_url = "raw_data_url_2"
    expected.metadata.CopyFrom(updated_metadata)
    expected.provider_metadata = json.dumps(provider_metadata)
    expected.status.cleaned_by = ""
    expected.status.ingested_by = "updated_by_job_2"
    expected.status.status = PaperStatus.Status.INGESTED
    expected.status.last_cleaned_usec = 0
    expected.status.last_ingested_usec = timestamp2_usec
    expected.created_at_usec = timestamp1_usec
    expected.last_updated_at_usec = timestamp2_usec
    assert actual == expected

    # Test that a 2nd call to update_metadata succeeds after a call to clean
    timestamp3 = datetime.now(timezone.utc)
    timestamp3_usec = int(timestamp3.timestamp() * 1000000)
    updated_metadata2 = valid_paper_metadata(provider_id="new_provider_id_2")
    assert updated_metadata2 != updated_metadata
    papers.update_clean_data_url(
        paper_id=paper.id,
        clean_data_url="clean_data_url",
        abstract="0123456789",
        job_name="cleaned_by_job",
        timestamp=timestamp3,
        commit=False,
    )
    papers.update_metadata(
        paper_id=paper.id,
        raw_data_url="raw_data_url_3",
        metadata=updated_metadata2,
        provider_metadata=provider_metadata,
        job_name="updated_by_job_3",
        timestamp=timestamp3,
        commit=False,
    )
    actual = papers.read_by_id(paper.id)

    expected.raw_data_url = "raw_data_url_3"
    expected.clean_data_url = "clean_data_url"
    expected.clean_data_hash = encode_clean_data_hash("0123456789")
    updated_metadata2.abstract_length = 10
    expected.metadata.CopyFrom(updated_metadata2)
    expected.provider_metadata = json.dumps(provider_metadata)
    expected.status.cleaned_by = "cleaned_by_job"
    expected.status.ingested_by = "updated_by_job_3"
    expected.status.status = PaperStatus.Status.INGESTED
    expected.status.last_cleaned_usec = timestamp3_usec
    expected.status.last_ingested_usec = timestamp3_usec
    expected.created_at_usec = timestamp1_usec
    expected.last_updated_at_usec = timestamp3_usec
    assert actual == expected


def test_update_metadata_fails_if_paper_not_found(connection) -> None:
    papers = Papers(connection)
    metadata = valid_paper_metadata()

    with pytest.raises(ValueError, match="Failed to update paper metadata: paper 1 not found"):
        papers.update_metadata(
            paper_id=1,
            raw_data_url="raw_data_url",
            metadata=metadata,
            provider_metadata=None,
            job_name="ingested_by",
            timestamp=None,
            commit=False,
        )


def test_update_clean_data_url(connection) -> None:
    timestamp1 = datetime.now(timezone.utc)

    papers = Papers(connection)
    metadata = valid_paper_metadata()
    paper = papers.write_paper(
        raw_data_url="raw_data_url",
        metadata=metadata,
        job_name="ingested_by",
        provider_metadata={},
        timestamp=timestamp1,
        commit=False,
        update_if_exists=False,
    )

    actual = papers.read_by_id(paper.id)
    expected = paper
    assert actual is not None
    assert actual == expected
    assert actual.clean_data_url == ""
    assert actual.clean_data_hash == ""
    assert actual.status.status == PaperStatus.Status.INGESTED
    assert actual.metadata.abstract_length == 0

    # Test that a call to update_clean_dat_url succeeds
    papers.update_clean_data_url(
        paper_id=paper.id,
        clean_data_url="clean_data_url1",
        abstract="0123456789",
        job_name="cleaned_by_job1",
        timestamp=timestamp1,
        commit=False,
    )
    actual = papers.read_by_id(paper.id)

    timestamp1_usec = int(timestamp1.timestamp() * 1000000)
    expected.status.status = PaperStatus.Status.CLEANED
    expected.status.cleaned_by = "cleaned_by_job1"
    expected.status.last_cleaned_usec = timestamp1_usec
    expected.clean_data_url = "clean_data_url1"
    expected.clean_data_hash = encode_clean_data_hash("0123456789")
    expected.last_updated_at_usec = timestamp1_usec
    expected.metadata.abstract_length = 10
    assert actual == expected

    # Test that a 2nd call to update_clean_dat_url succeeds
    timestamp2 = datetime.now(timezone.utc)
    papers.update_clean_data_url(
        paper_id=paper.id,
        clean_data_url="clean_data_url2",
        abstract="01234567890123456789",
        job_name="cleaned_by_job2",
        timestamp=timestamp2,
        commit=False,
    )
    actual = papers.read_by_id(paper.id)

    timestamp2_usec = int(timestamp2.timestamp() * 1000000)
    expected.status.status = PaperStatus.Status.CLEANED
    expected.status.cleaned_by = "cleaned_by_job2"
    expected.status.last_cleaned_usec = timestamp2_usec
    expected.clean_data_url = "clean_data_url2"
    expected.clean_data_hash = encode_clean_data_hash("01234567890123456789")
    expected.last_updated_at_usec = timestamp2_usec
    expected.metadata.abstract_length = 20
    assert actual == expected


def test_update_clean_data_url_fails_if_paper_not_found(connection) -> None:
    papers = Papers(connection)

    with pytest.raises(ValueError, match="Failed to update clean data url: paper 1 not found"):
        papers.update_clean_data_url(
            paper_id=1,
            clean_data_url="clean_data_url2",
            abstract="0123456789",
            job_name="cleaned_by_job2",
            timestamp=None,
            commit=False,
        )


def test_read_by_id_use_v2_succeeds(connection) -> None:
    papers = Papers(connection, use_v2=True)
    paper_records = PaperRecords(connection)
    abstract_records = AbstractRecords(connection)

    timestamp = datetime.now(timezone.utc)
    metadata = valid_paper_metadata()

    paper_records.write_record(
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
    abstract_records.write_record(
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
    actual = papers.read_by_id("paper_id")

    assert actual is not None
    assert actual.id == 1
    assert actual.paper_id == "paper_id"
    assert actual.metadata == metadata
    assert actual.clean_data_url == "abstract_url"
