from datetime import datetime, timezone

import pytest  # type: ignore
from common.db.journal_scores import JOURNAL_SCORES_TABLE, JournalScores
from common.db.test.connect import MainDbTestClient
from google.protobuf.json_format import MessageToDict, ParseDict
from journal_pb2 import JournalScoreMetadata, JournalScoreProvider


def mock_computed_score(
    percentile_rank=10,
) -> JournalScoreMetadata:
    return ParseDict(
        {
            "computed_score": {
                "percentile_rank": percentile_rank,
            },
        },
        JournalScoreMetadata(),
    )


@pytest.fixture
def connection():
    with MainDbTestClient() as connection:
        yield connection


def test_write_score_succeeds(connection) -> None:
    timestamp = datetime.now(timezone.utc)
    fmt = "%y%m%d%H%M%S%.f"

    scores = JournalScores(connection)

    metadata = JournalScoreMetadata()
    metadata.computed_score.percentile_rank = 5
    scores.write_score(
        journal_id=10,
        year=2022,
        provider=JournalScoreProvider.COMPUTED,
        metadata=metadata,
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {JOURNAL_SCORES_TABLE}")
        results = cursor.fetchall()

        assert len(results) == 1

        actual = results[0]

        assert actual["id"] == 1
        assert actual["journal_id"] == 10
        assert actual["year"] == 2022
        assert actual["provider"] == "COMPUTED"
        assert actual["metadata"] == MessageToDict(metadata, preserving_proto_field_name=True)
        assert actual["created_at"].strftime(fmt) == timestamp.strftime(fmt)
        assert actual["created_by"] == "test_job"


def test_write_provider_score_succeeds(connection) -> None:
    timestamp = datetime.now(timezone.utc)
    fmt = "%y%m%d%H%M%S"

    scores = JournalScores(connection)

    metadata = JournalScoreMetadata()
    metadata.sci_score.raw_data_url = "raw_data_url"
    metadata.sci_score.avg_score = 5.0
    metadata.sci_score.percentile_rank = 50
    scores.write_score(
        journal_id=10,
        year=2022,
        provider=JournalScoreProvider.SCI_SCORE,
        metadata=metadata,
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {JOURNAL_SCORES_TABLE}")
        results = cursor.fetchall()

        assert len(results) == 1

        actual = results[0]

        assert actual["id"] == 1
        assert actual["journal_id"] == 10
        assert actual["year"] == 2022
        assert actual["provider"] == "SCI_SCORE"
        assert actual["metadata"] == MessageToDict(metadata, preserving_proto_field_name=True)
        assert actual["created_at"].strftime(fmt) == timestamp.strftime(fmt)
        assert actual["created_by"] == "test_job"


def test_get_scores_succeeds(connection) -> None:
    timestamp = datetime.now(timezone.utc)

    scores = JournalScores(connection)
    score_1999 = scores.write_score(
        journal_id=1,
        year=1999,
        provider=JournalScoreProvider.COMPUTED,
        metadata=mock_computed_score(percentile_rank=10),
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )
    score_2000 = scores.write_score(
        journal_id=1,
        year=2000,
        provider=JournalScoreProvider.COMPUTED,
        metadata=mock_computed_score(percentile_rank=10),
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )
    score_2022 = scores.write_score(
        journal_id=1,
        year=2022,
        provider=JournalScoreProvider.COMPUTED,
        metadata=mock_computed_score(percentile_rank=10),
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )
    expected = [score_2000]
    actual = scores.get_scores(
        journal_id=1,
        year=2000,
        year_bound=0,
        provider=JournalScoreProvider.COMPUTED,
    )
    assert actual == expected

    expected = [score_1999, score_2000]
    actual = scores.get_scores(
        journal_id=1,
        year=2000,
        year_bound=5,
        provider=JournalScoreProvider.COMPUTED,
    )
    assert actual == expected

    expected = [score_1999, score_2000, score_2022]
    actual = scores.get_scores(
        journal_id=1,
        year=2000,
        year_bound=30,
        provider=JournalScoreProvider.COMPUTED,
    )
    assert actual == expected


def test_get_score_succeeds(connection) -> None:
    timestamp = datetime.now(timezone.utc)

    scores = JournalScores(connection)
    score_2000 = scores.write_score(
        journal_id=1,
        year=2000,
        provider=JournalScoreProvider.COMPUTED,
        metadata=mock_computed_score(percentile_rank=10),
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )
    expected = score_2000
    actual = scores.get_score(
        journal_id=1,
        year=2000,
        provider=JournalScoreProvider.COMPUTED,
    )
    assert actual == expected

    actual = scores.get_score(
        journal_id=1,
        year=1990,
        provider=JournalScoreProvider.COMPUTED,
    )
    assert actual is None


def test_get_scores_returns_latest_version(connection) -> None:
    scores = JournalScores(connection)

    timestamp = datetime.now(timezone.utc)
    score_2000_v1 = scores.write_score(
        journal_id=1,
        year=2000,
        provider=JournalScoreProvider.COMPUTED,
        metadata=mock_computed_score(percentile_rank=10),
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )
    score_2022_v1 = scores.write_score(
        journal_id=1,
        year=2022,
        provider=JournalScoreProvider.COMPUTED,
        metadata=mock_computed_score(percentile_rank=10),
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )
    timestamp = datetime.now(timezone.utc)
    score_2000_v2 = scores.write_score(
        journal_id=1,
        year=2000,
        provider=JournalScoreProvider.COMPUTED,
        metadata=mock_computed_score(percentile_rank=10),
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )
    score_2022_v2 = scores.write_score(
        journal_id=1,
        year=2022,
        provider=JournalScoreProvider.COMPUTED,
        metadata=mock_computed_score(percentile_rank=10),
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )
    assert score_2000_v1 != score_2000_v2
    assert score_2022_v1 != score_2022_v2

    expected = [score_2000_v2, score_2022_v2]
    actual = scores.get_scores(
        journal_id=1,
        year=2000,
        year_bound=30,
        provider=JournalScoreProvider.COMPUTED,
    )
    assert actual == expected


def test_get_score_returns_latest_version(connection) -> None:
    scores = JournalScores(connection)

    timestamp = datetime.now(timezone.utc)
    score_2000_v1 = scores.write_score(
        journal_id=1,
        year=2000,
        provider=JournalScoreProvider.COMPUTED,
        metadata=mock_computed_score(percentile_rank=10),
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )
    timestamp = datetime.now(timezone.utc)
    score_2000_v2 = scores.write_score(
        journal_id=1,
        year=2000,
        provider=JournalScoreProvider.COMPUTED,
        metadata=mock_computed_score(percentile_rank=10),
        job_name="test_job",
        timestamp=timestamp,
        commit=True,
    )
    assert score_2000_v1 != score_2000_v2

    actual = scores.get_score(
        journal_id=1,
        year=2000,
        provider=JournalScoreProvider.COMPUTED,
    )
    assert actual == score_2000_v2


def test_get_latest_scimago_quartile(connection) -> None:
    scores = JournalScores(connection)

    timestamp = datetime.now(timezone.utc)
    metadata = JournalScoreMetadata()
    metadata.scimago.raw_data_url = "raw_data_url"

    actual = scores.get_latest_scimago_quartile(
        journal_id=1,
    )
    assert actual is None

    metadata.scimago.best_quartile = 2
    scores.write_score(
        journal_id=1,
        year=2000,
        provider=JournalScoreProvider.SCIMAGO,
        metadata=metadata,
        job_name="test_job",
        timestamp=timestamp,
    )
    actual = scores.get_latest_scimago_quartile(
        journal_id=1,
    )
    assert actual == 2

    timestamp = datetime.now(timezone.utc)
    metadata.scimago.best_quartile = 3
    scores.write_score(
        journal_id=1,
        year=2000,
        provider=JournalScoreProvider.SCIMAGO,
        metadata=metadata,
        job_name="test_job",
        timestamp=timestamp,
    )
    actual = scores.get_latest_scimago_quartile(
        journal_id=1,
    )
    assert actual == 3

    metadata.scimago.best_quartile = 4
    scores.write_score(
        journal_id=1,
        year=2015,
        provider=JournalScoreProvider.SCIMAGO,
        metadata=metadata,
        job_name="test_job",
        timestamp=timestamp,
    )
    actual = scores.get_latest_scimago_quartile(
        journal_id=1,
    )
    assert actual == 4

    timestamp = datetime.now(timezone.utc)
    metadata.scimago.best_quartile = 0
    scores.write_score(
        journal_id=1,
        year=2015,
        provider=JournalScoreProvider.SCIMAGO,
        metadata=metadata,
        job_name="test_job",
        timestamp=timestamp,
    )
    actual = scores.get_latest_scimago_quartile(
        journal_id=1,
    )
    assert actual is None
