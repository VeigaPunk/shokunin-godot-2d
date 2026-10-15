#!/usr/bin/env bash
# r99-scout driver — in-engine audio surface under --headless (Dummy driver).
# Battery launch shape:
#   godot --headless --path proj --script res://audio_lattice.gd -- --arm=<arm>
# bounded by `timeout -s KILL`; stdout/stderr split into per-cell sidecars plus .rc.
# Reps: 3 per pure/readback cell, 6 per frame/block-bound cell.
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-40}
mkdir -p runs
cp -f probes/audio_lattice.gd proj/

run_cell() { # name arm reps
  local name="$1" arm="$2" reps="$3" i
  for i in $(seq 1 "$reps"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://audio_lattice.gd -- \
      "--arm=$arm" > "runs/r99_$name.rep$i.out" 2> "runs/r99_$name.rep$i.err"
    echo "$?" > "runs/r99_$name.rep$i.rc"
  done
}

: > runs/rc-summary.txt
note() { printf '%s\n' "$1" >> runs/rc-summary.txt; }

note "godot=$(timeout 20 "$GODOT" --version 2>&1 | tail -1)  bound_s=$BOUND  started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

for spec in "census census 3" "bus bus 3" "autoplay autoplay 3" "stoppos stoppos 3" \
            "peak_calib peak_calib 3" \
            "mixblock mixblock 6" "advance advance 6" "finish finish 6" \
            "loop_degenerate loop_degenerate 6" "loop_pts loop_pts 6" \
            "gen gen 6" "gen_peak gen_peak 6" "poly poly 6" "bus_peak bus_peak 6" \
            "p2d p2d 6" "pan_law pan_law 6" "gen2d gen2d 6" "pause pause 6"; do
  set -- $spec
  name="$1"; arm="$2"; reps="$3"
  run_cell "$name" "$arm" "$reps"
  note "$name arm=$arm reps=$reps rc=[$(cat runs/r99_$name.rep*.rc | tr '\n' ' ')]"
done

note "finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat runs/rc-summary.txt
echo "--- stray godot check (may include other lanes) ---"
pgrep -fa "audio_lattice" || echo "none"
