#!/usr/bin/env python3
"""r87-verifier2 bounded probe: focused input_lattice api_press reps.

Mirrors r87-critic/run_critic.py: fresh `godot --headless --path <proj>
--script res://input_lattice.gd -- --arm=api_press` per rep under an 8 s
bound (the battery's non-export timeout). Classification is the production
rule for this row: exit 0, no harness error, no "SCRIPT ERROR:"/"Parse
Error:", zero unrelated "ERROR:" lines (expected_errors=() for this row),
and >= 1 whitelisted envelope payload present in merged output.

Writes are this file's JSON receipts under corpus/live/r87-verifier2/ only.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE / "proj"
# The landed 7ef247c envelope for input_lattice_api_press (CASES row).
PAYLOADS = (
    'PASS input_lattice api_press imm[1/0.70/1/0] raw=0.70 pl=["ap"] recv=[] '
    'pr=["pr0{ap=1/0.70/1/0}", "pr1{ap=1/0.70/0/0}", "pr2{ap=0/0.00/0/1}"] '
    'ph=["ph1{ap=1/0.70/1/1}", "ph2{ap=0/0.00/0/0}", "ph3{ap=0/0.00/0/1}"]',
    'PASS input_lattice api_press imm[1/0.70/1/0] raw=0.70 pl=["ap"] recv=[] '
    'pr=["pr0{ap=1/0.70/1/0}", "pr1{ap=1/0.70/0/0}", "pr2{ap=0/0.00/0/1}"] '
    'ph=["ph1{ap=1/0.70/1/0}", "ph2{ap=0/0.00/0/0}", "ph3{ap=0/0.00/0/1}"]',
)


def one_rep(idx, timeout=8):
    env = dict(os.environ)
    env["XDG_DATA_HOME"] = str(HERE / "xdg-data")
    cmd = ["godot", "--headless", "--path", str(PROJ),
           "--script", "res://input_lattice.gd", "--", "--arm=api_press"]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout, env=env)
        out, rc, err = p.stdout + p.stderr, p.returncode, None
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or "") + (exc.stderr or "")
        rc, err = None, f"TIMEOUT after {timeout} seconds"
    hit = [i for i, sig in enumerate(PAYLOADS) if sig in out]
    error_lines = [ln for ln in out.splitlines() if "ERROR:" in ln]
    passed = (rc == 0 and err is None and bool(hit)
              and not error_lines
              and "SCRIPT ERROR:" not in out and "Parse Error:" not in out)
    pass_line = next((ln.strip() for ln in out.splitlines()
                      if ln.startswith("PASS input_lattice api_press")), None)
    return {"rep": idx, "rc": rc, "error": err,
            "dur": round(time.time() - t0, 3),
            "payload_hit": hit, "pass_line": pass_line,
            "error_lines": error_lines, "verdict": "PASS" if passed else "FAIL"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=8)
    ap.add_argument("--load", type=int, default=0,
                    help="CPU hog processes during the batch")
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()
    hogs = []
    for _ in range(args.load):
        hogs.append(subprocess.Popen(
            [sys.executable, "-c", "while True: pass"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
    try:
        reps = [one_rep(i) for i in range(args.reps)]
    finally:
        for h in hogs:
            h.kill()
        for h in hogs:
            h.wait()
    counts = {"p0": 0, "p1": 0, "both": 0, "neither": 0}
    for r in reps:
        if r["payload_hit"] == [0]:
            counts["p0"] += 1
        elif r["payload_hit"] == [1]:
            counts["p1"] += 1
        elif len(r["payload_hit"]) == 2:
            counts["both"] += 1
        else:
            counts["neither"] += 1
    payload = {"tag": args.tag, "arm": "api_press", "reps": args.reps,
               "load_hogs": args.load, "mode_counts": counts,
               "all_pass": all(r["verdict"] == "PASS" for r in reps),
               "verdicts": [r["verdict"] for r in reps], "results": reps}
    out = HERE / f"apipress-{args.tag}.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({k: payload[k] for k in
                      ("tag", "reps", "load_hogs", "mode_counts", "all_pass")}))
    print(f"receipt: {out}")
    return 0 if payload["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
