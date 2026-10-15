#!/usr/bin/env bash
# r100-boundary artifact-probe driver — phase/ordering/startup arms
# (probes/r100b_phase.gd) plus the same-process sequencing probe
# (probes/r100b_seq.gd, built by make_seq.py from the frozen scout probe).
#
#   bash run_probes.sh quiet|load|ff30|ff60|ff120|thr
#
# Same launch/hog discipline as run_matrix.sh: 16 own hogs, killed by PID via
# the EXIT trap; `timeout -s KILL 25`; rc/wall_ms sidecars.
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
  ff30) FF="--fixed-fps 30" ;;
  ff60) FF="--fixed-fps 60" ;;
  ff120) FF="--fixed-fps 120" ;;
  thr) PROJ=proj_thr ;;
  *) echo "unknown batch: $BATCH" >&2; exit 2 ;;
esac
case "$BATCH" in
  quiet) REPS=3 ;;
  *) REPS=2 ;;
esac
OUT="runs/probes/$BATCH"
mkdir -p "$OUT"
cp -f probes/r100b_phase.gd "$PROJ/"
cp -f probes/r100b_seq.gd "$PROJ/"

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

: > "$OUT/rc-summary.txt"
note() { printf '%s\n' "$1" >> "$OUT/rc-summary.txt"; }
note "batch=$BATCH proj=$PROJ ff='${FF:-none}' hogs=${HOGS} bound=${BOUND} godot=$(timeout 20 "$GODOT" --version 2>&1 | tail -1)"
note "started=$(date -u +%Y-%m-%dT%H:%M:%SZ) load=$(cut -d' ' -f1-3 /proc/loadavg) host_yes=$host_yes_before"

run_one() { # name script args
  local name="$1" script="$2" args="$3"
  for i in $(seq 1 "$REPS"); do
    t0=$(date +%s%N)
    # shellcheck disable=SC2086
    timeout -s KILL "$BOUND" "$GODOT" --headless $FF --path "$PROJ" --script "$script" -- $args \
      > "$OUT/${name}.rep${i}.out" 2> "$OUT/${name}.rep${i}.err"
    echo "$?" > "$OUT/${name}.rep${i}.rc"
    echo $(( ($(date +%s%N) - t0) / 1000000 )) > "$OUT/${name}.rep${i}.wall_ms"
  done
  note "$name reps=$REPS rc=[$(cat "$OUT/${name}".rep*.rc | tr '\n' ' ')] args='$args'"
}

for arm in cursorphase hoverphase dragphase coalesce velphase startup flushpos orderin dblclick; do
  run_one "r100b_${arm}" "res://r100b_phase.gd" "--arm=${arm}"
done
run_one "r100b_seq_noclean" "res://r100b_seq.gd" "--clean=0"
run_one "r100b_seq_clean" "res://r100b_seq.gd" "--clean=1"

note "finished=$(date -u +%Y-%m-%dT%H:%M:%SZ) load=$(cut -d' ' -f1-3 /proc/loadavg)"
own_hogs=$(printf '%s' "$HOG_PIDS" | wc -w)
stop_load
host_yes_after=$(pgrep -fc '^yes$' 2>/dev/null || echo 0)
note "own_hogs_started=$own_hogs host_yes_after=$host_yes_after"
echo "--- probes $BATCH done; rc summary tail:"
tail -3 "$OUT/rc-summary.txt"
echo "--- timeout check (rc=137): $(grep -rl 137 "$OUT"/*.rc 2>/dev/null | wc -l)"
echo "--- stray r100b probes: $(pgrep -fc 'r100b_' || true)"
