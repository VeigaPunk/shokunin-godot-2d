#!/usr/bin/env bash
# r96-scout discovery driver (not a battery row).
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-30}
mkdir -p runs/disc
cp -f probes/discover.gd proj/
for a in "$@"; do
  timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://discover.gd -- "--arm=$a" \
    > "runs/disc/$a.out" 2> "runs/disc/$a.err"
  echo "$?" > "runs/disc/$a.rc"
  echo "== $a rc=$(cat runs/disc/$a.rc) errbytes=$(wc -c < runs/disc/$a.err)"
done
