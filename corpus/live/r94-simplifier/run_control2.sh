#!/bin/bash
# r94-simplifier control2 battery: committed tree (c7228893), no seat hogs
# (the host is already heavily loaded by foreign lanes — loadavg recorded).
set -u
cd "$(dirname "$0")/../../.." || exit 1   # repo root
echo "loadavg start: $(cat /proc/loadavg)"
python3 corpus/fixtures/run_battery.py --runs corpus/live/r94-simplifier/runs-control2
rc=$?
echo "battery rc=$rc"
echo "loadavg end: $(cat /proc/loadavg)"
exit $rc
