#!/usr/bin/env bash
# r92-boundary nav row rate test — how often does the scout's `regions_f1` read 1 vs 0
# in each scheduler mode? 20 default + 20 ff120 + 10 ff150 + 10 ff600 reps of the
# frozen scout `nav` arm. (The row is proposed as a single-valued battery row.)
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-25}
mkdir -p runs/reps
cp -f probes/*.gd proj/

rate() { # name reps ff...
  local name="$1" reps="$2"; shift 2
  local i one zero other
  one=0; zero=0; other=0
  for i in $(seq 1 "$reps"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless "$@" --path proj \
      --script res://scout_tilemap_lattice.gd -- --arm=nav \
      > "runs/reps/${name}.rep$i.out" 2> "runs/reps/${name}.rep$i.err"
    echo "$?" > "runs/reps/${name}.rep$i.rc"
    case "$(grep -o 'regions_f1=[0-9-]*' runs/reps/${name}.rep$i.out | head -1)" in
      regions_f1=1) one=$((one+1));;
      regions_f1=0) zero=$((zero+1));;
      *) other=$((other+1));;
    esac
  done
  echo "$name reps=$reps regions_f1: one=$one zero=$zero other=$other"
}

rate def20 20
rate ff120x20 20 --fixed-fps 120
rate ff150x10 10 --fixed-fps 150
rate ff600x10 10 --fixed-fps 600
echo "loadavg=$(cat /proc/loadavg)"
