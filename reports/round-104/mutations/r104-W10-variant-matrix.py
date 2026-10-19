#!/usr/bin/env python3
"""r104 W10 — competing-variant x S0 interaction matrix.

For each of the 5 competing tab-PASS patches: apply it alone, then with S0, and
record (a) the flag reason it emits for the tab shape, (b) the S0 probe flags
induced, (c) whether the stored corpus gains false positives.
"""
import glob
import importlib.util
import json
import subprocess
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
M = REPO / "reports/round-104/mutations"
repo = Path("/var/tmp/r104-W10/realtest")
RB = repo / "corpus/fixtures/run_battery.py"
RUNS = sorted(glob.glob(str(REPO / "corpus/live/runs/*/verdicts.json")))
NEWEST = json.loads(Path(RUNS[-1]).read_text())["results"]

VARIANTS = {
    "G1": "r104-G1-tabpass.patch",
    "crit2": "r104-crit2-passprefix-tighten.patch",
    "R2": "r104-R2-tabpass-census.patch",
    "scr3": "r104-scr3-tabpass-census.patch",
    "V7": "r104-V7-pass-prefix-tighten.patch",
}
S0 = "r104-S0-evasion-probe.patch"
W4 = "r104-W4-floor-gate.patch"


def reset():
    subprocess.run(["git", "-C", str(repo), "checkout", "-q", "--",
                    "corpus/fixtures/run_battery.py"], check=True)


def ap(p):
    r = subprocess.run(["git", "-C", str(repo), "apply", str(M / p)],
                       capture_output=True, text=True)
    assert r.returncode == 0, (p, r.stderr)


def load(n):
    s = importlib.util.spec_from_file_location(n, RB)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def audit_total(mod):
    return sum(len(mod.receipt_shape_audit(
        json.loads(Path(r).read_text())["results"])["flags"]) for r in RUNS)


reset()
base = load("base")
BASE_TOTAL = audit_total(base)
print("HEAD baseline flags over 8 runs: %d\n" % BASE_TOTAL)

print("%-7s %-42s %-9s %-9s %s" % ("variant", "tab-shape reasons",
                                   "corpusFP", "S0-only", "S0+W4 probe flags"))
print("-" * 108)
for name, patch in VARIANTS.items():
    reset()
    ap(patch)
    mod = load("v_" + name)
    case = next(c for c in mod.CASES if c[0] == "input_route")[0]
    sig = mod.CASES_SIG_BY_CASE[case]
    tab = {"case": case, "verdict": "PASS", "output": [sig, "PASS\t" + sig]}
    reasons = [x.get("why") for x in mod.receipt_shape_flag(tab)]
    fp = audit_total(mod) - BASE_TOTAL

    reset()
    ap(patch)
    ap(S0)
    m2 = load("v2_" + name)
    r2 = m2.gate_evasion_replay(NEWEST)
    s0_only = len(r2["flags"])

    reset()
    ap(patch)
    ap(S0)
    ap(W4)
    m3 = load("v3_" + name)
    r3 = m3.gate_evasion_replay(NEWEST)
    print("%-7s %-42s %-9d %-9d %s" % (
        name, ",".join(reasons), fp, s0_only,
        [f["shape"] for f in r3["flags"]] or "[]"))
reset()
print("\n(S0-only column = probe flags when S0 is combined with this variant;")
print(" S0 alone = 0 flags; every combined tree needs the tab re-declaration.)")
