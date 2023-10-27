import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterator, List, Optional

import apache_beam as beam  # type: ignore
import pandas as pd
from apache_beam import metrics
from apache_beam.dataframe.convert import to_pcollection  # type: ignore
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions  # type: ignore
from common.beam.pipeline_config import PipelineConfig
from common.beam.pipeline_result import PipelineResult, write_pipeline_results
from common.config.secret_manager import SecretId
from common.db.connect import DbEnv, MainDbClient
from common.db.journal_scores import JournalScores
from common.db.journals import Journals
from journal_pb2 import Journal, JournalScoreMetadata, JournalScoreProvider

ISSN_REGEX_MATCH = re.compile("^[0-9]{4}-[0-9]{3}([0-9]|X)$")
SJR_BEST_QUARTILE_REGEX_MATCH = re.compile("^Q[1-4]$")
SJR_TYPE_JOURNAL = "journal"

COLUMN_JOURNAL = "journal"
COLUMN_ISSN = "issn"
COLUMN_TYPE = "type"
COLUMN_SJR_BEST_QUARTILE = "sjr_best_quartile"
COLUMN_YEAR = "year"
# Maps the column names from the scimago csv to the column names we want to use.
SCIMAGO_SELECTED_ROW_SCHEMA = {
    "Title": COLUMN_JOURNAL,
    "Issn": COLUMN_ISSN,
    "Type": COLUMN_TYPE,
    "SJR Best Quartile": COLUMN_SJR_BEST_QUARTILE,
}


@dataclass(frozen=True)
class ScimagoData:
    journal_name: str
    issn_list: List[str]
    sjr_best_quartile: int
    type: str
    year: int


def scimago_row_to_dataclass_tuple(df_row: Any) -> Optional[tuple[str, ScimagoData]]:
    """
    Converts scimago row data to dataclasses with validation.
    """
    journal = df_row.journal
    issn_list = df_row.issn
    sjr_best_quartile_list = df_row.sjr_best_quartile
    type = df_row.type
    year = df_row.year

    metrics.Metrics.counter("ingest_scimago/convert", "total_records").inc()

    # Drop missing quartile values, as we don't need to store them in the search index
    int_quartiles = [
        int(q_str[1])
        for q_str in sjr_best_quartile_list
        if SJR_BEST_QUARTILE_REGEX_MATCH.match(q_str)
    ]
    if not len(int_quartiles):
        metrics.Metrics.counter("ingest_scimago/convert", "missing_best_quartile").inc()
        return None
    best_quartile = min(int_quartiles)

    matched_issns = [issn for issn in issn_list if ISSN_REGEX_MATCH.match(issn)]
    if not len(matched_issns):
        metrics.Metrics.counter("ingest_scimago/convert", "no_valid_issns").inc()
        logging.error(f"No valid issns found: {issn_list}")
        return None

    key = f"{journal}-{'-'.join(matched_issns)}"
    scimago_data = ScimagoData(
        journal_name=journal,
        issn_list=matched_issns,
        sjr_best_quartile=best_quartile,
        type=type,
        year=year,
    )
    return (key, scimago_data)


@dataclass(frozen=True)
class WriteBestQuartilesToDbResult(PipelineResult):
    journal: str
    best_quartile: int
    dry_run: bool


class WriteBestQuartilesToDb(beam.DoFn):
    """
    Beam DoFn to write journals and scimago data to the DB.
    """

    def __init__(
        self,
        dry_run: bool,
        db_env: DbEnv,
        job_name: str,
        raw_data_url: str,
        timestamp: datetime,
        project_id: str,
    ):
        self.dry_run = dry_run
        self.db_env = db_env
        self.job_name = job_name
        self.raw_data_url = raw_data_url
        self.timestamp = timestamp
        self.project_id = project_id

    def setup(self):
        # Add project ID to worker environment to allow connection to
        # secret manager
        os.environ[SecretId.GCLOUD_PROJECT_ID.name] = self.project_id

        if not self.dry_run:
            self.db = MainDbClient(self.db_env)
            self.journals_db = Journals(self.db)
            self.journal_scores_db = JournalScores(self.db)
            self.commit_batch_count = 0

    def finish_bundle(self):
        if not self.dry_run:
            self.db.commit()

    def teardown(self):
        if not self.dry_run:
            self.db.close()

    def process(self, record: Any) -> Iterator[WriteBestQuartilesToDbResult]:
        key, scimago_record = record

        metrics.Metrics.counter("ingest_scimago/write", "total_records").inc()

        try:
            journal_name = scimago_record.journal_name
            issn_list = scimago_record.issn_list
            best_quartile = scimago_record.sjr_best_quartile
            year = scimago_record.year

            # Read journal from DB
            journal = Journal()
            if not self.dry_run:
                journal = self.journals.read_by_issn_with_name_fallback(
                    issn_list=issn_list, name=journal_name
                )
                # TODO(cvarano): differentiate between print/electronic issns from SJR data
                if not journal:
                    journal = self.journals_db.write_journal(
                        name=journal_name,
                        print_issn=None,
                        electronic_issn=None,
                        job_name=self.job_name,
                    )
                    metrics.Metrics.counter("ingest_scimago/write", "create_new_journal").inc()

            # Add Scimago data to journal scores
            metadata = JournalScoreMetadata()
            metadata.scimago.raw_data_url = self.raw_data_url
            metadata.scimago.best_quartile = best_quartile
            if not self.dry_run:
                self.journal_scores_db.write_score(
                    journal_id=journal.id,
                    year=year,
                    provider=JournalScoreProvider.SCIMAGO,
                    metadata=metadata,
                    job_name=self.job_name,
                    timestamp=self.timestamp,
                )

            yield WriteBestQuartilesToDbResult(
                journal=key,
                best_quartile=best_quartile,
                dry_run=self.dry_run,
                success=True,
                message=None,
            )
        except Exception as e:
            yield WriteBestQuartilesToDbResult(
                journal=key,
                best_quartile=best_quartile,
                dry_run=self.dry_run,
                success=False,
                message=str(e),
            )


def prepare_scimago_data(df, year):
    df = df.copy()
    # Select only columns we'll use, and rename so we don't hit errors in beam
    # due to spaces / malformed column names
    df = df[list(SCIMAGO_SELECTED_ROW_SCHEMA.keys())]
    df.rename(columns=SCIMAGO_SELECTED_ROW_SCHEMA, inplace=True)
    # Split comma-separated issns into separate rows
    df[COLUMN_ISSN] = df[COLUMN_ISSN].str.split(", ")
    df = df.explode(COLUMN_ISSN).reset_index(drop=True)
    # Add hyphen to match existing issn format
    df[COLUMN_ISSN] = df[COLUMN_ISSN].apply(lambda x: x[:4] + "-" + x[4:])
    # dedupe journal names
    df = df.groupby(COLUMN_JOURNAL, as_index=False).agg(
        {
            COLUMN_ISSN: list,
            COLUMN_SJR_BEST_QUARTILE: list,
            COLUMN_TYPE: "first",  # TODO: assumes all rows for a journal have the same type
        }
    )
    df[COLUMN_YEAR] = year

    return df


def run_ingest_scimago_pipeline(
    runner: str,
    project_id: str,
    beam_args: Any,
    config: PipelineConfig,
    dry_run: bool,
    db_env: DbEnv,
    input_path: str,
) -> None:
    pipeline_options = PipelineOptions(
        beam_args,
        runner=runner,
        job_name=config.job_name,
        temp_location=config.temp_dir,
        max_num_workers=config.max_num_workers,
    )
    pipeline_options.view_as(SetupOptions).save_main_session = True

    # Read scimago data into memory, data is not too large
    scimago_df = pd.read_csv(input_path, delimiter=";")
    scimago_df = prepare_scimago_data(scimago_df, year=2021)  # TODO: add year programatically

    with beam.Pipeline(options=pipeline_options) as p:
        pcollection = to_pcollection(scimago_df, pipeline=p)
        results = (
            pcollection
            | "ConvertToDataclass" >> beam.Map(scimago_row_to_dataclass_tuple)
            | "FilterInvalid" >> beam.Filter(lambda x: x is not None)
            | "FilterJournals" >> beam.Filter(lambda x: x[1].type == SJR_TYPE_JOURNAL)
            | "WriteBestQuartilesToDb"
            >> beam.ParDo(
                WriteBestQuartilesToDb(
                    dry_run=dry_run,
                    db_env=db_env,
                    job_name=config.job_name,
                    raw_data_url=input_path,
                    timestamp=config.timestamp,
                    project_id=project_id,
                )
            )
        )

        write_pipeline_results(config.results_file, results)
