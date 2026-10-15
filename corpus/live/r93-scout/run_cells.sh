#!/usr/bin/env bash
# r93-scout driver — AnimationPlayer + Tween authorability lattice.
# Battery launch shape:
#   godot --headless --path proj --script res://anim_lattice.gd -- --arm=<arm>
# bounded by `timeout -s KILL`; stdout/stderr split into per-cell sidecars plus .rc.
# Reps: 3 per pure/static cell, 6 per runtime/lifecycle cell.
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-30}
mkdir -p runs
cp -f probes/anim_lattice.gd proj/

run_cell() { # name arm reps
  local name="$1" arm="$2" reps="$3" i
  for i in $(seq 1 "$reps"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://anim_lattice.gd -- \
      "--arm=$arm" > "runs/r93_$name.rep$i.out" 2> "runs/r93_$name.rep$i.err"
    echo "$?" > "runs/r93_$name.rep$i.rc"
  done
}

: > runs/rc-summary.txt
note() { printf '%s\n' "$1" >> runs/rc-summary.txt; }

note "godot=$(timeout 20 "$GODOT" --version 2>&1 | tail -1)  bound_s=$BOUND  started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

for spec in "census census 3" "tweenval tweenval 3" "tweenval_grid tweenval_grid 3" "animtrack animtrack 3" \
            "tweenstep tweenstep 6" "tweenchain tweenchain 6" "tweenproc tweenproc 6" "animseek animseek 6" \
            "animmethod animmethod 6" "animblend animblend 6" "animproc animproc 6"; do
  set -- $spec
  run_cell "$1" "$2" "$3"
  note "$1 arm=$2 reps=$3 rc=[$(cat runs/r93_$1.rep*.rc | tr '\n' ' ')]"
done

note "finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat runs/rc-summary.txt
echo "--- stray godot check (may include other lanes) ---"
pgrep -fa "godot" || echo "none"
