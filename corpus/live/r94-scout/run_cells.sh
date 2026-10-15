#!/usr/bin/env bash
# r94-scout driver — CPUParticles2D + GPUParticles2D emission lattice.
# Battery launch shape:
#   godot --headless --path proj --script res://particles_lattice.gd -- --arm=<arm>
# bounded by `timeout -s KILL`; stdout/stderr split into per-cell sidecars plus .rc.
# Reps: 3 per pure/static cell, 6 per timing/lifecycle cell (REPS env override).
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-30}
REPS=${REPS:-0}
mkdir -p runs
cp -f probes/particles_lattice.gd proj/

run_cell() { # name arm reps
  local name="$1" arm="$2" reps="$3" i
  if [ "$REPS" != "0" ]; then reps="$REPS"; fi
  for i in $(seq 1 "$reps"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://particles_lattice.gd -- \
      "--arm=$arm" > "runs/r94_$name.rep$i.out" 2> "runs/r94_$name.rep$i.err"
    echo "$?" > "runs/r94_$name.rep$i.rc"
  done
}

: > runs/rc-summary.txt
note() { printf '%s\n' "$1" >> runs/rc-summary.txt; }

note "godot=$(timeout 20 "$GODOT" --version 2>&1 | tail -1)  bound_s=$BOUND  reps_override=$REPS  started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

for spec in "particles_census census 3" "particles_ppm ppm 3" "particles_convert convert 3" \
            "particles_cpu_lifetime cpu_lifetime 6" "particles_cpu_expl cpu_expl 6" \
            "particles_cpu_speed_pre cpu_speed_pre 6" "particles_cpu_stop cpu_stop 6" \
            "particles_cpu_never cpu_never 6" "particles_cpu_contam cpu_contam 6" \
            "particles_cpu_oneshot_off cpu_oneshot_off 6" "particles_cpu_oneshot_flag cpu_oneshot_flag 6" \
            "particles_cpu_pause cpu_pause 6" "particles_cpu_restart cpu_restart 6" \
            "particles_cpu_retrigger cpu_retrigger 6" "particles_cpu_lt_mid cpu_lt_mid 6" \
            "particles_cpu_speed_mid cpu_speed_mid 6" "particles_cpu_amount_mid cpu_amount_mid 6" \
            "particles_cpu_request cpu_request 6" "particles_gpu_headless gpu_headless 6"; do
  set -- $spec
  run_cell "$1" "$2" "$3"
  note "$1 arm=$2 reps=$3 rc=[$(cat runs/r94_$1.rep*.rc | tr '\n' ' ')]"
done

note "finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat runs/rc-summary.txt
echo "--- stray godot check (may include other lanes) ---"
pgrep -fa "godot" || echo "none"
