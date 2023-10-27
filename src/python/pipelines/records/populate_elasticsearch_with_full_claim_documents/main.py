"""
Iterates over claim feature records and writes full claims to a newly created
Elasticsearch index.
"""
import argparse
import logging

from common.beam.pipeline_config import get_pipeline_config
from common.db.connect import DbEnv
from common.search.connect import SearchEnv
from pipelines.records.populate_elasticsearch_with_full_claim_documents.pipeline import (
    run_pipeline,
)

PIPELINE_NAME = "populate-elasticsearch-with-full-claim-documents"


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
        "--input_patterns",
        action="append",
        dest="input_patterns",
        required=True,
        help="GCS file patterns that contain record parquets to ingest",
    )
    parser.add_argument(
        "--db_env",
        dest="db_env",
        default="dev",
        help="The database environment to read from ('dev'|'prod'|'prod-ingest')",
    )
    parser.add_argument(
        "--search_env",
        dest="search_env",
        default="dev",
        help="The database environment to write to ('dev'|'prod-ingest')",
    )
    parser.add_argument(
        "--no_dry_run",
        action="store_true",
        help="If set, data will be written to the database",
    )
    parser.add_argument(
        "--quantize_vectors",
        action="store_true",
        help="If set, embeddings will be quantized to 8 bits",
    )
    args, pipeline_args = parser.parse_known_args(argv)

    db_env = DbEnv(args.db_env)
    search_env = SearchEnv(args.search_env)
    if search_env != SearchEnv.PROD_INGEST and search_env != SearchEnv.DEV:
        logging.error(f"You can only ingest into search prod-ingest or dev, not {search_env}.")
        return

    pipeline_config = get_pipeline_config(PIPELINE_NAME)
    run_pipeline(
        runner=args.runner,
        project_id=args.gcp_project_id,
        beam_args=pipeline_args,
        config=pipeline_config,
        dry_run=(not args.no_dry_run),
        db_env=db_env,
        search_env=search_env,
        input_patterns=args.input_patterns,
        quantize_vectors=args.quantize_vectors,
    )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    main()
