#!/usr/bin/env bash
# r94b boundary driver — attack the r94 scout particle claims under
# quiet / 16-hog load / --fixed-fps 30 / 60 / 120 (+ff120+load) / tps variants.
#
# Launch shape (identical to the scout's):
#   godot --headless [--fixed-fps N] --path proj --script res://<script> -- --arm=<arm>
# bounded by `timeout -s KILL 25`; stdout/stderr split + .rc + .wall sidecars.
# Batch dirs: runs/quiet runs/load runs/ff30 runs/ff60 runs/ff120 runs/ff120load runs/ab
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-25}
mkdir -p runs
HOGS=""
FF=()
trap 'stop_load' EXIT

stop_load() { if [ -n "${HOGS:-}" ]; then kill $HOGS 2>/dev/null; HOGS=""; fi; }
start_load() { local n="$1" i; HOGS=""; for i in $(seq 1 "$n"); do yes > /dev/null & HOGS="$HOGS $!"; done; sleep 1; }

note() { printf '%s\n' "$1" | tee -a runs/rc-summary.txt; }

_run() { # name script arm reps dir
  local name="$1" script="$2" arm="$3" reps="$4" dir="$5"
  local i rc t0 t1
  mkdir -p "$dir"
  for i in $(seq 1 "$reps"); do
    t0=$(date +%s.%N)
    timeout -s KILL "$BOUND" "$GODOT" --headless ${FF[@]+"${FF[@]}"} --path proj \
      --script "res://$script" -- "--arm=$arm" \
      > "$dir/$name.rep$i.out" 2> "$dir/$name.rep$i.err"
    rc=$?
    echo "$rc" > "$dir/$name.rep$i.rc"
    t1=$(date +%s.%N)
    awk -v a="$t0" -v b="$t1" 'BEGIN{printf "%.2f\n", b-a}' > "$dir/$name.rep$i.wall"
  done
}

# 19 scout cells, launched from the frozen scout probe byte-copy
cells() { # dir reps
  local d="$1" reps="$2"
  for spec in \
      "particles_census census" "particles_ppm ppm" "particles_convert convert" \
      "particles_cpu_lifetime cpu_lifetime" "particles_cpu_expl cpu_expl" \
      "particles_cpu_speed_pre cpu_speed_pre" "particles_cpu_stop cpu_stop" \
      "particles_cpu_never cpu_never" "particles_cpu_contam cpu_contam" \
      "particles_cpu_oneshot_off cpu_oneshot_off" "particles_cpu_oneshot_flag cpu_oneshot_flag" \
      "particles_cpu_pause cpu_pause" "particles_cpu_restart cpu_restart" \
      "particles_cpu_retrigger cpu_retrigger" "particles_cpu_lt_mid cpu_lt_mid" \
      "particles_cpu_speed_mid cpu_speed_mid" "particles_cpu_amount_mid cpu_amount_mid" \
      "particles_cpu_request cpu_request" "particles_gpu_headless gpu_headless"; do
    set -- $spec
    _run "r94_$1" scout_particles_lattice.gd "$2" "$reps" "$d"
  done
}

# the scout's OWN discovery-6 amount arms (byte-copy), re-run as a stability control
disc6() { # dir reps
  local d="$1" reps="$2"
  for arm in amount_cont amount_long amount_pre_start; do
    _run "r94b_disc6_$arm" scout_discover6.gd "$arm" "$reps" "$d"
  done
}

# attack arms
arms() { # dir reps
  local d="$1" reps="$2"
  for arm in frame_ratio clock_unit tps30 tps120 ffprop ff1_long amount_sync amount_attr amount_pre amount_cont amount_phase \
             contam_a contam_b contam_c contam_d contam_e contam_f contam_g contam_h contam_j contam_k contam_first \
             gpu_probe req_var; do
    _run "r94b_$arm" r94b_particles.gd "$arm" "$reps" "$d"
  done
}

batch_quiet() {
  note "== batch quiet started=$(date -u +%Y-%m-%dT%H:%M:%SZ) godot=$(timeout 20 "$GODOT" --version 2>&1 | tail -1) bound=$BOUND"
  note "loadavg_start=$(cat /proc/loadavg)"
  cells runs/quiet 3
  arms runs/quiet 3
  disc6 runs/quiet 3
  note "loadavg_end=$(cat /proc/loadavg)"
  note "== batch quiet finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

batch_load() {
  note "== batch load (16 system-wide yes hogs + ambient) started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  start_load 16
  note "loadavg_start=$(cat /proc/loadavg) my_hogs=$(pgrep -c -x yes)"
  cells runs/load 3
  arms runs/load 2
  disc6 runs/load 3
  stop_load
  note "loadavg_end=$(cat /proc/loadavg) my_hogs_after_stop=$(pgrep -c -x yes)"
  note "== batch load finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

batch_ff() { # fps reps_arms
  local fps="$1" ra="$2"
  FF=(--fixed-fps "$fps")
  note "== batch ff$fps started=$(date -u +%Y-%m-%dT%H:%M:%SZ) ff=${FF[*]}"
  note "loadavg_start=$(cat /proc/loadavg)"
  cells "runs/ff$fps" 3
  arms "runs/ff$fps" "$ra"
  disc6 "runs/ff$fps" 2
  FF=()
  note "loadavg_end=$(cat /proc/loadavg)"
  note "== batch ff$fps finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

batch_ff120load() {
  note "== batch ff120load (--fixed-fps 120 + 16 hogs) started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  start_load 16
  FF=(--fixed-fps 120)
  note "loadavg_start=$(cat /proc/loadavg) my_hogs=$(pgrep -c -x yes)"
  cells runs/ff120load 2
  arms runs/ff120load 1
  FF=()
  stop_load
  note "loadavg_end=$(cat /proc/loadavg)"
  note "== batch ff120load finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

# Paired, interleaved A/B in one window: default vs --fixed-fps 30/60/120 on the
# three load-bearing timing cells (ladder, streamed formula, clock-free request).
batch_ab() {
  note "== batch ab (paired default vs ff30/ff60/ff120) started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  note "loadavg_start=$(cat /proc/loadavg)"
  local i
  for i in 1 2 3; do
    FF=(); _run "ab${i}_def_cpu_lifetime" scout_particles_lattice.gd cpu_lifetime 1 runs/ab
    FF=(--fixed-fps 30); _run "ab${i}_f30_cpu_lifetime" scout_particles_lattice.gd cpu_lifetime 1 runs/ab
    FF=(--fixed-fps 60); _run "ab${i}_f60_cpu_lifetime" scout_particles_lattice.gd cpu_lifetime 1 runs/ab
    FF=(--fixed-fps 120); _run "ab${i}_f120_cpu_lifetime" scout_particles_lattice.gd cpu_lifetime 1 runs/ab
    FF=(); _run "ab${i}_def_cpu_expl" scout_particles_lattice.gd cpu_expl 1 runs/ab
    FF=(--fixed-fps 30); _run "ab${i}_f30_cpu_expl" scout_particles_lattice.gd cpu_expl 1 runs/ab
    FF=(--fixed-fps 60); _run "ab${i}_f60_cpu_expl" scout_particles_lattice.gd cpu_expl 1 runs/ab
    FF=(--fixed-fps 120); _run "ab${i}_f120_cpu_expl" scout_particles_lattice.gd cpu_expl 1 runs/ab
    FF=(); _run "ab${i}_def_cpu_request" scout_particles_lattice.gd cpu_request 1 runs/ab
    FF=(--fixed-fps 30); _run "ab${i}_f30_cpu_request" scout_particles_lattice.gd cpu_request 1 runs/ab
    FF=(--fixed-fps 60); _run "ab${i}_f60_cpu_request" scout_particles_lattice.gd cpu_request 1 runs/ab
    FF=(--fixed-fps 120); _run "ab${i}_f120_cpu_request" scout_particles_lattice.gd cpu_request 1 runs/ab
  done
  FF=()
  note "loadavg_end=$(cat /proc/loadavg)"
  note "== batch ab finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

case "${1:-all}" in
  quiet) batch_quiet ;;
  load) batch_load ;;
  ff30) batch_ff 30 2 ;;
  ff60) batch_ff 60 2 ;;
  ff120) batch_ff 120 2 ;;
  ff120load) batch_ff120load ;;
  ab) batch_ab ;;
  all) batch_quiet; batch_load; batch_ff 30 2; batch_ff 60 2; batch_ff 120 2; batch_ff120load; batch_ab ;;
  *) echo "unknown batch: $1" >&2; exit 2 ;;
esac

note "timeout_hits=$(grep -l '^137$' runs/*/*.rc 2>/dev/null | wc -l) total_rc_files=$(ls runs/*/*.rc 2>/dev/null | wc -l)"
note "stray godot from this lane (may include other lanes): $(pgrep -fa 'r94-boundary' | wc -l)"
note "my yes hogs left: $(pgrep -c -x yes || echo 0)"
