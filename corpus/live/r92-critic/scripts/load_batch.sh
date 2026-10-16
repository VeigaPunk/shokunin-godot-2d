#!/usr/bin/env bash
# r92 critic seat — load batch. Adds 16 seat-owned `yes` hogs, runs all 14
# arms x2 in the battery launch shape, then kills exactly those hogs.
# Foreign hogs on this host are left untouched.
set -u
cd "$(dirname "$0")/.."
ulimit -c 0
pids=()
for i in $(seq 1 16); do
  yes > /dev/null &
  pids+=($!)
done
cleanup() { for p in "${pids[@]}"; do kill "$p" 2>/dev/null; done; wait 2>/dev/null; }
trap cleanup EXIT INT TERM
echo "loadavg before: $(cut -d' ' -f1-3 /proc/loadavg)  seat_hogs=${#pids[@]}" | tee -a runs/load.log
python3 scripts/probe.py run --proj proj --outdir runs --tag load \
  --arms census,atlas,cells,custom,terrain,pattern,encoding,fixinvalid,srcids,physics,timing,quadrant,nav,nullts \
  --reps 2 >/dev/null
echo "loadavg during: $(cut -d' ' -f1-3 /proc/loadavg)" | tee -a runs/load.log
cleanup
trap - EXIT
sleep 1
echo "loadavg after:  $(cut -d' ' -f1-3 /proc/loadavg)" | tee -a runs/load.log
ps -eo pid,ppid,comm | awk '$3=="yes" && $2==1 {c++} END {print "orphaned yes (ppid=1):", c+0}' | tee -a runs/load.log
python3 scripts/probe.py classify --dir runs --tag load 2>&1 | tail -3 | tee -a runs/load.log
