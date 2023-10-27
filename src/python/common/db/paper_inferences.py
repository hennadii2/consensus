from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional

import psycopg2
from common.db.paper_inferences_util import StudyTypeEnum, inferences_to_study_type
from common.time.convert import TimeUnit, datetime_to_unix
from google.protobuf.json_format import MessageToJson, ParseDict
from paper_inferences_pb2 import InferenceData, PaperInference

PAPER_INFERENCES_TABLE = "paper_inferences"
PAPER_INFERENCES_COLUMN_ID = "id"
PAPER_INFERENCES_COLUMN_PAPER_ID = "paper_id"
PAPER_INFERENCES_COLUMN_TYPE = "type"
PAPER_INFERENCES_COLUMN_PROVIDER = "provider"
PAPER_INFERENCES_COLUMN_SOURCE = "source"
PAPER_INFERENCES_COLUMN_DATA = "data"
PAPER_INFERENCES_COLUMN_CREATED_AT = "created_at"
PAPER_INFERENCES_COLUMN_CREATED_BY = "created_by"


def validate_proto(inference: PaperInference) -> None:
    if not inference.paper_id:
        raise ValueError("Missing paper_id for PaperInference.")
    if not inference.type:
        raise ValueError("Missing type for PaperInference.")
    if not inference.provider:
        raise ValueError("Missing provider for PaperInference.")
    if not inference.source:
        raise ValueError("Missing source for PaperInference.")
    if not inference.created_by:
        raise ValueError("Missing created_by for PaperInference.")
    if not inference.created_at_usec:
        raise ValueError("Missing created_at_usec for PaperInference.")

    if inference.type == PaperInference.Type.STUDY_TYPE:
        if len(inference.data.study_type.values) <= 0:
            raise ValueError("Empty values for study_type.")
        for study_type in inference.data.study_type.values:
            if not study_type.prediction:
                raise ValueError("Missing prediction for study_type.")


def provider_to_name(provider: PaperInference.Provider.V) -> str:
    return str(PaperInference.Provider.DESCRIPTOR.values_by_number[provider].name)


def name_to_provider(name: str) -> Any:
    return PaperInference.Provider.DESCRIPTOR.values_by_name[name].number


def type_to_name(inference_type: PaperInference.Type.V) -> str:
    return str(PaperInference.Type.DESCRIPTOR.values_by_number[inference_type].name)


def name_to_type(name: str) -> Any:
    return PaperInference.Type.DESCRIPTOR.values_by_name[name].number


def get_type_from_data(data: InferenceData) -> PaperInference.Type.V:
    if data.study_type is not None:
        return PaperInference.Type.STUDY_TYPE
    raise NotImplementedError("Failed to get type for inference: unsupported value")


def paper_inferences_row_to_proto(row: Any) -> PaperInference:
    inference = PaperInference()
    inference.id = row[PAPER_INFERENCES_COLUMN_ID]
    inference.paper_id = row[PAPER_INFERENCES_COLUMN_PAPER_ID]
    inference.type = name_to_type(row[PAPER_INFERENCES_COLUMN_TYPE])
    inference.provider = name_to_provider(row[PAPER_INFERENCES_COLUMN_PROVIDER])
    inference.source = row[PAPER_INFERENCES_COLUMN_SOURCE]
    inference.data.CopyFrom(ParseDict(row[PAPER_INFERENCES_COLUMN_DATA], InferenceData()))
    inference.created_by = row[PAPER_INFERENCES_COLUMN_CREATED_BY]
    inference.created_at_usec = datetime_to_unix(
        row[PAPER_INFERENCES_COLUMN_CREATED_AT], TimeUnit.MICROSECONDS
    )
    validate_proto(inference)
    return inference


class PaperInferences:
    """
    Interface class for reading/writing paper inferences stored in a DB.
    """

    def __init__(self, connection: psycopg2.extensions.connection):
        self.connection = connection

    def write(
        self,
        paper_id: int,
        provider: PaperInference.Provider.V,
        inference_data: InferenceData,
        source: str,
        job_name: str,
        timestamp: datetime,
        commit: bool,
    ) -> PaperInference:
        """
        Writes a paper inference to the database.

        Raises:
            ValueError: if inference with the same source already exists
        """

        if not timestamp:
            timestamp = datetime.now(timezone.utc)

        inference = PaperInference()
        inference.paper_id = paper_id
        inference.type = get_type_from_data(inference_data)
        inference.provider = provider
        inference.source = source
        inference.data.CopyFrom(inference_data)
        inference.created_by = job_name
        inference.created_at_usec = datetime_to_unix(timestamp, TimeUnit.MICROSECONDS)

        validate_proto(inference)

        sql = f"""
         INSERT INTO {PAPER_INFERENCES_TABLE} (
           {PAPER_INFERENCES_COLUMN_PAPER_ID},
           {PAPER_INFERENCES_COLUMN_TYPE},
           {PAPER_INFERENCES_COLUMN_PROVIDER},
           {PAPER_INFERENCES_COLUMN_SOURCE},
           {PAPER_INFERENCES_COLUMN_DATA},
           {PAPER_INFERENCES_COLUMN_CREATED_AT},
           {PAPER_INFERENCES_COLUMN_CREATED_BY}
         ) VALUES (
           %(paper_id)s,
           %(type_str)s,
           %(provider_str)s,
           %(source)s,
           %(data)s,
           %(created_at)s,
           %(created_by)s
         )
         RETURNING {PAPER_INFERENCES_COLUMN_ID}
        """
        data = {
            "paper_id": inference.paper_id,
            "type_str": type_to_name(inference.type),
            "provider_str": provider_to_name(inference.provider),
            "source": inference.source,
            "data": MessageToJson(inference.data, preserving_proto_field_name=True),
            "created_at": timestamp,
            "created_by": job_name,
        }

        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            inference.id = cursor.fetchone()[PAPER_INFERENCES_COLUMN_ID]

        if commit:
            self.connection.commit()

        return inference

    def get_inferences(
        self,
        paper_id: int,
        inference_type: PaperInference.Type.V,
    ) -> list[PaperInference]:
        """
        Returns latest inferences from all providers for a paper.
        """

        sql = f"""
          SELECT p.*
          FROM {PAPER_INFERENCES_TABLE} p
          INNER JOIN (
            SELECT
              {PAPER_INFERENCES_COLUMN_PAPER_ID} as grouped_paper_id,
              {PAPER_INFERENCES_COLUMN_PROVIDER} as grouped_provider,
              {PAPER_INFERENCES_COLUMN_TYPE} as grouped_type,
              MAX({PAPER_INFERENCES_COLUMN_CREATED_AT}) as max_created_at
            FROM {PAPER_INFERENCES_TABLE}
            WHERE {PAPER_INFERENCES_COLUMN_PAPER_ID} = %(paper_id)s
              AND {PAPER_INFERENCES_COLUMN_TYPE} = %(type)s
            GROUP BY
              {PAPER_INFERENCES_COLUMN_PAPER_ID},
              {PAPER_INFERENCES_COLUMN_PROVIDER},
              {PAPER_INFERENCES_COLUMN_TYPE}
          ) groupedp
          ON p.{PAPER_INFERENCES_COLUMN_PAPER_ID} = groupedp.grouped_paper_id
          AND p.{PAPER_INFERENCES_COLUMN_PROVIDER} = groupedp.grouped_provider
          AND p.{PAPER_INFERENCES_COLUMN_TYPE} = groupedp.grouped_type
          AND p.{PAPER_INFERENCES_COLUMN_CREATED_AT} = groupedp.max_created_at
          ORDER BY {PAPER_INFERENCES_COLUMN_PROVIDER}
        """
        data = {
            "paper_id": paper_id,
            "type": type_to_name(inference_type),
        }

        inferences: list[PaperInference] = []
        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            results = cursor.fetchall()
            for row in results:
                inference = paper_inferences_row_to_proto(row)
                inferences.append(inference)

        return inferences

    def get_study_type(
        self,
        paper_id: int,
        provider_metadata: Optional[str] = None,
    ) -> Optional[StudyTypeEnum]:
        inferences = self.get_inferences(
            paper_id=paper_id,
            inference_type=PaperInference.Type.STUDY_TYPE,
        )
        # S2 study types are not yet in the inferences table (need to make a view)
        # so parse them from provider_metadata directly if passed in.
        if provider_metadata:
            metadata = json.loads(provider_metadata)
            if "publicationtypes" in metadata:
                publication_types = metadata["publicationtypes"]
                if isinstance(publication_types, list) and len(publication_types):
                    inference = PaperInference()
                    inference.type = PaperInference.Type.STUDY_TYPE
                    inference.provider = PaperInference.Provider.SEMANTIC_SCHOLAR
                    for publication_type in publication_types:
                        study_type = inference.data.study_type.values.add()
                        study_type.prediction = publication_type
                    inferences.append(inference)

        return inferences_to_study_type(inferences)
