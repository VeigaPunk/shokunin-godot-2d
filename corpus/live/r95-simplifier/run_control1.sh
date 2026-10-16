#!/bin/bash
# r95-simplifier control1 battery: COMMITTED tree (9cd47507) with 8 explicit
# seat hogs on top of the foreign load. Mirrors the r94-simplifier control1
# shape; writes only corpus/live/r95-simplifier/runs-control1/.
set -u
cd "$(dirname "$0")/../../.." || exit 1   # repo root
HOGS=8
pids=()
for _ in $(seq "$HOGS"); do yes > /dev/null & pids+=($!); done
cleanup() { for p in "${pids[@]}"; do kill "$p" 2>/dev/null; done; }
trap cleanup EXIT
echo "loadavg start: $(cat /proc/loadavg)"
echo "own hogs: ${pids[*]}"
echo "harness sha256: $(sha256sum corpus/fixtures/run_battery.py)"
python3 corpus/fixtures/run_battery.py --runs corpus/live/r95-simplifier/runs-control1
rc=$?
echo "battery rc=$rc"
echo "loadavg end: $(cat /proc/loadavg)"
exit $rc
