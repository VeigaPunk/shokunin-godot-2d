#!/usr/bin/env bash
# r94b reprobe batch — re-run the contamination matrix + amount bisect with the
# FINAL probe revision (adds sync=/add_pf= instrumentation and the amount_b1..b4
# bisect arms) into runs/reprobe/.  Run only after run_matrix.sh has finished:
# it refreshes proj/ from probes/.
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-25}
mkdir -p runs/reprobe
cp -f probes/*.gd proj/

note() { printf '%s\n' "$1" | tee -a runs/rc-summary.txt; }
note "== batch reprobe started=$(date -u +%Y-%m-%dT%H:%M:%SZ) bound=$BOUND loadavg=$(cat /proc/loadavg)"

for arm in contam_a contam_b contam_c contam_d contam_e contam_f contam_g contam_h \
           contam_j contam_k contam_first amount_b1 amount_b2 amount_b3 amount_b4 \
           amount_cont amount_phase; do
  for i in 1 2 3; do
    timeout -s KILL "$BOUND" "$GODOT" --headless --path proj \
      --script res://r94b_particles.gd -- "--arm=$arm" \
      > "runs/reprobe/r94b_$arm.rep$i.out" 2> "runs/reprobe/r94b_$arm.rep$i.err"
    echo "$?" > "runs/reprobe/r94b_$arm.rep$i.rc"
  done
done

note "reprobe rc_nonzero=$(grep -l -v '^0$' runs/reprobe/*.rc 2>/dev/null | wc -l) runs=$(ls runs/reprobe/*.out | wc -l)"
note "== batch reprobe finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
