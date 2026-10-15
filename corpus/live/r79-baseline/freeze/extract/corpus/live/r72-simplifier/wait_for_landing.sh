#!/bin/bash
# Block until corpus/fixtures/pygame_{probe,battery}.py differ from pre-land hashes
# (or until git HEAD moves). Writes landing receipt to r72-simplifier/.
cd "$(git rev-parse --show-toplevel)" || exit 1
PRE=$(sha256sum corpus/fixtures/pygame_probe.py corpus/fixtures/pygame_battery.py)
for i in $(seq 1 360); do
  CUR=$(sha256sum corpus/fixtures/pygame_probe.py corpus/fixtures/pygame_battery.py)
  HEAD=$(git log -1 --format=%h)
  if [ "$CUR" != "$PRE" ] || [ "$HEAD" != "44127af" ]; then
    echo "LANDING DETECTED $(date -u +%H:%M:%S) head=$HEAD"
    echo "$CUR" | tee corpus/live/r72-simplifier/landed-sha256.txt
    exit 0
  fi
  sleep 5
done
echo "NO LANDING within window $(date -u +%H:%M:%S)"
