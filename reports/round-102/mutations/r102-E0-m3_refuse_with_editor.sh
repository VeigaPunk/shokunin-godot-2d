#!/usr/bin/env bash
# r102-E0-m3 — counterfactual: run the refusal probe with the EDITOR binary
# instead of the exported template binary. Expectation: the editor accepts
# --main-pack, so the refusal row's class flips to other/rc=0 (row FAILs),
# while editor_boot and hole are unchanged.
set -e
LANE=/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
W=/var/tmp/r102-E0/mut/m3
rm -rf "$W"; mkdir -p "$W/proj"
sed 's#\\n\./probe\.x86_64 --headless --main-pack#\\n" + _q(_godot()) + " --headless --main-pack#' "$LANE/corpus/fixtures/export_launch.gd" > "$W/proj/export_launch.gd"
grep -n 'main-pack' "$W/proj/export_launch.gd" | head -5
cp "$LANE/corpus/fixtures/project.godot" "$W/proj/project.godot"
EXPORT_LAUNCH_ROOT="$W/root" timeout 90 godot --headless --path "$W/proj" --script res://export_launch.gd -- --arm=probe > "$W/out.log" 2>&1
rc=$?
echo "m3 arm_probe rc=$rc"; grep -E '^(PASS|FAIL)' "$W/out.log"
