#!/usr/bin/env bash
# r93-scout loadtest — runtime cells under deliberate CPU load.
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-30}
mkdir -p runs/loadtest
HOGS=${HOGS:-16}
for i in $(seq 1 "$HOGS"); do (timeout 100 yes > /dev/null &) ; done
sleep 3
echo "load_before=$(cat /proc/loadavg)"
: > runs/loadtest/summary.txt
for spec in "tweenstep tweenstep" "tweenchain tweenchain" "tweenproc tweenproc" "animseek animseek" \
            "animmethod animmethod" "animblend animblend" "animproc animproc" "tweenval tweenval"; do
  set -- $spec
  for i in 1 2 3; do
    timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://anim_lattice.gd -- \
      "--arm=$2" > "runs/loadtest/r93_$1.rep$i.out" 2> "runs/loadtest/r93_$1.rep$i.err"
    echo "$?" > "runs/loadtest/r93_$1.rep$i.rc"
  done
  note="$1 rc=[$(cat runs/loadtest/r93_$1.rep*.rc | tr '\n' ' ')] out_uniq=$(sha256sum runs/loadtest/r93_$1.rep*.out | awk '{print $1}' | sort -u | wc -l) err_bytes=$(wc -c runs/loadtest/r93_$1.rep*.err | tail -1 | awk '{print $1}')"
  echo "$note" | tee -a runs/loadtest/summary.txt
done
pkill -x yes || true
sleep 1
echo "load_after=$(cat /proc/loadavg)"
