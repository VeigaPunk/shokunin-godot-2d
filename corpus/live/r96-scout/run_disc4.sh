#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-30}
mkdir -p runs/disc4
cp -f probes/discover4.gd proj/
for a in "$@"; do
  timeout -s KILL "$BOUND" "$GODOT" --headless --path proj --script res://discover4.gd -- "--arm=$a" \
    > "runs/disc4/$a.out" 2> "runs/disc4/$a.err"
  echo "$?" > "runs/disc4/$a.rc"
  echo "== $a rc=$(cat runs/disc4/$a.rc) errbytes=$(wc -c < runs/disc4/$a.err) errs=$(grep -c 'ERROR:' runs/disc4/$a.err || true)"
done
