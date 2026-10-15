#!/usr/bin/env bash
# r92-boundary driver — attack the r92 TileMapLayer scout's 13 rows under
# quiet / >=12-hog load / --fixed-fps 30 / 60 / 120 (+ ff120+load) / 120-tps project,
# plus the seat's own frame-latency pollers (r92b_probe.gd: sched|phys|nav).
# Launch shape (battery): godot --headless [--fixed-fps N] --path <proj> \
#   --script res://<script> -- --arm=<arm>
# bounded by `timeout -s KILL $BOUND` (default 25); stdout/stderr split + .rc + .wall.
# Batches: quiet | load | ff30 | ff60 | ff120 | ff120load | tps120 | own
# Usage: bash run_matrix.sh [batch ...]        (no args = all)
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-25}
HOGS_N=${HOGS_N:-12}
mkdir -p runs
cp -f probes/*.gd proj/
cp -f probes/*.gd proj_tps120/ 2>/dev/null || true

SCOUT_SCRIPT=scout_tilemap_lattice.gd
MY_SCRIPT=r92b_probe.gd
ARMS="census atlas cells custom terrain pattern encoding fixinvalid srcids physics timing quadrant nav"
MY_ARMS="sched phys nav"

FF_ARGS=()
PROJ=proj
HOGS=""
trap 'stop_load' EXIT

stop_load() { if [ -n "${HOGS:-}" ]; then kill $HOGS 2>/dev/null; HOGS=""; sleep 1; fi; }
start_load() { local n="$1" i; HOGS=""; for i in $(seq 1 "$n"); do yes > /dev/null & HOGS="$HOGS $!"; done; sleep 2; }

note() { printf '%s\n' "$1" | tee -a runs/rc-summary.txt; }

_run() { # name script arm reps
  local name="$1" script="$2" arm="$3" reps="$4" i rc t0 t1
  for i in $(seq 1 "$reps"); do
    t0=$(date +%s.%N)
    timeout -s KILL "$BOUND" "$GODOT" --headless ${FF_ARGS[@]+"${FF_ARGS[@]}"} --path "$PROJ" \
      --script "res://$script" -- "--arm=$arm" \
      > "runs/$name.rep$i.out" 2> "runs/$name.rep$i.err"
    rc=$?
    echo "$rc" > "runs/$name.rep$i.rc"
    t1=$(date +%s.%N)
    awk -v a="$t0" -v b="$t1" 'BEGIN{printf "%.2f\n", b-a}' > "runs/$name.rep$i.wall"
  done
}

cells() { # tag reps
  local tag="$1" reps="$2" a
  for a in $ARMS; do _run "$tag$a" "$SCOUT_SCRIPT" "$a" "$reps"; done
}

own() { # tag reps
  local tag="$1" reps="$2" a
  for a in $MY_ARMS; do _run "$tag$a" "$MY_SCRIPT" "$a" "$reps"; done
}

hdr() {
  note "== batch $1 started=$(date -u +%Y-%m-%dT%H:%M:%SZ) godot=$(timeout 20 "$GODOT" --version 2>&1 | tail -1) bound=$BOUND ff=[${FF_ARGS[@]+"${FF_ARGS[@]}"}] proj=$PROJ"
  note "loadavg_start=$(cat /proc/loadavg) yes_hogs_now=$(pgrep -c -x yes || echo 0)"
}

ftr() {
  note "loadavg_end=$(cat /proc/loadavg) yes_hogs_now=$(pgrep -c -x yes || echo 0)"
  note "== batch $1 finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

batch_quiet() {
  FF_ARGS=(); PROJ=proj; hdr quiet
  cells q60_ 3
  own oq_ 2
  ftr quiet
}

batch_load() {
  FF_ARGS=(); PROJ=proj; start_load "$HOGS_N"; hdr load
  cells l60_ 3
  own ol_ 2
  stop_load
  ftr load
}

batch_ff30() {
  FF_ARGS=(--fixed-fps 30); PROJ=proj; hdr ff30
  cells f30_ 3
  own of30_ 2
  ftr ff30
}

batch_ff60() {
  FF_ARGS=(--fixed-fps 60); PROJ=proj; hdr ff60
  cells f60_ 3
  own of60_ 2
  ftr ff60
}

batch_ff120() {
  FF_ARGS=(--fixed-fps 120); PROJ=proj; hdr ff120
  cells f120_ 3
  own of120_ 2
  ftr ff120
}

batch_ff120load() {
  FF_ARGS=(--fixed-fps 120); PROJ=proj; start_load "$HOGS_N"; hdr ff120load
  cells f120l_ 2
  own of120l_ 2
  stop_load
  ftr ff120load
}

batch_tps120() {
  FF_ARGS=(); PROJ=proj_tps120; hdr tps120
  cells t120_ 3
  own ot120_ 2
  ftr tps120
}

# --- scheduler-extreme + repeat + heavy-load additions (r92b second wave) ---------

batch_q60b() {
  FF_ARGS=(); PROJ=proj; hdr q60b
  cells q60b_ 2
  own oq60b_ 2
  ftr q60b
}

batch_ff10() {
  FF_ARGS=(--fixed-fps 10); PROJ=proj; hdr ff10
  cells f10_ 2
  own of10_ 2
  ftr ff10
}

batch_ff20() {
  FF_ARGS=(--fixed-fps 20); PROJ=proj; hdr ff20
  cells f20_ 2
  own of20_ 2
  ftr ff20
}

batch_ff600() {
  FF_ARGS=(--fixed-fps 600); PROJ=proj; hdr ff600
  cells f600_ 2
  own of600_ 2
  ftr ff600
}

batch_ff30load() {
  FF_ARGS=(--fixed-fps 30); PROJ=proj; start_load "$HOGS_N"; hdr ff30load
  cells f30l_ 2
  own of30l_ 2
  stop_load
  ftr ff30load
}

batch_load32() {
  FF_ARGS=(); PROJ=proj; start_load 32; hdr load32
  cells l32_ 2
  own ol32_ 2
  stop_load
  ftr load32
}

[ -f runs/rc-summary.txt ] || : > runs/rc-summary.txt
note "r92-boundary matrix wave start=$(date -u +%Y-%m-%dT%H:%M:%SZ) host=$(uname -n) nproc=$(nproc) batches=[$*]"
note "ambient_yes_hogs_at_start=$(pgrep -c -x yes || echo 0) ambient_loadavg=$(cat /proc/loadavg)"

if [ "$#" -eq 0 ]; then set -- quiet load ff30 ff60 ff120 ff120load tps120; fi
for b in "$@"; do "batch_$b"; done

note "matrix end=$(date -u +%Y-%m-%dT%H:%M:%SZ) loadavg=$(cat /proc/loadavg) yes_hogs_now=$(pgrep -c -x yes || echo 0)"
echo "--- stray godot check (may include other lanes) ---"
pgrep -fa "godot" | head -5 || echo "none"
echo "--- rc summary tail ---"
tail -5 runs/rc-summary.txt
