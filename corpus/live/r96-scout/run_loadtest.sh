#!/usr/bin/env bash
# r96-scout load-stability driver: 3 reps of all 13 cells under own-hog load.
# Only this script's own `yes` PIDs are killed (never `pkill -x yes`).
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-30}
HOGS=${HOGS:-16}
mkdir -p runs/loadtest
cp -f probes/scene_io_lattice.gd proj/

pids=""
for i in $(seq 1 "$HOGS"); do
  yes > /dev/null &
  pids="$pids $!"
done
echo "own_hogs=$(echo $pids | wc -w) pids=$pids" | tee runs/loadtest/loadtest-summary.txt
sleep 3
echo "loadavg_before=$(cut -d' ' -f1-3 /proc/loadavg)" | tee -a runs/loadtest/loadtest-summary.txt

for spec in "census census" "pack_basic pack_basic" "ownership ownership" "formats formats" \
            "det det" "uid uid" "takeover takeover" "cache cache" "subres subres" \
            "extres extres" "editstate editstate" "refuse refuse" "edges edges"; do
  set -- $spec
  name="$1"; arm="$2"
  for i in 1 2 3; do
    timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://scene_io_lattice.gd -- \
      "--arm=$arm" > "runs/loadtest/${name}.rep$i.out" 2> "runs/loadtest/${name}.rep$i.err"
    echo "$?" > "runs/loadtest/${name}.rep$i.rc"
  done
  echo "$name rc=[$(cat runs/loadtest/$name.rep*.rc | tr '\n' ' ')]" | tee -a runs/loadtest/loadtest-summary.txt
done
echo "loadavg_after=$(cut -d' ' -f1-3 /proc/loadavg)" | tee -a runs/loadtest/loadtest-summary.txt
kill $pids 2>/dev/null
sleep 1
own_left=0
for p in $pids; do kill -0 "$p" 2>/dev/null && own_left=$((own_left+1)); done
echo "own_hogs_killed=$(echo $pids | wc -w) own_hogs_remaining=$own_left host_yes_remaining=$(pgrep -x yes | wc -l)" | tee -a runs/loadtest/loadtest-summary.txt
