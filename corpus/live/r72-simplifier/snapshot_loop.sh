#!/bin/bash
# r72-simplifier revision snapper: save every distinct (probe,battery) state.
cd "$(git rev-parse --show-toplevel)" || exit 1
prev=""
for i in $(seq 1 300); do
  ph=$(sha256sum corpus/fixtures/pygame_probe.py | cut -d' ' -f1)
  bh=$(sha256sum corpus/fixtures/pygame_battery.py | cut -d' ' -f1)
  cur="${ph:0:12}-${bh:0:12}"
  if [ "$cur" != "$prev" ]; then
    d=corpus/live/r72-simplifier/snapshots/$cur
    mkdir -p "$d"
    cp corpus/fixtures/pygame_probe.py "$d/pygame_probe.py"
    cp corpus/fixtures/pygame_battery.py "$d/pygame_battery.py"
    echo "$(date -u +%H:%M:%S) $cur probe=$ph battery=$bh" >> corpus/live/r72-simplifier/snapshots/log.txt
    prev="$cur"
  fi
  sleep 10
done
