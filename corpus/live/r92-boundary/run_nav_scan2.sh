#!/usr/bin/env bash
# r92-boundary nav ratio scan, wave 2 — narrow the flip point between --fixed-fps 120
# (row OK) and 240 (row broken), and test whether the driver is the idle:physics
# RATIO or the --fixed-fps value itself, by crossing ff with the 120-tps project:
#   ff120 + tps120 => ratio 1     ff240 + tps120 => ratio 2     ff480 + tps120 => ratio 4
# (ratio = fixed_fps / physics_ticks_per_second).
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-25}
mkdir -p runs/scan2
cp -f probes/*.gd proj/
cp -f probes/*.gd proj_tps120/

run() { # name proj ff... reps
  local name="$1" proj="$2" reps="$3"; shift 3
  local i
  for i in $(seq 1 "$reps"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless "$@" --path "$proj" \
      --script res://scout_tilemap_lattice.gd -- --arm=nav \
      > "runs/scan2/${name}_scout.rep$i.out" 2> "runs/scan2/${name}_scout.rep$i.err"
    echo "$?" > "runs/scan2/${name}_scout.rep$i.rc"
    timeout -s KILL "$BOUND" "$GODOT" --headless "$@" --path "$proj" \
      --script res://r92b_probe.gd -- --arm=nav \
      > "runs/scan2/${name}_own.rep$i.out" 2> "runs/scan2/${name}_own.rep$i.err"
    echo "$?" > "runs/scan2/${name}_own.rep$i.rc"
    printf '%-14s rep%d scout=%s own=%s\n' "$name" "$i" \
      "$(grep -o 'regions_f1=[01]' runs/scan2/${name}_scout.rep$i.out | head -1)" \
      "$(grep -o 't_reg_add=[0-9-]*' runs/scan2/${name}_own.rep$i.out | head -1)"
  done
}

run ff150 proj 2 --fixed-fps 150
run ff180 proj 2 --fixed-fps 180
run ff200 proj 2 --fixed-fps 200
run ff210 proj 2 --fixed-fps 210
run t120_ff120 proj_tps120 2 --fixed-fps 120
run t120_ff240 proj_tps120 2 --fixed-fps 240
run t120_ff480 proj_tps120 2 --fixed-fps 480
run t120_none proj_tps120 2
echo "loadavg=$(cat /proc/loadavg)"
