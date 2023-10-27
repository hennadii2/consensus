from typing import Any, Optional

import apache_beam as beam  # type: ignore
from common.beam.model_outputs import MIN_CLAIM_PROBABILITY
from common.beam.records.base_record import RecordStatus
from common.beam.records.paper_feature_record import PaperFeatureRecord
from common.ingestion.extract import filter_metadata_for_ingestion, filter_metadata_for_product
from common.search.document_types import (
    ControlledStudyKeywordEnum,
    HumanStudyKeywordEnum,
    StudyTypeKeywordEnum,
)
from pydantic import validator


class FullMergedFeatureRecord(PaperFeatureRecord):
    claim_id: str
    claim_probability: float
    title: str
    sentence: str
    modified_claim: str
    enhanced_claim: Optional[str]
    sentence_id: int
    claim_embeddings: list[float]
    title_embeddings: list[float]
    study_type_prediction: StudyTypeKeywordEnum
    study_type_max_probability: Optional[float]
    BiomedPlus: Optional[bool]
    controlled_study_prediction: Optional[ControlledStudyKeywordEnum]
    human_classifier_prediction: Optional[HumanStudyKeywordEnum]
    sample_size_prediction: Optional[int]
    study_count_prediction: Optional[int]
    review_rct_classifier_prediction: Optional[bool]

    @validator("study_type_prediction", pre=True)
    def validate_study_type_prediction(cls, v: Any) -> StudyTypeKeywordEnum:
        return StudyTypeKeywordEnum(v)

    @validator("BiomedPlus", pre=True)
    def validate_biomed_plus(cls, v: Any) -> Optional[bool]:
        if v is None:
            return None
        if isinstance(v, str):
            if v == "Yes":
                return True
            if v == "No":
                return False
        raise ValueError(f"expected 'Yes' or 'No', not {v}")

    @validator("controlled_study_prediction", pre=True)
    def validate_controlled_study_prediction(cls, v: Any) -> Optional[ControlledStudyKeywordEnum]:
        if v is None:
            return None
        return ControlledStudyKeywordEnum(v)

    @validator("human_classifier_prediction", pre=True)
    def validate_human_classifier_prediction(cls, v: Any) -> Optional[HumanStudyKeywordEnum]:
        if v is None:
            return None
        return HumanStudyKeywordEnum(v)

    @validator("review_rct_classifier_prediction", pre=True)
    def validate_review_rct_classifier_prediction(cls, v: Any) -> Optional[bool]:
        if v is None:
            return None
        if isinstance(v, str):
            if v == "yes":
                return True
            if v == "no":
                return False
        raise ValueError(f"expected 'yes' or 'no', not {v}")


def _convert_to_model_or_none(data: Any) -> Optional[FullMergedFeatureRecord]:
    try:
        record = FullMergedFeatureRecord(**data)
        if record.metadata is None:
            raise ValueError("missing_metadata")
        filter_metadata_for_product(record.metadata)
        filter_metadata_for_ingestion(record.metadata)
        return record
    except Exception as e:
        beam.metrics.Metrics.counter(
            "read_qualifying_merged_feature_records_from_parquet/convert_to_model", str(e)
        ).inc()
        return None


def read_qualifying_merged_feature_records_from_parquet(
    p: beam.Pipeline,
    input_patterns: list[str],
) -> beam.PCollection[FullMergedFeatureRecord]:
    """
    Helper function to read claim features from parquet into a data model.
    """
    records = (
        p
        | "ListFullMergedFeatureRecords" >> beam.Create(input_patterns)
        | "ReadFeatures" >> beam.io.parquetio.ReadAllFromParquet()
        | "ConvertToModel" >> beam.Map(_convert_to_model_or_none)
        | "FilterFailedVaildation" >> beam.Filter(lambda x: x is not None)
        | "FilterActive" >> beam.Filter(lambda x: x.status == RecordStatus.ACTIVE)
        | "FilterLowProbabilityClaims"
        >> beam.Filter(lambda x: x.claim_probability >= MIN_CLAIM_PROBABILITY)
    )
    return records
