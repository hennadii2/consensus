from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Optional

import psycopg2
from common.time.convert import TimeUnit, datetime_to_unix
from google.protobuf.json_format import MessageToJson, ParseDict
from journal_pb2 import JournalScore, JournalScoreMetadata, JournalScoreProvider
from loguru import logger

JOURNAL_SCORES_TABLE = "journal_scores"
JOURNAL_SCORES_COLUMN_ID = "id"
JOURNAL_SCORES_COLUMN_JOURNAL_ID = "journal_id"
JOURNAL_SCORES_COLUMN_YEAR = "year"
JOURNAL_SCORES_COLUMN_PROVIDER = "provider"
JOURNAL_SCORES_COLUMN_METADATA = "metadata"
JOURNAL_SCORES_COLUMN_CREATED_AT = "created_at"
JOURNAL_SCORES_COLUMN_CREATED_BY = "created_by"

YEAR_REGEX_MATCH = re.compile("^(1|2)[0-9]{3}$")


def validate_score(score: JournalScore) -> None:
    if not score.journal_id:
        raise ValueError("Missing journal_id for JournalScore.")

    if not score.year:
        raise ValueError("Missing year for JournalScore.")

    if not YEAR_REGEX_MATCH.match(str(score.year)):
        raise ValueError(f"Invalid year: {score.year}")

    if score.provider == JournalScoreProvider.COMPUTED:
        if not score.metadata.computed_score:
            raise ValueError("JournalScoreMetadata is missing computed_score")
    elif score.provider == JournalScoreProvider.SCI_SCORE:
        if not score.metadata.sci_score.raw_data_url:
            raise ValueError("JournalScoreMetadata is missing sci_score.raw_data_url")
        if score.metadata.sci_score.avg_score <= 0:
            raise ValueError("JournalScoreMetadata is missing sci_score.avg_score")
    elif score.provider == JournalScoreProvider.SCIMAGO:
        if not score.metadata.scimago.raw_data_url:
            raise ValueError("JournalScoreMetadata is missing scimago.raw_data_url")
        best_quartile = score.metadata.scimago.best_quartile
        if best_quartile < 0 or best_quartile > 4:
            raise ValueError(
                f"JournalScoreMetadata scimago.best_quartile value is invalid: {best_quartile}"
            )
    else:
        raise NotImplementedError(f"validate_score not implemented for provider: {score.provider}")


def provider_to_name(provider: JournalScoreProvider.V) -> str:
    return str(JournalScoreProvider.DESCRIPTOR.values_by_number[provider].name)


def name_to_provider(name: str) -> Any:
    return JournalScoreProvider.DESCRIPTOR.values_by_name[name].number


def journal_scores_row_to_proto(row: Any) -> JournalScore:
    score = JournalScore()
    score.id = row[JOURNAL_SCORES_COLUMN_ID]
    score.journal_id = row[JOURNAL_SCORES_COLUMN_JOURNAL_ID]
    score.year = row[JOURNAL_SCORES_COLUMN_YEAR]
    score.provider = name_to_provider(row[JOURNAL_SCORES_COLUMN_PROVIDER])
    score.metadata.CopyFrom(ParseDict(row[JOURNAL_SCORES_COLUMN_METADATA], JournalScoreMetadata()))
    score.created_by = row[JOURNAL_SCORES_COLUMN_CREATED_BY]
    score.created_at_usec = datetime_to_unix(
        row[JOURNAL_SCORES_COLUMN_CREATED_AT], TimeUnit.MICROSECONDS
    )
    validate_score(score)
    return score


class JournalScores:
    """
    Interface class for reading/writing journal scores stored in a DB.
    """

    def __init__(self, connection: psycopg2.extensions.connection):
        self.connection = connection

    def write_score(
        self,
        journal_id: int,
        year: int,
        provider: JournalScoreProvider.V,
        metadata: JournalScoreMetadata,
        job_name: str,
        timestamp: Optional[datetime] = None,
        commit=False,
    ) -> JournalScore:
        """
        Writes a journal score to the database.

        Raises:
            ValueError: if journal with the same
        """

        if not timestamp:
            timestamp = datetime.now(timezone.utc)

        score = JournalScore()
        score.journal_id = journal_id
        score.year = year
        score.provider = provider
        score.metadata.CopyFrom(metadata)
        score.created_by = job_name
        score.created_at_usec = datetime_to_unix(timestamp, TimeUnit.MICROSECONDS)

        validate_score(score)

        sql = f"""
         INSERT INTO {JOURNAL_SCORES_TABLE} (
           {JOURNAL_SCORES_COLUMN_JOURNAL_ID},
           {JOURNAL_SCORES_COLUMN_YEAR},
           {JOURNAL_SCORES_COLUMN_PROVIDER},
           {JOURNAL_SCORES_COLUMN_METADATA},
           {JOURNAL_SCORES_COLUMN_CREATED_AT},
           {JOURNAL_SCORES_COLUMN_CREATED_BY}
         ) VALUES (
           %(journal_id)s,
           %(year)s,
           %(provider_str)s,
           %(metadata_json)s,
           %(created_at)s,
           %(created_by)s
         )
         RETURNING {JOURNAL_SCORES_COLUMN_ID}
        """
        data = {
            "journal_id": score.journal_id,
            "year": score.year,
            "provider_str": provider_to_name(score.provider),
            "metadata_json": MessageToJson(score.metadata, preserving_proto_field_name=True),
            "created_at": timestamp,
            "created_by": job_name,
        }

        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            score.id = cursor.fetchone()[JOURNAL_SCORES_COLUMN_ID]

        if commit:
            self.connection.commit()

        return score

    def get_scores(
        self,
        journal_id: int,
        year: int,
        provider: JournalScoreProvider.V,
        year_bound: int,
    ) -> list[JournalScore]:
        """
        Returns all scores for a journal available within +/- year_bound of
        the given year. If there is more then one entry for a provider for a
        given year, the score with the latest CREATED_AT date is selected. This
        is to support multiple ingestions and computiations of scores.
        """

        sql = f"""
          SELECT * FROM {JOURNAL_SCORES_TABLE}
            WHERE {JOURNAL_SCORES_COLUMN_JOURNAL_ID} = %(journal_id)s
              AND {JOURNAL_SCORES_COLUMN_PROVIDER} = %(provider)s
              AND {JOURNAL_SCORES_COLUMN_YEAR} BETWEEN %(low_year)s AND %(high_year)s
            ORDER BY {JOURNAL_SCORES_COLUMN_YEAR}, {JOURNAL_SCORES_COLUMN_CREATED_AT}
        """
        data = {
            "journal_id": journal_id,
            "provider": provider_to_name(provider),
            "low_year": year - year_bound,
            "high_year": year + year_bound,
        }

        scores: list[JournalScore] = []
        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            results = cursor.fetchall()
            for row in results:
                score = journal_scores_row_to_proto(row)
                if len(scores) and scores[-1].year == score.year:
                    scores[-1] = score
                else:
                    scores.append(score)

        return scores

    def _get_latest_score(
        self,
        journal_id: int,
        provider: JournalScoreProvider.V,
    ) -> Optional[JournalScore]:
        """
        Returns the latest score for a journal by update timestamp and year.
        """

        sql = f"""
          SELECT * FROM {JOURNAL_SCORES_TABLE}
            WHERE {JOURNAL_SCORES_COLUMN_JOURNAL_ID} = %(journal_id)s
              AND {JOURNAL_SCORES_COLUMN_PROVIDER} = %(provider)s
            ORDER BY {JOURNAL_SCORES_COLUMN_YEAR} DESC, {JOURNAL_SCORES_COLUMN_CREATED_AT} DESC
        """
        data = {
            "journal_id": journal_id,
            "provider": provider_to_name(provider),
        }

        with self.connection.cursor() as cursor:
            cursor.execute(sql, data)
            results = cursor.fetchall()
            if len(results) == 0:
                return None
            return journal_scores_row_to_proto(results[0])

    def get_score(
        self,
        journal_id: int,
        year: int,
        provider: JournalScoreProvider.V,
    ) -> Optional[JournalScore]:
        scores = self.get_scores(
            journal_id=journal_id,
            year=year,
            provider=provider,
            year_bound=0,
        )
        return scores[0] if len(scores) else None

    def get_computed_score(
        self,
        journal_id: int,
        year: int,
    ) -> Optional[JournalScore]:
        return self.get_score(
            journal_id=journal_id,
            year=year,
            provider=JournalScoreProvider.COMPUTED,
        )

    def get_latest_scimago_quartile(
        self,
        journal_id: int,
    ) -> Optional[int]:
        scimago_score = self._get_latest_score(
            journal_id=journal_id,
            provider=JournalScoreProvider.SCIMAGO,
        )
        if scimago_score is None:
            return None
        else:
            if not scimago_score.metadata.scimago.best_quartile:
                logger.error(f"Missing valid scimago best quartile for {journal_id}")
                return None
            return scimago_score.metadata.scimago.best_quartile
