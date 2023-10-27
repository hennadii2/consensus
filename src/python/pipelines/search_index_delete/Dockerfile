# Temporary packaging for running the search_index_delete pipeline locally
FROM python:3.9

WORKDIR /shared/common

ARG GCLOUD_PROJECT_ID

ENV GCLOUD_PROJECT_ID=${GCLOUD_PROJECT_ID}
ENV GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/gcloud_service_auth

# Binary
COPY src.python.pipelines.search_index_delete/search_index_delete_main.pex /bin/search_index_delete

# Local package dependencies
COPY protos_dist-1.0.tar.gz /dist/protos_dist.tar.gz
COPY common_dist-1.0.tar.gz /dist/common_dist.tar.gz
COPY search_index_delete_dist-1.0.tar.gz /dist/search_index_delete_dist.tar.gz

CMD /bin/search_index_delete \
    --runner DataflowRunner \
    --region us-central1 \
    --disk_size_gb=250 \
    --machine_type='n1-highmem-4' \
    --experiments=use_runner_v2 \
    --number_of_worker_harness_threads=2 \
    --project ${GCLOUD_PROJECT_ID} \
    --extra_package /dist/protos_dist.tar.gz \
    --extra_package /dist/common_dist.tar.gz \
    --extra_package /dist/search_index_delete_dist.tar.gz \
    --subnetwork https://www.googleapis.com/compute/v1/projects/consensus-334718/regions/us-central1/subnetworks/subnet-us-central1 \
    --service_account_email pipelines@consensus-334718.iam.gserviceaccount.com \
    --gcp_project_id ${GCLOUD_PROJECT_ID} \
    --input_file_pattern gs://consensus-paper-data/datasets/20220928180152/outputs/claim_extraction/biomed_roberta/v1.0/purpose_fix/deleted/* \
    --search_index_id 20220928180152-claim_extraction_biomed_roberta-v1_0-deduplicated-221019040900 \
    --db_env prod-ingest \
    --search_env prod-ingest \
