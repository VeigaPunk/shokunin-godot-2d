#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-30}
mkdir -p runs/disc2
cp -f probes/discover2.gd proj/
for a in "$@"; do
  timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://discover2.gd -- "--arm=$a" \
    > "runs/disc2/$a.out" 2> "runs/disc2/$a.err"
  echo "$?" > "runs/disc2/$a.rc"
  echo "== $a rc=$(cat runs/disc2/$a.rc) errbytes=$(wc -c < runs/disc2/$a.err)"
done
