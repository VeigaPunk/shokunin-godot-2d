#!/usr/bin/env python3
"""Battery-shape launches (subprocess.run, no `timeout` wrapper) under load."""
import subprocess, pathlib, time
RUNS = pathlib.Path("runs")
MODE_Q = "just_after_flush=w_jp[ex=false inex=true]"
MODE_L = "just_after_flush=w_jp[ex=false inex=false]"
modes = {"Q":0,"L":0,"?":0}
for i in range(8):
    p = subprocess.run(["godot","--headless","--path","proj","--script","res://input89_edges.gd","--","--arm=exact"],
                       capture_output=True, text=True, timeout=30)
    line = next((l for l in p.stdout.splitlines() if l.startswith("PASS input89_edges exact")), None)
    m = "Q" if line and MODE_Q in line else "L" if line and MODE_L in line else "?"
    modes[m]+=1
    pathlib.Path(f"runs/pipe_exact.rep{i+1}.out").write_text(p.stdout)
    pathlib.Path(f"runs/pipe_exact.rep{i+1}.err").write_text(p.stderr)
    pathlib.Path(f"runs/pipe_exact.rep{i+1}.rc").write_text(str(p.returncode))
# battery-shape lineempty (no timeout binary -> pure assert stderr)
p = subprocess.run(["godot","--headless","--path","proj","--script","res://geo2d_lattice.gd","--","--arm=lineempty"],
                   capture_output=True, text=True, timeout=30)
pathlib.Path("runs/pipe_lineempty.out").write_text(p.stdout)
pathlib.Path("runs/pipe_lineempty.err").write_text(p.stderr)
pathlib.Path("runs/pipe_lineempty.rc").write_text(str(p.returncode))
print("exact pipe modes:", modes)
print("lineempty rc:", p.returncode, "stderr bytes:", len(p.stderr))
print("stderr:", p.stderr.strip()[:200])
