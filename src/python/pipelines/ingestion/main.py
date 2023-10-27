"""

Iterates over all raw paper data in an input path, extracts the metadata, and
writes an entry into the papers table.

This pipeline does not currently handle deduping or overwriting existing entries.

"""
import argparse
import logging

from common.beam.pipeline_config import get_pipeline_config
from common.db.connect import DbEnv
from pipelines.ingestion.ingestion import run_ingestion_pipeline

PIPELINE_NAME = "ingestion"


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--gcp_project_id",
        dest="gcp_project_id",
        required=True,
        help="Google cloud project ID",
    )
    parser.add_argument(
        "--runner",
        dest="runner",
        default="DirectRunner",
        help="Where to run the job. DataflowRunner cloud, DirectRunner local.",
    )
    parser.add_argument(
        "--input_dir",
        dest="input_dir",
        required=True,
        help="GCS bucket that contains raw paper files to ingest",
    )
    parser.add_argument(
        "--db_env",
        dest="db_env",
        default="dev",
        help="The database environment to write to ('dev'|'prod')",
    )
    parser.add_argument(
        "--paper_provider",
        dest="paper_provider",
        default="SEMANTIC_SCHOLAR",
        help="The paper source provider ('SEMANTIC_SCHOLAR'|'CORE')",
    )
    parser.add_argument(
        "--no_dry_run",
        action="store_true",
        help="If set, data will be written to the database",
    )
    args, pipeline_args = parser.parse_known_args(argv)

    pipeline_config = get_pipeline_config(PIPELINE_NAME)
    run_ingestion_pipeline(
        runner=args.runner,
        project_id=args.gcp_project_id,
        beam_args=pipeline_args,
        config=pipeline_config,
        dry_run=(not args.no_dry_run),
        db_env=DbEnv(args.db_env),
        input_dir=args.input_dir,
        provider=args.paper_provider,
    )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    main()
