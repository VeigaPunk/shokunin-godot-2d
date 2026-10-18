#!/bin/bash
# r102-S3 comparator teeth: 1-token fixture mutants on folded trees; the
# classifier must FAIL (signature missing) — proves the pass criterion has teeth.
REPO=/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
cd "$REPO" || exit 1
S3=/var/tmp/r102-S3
R=reports/round-102/mutations/r102-S3-verify.py
T=$S3/fold/teeth
rm -rf $T; mkdir -p $T
cp -r $S3/fold/r95 $T/r95
cp -r $S3/fold/sceneio_h8 $T/sceneio
python3 - <<'EOF'
import pathlib
p1 = pathlib.Path('/var/tmp/r102-S3/fold/teeth/r95/corpus/fixtures/r95b_order.gd')
t = p1.read_text()
n = t.count('"add_order"')
assert n >= 1, n
p1.write_text(t.replace('"add_order"', '"add_orderX"'))
print('r95 teeth mutant sites:', n)
p2 = pathlib.Path('/var/tmp/r102-S3/fold/teeth/sceneio/corpus/fixtures/scene_io_lattice.gd')
t = p2.read_text()
n = t.count('"save_missing_dir"')
assert n >= 1, n
p2.write_text(t.replace('"save_missing_dir"', '"save_missing_dirX"'))
print('sceneio teeth mutant sites:', n)
EOF
python3 - <<'EOF'
import json
rows = json.load(open('/var/tmp/r102-S3/rows.json'))
for name, out in (('r95b_order_canon', '/var/tmp/r102-S3/rows_teeth_r95.json'),
                  ('r96_scene_io_refuse', '/var/tmp/r102-S3/rows_teeth_sceneio.json')):
    sub = [r for r in rows if r['name'] == name]
    assert len(sub) == 1, (name, len(sub))
    json.dump(sub, open(out, 'w'), indent=1)
    print('wrote', out)
EOF
python3 $R run --src $S3/archive/corpus/fixtures --rows $S3/rows_teeth_r95.json \
    --out $S3/res/teeth_r95.json --stamp $S3/scratch/teeth_r95 \
    --overlay r95b_order.gd=$T/r95/corpus/fixtures/r95b_order.gd \
    --overlay dss_lattice.gd=$T/r95/corpus/fixtures/dss_lattice.gd \
    > $S3/res/teeth_r95.log 2>&1; echo "teeth_r95 rc=$?"
python3 $R run --src $S3/archive/corpus/fixtures --rows $S3/rows_teeth_sceneio.json \
    --out $S3/res/teeth_sceneio.json --stamp $S3/scratch/teeth_sceneio \
    --overlay scene_io_lattice.gd=$T/sceneio/corpus/fixtures/scene_io_lattice.gd \
    > $S3/res/teeth_sceneio.log 2>&1; echo "teeth_sceneio rc=$?"
python3 $R analyze --rows $S3/rows_teeth_r95.json --base $S3/res/base.json --fold $S3/res/teeth_r95.json --out $S3/res/analyze_teeth_r95.txt --label teeth-r95
python3 $R analyze --rows $S3/rows_teeth_sceneio.json --base $S3/res/base.json --fold $S3/res/teeth_sceneio.json --out $S3/res/analyze_teeth_sceneio.txt --label teeth-sceneio
echo "TEETH DONE"
