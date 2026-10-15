#!/usr/bin/env bash
# r90-reviewer fresh-rep verification — battery launch shape:
#   timeout -s KILL 25 godot --headless --path <proj> --script res://rb_lattice.gd -- --arm=<a> [--frames=N]
# Receipts: runs/<cell>.rep<k>.{out,err,rc}
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
PROJ="${PROJ:-$HERE/proj}"
RUNS="${RUNS:-$HERE/runs}"
N="${N:-3}"
mkdir -p "$RUNS"

ARMS="props comread comrefuse gravity damp order write impulse impedge lag contacts"

for arm in $ARMS; do
  extra=()
  [ "$arm" = "lag" ] && extra=(--frames=30)
  for k in $(seq 1 "$N"); do
    base="$RUNS/${arm}.rep${k}"
    timeout -s KILL 25 godot --headless --path "$PROJ" --script res://rb_lattice.gd -- --arm="$arm" "${extra[@]}" \
      > "$base.out" 2> "$base.err"
    echo $? > "$base.rc"
  done
done
for k in $(seq 1 "$N"); do
  base="$RUNS/freezelock.rep${k}"
  timeout -s KILL 25 godot --headless --path "$PROJ" --script res://rb_lattice.gd -- --arm=freezelock --frames=120 \
    > "$base.out" 2> "$base.err"
  echo $? > "$base.rc"
done
echo "DONE $N reps x 12 arms -> $RUNS (proj=$PROJ)"
