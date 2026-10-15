#!/usr/bin/env python3
"""Interleaved before/after reps for the bimodal arms (mode sampling control)."""
import hashlib
import subprocess
import sys
from pathlib import Path

BEFORE = Path(sys.argv[1])
AFTER = Path(sys.argv[2])
ARMS = [("pre_frame", 20), ("api_press", 20), ("ui_ns", 12), ("release_edge", 12), ("press_phys", 12)]


def one(proj, arm):
    p = subprocess.run(["godot", "--headless", "--path", str(proj),
                        "--script", "res://input_lattice.gd", "--", "--arm=" + arm],
                       capture_output=True, text=True, timeout=30)
    line = [l for l in (p.stdout + p.stderr).splitlines() if l.startswith("PASS input_lattice")]
    return line[-1] if line else "<NO-PASS>"


for arm, n in ARMS:
    bs, as_ = {}, {}
    for i in range(n):
        for side, proj, acc in (("b", BEFORE, bs), ("a", AFTER, as_)):
            l = one(proj, arm)
            acc[l] = acc.get(l, 0) + 1
    print(f"=== {arm}: before_modes={len(bs)} after_modes={len(as_)} reps={n}")
    for side, acc in (("before", bs), ("after", as_)):
        for l, c in sorted(acc.items(), key=lambda kv: -kv[1]):
            h = hashlib.sha256(l.encode()).hexdigest()[:12]
            print(f"  {side} x{c} sha={h} tail=...{l[-90:]}")
