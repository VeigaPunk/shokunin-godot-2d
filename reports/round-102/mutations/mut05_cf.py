#!/usr/bin/env python3
"""mut05_cf — counterfactual reps for mut05 (r102 seat M5).

settle= distribution for link/path on folded vs mutant (is settle=6 load-conditional
or a resurrection effect?) + teardown crash/clean pair reps (discrimination firing).

Usage: python3 mut05_cf.py --work /var/tmp/r102-mut5 --battery <repo>/corpus/fixtures/run_battery.py --godot /usr/bin/godot
"""
import argparse, importlib.util, json, re, sys
from pathlib import Path

def load_mut05(p: Path):
    spec = importlib.util.spec_from_file_location("mut05", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--battery", required=True)
    ap.add_argument("--godot", default="godot")
    ap.add_argument("--reps", type=int, default=6)
    a = ap.parse_args()
    m = load_mut05(Path(__file__).with_name("mut05.py"))
    rows, ALLOW, REQ = m.extract_pins(Path(a.battery))
    m.ALLOW, m.REQ = ALLOW, REQ
    by = {r[0]: r for r in rows}
    work = Path(a.work)
    folded, mutant = work / "trees" / "folded", work / "trees" / "mutant"
    out = {}
    for name in ("nav_lattice_link", "nav_lattice_path"):
        row = by[name]
        rec = {"folded": [], "mutant": []}
        for rep in range(1, a.reps + 1):
            for tree_name, tree in (("folded", folded), ("mutant", mutant)):
                r = m.receipt(a.godot, tree, row)
                settle = re.search(r"settle=(\d+)", r["_out"].decode(errors="replace")).group(1)
                rec[tree_name].append({"rep": rep, "rc": r["rc"], "verdict": r["verdict"], "settle": settle})
                print(f"MUT5CF {name} {tree_name} rep{rep} rc={r['rc']} verdict={r['verdict']} settle={settle}", flush=True)
        out[name] = rec
    for name in ("nav_lattice_teardown_crash", "nav_lattice_teardown_clean"):
        row = by[name]
        rec = {"folded": [], "mutant": []}
        for rep in range(1, 4):
            for tree_name, tree in (("folded", folded), ("mutant", mutant)):
                r = m.receipt(a.godot, tree, row)
                rec[tree_name].append({"rep": rep, "rc": r["rc"], "verdict": r["verdict"],
                                       "required_stderr_ok": r["required_stderr_ok"]})
                print(f"MUT5CF {name} {tree_name} rep{rep} rc={r['rc']} verdict={r['verdict']} req_ok={r['required_stderr_ok']}", flush=True)
        out[name] = rec
    (work / "confirm.json").write_text(json.dumps(out, indent=1))
    for name in ("nav_lattice_link", "nav_lattice_path"):
        fs = sorted({x["settle"] for x in out[name]["folded"]})
        ms = sorted({x["settle"] for x in out[name]["mutant"]})
        vs = sorted({x["verdict"] for x in out[name]["folded"] + out[name]["mutant"]})
        print(f"MUT5CF summary {name}: settle folded={fs} mutant={ms} verdicts={vs}", flush=True)

if __name__ == "__main__":
    main()
