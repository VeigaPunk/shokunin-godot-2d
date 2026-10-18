#!/bin/bash
# r102-E4 discrimination counterfactuals for corpus/fixtures/export_launch_s04.gd.
# Copies the fixture bytes to a scratch host project under /var/tmp/r102-E4/, applies
# exactly one sed hunk (never touching the repo file), runs the battery launch shape,
# and prints the resulting PASS/FAIL lines. Usage:
#   bash reports/round-102/mutations/r102-E4-m1w-m2x.sh m1w   # widen A include to case/*
#   bash reports/round-102/mutations/r102-E4-m1w-m2x.sh m2x   # swap B exclude to case/G_UP.GD
set -u
REPO=/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
M=${1:-m1w}
SRC=$REPO/corpus/fixtures/export_launch_s04.gd
R=/var/tmp/r102-E4/mut-$M
rm -rf "$R"; mkdir -p "$R/host"
cp "$REPO/corpus/fixtures/project.godot" "$R/host/"
case "$M" in
  m1w) sed 's|^const INC_LOWER := "case/\*\.txt"|const INC_LOWER := "case/*"|' "$SRC" > "$R/host/export_launch_s04.gd" ;;
  m2x) sed 's|^const EXC_UPPER := "case/ONE.TXT,case/G_LOW.GD"|const EXC_UPPER := "case/G_UP.GD"|' "$SRC" > "$R/host/export_launch_s04.gd" ;;
  *) echo "unknown mutation: $M"; exit 2 ;;
esac
echo "--- hunk diff (repo -> mutant):"
diff "$SRC" "$R/host/export_launch_s04.gd" | head -8
EXPORT_LAUNCH_S04_ROOT="$R/root" godot --headless --path "$R/host" --script res://export_launch_s04.gd > "$R/out.txt" 2> "$R/err.txt"
echo "--- rc=$? stderr_bytes=$(wc -c < "$R/err.txt")"
grep -E '^(PASS|FAIL)' "$R/out.txt"
