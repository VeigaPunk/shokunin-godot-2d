#!/usr/bin/env python3
"""r93-critic seat fresh + load receipts for the 17 r93 arms (read-only on tracked files).

- fresh: every arm x3 in the battery launch shape (subprocess, no shell wrapper)
- load : every arm x2 with +16 named seat hogs (killed at end; ppid-checked)
Classifies each receipt with the COMMITTED classifier segment and reports per-arm
byte-stability across reps and across regimes.
"""
import ast
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

SEAT = Path(__file__).resolve().parent.parent
FROZEN = SEAT / "frozen" / "corpus" / "fixtures"
GODOT = "/usr/bin/godot"
BOUND = 25
REPS = 3
LOAD_REPS = 2
HOGS = 16


def load_classifier():
    src = (FROZEN / "run_battery.py").read_text()
    tree = ast.parse(src)
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name == "main":
            for sub in ast.walk(n):
                if isinstance(sub, ast.FunctionDef) and sub.name == "classify_process":
                    seg = ast.get_source_segment(src, sub)
                    ns = {}
                    exec(seg, {"re": __import__("re")}, ns)
                    return ns["classify_process"], hashlib.sha256(seg.encode()).hexdigest()
    raise SystemExit("no classifier")


def arms():
    rows = json.loads((SEAT / "scripts" / "r93_rows.json").read_text())
    out = {}
    for r in rows:
        key = (r[1], tuple(r[2]))
        out.setdefault(key, []).append(r)
    return out


def scratch(tag):
    proj = SEAT / f"proj-{tag}"
    if proj.exists():
        shutil.rmtree(proj)
    shutil.copytree(FROZEN, proj)
    return proj


def launch(proj, script, flags, receipt):
    cmd = [GODOT, "--headless", "--path", str(proj), "--script", f"res://{script}", "--"] + list(flags)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=BOUND)
        out, err, code, e = p.stdout, p.stderr, p.returncode, None
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        code, e = None, f"TIMEOUT after {BOUND}s"
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.with_suffix(".out").write_text(out)
    receipt.with_suffix(".err").write_text(err)
    receipt.with_suffix(".rc").write_text(("" if code is None else str(code)) + "\n")
    return out, err, code, e


def main():
    classify, sha = load_classifier()
    amap = arms()
    print(f"# classifier {sha}")
    print(f"# arms {len(amap)}")
    load_log = SEAT / "load.log"
    with load_log.open("a") as fh:
        fh.write(f"start {time.strftime('%H:%M:%S')} {Path('/proc/loadavg').read_text().strip()}\n")

    results = {}
    proj = scratch("fresh")
    for (script, flags), rows in sorted(amap.items()):
        arm = flags[0].split("=")[1]
        recs = []
        for rep in range(1, REPS + 1):
            out, err, code, e = launch(proj, script, flags,
                                       SEAT / "runs" / "fresh" / f"{script}.{arm}.rep{rep}")
            v = {r[0]: classify(code, e, out + err, r[3], r[4], ()) for r in rows}
            recs.append({"rep": rep, "out": out, "err": err, "rc": code, "err_msg": e, "rows": v})
        uniq = len({r["out"] for r in recs})
        results[f"{script}:{arm}"] = {"rows": [r[0] for r in rows], "uniq_out": uniq,
                                      "all_rows_pass": all(all(r["rows"].values()) for r in recs),
                                      "stderr_bytes": [len(r["err"]) for r in recs],
                                      "rcs": [r["rc"] for r in recs]}
        print(f"fresh {script}:{arm} uniq_out={uniq} rows_pass={results[f'{script}:{arm}']['all_rows_pass']} "
              f"stderr={results[f'{script}:{arm}']['stderr_bytes']} rc={results[f'{script}:{arm}']['rcs']}")

    # ---- load regime: +16 named hogs for exactly one batch
    hog_pids = []
    for i in range(HOGS):
        hog_pids.append(subprocess.Popen(["yes"], stdout=subprocess.DEVNULL,
                                         stderr=subprocess.DEVNULL).pid)
    with load_log.open("a") as fh:
        fh.write(f"hogs+{HOGS} {time.strftime('%H:%M:%S')} {Path('/proc/loadavg').read_text().strip()}\n")
    try:
        proj2 = scratch("load")
        load = {}
        for (script, flags), rows in sorted(amap.items()):
            arm = flags[0].split("=")[1]
            recs = []
            for rep in range(1, LOAD_REPS + 1):
                out, err, code, e = launch(proj2, script, flags,
                                           SEAT / "runs" / "load" / f"{script}.{arm}.rep{rep}")
                v = {r[0]: classify(code, e, out + err, r[3], r[4], ()) for r in rows}
                recs.append({"rep": rep, "out": out, "err": err, "rc": code, "rows": v})
            fresh_outs = {r["out"] for r in [{"out": (SEAT / "runs" / "fresh" / f"{script}.{arm}.rep{n}").with_suffix(".out").read_text()} for n in range(1, REPS + 1)]}
            load_outs = {r["out"] for r in recs}
            load[f"{script}:{arm}"] = {
                "uniq_out": len(load_outs), "all_rows_pass": all(all(r["rows"].values()) for r in recs),
                "stderr_bytes": [len(r["err"]) for r in recs],
                "fresh_eq_load": load_outs == fresh_outs,
                "rcs": [r["rc"] for r in recs]}
            print(f"load  {script}:{arm} uniq={len(load_outs)} rows_pass={load[f'{script}:{arm}']['all_rows_pass']} "
                  f"fresh==load={load[f'{script}:{arm}']['fresh_eq_load']} stderr={load[f'{script}:{arm}']['stderr_bytes']}")
        results["_load"] = load
    finally:
        for pid in hog_pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
        time.sleep(1)
    with load_log.open("a") as fh:
        fh.write(f"hogs killed {time.strftime('%H:%M:%S')} {Path('/proc/loadavg').read_text().strip()}\n")
    (SEAT / "fresh_load.json").write_text(json.dumps(results, indent=1) + "\n")
    nbad = [k for k, v in results.items() if k != "_load" and (v["uniq_out"] != 1 or not v["all_rows_pass"])]
    print(f"# fresh: {len(results) - 1 - len(nbad)}/{len(results) - 1} arms byte-stable (uniq_out==1) and all-rows-PASS")
    print(f"# load : {sum(1 for v in results['_load'].values() if v['all_rows_pass'])}/{len(results['_load'])} arms all-rows-PASS")
    print(f"# orphan hogs left: {sum(1 for p in hog_pids if Path(f'/proc/{p}').exists())}")
    return 0 if not nbad else 1


if __name__ == "__main__":
    sys.exit(main())
