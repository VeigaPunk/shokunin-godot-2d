#!/usr/bin/env bash
# r102-E3 mutant 2 — marker-expectation mutant of the contrast arm.
# The fixture copy expects a wrong boot marker, while the pack and the launched
# editor are untouched. Expected: the contrast arm FAILs with
# reason=boot_marker_count_0, proving the boot/frame assertion is live (the arm
# does not pass on rc=0 alone).
set -u
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
WORK=/var/tmp/r102-E3/mut/m2
rm -rf "$WORK"; mkdir -p "$WORK"
cp "$REPO/corpus/fixtures/project.godot" "$WORK/project.godot"
sed 's/const MARKER_BOOT := "S03_MARKER boot scene=main"/const MARKER_BOOT := "S03_MARKER boot scene=MUTANT"/' \
  "$REPO/corpus/fixtures/export_launch_s03.gd" > "$WORK/export_launch_s03.gd"
echo "mutant_diff_lines=$(diff <(cat "$REPO/corpus/fixtures/export_launch_s03.gd") <(cat "$WORK/export_launch_s03.gd") | grep -c '^[<>]')"
EXPORT_LAUNCH_S03_ROOT="$WORK/root" \
  timeout 120 godot --headless --path "$WORK" --script res://export_launch_s03.gd -- --arm=contrast \
  > "$WORK/stdout.txt" 2> "$WORK/stderr.txt"
rc=$?
echo "M2 exit=$rc stderr_bytes=$(wc -c < "$WORK/stderr.txt")"
grep -E "^(PASS|FAIL)" "$WORK/stdout.txt"
grep -E "contrast_stdout_bytes|nested_contrast" "$WORK/stdout.txt" | head -2
