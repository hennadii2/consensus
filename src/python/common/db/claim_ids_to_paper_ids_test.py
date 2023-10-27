from datetime import datetime, timedelta, timezone

import pytest  # type: ignore
from common.db.claim_ids_to_paper_ids import ClaimIdsToPaperIds, ClaimIdToPaperId
from common.db.test.connect import MainDbTestClient


@pytest.fixture
def connection():
    with MainDbTestClient() as connection:
        yield connection


def test_write_claim_id_to_paper_id(connection) -> None:
    db = ClaimIdsToPaperIds(connection)
    timestamp = datetime.now(timezone.utc)

    actual = db.write_claim_id_to_paper_id(
        claim_id="fa98898926de5e1f8a5cdef5a3454f5d",
        paper_id="S2:1234",
        job_name="mock_job_name",
        timestamp=timestamp,
        commit=True,
    )
    expected = ClaimIdToPaperId(
        row_id=1,
        claim_id="fa98898926de5e1f8a5cdef5a3454f5d",
        paper_id="S2:1234",
    )
    assert actual == expected


def test_read_by_claim_id_succeeds(connection) -> None:
    db = ClaimIdsToPaperIds(connection)
    timestamp = datetime.now(timezone.utc)

    expected = db.write_claim_id_to_paper_id(
        claim_id="fa98898926de5e1f8a5cdef5a3454f5d",
        paper_id="S2:1234",
        job_name="mock_job_name",
        timestamp=timestamp,
        commit=True,
    )
    actual = db.read_by_claim_id(claim_id="fa98898926de5e1f8a5cdef5a3454f5d")
    assert actual == expected


def test_read_by_claim_id_returns_none(connection) -> None:
    db = ClaimIdsToPaperIds(connection)
    actual = db.read_by_claim_id("unknown")
    assert actual is None


def test_read_by_id_returns_latest(connection) -> None:
    db = ClaimIdsToPaperIds(connection)
    timestamp_1 = datetime.now(timezone.utc)
    timestamp_2 = timestamp_1 + timedelta(minutes=10)

    db = ClaimIdsToPaperIds(connection)

    mapping_1 = db.write_claim_id_to_paper_id(
        claim_id="fa98898926de5e1f8a5cdef5a3454f5d",
        paper_id="S2:1234",
        job_name="mock_job_name_1",
        timestamp=timestamp_1,
        commit=True,
    )
    actual = db.read_by_claim_id(claim_id="fa98898926de5e1f8a5cdef5a3454f5d")
    assert actual == mapping_1

    mapping_2 = db.write_claim_id_to_paper_id(
        claim_id="fa98898926de5e1f8a5cdef5a3454f5d",
        paper_id="S2:1234",
        job_name="mock_job_name_2",
        timestamp=timestamp_2,
        commit=True,
    )
    actual = db.read_by_claim_id(claim_id="fa98898926de5e1f8a5cdef5a3454f5d")
    assert actual == mapping_2
