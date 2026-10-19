#!/usr/bin/env python3
"""r104-R2 — gate-boundary measurement harness (C2a census tightening + C2b harmlessness).

Reads the LIVE gate/classifier out of `corpus/fixtures/run_battery.py` at runtime
(AST-extracted, never reimplemented, never imported as a side effect of the
battery's main()). `run_battery.py` is never executed as a program.

Modes:
  --census-tighten   measure the pass-line census over every stored run
                     (startswith("PASS ") vs lstrip().startswith("PASS"))
  --replay           replay the 10-shape mut05 catalog (r103) against the live
                     gate and against a text-tightened copy of it
  --harmless         per-shape verdict-layer harmlessness proofs
  --all              all three
"""
import argparse
import ast
import copy
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # never leave __pycache__ in a shared reports/ tree

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
BATTERY = REPO / "corpus/fixtures/run_battery.py"
SCRATCH = Path("/var/tmp/r104-R2")
RUNS = sorted((REPO / "corpus/live/runs").glob("*/verdicts.json"))
MUT05 = REPO / "reports/round-103/mutations/mut05_gate_evasion.py"

CENSUS_OLD = 'line.startswith("PASS ")'
CENSUS_NEW = 'line.lstrip().startswith("PASS")'


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def extract(path, names):
    """Return {name: source} for top-level or nested FunctionDefs, via AST."""
    src = Path(path).read_text()
    tree = ast.parse(src)
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in names:
            out[node.name] = ast.get_source_segment(src, node)
    return out


def load_module(path, tag):
    SCRATCH.mkdir(parents=True, exist_ok=True)
    dst = SCRATCH / ("mod_%s.py" % tag)
    shutil.copyfile(path, dst)
    spec = importlib.util.spec_from_file_location("r104R2_%s" % tag, dst)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, dst


def classifier_ns():
    """classify_process is nested in main(); exec its source standalone."""
    seg = extract(BATTERY, {"classify_process"})["classify_process"]
    ns = {}
    exec("import re\n" + seg, ns)
    return ns["classify_process"], hashlib.sha256(seg.encode()).hexdigest()


# ---------------------------------------------------------------- census
def census():
    old = new = 0
    rows = 0
    noncanon = []
    per_file = []
    for p in RUNS:
        data = json.loads(p.read_bytes())
        o = n = 0
        for r in data.get("results", []):
            out = r.get("output")
            if not isinstance(out, list):
                continue
            for i, line in enumerate(out):
                if not isinstance(line, str):
                    continue
                if line.startswith("PASS "):
                    old += 1
                    o += 1
                elif line.lstrip().startswith("PASS"):
                    noncanon.append((p.parent.name, r.get("case"), i, line[:70]))
                if line.lstrip().startswith("PASS"):
                    new += 1
                    n += 1
            rows += 1
        per_file.append((p.parent.name, o, n))
    return {"runs": len(RUNS), "rows": rows, "old_census": old,
            "new_census": new, "delta": new - old,
            "noncanonical": noncanon, "per_file": per_file}


def census_tighten():
    c = census()
    print("RUNS=%d ROWS=%d" % (c["runs"], c["rows"]))
    print("OLD census (startswith('PASS ')) = %d" % c["old_census"])
    print("NEW census (lstrip().startswith('PASS')) = %d" % c["new_census"])
    print("DELTA = %+d" % c["delta"])
    print("NONCANONICAL_PASS_LINES = %d" % len(c["noncanonical"]))
    for x in c["noncanonical"][:20]:
        print("   ", x)
    print("PER_FILE (run, old, new):")
    for row in c["per_file"]:
        print("   %s old=%d new=%d" % row)
    return c


# ---------------------------------------------------------------- replay
def load_evasions():
    spec = importlib.util.spec_from_file_location("mut05", MUT05)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    data, run_sha = m.load_run()
    ev, cases = m.build_evasions(data["results"])
    return m, data, run_sha, ev, cases


def tightened_copy():
    """Text-tightened gate: census + span/diag membership over PASS-prefixed."""
    src = BATTERY.read_text()
    n = src.count(CENSUS_OLD)
    patched = src.replace(CENSUS_OLD, CENSUS_NEW)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    dst = SCRATCH / "gate_tightened.py"
    dst.write_text(patched)
    return dst, n


def replay():
    m, data, run_sha, ev, cases = load_evasions()
    print("BASE_RUN=%s sha256=%s rows=%d" % (m.RUN, run_sha, len(data["results"])))
    print("LIVE_BATTERY sha256=%s" % sha256(BATTERY))

    live_mod, live_path = load_module(BATTERY, "live")
    tight_path, nsub = tightened_copy()
    print("TIGHTEN substitute count for %r = %d" % (CENSUS_OLD, nsub))
    print("TIGHTENED sha256=%s" % sha256(tight_path))
    tight_mod, tight_copy = load_module(tight_path, "tight")

    units = [("evasion", n, r) for n, r in ev] + \
            [("green", "green_%s" % k, cases[k]) for k in cases]
    rows = [u[2] for u in units]

    live_res = [(n, live_mod.receipt_shape_flag(r)) for _, n, r in units]
    tight_res = [(n, tight_mod.receipt_shape_flag(r)) for _, n, r in units]
    live_by, tight_by = dict(live_res), dict(tight_res)

    print("\n%-30s %-8s %-6s %-6s %s" % ("unit", "kind", "live", "tight", "delta"))
    flips = []
    for kind, name, r in units:
        lf = live_by[name]
        tf = tight_by[name]
        print("%-30s %-8s %-6s %-6s %s" % (
            name, kind, len(lf), len(tf),
            "NEW" if (not lf and tf) else ("" if bool(lf) == bool(tf) else "LOST")))
        if not lf and tf:
            flips.append((name, [f["why"] for f in tf]))
    print("\nUNFLAGGED->FLAGGED flips = %d" % len(flips))
    for f in flips:
        print("   %s -> %s" % f)
    print("GREEN_CONTROLS live flags = %s" % [
        ("green_%s" % k, len(live_by["green_%s" % k])) for k in cases])
    print("GREEN_CONTROLS tight flags = %s" % [
        ("green_%s" % k, len(tight_by["green_%s" % k])) for k in cases])
    return {"live": live_by, "tight": tight_by, "flips": flips,
            "units": [(k, n, r["case"]) for k, n, r in units]}


# ---------------------------------------------------------------- harmless
def signatures():
    """All CASES pins (str or list) + the case name, AST-extracted from source."""
    src = BATTERY.read_text()
    tree = ast.parse(src)
    sigs = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "CASES":
                    for elt in node.value.elts:
                        case = elt.elts[0].value
                        sig = elt.elts[4]
                        if isinstance(sig, ast.Constant):
                            sigs[case] = [sig.value]
                        elif isinstance(sig, (ast.List, ast.Tuple)):
                            sigs[case] = [e.value for e in sig.elts]
    return sigs


def harmless():
    """Two legs per unflagged shape: (1) can the forged line supply ANY pin?
    (2) can it flip a real FAIL receipt to PASS? Negative control = r101 FAILs."""
    m, data, run_sha, ev, cases = load_evasions()
    live_mod, _ = load_module(BATTERY, "live2")
    cp, cp_sha = classifier_ns()
    print("classify_process src sha256=%s" % cp_sha)

    flagged = {"s3a_flood5_simple", "s3b_flood1_seq",
               "s4b_trail_space_simple", "s4c_trail_nbsp_simple"}
    sigs = signatures()
    all_sigs = [(c, s) for c, alts in sigs.items() for s in alts]
    print("CASES=%d signature-alternatives=%d" % (len(sigs), len(all_sigs)))

    # find a real FAIL receipt to use as negative control
    fail_rows = []
    for p in RUNS:
        d = json.loads(p.read_bytes())
        for r in d.get("results", []):
            if r.get("verdict") == "FAIL" and isinstance(r.get("output"), list) \
                    and r.get("signature"):
                fail_rows.append((p.parent.name, r))
    print("FAIL receipts available for control = %d (from %s)" %
          (len(fail_rows), sorted({x[0] for x in fail_rows})))

    table = []
    for name, row in ev:
        if name in flagged:
            continue
        base = [u[2] for u in [(0, 0, r) for r in []]]
        base_case = None
        for k, v in cases.items():
            pass
        # base row = the unmutated sibling
        base = None
        for k in m.BASES:
            if cases[k]["case"] == row["case"]:
                base = cases[k]
        base_out = base["output"] if base else None
        forged = [l for l in row["output"] if l not in (base_out or [])]
        # leg 1: does any CASES pin appear inside the forged line(s)?
        supplied = [(c, s) for (c, s) in all_sigs
                    if any(s in l for l in forged)]
        # leg 2a: base row reclassify with / without forgery (its own pin)
        own = row.get("signature")
        own_alts = [own] if isinstance(own, str) else (own or [])
        res = []
        for alt in own_alts:
            a = cp(row.get("actual_exit"), row.get("error"),
                   "\n".join(base_out or []), row.get("expected_exit"), alt,
                   tuple(row.get("expected_errors") or ()))
            b = cp(row.get("actual_exit"), row.get("error"),
                   "\n".join(row["output"]), row.get("expected_exit"), alt,
                   tuple(row.get("expected_errors") or ()))
            res.append((alt[:40], a, b))
        # leg 2b: negative control — append forgery to a real FAIL receipt
        ctl = []
        for rname, fr in fail_rows[:3]:
            alt = fr["signature"]
            alt = alt[0] if isinstance(alt, list) else alt
            before = cp(fr.get("actual_exit"), fr.get("error"),
                        "\n".join(fr["output"]), fr.get("expected_exit"), alt,
                        tuple(fr.get("expected_errors") or ()))
            after = cp(fr.get("actual_exit"), fr.get("error"),
                       "\n".join(fr["output"] + forged), fr.get("expected_exit"),
                       alt, tuple(fr.get("expected_errors") or ()))
            ctl.append((rname, fr["case"], before, after))
        table.append({"shape": name, "case": row["case"], "forged": forged,
                      "supplied_pins": supplied, "own_pin_reclass": res,
                      "fail_control": ctl})
        print("\n== %s  case=%s" % (name, row["case"]))
        print("   forged line(s): %r" % (forged,))
        print("   leg1 pins supplied by forgery: %d %s" % (len(supplied), supplied[:3]))
        print("   leg2a own-pin reclassify (alt, base, forged): %s" % (res,))
        print("   leg2b FAIL control (run, case, before, after): %s" % (ctl,))
    Path(SCRATCH / "harmless.json").write_text(
        json.dumps(table, indent=1, ensure_ascii=False) + "\n")
    print("\nWROTE %s (%d bytes)" % (SCRATCH / "harmless.json",
                                     (SCRATCH / "harmless.json").stat().st_size))
    return table


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--census-tighten", action="store_true")
    ap.add_argument("--replay", action="store_true")
    ap.add_argument("--harmless", action="store_true")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    if a.all or a.census_tighten:
        print("### CENSUS TIGHTEN"); census_tighten()
    if a.all or a.replay:
        print("\n### REPLAY"); replay()
    if a.all or a.harmless:
        print("\n### HARMLESS"); harmless()
    return 0


if __name__ == "__main__":
    sys.exit(main())
