#!/bin/bash
# r72-scribe landing watcher: log transitions of the round-72 landing surface.
# Write scope: corpus/live/r72-scribe/ only. Read-only elsewhere.
cd "$(git rev-parse --show-toplevel)" || exit 1
prev=""
for i in $(seq 1 360); do
  fx=$(sha256sum corpus/fixtures/pygame_probe.py corpus/fixtures/pygame_battery.py 2>/dev/null | sha256sum | cut -d' ' -f1)
  dirs=$(ls -d corpus/live/r72-* reports/round-72 2>/dev/null | tr '\n' ',')
  st=$(git status --porcelain -- corpus/fixtures reports/round-72 corpus/live 2>/dev/null | sha256sum | cut -d' ' -f1)
  head=$(git log -1 --format=%h 2>/dev/null)
  cur="$fx $dirs $st $head"
  if [ "$cur" != "$prev" ]; then
    echo "$(date -u +%H:%M:%S) $cur" >> corpus/live/r72-scribe/watch.log
    prev="$cur"
  fi
  sleep 15
done
