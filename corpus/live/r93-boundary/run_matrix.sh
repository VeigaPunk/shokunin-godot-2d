#!/usr/bin/env bash
# r93b boundary driver — attack the r93 Anim+Tween scout claims under
# quiet / 16-hog load / 32-hog load / --fixed-fps 30/60/120 (+ ff120+load).
# Launch shape (battery): godot --headless [--fixed-fps N] --path proj \
#   --script res://<script> -- --arm=<arm>
# bounded by `timeout -s KILL 25`; stdout/stderr split + .rc + .wall sidecars.
# Batches: q | l | f30 | f60 | f120 | f120l | l32 | all
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-25}
mkdir -p runs
HOGS=""
FF=()
trap 'stop_load' EXIT
trap 'stop_load; exit 130' INT TERM

# Only this seat's own hogs are ever killed (marker arg `r93b-hog`); other lanes' hogs untouched.
stop_load() { if [ -n "${HOGS:-}" ]; then kill $HOGS 2>/dev/null; HOGS=""; sleep 0.5; fi; }
start_load() {
  local n="$1" i
  HOGS=""
  for i in $(seq 1 "$n"); do yes r93b-hog > /dev/null & HOGS="$HOGS $!"; done
  sleep 1
}

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

scout_cells() { # tag reps
  [ "${CELLS:-both}" = "attack" ] && return 0
  local tag="$1" reps="$2"
  for arm in census tweenval tweenval_grid animtrack tweenstep tweenchain tweenproc \
             animseek animmethod animblend animproc; do
    _run "$tag$arm" scout_anim_lattice.gd "$arm" "$reps"
  done
}

attack_cells() { # tag reps
  [ "${CELLS:-both}" = "scout" ] && return 0
  local tag="$1" reps="$2"
  for arm in clock manual_inv frame deferred purity blend; do
    _run "$tag$arm" r93b_anim.gd "$arm" "$reps"
  done
}

mode_cells() { # tag reps — the frame-coupled + manual-clock subset only
  [ "${CELLS:-both}" = "attack" ] && return 0
  local tag="$1" reps="$2"
  for arm in tweenstep tweenproc animseek animproc; do
    _run "$tag$arm" scout_anim_lattice.gd "$arm" "$reps"
  done
}

batch_q() {
  note "== batch q (no seat hogs) started=$(date -u +%Y-%m-%dT%H:%M:%SZ) godot=$(timeout 20 "$GODOT" --version 2>&1 | tail -1) bound=$BOUND"
  note "loadavg_start=$(cat /proc/loadavg) my_hogs=$(pgrep -fc 'yes r93b-hog' || true)"
  scout_cells q_ 3
  attack_cells q_ 3
  note "loadavg_end=$(cat /proc/loadavg)"
  note "== batch q finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

batch_l() {
  note "== batch l (16 seat hogs + ambient) started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  start_load 16
  note "loadavg_start=$(cat /proc/loadavg) my_hogs=$(pgrep -fc 'yes r93b-hog')"
  scout_cells l_ 3
  attack_cells l_ 3
  stop_load
  note "loadavg_end=$(cat /proc/loadavg) my_hogs_after_stop=$(pgrep -fc 'yes r93b-hog' || true)"
  note "== batch l finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

batch_ff() { # tag fps reps [with_load]
  local tag="$1" fps="$2" reps="$3" load="${4:-0}"
  if [ "$load" = "1" ]; then
    start_load 16
    note "== batch $tag (--fixed-fps $fps + 16 seat hogs) started=$(date -u +%Y-%m-%dT%H:%M:%SZ) my_hogs=$(pgrep -fc 'yes r93b-hog')"
  else
    note "== batch $tag (--fixed-fps $fps) started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  fi
  FF=(--fixed-fps "$fps")
  note "loadavg_start=$(cat /proc/loadavg)"
  scout_cells "$tag" "$reps"
  attack_cells "$tag" "$reps"
  FF=()
  if [ "$load" = "1" ]; then
    stop_load
    note "my_hogs_after_stop=$(pgrep -fc 'yes r93b-hog' || true)"
  fi
  note "loadavg_end=$(cat /proc/loadavg)"
  note "== batch $tag finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

batch_l32() {
  note "== batch l32 (32 seat hogs on 32 cores + ambient) started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  start_load 32
  note "loadavg_start=$(cat /proc/loadavg) my_hogs=$(pgrep -fc 'yes r93b-hog')"
  mode_cells l32_ 2
  attack_cells l32_ 2
  stop_load
  note "loadavg_end=$(cat /proc/loadavg) my_hogs_after_stop=$(pgrep -fc 'yes r93b-hog' || true)"
  note "== batch l32 finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

batch_p() {
  # purity-arm re-run (extended overshoot lanes) across every condition: 16 runs.
  note "== batch p (purity only, extended) started=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  note "loadavg_start=$(cat /proc/loadavg)"
  _run q_purity r93b_anim.gd purity 3
  start_load 16
  note "load16_start loadavg=$(cat /proc/loadavg) my_hogs=$(pgrep -fc 'yes r93b-hog')"
  _run l_purity r93b_anim.gd purity 3
  stop_load
  for spec in "f30_ 30 2 0" "f60_ 60 2 0" "f120_ 120 2 0" "f120l_ 120 2 1"; do
    set -- $spec
    FF=(--fixed-fps "$2")
    [ "$4" = "1" ] && start_load 16
    note "sub-batch $1 loadavg=$(cat /proc/loadavg)"
    _run "$1purity" r93b_anim.gd purity "$3"
    [ "$4" = "1" ] && stop_load
    FF=()
  done
  start_load 32
  note "load32_start loadavg=$(cat /proc/loadavg) my_hogs=$(pgrep -fc 'yes r93b-hog')"
  _run l32_purity r93b_anim.gd purity 2
  stop_load
  note "loadavg_end=$(cat /proc/loadavg) my_hogs_after_stop=$(pgrep -fc 'yes r93b-hog' || true)"
  note "== batch p finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

case "${1:-all}" in
  q) batch_q ;;
  l) batch_l ;;
  f30) batch_ff f30_ 30 2 0 ;;
  f60) batch_ff f60_ 60 2 0 ;;
  f120) batch_ff f120_ 120 2 0 ;;
  f120l) batch_ff f120l_ 120 2 1 ;;
  l32) batch_l32 ;;
  p) batch_p ;;
  all) batch_q; batch_l; batch_ff f30_ 30 2 0; batch_ff f60_ 60 2 0; batch_ff f120_ 120 2 0; batch_ff f120l_ 120 2 1; batch_l32 ;;
  *) echo "unknown batch: $1" >&2; exit 2 ;;
esac
echo "--- stray godot check (may include other lanes) ---"
pgrep -fa "godot" | head -20 || echo "none"
echo "--- my hogs after run ---"
pgrep -fc 'yes r93b-hog' || echo "0"
