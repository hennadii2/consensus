from typing import Optional

from common.search.document_types import HumanStudyKeywordEnum, StudyTypeKeywordEnum
from journal_pb2 import JournalScore
from paper_metadata_pb2 import PaperMetadata
from web.backend.app.common.badges import Badges, get_badges


def test_get_badges_succeeds() -> None:
    paper_metadata = PaperMetadata()
    journal_score = JournalScore()

    paper_metadata.citation_count = 0
    journal_score.metadata.computed_score.percentile_rank = 0
    actual = get_badges(
        paper_id="1",
        journal_score=journal_score,
        paper_metadata=paper_metadata,
        study_type=None,
        sample_size=None,
        study_count=None,
        population_type=None,
        disputed_badges={},
        is_enhanced=False,
    )
    assert actual == Badges(
        very_rigorous_journal=False,
        rigorous_journal=False,
        highly_cited_paper=False,
        study_type=None,
        sample_size=None,
        study_count=None,
        animal_trial=None,
        large_human_trial=None,
        disputed=None,
        enhanced=False,
    )

    paper_metadata.citation_count = 70
    journal_score.metadata.computed_score.percentile_rank = 0
    actual = get_badges(
        paper_id="1",
        journal_score=journal_score,
        paper_metadata=paper_metadata,
        study_type=None,
        sample_size=None,
        study_count=None,
        population_type=None,
        disputed_badges={},
        is_enhanced=False,
    )
    assert actual == Badges(
        very_rigorous_journal=False,
        rigorous_journal=False,
        highly_cited_paper=True,
        study_type=None,
        sample_size=None,
        study_count=None,
        animal_trial=None,
        large_human_trial=None,
        disputed=None,
        enhanced=False,
    )

    paper_metadata.citation_count = 0
    journal_score.metadata.computed_score.percentile_rank = 0.5
    actual = get_badges(
        paper_id="1",
        journal_score=journal_score,
        paper_metadata=paper_metadata,
        study_type=None,
        sample_size=None,
        study_count=None,
        population_type=None,
        disputed_badges={},
        is_enhanced=False,
    )
    assert actual == Badges(
        very_rigorous_journal=False,
        rigorous_journal=True,
        highly_cited_paper=False,
        study_type=None,
        sample_size=None,
        study_count=None,
        animal_trial=None,
        large_human_trial=None,
        disputed=None,
        enhanced=False,
    )

    paper_metadata.citation_count = 0
    journal_score.metadata.computed_score.percentile_rank = 0.9
    actual = get_badges(
        paper_id="1",
        journal_score=journal_score,
        paper_metadata=paper_metadata,
        study_type=None,
        sample_size=None,
        study_count=None,
        population_type=None,
        disputed_badges={},
        is_enhanced=False,
    )
    assert actual == Badges(
        very_rigorous_journal=True,
        rigorous_journal=False,
        highly_cited_paper=False,
        study_type=None,
        sample_size=None,
        study_count=None,
        animal_trial=None,
        large_human_trial=None,
        disputed=None,
        enhanced=False,
    )

    paper_metadata.citation_count = 90
    journal_score.metadata.computed_score.percentile_rank = 0.9
    actual = get_badges(
        paper_id="1",
        journal_score=journal_score,
        paper_metadata=paper_metadata,
        study_type=None,
        sample_size=None,
        study_count=None,
        population_type=None,
        disputed_badges={},
        is_enhanced=False,
    )
    assert actual == Badges(
        very_rigorous_journal=True,
        rigorous_journal=False,
        highly_cited_paper=True,
        study_type=None,
        sample_size=None,
        study_count=None,
        animal_trial=None,
        large_human_trial=None,
        disputed=None,
        enhanced=False,
    )


def test_get_badges_with_study_type_succeeds() -> None:
    paper_metadata = PaperMetadata()
    journal_score = JournalScore()

    paper_metadata.citation_count = 0
    journal_score.metadata.computed_score.percentile_rank = 0
    actual = get_badges(
        paper_id="1",
        journal_score=journal_score,
        paper_metadata=paper_metadata,
        study_type=None,
        sample_size=None,
        study_count=None,
        population_type=None,
        disputed_badges={},
        is_enhanced=False,
    )
    assert actual == Badges(
        very_rigorous_journal=False,
        rigorous_journal=False,
        highly_cited_paper=False,
        study_type=None,
        sample_size=None,
        study_count=None,
        animal_trial=None,
        large_human_trial=None,
        disputed=None,
        enhanced=False,
    )

    actual = get_badges(
        paper_id="1",
        journal_score=journal_score,
        paper_metadata=paper_metadata,
        study_type=StudyTypeKeywordEnum.CASE_STUDY,
        sample_size=None,
        study_count=None,
        population_type=None,
        disputed_badges={},
        is_enhanced=False,
    )
    assert actual == Badges(
        very_rigorous_journal=False,
        rigorous_journal=False,
        highly_cited_paper=False,
        study_type=StudyTypeKeywordEnum.CASE_STUDY,
        sample_size=None,
        study_count=None,
        animal_trial=False,
        large_human_trial=False,
        disputed=None,
        enhanced=False,
    )

    actual = get_badges(
        paper_id="1",
        journal_score=journal_score,
        paper_metadata=paper_metadata,
        study_type=StudyTypeKeywordEnum.META_ANALYSIS,
        sample_size=None,
        study_count=None,
        population_type=None,
        disputed_badges={},
        is_enhanced=False,
    )
    assert actual == Badges(
        very_rigorous_journal=False,
        rigorous_journal=False,
        highly_cited_paper=False,
        study_type=StudyTypeKeywordEnum.META_ANALYSIS,
        sample_size=None,
        study_count=None,
        animal_trial=False,
        large_human_trial=False,
        disputed=None,
        enhanced=False,
    )

    actual = get_badges(
        paper_id="1",
        journal_score=journal_score,
        paper_metadata=paper_metadata,
        study_type=StudyTypeKeywordEnum.RCT,
        sample_size=None,
        study_count=None,
        population_type=None,
        disputed_badges={},
        is_enhanced=False,
    )
    assert actual == Badges(
        very_rigorous_journal=False,
        rigorous_journal=False,
        highly_cited_paper=False,
        study_type=StudyTypeKeywordEnum.RCT,
        sample_size=None,
        study_count=None,
        animal_trial=False,
        large_human_trial=False,
        disputed=None,
        enhanced=False,
    )

    actual = get_badges(
        paper_id="1",
        journal_score=journal_score,
        paper_metadata=paper_metadata,
        study_type=StudyTypeKeywordEnum.SYSTEMATIC_REVIEW,
        sample_size=None,
        study_count=None,
        population_type=None,
        disputed_badges={},
        is_enhanced=False,
    )
    assert actual == Badges(
        very_rigorous_journal=False,
        rigorous_journal=False,
        highly_cited_paper=False,
        study_type=StudyTypeKeywordEnum.SYSTEMATIC_REVIEW,
        sample_size=None,
        study_count=None,
        animal_trial=False,
        large_human_trial=False,
        disputed=None,
        enhanced=False,
    )


def test_animal_trial() -> None:
    paper_metadata = PaperMetadata()
    journal_score = JournalScore()

    def _get_badges(
        study_type: StudyTypeKeywordEnum,
        population_type: HumanStudyKeywordEnum,
    ) -> Badges:
        return get_badges(
            paper_id="1",
            journal_score=journal_score,
            paper_metadata=paper_metadata,
            study_type=study_type,
            sample_size=None,
            study_count=None,
            population_type=population_type,
            disputed_badges={},
            is_enhanced=False,
        )

    actual = _get_badges(
        study_type=StudyTypeKeywordEnum.RCT,
        population_type=HumanStudyKeywordEnum.ANIMAL,
    )
    assert actual.animal_trial is True

    actual = _get_badges(
        study_type=StudyTypeKeywordEnum.NON_RCT_EXPERIMENTAL,
        population_type=HumanStudyKeywordEnum.ANIMAL,
    )
    assert actual.animal_trial is True

    actual = _get_badges(
        study_type=StudyTypeKeywordEnum.NON_RCT_EXPERIMENTAL,
        population_type=HumanStudyKeywordEnum.HUMAN,
    )
    assert actual.animal_trial is False

    actual = _get_badges(
        study_type=StudyTypeKeywordEnum.NON_RCT_OTHER,
        population_type=HumanStudyKeywordEnum.ANIMAL,
    )
    assert actual.animal_trial is None


def test_large_human_trial() -> None:
    paper_metadata = PaperMetadata()
    journal_score = JournalScore()

    def _get_badges(
        study_type: StudyTypeKeywordEnum,
        sample_size: int,
        population_type: HumanStudyKeywordEnum,
    ) -> Badges:
        return get_badges(
            paper_id="1",
            journal_score=journal_score,
            paper_metadata=paper_metadata,
            study_type=study_type,
            sample_size=sample_size,
            study_count=None,
            population_type=population_type,
            disputed_badges={},
            is_enhanced=False,
        )

    actual = _get_badges(
        study_type=StudyTypeKeywordEnum.RCT,
        sample_size=300,
        population_type=HumanStudyKeywordEnum.HUMAN,
    )
    assert actual.large_human_trial is True

    actual = _get_badges(
        study_type=StudyTypeKeywordEnum.NON_RCT_EXPERIMENTAL,
        sample_size=300,
        population_type=HumanStudyKeywordEnum.HUMAN,
    )
    assert actual.large_human_trial is True

    actual = _get_badges(
        study_type=StudyTypeKeywordEnum.NON_RCT_EXPERIMENTAL,
        sample_size=299,
        population_type=HumanStudyKeywordEnum.HUMAN,
    )
    assert actual.large_human_trial is False

    actual = _get_badges(
        study_type=StudyTypeKeywordEnum.NON_RCT_EXPERIMENTAL,
        sample_size=300,
        population_type=HumanStudyKeywordEnum.ANIMAL,
    )
    assert actual.large_human_trial is False

    actual = _get_badges(
        study_type=StudyTypeKeywordEnum.NON_RCT_OTHER,
        sample_size=300,
        population_type=HumanStudyKeywordEnum.HUMAN,
    )
    assert actual.large_human_trial is None


def test_study_size() -> None:
    paper_metadata = PaperMetadata()
    journal_score = JournalScore()

    def _get_badges(
        study_count: Optional[int],
        sample_size: Optional[int],
    ) -> Badges:
        return get_badges(
            paper_id="1",
            journal_score=journal_score,
            paper_metadata=paper_metadata,
            study_type=None,
            sample_size=sample_size,
            study_count=study_count,
            population_type=None,
            disputed_badges={},
            is_enhanced=False,
        )

    actual = _get_badges(
        sample_size=None,
        study_count=None,
    )
    assert actual.sample_size is None
    assert actual.study_count is None

    actual = _get_badges(
        sample_size=300,
        study_count=None,
    )
    assert actual.sample_size == 300
    assert actual.study_count is None

    actual = _get_badges(
        sample_size=None,
        study_count=150,
    )
    assert actual.sample_size is None
    assert actual.study_count == 150

    # This state should not happen, validated during ingestion
    actual = _get_badges(
        sample_size=300,
        study_count=150,
    )
    assert actual.sample_size == 300
    assert actual.study_count is None
