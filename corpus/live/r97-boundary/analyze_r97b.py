#!/usr/bin/env python3
"""r97-boundary analyzer — stability within a mode, portability across modes,
and the r97-scout author rows replayed against every mode's receipts.

Modes are the directories under runs/.  For each cell it reports:
  reps / out_uniq / err_uniq / pass_uniq / rc set / stderr bytes
then compares each mode's PASS payload against the quiet payload (the r97
canonical mode) and, for the r97b arms, compares every `key=value` pair.

Finally it extracts the production `classify_process` from
corpus/fixtures/run_battery.py by AST and classifies the r97-scout ROWS and
ROWS_PREFIX against every receipt of every mode (stdout+stderr merged exactly
like run_battery.run_process does).
"""
import ast
import hashlib
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
RUNS = HERE / "runs"
SCOUT = HERE.parent / "r97-scout"
FIXTURE = HERE.parent.parent / "fixtures" / "run_battery.py"

MODES = ["quiet", "load", "ff30", "ff60", "ff120", "ff1"]
CELLS = [
    "r97b_order_ticks", "r97b_order_priority", "r97b_defer_capture_order",
    "r97b_defer_phase", "r97b_frame_shape", "r97b_phys_await",
    # secondary probe (probes/r97b_extra.gd via run_extra.sh), subset of modes
    "r97b_order_churn", "r97b_unique_boundary",
    "scout_census", "scout_group_order", "scout_group_order_rev",
    "scout_group_flags", "scout_group_lifecycle", "scout_group_setters",
    "scout_signal_order", "scout_signal_flags", "scout_defer_ladder",
    "scout_defer_slots", "scout_defer_order", "scout_scene_probe",
]


def reps(mode, cell):
    out = []
    for f in sorted((RUNS / mode).glob(f"{cell}.rep*.out")):
        n = int(re.search(r"rep(\d+)\.out$", f.name).group(1))
        err = f.with_suffix(".err")
        rc = f.with_suffix(".rc")
        out.append((n, f.read_text(), err.read_text() if err.exists() else "",
                    int(rc.read_text().strip()) if rc.exists() else None))
    out.sort()
    return out


def pass_line(text):
    for line in text.splitlines():
        if line.startswith("PASS "):
            return line
    return ""


def kv_lines(text, arm):
    d = {}
    for line in text.splitlines():
        if line.startswith("R97 r97b_lattice %s " % arm):
            body = line[len("R97 r97b_lattice %s " % arm):]
            if "=" in body:
                k, v = body.split("=", 1)
                d[k] = v
    return d


def main():
    report = {"modes": {}, "cross_mode": {}, "rows": {}}
    print("=== per-mode stability ===")
    for mode in MODES:
        if not (RUNS / mode).exists():
            continue
        per = {}
        for cell in CELLS:
            rs = reps(mode, cell)
            if not rs:
                continue
            outs = {r[1] for r in rs}
            errs = {r[2] for r in rs}
            passes = {pass_line(r[1]) for r in rs}
            rcs = sorted({r[3] for r in rs}, key=lambda x: -1 if x is None else x)
            per[cell] = {
                "reps": len(rs),
                "out_uniq": len(outs),
                "err_uniq": len(errs),
                "pass_uniq": len(passes),
                "rcs": rcs,
                "err_bytes": sorted({len(r[2]) for r in rs}),
                "pass": pass_line(rs[0][1]),
            }
            flag = "" if len(passes) == 1 and rcs == [0] else "  <-- UNSTABLE"
            print(f"{mode:6s} {cell:26s} reps={len(rs)} out_uniq={len(outs)} "
                  f"err_uniq={len(errs)} pass_uniq={len(passes)} rc={rcs} "
                  f"errB={sorted({len(r[2]) for r in rs})}{flag}")
        report["modes"][mode] = per

    print()
    print("=== cross-mode: scout cells vs quiet (PASS payload) ===")
    base = report["modes"].get("quiet", {})
    for cell in CELLS:
        if not cell.startswith("scout_") or cell not in base:
            continue
        variants = {}
        for mode in MODES:
            p = report["modes"].get(mode, {}).get(cell, {}).get("pass")
            if p:
                variants.setdefault(p, []).append(mode)
        if len(variants) == 1:
            print(f"{cell:26s} IDENTICAL in all modes")
        else:
            print(f"{cell:26s} {len(variants)} DISTINCT payloads:")
            for p, modes in variants.items():
                print(f"    modes={modes}")
                print(f"      {p[:200]}")
        report["cross_mode"][cell] = {p: m for p, m in variants.items()}

    print()
    print("=== cross-mode: r97b arm keys ===")
    print("buckets: LAW = one value in every mode and every rep; "
          "HOST = varies across reps inside at least one mode (host-coupled); "
          "MODE = stable inside each mode but differs across modes; BOTH.")
    for cell in CELLS:
        if not cell.startswith("r97b_"):
            continue
        arm = cell[len("r97b_"):]
        keys = {}
        for mode in MODES:
            per_mode = {}
            for n, out, err, rc in reps(mode, cell):
                for k, v in kv_lines(out, arm).items():
                    per_mode.setdefault(k, set()).add(v)
            for k, vs in per_mode.items():
                keys.setdefault(k, {})[mode] = sorted(vs)
        buckets = {"LAW": [], "HOST": [], "MODE": [], "BOTH": []}
        for k, by_mode in sorted(keys.items()):
            within = all(len(v) == 1 for v in by_mode.values())
            allvals = {v for vs in by_mode.values() for v in vs}
            cross = len(allvals) > 1
            if within and not cross:
                buckets["LAW"].append(k)
            elif not within and not cross:
                buckets["HOST"].append(k)
            elif within and cross:
                buckets["MODE"].append(k)
            else:
                buckets["BOTH"].append(k)
        print(f"{cell:26s} keys={len(keys)} "
              f"LAW={len(buckets['LAW'])} HOST={len(buckets['HOST'])} "
              f"MODE={len(buckets['MODE'])} BOTH={len(buckets['BOTH'])}")
        for b in ("MODE", "BOTH", "HOST"):
            for k in buckets[b]:
                print(f"    {b:4s} {k}: " + " | ".join(
                    f"{m}={keys[k][m]}" for m in MODES if m in keys[k]))
        report["cross_mode"][cell] = {
            "buckets": {b: v for b, v in buckets.items()},
            "by_mode": keys,
        }

    # ---- row replay with the production classifier
    print()
    print("=== r97-scout rows replayed on every mode's receipts ===")
    src = FIXTURE.read_text()
    tree = ast.parse(src)
    fn_src = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
            fn_src = ast.get_source_segment(src, node)
            break
    assert fn_src, "classify_process not found"
    seg_sha = hashlib.sha256(fn_src.encode()).hexdigest()
    ns = {}
    exec("import re\n" + fn_src, ns)
    classify_process = ns["classify_process"]
    rows_ns = {}
    exec((SCOUT / "author-rows.py.txt").read_text(), rows_ns)
    ROWS = rows_ns["ROWS"]
    ROWS_PREFIX = rows_ns["ROWS_PREFIX"]
    EXPECTED = rows_ns.get("EXPECTED_ERRORS", {})
    RUN_PREFIX = {"stree_lattice_group_order_rev": "group_order_rev"}

    def run_prefix(case):
        if case in RUN_PREFIX:
            return RUN_PREFIX[case]
        return case[len("stree_lattice_"):]

    for label, rows in (("ROWS(full-line)", ROWS), ("ROWS_PREFIX", ROWS_PREFIX)):
        print(f"[{label}]")
        for mode in MODES:
            if not (RUNS / mode).exists():
                continue
            rej = []
            checked = 0
            for case, script, flags, expected_exit, sig in rows:
                pre = run_prefix(case)
                for f in sorted((RUNS / mode).glob(f"scout_{pre}.rep*.out")):
                    err = f.with_suffix(".err")
                    rc = f.with_suffix(".rc")
                    out = f.read_text() + (err.read_text() if err.exists() else "")
                    code = int(rc.read_text().strip())
                    checked += 1
                    if not classify_process(code, None, out, expected_exit, sig,
                                            EXPECTED.get(case, ())):
                        rej.append((case, f.name))
            print(f"  {mode:6s} checked={checked} rejected={len(rej)} {rej[:6]}")
            report["rows"].setdefault(label, {})[mode] = {
                "checked": checked, "rejected": rej}
    print(f"classify_process segment sha256={seg_sha[:16]}")

    (HERE / "runs" / "analyze_r97b.json").write_text(json.dumps(report, indent=1))
    print("\nwrote runs/analyze_r97b.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
