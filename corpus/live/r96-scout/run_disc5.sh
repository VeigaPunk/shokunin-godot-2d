#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-30}
mkdir -p runs/disc5
cp -f probes/discover5.gd proj/
for a in "$@"; do
  timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://discover5.gd -- "--arm=$a" \
    > "runs/disc5/$a.out" 2> "runs/disc5/$a.err"
  echo "$?" > "runs/disc5/$a.rc"
  echo "== $a rc=$(cat runs/disc5/$a.rc) errbytes=$(wc -c < runs/disc5/$a.err) errs=$(grep -c 'ERROR:' runs/disc5/$a.err || true)"
done
