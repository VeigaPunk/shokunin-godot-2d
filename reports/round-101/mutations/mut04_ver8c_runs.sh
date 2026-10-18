#!/usr/bin/env bash
# MUT-4 (r101) — receipts against ver8's staged variant-C landing (proj3).
# committed fixture copy = proj3/r95b_order_committed.gd ; patched = proj3/r95b_order.gd
set -u
OUT=/tmp/r101-mut04/out3
PROJ=/tmp/r101-mut04/proj3
mkdir -p "$OUT" /tmp/r101-mut04/xdg-data
export XDG_DATA_HOME=/tmp/r101-mut04/xdg-data
: > "$OUT/run_log.txt"

# the committed (unpatched) fixture control, for the flag-ignored forgery
cp /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/fixtures/r95b_order.gd \
   "$PROJ/r95b_order_committed.gd"

run() {
  local name=$1 script=$2; shift 2
  local t0 t1 rc
  t0=$(date +%s)
  timeout 120 godot --headless --path "$PROJ" --script "res://$script" -- "$@" \
    > "$OUT/$name.stdout" 2> "$OUT/$name.stderr"
  rc=$?
  t1=$(date +%s)
  echo "$rc" > "$OUT/$name.rc"
  printf '%s rc=%s secs=%ss cmd=godot --headless --path %s --script res://%s -- %s\n' \
    "$name" "$rc" "$((t1 - t0))" "$PROJ" "$script" "$*" >> "$OUT/run_log.txt"
}

run c_base          r95b_order.gd            --arm=celloff --off=0 --offy=1000
run c_committed     r95b_order_committed.gd  --arm=celloff --off=0 --offy=1000
run c_omit_y        c_mut_omit_y.gd          --arm=celloff --off=0 --offy=1000
run c_swapkeys      c_mut_swapkeys.gd        --arm=celloff --off=0 --offy=1000
run c_dropt64       c_mut_dropt64.gd         --arm=celloff --off=0 --offy=1000

cat "$OUT/run_log.txt"
