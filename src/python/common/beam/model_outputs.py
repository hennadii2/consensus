import logging
from dataclasses import dataclass
from typing import Any, List, Optional

import apache_beam as beam  # type: ignore
import apache_beam.io.parquetio as parquetio  # type: ignore

# Minimum probability for accepting a claim into the product search index
MIN_CLAIM_PROBABILITY = 0.5
REQUIRED_COLUMNS = [
    "paper_id",
    "claim_probability",
    "sentence",
    "modified_claim",
]


@dataclass(frozen=True)
class ModelOutput:
    paper_id: int
    sentence: str
    modified_claim: str
    claim_probability: float
    sentence_id: Optional[int] = None
    dataset_id: Optional[str] = None
    clean_data_url: Optional[str] = None


def _parquet_record_to_dataclass(record: Any) -> ModelOutput:
    if "modified_claim" not in record:
        record["modified_claim"] = record["sentence"]
    return ModelOutput(**record)


def read_qualifying_model_outputs_from_parquet(
    p: beam.Pipeline,
    input_file_pattern: str,
    columns: Optional[List[str]] = None,
) -> beam.PCollection[ModelOutput]:
    """
    Helper function to read model output from parquet into a dataclass.
    """
    if columns is not None:
        for col in REQUIRED_COLUMNS:
            if col not in columns:
                columns.append(col)
                logging.warning(f"adding required column {col} to parquet read operation")
    model_outputs = (
        p
        | "ReadFilesByLine" >> parquetio.ReadFromParquet(input_file_pattern, columns=columns)
        | "ConvertToDataclass" >> beam.Map(_parquet_record_to_dataclass)
        | "FilterLowProbabilityClaims"
        >> beam.Filter(lambda x: x.claim_probability >= MIN_CLAIM_PROBABILITY)
    )
    return model_outputs
