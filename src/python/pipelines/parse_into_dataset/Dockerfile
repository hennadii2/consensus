# Temporary packaging for running the parse_into_dataset pipeline locally
FROM python:3.9

WORKDIR /shared/common

ARG GCLOUD_PROJECT_ID

ENV GCLOUD_PROJECT_ID=${GCLOUD_PROJECT_ID}
ENV GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/gcloud_service_auth

# Binary
COPY src.python.pipelines.parse_into_dataset/parse_into_dataset_main.pex /bin/parse_into_dataset

# Local package dependencies
COPY parse_into_dataset_dist-1.0.tar.gz /dist/parse_into_dataset_dist.tar.gz
COPY common_dist-1.0.tar.gz /dist/common_dist.tar.gz
COPY protos_dist-1.0.tar.gz /dist/protos_dist.tar.gz

COPY src/mock_data/raw_semantic_scholar_s2-corpus-000_2022-01-01.gz src/mock_data/raw_semantic_scholar_s2-corpus-000_2022-01-01.gz

CMD /bin/parse_into_dataset \
    --runner 'DataflowRunner' \
    --region 'us-central1' \
    --project ${GCLOUD_PROJECT_ID} \
    --extra_package /dist/protos_dist.tar.gz \
    --extra_package /dist/common_dist.tar.gz \
    --extra_package /dist/parse_into_dataset_dist.tar.gz \
    --subnetwork 'https://www.googleapis.com/compute/v1/projects/consensus-334718/regions/us-central1/subnetworks/subnet-us-central1' \
    --service_account_email pipelines@consensus-334718.iam.gserviceaccount.com \
    --gcp_project_id ${GCLOUD_PROJECT_ID} \
