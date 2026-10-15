#!/usr/bin/env bash
# r89-critic arm runner — battery launch shape:
#   timeout -s KILL 25 godot --headless --path proj --script res://<script> -- --arm=<arm>
# usage: run_arms.sh <script> <arm> <reps> <tag>
set -u
cd "$(dirname "$0")"
script="$1"; arm="$2"; reps="$3"; tag="${4:-load}"
for i in $(seq 1 "$reps"); do
  timeout -s KILL 25 godot --headless --path proj --script "res://${script}" -- "--arm=${arm}" \
    >"runs/${script}.${arm}.${tag}.rep${i}.out" 2>"runs/${script}.${arm}.${tag}.rep${i}.err"
  echo $? >"runs/${script}.${arm}.${tag}.rep${i}.rc"
done
