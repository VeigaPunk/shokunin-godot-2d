#!/usr/bin/env bash
# r92-scout loadtest — all 13 cells once under deliberate CPU load.
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-30}
mkdir -p runs/loadtest
HOGS=${HOGS:-16}
for i in $(seq 1 "$HOGS"); do (timeout 90 yes > /dev/null &) ; done
sleep 3
echo "load_before=$(cat /proc/loadavg)"
for spec in "tm_census census" "tm_atlas atlas" "tm_cells cells" "tm_custom custom" \
            "tm_terrain terrain" "tm_pattern pattern" "tm_encoding encoding" \
            "tm_fixinvalid fixinvalid" "tm_srcids srcids" "tm_physics physics" \
            "tm_timing timing" "tm_quadrant quadrant" "tm_nav nav"; do
  set -- $spec
  timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://tilemap_lattice.gd -- \
    "--arm=$2" > "runs/loadtest/r92_$1.rep1.out" 2> "runs/loadtest/r92_$1.rep1.err"
  echo "$?" > "runs/loadtest/r92_$1.rep1.rc"
  echo "$1 rc=$(cat runs/loadtest/r92_$1.rep1.rc)"
done
echo "load_after=$(cat /proc/loadavg)"
pkill -x yes 2>/dev/null || true
sleep 1
echo "yes_hogs_left=$(pgrep -c -x yes || echo 0)"
