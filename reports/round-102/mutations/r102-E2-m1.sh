#!/bin/sh
# r102-E2 mutant m1 — embed arm exports with embed_pck=false.
# Expectation: FAIL (pck_sibling=true, trailer_gdpc=false, bin_gt_template=false).
set -u
FIX=/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/fixtures/export_launch_s02.gd
MUT=/var/tmp/r102-E2/mut/m1
rm -rf "$MUT"; mkdir -p "$MUT/proj"
cp /var/tmp/r102-E2/bat/proj/project.godot "$MUT/proj/project.godot"
sed 's/_build_project("embed", true)/_build_project("embed", false)/' "$FIX" > "$MUT/proj/export_launch_s02.gd"
grep -c '_build_project("embed", false)' "$MUT/proj/export_launch_s02.gd"
EXPORT_LAUNCH_ROOT=/var/tmp/r102-E2/mut/m1root timeout 30 /usr/bin/godot --headless \
  --path "$MUT/proj" --script res://export_launch_s02.gd -- --arm=embed > /var/tmp/r102-E2/logs/m1.log 2>&1
echo "m1_rc=$?"
grep -E '^(PASS|FAIL)' /var/tmp/r102-E2/logs/m1.log
