#!/usr/bin/env bash
# r100-boundary matrix driver — the r100 scout's 14 GUI cells replayed under
# quiet / 16-hog load / --fixed-fps 30·60·120 / threaded physics (unstated mode),
# multiple fresh processes per cell.
#
#   bash run_matrix.sh quiet|load|ff30|ff60|ff120|thr|ff1
#
# Every launch is `timeout -s KILL 25`-bounded; stdout/stderr are split into
# per-cell sidecars plus .rc and .wall_ms.  The launch is the scout's exact shape
# (`res://r100_gui.gd`, the byte-frozen probe dd826f6e…) so stdout/stderr stay
# byte-comparable with corpus/live/r100-scout/runs/.  Hogs are this seat's own
# only and are killed by the EXIT trap (never pkill: other lanes run their own
# `yes` blocks); host `yes` count is recorded before/after to prove that.
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-25}
BATCH=${1:-quiet}
HOGS=${HOGS:-16}
PROJ=proj
FF=""
case "$BATCH" in
  quiet) ;;
  load) ;;
  ff1) FF="--fixed-fps 1" ;;
  ff30) FF="--fixed-fps 30" ;;
  ff60) FF="--fixed-fps 60" ;;
  ff120) FF="--fixed-fps 120" ;;
  thr) PROJ=proj_thr ;;
  *) echo "unknown batch: $BATCH" >&2; exit 2 ;;
esac
mkdir -p "runs/$BATCH"

HOG_PIDS=""
stop_load() {
  for p in $HOG_PIDS; do kill "$p" 2>/dev/null || true; done
  HOG_PIDS=""
}
trap 'stop_load' EXIT

host_yes_before=$(pgrep -fc '^yes$' 2>/dev/null || echo 0)
if [ "$BATCH" = "load" ]; then
  for i in $(seq 1 "$HOGS"); do yes > /dev/null & HOG_PIDS="$HOG_PIDS $!"; done
  sleep 2
fi

# cell|reps   (quiet: 3 fresh processes/cell; load: 3; ff: 2; thr: 2; ff1: 1)
case "$BATCH" in
  quiet|load) REPS=3 ;;
  ff1) REPS=1 ;;
  *) REPS=2 ;;
esac

: > "runs/$BATCH/rc-summary.txt"
note() { printf '%s\n' "$1" >> "runs/$BATCH/rc-summary.txt"; }
note "batch=$BATCH proj=$PROJ ff='${FF:-none}' hogs=${HOGS} bound=${BOUND} godot=$(timeout 20 "$GODOT" --version 2>&1 | tail -1)"
note "started=$(date -u +%Y-%m-%dT%H:%M:%SZ) load=$(cut -d' ' -f1-3 /proc/loadavg) host_yes=$host_yes_before"

for cell in census routing hover motion localpos cursor clip drag touch subvp warp focus render osmeta; do
  for i in $(seq 1 "$REPS"); do
    t0=$(date +%s%N)
    # shellcheck disable=SC2086
    timeout -s KILL "$BOUND" "$GODOT" --headless $FF --path "$PROJ" --script res://r100_gui.gd -- "--arm=$cell" \
      > "runs/$BATCH/r100b_gui_${cell}.rep${i}.out" 2> "runs/$BATCH/r100b_gui_${cell}.rep${i}.err"
    echo "$?" > "runs/$BATCH/r100b_gui_${cell}.rep${i}.rc"
    echo $(( ($(date +%s%N) - t0) / 1000000 )) > "runs/$BATCH/r100b_gui_${cell}.rep${i}.wall_ms"
  done
  note "$cell reps=$REPS rc=[$(cat runs/$BATCH/r100b_gui_${cell}.rep*.rc | tr '\n' ' ')]"
done

note "finished=$(date -u +%Y-%m-%dT%H:%M:%SZ) load=$(cut -d' ' -f1-3 /proc/loadavg)"
own_hogs=$(printf '%s' "$HOG_PIDS" | wc -w)
stop_load
host_yes_after=$(pgrep -fc '^yes$' 2>/dev/null || echo 0)
note "own_hogs_started=$own_hogs host_yes_after=$host_yes_after"
echo "--- $BATCH done; rc summary tail:"
tail -3 "runs/$BATCH/rc-summary.txt"
echo "--- timeout check (rc=137): $(grep -rl 137 runs/$BATCH/*.rc 2>/dev/null | wc -l)"
echo "--- stray r100_gui probes: $(pgrep -fc 'r100_gui.gd' || true)"
