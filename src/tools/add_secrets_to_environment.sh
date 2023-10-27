#!/usr/bin/env bash

# Writes secrets from enviornment variables to their expected file paths, which
# is required when running code in github actions.

set -euo pipefail

SECRETS_DIR="${PWD}"/.secrets
mkdir -p "${SECRETS_DIR}"

echo "${ENV}" >>"${SECRETS_DIR}/env"
echo "${GCLOUD_SERVICE_AUTH}" >>"${SECRETS_DIR}/gcloud_service_auth"
