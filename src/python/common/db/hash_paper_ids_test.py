from datetime import datetime, timedelta, timezone

import pytest  # type: ignore
from common.db.hash_paper_ids import HashPaperId, HashPaperIds
from common.db.test.connect import MainDbTestClient


@pytest.fixture
def connection():
    with MainDbTestClient() as connection:
        yield connection


def test_write_succeeds(connection) -> None:
    db = HashPaperIds(connection)

    timestamp_1 = datetime.now(timezone.utc)
    actual = db.write_mapping(
        paper_id="paper_id_1",
        hash_paper_id="hash_paper_id_1",
        job_name="job_name_1",
        timestamp=timestamp_1,
        commit=True,
    )
    assert actual == HashPaperId(
        paper_id="paper_id_1",
        hash_paper_id="hash_paper_id_1",
        created_at=timestamp_1,
        created_by="job_name_1",
    )

    timestamp_2 = datetime.now(timezone.utc) + timedelta(minutes=1)
    actual = db.write_mapping(
        paper_id="paper_id_2",
        hash_paper_id="hash_paper_id_2",
        job_name="job_name_2",
        timestamp=timestamp_2,
        commit=True,
    )
    assert actual == HashPaperId(
        paper_id="paper_id_2",
        hash_paper_id="hash_paper_id_2",
        created_at=timestamp_2,
        created_by="job_name_2",
    )

    assert db.read_hash_paper_id(paper_id="paper_id_1") == "hash_paper_id_1"
    assert db.read_paper_id(hash_paper_id="hash_paper_id_1") == "paper_id_1"


def test_read_methods_return_none_if_unknown_id(connection) -> None:
    db = HashPaperIds(connection)
    assert db.read_hash_paper_id(paper_id="unknown") is None
    assert db.read_paper_id(hash_paper_id="unknown") is None


def test_write_returns_error_if_violating_unique_constraint(connection) -> None:
    timestamp = datetime.now(timezone.utc)

    paper_id = "paper_id"
    hash_paper_id = "hash_paper_id"

    db = HashPaperIds(connection)
    db.write_mapping(
        paper_id=paper_id,
        hash_paper_id=hash_paper_id,
        job_name="job_name",
        timestamp=timestamp,
        commit=True,
    )

    with pytest.raises(Exception):
        db.write_mapping(
            paper_id=paper_id,
            hash_paper_id="new_hash_paper_id",
            job_name="job_name",
            timestamp=timestamp,
            commit=True,
        )
    with pytest.raises(Exception):
        db.write_mapping(
            paper_id="new_paper_id",
            hash_paper_id=hash_paper_id,
            job_name="job_name",
            timestamp=timestamp,
            commit=True,
        )
