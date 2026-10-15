#!/usr/bin/env bash
# r92-boundary nav ratio scan — locate the --fixed-fps ratio at which the scout's
# `nav` row breaks (regions_f1 1 -> 0) and cross-check with the seat's own
# per-physics-frame region poller (t_reg_add 1 -> 2).
# Idle:physics ratio = fixed_fps / 60.
# Usage: bash run_nav_scan.sh
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-25}
mkdir -p runs/scan
cp -f probes/*.gd proj/

run() { # name ff... reps
  local name="$1" reps="$2"; shift 2
  local i rc
  for i in $(seq 1 "$reps"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless "$@" --path proj \
      --script res://scout_tilemap_lattice.gd -- --arm=nav \
      > "runs/scan/${name}_scout.rep$i.out" 2> "runs/scan/${name}_scout.rep$i.err"
    echo "$?" > "runs/scan/${name}_scout.rep$i.rc"
    timeout -s KILL "$BOUND" "$GODOT" --headless "$@" --path proj \
      --script res://r92b_probe.gd -- --arm=nav \
      > "runs/scan/${name}_own.rep$i.out" 2> "runs/scan/${name}_own.rep$i.err"
    echo "$?" > "runs/scan/${name}_own.rep$i.rc"
    printf '%-8s rep%d scout=%s own=%s\n' "$name" "$i" \
      "$(grep -o 'regions_f1=[01]' runs/scan/${name}_scout.rep$i.out | head -1)" \
      "$(grep -o 't_reg_add=[0-9-]*' runs/scan/${name}_own.rep$i.out | head -1)"
  done
}

for ff in 240 300 400 480 600 900; do
  run "ff$ff" 2 --fixed-fps "$ff"
done
# load-independence of the ff600 break
HOGS=""
for i in $(seq 1 12); do yes > /dev/null & HOGS="$HOGS $!"; done
sleep 2
run "ff600load" 2 --fixed-fps 600
kill $HOGS 2>/dev/null
sleep 1
echo "loadavg=$(cat /proc/loadavg) yes_now=$(pgrep -c -x yes || echo 0)"
