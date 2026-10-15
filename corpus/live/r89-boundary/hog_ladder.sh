#!/usr/bin/env bash
# hog-count ladder for input89_edges exact just_after_flush mode
cd "$(dirname "$0")"
for n in 0 2 4 8 12 16 24; do
  if [ "$n" -gt 0 ]; then for i in $(seq "$n"); do yes > /dev/null & done; HOGS=$(jobs -p); sleep 1; fi
  vals=""
  for r in 1 2 3; do
    v=$(timeout -s KILL 25 godot --headless --path proj --script res://input89_edges.gd -- --arm=exact 2>/dev/null | grep "^PASS" | grep -o "just_after_flush=w_jp\[[^]]*\]")
    vals="$vals $v"
  done
  echo "hogs=$n reps:$vals"
  if [ "$n" -gt 0 ]; then kill $HOGS 2>/dev/null; wait 2>/dev/null; fi
done
