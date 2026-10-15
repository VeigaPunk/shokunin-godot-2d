#!/usr/bin/env bash
# r91-scout driver — Navigation2D authorability lattice (NavigationServer2D /
# NavigationRegion2D / NavigationAgent2D / NavigationPolygon / links / avoidance).
# Battery launch shape:
#   godot --headless --path proj --script res://nav_lattice.gd -- --arm=<arm>
# bounded by `timeout -s KILL`; stdout/stderr split into per-cell sidecars plus .rc.
# Reps: 3 per pure/static cell, 6 per sync/await/lifecycle cell.
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-30}
mkdir -p runs
cp -f probes/*.gd proj/

run_cell() { # name arm reps
  local name="$1" arm="$2" reps="$3" i
  for i in $(seq 1 "$reps"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://nav_lattice.gd -- \
      "--arm=$arm" > "runs/r91_$name.rep$i.out" 2> "runs/r91_$name.rep$i.err"
    echo "$?" > "runs/r91_$name.rep$i.rc"
  done
}

: > runs/rc-summary.txt
note() { printf '%s\n' "$1" >> runs/rc-summary.txt; }

note "godot=$(timeout 20 "$GODOT" --version 2>&1 | tail -1)  bound_s=$BOUND  started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

for spec in "nav_census census 3" "nav_path path 3" "nav_query query 3" \
            "nav_sync sync 6" "nav_region region 6" "nav_agent agent 6" \
            "nav_avoid avoid 6" "nav_bake bake 6" "nav_link link 6"; do
  set -- $spec
  run_cell "$1" "$2" "$3"
  note "$1 arm=$2 reps=$3 rc=[$(cat runs/r91_$1.rep*.rc | tr '\n' ' ')]"
done

note "finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat runs/rc-summary.txt
echo "--- stray godot check (may include other lanes) ---"
pgrep -fa "godot" || echo "none"
