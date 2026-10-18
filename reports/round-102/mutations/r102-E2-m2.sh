#!/bin/sh
# r102-E2 mutant m2 — embed arm boots with EMBED_FRAMES-1 while the receipt still
# claims quit_after=EMBED_FRAMES.
# Expectation: FAIL with frames=[1,2,3,4] extra=true.
set -u
FIX=/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/fixtures/export_launch_s02.gd
MUT=/var/tmp/r102-E2/mut/m2
rm -rf "$MUT"; mkdir -p "$MUT/proj"
cp /var/tmp/r102-E2/bat/proj/project.godot "$MUT/proj/project.godot"
sed 's/_boot(exe, out_dir, EMBED_FRAMES, 6, "run", "embed")/_boot(exe, out_dir, EMBED_FRAMES - 1, 6, "run", "embed")/' "$FIX" \
  > "$MUT/proj/export_launch_s02.gd"
grep -c 'EMBED_FRAMES - 1, 6, "run", "embed"' "$MUT/proj/export_launch_s02.gd"
EXPORT_LAUNCH_ROOT=/var/tmp/r102-E2/mut/m2root timeout 30 /usr/bin/godot --headless \
  --path "$MUT/proj" --script res://export_launch_s02.gd -- --arm=embed > /var/tmp/r102-E2/logs/m2.log 2>&1
echo "m2_rc=$?"
grep -E '^(PASS|FAIL)' /var/tmp/r102-E2/logs/m2.log
