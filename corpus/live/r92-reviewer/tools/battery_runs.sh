#!/bin/bash
# r92-reviewer: two full battery runs on the PINNED committed harness.
# The harness copies HERE (= pinned/) into its own scratch, so the dirty
# worktree corpus/fixtures/ is never read by these runs.
set -u
cd /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
for n in 1 2; do
  echo "=== reviewer battery run $n start $(date -u +%FT%TZ) loadavg=$(cut -d' ' -f1-3 /proc/loadavg) ==="
  python3 corpus/live/r92-reviewer/pinned/run_battery.py \
      --runs corpus/live/r92-reviewer/runs$n > corpus/live/r92-reviewer/battery$n.log 2>&1
  echo "run $n rc=$? $(date -u +%FT%TZ)"
  tail -3 corpus/live/r92-reviewer/battery$n.log
done
