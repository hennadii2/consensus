#!/usr/bin/env bash

# In CI, the cache must be uploaded and downloaded every run. This takes time,
# so there is a tradeoff where too large of a cache will slow down your CI.
# Use this script to help avoid that problem.
# See: https://www.pantsbuild.org/docs/using-pants-in-ci

set -euo pipefail

function delete_if_too_big() {
	path=$1
	limit_mb=$2
	if [[ ! -f "${path}" ]]; then
		echo "${path} does not exists."
		return
	fi
	echo "${path} does exists."
	size_mb=$(du -m -d0 "${path}" | cut -f 1)
	if ((size_mb > limit_mb)); then
		echo "${path} is too large (${size_mb}mb), deleting it."
		#rm -rf "${path}"
	fi
}

delete_if_too_big ~/.cache/pants/lmdb_store 2048
delete_if_too_big ~/.cache/pants/setup 256
delete_if_too_big ~/.cache/pants/named_caches 1024
