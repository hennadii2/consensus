import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterator, Optional

import apache_beam as beam  # type: ignore
import pandas as pd
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

COLUMN_JOURNAL = "journal"
COLUMN_PRINT_ISSN = "print_issn"
COLUMN_ELECTRONIC_ISSN = "electronic_issn"
COLUMN_AVG_SCISCORE = "avg_sciscore"
COLUMN_YEAR = "year"
COLUMN_PERCENTILE_RANK = "percentile_rank"
SCISCORE_SELECTED_ROW_SCHEMA = {
    "journal": COLUMN_JOURNAL,
    "Print-ISSN": COLUMN_PRINT_ISSN,
    "E-ISSN": COLUMN_ELECTRONIC_ISSN,
    "avg (sciscore)": COLUMN_AVG_SCISCORE,
    "pub_year": COLUMN_YEAR,
}


@dataclass(frozen=True)
class SciScoreData:
    journal_name: str
    print_issn: Optional[str]
    electronic_issn: Optional[str]
    average: float
    percentile_rank: float
    year: int


def sciscore_row_to_dataclass_tuple(df_row: Any) -> tuple[str, SciScoreData]:
    """
    Converts sciscore raw row data to dataclasses with validation.
    """
    journal = df_row.journal
    print_issn = df_row.print_issn
    electronic_issn = df_row.electronic_issn
    avg_sciscore = df_row.avg_sciscore
    year = df_row.year
    percentile_rank = round(df_row.percentile_rank, 4)

    if print_issn and not ISSN_REGEX_MATCH.match(print_issn):
        logging.error(f"Set unexpected print issn to None: {print_issn}")
        print_issn = None

    if electronic_issn and not ISSN_REGEX_MATCH.match(electronic_issn):
        logging.error(f"Set unexpected electronic issn to None: {electronic_issn}")
        electronic_issn = None

    key = f"{journal}-{print_issn}-{electronic_issn}"
    sci_score_data = SciScoreData(
        journal_name=journal,
        print_issn=print_issn,
        electronic_issn=electronic_issn,
        average=avg_sciscore,
        percentile_rank=percentile_rank,
        year=year,
    )
    return (key, sci_score_data)


@dataclass(frozen=True)
class WriteScoresAndJournalsToDbResult(PipelineResult):
    journal: str
    num_scores: int
    dry_run: bool


class WriteScoresAndJournalsToDb(beam.DoFn):
    """
    Beam DoFn to write journals and sci score data to the DB.
    """

    # Number of records to write to DB in one commit
    MAX_COMMIT_BATCH_COUNT = 10

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

    def process(self, record: Any) -> Iterator[WriteScoresAndJournalsToDbResult]:
        key, score_with_key_tuples = record
        scores = [score_tuple[1] for score_tuple in score_with_key_tuples]

        try:
            if not len(scores):
                raise ValueError(f"Empty scores list for journal: {key}")

            journal_name = scores[0].journal_name
            print_issn = scores[0].print_issn
            electronic_issn = scores[0].electronic_issn

            if not journal_name:
                raise ValueError(f"Missing name for journal data: {key}")

            # First add journal if it doesn't exist yet
            journal = Journal()
            if not self.dry_run:
                journal = self.journals_db.read_by_name(journal_name=journal_name)
                if not journal:
                    journal = self.journals_db.write_journal(
                        name=journal_name,
                        print_issn=print_issn,
                        electronic_issn=electronic_issn,
                        job_name=self.job_name,
                    )

            # Then add all score data
            for sciscore_data in scores:
                metadata = JournalScoreMetadata()
                metadata.sci_score.raw_data_url = self.raw_data_url
                metadata.sci_score.avg_score = sciscore_data.average
                metadata.sci_score.percentile_rank = sciscore_data.percentile_rank
                if not self.dry_run:
                    self.journal_scores_db.write_score(
                        journal_id=journal.id,
                        year=sciscore_data.year,
                        provider=JournalScoreProvider.SCI_SCORE,
                        metadata=metadata,
                        job_name=self.job_name,
                        timestamp=self.timestamp,
                    )

            if not self.dry_run:
                self.commit_batch_count += 1
                if self.commit_batch_count >= self.MAX_COMMIT_BATCH_COUNT:
                    self.db.commit()
                    self.commit_batch_count = 0

            yield WriteScoresAndJournalsToDbResult(
                journal=key,
                num_scores=len(scores),
                dry_run=self.dry_run,
                success=True,
                message=None,
            )
        except Exception as e:
            yield WriteScoresAndJournalsToDbResult(
                journal=key,
                num_scores=len(scores),
                dry_run=self.dry_run,
                success=False,
                message=str(e),
            )


def run_ingest_sciscore_pipeline(
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

    # Read sciscore data into memory, data is not too large
    sciscore_df = pd.read_excel(filepath=input_path)

    # Select only columns we'll use, and rename so we don't hit errors in beam
    # due to spaces / malformed column names
    sciscore_df = sciscore_df[list(SCISCORE_SELECTED_ROW_SCHEMA.keys())]
    sciscore_df.rename(columns=SCISCORE_SELECTED_ROW_SCHEMA, inplace=True)

    # Add percentile rank to dataframe
    sciscore_df[COLUMN_PERCENTILE_RANK] = sciscore_df[COLUMN_AVG_SCISCORE].rank(pct=True)

    with beam.Pipeline(options=pipeline_options) as p:
        pcollection = to_pcollection(sciscore_df, pipeline=p)
        results = (
            pcollection
            | "ConvertToDataclass" >> beam.Map(sciscore_row_to_dataclass_tuple)
            | "GroupByJournalName" >> beam.GroupBy(lambda x: x[0])
            | "WriteToDb"
            >> beam.ParDo(
                WriteScoresAndJournalsToDb(
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
