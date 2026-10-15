#!/usr/bin/env bash
# r97-scout driver — SceneTree groups / signal connect flags / call_deferred ladder.
# Battery launch shape:
#   godot --headless --path proj --script res://stree_lattice.gd -- --arm=<arm> [--rev]
# bounded by `timeout -s KILL`; stdout/stderr split into per-cell sidecars plus .rc.
# Reps: 3 per pure/static cell, 6 per frame-bound (await) cell.
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-30}
mkdir -p runs
cp -f probes/stree_lattice.gd proj/

run_cell() { # name arm reps extra
  local name="$1" arm="$2" reps="$3" extra="${4:-}" i
  for i in $(seq 1 "$reps"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://stree_lattice.gd -- \
      "--arm=$arm" $extra > "runs/r97_$name.rep$i.out" 2> "runs/r97_$name.rep$i.err"
    echo "$?" > "runs/r97_$name.rep$i.rc"
  done
}

: > runs/rc-summary.txt
note() { printf '%s\n' "$1" >> runs/rc-summary.txt; }

note "godot=$(timeout 20 "$GODOT" --version 2>&1 | tail -1)  bound_s=$BOUND  started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# pure / static cells: 3 reps
run_cell census census 3
run_cell group_order group_order 3
run_cell group_order_rev group_order 3 --rev
run_cell group_flags group_flags 3
run_cell group_lifecycle group_lifecycle 3
run_cell group_setters group_setters 3
run_cell signal_order signal_order 3
run_cell signal_flags signal_flags 3

# frame-bound cells (await process_frame / deferred flush): 6 reps
run_cell defer_ladder defer_ladder 6
run_cell defer_slots defer_slots 6
run_cell defer_order defer_order 6
run_cell scene_probe scene_probe 6

for f in runs/r97_*.rep*.rc; do
  printf '%s %s\n' "$(cat "$f")" "$f" >> runs/rc-summary.txt
done
note "finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "done: $(ls runs/r97_*.rep*.out | wc -l) receipts"
