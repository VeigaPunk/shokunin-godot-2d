#!/usr/bin/env bash
# r103-ver6: build folded r97_scene_marker.gd tree + A/B sweep of the 12 stree_lattice rows.
# Targeted godot launches only (battery NEVER run). All scratch under /var/tmp/r103-ver6.
set -euo pipefail
cd /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
V=/var/tmp/r103-ver6
mkdir -p "$V/res" "$V/scratch"

# ---- build folded tree (exact-string removal, count assert) ----
rm -rf "$V/fold"
cp -r "$V/archive" "$V/fold"
python3 - <<'PY'
from pathlib import Path
p = Path("/var/tmp/r103-ver6/fold/r97_scene_marker.gd")
t = p.read_text()
old = 'var ready_ticks := 0\n\nfunc _ready() -> void:\n\tready_ticks += 1\n'
assert t.count(old) == 1, f"anchor count {t.count(old)}"
new = t.replace(old, "")
assert new.endswith('@export var tag := "?"\n'), repr(new[-40:])
p.write_text(new)
print(f"folded marker lines={new.count(chr(10))} bytes={len(new.encode())}")
PY
echo "fold sha256: $(sha256sum "$V/fold/r97_scene_marker.gd")"

# ---- interleaved A/B sweep: base1 fold1 base2 fold2 (12 rows each) ----
for rep in 1 2; do
  for tree in base fold; do
    if [ "$tree" = base ]; then SRC="$V/archive"; else SRC="$V/fold"; fi
    echo "=== sweep $tree rep$rep ==="
    python3 reports/round-102/mutations/r102-S3-verify.py run \
      --src "$SRC" --rows "$V/rows_stree.json" \
      --out "$V/res/${tree}${rep}.json" --stamp "$V/scratch/${tree}${rep}" --timeout 20
  done
done

# ---- analyses ----
python3 reports/round-102/mutations/r102-S3-verify.py analyze --rows "$V/rows_stree.json" \
  --base "$V/res/base1.json" --fold "$V/res/fold1.json" --out "$V/res/analyze_A.txt" --label "base1-vs-fold1"
python3 reports/round-102/mutations/r102-S3-verify.py analyze --rows "$V/rows_stree.json" \
  --base "$V/res/base2.json" --fold "$V/res/fold2.json" --out "$V/res/analyze_B.txt" --label "base2-vs-fold2"
python3 reports/round-102/mutations/r102-S3-verify.py analyze --rows "$V/rows_stree.json" \
  --base "$V/res/base1.json" --fold "$V/res/base2.json" --out "$V/res/analyze_stability.txt" --label "base1-vs-base2"
echo "RUN-SWEEP-DONE"
