#!/usr/bin/env python3
"""r94 verifier — the cpu_pause fold, verified against its own motivation.

The r94-boundary measured that the FROZEN scout probe's cpu_pause row rejects
3/3 under `--fixed-fps 30` (windows [4,7]); the author folded the three
fin_after_* windows to [1,7] in the committed fixture. This probe:
  1. re-derives the fold on the boundary's own ff30 receipts (measured values
     vs the committed windows) — no new launches;
  2. runs the COMMITTED fixture's cpu_pause 3x under --fixed-fps 30 (expect
     3/3 PASS) and the FROZEN scout probe 3x (expect 3/3 reject) in the same
     scratch shape.
Writes only under corpus/live/r94-verifier/ff30-probe/.
"""
import ast
import pathlib
import re
import shutil
import subprocess
from datetime import datetime, timezone

ROOT = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FREEZE = ROOT / "corpus/live/r94-verifier/freeze/corpus/fixtures"
SCOUT_PROBE = ROOT / "corpus/live/r94-scout/probes/particles_lattice.gd"
OUT = ROOT / "corpus/live/r94-verifier/ff30-probe"
OUT.mkdir(parents=True, exist_ok=True)
GODOT = "/usr/bin/godot"
SIG = "PASS particles_lattice cpu_pause ok=true vis_ok=true vis_parent_ok=true pm_disabled_ok=true ts0_ok=true"

# --- 1. re-derive the fold on the boundary's own ff30 receipts
print("== re-derivation on boundary ff30 receipts (measured values vs committed windows)")
pat = re.compile(r"(vis|vis_parent|pm_disabled)\[fin_after_(?:show|enable)=(-?\d+) n=(\d+)\]|ts0\[fin_after_restore=(-?\d+) n=(\d+)\]")
for rep in (1, 2, 3):
    p = ROOT / f"corpus/live/r94-boundary/runs/ff30/r94_particles_cpu_pause.rep{rep}.out"
    text = p.read_text()
    line = next((l for l in text.splitlines() if l.startswith("PASS particles_lattice cpu_pause")), "")
    vals = {}
    for m in pat.finditer(line):
        if m.group(1):
            vals[m.group(1)] = int(m.group(2))
        else:
            vals["ts0"] = int(m.group(4))
    windows = {"vis": (1, 7), "vis_parent": (1, 7), "pm_disabled": (1, 7), "ts0": (15, 25)}
    oks = {k: windows[k][0] <= v <= windows[k][1] for k, v in vals.items()}
    print(f" rep{rep}: values={vals} committed-windows-ok={oks} -> committed row would {'PASS' if all(oks.values()) else 'REJECT'}")

# --- 2. live ff30 runs: committed fixture vs frozen scout probe
scratch = OUT / f"scratch-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}"
scratch.mkdir(parents=True)
for item in FREEZE.iterdir():
    if item.name == "run_battery.py" or item.name.startswith("."):
        continue
    if item.is_dir():
        shutil.copytree(item, scratch / item.name)
    else:
        shutil.copy2(item, scratch / item.name)
shutil.copy2(scratch / "controls" / "pickup.tscn", scratch / "pickup.tscn")

def run(label, probe_src, reps=3):
    (scratch / "particles_lattice.gd").write_text(probe_src.read_text())
    print(f"== live ff30: {label} ({probe_src.name})")
    for rep in range(1, reps + 1):
        cmd = [GODOT, "--headless", "--fixed-fps", "30", "--path", str(scratch),
               "--script", "res://particles_lattice.gd", "--", "--arm=cpu_pause"]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        line = next((l for l in p.stdout.splitlines() if l.startswith("PASS particles_lattice cpu_pause")), "")
        ok = SIG in (p.stdout + p.stderr)
        (OUT / f"{label}.rep{rep}.out").write_text(p.stdout)
        (OUT / f"{label}.rep{rep}.err").write_text(p.stderr)
        print(f" rep{rep}: committed-signature {'PASS' if ok else 'REJECT'} rc={p.returncode} :: {line[:200]}")

run("committed-fixture", FREEZE / "particles_lattice.gd")
run("frozen-scout-probe", SCOUT_PROBE)
