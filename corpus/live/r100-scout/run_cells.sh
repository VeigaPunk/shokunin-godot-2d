#!/usr/bin/env bash
# r100-scout cell runner: one fresh godot process per (cell, rep).
set -u
cd "$(dirname "$0")"
ARMS="$1"; REPS="${2:-3}"
for arm in $ARMS; do
  for r in $(seq 1 "$REPS"); do
    out="runs/r100_gui_${arm}.rep${r}.out"; err="runs/r100_gui_${arm}.rep${r}.err"; rc="runs/r100_gui_${arm}.rep${r}.rc"
    timeout -s KILL 30 /usr/bin/godot --headless --path proj --script res://r100_gui.gd -- "--arm=${arm}" >"$out" 2>"$err"
    echo "$?" > "$rc"
  done
done
echo "done arms=[$ARMS] reps=$REPS"
