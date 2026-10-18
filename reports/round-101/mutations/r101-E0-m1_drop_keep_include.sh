#!/usr/bin/env bash
# r101-E0 C1 discrimination mutant M1 (include filter).
# Mutation: remove secret/keep* from the export preset include_filter in
# _build_prod. Expect the filter receipt to flip keep_in=true -> false and the
# base receipt keep_size=8 -> -1, so both the
# export_prod_include_exclude_filter and export_prod_base_pck pinned
# signatures stop appearing (rows FAIL).
set -euo pipefail
REPO="/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin"
SRC="$REPO/corpus/fixtures/export_prod.gd"
OUT="/var/tmp/r101-E0/mut-m1"
rm -rf "$OUT"
mkdir -p "$OUT"
cp "$REPO/corpus/fixtures/project.godot" "$REPO/corpus/fixtures/export_presets.cfg" "$OUT/"
sed 's/include_filter=\\"data\/\*,secret\/keep\*\\"/include_filter=\\"data\/\*\\"/' "$SRC" > "$OUT/export_prod.gd"
echo "mutant_marker_hits=$(grep -c 'include_filter=\\"data/\*\\"' "$OUT/export_prod.gd")"
cd "$OUT"
EXPORT_PROD_ROOT="$OUT/root" godot --headless --path "$OUT" --script res://export_prod.gd -- --arm=base 2>/dev/null | grep -E '^(PASS|FAIL)' || true
