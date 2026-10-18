#!/bin/bash
# r101-CRIT4 ambient-load rep matrix. Runs on scratch copy /var/tmp/r101-CRIT4/proj
# (fixtures byte-copy, project renamed r101crit4). NEVER touches the lane repo fixtures.
cd /var/tmp/r101-CRIT4 || exit 1
run() {
  local name=$1; shift
  local script=$1; shift
  local log="logs/${name}.out"
  local s e el rc sh
  s=$(date +%s.%N)
  timeout 150 godot --headless --path proj --script "res://${script}" -- "$@" > "$log" 2>&1
  rc=$?
  e=$(date +%s.%N)
  el=$(echo "$e $s" | awk '{printf "%.2f", $1-$2}')
  sh=$(sha256sum "$log" | cut -d' ' -f1)
  echo "${name} rc=${rc} t=${el}s sha=${sh}"
}
run "A_seq_clean_1" r100b_seq.gd --clean=1
for i in 2 3 4 5 6; do run "A_seq_clean_$i" r100b_seq.gd --clean=1; done
for i in 1 2 3 4; do run "A_seq_noclean_$i" r100b_seq.gd --clean=0; done
run "A_celloff0_1" r95b_order.gd --arm=celloff --off=0
for i in 2 3 4; do run "A_celloff0_$i" r95b_order.gd --arm=celloff --off=0; done
for i in 1 2; do run "A_celloff1000_$i" r95b_order.gd --arm=celloff --off=1000; done
for i in 1 2; do run "A_celloffy1000_$i" r95b_order.gd --arm=celloff --off=0 --offy=1000; done
for i in 1 2 3 4 5 6 7 8 9 10; do run "A_apipress_$i" input_lattice.gd --arm=api_press; done
for i in 1 2 3 4 5 6; do run "A_physpeer_$i" input_lattice.gd --arm=phys_peer; done
for i in 1 2 3; do run "A_cursorphase_$i" r100b_phase.gd --arm=cursorphase; done
for i in 1 2 3; do run "A_dragphase_$i" r100b_phase.gd --arm=dragphase; done
echo "MATRIX_DONE"
uptime
