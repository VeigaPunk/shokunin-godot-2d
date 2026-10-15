#!/usr/bin/env bash
# r97-boundary mode driver — run the r97b attack arms AND the frozen r97-scout
# cells under one host mode.  Every launch is `timeout -s KILL`-bounded (25 s,
# the seat's bound) and stdout/stderr/rc are split into per-cell sidecars.
#
#   bash run_modes.sh <mode> [reps]
#     mode: quiet | load | ff30 | ff60 | ff120 | ff1
#   `load` starts 12 own `yes` hogs (task floor), tracks their PIDs and kills
#   exactly those PIDs at the end (never pkill / never another lane's hogs).
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-25}
MODE=${1:?usage: run_modes.sh <mode> [reps]}
REPS=${2:-3}
case "$MODE" in
  quiet) EXTRA="" ;;
  load)  EXTRA="" ;;
  ff30)  EXTRA="--fixed-fps 30" ;;
  ff60)  EXTRA="--fixed-fps 60" ;;
  ff120) EXTRA="--fixed-fps 120" ;;
  ff1)   EXTRA="--fixed-fps 1" ;;
  *) echo "unknown mode $MODE"; exit 2 ;;
esac
mkdir -p "runs/$MODE"
cp -f probes/r97b_lattice.gd proj/
cp -f ../r97-scout/probes/stree_lattice.gd proj/

HOG_PIDS=()
HOGFILE="runs/$MODE/hogs.txt"
{
  echo "mode=$MODE extra=[$EXTRA] reps=$REPS bound=$BOUND"
  echo "godot=$(timeout 20 "$GODOT" --version 2>&1 | tail -1)"
  echo "loadavg_start=$(cut -d' ' -f1-3 /proc/loadavg)"
} > "$HOGFILE"

if [ "$MODE" = "load" ]; then
  for i in $(seq 1 12); do
    yes > /dev/null &
    HOG_PIDS+=("$!")
  done
  echo "own_hogs=${#HOG_PIDS[@]} pids=${HOG_PIDS[*]}" >> "$HOGFILE"
fi

run_cell() { # tag script arm reps extra
  local tag="$1" script="$2" arm="$3" reps="$4" extra="${5:-}" i
  for i in $(seq 1 "$reps"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless $EXTRA --path proj --script "res://$script" -- \
      "--arm=$arm" $extra > "runs/$MODE/${tag}.rep$i.out" 2> "runs/$MODE/${tag}.rep$i.err"
    echo "$?" > "runs/$MODE/${tag}.rep$i.rc"
    printf 'loadavg=%s cell=%s rep=%s rc=%s\n' "$(cut -d' ' -f1-3 /proc/loadavg)" "$tag" "$i" \
      "$(cat "runs/$MODE/${tag}.rep$i.rc")" >> "$HOGFILE"
  done
}

# ---- own attack arms (r97b_*)
run_cell r97b_order_ticks r97b_lattice.gd order_ticks "$REPS"
run_cell r97b_order_priority r97b_lattice.gd order_priority "$REPS"
run_cell r97b_defer_capture_order r97b_lattice.gd defer_capture_order "$REPS"
run_cell r97b_defer_phase r97b_lattice.gd defer_phase "$REPS"
run_cell r97b_frame_shape r97b_lattice.gd frame_shape "$REPS"
run_cell r97b_phys_await r97b_lattice.gd phys_await "$REPS"

# ---- frozen r97-scout cells (replication under this mode)
run_cell scout_census stree_lattice.gd census "$REPS"
run_cell scout_group_order stree_lattice.gd group_order "$REPS"
run_cell scout_group_order_rev stree_lattice.gd group_order "$REPS" "--rev"
run_cell scout_group_flags stree_lattice.gd group_flags "$REPS"
run_cell scout_group_lifecycle stree_lattice.gd group_lifecycle "$REPS"
run_cell scout_group_setters stree_lattice.gd group_setters "$REPS"
run_cell scout_signal_order stree_lattice.gd signal_order "$REPS"
run_cell scout_signal_flags stree_lattice.gd signal_flags "$REPS"
run_cell scout_defer_ladder stree_lattice.gd defer_ladder "$REPS"
run_cell scout_defer_slots stree_lattice.gd defer_slots "$REPS"
run_cell scout_defer_order stree_lattice.gd defer_order "$REPS"
run_cell scout_scene_probe stree_lattice.gd scene_probe "$REPS"

if [ "$MODE" = "load" ]; then
  killed=0
  for pid in "${HOG_PIDS[@]}"; do
    if kill "$pid" 2>/dev/null; then killed=$((killed + 1)); fi
  done
  echo "own_hogs_killed=$killed" >> "$HOGFILE"
  echo "host_yes_remaining=$(pgrep -c '^yes$' || true)" >> "$HOGFILE"
fi
echo "loadavg_end=$(cut -d' ' -f1-3 /proc/loadavg)" >> "$HOGFILE"
echo "mode=$MODE done: $(ls runs/$MODE/*.rep*.out 2>/dev/null | wc -l) receipts"
