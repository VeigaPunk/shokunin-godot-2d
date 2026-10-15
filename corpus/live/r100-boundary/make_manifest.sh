#!/usr/bin/env bash
# r100-boundary manifest — sha256 of every receipt, probe, driver and the report,
# with paths relative to the repo root (game-dev-2d-shokunin/).
set -u
cd "$(dirname "$0")"
REPO_ROOT=$(cd ../../.. && pwd)
REPORT_REL="reports/round-100/r100-boundary.md"
cd "$REPO_ROOT"
{
  find corpus/live/r100-boundary -type f ! -name manifest.sha256 -print0 \
    | sort -z | xargs -0 sha256sum
  if [ -f "$REPORT_REL" ]; then
    sha256sum "$REPORT_REL" | sed "s# .*#  $REPORT_REL#"
  fi
} > corpus/live/r100-boundary/manifest.sha256
wc -l < corpus/live/r100-boundary/manifest.sha256
