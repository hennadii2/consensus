# Temporary packaging for running the update_elasticsearch_with_claim_embeddings pipeline locally
FROM python:3.9

WORKDIR /shared/common

ARG GCLOUD_PROJECT_ID

ENV GCLOUD_PROJECT_ID=${GCLOUD_PROJECT_ID}
ENV GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/gcloud_service_auth

# Binary
COPY src.python.pipelines.records.update_elasticsearch_with_claim_embeddings/update_elasticsearch_with_claim_embeddings_main.pex /bin/update_elasticsearch_with_claim_embeddings

# Local package dependencies
COPY common_dist-1.0.tar.gz /dist/common_dist.tar.gz
COPY protos_dist-1.0.tar.gz /dist/protos_dist.tar.gz
COPY update_elasticsearch_with_claim_embeddings_dist-1.0.tar.gz /dist/update_elasticsearch_with_claim_embeddings_dist.tar.gz

CMD /bin/update_elasticsearch_with_claim_embeddings \
    --runner 'DirectRunner' \
    --region 'us-central1' \
    --worker_machine_type=n2-highmem-2 \
    --number_of_worker_harness_threads=1 \
    --project ${GCLOUD_PROJECT_ID} \
    --extra_package /dist/protos_dist.tar.gz \
    --extra_package /dist/common_dist.tar.gz \
    --extra_package /dist/update_elasticsearch_with_claim_embeddings_dist.tar.gz \
    --subnetwork 'https://www.googleapis.com/compute/v1/projects/consensus-334718/regions/us-central1/subnetworks/subnet-us-central1' \
    --service_account_email pipelines@consensus-334718.iam.gserviceaccount.com \
    --gcp_project_id ${GCLOUD_PROJECT_ID} \
    --search_env prod-ingest \
    --search_index_id_no_prefix populate-elasticsearch-with-base-claims-230607083124 \
    --input_patterns 'gs://consensus-paper-data/features/embeddings/230524074450_existing_and_resolved_papers/claim/all-MiniLM-L6-v2/outputs.parquet*' \
    --input_patterns 'gs://consensus-paper-data/features/embeddings/230524074450_new_and_existing_needs_reprocessing/claim/all-MiniLM-L6-v2/outputs.parquet*' \
