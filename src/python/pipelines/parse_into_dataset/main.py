"""

Iterates over all nested clean paper data in an input path, creates a new
dataset directory, tokenizes the text into sentences, and writes the tokenized
abstract sentences into parquet files.

"""
import argparse
import logging

from common.beam.pipeline_config import get_pipeline_config
from common.db.connect import DbEnv
from common.storage.connect import StorageEnv
from pipelines.parse_into_dataset.parse_into_dataset import run_parse_into_dataset_pipeline

PIPELINE_NAME = "parse-into-dataset"


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
        "--db_env",
        dest="db_env",
        default="dev",
        help="The database environment to write to ('dev'|'prod')",
    )
    parser.add_argument(
        "--no_dry_run",
        action="store_true",
        help="If set, data will be written to the database",
    )
    args, pipeline_args = parser.parse_known_args(argv)

    pipeline_config = get_pipeline_config(PIPELINE_NAME)
    run_parse_into_dataset_pipeline(
        runner=args.runner,
        project_id=args.gcp_project_id,
        beam_args=pipeline_args,
        config=pipeline_config,
        dry_run=(not args.no_dry_run),
        db_env=DbEnv(args.db_env),
        storage_env=StorageEnv(args.db_env),
    )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    main()
