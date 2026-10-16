#!/bin/bash
# seat-owned hogs: 16 yes, PID-tracked, killed by PID only
cd "$(dirname "$0")"
: > pids.txt
for i in $(seq 1 16); do
  yes > /dev/null &
  echo $! >> pids.txt
done
echo "started $(wc -l < pids.txt) hogs at $(date -u +%FT%TZ) loadavg=$(cut -d' ' -f1-3 /proc/loadavg)"
