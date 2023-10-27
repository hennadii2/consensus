import json
from typing import Any, Optional

import pyarrow  # type: ignore
from common.beam.records.base_record import BaseFeatureRecord, BaseFeatureRecordParquetSchemaFields
from google.protobuf.json_format import MessageToJson, ParseDict
from paper_metadata_pb2 import PaperMetadata
from pydantic import BaseModel, validator


class ProviderId(BaseModel):
    item: str


class ProviderIdList(BaseModel):
    list: list[ProviderId]


def encode_metadata(data: PaperMetadata) -> str:
    return MessageToJson(data, preserving_proto_field_name=True, indent=None)


def encode_provider_id_list(data: ProviderIdList) -> list[str]:
    return [x.item for x in data.list]


class PaperFeatureRecord(BaseFeatureRecord):
    paper_id: str
    old_paper_id: Optional[str]
    provider_ids: ProviderIdList
    abstract: Optional[str]
    metadata: Optional[PaperMetadata]
    abstract_last_updated_at_iso: str
    metadata_last_updated_at_iso: str

    class Config:
        json_encoders = {
            PaperMetadata: encode_metadata,
            ProviderIdList: encode_provider_id_list,
        }

    @validator("metadata", pre=True)
    def validate_metadata(cls, v: Any) -> Optional[PaperMetadata]:
        if isinstance(v, str):
            return ParseDict(json.loads(v), PaperMetadata())
        elif isinstance(v, PaperMetadata):
            return v
        raise ValueError(f"Must be a paper metadata message or str, not {type(v)}")

    @validator("provider_ids", pre=True)
    def validate_provider_ids(cls, v: Any) -> ProviderIdList:
        if isinstance(v, dict):
            return ProviderIdList(**v)
        else:
            return ProviderIdList(list=[ProviderId(item=x) for x in v])


PaperFeatureRecordParquetSchema = pyarrow.schema(
    [
        ("paper_id", pyarrow.string()),
        ("old_paper_id", pyarrow.string()),
        ("provider_ids", pyarrow.list_(pyarrow.string())),
        ("abstract", pyarrow.string()),
        ("metadata", pyarrow.string()),
        ("abstract_last_updated_at_iso", pyarrow.string()),
        ("metadata_last_updated_at_iso", pyarrow.string()),
    ]
    + BaseFeatureRecordParquetSchemaFields
)
