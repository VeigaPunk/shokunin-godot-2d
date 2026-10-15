#!/usr/bin/env bash
# r91-scribe: fresh single-rep launch of every nav arm in the battery's exact
# shape, plus the two scheduler-tail probes. Bounded; receipts under
# corpus/live/r91-scribe/fresh/.
set -u
cd /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
OUT=corpus/live/r91-scribe/fresh
mkdir -p "$OUT"
ARMS="census path query sync region agent avoid bake link teardown_crash teardown_clean"
for arm in $ARMS; do
  timeout -s KILL 25 godot --headless --path corpus/fixtures --script res://nav_lattice.gd -- --arm="$arm" \
    > "$OUT/$arm.out" 2> "$OUT/$arm.err"
  echo $? > "$OUT/$arm.rc"
  printf '%-16s rc=%s out=%sB err=%sB\n' "$arm" "$(cat "$OUT/$arm.rc")" "$(stat -c%s "$OUT/$arm.out")" "$(stat -c%s "$OUT/$arm.err")"
done
