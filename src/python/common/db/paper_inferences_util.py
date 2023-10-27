from __future__ import annotations

from enum import Enum
from typing import Optional

from paper_inferences_pb2 import PaperInference, StudyType


class StudyTypeEnum(Enum):
    META_ANALYSIS = "Meta Analysis"
    RCT_STUDY = "RCT"
    NON_RCT_STUDY = "Non-RCT"
    CASE_REPORT = "Case Report"
    SYSTEMATIC_REVIEW = "Systematic Review"
    OTHER = "Other"


def _parse_s2_study_type(inference: StudyType) -> Optional[StudyTypeEnum]:
    def to_enum(value: str) -> Optional[StudyTypeEnum]:
        if value == "Review":
            return StudyTypeEnum.SYSTEMATIC_REVIEW
        elif value == "CaseReport":
            return StudyTypeEnum.CASE_REPORT
        elif value == "MetaAnalysis":
            return StudyTypeEnum.META_ANALYSIS

        other_types = ["LettersAndComments", "Editorial", "Conference", "News", "Dataset", "Book"]
        if value in other_types:
            return StudyTypeEnum.OTHER

        none_types = ["JournalArticle", "Study", "ClinicalTrial"]
        if value in none_types:
            return None

        raise NotImplementedError(f"Failed to parse s2 study type: unknown {value}")

    s2_study_types = [to_enum(x.prediction) for x in inference.values]
    s2_study_types = list(filter(lambda x: x is not None, s2_study_types))
    if len(s2_study_types) == 1:
        return s2_study_types[0]
    elif len(s2_study_types) == 2:
        if StudyTypeEnum.CASE_REPORT in s2_study_types and StudyTypeEnum.OTHER in s2_study_types:
            return StudyTypeEnum.CASE_REPORT
        elif StudyTypeEnum.OTHER in s2_study_types:
            return StudyTypeEnum.OTHER
        elif StudyTypeEnum.META_ANALYSIS in s2_study_types:
            return StudyTypeEnum.META_ANALYSIS
        elif StudyTypeEnum.SYSTEMATIC_REVIEW in s2_study_types:
            return StudyTypeEnum.SYSTEMATIC_REVIEW
    elif len(s2_study_types) == 3:
        if (
            StudyTypeEnum.SYSTEMATIC_REVIEW in s2_study_types
            and StudyTypeEnum.META_ANALYSIS in s2_study_types
            and StudyTypeEnum.CASE_REPORT in s2_study_types
        ):
            return StudyTypeEnum.META_ANALYSIS

    return None


def _parse_consensus_study_type(inference: StudyType) -> Optional[StudyTypeEnum]:
    def to_enum(value: str) -> Optional[StudyTypeEnum]:
        if value == "RCT Study":
            return StudyTypeEnum.RCT_STUDY
        elif value == "Non-RCT Study":
            return StudyTypeEnum.NON_RCT_STUDY
        elif value == "Meta Analysis":
            return StudyTypeEnum.META_ANALYSIS
        elif value == "Case Report":
            return StudyTypeEnum.CASE_REPORT
        elif value == "Other":
            return StudyTypeEnum.OTHER
        elif value == "Systematic Review":
            return StudyTypeEnum.SYSTEMATIC_REVIEW
        elif value == "None":
            return None
        raise NotImplementedError(f"Failed to parse consensus study type: unknown {value}")

    return to_enum(inference.values[0].prediction) if len(inference.values) == 1 else None


def inferences_to_study_type(inferences: list[PaperInference]) -> Optional[StudyTypeEnum]:
    s2_study_type = None
    consensus_study_type = None
    for inference in inferences:
        if not inference.data.study_type:
            continue
        if inference.provider == PaperInference.Provider.CONSENSUS:
            consensus_study_type = _parse_consensus_study_type(inference.data.study_type)
        elif inference.provider == PaperInference.Provider.SEMANTIC_SCHOLAR:
            s2_study_type = _parse_s2_study_type(inference.data.study_type)

    return consensus_study_type if s2_study_type is None else s2_study_type
