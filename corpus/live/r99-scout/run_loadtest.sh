#!/usr/bin/env bash
# r99-scout loadtest driver — all 16 cells x3 reps under own `yes` hogs.
# Own-PID-only cleanup: never pkill by name (other lanes run hogs too).
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-60}
HOGS=${HOGS:-16}
mkdir -p runs/loadtest
cp -f probes/audio_lattice.gd proj/

PIDS=()
for i in $(seq 1 "$HOGS"); do
  yes > /dev/null &
  PIDS+=("$!")
done
cleanup() {
  for p in "${PIDS[@]}"; do kill "$p" 2>/dev/null; done
  wait 2>/dev/null
}
trap cleanup EXIT

sleep 5
: > runs/loadtest/rc-summary.txt
printf 'load=%s hogs=%d godot=%s started=%s\n' "$(cut -d' ' -f1 /proc/loadavg)" "$HOGS" \
  "$(timeout 20 "$GODOT" --version 2>&1 | tail -1)" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  >> runs/loadtest/rc-summary.txt

for cell in census bus autoplay stoppos peak_calib mixblock advance finish \
            loop_degenerate loop_pts gen gen_peak poly bus_peak p2d pan_law gen2d pause; do
  for i in 1 2 3; do
    timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://audio_lattice.gd -- \
      "--arm=$cell" > "runs/loadtest/$cell.rep$i.out" 2> "runs/loadtest/$cell.rep$i.err"
    echo "$?" > "runs/loadtest/$cell.rep$i.rc"
  done
  printf '%s rc=[%s]\n' "$cell" "$(cat runs/loadtest/$cell.rep*.rc | tr '\n' ' ')" >> runs/loadtest/rc-summary.txt
done

printf 'load_end=%s finished=%s\n' "$(cut -d' ' -f1 /proc/loadavg)" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  >> runs/loadtest/rc-summary.txt
cat runs/loadtest/rc-summary.txt
