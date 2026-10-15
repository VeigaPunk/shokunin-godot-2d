#!/usr/bin/env bash
# r98-scout loadtest driver — all 15 cells x 3 reps under deliberate load.
# Only this seat's own hog PIDs are killed (never pkill/pgrep-kill of host hogs).
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-30}
HOGS=${HOGS:-8}
REPS=${REPS:-3}
mkdir -p runs/loadtest
cp -f probes/canvas_lattice.gd proj/

HOG_PIDS=()
for i in $(seq 1 "$HOGS"); do
  yes > /dev/null 2>&1 &
  HOG_PIDS+=("$!")
done

run_cell() { # name arm reps
  local name="$1" arm="$2" reps="$3" i
  for i in $(seq 1 "$reps"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://canvas_lattice.gd -- \
      "--arm=$arm" > "runs/loadtest/r98_canvas_$name.rep$i.out" 2> "runs/loadtest/r98_canvas_$name.rep$i.err"
    echo "$?" > "runs/loadtest/r98_canvas_$name.rep$i.rc"
  done
}

: > runs/loadtest/rc-summary.txt
note() { printf '%s\n' "$1" >> runs/loadtest/rc-summary.txt; }
note "godot=$(timeout 20 "$GODOT" --version 2>&1 | tail -1)  hogs=$HOGS  bound_s=$BOUND  started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

for spec in "census census" "modulate modulate" \
            "queue queue" "draw_surface draw_surface" "draw_refusal draw_refusal" \
            "vis_chain vis_chain" "clip clip" "zorder zorder" \
            "xform_skew xform_skew" "xform_mirror xform_mirror" "xform_global xform_global" \
            "notify notify" "draw_state draw_state" "redraw_triggers redraw_triggers" \
            "redraw_context redraw_context"; do
  set -- $spec
  note "$1 loadavg_before=$(cut -d' ' -f1 /proc/loadavg) rc_before=[$(cat runs/loadtest/r98_canvas_$1.rep*.rc 2>/dev/null | tr '\n' ' ')]"
  run_cell "$1" "$2" "$REPS"
  note "$1 reps=$REPS rc=[$(cat runs/loadtest/r98_canvas_$1.rep*.rc | tr '\n' ' ')] loadavg_after=$(cut -d' ' -f1 /proc/loadavg)"
done

own_hogs_killed=0
for pid in "${HOG_PIDS[@]}"; do
  if kill "$pid" 2>/dev/null; then own_hogs_killed=$((own_hogs_killed + 1)); fi
done
note "own_hogs_killed=$own_hogs_killed"
note "host_yes_remaining=$(pgrep -cx yes || true)"
note "finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat runs/loadtest/rc-summary.txt
echo "--- stray canvas_lattice check ---"
pgrep -fa "canvas_lattice" || echo "none"
