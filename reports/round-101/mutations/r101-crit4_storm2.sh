#!/bin/bash
# r101-CRIT4 storm2: SUCCESSFUL 4-way concurrent export launches (absolute output paths),
# overlapping C2/C3 reps. run 1 of storm.sh proved relative paths fail 48/48.
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
export_1() {
  local tag=$1
  local s e
  s=$(date +%s.%N)
  timeout 300 godot --headless --path "storm$2" --export-release "Linux/X11" "/var/tmp/r101-CRIT4/out/ok_${tag}.pck" > "logs/ok_exp_${tag}.out" 2>&1
  local rc=$?
  e=$(date +%s.%N)
  echo "export_${tag} rc=$rc t=$(echo "$e $s" | awk '{printf "%.2f", $1-$2}')s $(ls -la out/ok_${tag}.pck 2>/dev/null | awk '{print $5}')B"
}
echo "STORM2_START $(date -Is) $(uptime)"
for r in 1 2; do
  pids=()
  for i in 1 2 3 4; do export_1 "${r}_$i" "$i" & pids+=($!); done
  for p in "${pids[@]}"; do wait "$p"; done
done &
GEN=$!
sleep 1
for i in 1 2; do run "C_seq_clean_$i" r100b_seq.gd --clean=1; done
run "C_seq_noclean_1" r100b_seq.gd --clean=0
for i in 1 2; do run "C_celloff0_$i" r95b_order.gd --arm=celloff --off=0; done
for i in 1 2 3 4; do run "C_apipress_$i" input_lattice.gd --arm=api_press; done
wait $GEN
echo "STORM2_END $(date -Is) $(uptime)"
sha256sum out/ok_1_1.pck out/ok_1_2.pck out/ok_1_3.pck out/ok_1_4.pck 2>/dev/null
sha256sum out/ok_2_1.pck out/ok_2_2.pck out/ok_2_3.pck out/ok_2_4.pck 2>/dev/null
echo STORM2_DONE
