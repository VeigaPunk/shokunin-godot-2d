#!/usr/bin/env bash
# r101-E0 C1 discrimination mutant M3 (main-scene swap).
# Mutation: point the swap project's initial main_scene at main_b instead of
# main. Expect the pack to boot main_b, so
#   PASS export_prod swap pack_boot=main_a ...  (pinned) no longer appears
# while the quitframes line (which only counts engine frames) still passes.
set -euo pipefail
REPO="/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin"
SRC="$REPO/corpus/fixtures/export_prod.gd"
OUT="/var/tmp/r101-E0/mut-m3"
rm -rf "$OUT"
mkdir -p "$OUT"
cp "$REPO/corpus/fixtures/project.godot" "$REPO/corpus/fixtures/export_presets.cfg" "$OUT/"
sed 's/run\/main_scene=\\"res:\/\/main.tscn\\"/run\/main_scene=\\"res:\/\/main_b.tscn\\"/g' "$SRC" > "$OUT/export_prod.gd"
echo "mutant_marker_hits=$(grep -c 'res://main_b.tscn' "$OUT/export_prod.gd")"
cd "$OUT"
EXPORT_PROD_ROOT="$OUT/root" godot --headless --path "$OUT" --script res://export_prod.gd -- --arm=swap 2>/dev/null | grep -E '^(PASS|FAIL)' || true
