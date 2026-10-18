#!/bin/bash
# r101 SIMP-3 scratch setup. NOTE: /tmp tmpfs is effectively exhausted on this
# host (13G/16G held by other lanes; >few-KB writes fail with EDQUOT while
# df still reports 3.1G free) -> scratch projects live under /var/tmp/r101-simp3.
set -euo pipefail
REPO=/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
ROOT=/var/tmp/r101-simp3
mkdir -p "$ROOT/runs" "$ROOT/scripts" "$ROOT/work"

make_base() {
  local dest=$1
  rm -rf "$dest"
  mkdir -p "$dest"
  local item name
  for item in "$REPO"/corpus/fixtures/*; do
    name=$(basename "$item")
    case "$name" in
      run_battery.py) continue ;;
    esac
    cp -a "$item" "$dest/$name"
  done
  python3 - "$dest/project.godot" <<'PY'
import sys
p = sys.argv[1]
t = open(p).read()
t = t.replace('config/name="MechanicOneShotTest"', 'config/name="MechanicOneShotTest-r101simp3"', 1)
open(p, 'w').write(t)
PY
  cp -a "$dest/controls/pickup.tscn" "$dest/pickup.tscn"
  python3 - "$dest/causal_chain.gd" <<'PY'
import sys
p = sys.argv[1]
t = open(p).read()
anchor = "    await process_frame\n    var old := current_scene"
assert anchor in t, "causal fixture changed"
t = t.replace(anchor, "    await process_frame\n    await process_frame\n    var old := current_scene", 1)
open(p, 'w').write(t)
PY
}

make_base "$ROOT/base"
echo "base built: $ROOT/base"
sha256sum "$ROOT/base/nav_lattice.gd" "$ROOT/base/particles_lattice.gd" \
          "$ROOT/base/dss_lattice.gd" "$ROOT/base/r95b_order.gd" \
          "$ROOT/base/tilemap_lattice.gd" "$ROOT/base/anim_lattice.gd" \
          "$ROOT/base/r93b_anim.gd"
