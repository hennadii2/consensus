# Temporary packaging for running the ingest_semantic_scholar pipeline locally
FROM python:3.9

WORKDIR /shared/common

ARG GCLOUD_PROJECT_ID

ENV GCLOUD_PROJECT_ID=${GCLOUD_PROJECT_ID}
ENV GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/gcloud_service_auth

# Binary
COPY src.python.pipelines.ingest_semantic_scholar/ingest_semantic_scholar_main.pex /bin/ingest_semantic_scholar

# Local package dependencies
COPY ingest_semantic_scholar_dist-1.0.tar.gz /dist/ingest_semantic_scholar_dist.tar.gz
COPY common_dist-1.0.tar.gz /dist/common_dist.tar.gz
COPY protos_dist-1.0.tar.gz /dist/protos_dist.tar.gz

CMD /bin/ingest_semantic_scholar \
    --runner 'DataflowRunner' \
    --machine_type 'n1-highmem-8' \
    --region 'us-central1' \
    --project ${GCLOUD_PROJECT_ID} \
    --extra_package /dist/protos_dist.tar.gz \
    --extra_package /dist/common_dist.tar.gz \
    --extra_package /dist/ingest_semantic_scholar_dist.tar.gz \
    --subnetwork 'https://www.googleapis.com/compute/v1/projects/consensus-334718/regions/us-central1/subnetworks/subnet-us-central1' \
    --service_account_email pipelines@consensus-334718.iam.gserviceaccount.com \
    --gcp_project_id ${GCLOUD_PROJECT_ID} \
    --input_dir 'gs://consensus-paper-data/raw/s2/2022-09-13' \
