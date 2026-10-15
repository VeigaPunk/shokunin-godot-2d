#!/bin/bash
# Poll: log when the r71 pygame fixtures land or the tree state changes.
cd "$(git rev-parse --show-toplevel)" || exit 1
prev=""
for i in $(seq 1 300); do
  cur=$(sha256sum corpus/fixtures/pygame_probe.py corpus/fixtures/pygame_battery.py 2>/dev/null | sha256sum | cut -d' ' -f1)
  cur="$cur $(ls -d corpus/live/r71-author corpus/live/r71-scout reports/round-71 2>/dev/null | tr '\n' ',')"
  cur="$cur $(git status --porcelain -- corpus/fixtures reports/round-71 2>/dev/null | sha256sum | cut -d' ' -f1)"
  if [ "$cur" != "$prev" ]; then
    echo "$(date -u +%H:%M:%S) $cur" >> corpus/live/r71-simplifier/watch.log
    prev="$cur"
  fi
  sleep 10
done
