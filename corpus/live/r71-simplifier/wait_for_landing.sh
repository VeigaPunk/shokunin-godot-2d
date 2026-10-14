#!/bin/bash
# Exit as soon as the r71 pygame fixtures land (or after ~12 min).
cd "$(git rev-parse --show-toplevel)" || exit 1
for i in $(seq 1 144); do
  if [ -f corpus/fixtures/pygame_battery.py ] && [ -f corpus/fixtures/pygame_probe.py ]; then
    echo "LANDED $(date -u +%H:%M:%S)"
    ls -la corpus/fixtures/pygame_battery.py corpus/fixtures/pygame_probe.py
    exit 0
  fi
  sleep 5
done
echo "NOT_LANDED $(date -u +%H:%M:%S)"
