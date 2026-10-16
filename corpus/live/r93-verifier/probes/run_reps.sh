#!/bin/bash
# r93 verifier — battery reps on the FROZEN committed fixtures (4b75151).
# Every rep launches the frozen extraction's run_battery.py, which copies the
# frozen fixtures into its own scratch project.  Never touches the worktree.
set -u
V=/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r93-verifier
cd "$V/freeze/x/corpus/fixtures" || exit 1
for i in 1 2 3 4 5; do
  echo "=== rep$i start $(date -u +%Y%m%dT%H%M%SZ) load=$(cut -d' ' -f1-3 /proc/loadavg)"
  python3 run_battery.py --godot /usr/bin/godot --runs "$V/runs" > "$V/battery$i.log" 2>&1
  echo "=== rep$i rc=$? end $(date -u +%Y%m%dT%H%M%SZ) load=$(cut -d' ' -f1-3 /proc/loadavg)"
done
echo "=== all reps done"
