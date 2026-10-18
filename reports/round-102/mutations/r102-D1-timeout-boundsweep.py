#!/usr/bin/env python3
"""r102-D1 phase D: bound sweep counterfactual for the timeout probe's
slow_clean_old_bound arm. Same fixture, same bounded_run semantics as the
run_battery driver; only timeout_seconds varies. Shows the crossover bound at
which marker_observed flips false->true (== boot-to-marker latency), i.e. the
margin between the shipped 0.75s bound and this host's Godot boot latency.

Usage: python3 r102-D1-timeout-boundsweep.py <reps-per-bound>
Writes /var/tmp/r102-D1/d1-boundsweep.json
"""
import importlib.util
import json
import subprocess
import sys
import time

spec = importlib.util.spec_from_file_location(
    "d1standalone",
    "/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/reports/round-102/mutations/r102-D1-timeout-standalone.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

BOUNDS = [0.75, 0.9, 1.0, 1.1, 1.25, 1.5]


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    out = {"bounds": BOUNDS, "reps": reps, "host_loadavg_at_start": None,
           "rows": [], "godot_version": mod.subprocess.run(
               [mod.GODOT, "--version"], capture_output=True, text=True).stdout.strip()}
    with open("/proc/loadavg") as fh:
        out["host_loadavg_at_start"] = fh.read().strip()
    for bound in BOUNDS:
        for rep in range(reps):
            rec = mod.bounded_run("slow_clean_old_bound", ["--delay-clean"], bound)
            rec["rep"] = rep + 1
            out["rows"].append(rec)
            print(f"bound={bound} rep{rep+1}: marker={rec['marker_observed']} "
                  f"timed_out={rec['timed_out']} elapsed={rec['elapsed_seconds']} "
                  f"err={rec['error']}", flush=True)
    with open("/var/tmp/r102-D1/d1-boundsweep.json", "w") as fh:
        json.dump(out, fh, indent=2)
    print("WROTE /var/tmp/r102-D1/d1-boundsweep.json")


if __name__ == "__main__":
    main()
