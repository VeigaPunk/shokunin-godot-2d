#!/usr/bin/env python3
"""r87-simplifier direct arm reps: before (tracked fixtures) vs after (folded copy).

Runs one arm per process in the battery launch shape, extracts the
`PASS input_lattice <arm> ...` / `PASS r87_edge ...` line, and diffs the
payload sets. Also records stderr bytes.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
BEFORE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "corpus/live/r87-simplifier/proj-before"
AFTER = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "corpus/live/r87-simplifier/proj-after"
REPS = int(sys.argv[3]) if len(sys.argv) > 3 else 3

ARMS = [
    ("input_lattice.gd", "census", 3),
    ("input_lattice.gd", "press_idle", 3),
    ("input_lattice.gd", "api_press", 8),
    ("input_lattice.gd", "ui_ns", 6),
    ("input_lattice.gd", "pre_frame", 6),
    ("input_lattice.gd", "imap_erase", 6),
    ("input_lattice.gd", "imap_mid_cb", 6),
    ("input_lattice.gd", "reentrant", 6),
    ("input_lattice.gd", "dispatch_order", 6),
    ("input_lattice.gd", "press_phys", 6),
    ("r87_edge.gd", "jpbe", 3),
]


def reps(proj: Path, script: str, arm: str, n: int):
    out = []
    for i in range(n):
        p = subprocess.run(
            ["godot", "--headless", "--path", str(proj), "--script", "res://" + script,
             "--", "--arm=" + arm],
            capture_output=True, text=True, timeout=30)
        lines = [l for l in (p.stdout + p.stderr).splitlines()
                 if l.startswith("PASS input_lattice") or l.startswith("PASS r87_edge")]
        out.append((p.returncode, lines[-1] if lines else "<NO-PASS-LINE>"))
    return out


fail = 0
for script, arm, n in ARMS:
    b = reps(BEFORE, script, arm, n)
    a = reps(AFTER, script, arm, n)
    bs = {l for _, l in b}
    as_ = {l for _, l in a}
    same = bs == as_
    status = "IDENTICAL" if same else "DIFF"
    if not same:
        fail += 1
    print(f"{status} {arm}: before_payloads={len(bs)} after_payloads={len(as_)} reps={n}")
    if not same:
        for l in sorted(bs - as_):
            print("  only-before:", l[:160])
        for l in sorted(as_ - bs):
            print("  only-after :", l[:160])
    # per-rep exit codes
    bad = [c for c, _ in b + a if c != 0]
    if bad:
        print(f"  NONZERO exits: {bad}")
        fail += 1

print("REPS-ALL-IDENTICAL" if fail == 0 else f"REPS-FAILURES={fail}")
sys.exit(0 if fail == 0 else 1)
