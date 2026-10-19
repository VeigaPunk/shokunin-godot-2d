#!/usr/bin/env bash
# r103-ver6 teeth: mutate the FOLDED r97_scene_marker.gd (tag channel) and re-run the 12 rows.
# Expectation: stree_lattice_scene_probe FAILs (folded tree still discriminates the marker contract).
set -euo pipefail
cd /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
V=/var/tmp/r103-ver6
mkdir -p "$V/teeth" "$V/res" "$V/scratch"

# mutant 1: rename the exported property tag -> tagX in the folded marker
python3 - <<'PY'
from pathlib import Path
t = Path("/var/tmp/r103-ver6/fold/r97_scene_marker.gd").read_text()
old = '@export var tag := "?"'
assert t.count(old) == 1
new = t.replace(old, '@export var tagX := "?"')
assert new != t
Path("/var/tmp/r103-ver6/teeth/marker_tagX.gd").write_text(new)
print("mutant1 tagX bytes:", len(new.encode()))
PY

# mutant 2: drop the @export keyword (property stays, tscn can no longer set it)
python3 - <<'PY'
from pathlib import Path
t = Path("/var/tmp/r103-ver6/fold/r97_scene_marker.gd").read_text()
old = '@export var tag := "?"'
assert t.count(old) == 1
new = t.replace(old, 'var tag := "?"')
Path("/var/tmp/r103-ver6/teeth/marker_noexport.gd").write_text(new)
print("mutant2 noexport bytes:", len(new.encode()))
PY

for m in tagX noexport; do
  echo "=== teeth $m ==="
  python3 reports/round-102/mutations/r102-S3-verify.py run \
    --src "$V/fold" --rows "$V/rows_stree.json" \
    --out "$V/res/teeth_${m}.json" --stamp "$V/scratch/teeth_${m}" --timeout 20 \
    --overlay "r97_scene_marker.gd=$V/teeth/marker_${m}.gd"
  python3 reports/round-102/mutations/r102-S3-verify.py analyze --rows "$V/rows_stree.json" \
    --base "$V/res/fold1.json" --fold "$V/res/teeth_${m}.json" \
    --out "$V/res/analyze_teeth_${m}.txt" --label "fold-vs-teeth_${m}"
done
echo "TEETH-DONE"
