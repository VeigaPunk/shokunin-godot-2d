#!/usr/bin/env bash
# hog-count ladder v2: verified cleanup between steps
cd "$(dirname "$0")"
cleanup() { pkill -x yes 2>/dev/null; sleep 1; }
for n in 0 2 4 8 16 24; do
  cleanup
  if [ "$n" -gt 0 ]; then for i in $(seq "$n"); do yes > /dev/null & done; sleep 1; fi
  vals=""
  for r in 1 2 3; do
    v=$(timeout -s KILL 25 godot --headless --path proj --script res://input89_edges.gd -- --arm=exact 2>/dev/null | grep "^PASS" | grep -o "just_after_flush=w_jp\[[^]]*\]")
    vals="$vals ${v#just_after_flush=w_jp[}"
  done
  load=$(cut -d' ' -f1 /proc/loadavg)
  echo "hogs=$n load=$load reps:$vals"
done
cleanup
