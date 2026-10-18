#!/bin/bash
set -e
F="nav_lattice_query,nav_lattice_avoid,r98b_qflush_suppress,r98b_qorder_flat,r98b_qorder_tree"
for i in 1 2 3 4 5 6; do
  python3 scripts/verify.py run --tree trees/base --rows p123_rows.json --out receipts/ab_base_$i.jsonl --rep $i --filter "$F" >/dev/null
  python3 scripts/verify.py run --tree trees/fold_t1 --rows p123_rows.json --out receipts/ab_fold_$i.jsonl --rep $i --filter "$F" >/dev/null
  echo "rep $i done"
done
