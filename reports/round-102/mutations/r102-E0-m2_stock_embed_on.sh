#!/usr/bin/env bash
# r102-E0-m2 — counterfactual: flip the STOCK preset to embed_pck=true.
# Expectation: out/ has a single self-contained artifact => stock_census
# artifacts=1 pck_exists=false pck_magic=missing (row FAILs); stock_boot still
# PASSes because the embedded pack boots.
set -e
LANE=/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
W=/var/tmp/r102-E0/mut/m2
rm -rf "$W"; mkdir -p "$W/proj"
sed 's#binary_format/embed_pck=false#binary_format/embed_pck=true#' "$LANE/corpus/fixtures/export_launch.gd" > "$W/proj/export_launch.gd"
cp "$LANE/corpus/fixtures/project.godot" "$W/proj/project.godot"
EXPORT_LAUNCH_ROOT="$W/root" timeout 90 godot --headless --path "$W/proj" --script res://export_launch.gd -- --arm=stock > "$W/out.log" 2>&1
rc=$?
echo "m2 arm_stock rc=$rc"; grep -E '^(PASS|FAIL)' "$W/out.log"
