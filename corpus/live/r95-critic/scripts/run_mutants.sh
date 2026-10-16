#!/usr/bin/env bash
# r95 critic mutant driver — 3 reps per (mutant, row).
set -u
cd /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin || exit 1
S=corpus/live/r95-critic/scripts/run_arms.py
M=corpus/live/r95-critic/mutants
echo "=== mutants start $(date -u +%H:%M:%S) loadavg=$(cut -d' ' -f1 /proc/loadavg)"
python3 "$S" --batch m1a --fixtures "$M/m1a_ordercore_nomeasure/fixtures" --filter order_core --reps 3
python3 "$S" --batch m1b --fixtures "$M/m1b_ordercore_mirror/fixtures"    --filter order_core --reps 3
python3 "$S" --batch m2  --fixtures "$M/m2_pointcap_cap0_full/fixtures"   --filter point_cap --reps 3
python3 "$S" --batch m3  --fixtures "$M/m3_canon_extra_collider/fixtures" --filter r95b_order_canon --reps 3
python3 "$S" --batch m5  --fixtures "$M/m5_periodx_ext_window/fixtures"   --filter periodx --reps 1
echo "=== mutants done $(date -u +%H:%M:%S) loadavg=$(cut -d' ' -f1 /proc/loadavg)"
