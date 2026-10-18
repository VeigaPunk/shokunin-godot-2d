#!/bin/bash
# r102-S3 sweep: inventory + folded trees + targeted row sweeps (battery NEVER run).
REPO=/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
cd "$REPO" || exit 1
S3=/var/tmp/r102-S3
R=reports/round-102/mutations/r102-S3-verify.py
mkdir -p $S3/res

# 1. per-hunk inventory (fixed splitter)
python3 reports/round-102/mutations/r102-S3-inventory.py > $S3/inventory.txt 2>&1
tail -4 $S3/inventory.txt

# 2. folded trees from archive bytes
F=$S3/fold
for t in particles r95 sceneio_full sceneio_h8; do
  rm -rf $F/$t; mkdir -p $F/$t/corpus/fixtures
  cp $S3/archive/corpus/fixtures/*.gd $F/$t/corpus/fixtures/
done
(cd $F/particles    && patch -p1 < $REPO/reports/round-101/mutations/r101-simp3-particles-fold.patch)
(cd $F/r95          && patch -p1 < $REPO/reports/round-101/mutations/r101-simp3-r95-fold.patch)
(cd $F/sceneio_full && patch -p1 < $REPO/reports/round-101/mutations/r101-simp2-scene_io_lattice.gd.diff)
python3 - <<'EOF'
import pathlib
p = pathlib.Path('/var/tmp/r102-S3/fold/sceneio_h8/corpus/fixtures/scene_io_lattice.gd')
t = p.read_text()
old = "\tloaded = null\n\troot.free()"
assert t.count(old) == 1, ("count", t.count(old))
p.write_text(t.replace(old, "\troot.free()", 1))
print("sceneio_h8 isolated edit ok")
EOF
echo "== folded shas =="
sha256sum $F/particles/corpus/fixtures/particles_lattice.gd \
          $F/r95/corpus/fixtures/dss_lattice.gd $F/r95/corpus/fixtures/r95b_order.gd \
          $F/sceneio_full/corpus/fixtures/scene_io_lattice.gd $F/sceneio_h8/corpus/fixtures/scene_io_lattice.gd

# 3. row subsets
python3 - <<'EOF'
import json
rows = json.load(open('/var/tmp/r102-S3/rows.json'))
def w(p, f):
    sub = [r for r in rows if f(r)]
    json.dump(sub, open(p, 'w'), indent=1)
    print(p, len(sub))
w('/var/tmp/r102-S3/rows_particles.json', lambda r: r['fixture'] == 'particles_lattice.gd')
w('/var/tmp/r102-S3/rows_r95.json', lambda r: r['fixture'] in ('dss_lattice.gd', 'r95b_order.gd') or r['name'] == 'r101_ytrans_census')
w('/var/tmp/r102-S3/rows_sceneio.json', lambda r: r['fixture'] == 'scene_io_lattice.gd')
refuse = [r for r in rows if r['fixture'] == 'scene_io_lattice.gd' and 'refuse' in r['name']]
assert len(refuse) == 1, refuse
print('refuse row:', refuse[0]['name'], refuse[0]['flags'])
json.dump(refuse, open('/var/tmp/r102-S3/rows_sceneio_refuse.json', 'w'), indent=1)
EOF

# 4. sweeps (sequential; host load is shared)
runsp() {
  local name=$1 rowsf=$2 out=$3; shift 3
  local ov=()
  for o in "$@"; do ov+=(--overlay "$o"); done
  python3 $R run --src $S3/archive/corpus/fixtures --rows "$rowsf" --out "$out" \
      --stamp $S3/scratch/$name "${ov[@]}" > $S3/res/$name.log 2>&1
  echo "$name rc=$?"
}
runsp base           $S3/rows.json                 $S3/res/base.json
runsp particles      $S3/rows_particles.json       $S3/res/particles.json       particles_lattice.gd=$F/particles/corpus/fixtures/particles_lattice.gd
runsp r95            $S3/rows_r95.json             $S3/res/r95.json             dss_lattice.gd=$F/r95/corpus/fixtures/dss_lattice.gd r95b_order.gd=$F/r95/corpus/fixtures/r95b_order.gd
runsp sceneio_full   $S3/rows_sceneio.json         $S3/res/sceneio_full.json    scene_io_lattice.gd=$F/sceneio_full/corpus/fixtures/scene_io_lattice.gd
runsp sceneio_h8     $S3/rows_sceneio_refuse.json  $S3/res/sceneio_h8.json      scene_io_lattice.gd=$F/sceneio_h8/corpus/fixtures/scene_io_lattice.gd

# 5. analyses
python3 $R analyze --rows $S3/rows_particles.json        --base $S3/res/base.json --fold $S3/res/particles.json    --out $S3/res/analyze_particles.txt    --label particles
python3 $R analyze --rows $S3/rows_r95.json              --base $S3/res/base.json --fold $S3/res/r95.json          --out $S3/res/analyze_r95.txt          --label r95
python3 $R analyze --rows $S3/rows_sceneio.json          --base $S3/res/base.json --fold $S3/res/sceneio_full.json --out $S3/res/analyze_sceneio_full.txt --label sceneio_full
python3 $R analyze --rows $S3/rows_sceneio_refuse.json   --base $S3/res/base.json --fold $S3/res/sceneio_h8.json   --out $S3/res/analyze_sceneio_h8.txt   --label sceneio_h8
echo "ALL DONE"
