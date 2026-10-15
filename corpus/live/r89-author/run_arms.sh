#!/usr/bin/env bash
# r89-author fresh-rep byte verification — runs every authored arm N times
# in the battery's exact launch shape:
#   timeout -s KILL 25 godot --headless --path proj --script res://<probe> -- --arm=<a>
# Receipts: runs/<cell>.rep<k>.{out,err,rc}
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
PROJ="$HERE/proj"
RUNS="$HERE/runs"
N="${1:-6}"
mkdir -p "$RUNS"

GEO_ARMS="census ops contain joins trig pred pipedges edge offempty offdeg atlasempty polyendpoly bridge ring ring2 ring4 ringhits lineempty"
IN_ARMS="exact axisdev"

for arm in $GEO_ARMS; do
  for k in $(seq 1 "$N"); do
    base="$RUNS/geo_${arm}.rep${k}"
    timeout -s KILL 25 godot --headless --path "$PROJ" --script res://geo2d_lattice.gd -- --arm="$arm" \
      > "$base.out" 2> "$base.err"
    echo $? > "$base.rc"
  done
done
for arm in $IN_ARMS; do
  for k in $(seq 1 "$N"); do
    base="$RUNS/in_${arm}.rep${k}"
    timeout -s KILL 25 godot --headless --path "$PROJ" --script res://input89_edges.gd -- --arm="$arm" \
      > "$base.out" 2> "$base.err"
    echo $? > "$base.rc"
  done
done
echo "DONE $N reps x 20 arms -> $RUNS"
