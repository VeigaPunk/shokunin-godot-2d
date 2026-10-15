#!/usr/bin/env bash
# r91b boundary driver — attack the r91 Navigation2D scout claims under
# quiet / 16-hog load / --fixed-fps 30 / --fixed-fps 120 (+ ff120+load).
# Launch shape (battery): godot --headless [--fixed-fps N] --path proj \
#   --script res://<script> -- --arm=<arm>
# bounded by `timeout -s KILL 25`; stdout/stderr split + .rc + .wall sidecars.
# Batches: quiet | load | ff30 | ff120 | ff120load | quiet2 | all
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

_run() { # name script arm reps
  local name="$1" script="$2" arm="$3" reps="$4"
  local i rc t0 t1
  for i in $(seq 1 "$reps"); do
    t0=$(date +%s.%N)
    timeout -s KILL "$BOUND" "$GODOT" --headless ${FF[@]+"${FF[@]}"} --path proj \
      --script "res://$script" -- "--arm=$arm" \
      > "runs/$name.rep$i.out" 2> "runs/$name.rep$i.err"
    rc=$?
    echo "$rc" > "runs/$name.rep$i.rc"
    t1=$(date +%s.%N)
    awk -v a="$t0" -v b="$t1" 'BEGIN{printf "%.2f\n", b-a}' > "runs/$name.rep$i.wall"
  done
}

# Full claim set: 5 scout-verbatim cells + 5 attack cells + 4 agent-diag variants + 6 teardown arms.
cells() { # tag reps
  local tag="$1" reps="$2"
  for spec in \
      "sv_sync scout_nav_lattice.gd sync" "sv_region scout_nav_lattice.gd region" \
      "sv_agent scout_nav_lattice.gd agent" "sv_avoid scout_nav_lattice.gd avoid" \
      "sv_bake scout_nav_lattice.gd bake" \
      "b_gate r91b_nav.gd gate" "b_change r91b_nav.gd change" "b_agent r91b_nav.gd agent" \
      "b_avoid r91b_nav.gd avoid" "b_bake r91b_nav.gd bake" \
      "d_v1 r91b_agent_diag.gd v1" "d_v5 r91b_agent_diag.gd v5" \
      "d_v7 r91b_agent_diag.gd v7" "d_v8 r91b_agent_diag.gd v8" \
      "c_noclear r91b_nav.gd crash_noclear" "c_clear0 r91b_nav.gd crash_clear0" \
      "c_clear1 r91b_nav.gd clean_clear1" "c_clear2 r91b_nav.gd clean_clear2" \
      "c_leak_cb r91b_nav.gd leak_cb" "c_leak_clean r91b_nav.gd leak_clean"; do
    set -- $spec
    _run "$tag$1" "$2" "$3" "$reps"
  done
}

# Mode-prone subset for the repeat window.
cells2() { # tag reps
  local tag="$1" reps="$2"
  for spec in \
      "b_gate r91b_nav.gd gate" "b_change r91b_nav.gd change" "b_agent r91b_nav.gd agent" \
      "b_avoid r91b_nav.gd avoid" "d_v1 r91b_agent_diag.gd v1" "d_v5 r91b_agent_diag.gd v5"; do
    set -- $spec
    _run "$tag$1" "$2" "$3" "$reps"
  done
}

batch_quiet() {
  note "== batch quiet started=$(date -u +%Y-%m-%dT%H:%M:%SZ) godot=$(timeout 20 "$GODOT" --version 2>&1 | tail -1) bound=$BOUND"
  note "loadavg_start=$(cat /proc/loadavg)"
  cells q_ 3
  note "loadavg_end=$(cat /proc/loadavg)"
  note "== batch quiet finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

batch_load() {
  note "== batch load (16 system-wide yes hogs + ambient) started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  start_load 16
  note "loadavg_start=$(cat /proc/loadavg) my_hogs=$(pgrep -c -x yes)"
  cells l_ 5
  stop_load
  note "loadavg_end=$(cat /proc/loadavg) my_hogs_after_stop=$(pgrep -c -x yes)"
  note "== batch load finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

batch_ff30() {
  FF=(--fixed-fps 30)
  note "== batch ff30 started=$(date -u +%Y-%m-%dT%H:%M:%SZ) ff=${FF[*]}"
  note "loadavg_start=$(cat /proc/loadavg)"
  cells f30_ 3
  FF=()
  note "== batch ff30 finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

batch_ff120() {
  FF=(--fixed-fps 120)
  note "== batch ff120 started=$(date -u +%Y-%m-%dT%H:%M:%SZ) ff=${FF[*]}"
  note "loadavg_start=$(cat /proc/loadavg)"
  cells f120_ 3
  FF=()
  note "== batch ff120 finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

batch_ff120load() {
  note "== batch ff120load (--fixed-fps 120 + 16 hogs) started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  start_load 16
  FF=(--fixed-fps 120)
  note "loadavg_start=$(cat /proc/loadavg) my_hogs=$(pgrep -c -x yes)"
  cells f120l_ 3
  FF=()
  stop_load
  note "loadavg_end=$(cat /proc/loadavg)"
  note "== batch ff120load finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

batch_quiet2() {
  note "== batch quiet2 (repeat window, mode-prone subset) started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  note "loadavg_start=$(cat /proc/loadavg)"
  cells2 q2_ 3
  note "loadavg_end=$(cat /proc/loadavg)"
  note "== batch quiet2 finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

# Paired, interleaved A/B in one window: default vs --fixed-fps 30/60/120.
# ff60 is the ratio control (1 idle : 1 physics, like default) — if it stalls like
# ff30/ff120, the cause is the fixed-fps mode itself, not the tps ratio.
batch_ab() {
  note "== batch ab (paired default vs ff30/ff60/ff120) started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  note "loadavg_start=$(cat /proc/loadavg)"
  local i
  for i in 1 2 3 4 5 6; do
    FF=(); _run "ab${i}_def" r91b_nav.gd gate 1
    FF=(--fixed-fps 30); _run "ab${i}_f30" r91b_nav.gd gate 1
    FF=(--fixed-fps 60); _run "ab${i}_f60" r91b_nav.gd gate 1
    FF=(--fixed-fps 120); _run "ab${i}_f120" r91b_nav.gd gate 1
  done
  FF=()
  note "loadavg_end=$(cat /proc/loadavg)"
  note "== batch ab finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

# Independent crash-class reproduction with the SCOUT's own discovery arms
# (navfree2 clear+free same frame, navfree5 two-agent callback free, navfree6 clear+1 frame+free).
# Runs against the scout's frozen proj dir (read-only: godot --script writes nothing).
batch_disc() {
  note "== batch disc (scout discover.gd crash class, 3 reps) started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  note "loadavg_start=$(cat /proc/loadavg)"
  local arm i rc t0 t1
  for arm in navfree2 navfree5 navfree6; do
    for i in 1 2 3; do
      t0=$(date +%s.%N)
      timeout -s KILL "$BOUND" "$GODOT" --headless --path ../r91-scout/proj \
        --script res://discover.gd -- "--arm=$arm" \
        > "runs/dc_$arm.rep$i.out" 2> "runs/dc_$arm.rep$i.err"
      rc=$?
      echo "$rc" > "runs/dc_$arm.rep$i.rc"
      t1=$(date +%s.%N)
      awk -v a="$t0" -v b="$t1" 'BEGIN{printf "%.2f\n", b-a}' > "runs/dc_$arm.rep$i.wall"
    done
  done
  note "loadavg_end=$(cat /proc/loadavg)"
  note "== batch disc finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

# Single-frame triple-read proof (v9) + discriminating bent-path lane, quiet and loaded.
batch_diag2() {
  note "== batch diag2 (v9 triple + bent) started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  note "loadavg_start=$(cat /proc/loadavg)"
  _run q_d_v9 r91b_agent_diag.gd v9 3
  _run q_d_bent r91b_agent_diag.gd bent 3
  start_load 16
  note "loadavg_load=$(cat /proc/loadavg) my_hogs=$(pgrep -c -x yes)"
  _run l_d_v9 r91b_agent_diag.gd v9 3
  _run l_d_bent r91b_agent_diag.gd bent 3
  stop_load
  note "loadavg_end=$(cat /proc/loadavg)"
  note "== batch diag2 finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

case "${1:-all}" in
  quiet) batch_quiet ;;
  load) batch_load ;;
  ff30) batch_ff30 ;;
  ff120) batch_ff120 ;;
  ff120load) batch_ff120load ;;
  quiet2) batch_quiet2 ;;
  ab) batch_ab ;;
  disc) batch_disc ;;
  diag2) batch_diag2 ;;
  all) batch_quiet; batch_load; batch_ff30; batch_ff120; batch_ff120load; batch_quiet2; batch_ab; batch_disc; batch_diag2 ;;
  *) echo "unknown batch: $1" >&2; exit 2 ;;
esac

note "timeout_hits=$(grep -l '^137$' runs/*.rc 2>/dev/null | wc -l) over=$(ls runs/*.rc 2>/dev/null | wc -l)"
note "stray godot from this lane (may include other lanes): $(pgrep -fa 'r91-boundary' | wc -l)"
note "my yes hogs left: $(pgrep -c -x yes)"
