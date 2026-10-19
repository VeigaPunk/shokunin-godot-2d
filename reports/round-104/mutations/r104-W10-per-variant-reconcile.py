#!/usr/bin/env python3
"""r104 W10 — per-variant reconciliation: the tab re-declaration is variant-specific."""
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
BS = "\\"

VARIANTS = {"G1": "r104-G1-tabpass.patch",
            "crit2": "r104-crit2-passprefix-tighten.patch",
            "R2": "r104-R2-tabpass-census.patch",
            "scr3": "r104-scr3-tabpass-census.patch",
            "V7": "r104-V7-pass-prefix-tighten.patch"}


def reset():
    subprocess.run(["git", "-C", str(repo), "checkout", "-q", "--",
                    "corpus/fixtures/run_battery.py"], check=True)


def ap(p):
    r = subprocess.run(["git", "-C", str(repo), "apply", str(M / p)],
                       capture_output=True, text=True)
    assert r.returncode == 0, (p, r.stderr)


def load(p, n):
    s = importlib.util.spec_from_file_location(n, p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


for name, patch in VARIANTS.items():
    reset()
    ap(patch)
    ap("r104-S0-evasion-probe.patch")
    ap("r104-W4-floor-gate.patch")
    mod = load(RB, "m_" + name)
    observed = None
    for sh in mod.gate_evasion_replay(NEWEST)["shapes"]:
        if sh["shape"] == "s4a_tab_leading_pass_line":
            observed = sh["observed_reasons"]
    # build the corrected source for THIS variant
    text = RB.read_text()
    old_a = '     (("append", None, "' + BS + 'tPASS forged=true"),), ()),\n'
    old_d = '     (("append", None, "PASS' + BS + 'tforged=true"),), ()),\n'
    # The tuple ends `),), ()),` — split on the empty-expected-set tail and
    # re-close with the observed reason set.
    tail = ", ()),\n"
    assert text.count(old_a) == 1 and text.count(old_d) == 1, (name, text.count(old_a), text.count(old_d))
    assert old_a.count(tail) == 1 and old_d.count(tail) == 1
    reasons = ", ".join('"%s"' % r for r in observed)
    # A one-element parenthesised list is NOT a tuple; the trailing comma is
    # required or the catalogue entry collapses to a plain string and the
    # probe compares against its characters.
    if len(observed) == 1:
        reasons += ","
    new_a = old_a.split(tail)[0] + ",\n     (" + reasons + ")),\n"
    new_d = old_d.split(tail)[0] + ",\n     (" + reasons + ")),\n"
    text = text.replace(old_a, new_a).replace(old_d, new_d)
    out = repo / "corpus/fixtures" / ("corrected_%s.py" % name)
    out.write_text(text)
    try:
        m2 = load(out, "c_" + name)
        flags = m2.gate_evasion_replay(NEWEST)["flags"]
        aud = sum(len(m2.receipt_shape_audit(json.loads(Path(r).read_text())["results"])["flags"])
                  for r in RUNS)
        print("%-6s observed=%-52s -> after re-decl: probe_flags=%d audit_total=%d %s"
              % (name, str(observed), len(flags), aud,
                 "GREEN" if not flags else "STILL RED"))
    except Exception as e:
        print("%-6s observed=%-52s -> RECONCILE FAILED: %s" % (name, str(observed), e))
reset()
