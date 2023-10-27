from datetime import datetime, timedelta, timezone

import pytest  # type: ignore
from common.db.abstract_takeaways import AbstractTakeaway, AbstractTakeaways, TakeawayMetrics
from common.db.test.connect import MainDbTestClient

MOCK_METRICS = TakeawayMetrics(
    takeaway_to_title_abstract_r1r=1.0,
    takeaway_length=100,
    takeaway_distinct_pct=1.0,
    takeaway_non_special_char_pct=1.0,
    abstract_length=100,
    abstract_distinct_pct=1.0,
    abstract_non_special_char_pct=100,
)


@pytest.fixture
def connection():
    with MainDbTestClient() as connection:
        yield connection


def test_write_takeaway(connection) -> None:
    db = AbstractTakeaways(connection)
    timestamp = datetime.now(timezone.utc)

    actual = db.write_takeaway(
        paper_id="S2:1234",
        takeaway="mock takeaway",
        metrics=MOCK_METRICS,
        job_name="mock_job_name",
        timestamp=timestamp,
        commit=True,
    )
    expected = AbstractTakeaway(
        row_id=1,
        paper_id="S2:1234",
        takeaway="mock takeaway",
        is_valid_for_product=True,
    )
    assert actual == expected


def test_read_by_id_succeeds(connection) -> None:
    db = AbstractTakeaways(connection)
    timestamp = datetime.now(timezone.utc)

    expected = db.write_takeaway(
        paper_id="S2:1234",
        takeaway="mock takeaway",
        metrics=MOCK_METRICS,
        job_name="mock_job_name",
        timestamp=timestamp,
        commit=True,
    )
    actual = db.read_by_id("S2:1234")
    assert actual == expected


def test_read_by_id_returns_none(connection) -> None:
    db = AbstractTakeaways(connection)
    actual = db.read_by_id("unknown")
    assert actual is None


def test_read_by_id_returns_latest(connection) -> None:
    db = AbstractTakeaways(connection)
    timestamp_1 = datetime.now(timezone.utc)
    timestamp_2 = timestamp_1 + timedelta(minutes=10)

    db = AbstractTakeaways(connection)

    takeaway_1 = db.write_takeaway(
        paper_id="S2:1234",
        takeaway="mock takeaway 1",
        metrics=MOCK_METRICS,
        job_name="mock_job_name_1",
        timestamp=timestamp_1,
        commit=True,
    )
    actual = db.read_by_id("S2:1234")
    assert actual == takeaway_1

    takeaway_2 = db.write_takeaway(
        paper_id="S2:1234",
        takeaway="mock takeaway 2",
        metrics=MOCK_METRICS,
        job_name="mock_job_name_2",
        timestamp=timestamp_2,
        commit=True,
    )
    actual = db.read_by_id("S2:1234")
    assert actual == takeaway_2


def test_metrics_set_is_valid_for_product(connection) -> None:
    db = AbstractTakeaways(connection)
    timestamp_1 = datetime.now(timezone.utc)
    timestamp_2 = timestamp_1 + timedelta(minutes=10)

    expected = db.write_takeaway(
        paper_id="S2:1234",
        takeaway="mock takeaway",
        metrics=MOCK_METRICS,
        job_name="mock_job_name",
        timestamp=timestamp_1,
        commit=True,
    )
    actual = db.read_by_id("S2:1234")
    assert actual is not None
    assert actual.is_valid_for_product is True
    assert expected.is_valid_for_product is True

    expected = db.write_takeaway(
        paper_id="S2:1234",
        takeaway="mock takeaway",
        metrics=TakeawayMetrics(
            takeaway_to_title_abstract_r1r=0,
            takeaway_length=0,
            takeaway_distinct_pct=0,
            takeaway_non_special_char_pct=0,
            abstract_length=0,
            abstract_distinct_pct=0,
            abstract_non_special_char_pct=0,
        ),
        job_name="mock_job_name",
        timestamp=timestamp_2,
        commit=True,
    )
    actual = db.read_by_id("S2:1234")
    assert actual is not None
    assert actual.is_valid_for_product is False
    assert expected.is_valid_for_product is False
