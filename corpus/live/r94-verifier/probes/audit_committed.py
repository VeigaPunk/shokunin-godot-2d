#!/usr/bin/env python3
"""r94 verifier — static audit of the committed r94 landing (c7228893).

Reads only the frozen extraction (corpus/live/r94-verifier/freeze) plus the
frozen scout corpus. Writes nothing except stdout.
"""
import ast
import hashlib
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FREEZE = ROOT / "corpus/live/r94-verifier/freeze/corpus/fixtures"
SCOUT = ROOT / "corpus/live/r94-scout"
OUT = []


def say(*a):
    line = " ".join(str(x) for x in a)
    OUT.append(line)
    print(line, flush=True)


def load_harness(path):
    spec = importlib.util.spec_from_file_location("frozen_run_battery", path)
    mod = importlib.util.module_from_spec(spec)
    src = path.read_text()
    # Execute only up to main(): the module is side-effect free at import.
    spec.loader.exec_module(mod)
    return mod, src


def main():
    harness = FREEZE / "run_battery.py"
    fixture = FREEZE / "particles_lattice.gd"
    scout_probe = SCOUT / "probes/particles_lattice.gd"
    mod, src = load_harness(harness)

    say("== harness ==")
    say("run_battery.py sha256", hashlib.sha256(harness.read_bytes()).hexdigest())
    say("CASES len", len(mod.CASES))
    r94 = [(i, c) for i, c in enumerate(mod.CASES) if c[0].startswith("r94_")]
    say("r94 rows", len(r94), "indices", r94[0][0], "..", r94[-1][0])
    say("r94 names unique", len({c[0] for _, c in r94}) == len(r94))
    say("row before first r94", mod.CASES[r94[0][0] - 1][0])
    say("row after last r94", mod.CASES[r94[-1][0] + 1][0])

    # flags shape
    bad_flags = [(c[0], c[2]) for _, c in r94 if len(c[2]) != 1 or not c[2][0].startswith("--arm=")]
    say("r94 rows with non --arm= flags", bad_flags)

    # arm coverage vs fixture match block
    arms = [c[2][0].removeprefix("--arm=") for _, c in r94]
    ftext = fixture.read_text()
    match_arms = re.findall(r'^\t\t"([a-z0-9_]+)": ', ftext, re.M)
    say("fixture match arms", len(match_arms), match_arms)
    say("CASES arms not in fixture", sorted(set(arms) - set(match_arms)))
    say("fixture arms not in CASES", sorted(set(match_arms) - set(arms)))

    # expected_errors / required_stderr coverage
    ee = {k: v for k, v in getattr(mod, "EXPECTED_ERRORS", {}).items() if k.startswith("r94_")}
    rs = {k: v for k, v in getattr(mod, "REQUIRED_STDERR", {}).items() if k.startswith("r94_")}
    say("r94 expected_errors entries", ee)
    say("r94 required_stderr entries", rs)

    # signature uniqueness across all CASES
    sigs = {}
    dup = []
    for i, c in enumerate(mod.CASES):
        sig = c[4]
        if sig in sigs:
            dup.append((sigs[sig], i, sig[:60]))
        else:
            sigs[sig] = i
    say("duplicate signatures in CASES", dup)

    # scout ROWS / ROWS_PREFIX comparison
    scout_rows_src = (SCOUT / "author-rows.py.txt").read_text()
    tree = ast.parse(scout_rows_src)
    rows = {}
    rows_prefix = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in ("ROWS", "ROWS_PREFIX"):
                val = ast.literal_eval(node.value)
                (rows if name == "ROWS" else rows_prefix).update({t[0]: t for t in val})
    say("scout ROWS", len(rows), "ROWS_PREFIX", len(rows_prefix))
    say("scout ROWS_PREFIX names == CASES r94 names",
        [t[0] for t in rows_prefix.values()] == [c[0] for _, c in r94])
    same_prefix = all(rows_prefix[c[0]] == c for _, c in r94)
    say("committed r94 tuple == scout ROWS_PREFIX tuple (all 19)", same_prefix)
    diffs = [(c[0], rows_prefix[c[0]], c) for _, c in r94 if rows_prefix.get(c[0]) != c]
    for d in diffs[:5]:
        say("DIFF", d[0], "\n  scout:", d[1], "\n  commit:", d[2])

    # full-line ROWS vs committed: committed sig must be a prefix of scout ROWS sig
    not_prefix = [c[0] for _, c in r94 if not rows[c[0]][4].startswith(c[4])]
    say("committed sig not a prefix of scout ROWS full line", not_prefix)

    # fixture fold constants
    say("== fixture ==")
    say("fixture sha256", hashlib.sha256(fixture.read_bytes()).hexdigest())
    say("fixture lines", len(ftext.splitlines()))
    for m in re.finditer(r"var ok(vis|vp|pm|ts) := _okb\([^,]+, (\d+), (\d+)\)", ftext):
        say("_okb window", m.group(1), m.group(2), m.group(3))
    say("request expected line:", re.search(r"var expected: int = int\((\w+)\(0\.5 / spec\)\) \+ 1", ftext).group(0))
    say("scout probe sha256", hashlib.sha256(scout_probe.read_bytes()).hexdigest())

    # classify_process source hash (production segment)
    cp = re.search(r"\n    def classify_process\(.*?\n(?=    def classify_streams)", src, re.S)
    if cp:
        seg = cp.group(0)
        say("classify_process sha256", hashlib.sha256(seg.encode()).hexdigest(), "lines", len(seg.splitlines()))

    # floor gate
    gate = re.search(r'"r94_expected_errors_all_matched": all\(.*?\n(?:.*?\n)*?.*?\),\n', src)
    say("floor gate present", gate is not None)
    if gate:
        say("floor gate text:", gate.group(0).strip().replace("\n", " | "))
    gates = re.findall(r'"(r\d+_expected_errors_all_matched)"', src)
    say("round gates in harness", len(gates), gates)

    # which r94 rows are prefix-shaped (end without trailing token boundary)
    say("== pin shapes ==")
    for _, c in r94:
        sig = c[4]
        say(f"{c[0]:36s} len={len(sig):5d} tail={sig[-24:]!r}")


if __name__ == "__main__":
    main()
