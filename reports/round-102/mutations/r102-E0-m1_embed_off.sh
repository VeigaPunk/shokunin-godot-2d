#!/usr/bin/env bash
# r102-E0-m1 — counterfactual: flip the EMBED preset to embed_pck=false.
# Expectation: moved/ gains a sidecar => embed_census artifacts=2 sidecar_pck=1
# tail_magic!=47445043 (row export_launch_embed_self_contained FAILs), while
# embed_boot keeps PASSing via the sidecar and embed_refusal is unaffected.
set -e
LANE=/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
W=/var/tmp/r102-E0/mut/m1
rm -rf "$W"; mkdir -p "$W/proj"
sed 's#binary_format/embed_pck=true#binary_format/embed_pck=false#' "$LANE/corpus/fixtures/export_launch.gd" > "$W/proj/export_launch.gd"
cp "$LANE/corpus/fixtures/project.godot" "$W/proj/project.godot"
EXPORT_LAUNCH_ROOT="$W/root" timeout 90 godot --headless --path "$W/proj" --script res://export_launch.gd -- --arm=embed > "$W/out.log" 2>&1
rc=$?
echo "m1 arm_embed rc=$rc"; grep -E '^(PASS|FAIL)' "$W/out.log"
