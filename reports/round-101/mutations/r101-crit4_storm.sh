#!/bin/bash
# r101-CRIT4 export-storm arm: sustained 4-way concurrent `--export-release` launches
# against C2/C3 measurement runs. Scratch only: /var/tmp/r101-CRIT4.
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

for i in 1 2 3 4; do
  rm -rf "storm$i"; mkdir -p "storm$i"
  cp storm/project.godot storm/main.gd storm/main.tscn storm/export_presets.cfg "storm$i/"
done

storm_gen() {
  local r=0 pids p
  while [ ! -f storm_stop ] && [ $r -lt 15 ]; do
    r=$((r + 1))
    pids=()
    for i in 1 2 3 4; do
      timeout 300 godot --headless --path "storm$i" --export-release "Linux/X11" "out/storm_${r}_$i.pck" > "logs/storm_exp_${r}_$i.out" 2>&1 &
      pids+=($!)
    done
    for p in "${pids[@]}"; do wait "$p"; done
  done
  echo "STORM_GEN_DONE rounds=$r"
}

rm -f storm_stop
echo "STORM_START $(date -Is) $(uptime)"
storm_gen &
GEN=$!
sleep 2

for i in 1 2 3 4; do run "B_seq_clean_$i" r100b_seq.gd --clean=1; done
for i in 1 2; do run "B_seq_noclean_$i" r100b_seq.gd --clean=0; done
for i in 1 2 3 4; do run "B_celloff0_$i" r95b_order.gd --arm=celloff --off=0; done
for i in 1 2; do run "B_celloffy1000_$i" r95b_order.gd --arm=celloff --off=0 --offy=1000; done
for i in 1 2 3 4 5 6 7 8; do run "B_apipress_$i" input_lattice.gd --arm=api_press; done
for i in 1 2 3 4; do run "B_physpeer_$i" input_lattice.gd --arm=phys_peer; done
for i in 1 2; do run "B_cursorphase_$i" r100b_phase.gd --arm=cursorphase; done

touch storm_stop
wait $GEN
echo "STORM_END $(date -Is) $(uptime)"
echo "STORM_MATRIX_DONE"
