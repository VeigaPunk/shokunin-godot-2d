#!/usr/bin/env bash
# r89 baseline rep runner — replays the FROZEN tracked tree (git archive HEAD=0628932)
# into receipt dirs under corpus/live/r89-baseline/. Serial reps only.
# Usage: run-reps.sh <repN>
set -u
LIVE=/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
TREE=$LIVE/corpus/live/r89-baseline/tree
OUT=$LIVE/corpus/live/r89-baseline
N=${1:?rep number}
mkdir -p "$OUT/runs$N"
sha=$(sha256sum "$TREE/corpus/fixtures/run_battery.py" | cut -d' ' -f1)
echo "[pre-rep$N] $(date -u +%FT%TZ) harness=$sha live_head=$(git -C "$LIVE" rev-parse HEAD) load=$(cut -d' ' -f1-3 /proc/loadavg)" >> "$OUT/rep-timing.txt"
t0=$(date +%s.%N)
cd "$TREE" || exit 90
PYTHONDONTWRITEBYTECODE=1 timeout 1200 python3 -B corpus/fixtures/run_battery.py --runs "$OUT/runs$N" \
  > "$OUT/godot-battery-rep$N.stdout" 2> "$OUT/godot-battery-rep$N.stderr"
rc=$?
t1=$(date +%s.%N)
secs=$(awk "BEGIN{printf \"%.3f\", $t1 - $t0}")
echo "[rep$N-end] $(date -u +%FT%TZ) rc=$rc seconds=$secs load=$(cut -d' ' -f1-3 /proc/loadavg)" >> "$OUT/rep-timing.txt"
sha2=$(sha256sum "$TREE/corpus/fixtures/run_battery.py" | cut -d' ' -f1)
echo "[post-rep$N] $(date -u +%FT%TZ) harness=$sha2 live_head=$(git -C "$LIVE" rev-parse HEAD)" >> "$OUT/rep-timing.txt"
echo "DONE rep$N rc=$rc seconds=$secs"
