#!/bin/bash
# r93-reviewer floor-gate control (ctlB analog): one planted dead r93
# expected_errors entry in a pinned copy; the battery must FAIL loudly.
set -u
cd /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
echo "=== ctl battery start $(date -u +%FT%TZ) loadavg=$(cut -d' ' -f1-3 /proc/loadavg) ==="
python3 corpus/live/r93-reviewer/ctl/proj/run_battery.py \
    --runs corpus/live/r93-reviewer/ctl/runs > corpus/live/r93-reviewer/ctl/battery.log 2>&1
echo "ctl rc=$? $(date -u +%FT%TZ) loadavg=$(cut -d' ' -f1-3 /proc/loadavg)"
tail -4 corpus/live/r93-reviewer/ctl/battery.log
