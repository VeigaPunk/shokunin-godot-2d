#!/usr/bin/env bash
# r95 critic condition matrix — serial, one batch at a time (the host is shared;
# never run two of this seat's batches concurrently).
set -u
cd /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin || exit 1
S=corpus/live/r95-critic/scripts/run_arms.py
echo "=== matrix start $(date -u +%H:%M:%S) loadavg=$(cut -d' ' -f1 /proc/loadavg)"
python3 "$S" --batch ff1   --reps 1 --fixed-fps 1
python3 "$S" --batch ff30  --reps 1 --fixed-fps 30
python3 "$S" --batch ff120 --reps 1 --fixed-fps 120
python3 "$S" --batch tps30 --reps 1 --tps 30
python3 "$S" --batch tps120 --reps 1 --tps 120
python3 "$S" --batch thr   --reps 1 --threaded
python3 "$S" --batch load  --reps 1 --hog 16
echo "=== matrix done $(date -u +%H:%M:%S) loadavg=$(cut -d' ' -f1 /proc/loadavg)"
