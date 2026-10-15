#!/usr/bin/env bash
# r91-critic: run nav_lattice arms in the battery's exact launch shape.
# usage: run_arms.sh <proj-dir> <tag> <reps> [extra-godot-flags...] -- <arms...>
# battery shape: godot --headless --path <proj> --script res://nav_lattice.gd -- --arm=<a>
set -u
PROJ="$1"; TAG="$2"; REPS="$3"; shift 3
EXTRA=()
while [ "$1" != "--" ]; do EXTRA+=("$1"); shift; done
shift
cd "$(dirname "$0")/.."
mkdir -p runs
for arm in "$@"; do
  for r in $(seq 1 "$REPS"); do
    base="runs/${TAG}.${arm}.rep${r}"
    timeout -s KILL 25 godot --headless --path "$PROJ" ${EXTRA[@]+"${EXTRA[@]}"} \
      --script res://nav_lattice.gd -- "--arm=${arm}" \
      > "${base}.out" 2> "${base}.err"
    echo $? > "${base}.rc"
  done
done
