#!/usr/bin/env bash
# r92 critic seat — crash-row wall-time distribution.
# The engine's crash handler symbolizes the C++ backtrace by forking
# `sh -c llvm-addr2line <addrs...>` and waiting for it; the wall time of every
# crash-handler row is therefore symbolization-bound, not crash-bound.
# Measures the nullts row (r92) against two pre-existing crash rows.
set -u
cd "$(dirname "$0")/.."
ulimit -c 0
proj=proj
run() { # tag, script, flag
  local tag=$1 script=$2 flag=$3 i t0 t1
  for i in $(seq 1 "$4"); do
    t0=$(date +%s%N)
    timeout -s KILL 20 godot --headless --path "$proj" --script "res://$script" -- "$flag" \
      > "runs/wall.$tag.rep$i.out" 2> "runs/wall.$tag.rep$i.err"
    echo $? > "runs/wall.$tag.rep$i.rc"
    t1=$(date +%s%N)
    echo "$tag rep$i wall_ms=$(( (t1 - t0) / 1000000 )) rc=$(cat runs/wall.$tag.rep$i.rc) \
frames=$(grep -c '^\[[0-9]*\]' runs/wall.$tag.rep$i.err) loadavg=$(cut -d' ' -f1 /proc/loadavg)"
  done
}
echo "loadavg start: $(cut -d' ' -f1-3 /proc/loadavg)"
run nullts_w tilemap_lattice.gd --arm=nullts 8
run spont_w spontaneous_crash_probe.gd --spontaneous-crash 5
run lineempty_w geo2d_lattice.gd --arm=lineempty 3
echo "loadavg end:   $(cut -d' ' -f1-3 /proc/loadavg)"
