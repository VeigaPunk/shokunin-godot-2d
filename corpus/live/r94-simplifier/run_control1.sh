#!/bin/bash
# r94-simplifier control battery: committed tree (c7228893), explicit load.
# Usage: bash run_control1.sh
set -u
cd "$(dirname "$0")/../../.." || exit 1   # repo root
HOGS=8
pids=()
for _ in $(seq "$HOGS"); do yes > /dev/null & pids+=($!); done
cleanup() { for p in "${pids[@]}"; do kill "$p" 2>/dev/null; done; }
trap cleanup EXIT
echo "loadavg start: $(cat /proc/loadavg)"
echo "own hogs: ${pids[*]}"
python3 corpus/fixtures/run_battery.py --runs corpus/live/r94-simplifier/runs-control1
rc=$?
echo "battery rc=$rc"
echo "loadavg end: $(cat /proc/loadavg)"
exit $rc
