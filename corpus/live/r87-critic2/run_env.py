#!/usr/bin/env python3
"""r87-critic2 focused envelope check on the FOLDED HEAD bytes.

Runs the 5 tuple-signature rows (api_press, pre_frame, press_phys,
release_edge, ui_ns) N reps each under optional CPU load, in the battery's
launch shape, and classifies each rep against the two whitelisted payloads
using the production rule (rc==0, no unrelated ERROR:, no SCRIPT ERROR /
Parse Error, one payload present).

No tracked writes: scratch project under corpus/live/r87-critic2/proj.
Every godot launch is one fresh process under a per-rep timeout (8 s).
"""
import argparse
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
FIXTURES = REPO / "corpus" / "fixtures"
PROJ = HERE / "proj"
PAT = re.compile(r"^(PASS|FAIL) input_lattice (\S+) (.*)$", re.M)

ARMS = {
    "input_lattice_api_press": "api_press",
    "input_lattice_pre_frame": "pre_frame",
    "input_lattice_press_phys": "press_phys",
    "input_lattice_release_edge": "release_edge",
    "input_lattice_ui_ns": "ui_ns",
}


def landed_evidence():
    src = (FIXTURES / "run_battery.py").read_text()
    i = src.index("CASES = [")
    k = i
    while True:
        k = src.index("\n]", k)
        if src[k + 2:k + 3] in ("\n", "\r", ""):
            break
        k += 1
    rows = ast.literal_eval(src[i:k + 2][src[i:k + 2].index("["):])
    return {r[0]: r[4] for r in rows if r[0] in ARMS}


def make_proj():
    if PROJ.exists():
        shutil.rmtree(PROJ)
    PROJ.mkdir(parents=True)
    for item in FIXTURES.iterdir():
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, PROJ / item.name)
        else:
            shutil.copy2(item, PROJ / item.name)
    shutil.copy2(PROJ / "controls" / "pickup.tscn", PROJ / "pickup.tscn")


def one_rep(arm, timeout=8):
    env = dict(os.environ)
    env["XDG_DATA_HOME"] = str(HERE / "xdg-data")
    cmd = ["godot", "--headless", "--path", str(PROJ),
           "--script", "res://input_lattice.gd", "--", f"--arm={arm}"]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
        out, rc, err = p.stdout + p.stderr, p.returncode, None
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or "") + (exc.stderr or "")
        rc, err = 124, "timeout"
    return {"arm": arm, "rc": rc, "error": err, "dur": round(time.time() - t0, 3),
            "output": out}


def classify(out, payloads):
    if not out:
        return "no-output", None
    lines = out.splitlines()
    if any("SCRIPT ERROR:" in l for l in lines) or any("Parse Error:" in l for l in lines):
        return "script-parse-error", None
    if any("ERROR:" in l for l in lines):
        return "unrelated-error", None
    hits = [i for i, sig in enumerate(payloads)
            if any(sig in line for line in lines)]
    if len(hits) == 1:
        return "PASS", hits[0]
    if len(hits) == 0:
        return "FAIL-no-payload", None
    return "FAIL-both", None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=8)
    ap.add_argument("--load", type=int, default=0)
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()

    ev = landed_evidence()
    make_proj()
    hogs = [subprocess.Popen([sys.executable, "-c", "while True: pass"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            for _ in range(args.load)]
    results = []
    try:
        for arm in ARMS:
            payloads = ev[arm]
            for rep in range(args.reps):
                r = one_rep(ARMS[arm])
                verdict, hit = classify(r["output"], payloads)
                m = PAT.search(r["output"])
                r.update({"case": arm, "verdict": verdict, "payload_hit": hit,
                          "pass_line": m.group(0)[:200] if m else None})
                results.append(r)
                print(f"{arm} rep{rep}: {verdict} payload={hit} rc={r['rc']} dur={r['dur']}", flush=True)
    finally:
        for h in hogs:
            h.kill()
    summary = {}
    for arm in ARMS:
        rr = [r for r in results if r["case"] == arm]
        summary[arm] = {
            "n": len(rr),
            "verdicts": sorted({r["verdict"] for r in rr}),
            "hits": {str(h): sum(1 for r in rr if r["payload_hit"] == h)
                     for h in {r["payload_hit"] for r in rr}},
        }
    out = {"tag": args.tag, "load": args.load, "summary": summary, "results": results}
    dest = HERE / f"env-load{args.load}-{args.tag}.json"
    dest.write_text(json.dumps(out, indent=1))
    print(json.dumps(summary, indent=1))
    print("wrote", dest)


if __name__ == "__main__":
    main()
