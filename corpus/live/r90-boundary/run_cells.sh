#!/usr/bin/env bash
# r90-boundary driver — stress the r90 scout's RigidBody2D lattice claims.
# Every run is the battery launch shape:
#   godot --headless --path <proj> --script res://<script> -- --arm=<arm> [extra...]
# bounded by `timeout -s KILL 25`; stdout/stderr split into per-cell sidecars plus
# .rc and .wall sidecars. Batches: base | com | load1 | load2 | par | all.
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-25}
mkdir -p runs
HOGS=""
RUN_PREFIX=()
trap 'stop_load' EXIT

make_proj() { # dir tps engine
  local dir="$1" tps="$2" engine="$3"
  rm -rf "$dir"; mkdir -p "$dir"
  {
    printf '%s\n' '[application]' 'config/name="MechanicOneShotTest"' \
      'config/features=PackedStringArray("4.7")'
    if [ -n "$tps" ] || [ -n "$engine" ]; then
      printf '%s\n' '' '[physics]'
      [ -n "$tps" ] && printf 'common/physics_ticks_per_second=%s\n' "$tps"
      [ -n "$engine" ] && printf '2d/physics_engine="%s"\n' "$engine"
    fi
  } > "$dir/project.godot"
  cp -f probes/b90.gd probes/b90_watch.gd "$dir/"
  cp -f probes/scout_rb_lattice.gd "$dir/scout_rb_lattice.gd"
  cp -f probes/scout_rb_watch.gd "$dir/rb_watch.gd"
}

make_proj proj "" ""
make_proj proj_tps30 30 ""
make_proj proj_tps120 120 ""
make_proj proj_tps240 240 ""
make_proj proj_dummy "" "Dummy"
make_proj proj_jolt2d "" "Jolt Physics"
make_proj proj_garbage "" "garbage_xyz"

_run_one() { # name script arm reps dir [extra...]
  local name="$1" script="$2" arm="$3" reps="$4" dir="${5:-proj}"
  shift 5 || true
  local extra=("$@")
  local i t0 t1 rc
  for i in $(seq 1 "$reps"); do
    t0=$(date +%s.%N)
    timeout -s KILL "$BOUND" ${RUN_PREFIX[@]+"${RUN_PREFIX[@]}"} "$GODOT" --headless --path "$dir" \
      --script "res://$script" -- "--arm=$arm" ${extra[@]+"${extra[@]}"} \
      > "runs/$name.rep$i.out" 2> "runs/$name.rep$i.err"
    rc=$?
    echo "$rc" > "runs/$name.rep$i.rc"
    t1=$(date +%s.%N)
    awk -v a="$t0" -v b="$t1" 'BEGIN{printf "%.2f\n", b-a}' > "runs/$name.rep$i.wall"
  done
}

run_cell() { # name arm reps dir [extra...]  (probe b90.gd)
  local name="$1" arm="$2" reps="$3" dir="${4:-proj}"
  shift 4 || true
  local extra=("$@")
  _run_one "$name" b90.gd "$arm" "$reps" "$dir" ${extra[@]+"${extra[@]}"}
}

run_cell_s() { # name script arm reps dir [extra...]  (verbatim scout probe)
  _run_one "$@"
}

run_par() { # name script arm reps dir [extra...] — reps concurrent processes
  local name="$1" script="$2" arm="$3" reps="$4" dir="${5:-proj}"
  shift 5 || true
  local extra=("$@")
  local i pids=""
  for i in $(seq 1 "$reps"); do
    (
      timeout -s KILL "$BOUND" "$GODOT" --headless --path "$dir" \
        --script "res://$script" -- "--arm=$arm" ${extra[@]+"${extra[@]}"} \
        > "runs/$name.rep$i.out" 2> "runs/$name.rep$i.err"
      echo "$?" > "runs/$name.rep$i.rc"
    ) &
    pids="$pids $!"
  done
  for p in $pids; do wait "$p"; done
}

start_load() { # n [cpu-list]
  local n="$1" cpu="${2:-}"
  HOGS=""
  local i
  for i in $(seq 1 "$n"); do
    if [ -n "$cpu" ]; then
      taskset -c "$cpu" yes > /dev/null &
    else
      yes > /dev/null &
    fi
    HOGS="$HOGS $!"
  done
  sleep 1
}

stop_load() {
  if [ -n "${HOGS:-}" ]; then
    kill $HOGS 2>/dev/null
    HOGS=""
  fi
}

note() { printf '%s\n' "$1" | tee -a runs/rc-summary.txt; }

batch_base() {
  note "== batch base started=$(date -u +%Y-%m-%dT%H:%M:%SZ) godot=$(timeout 20 "$GODOT" --version 2>&1 | tail -1) bound=$BOUND"
  run_cell b_order order 3 proj --frames=60
  run_cell b_order_t120 order 3 proj_tps120 --frames=60
  run_cell b_order_t30 order 3 proj_tps30 --frames=30
  run_cell b_write write 3 proj --frames=60
  run_cell b_lag_t60_n30 lag 3 proj --frames=30
  run_cell b_lag_t60_n60 lag 3 proj --frames=60
  run_cell b_lag_t30_n30 lag 3 proj_tps30 --frames=30
  run_cell b_lag_t30_n60 lag 3 proj_tps30 --frames=60
  run_cell b_lag_t120_n30 lag 3 proj_tps120 --frames=30
  run_cell b_lag_t120_n60 lag 3 proj_tps120 --frames=60
  run_cell b_lag_t120_n120 lag 3 proj_tps120 --frames=120
  run_cell b_lag_t240_n30 lag 3 proj_tps240 --frames=30
  run_cell b_damp damp 3 proj --frames=60
  run_cell b_damp_t120 damp 3 proj_tps120 --frames=120
  run_cell b_impulse impulse 3 proj
  run_cell b_backend_gp2d backend 3 proj
  run_cell b_backend_dummy backend 3 proj_dummy
  run_cell b_backend_jolt2d backend 3 proj_jolt2d
  run_cell b_backend_garbage backend 3 proj_garbage
  run_cell b_damp_dummy damp 3 proj_dummy --frames=60
  run_cell b_stall_none stall 3 proj --stall=none --stall_at=30 --frames=90
  run_cell b_stall_idle stall 3 proj --stall=idle --stall_at=30 --frames=90
  run_cell b_stall_phys stall 3 proj --stall=phys --stall_at=30 --frames=90
  run_cell b_settle settle 3 proj --frames=120
  run_cell_s sv_order scout_rb_lattice.gd order 3 proj --frames=60
  run_cell_s sv_damp scout_rb_lattice.gd damp 3 proj --frames=60
  run_cell_s sv_write scout_rb_lattice.gd write 3 proj --frames=60
  run_cell_s sv_impulse scout_rb_lattice.gd impulse 3 proj
  run_cell_s sv_comrefuse scout_rb_lattice.gd comrefuse 3 proj
  run_cell_s sv_freezelock scout_rb_lattice.gd freezelock 3 proj --frames=120
  run_cell_s sv_contacts scout_rb_lattice.gd contacts 3 proj --frames=60
  run_cell_s sv_gravity scout_rb_lattice.gd gravity 3 proj --frames=60
  run_cell_s sv_gravity_t120 scout_rb_lattice.gd gravity 3 proj_tps120 --frames=120
  note "== batch base finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

batch_com() {
  note "== batch com started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  local c
  for c in intree_auto_diff intree_auto_same intree_custom_diff frozen_static_auto_diff \
           frozen_kin_auto_diff frozen_static_custom_diff frozen_kin_custom_diff \
           nottree_auto_diff nottree_custom_diff set_via_set mode_invalid mode_neg \
           custom_freeze_sequence auto_nan custom_nan frozen_static_auto_then_mode \
           custom_back_auto_diff custom_dupe; do
    run_cell "b_com_$c" comcase 3 proj "--case=$c"
  done
  note "== batch com finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

batch_load1() {
  note "== batch load1 (32 system-wide hogs) started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  start_load 32
  run_cell l_order order 6 proj --frames=60
  run_cell l_order_t120 order 3 proj_tps120 --frames=60
  run_cell l_damp damp 3 proj --frames=60
  run_cell l_write write 3 proj --frames=60
  run_cell l_impulse impulse 3 proj
  run_cell_s l_sv_order scout_rb_lattice.gd order 3 proj --frames=60
  run_cell_s l_sv_freezelock scout_rb_lattice.gd freezelock 6 proj --frames=120
  run_cell_s l_sv_contacts scout_rb_lattice.gd contacts 6 proj --frames=60
  run_cell l_settle settle 3 proj --frames=120
  run_cell l_stall_idle stall 3 proj --stall=idle --stall_at=30 --frames=90
  stop_load
  note "== batch load1 finished=$(date -u +%Y-%m-%dT%H:%M:%SZ) load_stopped=1"
}

batch_load2() {
  note "== batch load2 (12 hogs pinned 0-3, godot pinned 0,1) started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  start_load 12 "0-3"
  RUN_PREFIX=(taskset -c 0,1)
  run_cell l2_order order 3 proj --frames=60
  run_cell_s l2_sv_order scout_rb_lattice.gd order 3 proj --frames=60
  run_cell_s l2_sv_freezelock scout_rb_lattice.gd freezelock 3 proj --frames=120
  run_cell_s l2_sv_contacts scout_rb_lattice.gd contacts 3 proj --frames=60
  run_cell l2_settle settle 3 proj --frames=120
  RUN_PREFIX=()
  stop_load
  note "== batch load2 finished=$(date -u +%Y-%m-%dT%H:%M:%SZ) load_stopped=1"
}

batch_delay() {
  note "== batch delay (startup-race positive control) started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  local d
  for d in 0 20 50 100 200 300; do
    run_cell "d_order_d$d" order 3 proj --frames=60 "--delay=$d"
  done
  note "== batch delay finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

batch_dummy() {
  note "== batch dummy (lattice under PhysicsServer2DDummy) started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  run_cell b_order_dummy order 3 proj_dummy --frames=60
  run_cell b_impulse_dummy impulse 3 proj_dummy
  run_cell_s sv_freezelock_dummy scout_rb_lattice.gd freezelock 3 proj_dummy --frames=120
  run_cell_s sv_contacts_dummy scout_rb_lattice.gd contacts 3 proj_dummy --frames=60
  note "== batch dummy finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

batch_t30() {
  note "== batch t30 (30 tps pairing race, N=9) started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  run_cell t30_order order 9 proj_tps30 --frames=30
  run_cell t30_lag lag 9 proj_tps30 --frames=30
  note "== batch t30 finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

batch_par() {
  note "== batch par (concurrent processes) started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  run_par p_order b90.gd order 8 proj --frames=60
  run_par p_sv_order scout_rb_lattice.gd order 6 proj --frames=60
  run_par p_sv_freezelock scout_rb_lattice.gd freezelock 6 proj --frames=120
  run_par p_sv_contacts scout_rb_lattice.gd contacts 6 proj --frames=60
  note "== batch par finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

case "${1:-all}" in
  base) batch_base ;;
  com) batch_com ;;
  load1) batch_load1 ;;
  load2) batch_load2 ;;
  delay) batch_delay ;;
  dummy) batch_dummy ;;
  t30) batch_t30 ;;
  par) batch_par ;;
  all) batch_base; batch_com; batch_load1; batch_load2; batch_delay; batch_dummy; batch_t30; batch_par ;;
  *) echo "unknown batch: $1" >&2; exit 2 ;;
esac

note "stray godot check (may include other lanes): $(pgrep -fa 'godot' | wc -l) procs"
