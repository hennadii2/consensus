# Temporary packaging for running the download_semantic_scholar pipeline locally
FROM python:3.9

WORKDIR /shared/common

ARG GCLOUD_PROJECT_ID

ENV GCLOUD_PROJECT_ID=${GCLOUD_PROJECT_ID}
ENV GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/gcloud_service_auth

# Binary
COPY src.python.pipelines.download_semantic_scholar/download_semantic_scholar_main.pex /bin/download_semantic_scholar

# Local package dependencies
COPY protos_dist-1.0.tar.gz /dist/protos_dist.tar.gz
COPY common_dist-1.0.tar.gz /dist/common_dist.tar.gz
COPY download_semantic_scholar_dist-1.0.tar.gz /dist/download_semantic_scholar_dist.tar.gz

CMD /bin/download_semantic_scholar \
    --runner 'DataflowRunner' \
    --machine_type 'm1-ultramem-40' \
    --disk_size_gb 4000 \
    --experiments 'use_runner_v2' \
    --number_of_worker_harness_threads 10 \
    --num_workers 1 \
    --region 'us-central1' \
    --project ${GCLOUD_PROJECT_ID} \
    --extra_package /dist/protos_dist.tar.gz \
    --extra_package /dist/common_dist.tar.gz \
    --extra_package /dist/download_semantic_scholar_dist.tar.gz \
    --subnetwork 'https://www.googleapis.com/compute/v1/projects/consensus-334718/regions/us-central1/subnetworks/subnet-us-central1' \
    --service_account_email pipelines@consensus-334718.iam.gserviceaccount.com \
    --gcp_project_id ${GCLOUD_PROJECT_ID} \
