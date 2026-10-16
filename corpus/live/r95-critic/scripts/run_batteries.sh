#!/usr/bin/env bash
# r95 critic: two full battery reps on the FROZEN committed tree (git archive
# 9cd47507), independent of the author's runs. Serial.
set -u
cd /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin || exit 1
B=corpus/live/r95-critic/frozen/corpus/fixtures/run_battery.py
R=corpus/live/r95-critic/battery-runs
echo "=== battery start $(date -u +%H:%M:%S) loadavg=$(cut -d' ' -f1 /proc/loadavg)"
python3 "$B" --runs "$R/full-rep1" > "$R/full-rep1.log" 2>&1; echo "rep1 rc=$?"
echo "=== rep1 done $(date -u +%H:%M:%S) loadavg=$(cut -d' ' -f1 /proc/loadavg)"
python3 "$B" --runs "$R/full-rep2" > "$R/full-rep2.log" 2>&1; echo "rep2 rc=$?"
echo "=== battery done $(date -u +%H:%M:%S) loadavg=$(cut -d' ' -f1 /proc/loadavg)"
