#!/usr/bin/env bash
# r91-critic: write the seat manifest over all seat-owned artifacts.
set -u
cd "$(dirname "$0")/.."
{
  find . -type f ! -name 'manifest.sha256' ! -path './battery-runs/*/scratch/*' \
       ! -path './battery/*' -print0 | sort -z | xargs -0 sha256sum
} > manifest.sha256
wc -l manifest.sha256
