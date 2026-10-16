#!/bin/bash
# r95-simplifier floor-gate battery: the folded harness (one stale r95
# allowlist entry) + committed fixtures, 8 seat hogs.
set -u
cd "$(dirname "$0")/../../.." || exit 1   # repo root
HOGS=8
pids=()
for _ in $(seq "$HOGS"); do yes > /dev/null & pids+=($!); done
cleanup() { for p in "${pids[@]}"; do kill "$p" 2>/dev/null; done; }
trap cleanup EXIT
echo "loadavg start: $(cat /proc/loadavg)"
echo "folded harness sha256: $(sha256sum corpus/live/r95-simplifier/fold-gate/run_battery.py)"
python3 corpus/live/r95-simplifier/fold-gate/run_battery.py --runs corpus/live/r95-simplifier/runs-fold-gate
rc=$?
echo "battery rc=$rc"
echo "loadavg end: $(cat /proc/loadavg)"
exit $rc
