#!/usr/bin/env bash
# VER-11 forge-kill probe harness (r101).
# Deviation note: the seat brief named /tmp/r101-ver11/, but /tmp hit EDQUOT
# (a 89-byte copy fails); scratch lives in the repo's gitignored
# corpus/live/r101-ver11/ instead (corpus/.gitignore: live/**/scratch/).
# Never runs run_battery.py; only targeted godot --headless calls.
set -u
REPO=/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
SCR=$REPO/corpus/live/r101-ver11/scratch
OUT=$REPO/corpus/live/r101-ver11/receipts
GODOT=${GODOT:-godot}
mkdir -p "$OUT"

run() { # name dir args...
  local name=$1; shift; local dir=$1; shift
  local t0 t1 rc
  t0=$(date +%s%N)
  ( cd "$dir" && "$GODOT" --headless --path "$dir" --script "res://$1" -- "${@:2}" ) \
     >"$OUT/$name.out" 2>"$OUT/$name.err" </dev/null
  rc=$?
  t1=$(date +%s%N)
  echo "$name rc=$rc ms=$(( (t1 - t0) / 1000000 )) stdout_sha=$(sha256sum <"$OUT/$name.out" | cut -d' ' -f1) stderr_sha=$(sha256sum <"$OUT/$name.err" | cut -d' ' -f1)"
}

{
  date -Is; echo "load: $(uptime)"
  echo "godot: $($GODOT --version 2>&1 | tail -1)"
  echo "--- r100b_seq baseline --clean=0"
  run seq_base_clean0 "$SCR/base" r100b_seq.gd --clean=0
  echo "--- r100b_seq baseline --clean=1"
  run seq_base_clean1 "$SCR/base" r100b_seq.gd --clean=1
  echo "--- r100b_seq FORGED (extra replay line) --clean=0"
  run seq_forged_clean0 "$SCR/forged" r100b_seq.gd --clean=0
  echo "--- r100b_seq FORGED --clean=1"
  run seq_forged_clean1 "$SCR/forged" r100b_seq.gd --clean=1
  echo "--- offy dead-flag triple (r95b_order celloff)"
  run offy_1000 "$SCR/offy" r95b_order.gd --arm=celloff --off=0 --offy=1000
  run offy_absent "$SCR/offy" r95b_order.gd --arm=celloff --off=0
  run offy_999999 "$SCR/offy" r95b_order.gd --arm=celloff --off=0 --offy=999999
  run offy_x1000 "$SCR/offy" r95b_order.gd --arm=celloff --off=1000
  date -Is
} 2>&1 | tee "$OUT/manifest.txt"
