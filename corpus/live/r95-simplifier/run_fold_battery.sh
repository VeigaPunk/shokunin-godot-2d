#!/bin/bash
# r95-simplifier folded-tree battery: the 18-site dead-store fold applied to
# both fixtures + the two harness sha256 comment lines updated (fold-battery-project/).
set -u
cd "$(dirname "$0")/../../.." || exit 1   # repo root
HOGS=4
pids=()
for _ in $(seq "$HOGS"); do yes > /dev/null & pids+=($!); done
cleanup() { for p in "${pids[@]}"; do kill "$p" 2>/dev/null; done; }
trap cleanup EXIT
echo "loadavg start: $(cat /proc/loadavg)"
echo "folded fixtures: $(sha256sum corpus/live/r95-simplifier/fold-battery-project/dss_lattice.gd corpus/live/r95-simplifier/fold-battery-project/r95b_order.gd)"
python3 corpus/live/r95-simplifier/fold-battery-project/run_battery.py --runs corpus/live/r95-simplifier/runs-fold-battery
rc=$?
echo "battery rc=$rc"
echo "loadavg end: $(cat /proc/loadavg)"
exit $rc
