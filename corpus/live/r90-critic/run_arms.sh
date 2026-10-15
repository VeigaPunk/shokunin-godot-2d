#!/usr/bin/env bash
# r90-critic: run one rb_lattice arm N times in the battery's exact launch shape.
# usage: run_arms.sh <proj-dir> <tag> <reps> [extra-godot-flags...] -- <arms...>
# battery shape: godot --headless --path <proj> --script res://rb_lattice.gd -- <flags>
set -u
PROJ="$1"; TAG="$2"; REPS="$3"; shift 3
EXTRA=()
while [ "$1" != "--" ]; do EXTRA+=("$1"); shift; done
shift
cd "$(dirname "$0")"
mkdir -p runs
for arm in "$@"; do
  case "$arm" in
    freezelock) FLAGS=(--arm=freezelock --frames=120) ;;
    lag)        FLAGS=(--arm=lag --frames=30) ;;
    *)          FLAGS=(--arm="$arm") ;;
  esac
  for r in $(seq 1 "$REPS"); do
    base="runs/${TAG}.${arm}.rep${r}"
    timeout -s KILL 15 godot --headless --path "$PROJ" ${EXTRA[@]+"${EXTRA[@]}"} \
      --script res://rb_lattice.gd -- "${FLAGS[@]}" \
      > "${base}.out" 2> "${base}.err"
    echo $? > "${base}.rc"
  done
done
