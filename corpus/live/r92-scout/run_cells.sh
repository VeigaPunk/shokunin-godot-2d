#!/usr/bin/env bash
# r92-scout driver — TileMapLayer/TileSet authorability lattice.
# Battery launch shape:
#   godot --headless --path proj --script res://tilemap_lattice.gd -- --arm=<arm>
# bounded by `timeout -s KILL`; stdout/stderr split into per-cell sidecars plus .rc.
# Reps: 3 per pure/data cell, 6 per physics-await cell.
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-30}
mkdir -p runs
cp -f probes/*.gd proj/

run_cell() { # name arm reps
  local name="$1" arm="$2" reps="$3" i
  for i in $(seq 1 "$reps"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://tilemap_lattice.gd -- \
      "--arm=$arm" > "runs/r92_$name.rep$i.out" 2> "runs/r92_$name.rep$i.err"
    echo "$?" > "runs/r92_$name.rep$i.rc"
  done
}

: > runs/rc-summary.txt
note() { printf '%s\n' "$1" >> runs/rc-summary.txt; }

note "godot=$(timeout 20 "$GODOT" --version 2>&1 | tail -1)  bound_s=$BOUND  started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

for spec in "tm_census census 3" "tm_atlas atlas 3" "tm_cells cells 3" \
            "tm_custom custom 3" "tm_terrain terrain 3" "tm_pattern pattern 3" \
            "tm_encoding encoding 3" "tm_fixinvalid fixinvalid 3" "tm_srcids srcids 3" \
            "tm_physics physics 6" "tm_timing timing 6" "tm_quadrant quadrant 6" \
            "tm_nav nav 6"; do
  set -- $spec
  run_cell "$1" "$2" "$3"
  note "$1 arm=$2 reps=$3 rc=[$(cat runs/r92_$1.rep*.rc | tr '\n' ' ')]"
done

note "finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat runs/rc-summary.txt
echo "--- stray godot check (may include other lanes) ---"
pgrep -fa "godot" || echo "none"
