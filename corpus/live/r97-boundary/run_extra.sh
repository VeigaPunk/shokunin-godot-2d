#!/usr/bin/env bash
# r97-boundary secondary driver — the two r97b_extra arms (order_churn,
# unique_boundary) under a subset of modes.  Kept separate from run_modes.sh
# because those receipts belong to probes/r97b_extra.gd, not to the frozen
# probes/r97b_lattice.gd revision used for the 324-receipt matrix.
#
#   bash run_extra.sh <mode> [reps]      mode: quiet | load | ff60
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-25}
MODE=${1:?usage: run_extra.sh <mode> [reps]}
REPS=${2:-3}
case "$MODE" in
  quiet) EXTRA="" ;;
  load)  EXTRA="" ;;
  ff60)  EXTRA="--fixed-fps 60" ;;
  *) echo "unknown mode $MODE"; exit 2 ;;
esac
mkdir -p "runs/$MODE"
cp -f probes/r97b_extra.gd proj/

HOG_PIDS=()
HOGFILE="runs/$MODE/hogs_extra.txt"
{
  echo "mode=$MODE extra=[$EXTRA] reps=$REPS bound=$BOUND script=r97b_extra.gd"
  echo "loadavg_start=$(cut -d' ' -f1-3 /proc/loadavg)"
} > "$HOGFILE"
if [ "$MODE" = "load" ]; then
  for i in $(seq 1 12); do
    yes > /dev/null &
    HOG_PIDS+=("$!")
  done
  echo "own_hogs=${#HOG_PIDS[@]} pids=${HOG_PIDS[*]}" >> "$HOGFILE"
fi

run_cell() { # tag arm
  local tag="$1" arm="$2" i
  for i in $(seq 1 "$REPS"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless $EXTRA --path proj --script res://r97b_extra.gd -- \
      "--arm=$arm" > "runs/$MODE/${tag}.rep$i.out" 2> "runs/$MODE/${tag}.rep$i.err"
    echo "$?" > "runs/$MODE/${tag}.rep$i.rc"
  done
}

run_cell r97b_order_churn order_churn
run_cell r97b_unique_boundary unique_boundary

if [ "$MODE" = "load" ]; then
  killed=0
  for pid in "${HOG_PIDS[@]}"; do
    if kill "$pid" 2>/dev/null; then killed=$((killed + 1)); fi
  done
  echo "own_hogs_killed=$killed" >> "$HOGFILE"
  echo "host_yes_remaining=$(pgrep -c '^yes$' || true)" >> "$HOGFILE"
fi
echo "loadavg_end=$(cut -d' ' -f1-3 /proc/loadavg)" >> "$HOGFILE"
echo "mode=$MODE extra done: $(ls runs/$MODE/r97b_*_boundary.rep*.out runs/$MODE/r97b_order_churn.rep*.out 2>/dev/null | wc -l) receipts"
