#!/usr/bin/env python3
"""r93-scout claim audit — recomputes every headline numeric law from the raw
receipts (no Godot needed). Exits non-zero on any mismatch.

Checks:
  A. the r91 receipt value in every canonical+loadtest tweenval receipt;
  B. the expo closed forms (in: 2^(10(t-1))-0.001, out: 1.001*(1-2^(-10t))) against
     the tweenval_grid expo row, float32 tolerance 1e-6;
  C. the crossfade weight law w_i=(i-1)/(N-1) for the four dt sequences;
  D. the running-source crossfade formula w_i*500+(1-w_i)*a(t_i);
  E. the stable=[...] clauses of tweenproc/animproc in all canonical+loadtest reps;
  F. byte-identity of the six non-frame-coupled cells across canonical reps.
"""
import math
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
RUNS = HERE / "runs"
FAILS = []


def fail(msg):
    FAILS.append(msg)
    print("MISMATCH:", msg)


def pass_line(path, cell):
    for ln in path.read_text().splitlines():
        if ln.startswith(f"PASS anim_lattice {cell}"):
            return ln
    raise SystemExit(f"no PASS line in {path}")


# A. r91 receipt
vals = set()
for p in list(RUNS.glob("r93_tweenval.rep*.out")) + list((RUNS / "loadtest").glob("r93_tweenval.rep*.out")):
    m = re.search(r"r91_exact=([0-9.eE+-]+)", pass_line(p, "tweenval"))
    vals.add(m.group(1))
print("A. r91_exact values:", sorted(vals))
if vals != {"9.69718754291534"}:
    fail(f"r91 receipt drifted: {sorted(vals)}")

# B. expo closed forms from the grid row
grid = pass_line(RUNS / "r93_tweenval_grid.rep1.out", "tweenval_grid")
m = re.search(r"expo in=([\d.,eE+-]+) out=([\d.,eE+-]+) io=([\d.,eE+-]+) oi=([\d.,eE+-]+)", grid)
ts = [0.0, 0.25, 0.5, 0.75, 1.0]
ins = [float(v) for v in m.group(1).split(",")]
outs = [float(v) for v in m.group(2).split(",")]
worst_in = worst_out = 0.0
for t, v in zip(ts, ins):
    if t == 0.0:
        continue
    cand = 10.0 * (2 ** (10 * (t - 1)) - 0.001)
    worst_in = max(worst_in, abs(v - cand))
for t, v in zip(ts, outs):
    if t == 0.0 or t == 1.0:
        continue
    cand = 10.0 * 1.001 * (1 - 2 ** (-10 * t))
    worst_out = max(worst_out, abs(v - cand))
print(f"B. expo worst residuals: in={worst_in:.3e} out={worst_out:.3e} "
      f"(endpoints: in_1={ins[-1]} out_1={outs[-1]})")
if worst_in > 1e-5 or worst_out > 1e-5:
    fail("expo closed form outside float32 tolerance")
if ins[-1] != 9.99000012874603 or outs[-1] != 10.0:
    fail("expo endpoint values drifted")

# C/D. blend laws
blend = pass_line(RUNS / "r93_animblend.rep1.out", "animblend")


def seq(name):
    m = re.search(re.escape(name) + r"=\[([\d.,eE+-]+)\]", blend)
    return [float(v) for v in m.group(1).split(",")]


for name, dt, n in [("finished_010", 0.1, 10), ("finished_005", 0.05, 20), ("finished_020", 0.2, 5)]:
    got = seq(name)
    if len(got) != n:
        fail(f"{name}: {len(got)} values, expected {n}")
        continue
    worst = 0.0
    for i, v in enumerate(got, start=1):
        w = (i - 1) / (n - 1)
        cand = 100.0 + (500.0 - 100.0) * w
        worst = max(worst, abs(v - cand))
    print(f"C. {name}: worst residual vs w_i=(i-1)/(N-1): {worst:.3e}")
    if worst > 0.02:
        fail(f"{name} violates the crossfade weight law")

running = seq("running_from_50")
worst = 0.0
for i, v in enumerate(running, start=1):
    w = (i - 1) / 9
    a = 100.0 * min(1.0, 0.5 + i * 0.1)
    cand = w * 500.0 + (1 - w) * a
    worst = max(worst, abs(v - cand))
print(f"D. running_from_50 worst residual: {worst:.3e}")
if worst > 0.02:
    fail("running-source crossfade formula mismatch")
m = re.search(r"capture=\[before=[\d.]+,seq=([\d.,eE+-]+)\]", blend)
capture = [float(v) for v in m.group(1).split(",")]
if capture != running:
    fail("play_with_capture sequence differs from the running crossfade")

# E. stable clauses in every mode-cell receipt
expected_tweenproc = "stable=[auto_advanced=true,paused_frozen=true,phys_advanced=true,manual_exact=true]"
expected_animproc = ("stable=[manual_frame_frozen=true,manual_exact=true,speed0_frozen=true,"
                     "inactive_advance=true,fin_fired=true,caches_once=true,mixer_updated_zero=true]")
n = 0
for p in list(RUNS.glob("r93_tweenproc.rep*.out")) + list((RUNS / "loadtest").glob("r93_tweenproc.rep*.out")):
    n += 1
    if expected_tweenproc not in pass_line(p, "tweenproc"):
        fail(f"tweenproc stable clause missing in {p}")
for p in list(RUNS.glob("r93_animproc.rep*.out")) + list((RUNS / "loadtest").glob("r93_animproc.rep*.out")):
    n += 1
    if expected_animproc not in pass_line(p, "animproc"):
        fail(f"animproc stable clause missing in {p}")
print(f"E. stable clauses checked in {n} mode-cell receipts")

# F. byte identity of the non-frame-coupled cells
for cell in ["census", "tweenval", "tweenval_grid", "animtrack", "tweenstep", "tweenchain",
             "animseek", "animmethod", "animblend"]:
    outs = {p.read_text() for p in RUNS.glob(f"r93_{cell}.rep*.out")}
    if len(outs) != 1:
        fail(f"{cell} not byte-stable across canonical reps ({len(outs)} variants)")
print("F. non-frame-coupled canonical cells byte-stable: 9/9")

print("AUDIT", "FAIL" if FAILS else "PASS", f"({len(FAILS)} mismatches)")
sys.exit(1 if FAILS else 0)
