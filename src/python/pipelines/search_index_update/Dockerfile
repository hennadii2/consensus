# Temporary packaging for running the search_index pipeline locally
FROM python:3.9

WORKDIR /shared/common

ARG GCLOUD_PROJECT_ID

ENV GCLOUD_PROJECT_ID=${GCLOUD_PROJECT_ID}
ENV GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/gcloud_service_auth

# Local package dependencies
COPY protos_dist-1.0.tar.gz /dist/protos_dist.tar.gz
COPY common_dist-1.0.tar.gz /dist/common_dist.tar.gz
COPY search_index_update_dist-1.0.tar.gz /dist/search_index_update_dist.tar.gz

# Binary
COPY src.python.pipelines.search_index_update/search_index_update_main.pex /bin/search_index_update

CMD /bin/search_index_update \
    --runner DataflowRunner \
    --region us-central1 \
    --project ${GCLOUD_PROJECT_ID} \
    --extra_package /dist/protos_dist.tar.gz \
    --extra_package /dist/common_dist.tar.gz \
    --extra_package /dist/search_index_update_dist.tar.gz \
    --subnetwork https://www.googleapis.com/compute/v1/projects/consensus-334718/regions/us-central1/subnetworks/subnet-us-central1 \
    --service_account_email pipelines@consensus-334718.iam.gserviceaccount.com \
    --gcp_project_id ${GCLOUD_PROJECT_ID} \
    --input_file_pattern gs://consensus-paper-data/datasets/20220928180152/outputs/claim_extraction/biomed_roberta/v1.0/purpose_fix/claims/sentences.parquet-00000000000* \
    --search_index_id_no_prefix 20220408195323-biomed_roberta_v0_3-20220502_filtered_with_title-modified_and_deduplicated_v2-220924225330 \
    --search_env dev \
    --db_env dev
