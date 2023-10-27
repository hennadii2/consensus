import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterator
from xml.etree import ElementTree as etree

import apache_beam as beam  # type: ignore
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions  # type: ignore
from common.beam.claims import ClaimWithCountId, read_claims_with_count_id_from_parquet
from common.beam.pipeline_config import PipelineConfig
from common.beam.pipeline_result import PipelineResult, write_pipeline_results
from common.config.constants import PROD_URL, PROD_URL_WORDPRESS_SITEMAP
from common.config.secret_manager import SecretId
from common.db.connect import DbEnv
from common.search.claim_index import ClaimIndex
from common.search.connect import ElasticClient, SearchEnv
from common.storage.connect import StorageEnv, init_storage_client
from common.storage.datasets import search_index_id_without_run_timestamp
from common.storage.sitemaps import write_sitemap
from pipelines.sitemap.util import (
    SitemapEntry,
    build_sitemap_from_entries,
    generate_sitemap_entries,
    get_sitemap_distribution_hierarchy,
)

MAX_ITEMS_PER_SITEMAP = 10000


@dataclass(frozen=True)
class WriteSitemapResult(PipelineResult):
    sitemap: str
    num_entries: int
    dry_run: bool


class WriteSitemap(beam.DoFn):
    """
    Writes all entries for a single sitemap to blob store.
    """

    def __init__(
        self,
        dry_run: bool,
        storage_env: StorageEnv,
        project_id: str,
        timestamp: datetime,
        search_index_id: str,
    ):
        self.dry_run = dry_run
        self.storage_env = storage_env
        self.project_id = project_id
        self.timestamp = timestamp
        self.search_index_id = search_index_id

    def setup(self):
        # Set GCLOUD_PROJECT_ID in worker to enable access to secret manager
        os.environ[SecretId.GCLOUD_PROJECT_ID.name] = self.project_id

        self.storage_client = init_storage_client(self.storage_env)

    def process(self, record: Any) -> Iterator[WriteSitemapResult]:
        sitemap_name, entries = record

        num_entries = 0
        is_sitemap_index = False
        for entry in entries:
            num_entries += 1
            is_sitemap_index = entry.is_sitemap_index

        try:
            if not num_entries:
                raise ValueError("Empty sitemap.")

            root = build_sitemap_from_entries(
                sitemap_name=sitemap_name,
                entries=entries,
                timestamp=self.timestamp,
                is_sitemap_index=is_sitemap_index,
                add_to_root_entry=[PROD_URL_WORDPRESS_SITEMAP],
            )
            tree = etree.ElementTree(root)

            filename = os.path.join(tempfile.gettempdir(), sitemap_name)
            if not self.dry_run:
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                tree.write(filename, encoding="UTF-8")
                base_id = search_index_id_without_run_timestamp(self.search_index_id)
                filename = write_sitemap(
                    client=self.storage_client,
                    search_index_id=base_id,
                    sitemap_path=sitemap_name,
                    filename=filename,
                )

            yield WriteSitemapResult(
                sitemap=filename,
                num_entries=num_entries,
                dry_run=self.dry_run,
                success=True,
                message=None,
            )
        except Exception as e:
            yield WriteSitemapResult(
                sitemap=sitemap_name,
                num_entries=num_entries,
                dry_run=self.dry_run,
                success=False,
                message=str(e),
            )


class GenerateSitemapEntries(beam.DoFn):
    """
    Generates an entry for all sitemap levels for a single claim.
    """

    def __init__(self, hierarchy: list[int]):
        self.hierarchy = hierarchy
        # We always write sitemaps with production URL for now
        self.base_url = PROD_URL

    def process(self, claim_with_count_id: ClaimWithCountId) -> Iterator[SitemapEntry]:
        yield from generate_sitemap_entries(
            claim=claim_with_count_id.claim,
            count_id=claim_with_count_id.count_id,
            hierarchy=self.hierarchy,
            base_url=self.base_url,
        )


def run_sitemap_pipeline(
    runner: str,
    project_id: str,
    beam_args: Any,
    config: PipelineConfig,
    dry_run: bool,
    db_env: DbEnv,
    storage_env: StorageEnv,
    search_env: SearchEnv,
    search_index_id: str,
    input_file_pattern: str,
) -> None:
    pipeline_options = PipelineOptions(
        beam_args,
        runner=runner,
        job_name=config.job_name,
        temp_location=config.temp_dir,
        max_num_workers=config.max_num_workers,
    )
    pipeline_options.view_as(SetupOptions).save_main_session = True

    es = ElasticClient(search_env)
    claim_index = ClaimIndex(es, search_index_id)
    if not claim_index.exists():
        print(f"ERROR: Claim index {search_index_id} does not exist")
        return

    num_claims = claim_index.count()
    if not num_claims:
        print(f"ERROR: Claim index {claim_index.name} is empty")
        return

    hierarchy, num_leaf_level_sitemaps = get_sitemap_distribution_hierarchy(
        num_claims, MAX_ITEMS_PER_SITEMAP
    )

    with beam.Pipeline(options=pipeline_options) as p:
        claims_with_count_id = read_claims_with_count_id_from_parquet(
            p,
            input_file_pattern=input_file_pattern,
            db_env=db_env,
            project_id=project_id,
            total_num_claims=num_leaf_level_sitemaps,
        )
        results = (
            claims_with_count_id
            | "GenerateSitemapEntries" >> beam.ParDo(GenerateSitemapEntries(hierarchy))
            | "Reshuffle" >> beam.transforms.util.Reshuffle()
            | "DedupSitemapEntries" >> beam.Distinct()
            | "GroupBySitemap" >> beam.GroupBy(lambda x: x.sitemap)
            | "WriteSitemap"
            >> beam.ParDo(
                WriteSitemap(
                    dry_run=dry_run,
                    storage_env=storage_env,
                    project_id=project_id,
                    timestamp=config.timestamp,
                    search_index_id=search_index_id,
                )
            )
        )

        write_pipeline_results(config.results_file, results)
