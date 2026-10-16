#!/usr/bin/env bash
# r94-critic wall-margin probe: the slowest r94 arms under +32 seat hogs.
set -u
cd /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
S=corpus/live/r94-critic/scripts/run_one.sh
for i in $(seq 1 32); do yes > /dev/null & done
HOGS=$(jobs -p | tr '\n' ' ')
echo "seat hogs started: $HOGS loadavg=$(cut -d' ' -f1-3 /proc/loadavg)"
bash $S hog32 corpus/live/r94-critic/proj cpu_pause 5
bash $S hog32 corpus/live/r94-critic/proj cpu_lifetime 3
bash $S hog32 corpus/live/r94-critic/proj cpu_expl 3
bash $S hog32 corpus/live/r94-critic/proj cpu_speed_pre 3
kill $HOGS 2>/dev/null
sleep 1
echo "seat hogs killed; loadavg=$(cut -d' ' -f1-3 /proc/loadavg)"
