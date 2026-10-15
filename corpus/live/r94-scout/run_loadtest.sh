#!/usr/bin/env bash
# r94-scout loadtest — same 19 cells under deliberate CPU load (`yes` hogs),
# receipts in runs/loadtest/.  Validates the gating prefixes against load.
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-30}
REPS=${REPS:-2}
HOGS=${HOGS:-16}
mkdir -p runs/loadtest
cp -f probes/particles_lattice.gd proj/

run_cell() { # name arm
  local name="$1" arm="$2" i
  for i in $(seq 1 "$REPS"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://particles_lattice.gd -- \
      "--arm=$arm" > "runs/loadtest/r94_$name.rep$i.out" 2> "runs/loadtest/r94_$name.rep$i.err"
    echo "$?" > "runs/loadtest/r94_$name.rep$i.rc"
  done
}

: > runs/loadtest/load-summary.txt
note() { printf '%s\n' "$1" >> runs/loadtest/load-summary.txt; }

for i in $(seq 1 "$HOGS"); do yes > /dev/null & done
HOG_PIDS=$(jobs -p | tr '\n' ' ')
sleep 3
note "loadavg_before=$(cut -d' ' -f1-3 /proc/loadavg)  hogs=$HOGS  reps=$REPS  bound_s=$BOUND  started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

for spec in "particles_census census" "particles_ppm ppm" "particles_convert convert" \
            "particles_cpu_lifetime cpu_lifetime" "particles_cpu_expl cpu_expl" \
            "particles_cpu_speed_pre cpu_speed_pre" "particles_cpu_stop cpu_stop" \
            "particles_cpu_never cpu_never" "particles_cpu_contam cpu_contam" \
            "particles_cpu_oneshot_off cpu_oneshot_off" "particles_cpu_oneshot_flag cpu_oneshot_flag" \
            "particles_cpu_pause cpu_pause" "particles_cpu_restart cpu_restart" \
            "particles_cpu_retrigger cpu_retrigger" "particles_cpu_lt_mid cpu_lt_mid" \
            "particles_cpu_speed_mid cpu_speed_mid" "particles_cpu_amount_mid cpu_amount_mid" \
            "particles_cpu_request cpu_request" "particles_gpu_headless gpu_headless"; do
  set -- $spec
  run_cell "$1" "$2"
  note "$1 arm=$2 reps=$REPS rc=[$(cat runs/loadtest/r94_$1.rep*.rc | tr '\n' ' ')] loadavg_now=$(cut -d' ' -f1-3 /proc/loadavg)"
done

kill $HOG_PIDS 2>/dev/null
wait 2>/dev/null
note "loadavg_after=$(cut -d' ' -f1-3 /proc/loadavg)  yes_remaining=$(pgrep -c -x yes || echo 0)  finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat runs/loadtest/load-summary.txt
