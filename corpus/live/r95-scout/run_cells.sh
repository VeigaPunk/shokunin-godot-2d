#!/usr/bin/env bash
# r95-scout driver — PhysicsDirectSpaceState2D query lattice + ordering stability.
# Battery launch shape:
#   godot --headless --path proj --script res://dss_lattice.gd -- --arm=<arm> [--rev]
# bounded by `timeout -s KILL`; stdout/stderr split into per-cell sidecars plus .rc.
# Reps: 3 per pure/static cell, 6 per frame-bound (physics-await) cell.
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-30}
mkdir -p runs
cp -f probes/dss_lattice.gd proj/

run_cell() { # name arm reps extra
  local name="$1" arm="$2" reps="$3" extra="${4:-}" i
  for i in $(seq 1 "$reps"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://dss_lattice.gd -- \
      "--arm=$arm" $extra > "runs/r95_$name.rep$i.out" 2> "runs/r95_$name.rep$i.err"
    echo "$?" > "runs/r95_$name.rep$i.rc"
  done
}

: > runs/rc-summary.txt
note() { printf '%s\n' "$1" >> runs/rc-summary.txt; }

note "godot=$(timeout 20 "$GODOT" --version 2>&1 | tail -1)  bound_s=$BOUND  started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

for spec in "dss_census census 3" "dss_ray_flags ray_flags 6" "dss_ray_geom ray_geom 6" \
            "dss_ray_order ray_order 6" "dss_ray_order_rev ray_order 6 --rev" \
            "dss_point_cap point_cap 6" "dss_point_cap_rev point_cap 6 --rev" \
            "dss_point_edge point_edge 6" "dss_point_canvas point_canvas 6" \
            "dss_shape_lattice shape_lattice 6" "dss_shape_lattice_rev shape_lattice 6 --rev" \
            "dss_order_core order_core 6" "dss_order_core_rev order_core 6 --rev" \
            "dss_layer_forms layer_forms 6" "dss_cast_rest cast_rest 6" \
            "dss_excl_space excl_space 6" "dss_fresh fresh 6"; do
  set -- $spec
  name="$1"; arm="$2"; reps="$3"; extra="${4:-}"
  run_cell "$name" "$arm" "$reps" "$extra"
  note "$name arm=$arm reps=$reps extra=${extra:-none} rc=[$(cat runs/r95_$name.rep*.rc | tr '\n' ' ')]"
done

note "finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat runs/rc-summary.txt
echo "--- stray godot check (may include other lanes) ---"
pgrep -fa "godot" || echo "none"
