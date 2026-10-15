#!/usr/bin/env bash
# r99-boundary probe-arm driver — run the 8 r99b_modes arms under one startup mode.
#   bash run_probes.sh <mode> [reps]
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-45}
MODE="${1:-quiet}"
REPS="${2:-2}"
ARMS="modeinfo mixphase startphase peakphase mixfree finfree advfree splitcycle"
case "$MODE" in
  quiet)  FLAGS=""; PROJ=proj;;
  load)   FLAGS=""; PROJ=proj;;
  ff30)   FLAGS="--fixed-fps 30"; PROJ=proj;;
  ff60)   FLAGS="--fixed-fps 60"; PROJ=proj;;
  ff120)  FLAGS="--fixed-fps 120"; PROJ=proj;;
  ff1)    FLAGS="--fixed-fps 1"; PROJ=proj;;
  maxfps30)  FLAGS="--max-fps 30"; PROJ=proj;;
  maxfps60)  FLAGS="--max-fps 60"; PROJ=proj;;
  maxfps120) FLAGS="--max-fps 120"; PROJ=proj;;
  single) FLAGS="--single-threaded-scene"; PROJ=proj;;
  proj2d) FLAGS=""; PROJ=proj2d;;
  *) echo "unknown mode: $MODE" >&2; exit 2;;
esac
mkdir -p "runs/$MODE"
cp -f probes/r99b_modes.gd "$PROJ/r99b_modes.gd"
: > "runs/$MODE/probe-summary.txt"
printf 'mode=%s flags=[%s] proj=%s reps=%s load=%s started=%s\n' \
  "$MODE" "$FLAGS" "$PROJ" "$REPS" "$(cut -d' ' -f1-3 /proc/loadavg)" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  >> "runs/$MODE/probe-summary.txt"
for arm in $ARMS; do
  for i in $(seq 1 "$REPS"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless $FLAGS --path "$PROJ" --script res://r99b_modes.gd -- \
      "--arm=$arm" > "runs/$MODE/r99b_probe_${arm}.rep$i.out" 2> "runs/$MODE/r99b_probe_${arm}.rep$i.err"
    echo "$?" > "runs/$MODE/r99b_probe_${arm}.rep$i.rc"
  done
  printf '%s rc=[%s]\n' "$arm" "$(cat runs/$MODE/r99b_probe_${arm}.rep*.rc | tr '\n' ' ')" >> "runs/$MODE/probe-summary.txt"
done
printf 'finished=%s load=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(cut -d' ' -f1-3 /proc/loadavg)" >> "runs/$MODE/probe-summary.txt"
cat "runs/$MODE/probe-summary.txt"
