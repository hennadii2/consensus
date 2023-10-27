"""
Downloads all dataset files from latest semantic scholar release to GCS.
"""
import argparse
import logging

from common.beam.pipeline_config import get_pipeline_config
from common.storage.connect import StorageEnv
from pipelines.download_semantic_scholar.pipeline import run_pipeline

PIPELINE_NAME = "download-semantic-scholar"


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
        "--storage_env",
        dest="storage_env",
        default="dev",
        help="The database environment to read from ('dev'|'prod')",
    )
    parser.add_argument(
        "--no_dry_run",
        action="store_true",
        help="If set, data will be written to the database",
    )
    args, pipeline_args = parser.parse_known_args(argv)

    pipeline_config = get_pipeline_config(PIPELINE_NAME)
    run_pipeline(
        runner=args.runner,
        project_id=args.gcp_project_id,
        beam_args=pipeline_args,
        config=pipeline_config,
        dry_run=(not args.no_dry_run),
        storage_env=StorageEnv(args.storage_env),
    )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    main()
