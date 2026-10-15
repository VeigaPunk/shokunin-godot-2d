#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-30}
mkdir -p runs/disc3
cp -f probes/discover3.gd proj/
for a in "$@"; do
  timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://discover3.gd -- "--arm=$a" \
    > "runs/disc3/$a.out" 2> "runs/disc3/$a.err"
  echo "$?" > "runs/disc3/$a.rc"
  echo "== $a rc=$(cat runs/disc3/$a.rc) errbytes=$(wc -c < runs/disc3/$a.err) errs=$(grep -c 'ERROR:' runs/disc3/$a.err || true)"
done
