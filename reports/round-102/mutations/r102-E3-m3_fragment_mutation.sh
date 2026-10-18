#!/usr/bin/env bash
# r102-E3 mutant 3 — refusal-fragment mutant of the refuse arm.
# The fixture copy pins a wrong refusal fragment; the engine output is untouched.
# Expected: the refuse arm FAILs with reason=refusal_fragment_mismatch, proving
# the verbatim-fragment assertion (not just rc) is what the row pins.
set -u
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
WORK=/var/tmp/r102-E3/mut/m3
rm -rf "$WORK"; mkdir -p "$WORK"
cp "$REPO/corpus/fixtures/project.godot" "$WORK/project.godot"
sed 's/was compiled without support for path overrides/was compiled WITH support for path overrides/' \
  "$REPO/corpus/fixtures/export_launch_s03.gd" > "$WORK/export_launch_s03.gd"
echo "mutant_diff_lines=$(diff <(cat "$REPO/corpus/fixtures/export_launch_s03.gd") <(cat "$WORK/export_launch_s03.gd") | grep -c '^[<>]')"
EXPORT_LAUNCH_S03_ROOT="$WORK/root" \
  timeout 120 godot --headless --path "$WORK" --script res://export_launch_s03.gd -- --arm=refuse \
  > "$WORK/stdout.txt" 2> "$WORK/stderr.txt"
rc=$?
echo "M3 exit=$rc stderr_bytes=$(wc -c < "$WORK/stderr.txt")"
grep -E "^(PASS|FAIL)" "$WORK/stdout.txt"
grep -E "refusal_stderr_sha256" "$WORK/stdout.txt" | head -2
