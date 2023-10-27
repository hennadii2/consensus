from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import pytest  # type: ignore
from common.db.journal_scores import JournalScores
from common.db.journal_util import get_journal_scimago_quartile, get_journal_score
from common.db.journals import Journals
from common.db.test.connect import MainDbTestClient
from journal_pb2 import JournalScoreMetadata, JournalScoreProvider
from paper_metadata_pb2 import PaperMetadata

PUBLISH_YEAR = 2000


def mock_computed_score(percentile_rank: int) -> JournalScoreMetadata:
    score_metadata = JournalScoreMetadata()
    score_metadata.computed_score.percentile_rank = percentile_rank
    return score_metadata


def mock_scimago_score(best_quartile: int) -> JournalScoreMetadata:
    score_metadata = JournalScoreMetadata()
    score_metadata.scimago.raw_data_url = "raw_data_url"
    score_metadata.scimago.best_quartile = best_quartile
    return score_metadata


def mock_paper_metadata(
    journal_name: str,
    journal_issn: Optional[str],
    journal_alternate_issns: Optional[list[str]],
) -> PaperMetadata:
    paper_metadata = PaperMetadata()
    paper_metadata.journal_name = journal_name
    paper_metadata.publish_year = PUBLISH_YEAR
    if journal_issn:
        paper_metadata.journal_issn = journal_issn
    if journal_alternate_issns:
        for issn in journal_alternate_issns:
            paper_metadata.journal_alternate_issns.append(issn)
    return paper_metadata


# Helper function for brevity
def _write_journal(
    journals: Journals,
    name: str,
    print_issn: Optional[str],
    electronic_issn: Optional[str],
) -> int:
    journal = journals.write_journal(
        name=name,
        print_issn=print_issn,
        electronic_issn=electronic_issn,
        job_name="test_job",
        timestamp=datetime.now(timezone.utc),
        commit=True,
    )
    return journal.id


# Helper function for brevity
def _write_score(
    scores: JournalScores,
    provider: JournalScoreProvider.V,
    metadata: JournalScoreMetadata,
    journal_id: int,
    year: int = PUBLISH_YEAR,
) -> None:
    scores.write_score(
        journal_id=journal_id,
        year=year,
        provider=provider,
        metadata=metadata,
        job_name="test_job",
        timestamp=datetime.now(timezone.utc),
        commit=True,
    )


@pytest.fixture
def journals():
    with MainDbTestClient() as connection:
        journals = Journals(connection)
        yield journals


@pytest.fixture
def scores():
    with MainDbTestClient() as connection:
        scores = JournalScores(connection)
        yield scores


def test_get_journal_score_succeeds_by_name(journals, scores) -> None:
    journal_id = _write_journal(
        journals,
        name="Test Journal",
        print_issn=None,
        electronic_issn=None,
    )
    _write_score(
        scores,
        journal_id=journal_id,
        provider=JournalScoreProvider.COMPUTED,
        metadata=mock_computed_score(percentile_rank=10),
    )
    metadata = mock_paper_metadata(
        journal_name="Test Journal",  # Name matches
        journal_issn=None,
        journal_alternate_issns=None,
    )

    actual = get_journal_score(
        journals=journals,
        journal_scores=scores,
        paper_metadata=metadata,
        use_issn=False,  # Match by name
    )
    assert actual and actual.metadata.computed_score.percentile_rank == 10


def test_get_journal_score_fails_by_name(journals, scores) -> None:
    journal_id = _write_journal(
        journals,
        name="Test Journal",
        print_issn="1234-5678",
        electronic_issn=None,
    )
    _write_score(
        scores,
        journal_id=journal_id,
        provider=JournalScoreProvider.COMPUTED,
        metadata=mock_computed_score(percentile_rank=10),
    )
    metadata = mock_paper_metadata(
        journal_name="Test Journal 2",  # Name doesn't match
        journal_issn="1234-5678",
        journal_alternate_issns=None,
    )

    actual = get_journal_score(
        journals=journals,
        journal_scores=scores,
        paper_metadata=metadata,
        use_issn=False,  # Match by name
    )
    assert actual is None


def test_get_journal_score_succeeds_by_issn(journals, scores) -> None:
    journal_id = _write_journal(
        journals,
        name="Test Journal",
        print_issn="1234-5678",
        electronic_issn=None,
    )
    _write_score(
        scores,
        journal_id=journal_id,
        provider=JournalScoreProvider.COMPUTED,
        metadata=mock_computed_score(percentile_rank=10),
    )
    metadata = mock_paper_metadata(
        journal_name="Test Journal 2",  # Name doesn't match
        journal_issn="1234-5678",  # Matches print ISSN
        journal_alternate_issns=None,
    )

    actual = get_journal_score(
        journals=journals,
        journal_scores=scores,
        paper_metadata=metadata,
        use_issn=True,  # Match by ISSN
    )
    assert actual and actual.metadata.computed_score.percentile_rank == 10


def test_get_journal_score_succeeds_by_alt_issn(journals, scores) -> None:
    journal_id = _write_journal(
        journals,
        name="Test Journal",
        print_issn="1234-5678",
        electronic_issn="8765-4321",
    )
    _write_score(
        scores,
        journal_id=journal_id,
        provider=JournalScoreProvider.COMPUTED,
        metadata=mock_computed_score(percentile_rank=10),
    )
    metadata = mock_paper_metadata(
        journal_name="Test Journal 2",  # Name doesn't match
        journal_issn="1111-1111",
        journal_alternate_issns=["8765-4321"],  # Matches electronic ISSN
    )

    actual = get_journal_score(
        journals=journals,
        journal_scores=scores,
        paper_metadata=metadata,
        use_issn=True,  # Match by ISSN
    )
    assert actual and actual.metadata.computed_score.percentile_rank == 10


def test_get_journal_score_succeeds_by_name_fallback(journals, scores) -> None:
    journal_id = _write_journal(
        journals,
        name="Test Journal",
        print_issn="1234-5678",
        electronic_issn=None,
    )
    _write_score(
        scores,
        journal_id=journal_id,
        provider=JournalScoreProvider.COMPUTED,
        metadata=mock_computed_score(percentile_rank=10),
    )
    metadata = mock_paper_metadata(
        journal_name="Test Journal",  # Name matches
        journal_issn="1111-1111",  # ISSN does not match
        journal_alternate_issns=None,
    )

    actual = get_journal_score(
        journals=journals,
        journal_scores=scores,
        paper_metadata=metadata,
        use_issn=True,  # Match by ISSN with name fallback
    )
    assert actual and actual.metadata.computed_score.percentile_rank == 10


def test_get_journal_score_fails_with_issn_and_name_fallback(journals, scores) -> None:
    journal_id = _write_journal(
        journals,
        name="Test Journal",
        print_issn="1234-5678",
        electronic_issn=None,
    )
    _write_score(
        scores,
        journal_id=journal_id,
        provider=JournalScoreProvider.COMPUTED,
        metadata=mock_computed_score(percentile_rank=10),
    )
    metadata = mock_paper_metadata(
        journal_name="Test Journal 2",  # Name doesn't match
        journal_issn="1111-1111",  # ISSN doesn't match
        journal_alternate_issns=None,
    )

    actual = get_journal_score(
        journals=journals,
        journal_scores=scores,
        paper_metadata=metadata,
        use_issn=True,  # Match by ISSN with name fallback
    )
    assert actual is None


def test_get_journal_scimago_quartile_succeeds_by_name(journals, scores) -> None:
    journal_id = _write_journal(
        journals,
        name="Test Journal",
        print_issn=None,
        electronic_issn=None,
    )
    _write_score(
        scores,
        journal_id=journal_id,
        provider=JournalScoreProvider.SCIMAGO,
        metadata=mock_scimago_score(best_quartile=2),
    )
    metadata = mock_paper_metadata(
        journal_name="Test Journal",  # Name matches
        journal_issn=None,
        journal_alternate_issns=None,
    )

    actual = get_journal_scimago_quartile(
        journals=journals,
        journal_scores=scores,
        paper_metadata=metadata,
        use_issn=False,  # Match by name
    )
    assert actual == 2


def test_get_journal_scimago_quartile_fails_by_name(journals, scores) -> None:
    journal_id = _write_journal(
        journals,
        name="Test Journal",
        print_issn="1234-5678",
        electronic_issn=None,
    )
    _write_score(
        scores,
        journal_id=journal_id,
        provider=JournalScoreProvider.SCIMAGO,
        metadata=mock_scimago_score(best_quartile=2),
    )
    metadata = mock_paper_metadata(
        journal_name="Test Journal 2",  # Name doesn't match
        journal_issn="1234-5678",
        journal_alternate_issns=None,
    )

    actual = get_journal_scimago_quartile(
        journals=journals,
        journal_scores=scores,
        paper_metadata=metadata,
        use_issn=False,  # Match by name
    )
    assert actual is None


def test_get_journal_scimago_quartile_succeeds_by_issn(journals, scores) -> None:
    journal_id = _write_journal(
        journals,
        name="Test Journal",
        print_issn="1234-5678",
        electronic_issn=None,
    )
    _write_score(
        scores,
        journal_id=journal_id,
        provider=JournalScoreProvider.SCIMAGO,
        metadata=mock_scimago_score(best_quartile=2),
    )
    metadata = mock_paper_metadata(
        journal_name="Test Journal 2",  # Name doesn't match
        journal_issn="1234-5678",  # Matches print ISSN
        journal_alternate_issns=None,
    )

    actual = get_journal_scimago_quartile(
        journals=journals,
        journal_scores=scores,
        paper_metadata=metadata,
        use_issn=True,  # Match by ISSN
    )
    assert actual == 2


def test_get_journal_scimago_quartile_succeeds_by_alt_issn(journals, scores) -> None:
    journal_id = _write_journal(
        journals,
        name="Test Journal",
        print_issn="1234-5678",
        electronic_issn="8765-4321",
    )
    _write_score(
        scores,
        journal_id=journal_id,
        provider=JournalScoreProvider.SCIMAGO,
        metadata=mock_scimago_score(best_quartile=2),
    )
    metadata = mock_paper_metadata(
        journal_name="Test Journal 2",  # Name doesn't match
        journal_issn="1111-1111",
        journal_alternate_issns=["8765-4321"],  # Matches electronic ISSN
    )

    actual = get_journal_scimago_quartile(
        journals=journals,
        journal_scores=scores,
        paper_metadata=metadata,
        use_issn=True,  # Match by ISSN
    )
    assert actual == 2


def test_get_journal_scimago_quartile_succeeds_by_name_fallback(journals, scores) -> None:
    journal_id = _write_journal(
        journals,
        name="Test Journal",
        print_issn="1234-5678",
        electronic_issn=None,
    )
    _write_score(
        scores,
        journal_id=journal_id,
        provider=JournalScoreProvider.SCIMAGO,
        metadata=mock_scimago_score(best_quartile=2),
    )
    metadata = mock_paper_metadata(
        journal_name="Test Journal",  # Name matches
        journal_issn="1111-1111",  # ISSN doesn't match
        journal_alternate_issns=None,
    )

    actual = get_journal_scimago_quartile(
        journals=journals,
        journal_scores=scores,
        paper_metadata=metadata,
        use_issn=True,  # Match by ISSN with name fallback
    )
    assert actual == 2


def test_get_journal_scimago_quartile_fails_with_issn_and_name_fallback(journals, scores) -> None:
    journal_id = _write_journal(
        journals,
        name="Test Journal",
        print_issn="1234-5678",
        electronic_issn=None,
    )
    _write_score(
        scores,
        journal_id=journal_id,
        provider=JournalScoreProvider.SCIMAGO,
        metadata=mock_scimago_score(best_quartile=2),
    )
    metadata = mock_paper_metadata(
        journal_name="Test Journal 2",  # Name doesn't match
        journal_issn="1111-1111",  # ISSN doesn't match
        journal_alternate_issns=None,
    )

    actual = get_journal_scimago_quartile(
        journals=journals,
        journal_scores=scores,
        paper_metadata=metadata,
        use_issn=True,  # Match by ISSN with name fallback
    )
    assert actual is None
