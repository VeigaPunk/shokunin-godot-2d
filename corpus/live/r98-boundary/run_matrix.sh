#!/usr/bin/env bash
# r98b boundary driver — attacks the r98 scout's CanvasItem claims
# (queue_redraw flush L1, skew decomposition L3/L4/L5, clip refusal L9) under
# quiet / 16-hog load / --fixed-fps 1|30|120 / ff30+load.
#
#   bash run_matrix.sh quiet|load|ff1|ff30|ff120|ff30load
#
# Two probes per batch:
#   - scout_canvas_lattice.gd  (BYTE-COPY of the scout's frozen probe; PASS tag
#     `canvas_lattice`, so every payload is directly comparable with the scout's
#     canonical + loadtest receipts)
#   - r98b_attack.gd           (this seat's unstated-mode attack probe)
#
# Every run is `timeout -s KILL 25`-bounded; stdout/stderr split into per-cell
# sidecars plus .rc and .wall_ms. Hogs are this seat's own only and are killed
# by the EXIT trap (never pkill: other lanes run their own `yes` blocks).
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
  ff120) FF="--fixed-fps 120" ;;
  ff30load) FF="--fixed-fps 30" ;;
  slow) FF="--frame-delay 100" ;;
  *) echo "unknown batch: $BATCH" >&2; exit 2 ;;
esac
mkdir -p "runs/$BATCH"
cp -f probes/scout_canvas_lattice.gd "$PROJ"/canvas_lattice.gd
cp -f probes/r98b_attack.gd "$PROJ"/

HOG_PIDS=""
stop_load() {
  for p in $HOG_PIDS; do kill "$p" 2>/dev/null || true; done
  HOG_PIDS=""
}
trap 'stop_load' EXIT

if [ "$BATCH" = "load" ] || [ "$BATCH" = "ff30load" ]; then
  for i in $(seq 1 "$HOGS"); do yes > /dev/null & HOG_PIDS="$HOG_PIDS $!"; done
  sleep 2
fi

run_one() { # cell script reps args
  local cell="$1" script="$2" reps="$3" args="$4" i rc t0
  for i in $(seq 1 "$reps"); do
    t0=$(date +%s%N)
    # shellcheck disable=SC2086
    timeout -s KILL "$BOUND" "$GODOT" --headless $FF --path "$PROJ" --script "res://$script" -- $args \
      > "runs/$BATCH/$cell.rep$i.out" 2> "runs/$BATCH/$cell.rep$i.err"
    rc=$?
    echo "$rc" > "runs/$BATCH/$cell.rep$i.rc"
    echo $(( ($(date +%s%N) - t0) / 1000000 )) > "runs/$BATCH/$cell.rep$i.wall_ms"
  done
}

scout_cells() {
  local reps="$1"
  for spec in \
      "census|--arm=census" "queue|--arm=queue" "draw_surface|--arm=draw_surface" \
      "draw_refusal|--arm=draw_refusal" "vis_chain|--arm=vis_chain" "clip|--arm=clip" \
      "zorder|--arm=zorder" "modulate|--arm=modulate" "xform_skew|--arm=xform_skew" \
      "xform_mirror|--arm=xform_mirror" "xform_global|--arm=xform_global" \
      "notify|--arm=notify" "draw_state|--arm=draw_state" \
      "redraw_triggers|--arm=redraw_triggers" "redraw_context|--arm=redraw_context"; do
    run_one "r98_canvas_${spec%%|*}" canvas_lattice.gd "$reps" "${spec#*|}"
  done
}

attack_cells() {
  local reps="$1"
  for spec in \
      "qflush|--arm=qflush" "qorder|--arm=qorder" "gskew|--arm=gskew" \
      "skewgrid|--arm=skewgrid" "epssweep|--arm=epssweep" "clipmatrix|--arm=clipmatrix" \
      "notifyphase|--arm=notifyphase" "visphase|--arm=visphase" "env|--arm=env" \
      "latch_canon|--arm=latch --var=canon" "latch_t1|--arm=latch --var=t1" \
      "latch_t3|--arm=latch --var=t3" "latch_imm|--arm=latch --var=imm" \
      "latch_second|--arm=latch --var=second"; do
    run_one "r98b_${spec%%|*}" r98b_attack.gd "$reps" "${spec#*|}"
  done
}

SCOUT_REPS=2
ATK_REPS=2
case "$BATCH" in
  ff1|ff30|ff120|ff30load|slow) SCOUT_REPS=1; ATK_REPS=1 ;;
esac

: > "runs/$BATCH/rc-summary.txt"
note() { printf '%s\n' "$1" >> "runs/$BATCH/rc-summary.txt"; }
note "batch=$BATCH ff='${FF:-none}' hogs=${HOGS} bound=${BOUND} godot=$(timeout 20 "$GODOT" --version 2>&1 | tail -1)"
note "started=$(date -u +%Y-%m-%dT%H:%M:%SZ) load=$(cut -d' ' -f1-3 /proc/loadavg)"

scout_cells "$SCOUT_REPS"
attack_cells "$ATK_REPS"

note "finished=$(date -u +%Y-%m-%dT%H:%M:%SZ) load=$(cut -d' ' -f1-3 /proc/loadavg)"
for f in runs/$BATCH/*.rep1.rc; do
  cell=$(basename "$f" .rep1.rc)
  printf '%s rc=[%s]\n' "$cell" "$(cat runs/$BATCH/"$cell".rep*.rc | tr '\n' ' ')" >> "runs/$BATCH/rc-summary.txt"
done
stop_load
echo "--- $BATCH done; rc summary tail:"
tail -5 "runs/$BATCH/rc-summary.txt"
echo "--- timeout check (rc=137): $(grep -rl 137 runs/$BATCH/*.rc 2>/dev/null | wc -l)"
echo "--- stray probes: $(pgrep -fc 'canvas_lattice|r98b_attack' || true)"
