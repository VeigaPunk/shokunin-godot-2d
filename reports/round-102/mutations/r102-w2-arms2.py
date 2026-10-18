#!/usr/bin/env python3
"""r102-w2 part 2: hold-open arm replications (predicate check) + r101-scratch fidelity arms.

- hold_open_new_bound x6 against /var/tmp/r102-w2/proj (exact bounded_run replication, bound 3.0)
- delay-clean timestamped x6 against a copy of the actual r101 run scratch
- delay-clean old-bound replication x6 against the same copy
Census per trial. Prints hold_rejects predicate per trial.
"""
import json
import os
import selectors
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

GODOT = "/usr/bin/godot"
MARKER = "TIMEOUT_PROBE: expected signature"
W2 = Path("/var/tmp/r102-w2")
PROJ = str(W2 / "proj")
R101_SCRATCH = str(W2 / "scratch-r101")
OUT = W2 / "trials2.json"


def census():
    godot = zombies = 0
    for p in Path("/proc").iterdir():
        if not p.name.isdigit():
            continue
        try:
            comm = (p / "comm").read_text().strip()
            stat = (p / "stat").read_text()
        except OSError:
            continue
        if comm == "godot":
            godot += 1
        if stat.rsplit(")", 1)[1].split()[0] == "Z":
            zombies += 1
    return {"godot": godot, "zombies": zombies, "load": [round(x, 2) for x in os.getloadavg()]}


def bounded_run(proj, case, extra_args, bound, cleanup_seconds=3):
    command = [GODOT, "--headless", "--path", proj, "--script",
               "res://timeout_probe.gd", "--"] + extra_args
    rec = {"case": case, "command": command, "timeout_seconds": bound,
           "census_before": census(), "timed_out": False, "marker_observed": False,
           "actual_exit": None, "error": None, "raw_stdout": ""}
    t0 = time.monotonic()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, bufsize=1)
    try:
        out, err = proc.communicate(timeout=bound)
        rec["actual_exit"] = proc.returncode
    except subprocess.TimeoutExpired as exc:
        rec["timed_out"] = True
        out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        rec["pre_timeout_stdout"] = out
        rec["process_was_running"] = proc.poll() is None
        rec["error"] = f"TIMEOUT after {bound} seconds"
        if proc.poll() is None:
            proc.kill()
        more_out, err = proc.communicate(timeout=cleanup_seconds)
        out = more_out or ""
        rec["cleanup_exit_code"] = proc.returncode
    rec["elapsed_seconds"] = round(time.monotonic() - t0, 3)
    rec["raw_stdout"] = out
    rec["direct_child_alive_after_cleanup"] = proc.poll() is None
    rec["marker_observed"] = MARKER in out
    rec["inner_classification"] = False
    rec["census_after"] = census()
    return rec


def timestamped(proj, series, i, extra_args, bound=8.0):
    command = [GODOT, "--headless", "--path", proj, "--script",
               "res://timeout_probe.gd", "--"] + extra_args
    rec = {"series": series, "index": i, "command": command, "bound": bound,
           "census_before": census()}
    t0 = time.monotonic()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, bufsize=1)
    lines = []
    errs = []
    threading.Thread(target=lambda: [errs.append(l) for l in proc.stderr], daemon=True).start()
    sel = selectors.DefaultSelector()
    sel.register(proc.stdout, selectors.EVENT_READ)
    deadline = t0 + bound
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            rest = proc.stdout.read()
            if rest:
                lines.append((round(time.monotonic() - t0, 4), rest))
            break
        for key, _ in sel.select(min(0.1, max(0.0, deadline - time.monotonic()))):
            line = key.fileobj.readline()
            if line:
                lines.append((round(time.monotonic() - t0, 4), line))
    sel.close()
    if proc.poll() is None:
        proc.kill()
    proc.wait(timeout=3)
    rec["exit"] = proc.returncode
    rec["elapsed_seconds"] = round(time.monotonic() - t0, 4)
    rec["marker_at"] = next((t for t, l in lines if MARKER in l), None)
    rec["banner_at"] = next((t for t, l in lines if "Godot Engine v" in l), None)
    rec["census_after"] = census()
    return rec


def main():
    out = {"godot": subprocess.run([GODOT, "--version"], capture_output=True, text=True).stdout.strip(),
           "uptime": subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip(),
           "hold": [], "r101_scratch_delay": [], "r101_scratch_old": [], "stats": {}}
    # 1) hold-open arm x6 on my scratch (exact bounded_run semantics)
    for i in range(6):
        r = bounded_run(PROJ, "hold_open_new_bound", ["--hold-open"], 3.0)
        r["index"] = i
        r["hold_rejects"] = (r["timed_out"] and r["marker_observed"]
                             and r["inner_classification"] is False
                             and r["direct_child_alive_after_cleanup"] is False)
        out["hold"].append(r)
        print(f"hold[{i}] timed_out={r['timed_out']} marker={r['marker_observed']} "
              f"cleanup_rc={r.get('cleanup_exit_code')} alive_after={r['direct_child_alive_after_cleanup']} "
              f"hold_rejects={r['hold_rejects']} census_before={r['census_before']}")
    # 2) fidelity arms on a copy of the actual r101 run scratch
    src = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/"
               "corpus/live/runs/20261018T202131127599Z/scratch")
    if not Path(R101_SCRATCH).exists():
        shutil.copytree(src, R101_SCRATCH, symlinks=True)
    w = timestamped(R101_SCRATCH, "warmup_r101scratch", 0, ["--delay-clean"])
    out["r101_scratch_warmup"] = w
    for i in range(6):
        r = timestamped(R101_SCRATCH, "r101_scratch_delay", i, ["--delay-clean"])
        out["r101_scratch_delay"].append(r)
        print(f"r101scratch[{i}] marker_at={r['marker_at']} exit={r['exit']} {r['census_before']}")
    for i in range(6):
        r = bounded_run(R101_SCRATCH, "slow_clean_old_bound", ["--delay-clean"], 0.75)
        r["index"] = i
        out["r101_scratch_old"].append(r)
        print(f"r101scratch_old[{i}] timed_out={r['timed_out']} marker={r['marker_observed']} "
              f"stdout_tail={r['raw_stdout'][-40:]!r} {r['census_before']}")
    # 3) stats
    tl = json.load(open(W2 / "trials.json"))
    marks = {}
    for name, rs in tl["series"].items():
        if name == "warmup":
            continue
        vals = [r["marker_observed_at"] for r in rs if r.get("marker_observed_at")]
        marks[name] = vals
    marks["r101_scratch_delay"] = [r["marker_at"] for r in out["r101_scratch_delay"] if r["marker_at"]]
    marks["r101_scratch_warmup"] = [w["marker_at"]] if w.get("marker_at") else []
    kmiss = {}
    for name, rs in tl["series"].items():
        if name == "warmup":
            continue
        kmiss[name] = sum(1 for r in rs if r.get("marker_observed_at") and r["marker_observed_at"] >= 0.753)
    marks["r101_scratch_over_0753"] = [sum(1 for v in marks["r101_scratch_delay"] if v >= 0.753)]
    kmiss["r101_scratch_delay"] = sum(1 for v in marks["r101_scratch_delay"] if v >= 0.753)
    old_miss = sum(1 for r in out["r101_scratch_old"] if not r["marker_observed"])
    kmiss["r101_scratch_old_marker_miss"] = old_miss
    out["stats"] = {"marker_at_by_series": marks, "trials_at_or_above_0.753": kmiss}
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    print("stats:", json.dumps(out["stats"], indent=1))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
