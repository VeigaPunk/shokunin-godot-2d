#!/usr/bin/env bash
# extra evidence: (a) seedcheck/fresh2 mechanism receipts, (b) pack_basic flip-rate scan
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-25}
mkdir -p runs/extra
cp -f probes/*.gd proj/
for arm in seedcheck fresh2; do
  for i in 1 2 3; do
    timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://r96b_seed.gd -- "--arm=$arm" \
      > "runs/extra/seed_$arm.rep$i.out" 2> "runs/extra/seed_$arm.rep$i.err"
    echo "$?" > "runs/extra/seed_$arm.rep$i.rc"
  done
done
for i in $(seq 1 150); do
  timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://scene_io_lattice.gd -- "--arm=pack_basic" \
    > "runs/extra/flip_pack_basic.rep$i.out" 2> "runs/extra/flip_pack_basic.rep$i.err"
  echo "$?" > "runs/extra/flip_pack_basic.rep$i.rc"
done
echo "flip_false=$(grep -L 'size_in_190_200=true' runs/extra/flip_pack_basic.rep*.out | wc -l) of 150"
grep -h "^PASS" runs/extra/flip_pack_basic.rep*.out | sed 's/.*size_in_190_200=\([a-z]*\).*/\1/' | sort | uniq -c
echo "finished=$(date -u +%Y-%m-%dT%H:%M:%SZ) loadavg=$(cat /proc/loadavg | cut -d' ' -f1-3)"
