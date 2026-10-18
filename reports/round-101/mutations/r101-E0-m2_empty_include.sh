#!/usr/bin/env bash
# r101-E0 C1 discrimination mutant M2 (include filter removed).
# Mutation: empty the export preset include_filter in _build_prod. Expect the
# non-resource txt files to disappear from the pack: entry_count 16 -> 14,
# nested_in/keep_in=false, nested_size/keep_size=-1, so the base, subdir and
# filter pinned signatures all stop appearing.
set -euo pipefail
REPO="/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin"
SRC="$REPO/corpus/fixtures/export_prod.gd"
OUT="/var/tmp/r101-E0/mut-m2"
rm -rf "$OUT"
mkdir -p "$OUT"
cp "$REPO/corpus/fixtures/project.godot" "$REPO/corpus/fixtures/export_presets.cfg" "$OUT/"
sed 's/include_filter=\\"data\/\*,secret\/keep\*\\"/include_filter=\\"\\"/' "$SRC" > "$OUT/export_prod.gd"
echo "mutant_marker_hits=$(grep -c 'include_filter=\\"\\"' "$OUT/export_prod.gd")"
cd "$OUT"
EXPORT_PROD_ROOT="$OUT/root" godot --headless --path "$OUT" --script res://export_prod.gd -- --arm=base 2>/dev/null | grep -E '^(PASS|FAIL)' || true
