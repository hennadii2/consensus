# Temporary packaging for running the sitemap pipeline locally
FROM python:3.9

WORKDIR /shared/common

ARG GCLOUD_PROJECT_ID

ENV GCLOUD_PROJECT_ID=${GCLOUD_PROJECT_ID}
ENV GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/gcloud_service_auth

# Binary
COPY src.python.pipelines.sitemap/sitemap_main.pex /bin/sitemap

# Local package dependencies
COPY protos_dist-1.0.tar.gz /dist/protos_dist.tar.gz
COPY common_dist-1.0.tar.gz /dist/common_dist.tar.gz
COPY sitemap_dist-1.0.tar.gz /dist/sitemap_dist.tar.gz

CMD /bin/sitemap \
    --runner DataflowRunner \
    --region us-central1 \
    --project ${GCLOUD_PROJECT_ID} \
    --extra_package /dist/protos_dist.tar.gz \
    --extra_package /dist/common_dist.tar.gz \
    --extra_package /dist/sitemap_dist.tar.gz \
    --subnetwork https://www.googleapis.com/compute/v1/projects/consensus-334718/regions/us-central1/subnetworks/subnet-us-central1 \
    --service_account_email pipelines@consensus-334718.iam.gserviceaccount.com \
    --gcp_project_id ${GCLOUD_PROJECT_ID} \
    --input_file_pattern gs://consensus-paper-data/datasets/20220928180152/outputs/claim_extraction/biomed_roberta/v1.0/purpose_fix/claims/* \
    --search_index_id 20220928180152-claim_extraction_biomed_roberta_v1_0-purpose_fix-claims-221223203652-shrunk \
    --db_env prod \
    --search_env prod \
