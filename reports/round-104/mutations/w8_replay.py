#!/usr/bin/env python3
"""r104-W8 probe cost census replay.

Reads a stored battery verdicts.json, rebuilds each ordinary row's command
exactly as run_battery.py:2228-2236 would, and times it with wall clock.
Writes one JSONL record per row. Does NOT import or execute run_battery.py.
"""
import json, os, subprocess, sys, time, argparse
from pathlib import Path

SCRATCH = Path("/var/tmp/r104-w8/scratch")
XDG = Path("/var/tmp/r104-w8/xdg-data")
GODOT = "godot"


def build(row):
    script = row["script"]
    flags = row.get("flags") or []
    if script.startswith("__save_process_"):
        mode = script.removeprefix("__save_process_").removesuffix("__")
        pflags = {"writer": [], "reader": ["--reader"], "missing": ["--missing"]}[mode]
        return [GODOT, "--headless", "--path", str(SCRATCH), "--script",
                "res://save_process.gd", "--", *pflags], True
    if script.startswith("__godot_export"):
        return None, False
    return [GODOT, "--headless", "--path", str(SCRATCH), "--script",
            "res://" + script, "--", *flags], False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verdicts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", default="")
    args = ap.parse_args()

    j = json.load(open(args.verdicts))
    rows = [r for r in j["results"] if "script" in r]
    if args.only:
        want = set(args.only.split(","))
        rows = [r for r in rows if r["case"] in want]
    if args.limit:
        rows = rows[: args.limit]

    XDG.mkdir(parents=True, exist_ok=True)
    out = open(args.out, "w")
    for i, row in enumerate(rows):
        cmd, needs_xdg = build(row)
        if cmd is None:
            out.write(json.dumps({"case": row["case"], "script": row["script"],
                                  "skipped": "export-class"}) + "\n")
            continue
        env = os.environ.copy()
        if needs_xdg:
            env["XDG_DATA_HOME"] = str(XDG)
        t0 = time.monotonic()
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=env)
            rc, err = p.returncode, None
            ob = len((p.stdout or "").encode()) + len((p.stderr or "").encode())
        except subprocess.TimeoutExpired:
            rc, err, ob = None, "TIMEOUT after 60 seconds", 0
        dt = time.monotonic() - t0
        out.write(json.dumps({"case": row["case"], "script": row["script"],
                              "flags": row.get("flags") or [],
                              "expected_exit": row["expected_exit"],
                              "actual_exit": rc, "error": err,
                              "wall_ms": round(dt * 1000, 1), "out_bytes": ob,
                              "row_verdict": row["verdict"]}) + "\n")
        out.flush()
        if i % 25 == 0:
            print(f"[{i}/{len(rows)}] {row['case']} {dt*1000:.0f}ms", flush=True)
    out.close()


if __name__ == "__main__":
    main()
