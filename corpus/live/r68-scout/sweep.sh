for s in 0 0.04 0.08 0.12 0.16 0.20 0.24 0.30; do
  for rep in 1 2 3; do
    MIDLINE_SLEEP=$s /usr/bin/godot --headless --path proj --script res://descendant_pipe_probe.gd -- --spawn-midlineforge > runs/t_${s}_${rep}.out 2>&1
  done
done
