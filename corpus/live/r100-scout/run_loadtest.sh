#!/usr/bin/env bash
# r100-scout load test: N own hogs + REPS reps of every cell.
set -u
cd "$(dirname "$0")"
HOGS="${HOGS:-8}"; REPS="${REPS:-2}"
pids=()
for i in $(seq 1 "$HOGS"); do yes > /dev/null & pids+=($!); done
for arm in census routing hover motion localpos cursor clip drag touch subvp warp focus render osmeta; do
  for r in $(seq 1 "$REPS"); do
    out="runs/loadtest/r100_gui_${arm}.rep${r}.out"; err="runs/loadtest/r100_gui_${arm}.rep${r}.err"; rc="runs/loadtest/r100_gui_${arm}.rep${r}.rc"
    timeout -s KILL 30 /usr/bin/godot --headless --path proj --script res://r100_gui.gd -- "--arm=${arm}" >"$out" 2>"$err"
    echo "$?" > "$rc"
  done
done
for p in "${pids[@]}"; do kill "$p" 2>/dev/null; done
echo "loadtest done hogs=$HOGS reps=$REPS"
