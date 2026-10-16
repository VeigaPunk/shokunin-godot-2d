#!/bin/bash
# r93-reviewer: full battery runs on the PINNED committed harness (4b75151).
# The harness copies HERE (= pinned/) into its own scratch, so the dirty
# worktree corpus/fixtures/ is never read by these runs.
set -u
cd /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
N=${1:-1}
echo "=== reviewer battery run $N start $(date -u +%FT%TZ) loadavg=$(cut -d' ' -f1-3 /proc/loadavg) ==="
python3 corpus/live/r93-reviewer/pinned/run_battery.py \
    --runs corpus/live/r93-reviewer/runs$N > corpus/live/r93-reviewer/battery$N.log 2>&1
echo "run $N rc=$? $(date -u +%FT%TZ) loadavg=$(cut -d' ' -f1-3 /proc/loadavg)"
tail -5 corpus/live/r93-reviewer/battery$N.log
