#!/usr/bin/env bash

# Workaround to run a tests in a docker container, until it is supported by
# pants directly (https://github.com/pantsbuild/pants/issues/13682)
# To run a test in this mode:
#   1. Name the test target with the prefix $(SKIP_DOCKER_TEST_PREFIX) (see Makefile)
#   2. Add the Dockerfile as the only depencency on the test target

set -euo pipefail

test_target="${1?'ERROR: must give test target (1)'}"

dockerfile="$(./pants filedeps --transitive "${test_target}" | grep Dockerfile)"
docker_target="$(./pants peek "${dockerfile}" | jq -r '.[] | .["address"]')"
docker_image="$(echo "${docker_target}" | cut -d ':' -f2)"

./pants package "${dockerfile}"
docker run \
	-v "$PWD":/shared/common \
	-w /shared/common \
	--rm "${docker_image}":latest \
	"./pants test ${test_target}"
