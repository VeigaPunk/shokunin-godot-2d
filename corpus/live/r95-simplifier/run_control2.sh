#!/bin/bash
# r95-simplifier control2 battery: COMMITTED tree (9cd47507), no seat hogs
# (the host is already heavily loaded by foreign lanes; loadavg recorded).
set -u
cd "$(dirname "$0")/../../.." || exit 1   # repo root
echo "loadavg start: $(cat /proc/loadavg)"
echo "harness sha256: $(sha256sum corpus/fixtures/run_battery.py)"
python3 corpus/fixtures/run_battery.py --runs corpus/live/r95-simplifier/runs-control2
rc=$?
echo "battery rc=$rc"
echo "loadavg end: $(cat /proc/loadavg)"
exit $rc
