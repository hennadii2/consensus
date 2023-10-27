from typing import Optional

import apache_beam as beam  # type: ignore
import pyarrow  # type: ignore
from common.beam.model_outputs import MIN_CLAIM_PROBABILITY
from common.beam.records.base_record import (
    BaseFeatureRecord,
    BaseFeatureRecordParquetSchemaFields,
    RecordStatus,
)


class ClaimFeatureRecord(BaseFeatureRecord):
    paper_id: str
    sentence_id: int
    sentence: str
    claim_probability: float
    modified_claim: str
    modified_flag: int
    claim_hash: str
    enhanced_claim: Optional[str]


ClaimFeatureRecordParquetSchema = pyarrow.schema(
    [
        ("paper_id", pyarrow.string()),
        ("sentence_id", pyarrow.int16()),
        ("sentence", pyarrow.string()),
        ("claim_probability", pyarrow.float32()),
        ("modified_claim", pyarrow.string()),
        ("modified_flag", pyarrow.int8()),
        ("claim_hash", pyarrow.string()),
        ("enhanced_claim", pyarrow.string()),
    ]
    + BaseFeatureRecordParquetSchemaFields
)


def read_qualifying_claims_from_parquet(
    p: beam.Pipeline,
    input_patterns: list[str],
) -> beam.PCollection[ClaimFeatureRecord]:
    """
    Helper function to read claim features from parquet into a data model.
    """
    records = (
        p
        | "ListClaimFeatureRecords" >> beam.Create(input_patterns)
        | "ReadFeatures" >> beam.io.parquetio.ReadAllFromParquet()
        | "ConvertToModel" >> beam.Map(lambda x: ClaimFeatureRecord(**x))
        | "FilterActive" >> beam.Filter(lambda x: x.status == RecordStatus.ACTIVE)
        | "FilterLowProbabilityClaims"
        >> beam.Filter(lambda x: x.claim_probability >= MIN_CLAIM_PROBABILITY)
    )
    return records
