# Temporary packaging for running the study_types_ingest pipeline locally
FROM python:3.9

WORKDIR /shared/common

ARG GCLOUD_PROJECT_ID

ENV GCLOUD_PROJECT_ID=${GCLOUD_PROJECT_ID}
ENV GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/gcloud_service_auth

# Binary
COPY src.python.pipelines.study_types_ingest/study_types_ingest_main.pex /bin/study_types_ingest

# Local package dependencies
COPY protos_dist-1.0.tar.gz /dist/protos_dist.tar.gz
COPY common_dist-1.0.tar.gz /dist/common_dist.tar.gz
COPY study_types_ingest_dist-1.0.tar.gz /dist/study_types_ingest_dist.tar.gz

CMD /bin/study_types_ingest \
    --runner DataflowRunner \
    --region us-central1 \
    --project ${GCLOUD_PROJECT_ID} \
    --extra_package /dist/protos_dist.tar.gz \
    --extra_package /dist/common_dist.tar.gz \
    --extra_package /dist/study_types_ingest_dist.tar.gz \
    --subnetwork https://www.googleapis.com/compute/v1/projects/consensus-334718/regions/us-central1/subnetworks/subnet-us-central1 \
    --service_account_email pipelines@consensus-334718.iam.gserviceaccount.com \
    --gcp_project_id ${GCLOUD_PROJECT_ID} \
    --input_file_pattern gs://consensus-paper-data/datasets/20220928180152/outputs/study_type/biomed_roberta/v0.2/* \
    --db_env prod-ingest \
