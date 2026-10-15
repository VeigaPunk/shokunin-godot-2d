#!/usr/bin/env bash
# r99-boundary r88-repro batch — the scout's causal-repro probe re-run across modes.
# The repro is the scout's own file, copied byte-identical from
# corpus/live/r99-scout/proj/r88_audio_repro.gd (sha recorded in the report).
# Launch shape is the scout's: --arm <name> (space-separated), no battery convention.
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-45}
MODE="${1:-quiet}"
REPS="${2:-2}"
case "$MODE" in
  quiet) FLAGS="";;
  ff30)  FLAGS="--fixed-fps 30";;
  ff120) FLAGS="--fixed-fps 120";;
  maxfps30) FLAGS="--max-fps 30";;
  *) echo "unknown mode: $MODE" >&2; exit 2;;
esac
mkdir -p "runs/$MODE"
cp -f "$(dirname "$0")/../r99-scout/proj/r88_audio_repro.gd" "proj/r88_audio_repro.gd"
printf 'mode=%s flags=[%s] load=%s started=%s\n' "$MODE" "$FLAGS" \
  "$(cut -d' ' -f1-3 /proc/loadavg)" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  >> "runs/$MODE/r88-summary.txt"
for variant in verbatim fixloop; do
  extra=""
  [ "$variant" = "fixloop" ] && extra="--fix-loop"
  for i in $(seq 1 "$REPS"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless $FLAGS --path proj --arm audio_pos \
      --script res://r88_audio_repro.gd -- $extra > "runs/$MODE/r99b_r88_${variant}.rep$i.out" 2> "runs/$MODE/r99b_r88_${variant}.rep$i.err"
    echo "$?" > "runs/$MODE/r99b_r88_${variant}.rep$i.rc"
  done
  printf '%s rc=[%s]\n' "$variant" "$(cat runs/$MODE/r99b_r88_${variant}.rep*.rc | tr '\n' ' ')" >> "runs/$MODE/r88-summary.txt"
done
printf 'finished=%s load=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(cut -d' ' -f1-3 /proc/loadavg)" \
  >> "runs/$MODE/r88-summary.txt"
cat "runs/$MODE/r88-summary.txt"
