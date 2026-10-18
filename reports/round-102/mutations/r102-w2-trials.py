#!/usr/bin/env python3
"""r102-w2: timeout_probe timing reproduction under host pollution.

Series A: exact replication of run_battery.py bounded_run (bound 0.75, text=True, bufsize=1).
Series B: timestamped line-arrival reader, ambient host state.
Series C: timestamped reader while 6 own CPU spinners run (controlled load).
Series D: timestamped reader after spinner kill (recovery check).
Census (godot count, zombie count, loadavg) recorded per trial.
"""
import json
import os
import selectors
import subprocess
import sys
import threading
import time
from pathlib import Path

PROJ = "/var/tmp/r102-w2/proj"
GODOT = "/usr/bin/godot"
OUT = Path("/var/tmp/r102-w2/trials.json")

MARKER = "TIMEOUT_PROBE: expected signature"


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
        state = stat.rsplit(")", 1)[1].split()[0]
        if state == "Z":
            zombies += 1
    la = os.getloadavg()
    return {"godot": godot, "zombies": zombies, "load": [round(x, 2) for x in la]}


def old_bound_trial(i):
    # faithful copy of run_battery.py lines 5332-5368 semantics
    command = [GODOT, "--headless", "--path", PROJ, "--script",
               "res://timeout_probe.gd", "--", "--delay-clean"]
    rec = {"series": "A_old_bound", "index": i, "census_before": census(),
           "command": command, "timeout_seconds": 0.75}
    t0 = time.monotonic()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, bufsize=1)
    timed_out = False
    try:
        out, err = proc.communicate(timeout=0.75)
        rec["actual_exit"] = proc.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        rec["process_was_running"] = proc.poll() is None
        if proc.poll() is None:
            proc.kill()
        out2, err2 = proc.communicate(timeout=3)
        rec["cleanup_exit_code"] = proc.returncode
        out = out2 or ""
        err = err2 or ""
    rec["timed_out"] = timed_out
    rec["elapsed_seconds"] = round(time.monotonic() - t0, 3)
    rec["raw_stdout"] = out
    rec["raw_stderr"] = err
    rec["marker_observed"] = MARKER in out
    rec["census_after"] = census()
    return rec


def timestamped_trial(series, i, extra_env=None, bound=8.0):
    command = [GODOT, "--headless", "--path", PROJ, "--script",
               "res://timeout_probe.gd", "--", "--delay-clean"]
    env = None
    if extra_env:
        env = dict(os.environ)
        env.update(extra_env)
    rec = {"series": series, "index": i, "census_before": census(),
           "command": command, "bound": bound}
    t0 = time.monotonic()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, bufsize=1, env=env)
    lines = []
    stderr_chunks = []

    def drain_err():
        for line in proc.stderr:
            stderr_chunks.append(line)
    terr = threading.Thread(target=drain_err, daemon=True)
    terr.start()

    sel = selectors.DefaultSelector()
    sel.register(proc.stdout, selectors.EVENT_READ)
    deadline = t0 + bound
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            # final drain once
            rest = proc.stdout.read()
            if rest:
                lines.append((round(time.monotonic() - t0, 4), rest))
            break
        events = sel.select(min(0.1, max(0.0, deadline - time.monotonic())))
        for key, _ in events:
            line = key.fileobj.readline()
            if line:
                lines.append((round(time.monotonic() - t0, 4), line))
    sel.close()
    if proc.poll() is None:
        proc.kill()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        rec["cleanup_wait_timeout"] = True
    terr.join(timeout=2)
    rec["exit"] = proc.returncode
    rec["elapsed_seconds"] = round(time.monotonic() - t0, 4)
    rec["lines"] = lines
    rec["stderr"] = "".join(stderr_chunks)
    joined = "".join(x[1] for x in lines)
    rec["marker_observed_at"] = next((t for t, l in lines if MARKER in l), None)
    rec["banner_at"] = next((t for t, l in lines if "Godot Engine v" in l), None)
    rec["marker_in_final"] = MARKER in joined
    rec["census_after"] = census()
    return rec


def main():
    trials = {"godot_version": subprocess.run([GODOT, "--version"], capture_output=True, text=True).stdout.strip(),
              "wc": int(sys.argv[1]) if len(sys.argv) > 1 else 6,
              "series": {}}
    # warmup
    w = timestamped_trial("warmup", 0)
    trials["series"]["warmup"] = [w]
    n = trials["wc"]

    trials["series"]["A_old_bound"] = [old_bound_trial(i) for i in range(n)]
    trials["series"]["B_ambient"] = [timestamped_trial("B_ambient", i) for i in range(n)]

    spinners = [subprocess.Popen([sys.executable, "-c", "while True: pass"]) for _ in range(6)]
    try:
        trials["series"]["C_loaded"] = [timestamped_trial("C_loaded", i) for i in range(n)]
    finally:
        for s in spinners:
            s.kill()
        for s in spinners:
            s.wait()
    trials["series"]["D_recovery"] = [timestamped_trial("D_recovery", i) for i in range(max(3, n // 2))]

    OUT.write_text(json.dumps(trials, indent=1) + "\n")
    for name, rs in trials["series"].items():
        for r in rs:
            if "lines" in r:
                print(f"{name}[{r['index']}] marker_at={r['marker_observed_at']} banner_at={r['banner_at']} "
                      f"exit={r['exit']} elapsed={r['elapsed_seconds']} census_before={r['census_before']}")
            else:
                print(f"{name}[{r['index']}] timed_out={r['timed_out']} marker={r['marker_observed']} "
                      f"stdout={r['raw_stdout']!r} elapsed={r['elapsed_seconds']} census_before={r['census_before']}")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
