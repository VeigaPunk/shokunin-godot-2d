#!/bin/bash
# r101-CRIT4 export race probes (run AFTER the storm arm, to keep the storm window clean).
# P1: two concurrent exports of the SAME warmed project dir, distinct outputs.
# P2: two concurrent exports writing the SAME output path.
cd /var/tmp/r101-CRIT4 || exit 1
echo "PROBE_START $(date -Is) $(uptime)"

echo "--- P1: same project dir, concurrent, distinct outs ---"
timeout 300 godot --headless --path sA --export-release "Linux/X11" /var/tmp/r101-CRIT4/out/raceA.pck > logs/raceA.out 2>&1 &
P1=$!
timeout 300 godot --headless --path sA --export-release "Linux/X11" /var/tmp/r101-CRIT4/out/raceB.pck > logs/raceB.out 2>&1 &
P2=$!
wait $P1; R1=$?
wait $P2; R2=$?
echo "raceA rc=$R1 raceB rc=$R2"
ls -la out/raceA.pck out/raceB.pck 2>/dev/null
sha256sum out/raceA.pck out/raceB.pck 2>/dev/null
# compare each against the warmed sequential reference (calib2 == calib4 == 8aa316ce)
grep -E 'ERROR|DONE' logs/raceA.out | tail -2
grep -E 'ERROR|DONE' logs/raceB.out | tail -2

echo "--- P2: same output path, concurrent ---"
rm -f out/race.pck
timeout 300 godot --headless --path sA --export-release "Linux/X11" /var/tmp/r101-CRIT4/out/race.pck > logs/raceC.out 2>&1 &
P3=$!
timeout 300 godot --headless --path sB --export-release "Linux/X11" /var/tmp/r101-CRIT4/out/race.pck > logs/raceD.out 2>&1 &
P4=$!
wait $P3; R3=$?
wait $P4; R4=$?
echo "raceC rc=$R3 raceD rc=$R4"
ls -la out/race.pck 2>/dev/null; sha256sum out/race.pck 2>/dev/null
grep -E 'ERROR|DONE' logs/raceC.out | tail -2
grep -E 'ERROR|DONE' logs/raceD.out | tail -2
echo "PROBE_END $(date -Is) $(uptime)"
