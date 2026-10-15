#!/usr/bin/env bash
# r95-scout loadtest driver — every canonical cell re-run under deliberate CPU
# pressure (r87/r91 precedent: `yes` hogs, load avg 20+), to prove the pinned
# rows are load-stable (especially the ordering vectors and cast_motion fractions).
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-30}
HOGS=${HOGS:-16}
mkdir -p runs/loadtest
cp -f probes/dss_lattice.gd proj/

run_cell() { # name arm reps extra
  local name="$1" arm="$2" reps="$3" extra="${4:-}" i
  for i in $(seq 1 "$reps"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://dss_lattice.gd -- \
      "--arm=$arm" $extra > "runs/loadtest/$name.rep$i.out" 2> "runs/loadtest/$name.rep$i.err"
    echo "$?" > "runs/loadtest/$name.rep$i.rc"
  done
}

# start ONLY our own hogs and remember their PIDs (never pkill -x yes: other lanes
# run their own hog blocks on this shared host).
HOG_PIDS=""
for i in $(seq 1 "$HOGS"); do yes > /dev/null & HOG_PIDS="$HOG_PIDS $!"; done
sleep 2
: > runs/loadtest/rc-summary.txt
note() { printf '%s\n' "$1" >> runs/loadtest/rc-summary.txt; }
note "godot=$(timeout 20 "$GODOT" --version 2>&1 | tail -1)  hogs=$HOGS  load=$(cut -d' ' -f1-3 /proc/loadavg)  started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

for spec in "dss_census census 3" "dss_ray_flags ray_flags 3" "dss_ray_geom ray_geom 3" \
            "dss_ray_order ray_order 3" "dss_ray_order_rev ray_order 3 --rev" \
            "dss_point_cap point_cap 3" "dss_point_cap_rev point_cap 3 --rev" \
            "dss_point_edge point_edge 3" "dss_point_canvas point_canvas 3" \
            "dss_shape_lattice shape_lattice 3" "dss_shape_lattice_rev shape_lattice 3 --rev" \
            "dss_order_core order_core 3" "dss_order_core_rev order_core 3 --rev" \
            "dss_layer_forms layer_forms 3" "dss_cast_rest cast_rest 3" \
            "dss_excl_space excl_space 3" "dss_fresh fresh 3"; do
  set -- $spec
  name="$1"; arm="$2"; reps="$3"; extra="${4:-}"
  run_cell "$name" "$arm" "$reps" "$extra"
  note "$name arm=$arm reps=$reps extra=${extra:-none} rc=[$(cat runs/loadtest/$name.rep*.rc | tr '\n' ' ')] load=$(cut -d' ' -f1-3 /proc/loadavg)"
done

note "finished=$(date -u +%Y-%m-%dT%H:%M:%SZ) load=$(cut -d' ' -f1-3 /proc/loadavg)"
for p in $HOG_PIDS; do kill "$p" 2>/dev/null || true; done
sleep 1
note "own_hogs_killed=$(echo $HOG_PIDS | wc -w)  host_yes_remaining=$(pgrep -c -x yes || true)"
cat runs/loadtest/rc-summary.txt
echo "--- stray godot check (may include other lanes) ---"
pgrep -fa "dss_lattice" || echo "no r95 probes running"
