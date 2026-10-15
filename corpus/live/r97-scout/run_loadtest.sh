#!/usr/bin/env bash
# r97-scout loadtest driver — re-run every canonical cell under deliberate host load.
# Own hog PIDs are tracked and killed at the end; no other process is touched.
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-30}
HOGS=${HOGS:-10}
REPS=${REPS:-3}
mkdir -p runs/loadtest
cp -f probes/stree_lattice.gd proj/

HOG_PIDS=()
for i in $(seq 1 "$HOGS"); do
  yes > /dev/null &
  HOG_PIDS+=("$!")
done
echo "own_hogs=${#HOG_PIDS[@]} pids=${HOG_PIDS[*]}" > runs/loadtest/hogs.txt
echo "loadavg_start=$(cut -d' ' -f1-3 /proc/loadavg)" >> runs/loadtest/hogs.txt

run_cell() { # name arm reps extra
  local name="$1" arm="$2" reps="$3" extra="${4:-}" i
  for i in $(seq 1 "$reps"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://stree_lattice.gd -- \
      "--arm=$arm" $extra > "runs/loadtest/${name}.rep$i.out" 2> "runs/loadtest/${name}.rep$i.err"
    echo "$?" > "runs/loadtest/${name}.rep$i.rc"
    printf 'loadavg=%s cell=%s rep=%s\n' "$(cut -d' ' -f1-3 /proc/loadavg)" "$name" "$i" >> runs/loadtest/hogs.txt
  done
}

run_cell census census "$REPS"
run_cell group_order group_order "$REPS"
run_cell group_order_rev group_order "$REPS" --rev
run_cell group_flags group_flags "$REPS"
run_cell group_lifecycle group_lifecycle "$REPS"
run_cell group_setters group_setters "$REPS"
run_cell signal_order signal_order "$REPS"
run_cell signal_flags signal_flags "$REPS"
run_cell defer_ladder defer_ladder "$REPS"
run_cell defer_slots defer_slots "$REPS"
run_cell defer_order defer_order "$REPS"
run_cell scene_probe scene_probe "$REPS"

echo "loadavg_end=$(cut -d' ' -f1-3 /proc/loadavg)" >> runs/loadtest/hogs.txt
killed=0
for pid in "${HOG_PIDS[@]}"; do
  if kill "$pid" 2>/dev/null; then killed=$((killed + 1)); fi
done
echo "own_hogs_killed=$killed" >> runs/loadtest/hogs.txt
echo "host_yes_remaining=$(pgrep -c '^yes$' || true)" >> runs/loadtest/hogs.txt
cat runs/loadtest/hogs.txt | tail -5
echo "done: $(ls runs/loadtest/*.rep*.out 2>/dev/null | wc -l) loadtest receipts"
