#!/usr/bin/env python3
"""r103-C4 order test: apply an arbitrary run_battery.py patch together with
reports/round-103/mutations/w5_export_div.patch in BOTH orders in a scratch git
worktree and compare the resulting bytes. Prints `git apply -v` offset reports.

Usage: python3 r103-crit4-order.py <patch> [<patch2> ...]   (default: w5 alone test)
Never executes corpus/fixtures/run_battery.py.
"""
import hashlib, subprocess, sys
from pathlib import Path

WT = Path("/var/tmp/r103c-C4/wt")
REL = "corpus/fixtures/run_battery.py"
W5 = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/reports/round-103/mutations/w5_export_div.patch")
PATCHES = [Path(p).resolve() for p in sys.argv[1:]] or [W5]

def git(*a, check=True):
    r = subprocess.run(["git", "-C", str(WT), *a], capture_output=True, text=True)
    if check and r.returncode:
        raise SystemExit(f"git {' '.join(a)} rc={r.returncode}: {r.stderr}")
    return r

def sha():
    return hashlib.sha256((WT / REL).read_bytes()).hexdigest(), sum(1 for _ in (WT / REL).open())

def sequence(order, label):
    git("checkout", "--", REL)
    log = []
    for p in order:
        r = git("apply", "-v", str(p), check=False)
        log.append((p.name, r.returncode, r.stderr.strip()))
        if r.returncode:
            raise SystemExit(f"{label}: {p.name} failed to apply: {r.stderr}")
    s, n = sha()
    print(f"[obs] {label} order={[p.name for p in order]} -> sha256 {s} lines {n}")
    for name, rc, err in log:
        print(f"        {name} rc={rc} :: {' | '.join(err.splitlines()[1:]) or err.splitlines()[0]}")
    return s

# apply all patches in listed order, then all in reverse order
fwd = PATCHES
rev = list(reversed(PATCHES))
print(f"[obs] wt HEAD: {git('rev-parse', 'HEAD').stdout.strip()} dirty={git('status', '--porcelain').stdout.strip()!r}")
a = sequence(fwd, "A")
b = sequence(rev, "B")
print(f"[obs] ORDER-FREE across {[p.name for p in PATCHES]}: {a == b}")
git("checkout", "--", REL)
print(f"[obs] wt restored; dirty={git('status', '--porcelain').stdout.strip()!r}")
