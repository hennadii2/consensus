from typing import Optional

from common.search.document_types import HumanStudyKeywordEnum, StudyTypeKeywordEnum
from journal_pb2 import JournalScore
from paper_metadata_pb2 import PaperMetadata
from pydantic import BaseModel

MIN_VERY_RIGOROUS_JOURNAL_RANK_PERCENTILE = 0.9
MIN_RIGOROUS_JOURNAL_RANK_PERCENTILE = 0.5
MIN_HIGHLY_CITED_PAPER_COUNT = 70
ALLOWED_STUDY_TYPES = [
    StudyTypeKeywordEnum.CASE_STUDY,
    StudyTypeKeywordEnum.RCT,
    StudyTypeKeywordEnum.SYSTEMATIC_REVIEW,
    StudyTypeKeywordEnum.META_ANALYSIS,
    StudyTypeKeywordEnum.LITERATURE_REVIEW,
    StudyTypeKeywordEnum.NON_RCT_EXPERIMENTAL,
    StudyTypeKeywordEnum.NON_RCT_OBSERVATIONAL_STUDY,
    StudyTypeKeywordEnum.NON_RCT_IN_VITRO,
]


class DisputedBadge(BaseModel):
    reason: str
    url: str


class Badges(BaseModel):
    very_rigorous_journal: bool
    rigorous_journal: bool
    highly_cited_paper: bool
    study_type: Optional[StudyTypeKeywordEnum]
    sample_size: Optional[int]
    study_count: Optional[int]
    animal_trial: Optional[bool]
    large_human_trial: Optional[bool]
    disputed: Optional[DisputedBadge]
    enhanced: Optional[bool] = False  # TODO(cvarano): remove after claim search deprecation


def _is_animal_trial(
    study_type: StudyTypeKeywordEnum,
    population_type: Optional[HumanStudyKeywordEnum],
) -> bool:
    if (
        study_type == StudyTypeKeywordEnum.RCT
        or study_type == StudyTypeKeywordEnum.NON_RCT_EXPERIMENTAL
    ):
        return population_type == HumanStudyKeywordEnum.ANIMAL
    return False


def _is_large_human_trial(
    study_type: StudyTypeKeywordEnum,
    population_type: Optional[HumanStudyKeywordEnum],
    sample_size: Optional[int],
) -> bool:
    if (
        study_type == StudyTypeKeywordEnum.RCT
        or study_type == StudyTypeKeywordEnum.NON_RCT_EXPERIMENTAL
    ):
        if sample_size and sample_size >= 300:
            return population_type == HumanStudyKeywordEnum.HUMAN
    return False


def get_badges(
    paper_id: str,
    journal_score: Optional[JournalScore],
    paper_metadata: PaperMetadata,
    study_type: Optional[StudyTypeKeywordEnum],
    population_type: Optional[HumanStudyKeywordEnum],
    sample_size: Optional[int],
    study_count: Optional[int],
    disputed_badges: dict[str, DisputedBadge],
    is_enhanced: bool,
) -> Badges:
    """
    Returns a set of binary badges to be displayed by the frontend
    if the paper or it's journal meet certain criteria.
    """
    badges = Badges(
        very_rigorous_journal=False,
        rigorous_journal=False,
        highly_cited_paper=False,
        study_type=None,
        sample_size=None,
        study_count=None,
        animal_trial=None,
        large_human_trial=None,
        disputed=None,
        enhanced=is_enhanced,
    )

    # Check "rigorous journal" criteria
    if journal_score:
        percentile_rank = round(journal_score.metadata.computed_score.percentile_rank, 4)
        if percentile_rank >= MIN_VERY_RIGOROUS_JOURNAL_RANK_PERCENTILE:
            badges.very_rigorous_journal = True
        elif percentile_rank >= MIN_RIGOROUS_JOURNAL_RANK_PERCENTILE:
            badges.rigorous_journal = True

    # Check "highly cited paper" criteria
    if paper_metadata.citation_count >= MIN_HIGHLY_CITED_PAPER_COUNT:
        badges.highly_cited_paper = True

    # Create study type badge
    if study_type in ALLOWED_STUDY_TYPES:
        badges.study_type = study_type
        badges.animal_trial = _is_animal_trial(study_type, population_type)
        badges.large_human_trial = _is_large_human_trial(
            study_type,
            population_type,
            sample_size=sample_size,
        )

    # Either one or the other will be set, dependent on study type
    if sample_size:
        badges.sample_size = sample_size
    elif study_count:
        badges.study_count = study_count

    if paper_id in disputed_badges:
        badges.disputed = disputed_badges[paper_id]

    return badges


def get_primary_author(authors: list[str]) -> str:
    """Returns the primary author of a paper or an empty string."""
    return authors[0] if len(authors) else ""
