#!/bin/bash
# r94-simplifier fold-candidates battery: T0+start3 dead-store fold (−3 lines)
# on a copied tree (fold-candidates/). Expect: 314/314 PASS incl. r94 19/19 and
# r94_expected_errors_all_matched=True on the folded bytes.
set -u
cd "$(dirname "$0")/../../.." || exit 1   # repo root
echo "loadavg start: $(cat /proc/loadavg)"
python3 corpus/live/r94-simplifier/fold-candidates/run_battery.py \
  --runs corpus/live/r94-simplifier/runs-fold-candidates
rc=$?
echo "fold-candidates battery rc=$rc"
echo "loadavg end: $(cat /proc/loadavg)"
exit $rc
