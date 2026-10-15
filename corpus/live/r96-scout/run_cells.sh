#!/usr/bin/env bash
# r96-scout canonical driver — PackedScene/ResourceSaver/ResourceLoader round-trip lattice.
# Battery launch shape:
#   godot --headless --path proj --script res://scene_io_lattice.gd -- --arm=<arm>
# bounded by `timeout -s KILL`; stdout/stderr split into per-cell sidecars plus .rc.
# Reps: 3 per pure/static cell (census), 6 per runtime cell.
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-30}
mkdir -p runs
cp -f probes/scene_io_lattice.gd proj/

run_cell() { # name arm reps
  local name="$1" arm="$2" reps="$3" i
  for i in $(seq 1 "$reps"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://scene_io_lattice.gd -- \
      "--arm=$arm" > "runs/r96_$name.rep$i.out" 2> "runs/r96_$name.rep$i.err"
    echo "$?" > "runs/r96_$name.rep$i.rc"
  done
}

: > runs/rc-summary.txt
note() { printf '%s\n' "$1" >> runs/rc-summary.txt; }

note "godot=$(timeout 20 "$GODOT" --version 2>&1 | tail -1)  bound_s=$BOUND  started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

for spec in "census census 3" "pack_basic pack_basic 6" "ownership ownership 6" \
            "formats formats 6" "det det 6" "uid uid 6" "takeover takeover 6" \
            "cache cache 6" "subres subres 6" "extres extres 6" \
            "editstate editstate 6" "refuse refuse 6" "edges edges 6"; do
  set -- $spec
  name="$1"; arm="$2"; reps="$3"
  run_cell "$name" "$arm" "$reps"
  note "$name arm=$arm reps=$reps rc=[$(cat runs/r96_$name.rep*.rc | tr '\n' ' ')]"
done

note "finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat runs/rc-summary.txt
echo "--- stray godot check (may include other lanes) ---"
pgrep -fa "scene_io_lattice" || echo "none"
