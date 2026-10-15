#!/usr/bin/env bash
# r99-boundary driver — replay the frozen 18-cell r99 audio lattice across startup modes.
#
#   bash run_matrix.sh <mode> [reps]
#
# modes: quiet | load | ff30 | ff60 | ff120 | ff1 | single | proj2d
#   quiet   no seat hogs (the host still carries other lanes' load — recorded)
#   load    + 16 own `yes` hogs (task floor >=12), killed by PID only
#   ffN     --fixed-fps N
#   single  --single-threaded-scene (scene-thread startup mode)
#   proj2d  physics/2d/run_on_separate_thread=true project (threaded physics)
#
# Receipts: runs/<mode>/r99b_<cell>.rep<N>.{out,err,rc}
#           runs/<mode>/r99b_probe_<arm>.rep<N>.{out,err,rc}
# Namespace r99b_*; nothing is written outside this lane dir; no tracked file touched.
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-45}
MODE="${1:-quiet}"
REPS="${2:-3}"
HOGS=${HOGS:-16}
CELLS="census bus autoplay stoppos peak_calib mixblock advance finish loop_degenerate loop_pts gen gen_peak poly bus_peak p2d pan_law gen2d pause"
ARMS="modeinfo mixphase startphase peakphase mixfree finfree advfree splitcycle"

case "$MODE" in
  quiet)  FLAGS=""; PROJ=proj; DO_HOGS=0;;
  load)   FLAGS=""; PROJ=proj; DO_HOGS="$HOGS";;
  ff30)   FLAGS="--fixed-fps 30"; PROJ=proj; DO_HOGS=0;;
  ff60)   FLAGS="--fixed-fps 60"; PROJ=proj; DO_HOGS=0;;
  ff120)  FLAGS="--fixed-fps 120"; PROJ=proj; DO_HOGS=0;;
  ff1)    FLAGS="--fixed-fps 1"; PROJ=proj; DO_HOGS=0;;
  maxfps30)  FLAGS="--max-fps 30"; PROJ=proj; DO_HOGS=0;;
  maxfps60)  FLAGS="--max-fps 60"; PROJ=proj; DO_HOGS=0;;
  maxfps120) FLAGS="--max-fps 120"; PROJ=proj; DO_HOGS=0;;
  single) FLAGS="--single-threaded-scene"; PROJ=proj; DO_HOGS=0;;
  proj2d) FLAGS=""; PROJ=proj2d; DO_HOGS=0;;
  *) echo "unknown mode: $MODE" >&2; exit 2;;
esac

mkdir -p "runs/$MODE"
cp -f probes/audio_lattice.gd "$PROJ/audio_lattice.gd"
cp -f probes/r99b_modes.gd "$PROJ/r99b_modes.gd"
: > "runs/$MODE/rc-summary.txt"

PIDS=()
cleanup() {
  for p in ${PIDS[@]+"${PIDS[@]}"}; do kill "$p" 2>/dev/null; done
  wait 2>/dev/null
}
trap cleanup EXIT

host_yes() { pgrep -x yes | wc -l; }

if [ "$DO_HOGS" -gt 0 ]; then
  for i in $(seq 1 "$DO_HOGS"); do
    yes > /dev/null &
    PIDS+=("$!")
  done
  sleep 5
fi

{
  printf 'mode=%s flags=[%s] proj=%s reps=%s hogs=%d godot=%s\n' \
    "$MODE" "$FLAGS" "$PROJ" "$REPS" "$DO_HOGS" "$(timeout 20 "$GODOT" --version 2>&1 | tail -1)"
  printf 'load_start=%s host_yes_start=%s started=%s\n' \
    "$(cut -d' ' -f1-3 /proc/loadavg)" "$(host_yes)" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} >> "runs/$MODE/rc-summary.txt"

for cell in $CELLS; do
  for i in $(seq 1 "$REPS"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless $FLAGS --path "$PROJ" --script res://audio_lattice.gd -- \
      "--arm=$cell" > "runs/$MODE/r99b_${cell}.rep$i.out" 2> "runs/$MODE/r99b_${cell}.rep$i.err"
    echo "$?" > "runs/$MODE/r99b_${cell}.rep$i.rc"
  done
  printf '%s rc=[%s]\n' "$cell" "$(cat runs/$MODE/r99b_${cell}.rep*.rc | tr '\n' ' ')" >> "runs/$MODE/rc-summary.txt"
done

for arm in $ARMS; do
  for i in $(seq 1 2); do
    timeout -s KILL "$BOUND" "$GODOT" --headless $FLAGS --path "$PROJ" --script res://r99b_modes.gd -- \
      "--arm=$arm" > "runs/$MODE/r99b_probe_${arm}.rep$i.out" 2> "runs/$MODE/r99b_probe_${arm}.rep$i.err"
    echo "$?" > "runs/$MODE/r99b_probe_${arm}.rep$i.rc"
  done
done

printf 'load_end=%s host_yes_end=%s finished=%s own_hogs_killed=%d\n' \
  "$(cut -d' ' -f1-3 /proc/loadavg)" "$(host_yes)" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${#PIDS[@]}" \
  >> "runs/$MODE/rc-summary.txt"
cleanup
trap - EXIT
printf 'own_hogs_killed=%d host_yes_after_kill=%s\n' "${#PIDS[@]}" "$(host_yes)" >> "runs/$MODE/rc-summary.txt"
cat "runs/$MODE/rc-summary.txt"
