#!/usr/bin/env bash
# r99-boundary causal control — `--fixed-fps 30 --frame-delay 100`.
# Keeps the unpaced `--fixed-fps` startup mode but makes each process frame cost
# ~100 ms wall, so the frozen probe's `frames < cap` bound stops binding and its
# wall-time windows (300-400 ms) are restored. If the pinned prefixes come back,
# the ff30/60/120 rejections are attributable to the frame-cap truncation.
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-60}
REPS="${1:-2}"
CELLS="census bus autoplay stoppos peak_calib mixblock advance finish loop_degenerate loop_pts gen gen_peak poly bus_peak p2d pan_law gen2d pause"
mkdir -p runs/ff30slow
cp -f probes/audio_lattice.gd proj/audio_lattice.gd
: > runs/ff30slow/rc-summary.txt
printf 'mode=ff30slow flags=[--fixed-fps 30 --frame-delay 100] reps=%s load=%s started=%s\n' \
  "$REPS" "$(cut -d' ' -f1-3 /proc/loadavg)" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> runs/ff30slow/rc-summary.txt
for cell in $CELLS; do
  for i in $(seq 1 "$REPS"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless --fixed-fps 30 --frame-delay 100 --path proj \
      --script res://audio_lattice.gd -- "--arm=$cell" \
      > "runs/ff30slow/r99b_${cell}.rep$i.out" 2> "runs/ff30slow/r99b_${cell}.rep$i.err"
    echo "$?" > "runs/ff30slow/r99b_${cell}.rep$i.rc"
  done
  printf '%s rc=[%s]\n' "$cell" "$(cat runs/ff30slow/r99b_${cell}.rep*.rc | tr '\n' ' ')" >> runs/ff30slow/rc-summary.txt
done
printf 'finished=%s load=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(cut -d' ' -f1-3 /proc/loadavg)" >> runs/ff30slow/rc-summary.txt
cat runs/ff30slow/rc-summary.txt
