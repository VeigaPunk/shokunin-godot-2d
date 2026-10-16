#!/usr/bin/env python3
"""r94-simplifier volatile-row flake probe.

The two full-battery control runs on the committed bytes failed ONLY on the
pre-existing load-conditioned scene-install race rows (`overlap`, `transition`),
the same class the r93/r94 reviewers enumerate. This probe quantifies the
`transition` row's pass rate on this host: N launches of
`controls/scene_transition_probe.gd` in the battery's exact launch shape
(scratch project copy, `--headless --path <proj> --script res://...`).

Usage: python3 flake_probe.py [--reps 10]
Outputs: flake-probe.txt (+ scratch under fold-runs/<stamp>/scratch-flake)
"""
import argparse
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE / "proj"
GODOT = "godot"
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=10)
    args = ap.parse_args()

    scratch = HERE / "fold-runs" / STAMP / "scratch-flake"
    scratch.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(PROJ, scratch)
    pf = scratch / "project.godot"
    pf.write_text(pf.read_text().replace(
        'config/name="MechanicOneShotTest"',
        'config/name="MechanicOneShotTest-%s"' % scratch.name, 1))

    results = []
    for r in range(1, args.reps + 1):
        cmd = [GODOT, "--headless", "--path", str(scratch),
               "--script", "res://controls/scene_transition_probe.gd"]
        t0 = time.time()
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        out = proc.stdout + proc.stderr
        ok = proc.returncode == 0 and "PASS valid_transition=true" in out
        results.append({"rep": r, "rc": proc.returncode, "pass": ok,
                        "wall_s": round(time.time() - t0, 3),
                        "line": next((l for l in out.splitlines()
                                      if l.startswith("PASS ") or "ERROR:" in l), "")})
        print("rep %2d rc=%s pass=%s %s" % (r, proc.returncode, ok, results[-1]["line"][:120]))

    npass = sum(1 for x in results if x["pass"])
    print("transition flake probe: %d/%d PASS on this host" % (npass, args.reps))
    (HERE / "flake-probe.txt").write_text(
        "stamp: %s\nhost loadavg: %s\ncase: controls/scene_transition_probe.gd\n"
        "launch: godot --headless --path <scratch> --script res://controls/scene_transition_probe.gd\n"
        "result: %d/%d PASS\n" % (STAMP, open("/proc/loadavg").read().strip(),
                                  npass, args.reps)
        + "".join("  rep %2d rc=%s pass=%s wall=%ss\n" % (x["rep"], x["rc"], x["pass"], x["wall_s"])
                  for x in results)
        + "lines:\n" + "".join("  %s\n" % x["line"] for x in results))


if __name__ == "__main__":
    main()
