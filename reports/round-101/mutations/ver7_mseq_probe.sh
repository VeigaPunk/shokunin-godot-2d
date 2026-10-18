#!/bin/bash
# r101-ver7 F2 discrimination probe (VER-7 seat): forge one extra replay line
# inside the hover cell of corpus/fixtures/r100b_seq.gd and re-run both replay
# variants, so the landed one-line pins and the proposed 15-line pins can be
# compared on the SAME bytes.
#
# Read-only w.r.t. the lane repo: the mutant is written into scratch only.
# Scratch root: /var/tmp/r101-ver7-vv/probe (the shared /tmp tmpfs is at quota:
# a 3-file copy there failed with EDQUOT, observed 2026-10-18 16:22 -03).
set -eu
W=/var/tmp/r101-ver7-vv/probe
SRC=/var/tmp/r101-ver7-vv/proj
rm -rf "$W"; mkdir -p "$W/proj" "$W/out"
cp "$SRC/project.godot" "$SRC/r100_gui.gd" "$W/proj/"
python3 - "$W" <<'PY'
import hashlib, pathlib, sys
w = pathlib.Path(sys.argv[1])
src = pathlib.Path('/var/tmp/r101-ver7-vv/proj/r100b_seq.gd').read_text()
anchor = '\tprint("PASS r100_gui hover %s" % " ".join(out))'
assert src.count(anchor) == 1, "hover PASS print not found exactly once"
mut = src.replace(anchor, anchor + '\n\tprint("FORGED_EXTRA_CELL_OUTPUT")', 1)
(w / 'proj' / 'r100b_seq.gd').write_text(mut)
print('mutant r100b_seq.gd sha256', hashlib.sha256(mut.encode()).hexdigest())
PY
for v in 1 0; do
  timeout 90 godot --headless --path "$W/proj" --script res://r100b_seq.gd -- --clean=$v \
      >"$W/out/mseq_clean$v.stdout" 2>"$W/out/mseq_clean$v.stderr"
  echo "mseq clean=$v rc=$?"
done
echo MSEQ_RUNS_DONE
