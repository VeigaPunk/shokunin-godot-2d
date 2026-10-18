#!/usr/bin/env bash
# r102-E3 mutant 1 — substitute the "stock template binary" with the EDITOR build.
# Expected: the refuse arm FAILs (the editor accepts --main-pack and boots the
# pack), proving the row's rc=1 + refusal-fragment pin discriminates a stock
# template binary from an editor build — i.e. the refusal is a property of the
# released binary, not of the flag.
set -u
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
WORK=/var/tmp/r102-E3/mut/m1
rm -rf "$WORK"; mkdir -p "$WORK"
cp "$REPO/corpus/fixtures/project.godot" "$WORK/project.godot"
cp "$REPO/corpus/fixtures/export_launch_s03.gd" "$WORK/export_launch_s03.gd"
EXPORT_LAUNCH_S03_ROOT="$WORK/root" EXPORT_LAUNCH_S03_TEMPLATE=/usr/bin/godot \
  timeout 120 godot --headless --path "$WORK" --script res://export_launch_s03.gd -- --arm=refuse \
  > "$WORK/stdout.txt" 2> "$WORK/stderr.txt"
rc=$?
echo "M1 exit=$rc stderr_bytes=$(wc -c < "$WORK/stderr.txt")"
grep -E "^(PASS|FAIL)" "$WORK/stdout.txt"
grep -E "template_bin|link_mode" "$WORK/stdout.txt" | head -3
