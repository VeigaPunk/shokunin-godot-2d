#!/bin/bash
# r71-scribe state watcher: log transitions of the round-71 landing surface.
# Write scope: corpus/live/r71-scribe/ only. Read-only elsewhere.
cd "$(git rev-parse --show-toplevel)" || exit 1
prev=""
for i in $(seq 1 240); do
  fx=$(sha256sum corpus/fixtures/pygame_probe.py corpus/fixtures/pygame_battery.py 2>/dev/null | sha256sum | cut -d' ' -f1)
  dirs=$(ls -d corpus/live/r71-author corpus/live/r71-scout corpus/live/r71-verifier reports/round-71 2>/dev/null | tr '\n' ',')
  st=$(git status --porcelain -- corpus/fixtures reports/round-71 corpus/live 2>/dev/null | sha256sum | cut -d' ' -f1)
  head=$(git log -1 --format=%h 2>/dev/null)
  cur="$fx $dirs $st $head"
  if [ "$cur" != "$prev" ]; then
    echo "$(date -u +%H:%M:%S) $cur" >> corpus/live/r71-scribe/watch.log
    prev="$cur"
  fi
  sleep 15
done
