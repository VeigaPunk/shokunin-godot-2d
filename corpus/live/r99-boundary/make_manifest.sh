#!/usr/bin/env bash
# r99-boundary manifest — sha256 of every artefact under this lane dir.
set -u
cd "$(dirname "$0")"
rm -f manifest.sha256
find . -type f ! -name manifest.sha256 -print0 | sort -z | xargs -0 sha256sum > manifest.sha256
wc -l < manifest.sha256
