#!/usr/bin/env python3
"""r102-connector: host timing probe for the r62 timeout arms (lane repo read-only).

Measures on this host, at this moment's load:
  A) unbounded runs, timestamped stdout lines: banner time vs marker time vs exit time.
  B) bounded_run replica (Popen + communicate(timeout), same as run_battery.py:5322-5369)
     at 0.75s (old bound) and 3.0s (new bound), --delay-clean arm.

Scratch: /var/tmp/r102-connector/proj (copy of corpus/fixtures/{project.godot,timeout_probe.gd}).
Writes nothing into the lane repo. NOT run_battery.py.
"""
import datetime
import json
import subprocess
import sys
import time

GODOT = sys.argv[1] if len(sys.argv) > 1 else "/usr/bin/godot"
PROJ = "/var/tmp/r102-connector/proj"
MARKER = "TIMEOUT_PROBE: expected signature"


def timed_unbounded(case):
    cmd = [GODOT, "--headless", "--path", PROJ, "--script", "res://timeout_probe.gd", "--", "--delay-clean"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    t0 = time.monotonic()
    events = []
    for line in p.stdout:
        events.append([round(time.monotonic() - t0, 3), line.rstrip("\n")])
    rc = p.wait()
    total = round(time.monotonic() - t0, 3)
    banner = next((t for t, l in events if "Godot Engine" in l), None)
    marker = next((t for t, l in events if MARKER in l), None)
    return {"case": case, "exit": rc, "total_s": total, "banner_s": banner, "marker_s": marker, "lines": events}


def bounded(case, bound):
    cmd = [GODOT, "--headless", "--path", PROJ, "--script", "res://timeout_probe.gd", "--", "--delay-clean"]
    m = {"case": case, "bound": bound, "timed_out": False, "actual_exit": None,
         "marker_observed": False, "elapsed": None, "error": None}
    t0 = time.monotonic()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    try:
        out, err = p.communicate(timeout=bound)
        m["actual_exit"] = p.returncode
    except subprocess.TimeoutExpired as exc:
        m["timed_out"] = True
        out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        m["error"] = f"TIMEOUT after {bound} seconds"
        if p.poll() is None:
            p.kill()
        out2, err2 = p.communicate(timeout=3)
        out = (out or "") + (out2 or "")
    m["marker_observed"] = MARKER in out
    m["elapsed"] = round(time.monotonic() - t0, 3)
    return m


def main():
    results = {"godot": GODOT, "load_before": open("/proc/loadavg").read().strip(),
               "at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    for i in range(3):
        results[f"unbounded_{i}"] = timed_unbounded(f"unbounded_{i}")
    b = [bounded(f"bound075_{i}", 0.75) for i in range(3)]
    b.append(bounded("bound300_0", 3.0))
    results["bounded"] = b
    results["load_after"] = open("/proc/loadavg").read().strip()
    print(json.dumps(results, indent=1))


main()
