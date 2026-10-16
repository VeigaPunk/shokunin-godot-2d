#!/usr/bin/env bash
# r94-critic single-arm mutant driver.
# usage: run_one.sh <batch> <proj_dir> <arm> <reps> [extra godot flags...]
set -u
BATCH="$1"; PROJ="$2"; ARM="$3"; REPS="$4"; shift 4
OUT="$(cd "$(dirname "$0")/.." && pwd)/runs/$BATCH"
mkdir -p "$OUT"
echo "batch=$BATCH arm=$ARM proj=$PROJ reps=$REPS flags=$* start=$(date -u +%Y-%m-%dT%H:%M:%SZ) loadavg=$(cut -d' ' -f1-3 /proc/loadavg)"
for rep in $(seq 1 "$REPS"); do
  f="$OUT/$ARM.rep$rep"
  s=$(date +%s.%N)
  timeout -s KILL 25 godot --headless --path "$PROJ" --script res://particles_lattice.gd "$@" -- --arm="$ARM" \
    > "$f.out" 2> "$f.err"; rc=$?
  e=$(date +%s.%N)
  echo "$rc" > "$f.rc"
  echo "$s $e" | awk '{printf "%.3f\n", $2-$1}' > "$f.wall"
done
echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ) loadavg=$(cut -d' ' -f1-3 /proc/loadavg)"
