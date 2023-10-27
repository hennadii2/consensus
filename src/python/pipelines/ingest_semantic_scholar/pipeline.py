import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterator, Optional

import apache_beam as beam  # type: ignore
import apache_beam.io.textio as textio  # type: ignore
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions  # type: ignore
from common.beam.pipeline_config import PipelineConfig
from common.beam.pipeline_result import PipelineResult, write_pipeline_results
from common.config.secret_manager import SecretId
from common.db.connect import DbEnv, MainDbClient
from common.db.papers import Papers
from common.ingestion.extract import extract_metadata_and_abstract, filter_metadata_for_ingestion
from common.storage.connect import StorageClient, StorageEnv
from common.storage.paper_data import write_clean_abstract
from paper_metadata_pb2 import PaperProvider


@dataclass(frozen=True)
class S2PairedData:
    metadata: list[str]
    abstract: list[str]


def get_latest_abstract(abstracts: list[str]) -> Optional[dict]:
    """
    Returns the S2 abstract with the latest update date paired with its json.
    """
    if len(abstracts) <= 0:
        return None

    loaded_abstract = json.loads(abstracts[0])
    for i in range(1, len(abstracts)):
        next_abstract = json.loads(abstracts[i])
        if next_abstract["updated"] > loaded_abstract["updated"]:
            loaded_abstract = next_abstract
    return dict(loaded_abstract)


@dataclass(frozen=True)
class IngestS2DataResult(PipelineResult):
    paper_id: str
    updated_existing_paper: Optional[bool]
    data: S2PairedData
    dry_run: bool


class IngestS2Data(beam.DoFn):
    """
    Beam DoFn to extract paper metadata from raw provider records
    and write the metadata to the DB.
    """

    # Number of records to write to DB in one commit
    MAX_COMMIT_BATCH_COUNT = 1500

    def __init__(
        self,
        dry_run: bool,
        db_env: DbEnv,
        job_name: str,
        project_id: str,
        timestamp: datetime,
        raw_data_url: str,
        storage_env: StorageEnv,
        update_metadata: bool,
        update_abstract: bool,
    ):
        self.dry_run = dry_run
        self.db_env = db_env
        self.job_name = job_name
        self.project_id = project_id
        self.timestamp = timestamp
        self.raw_data_url = raw_data_url
        self.storage_env = storage_env
        self.update_metadata = update_metadata
        self.update_abstract = update_abstract

    def setup(self):
        # Add project ID to worker environment to allow connection to
        # secret manager
        os.environ[SecretId.GCLOUD_PROJECT_ID.name] = self.project_id
        connection = MainDbClient(self.db_env)
        self.db = Papers(connection)
        self.commit_batch_count = 0
        self.storage_client = StorageClient(self.storage_env)

    def finish_bundle(self):
        if not self.dry_run:
            self.db.connection.commit()

    def teardown(self):
        if not self.dry_run:
            self.db.connection.close()

    def process(self, record: Any) -> Iterator[IngestS2DataResult]:
        corpus_id, paired_data = record
        data = S2PairedData(**paired_data)
        updated_existing_paper = None
        wrote_abstract = False

        if len(data.metadata) != 1:
            yield IngestS2DataResult(
                paper_id=corpus_id,
                updated_existing_paper=updated_existing_paper,
                data=data,
                dry_run=self.dry_run,
                success=False,
                message=f"""Bad pairing lengths:
                metadata {len(data.metadata)} abstract {len(data.abstract)}""",
            )
            return

        try:
            s2_metadata = json.loads(data.metadata[0])
            loaded_json_abstract_or_none = get_latest_abstract(data.abstract)
            s2_metadata["added_abstract"] = loaded_json_abstract_or_none
            metadata, abstract = extract_metadata_and_abstract(
                PaperProvider.SEMANTIC_SCHOLAR,
                json.dumps(s2_metadata),
                try_old_formats=False,
            )
            s2_metadata.pop("added_abstract")

            # Skip saving invalid metadata to the database
            filter_metadata_for_ingestion(metadata)

            if not self.dry_run:
                # Semantic scholar changed their primary keys for the papers
                # in their dataset. Originally the key was a hash, but they
                # introduced corpusid. So first, lookup if the hash ID'd paper
                # exists in our DB. If it's already been converted we will
                # update it in write_paper().
                old_provider_id = metadata.provider_url.split("/")[-1]
                paper = self.db.read_by_provider_id(
                    provider=PaperProvider.SEMANTIC_SCHOLAR,
                    provider_id=old_provider_id,
                )

                if paper is None:
                    paper = self.db.write_paper(
                        job_name=self.job_name,
                        raw_data_url=self.raw_data_url,
                        metadata=metadata,
                        provider_metadata=s2_metadata,
                        timestamp=self.timestamp,
                        commit=False,
                        update_if_exists=True,
                    )
                elif self.update_metadata:
                    paper = self.db.update_metadata(
                        job_name=self.job_name,
                        paper_id=paper.id,
                        raw_data_url=self.raw_data_url,
                        metadata=metadata,
                        provider_metadata=s2_metadata,
                        timestamp=self.timestamp,
                        commit=False,
                    )
                updated_existing_paper = paper.created_at_usec != paper.last_updated_at_usec

                if self.update_abstract and abstract is not None:
                    wrote_abstract = True
                    clean_data_url = write_clean_abstract(
                        client=self.storage_client,
                        clean_abstract=abstract,
                        paper=paper,
                        timestamp=self.timestamp,
                    )
                    self.db.update_clean_data_url(
                        paper_id=paper.id,
                        clean_data_url=clean_data_url,
                        abstract=abstract,
                        job_name=self.job_name,
                        timestamp=self.timestamp,
                        commit=False,
                    )

                self.commit_batch_count += 1
                if self.commit_batch_count >= self.MAX_COMMIT_BATCH_COUNT:
                    self.db.connection.commit()
                    self.commit_batch_count = 0

            message = (
                f"Updated metadata: {updated_existing_paper} Wrote abstract: {wrote_abstract}"
            )
            yield IngestS2DataResult(
                paper_id=corpus_id,
                updated_existing_paper=updated_existing_paper,
                data=data,
                dry_run=self.dry_run,
                success=True,
                message=message,
            )
        except Exception as e:
            yield IngestS2DataResult(
                paper_id=corpus_id,
                updated_existing_paper=updated_existing_paper,
                data=data,
                dry_run=self.dry_run,
                success=False,
                message=str(e),
            )


def run_pipeline(
    runner: str,
    project_id: str,
    beam_args: Any,
    config: PipelineConfig,
    dry_run: bool,
    db_env: DbEnv,
    storage_env: StorageEnv,
    input_dir: str,
    update_metadata: bool,
    update_abstract: bool,
) -> None:
    pipeline_options = PipelineOptions(
        beam_args,
        runner=runner,
        job_name=config.job_name,
        temp_location=config.temp_dir,
        max_num_workers=config.max_num_workers,
    )
    pipeline_options.view_as(SetupOptions).save_main_session = True

    if not update_metadata and not update_abstract:
        raise ValueError("At least one of [update_metadata, update_abstract] must be selected.")

    with beam.Pipeline(options=pipeline_options) as p:
        metadata_dir = f"{input_dir}/papers/*.gz"
        abstracts_dir = f"{input_dir}/abstracts/*.gz"

        metadata_pairs = (
            p
            | "ReadMetadataFilesByLine" >> textio.ReadFromText(metadata_dir)
            | "ConvertMetadataToPair" >> beam.Map(lambda x: (json.loads(x)["corpusid"], x))
        )

        abstract_pairs = (
            p
            | "ReadAbstractFilesByLine" >> textio.ReadFromText(abstracts_dir)
            | "ConvertAbstractToPair" >> beam.Map(lambda x: (json.loads(x)["corpusid"], x))
        )

        results = (
            (
                {
                    "metadata": metadata_pairs,
                    "abstract": abstract_pairs,
                }
            )
            | "GroupPairsByCleanDataUrl" >> beam.CoGroupByKey()
            | "IngestS2DataAndWriteToDb"
            >> beam.ParDo(
                IngestS2Data(
                    dry_run=dry_run,
                    db_env=db_env,
                    job_name=config.job_name,
                    project_id=project_id,
                    timestamp=config.timestamp,
                    raw_data_url=input_dir,
                    storage_env=storage_env,
                    update_metadata=update_metadata,
                    update_abstract=update_abstract,
                )
            )
        )

        noisy_msg = "Bad pairing lengths:\n                metadata 1 abstract 0"
        write_pipeline_results(
            config.results_file,
            results,
            custom_filter_for_individual_results=(lambda x: x.message != noisy_msg),
        )
