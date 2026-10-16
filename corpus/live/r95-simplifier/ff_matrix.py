#!/usr/bin/env python3
"""r95-simplifier scheduler-robustness re-check of the landed order-law rows.

The boundary folded `--fixed-fps` and load into the landing by pinning the
k(k-1) ladder rows in their scheduler-invariant form. This re-verifies, on the
landed bytes, that the 11 order-law rows still emit their committed signatures
under `--fixed-fps 30`, `--fixed-fps 120`, and a 12-hog load.

Usage: python3 ff_matrix.py > ff-matrix.txt
Outputs: ff-matrix.json, ff-runs/<stamp>/
"""
import ast
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CF = HERE / "committed-fixtures"
HARNESS = CF / "run_battery.py"
REPO = HERE.parents[2]
FIXTURES = REPO / "corpus" / "fixtures"
GODOT = "godot"
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
ROWS = ["r95b_order_canon", "r95b_order_period_k5"] + \
       ["r95b_order_periodx_k%s" % k for k in ("2", "3", "4", "5", "5s8", "6", "7", "8", "10")]


def rows_and_classifier():
    src = HARNESS.read_text()
    tree = ast.parse(src)
    cases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            for elt in node.value.elts:
                t = ast.literal_eval(elt)
                cases[t[0]] = {"script": t[1], "flags": list(t[2]),
                               "expected_exit": t[3], "signature": t[4]}
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "classify_process")
    ns = {}
    exec("import re\n" + ast.get_source_segment(src, fn), ns)
    return cases, ns["classify_process"]


def stage(dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    for item in FIXTURES.iterdir():
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, dest / item.name)
        else:
            shutil.copy2(item, dest / item.name)
    pf = dest / "project.godot"
    pf.write_text(pf.read_text().replace('config/name="MechanicOneShotTest"',
                                         'config/name="MechanicOneShotTest-%s"' % dest.name, 1))
    shutil.copy2(dest / "controls" / "pickup.tscn", dest / "pickup.tscn")
    chain = dest / "causal_chain.gd"
    t = chain.read_text()
    chain.write_text(t.replace("    await process_frame\n    var old := current_scene",
                               "    await process_frame\n    await process_frame\n    var old := current_scene", 1))
    return dest


def launch(scratch: Path, script: str, flags: list, engine_flags: list, timeout=8):
    cmd = [GODOT, "--headless", *engine_flags, "--path", str(scratch),
           "--script", "res://" + script, "--", *flags]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.stdout, p.stderr, p.returncode, None
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return out, err, None, "TIMEOUT"
    except OSError as exc:
        return "", str(exc), None, "OSError"


def main() -> int:
    cases, classify = rows_and_classifier()
    scratch = stage(HERE / "ff-runs" / STAMP / "scratch")
    variants = [("ff30", ["--fixed-fps", "30"]), ("ff120", ["--fixed-fps", "120"])]
    results, failures = {}, []
    for label, eflags in variants:
        for row in ROWS:
            spec = cases[row]
            reps = []
            for rep in range(1, 3):
                out, err, rc, terr = launch(scratch, spec["script"], spec["flags"], eflags)
                ok = classify(rc, terr, out + err, spec["expected_exit"], spec["signature"], ())
                reps.append({"rep": rep, "rc": rc, "error": terr, "passed": ok})
                if not ok:
                    failures.append("%s %s rep%d" % (label, row, rep))
            results["%s/%s" % (label, row)] = reps
            print("%-6s %-30s pass=%d/2" % (label, row, sum(1 for r in reps if r["passed"])))
    # load variant: 12 seat hogs, default fps
    pids = []
    for _ in range(12):
        pids.append(subprocess.Popen(["yes"], stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL, preexec_fn=os.setsid))
    print("hogs: %s  loadavg %s" % (pids, open("/proc/loadavg").read().strip()))
    try:
        for row in ROWS:
            spec = cases[row]
            reps = []
            for rep in range(1, 3):
                out, err, rc, terr = launch(scratch, spec["script"], spec["flags"], [])
                ok = classify(rc, terr, out + err, spec["expected_exit"], spec["signature"], ())
                reps.append({"rep": rep, "rc": rc, "error": terr, "passed": ok})
                if not ok:
                    failures.append("load %s rep%d" % (row, rep))
            results["load/%s" % row] = reps
            print("%-6s %-30s pass=%d/2" % ("load", row, sum(1 for r in reps if r["passed"])))
    finally:
        for p in pids:
            try:
                os.killpg(os.getpgid(p.pid), signal.SIGKILL)
            except OSError:
                pass
    print("loadavg end: %s" % open("/proc/loadavg").read().strip())
    summary = {"stamp": STAMP, "rows": ROWS, "variants": ["ff30", "ff120", "load12"],
               "results": results, "failures": failures,
               "all_pass": not failures}
    (HERE / "ff-matrix.json").write_text(json.dumps(summary, indent=1))
    print("failures: %d  all_pass: %s" % (len(failures), not failures))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
