#!/usr/bin/env bash
# r94-critic arm driver: timeout-bounded fresh-process launches.
# usage: run_arms.sh <batch> <proj_dir> <reps> [extra godot flags...]
set -u
BATCH="$1"; PROJ="$2"; REPS="$3"; shift 3
OUT="$(cd "$(dirname "$0")/.." && pwd)/runs/$BATCH"
mkdir -p "$OUT"
ARMS="census ppm convert cpu_lifetime cpu_expl cpu_speed_pre cpu_stop cpu_never cpu_contam cpu_oneshot_off cpu_oneshot_flag cpu_pause cpu_restart cpu_retrigger cpu_lt_mid cpu_speed_mid cpu_amount_mid cpu_request gpu_headless"
echo "batch=$BATCH proj=$PROJ reps=$REPS flags=$* start=$(date -u +%Y-%m-%dT%H:%M:%SZ) loadavg=$(cut -d' ' -f1-3 /proc/loadavg)"
for rep in $(seq 1 "$REPS"); do
  for arm in $ARMS; do
    f="$OUT/$arm.rep$rep"
    s=$(date +%s.%N)
    timeout -s KILL 25 godot --headless --path "$PROJ" --script res://particles_lattice.gd "$@" -- --arm="$arm" \
      > "$f.out" 2> "$f.err"; rc=$?
    e=$(date +%s.%N)
    echo "$rc" > "$f.rc"
    echo "$s $e" | awk '{printf "%.3f\n", $2-$1}' > "$f.wall"
  done
  echo "rep$rep done $(date -u +%Y-%m-%dT%H:%M:%SZ) loadavg=$(cut -d' ' -f1-3 /proc/loadavg)"
done
echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ) loadavg=$(cut -d' ' -f1-3 /proc/loadavg)"
