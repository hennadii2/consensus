# Temporary packaging for running the populate_elasticsearch_with_full_claim_documents pipeline locally
FROM python:3.9

WORKDIR /shared/common

ARG GCLOUD_PROJECT_ID

ENV GCLOUD_PROJECT_ID=${GCLOUD_PROJECT_ID}
ENV GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/gcloud_service_auth

# Binary
COPY src.python.pipelines.records.populate_elasticsearch_with_full_claim_documents/populate_elasticsearch_with_full_claim_documents_main.pex /bin/populate_elasticsearch_with_full_claim_documents

# Local package dependencies
COPY common_dist-1.0.tar.gz /dist/common_dist.tar.gz
COPY protos_dist-1.0.tar.gz /dist/protos_dist.tar.gz
COPY populate_elasticsearch_with_full_claim_documents_dist-1.0.tar.gz /dist/populate_elasticsearch_with_full_claim_documents_dist.tar.gz

CMD /bin/populate_elasticsearch_with_full_claim_documents \
    --runner 'DataflowRunner' \
    --region 'us-central1' \
    --project ${GCLOUD_PROJECT_ID} \
    --extra_package /dist/protos_dist.tar.gz \
    --extra_package /dist/common_dist.tar.gz \
    --extra_package /dist/populate_elasticsearch_with_full_claim_documents_dist.tar.gz \
    --subnetwork 'https://www.googleapis.com/compute/v1/projects/consensus-334718/regions/us-central1/subnetworks/subnet-us-central1' \
    --service_account_email pipelines@consensus-334718.iam.gserviceaccount.com \
    --gcp_project_id ${GCLOUD_PROJECT_ID} \
    --db_env prod \
    --search_env dev \
    --input_patterns 'gs://consensus-paper-data/features/search_index_input/230524074450_existing_and_resolved_papers/*parquet*' \
    --input_patterns 'gs://consensus-paper-data/features/search_index_input/230524074450_new_and_existing_needs_reprocessing/*parquet*' \
    --input_patterns 'gs://consensus-paper-data/features/search_index_input/20230622_missing_embeddings/*parquet*' \
    --input_patterns 'gs://consensus-paper-data/features/search_index_input/20230622_missing_title_embeddings/*parquet*' \
