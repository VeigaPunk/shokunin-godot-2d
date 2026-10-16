#!/bin/bash
# r94-simplifier fold-gate battery: committed harness + 1 injected stale r94
# allowlist entry (fold-gate/). Expect: r94 row still PASS, r94 gate False,
# dead_entry_count=1, battery FAIL on probe_error_clause_surface.
set -u
cd "$(dirname "$0")/../../.." || exit 1   # repo root
echo "loadavg start: $(cat /proc/loadavg)"
python3 corpus/live/r94-simplifier/fold-gate/run_battery.py \
  --runs corpus/live/r94-simplifier/runs-fold-gate
rc=$?
echo "fold-gate battery rc=$rc"
echo "loadavg end: $(cat /proc/loadavg)"
exit $rc
