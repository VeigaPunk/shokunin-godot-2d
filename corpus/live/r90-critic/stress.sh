#!/usr/bin/env bash
# r90-critic: concurrency + single-CPU starvation probes for the r90 arms.
# usage: stress.sh <proj> <tag> <mode>   mode=conc|starve
set -u
PROJ="$1"; TAG="$2"; MODE="$3"
cd "$(dirname "$0")"
mkdir -p runs

if [ "$MODE" = "conc" ]; then
  # 6 simultaneous godot processes (mixed arms), same launch shape
  for spec in "gravity:--arm=gravity" "order:--arm=order" "freezelock:--arm=freezelock --frames=120" \
              "contacts:--arm=contacts" "lag:--arm=lag --frames=30" "impedge:--arm=impedge"; do
    arm="${spec%%:*}"; flags="${spec#*:}"
    ( timeout -s KILL 20 godot --headless --path "$PROJ" --script res://rb_lattice.gd -- $flags \
        > "runs/${TAG}.${arm}.out" 2> "runs/${TAG}.${arm}.err"; echo $? > "runs/${TAG}.${arm}.rc" ) &
  done
  wait
fi

if [ "$MODE" = "starve" ]; then
  # godot pinned to one CPU; 12 hogs on the same CPU
  for i in $(seq 1 12); do
    nohup bash -c 'exec -a r90c_pinhog yes > /dev/null' >/dev/null 2>&1 &
  done
  for r in $(seq 1 6); do
    taskset -c 0 timeout -s KILL 20 godot --headless --path "$PROJ" --script res://rb_lattice.gd -- --arm=order \
      > "runs/${TAG}.order.rep${r}.out" 2> "runs/${TAG}.order.rep${r}.err"
    echo $? > "runs/${TAG}.order.rep${r}.rc"
  done
  pkill -f r90c_pinhog
fi
