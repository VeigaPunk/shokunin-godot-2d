#!/usr/bin/env bash
# r95b boundary driver — the r95 scout's multi-hit ordering claims under
# quiet / 16-hog load / --fixed-fps 1/30/120 / threaded physics (unstated mode).
#
#   bash run_matrix.sh quiet|load|ff1|ff30|ff120|thr
#
# Every run is `timeout -s KILL 25`-bounded (BOUND), stdout/stderr split into
# per-cell sidecars plus .rc and .wall_ms.  Hogs are this seat's own only and are
# killed by the EXIT trap (never pkill: other lanes run their own `yes` blocks).
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-25}
BATCH=${1:-quiet}
HOGS=${HOGS:-16}
PROJ=proj
FF=""
case "$BATCH" in
  quiet) ;;
  load) ;;
  ff1) FF="--fixed-fps 1" ;;
  ff30) FF="--fixed-fps 30" ;;
  ff120) FF="--fixed-fps 120" ;;
  thr) PROJ=proj_thr ;;
  label) ;;
  extra) ;;
  *) echo "unknown batch: $BATCH" >&2; exit 2 ;;
esac
mkdir -p "runs/$BATCH"
cp -f probes/r95b_order.gd "$PROJ"/

HOG_PIDS=""
stop_load() {
  for p in $HOG_PIDS; do kill "$p" 2>/dev/null || true; done
  HOG_PIDS=""
}
trap 'stop_load' EXIT

if [ "$BATCH" = "load" ]; then
  for i in $(seq 1 "$HOGS"); do yes > /dev/null & HOG_PIDS="$HOG_PIDS $!"; done
  sleep 2
fi

specs() {
  case "$BATCH" in
    quiet) cat <<'EOF'
canon|6|--arm=canon
perm0|3|--arm=perm --perm=0
perm1|3|--arm=perm --perm=1
perm2|3|--arm=perm --perm=2
perm3|3|--arm=perm --perm=3
perm4|3|--arm=perm --perm=4
perm5|3|--arm=perm --perm=5
perm6|3|--arm=perm --perm=6
perm7|3|--arm=perm --perm=7
warm_k0|2|--arm=warm --k=0 --keep=0
warm_k1|2|--arm=warm --k=1 --keep=0
warm_k2|2|--arm=warm --k=2 --keep=0
warm_k3|2|--arm=warm --k=3 --keep=0
warm_k5|2|--arm=warm --k=5 --keep=0
warm_k8|2|--arm=warm --k=8 --keep=0
warm_k13|2|--arm=warm --k=13 --keep=0
warm_k32|2|--arm=warm --k=32 --keep=0
warm_keep8|2|--arm=warm --k=8 --keep=1
warm_keep64|2|--arm=warm --k=64 --keep=1
free_a|2|--arm=free --which=a
free_b|2|--arm=free --which=b
free_c|2|--arm=free --which=c
free_d|2|--arm=free --which=d
free_e|2|--arm=free --which=e
free_ab|2|--arm=free --order=ab
free_ba|2|--arm=free --order=ba
free_ac|2|--arm=free --order=ac
free_ca|2|--arm=free --order=ca
readd_a|2|--arm=readd --which=a
readd_c|2|--arm=readd --which=c
cap40_p0|3|--arm=cap40 --perm=0
cap40_p1|3|--arm=cap40 --perm=1
cap40_p2|3|--arm=cap40 --perm=2
layers_k0|3|--arm=layers --k=0
layers_k1|3|--arm=layers --k=1
celloff_x0|3|--arm=celloff --off=0
celloff_x0.25|3|--arm=celloff --off=0.25
celloff_x0.5|2|--arm=celloff --off=0.5
celloff_x1|1|--arm=celloff --off=1
celloff_x2|1|--arm=celloff --off=2
celloff_x4|1|--arm=celloff --off=4
celloff_x8|1|--arm=celloff --off=8
celloff_x16|1|--arm=celloff --off=16
celloff_x32|1|--arm=celloff --off=32
celloff_x64|1|--arm=celloff --off=64
celloff_x1000|1|--arm=celloff --off=1000
celloff_xm1000|1|--arm=celloff --off=-1000
celloff_xm0.25|2|--arm=celloff --off=-0.25
celloff_y1000|3|--arm=celloff --off=0 --offy=1000
rigid|3|--arm=rigid
procwait|4|--arm=procwait
period_k2|2|--arm=period --k=2
period_k3|2|--arm=period --k=3
period_k4|2|--arm=period --k=4
period_k6|2|--arm=period --k=6
period_k8|2|--arm=period --k=8
twopiles|4|--arm=twopiles
env|2|--arm=env
EOF
    ;;
    load) cat <<'EOF'
canon|4|--arm=canon
perm0|2|--arm=perm --perm=0
perm1|2|--arm=perm --perm=1
perm2|2|--arm=perm --perm=2
perm4|2|--arm=perm --perm=4
warm_k1|2|--arm=warm --k=1 --keep=0
warm_k32|2|--arm=warm --k=32 --keep=0
warm_keep8|2|--arm=warm --k=8 --keep=1
warm_keep64|2|--arm=warm --k=64 --keep=1
free_c|2|--arm=free --which=c
free_ab|2|--arm=free --order=ab
free_ba|2|--arm=free --order=ba
readd_a|2|--arm=readd --which=a
cap40_p0|2|--arm=cap40 --perm=0
cap40_p1|2|--arm=cap40 --perm=1
layers_k1|2|--arm=layers --k=1
celloff_x0|2|--arm=celloff --off=0
celloff_x0.25|2|--arm=celloff --off=0.25
celloff_x1000|2|--arm=celloff --off=1000
celloff_y1000|2|--arm=celloff --off=0 --offy=1000
rigid|2|--arm=rigid
procwait|3|--arm=procwait
period_k5|2|--arm=period --k=5
twopiles|3|--arm=twopiles
env|1|--arm=env
EOF
    ;;
    ff1) cat <<'EOF'
canon|2|--arm=canon
perm0|1|--arm=perm --perm=0
celloff_x0|1|--arm=celloff --off=0
procwait|3|--arm=procwait
period_k5|1|--arm=period --k=5
EOF
    ;;
    ff30|ff120) cat <<'EOF'
canon|3|--arm=canon
perm0|2|--arm=perm --perm=0
perm1|2|--arm=perm --perm=1
celloff_x0|1|--arm=celloff --off=0
celloff_x1000|1|--arm=celloff --off=1000
procwait|3|--arm=procwait
period_k5|2|--arm=period --k=5
cap40_p0|1|--arm=cap40 --perm=0
layers_k1|1|--arm=layers --k=1
EOF
    ;;
    extra) cat <<'EOF'
canon|2|--arm=canon
periodx_k2|2|--arm=periodx --k=2
periodx_k3|2|--arm=periodx --k=3
periodx_k4|1|--arm=periodx --k=4
periodx_k5|2|--arm=periodx --k=5
periodx_k5s8|2|--arm=periodx --k=5 --spacing=8
periodx_k6|1|--arm=periodx --k=6
periodx_k7|1|--arm=periodx --k=7
periodx_k8|1|--arm=periodx --k=8
periodx_k10|1|--arm=periodx --k=10
EOF
    ;;
    label) cat <<'EOF'
scoutrev|4|--arm=scoutrev
perm0|2|--arm=perm --perm=0
perm1|2|--arm=perm --perm=1
EOF
    ;;
    thr) cat <<'EOF'
canon|4|--arm=canon
perm0|2|--arm=perm --perm=0
perm1|2|--arm=perm --perm=1
period_k5|2|--arm=period --k=5
twopiles|2|--arm=twopiles
env|1|--arm=env
EOF
    ;;
  esac
}

: > "runs/$BATCH/rc-summary.txt"
note() { printf '%s\n' "$1" >> "runs/$BATCH/rc-summary.txt"; }
note "batch=$BATCH proj=$PROJ ff='${FF:-none}' hogs=${HOGS} bound=${BOUND} godot=$(timeout 20 "$GODOT" --version 2>&1 | tail -1)"
note "started=$(date -u +%Y-%m-%dT%H:%M:%SZ) load=$(cut -d' ' -f1-3 /proc/loadavg)"

specs | while IFS='|' read -r cell reps args; do
  [ -z "$cell" ] && continue
  for i in $(seq 1 "$reps"); do
    t0=$(date +%s%N)
    # shellcheck disable=SC2086
    timeout -s KILL "$BOUND" "$GODOT" --headless $FF --path "$PROJ" --script res://r95b_order.gd -- $args \
      > "runs/$BATCH/$cell.rep$i.out" 2> "runs/$BATCH/$cell.rep$i.err"
    echo "$?" > "runs/$BATCH/$cell.rep$i.rc"
    echo $(( ($(date +%s%N) - t0) / 1000000 )) > "runs/$BATCH/$cell.rep$i.wall_ms"
  done
  note "$cell reps=$reps rc=[$(cat runs/$BATCH/$cell.rep*.rc | tr '\n' ' ')] args='$args'"
done

note "finished=$(date -u +%Y-%m-%dT%H:%M:%SZ) load=$(cut -d' ' -f1-3 /proc/loadavg)"
stop_load
echo "--- $BATCH done; rc summary tail:"
tail -3 "runs/$BATCH/rc-summary.txt"
echo "--- timeout check (rc=137): $(grep -rl 137 runs/$BATCH/*.rc 2>/dev/null | wc -l)"
echo "--- stray probes: $(pgrep -fc 'r95b_order' || true)"
