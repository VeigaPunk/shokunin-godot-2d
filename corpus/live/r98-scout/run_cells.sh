#!/usr/bin/env bash
# r98-scout driver — CanvasItem draw/transform lattice (15 cells).
# Battery launch shape:
#   godot --headless --path proj --script res://canvas_lattice.gd -- --arm=<arm>
# bounded by `timeout -s KILL`; stdout/stderr split into per-cell sidecars plus .rc.
# Reps: 3 per pure/static cell, 6 per frame-bound cell (REPS env override).
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-30}
REPS=${REPS:-0}
mkdir -p runs
cp -f probes/canvas_lattice.gd proj/

run_cell() { # name arm reps
  local name="$1" arm="$2" reps="$3" i
  if [ "$REPS" != "0" ]; then reps="$REPS"; fi
  for i in $(seq 1 "$reps"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://canvas_lattice.gd -- \
      "--arm=$arm" > "runs/r98_canvas_$name.rep$i.out" 2> "runs/r98_canvas_$name.rep$i.err"
    echo "$?" > "runs/r98_canvas_$name.rep$i.rc"
  done
}

: > runs/rc-summary.txt
note() { printf '%s\n' "$1" >> runs/rc-summary.txt; }

note "godot=$(timeout 20 "$GODOT" --version 2>&1 | tail -1)  bound_s=$BOUND  reps_override=$REPS  started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

for spec in "census census 3" "modulate modulate 3" \
            "queue queue 6" "draw_surface draw_surface 6" "draw_refusal draw_refusal 6" \
            "vis_chain vis_chain 6" "clip clip 6" "zorder zorder 6" \
            "xform_skew xform_skew 6" "xform_mirror xform_mirror 6" "xform_global xform_global 6" \
            "notify notify 6" "draw_state draw_state 6" "redraw_triggers redraw_triggers 6" \
            "redraw_context redraw_context 6"; do
  set -- $spec
  run_cell "$1" "$2" "$3"
  note "$1 arm=$2 reps=$3 rc=[$(cat runs/r98_canvas_$1.rep*.rc | tr '\n' ' ')]"
done

note "finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat runs/rc-summary.txt
echo "--- stray godot check (may include other lanes) ---"
pgrep -fa "canvas_lattice" || echo "none"
