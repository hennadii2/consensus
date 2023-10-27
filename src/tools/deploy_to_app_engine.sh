#!/usr/bin/env bash

set -euo pipefail

APP_ENGINE_CONFIG="./src/python/web/backend/dev.yaml"
DOCKERFILE="./src/python/web/backend/Dockerfile"
TARGET_PACKAGE="./src/python/web/backend:backend"
GENERATED_PEX="dist/src.python.web.backend/backend.pex"

function main() {
	local deploy_dir
	deploy_dir=$(mktemp -d)

	./pants package "${TARGET_PACKAGE}"
	cp "${GENERATED_PEX}" "${deploy_dir}"
	cp "${APP_ENGINE_CONFIG}" "${deploy_dir}/app.yaml"
	cp "${DOCKERFILE}" "${deploy_dir}/Dockerfile"

	pushd "${deploy_dir}"
	gcloud app deploy
	popd

	rm -rf "${deploy_dir}"
}

main
