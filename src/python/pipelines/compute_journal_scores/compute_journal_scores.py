import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterator, Optional

import apache_beam as beam  # type: ignore
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions  # type: ignore
from common.beam.pipeline_config import PipelineConfig
from common.beam.pipeline_result import PipelineResult, write_pipeline_results
from common.config.secret_manager import SecretId
from common.db.connect import DbEnv, MainDbClient
from common.db.journal_scores import JournalScores
from common.db.journals import Journals
from journal_pb2 import Journal, JournalScore, JournalScoreMetadata, JournalScoreProvider

MIN_SCORE_YEAR = 1900
MAX_SCORE_YEAR = datetime.now(timezone.utc).year


@dataclass(frozen=True)
class JournalAndYear:
    journal: Journal
    year: int


class ReadJournalsAndYear(beam.DoFn):
    """
    DoFn to read all DB rows in the journals table.
    """

    def __init__(self, db_env: DbEnv, project_id: str):
        self.db_env = db_env
        self.project_id = project_id

    def setup(self):
        # Set GCLOUD_PROJECT_ID in worker to enable access to secret manager
        os.environ[SecretId.GCLOUD_PROJECT_ID.name] = self.project_id

        connection = MainDbClient(self.db_env)
        self.db = Journals(connection)

    def teardown(self):
        self.db.connection.close()

    def process(self, p) -> Iterator[JournalAndYear]:
        for journal in self.db.read_all():
            for year in range(MIN_SCORE_YEAR, MAX_SCORE_YEAR + 1):
                yield JournalAndYear(journal=journal, year=year)


def read_journals_and_year(
    p: beam.Pipeline, db_env: DbEnv, project_id: str
) -> beam.PCollection[JournalAndYear]:
    """
    Helper function to read all journals from the DB using a workaround instead
    of jdbc, which is not currently working (TODO: meganvw).
    """
    journal_protos = (
        p
        | "Workaround" >> beam.Create([""])
        | "ReadJournalsAndYear"
        >> beam.ParDo(
            ReadJournalsAndYear(
                db_env=db_env,
                project_id=project_id,
            )
        )
        | "ReshuffleForFanout" >> beam.transforms.util.Reshuffle()
    )
    return journal_protos


@dataclass(frozen=True)
class WriteComputedScoresToDbResult(PipelineResult):
    journal: JournalAndYear
    score: Optional[JournalScoreMetadata]
    dry_run: bool


class WriteComputedScoresToDb(beam.DoFn):
    """
    Beam DoFn to write computed journal scores to the DB.
    """

    # Number of records to write to DB in one commit
    MAX_COMMIT_BATCH_COUNT = 10

    def __init__(
        self,
        dry_run: bool,
        db_env: DbEnv,
        job_name: str,
        timestamp: datetime,
        project_id: str,
    ):
        self.dry_run = dry_run
        self.db_env = db_env
        self.job_name = job_name
        self.timestamp = timestamp
        self.project_id = project_id

    def setup(self):
        # Add project ID to worker environment to allow connection to
        # secret manager
        os.environ[SecretId.GCLOUD_PROJECT_ID.name] = self.project_id

        self.db = MainDbClient(self.db_env)
        self.journals_db = Journals(self.db)
        self.journal_scores_db = JournalScores(self.db)
        self.commit_batch_count = 0

    def finish_bundle(self):
        if not self.dry_run:
            self.db.commit()

    def teardown(self):
        self.db.close()

    def _get_closest_sci_score(self, record: JournalAndYear) -> Optional[JournalScore]:
        # Get all sci_score values for the journal within 5 years
        scores: list[JournalScore] = self.journal_scores_db.get_scores(
            journal_id=record.journal.id,
            year=record.year,
            provider=JournalScoreProvider.SCI_SCORE,
            year_bound=5,
        )

        # If there are no scores within 5 years, keep blank
        if not len(scores):
            return None

        # If an exact year match exists, return it
        for score in scores:
            if score.year == record.year:
                return score

        # If year is before 1997 and did not have an exact match, keep blank
        if record.year < 1997:
            return None

        # Otherwise, return the most recent score year
        return scores[-1]

    def process(self, record: JournalAndYear) -> Iterator[WriteComputedScoresToDbResult]:
        metadata = None
        try:
            score = self._get_closest_sci_score(record)
            if not score:
                return

            metadata = JournalScoreMetadata()
            metadata.computed_score.percentile_rank = score.metadata.sci_score.percentile_rank
            if not self.dry_run:
                self.journal_scores_db.write_score(
                    journal_id=record.journal.id,
                    year=record.year,
                    provider=JournalScoreProvider.COMPUTED,
                    metadata=metadata,
                    job_name=self.job_name,
                    timestamp=self.timestamp,
                )

                self.commit_batch_count += 1
                if self.commit_batch_count >= self.MAX_COMMIT_BATCH_COUNT:
                    self.db.commit()
                    self.commit_batch_count = 0

            yield WriteComputedScoresToDbResult(
                journal=record,
                score=metadata,
                dry_run=self.dry_run,
                success=True,
                message=None,
            )
        except Exception as e:
            yield WriteComputedScoresToDbResult(
                journal=record,
                score=metadata,
                dry_run=self.dry_run,
                success=False,
                message=str(e),
            )


def run_compute_journal_scores_pipeline(
    runner: str,
    project_id: str,
    beam_args: Any,
    config: PipelineConfig,
    dry_run: bool,
    db_env: DbEnv,
) -> None:
    pipeline_options = PipelineOptions(
        beam_args,
        runner=runner,
        job_name=config.job_name,
        temp_location=config.temp_dir,
        max_num_workers=config.max_num_workers,
    )
    pipeline_options.view_as(SetupOptions).save_main_session = True

    with beam.Pipeline(options=pipeline_options) as p:
        journals_and_year = read_journals_and_year(p, db_env=db_env, project_id=project_id)

        results = journals_and_year | "WriteComputedScoreToDb" >> beam.ParDo(
            WriteComputedScoresToDb(
                dry_run=dry_run,
                db_env=db_env,
                job_name=config.job_name,
                timestamp=config.timestamp,
                project_id=project_id,
            )
        )

        write_pipeline_results(config.results_file, results)
