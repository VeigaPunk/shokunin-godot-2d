#!/usr/bin/env python3
"""r68 critic — kernel-level write() timing of the midlineforge window.

strace -f -ttt on the probe captures EVERY write() syscall with µs wall
timestamps and the writing pid. The godot child's stdout writes (banner,
godot_pid, spawned_pid, printraw HEAD, print TAIL) and the descendant's
inherited-fd writes (ERROR, write_ppid) are all visible on the pipe.

Measures:
  gap_on_pipe   = ts(T_tail_write) - ts(T_head_write)   (true window width)
  eff_offset    = ts(T_E_write)    - ts(T_head_write)   (where E landed in gap)
  exec_overhead = ts(T_E_write|offset=0) - ts(T_head_write) (startup shift)
  spawn_to_head = ts(T_head_write) - ts(clone of descendant) (child-side lead)

This is the evidence that decides whether a nominal-offset ladder measures a
temporal bound or an affine-shifted image of one.
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE / "proj"
GODOT = "godot"

HEAD = "DESCENDANT_PIPE_PROBE: expected "
ERR = "ERROR: DESCENDANT_PIPE_MIDLINE forged splice"
PPID = "DESCENDANT_PIPE_MIDLINE write_ppid="
TAILW = "signature"
GODOT_PID_LINE = "DESCENDANT_PIPE godot_pid="
SPAWNED_LINE = "DESCENDANT_PIPE spawned_pid="

# strace -ttt line: "<epoch.us> <syscall>(...)" optionally prefixed by pid
# with -f: lines look like "12345  1759... write(1, \"...\", N) = N"
LINE_RE = re.compile(
    r"^(?P<pid>\d+)\s+(?P<ts>\d+\.\d+)\s+"
    r"(?P<call>\w+)\((?P<args>.*)\)\s+=\s+(?P<ret>\S+)")


def trace_run(offset_ms, gap_ms=200, bound=15):
    env = dict(os.environ)
    xdg = (HERE / "xdg-data").resolve()
    xdg.mkdir(exist_ok=True)
    env["XDG_DATA_HOME"] = str(xdg)
    trace_file = HERE / f"trace_{offset_ms}_{int(time.time()*1000)}.log"
    cmd = ["strace", "-f", "-ttt", "-s", "256",
           "-e", "trace=write,execve,clone,fork,vfork",
           "-o", str(trace_file),
           GODOT, "--headless", "--path", str(PROJ), "--script",
           "res://critic_midline_probe.gd", "--",
           f"--midline-offset-ms={offset_ms}", f"--gap-ms={gap_ms}"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=bound,
                          env=env)
    events = []
    for line in trace_file.read_text(errors="replace").splitlines():
        m = LINE_RE.match(line.strip())
        if not m:
            continue
        events.append({"pid": int(m.group("pid")),
                       "ts": float(m.group("ts")),
                       "call": m.group("call"),
                       "args": m.group("args"),
                       "ret": m.group("ret")})
    trace_file.unlink()

    def find_write(substr):
        # pin fd 1 (the captured stdout pipe); Godot also shadows every print
        # to fd 3 (an inherited/strace artifact), which must not match.
        for e in events:
            if (e["call"] == "write" and e["args"].startswith("1,")
                    and substr in e["args"]):
                return e
        return None

    ev_head = find_write(HEAD[:30])
    # tail write is exactly write(1, "signature\n", 10)
    ev_tail = next((e for e in events
                    if e["call"] == "write"
                    and e["args"].startswith('1, "signature\\n"')), None)
    ev_err = find_write(ERR[:40])
    ev_ppid = find_write(PPID[:40])
    ev_gpid = find_write(GODOT_PID_LINE[:30])
    ev_spawned = find_write(SPAWNED_LINE[:30])
    # find the clone that created the descendant: child sh execve of /usr/bin/sh
    ev_sh = next((e for e in events if e["call"] == "execve"
                  and "/usr/bin/sh" in e["args"]), None)
    out = {"offset_ms": offset_ms, "gap_ms": gap_ms,
           "exit": proc.returncode,
           "stdout_tail": proc.stdout.splitlines()[-4:],
           "events_seen": len(events)}
    def ts(e):
        return e["ts"] if e else None
    out["t_head"] = ts(ev_head)
    out["t_tail"] = ts(ev_tail)
    out["t_err"] = ts(ev_err)
    out["t_ppid"] = ts(ev_ppid)
    out["t_sh_execve"] = ts(ev_sh)
    out["t_spawned_line"] = ts(ev_spawned)
    out["err_pid"] = ev_err["pid"] if ev_err else None
    out["head_pid"] = ev_head["pid"] if ev_head else None
    if out["t_head"] and out["t_tail"]:
        out["gap_on_pipe_ms"] = round((out["t_tail"] - out["t_head"]) * 1000, 3)
    if out["t_head"] and out["t_err"]:
        out["eff_offset_ms"] = round((out["t_err"] - out["t_head"]) * 1000, 3)
    if out["t_err"] and out["t_ppid"]:
        out["err_to_ppid_ms"] = round((out["t_ppid"] - out["t_err"]) * 1000, 3)
    if out["t_sh_execve"] and out["t_err"]:
        out["shexc_to_err_ms"] = round((out["t_err"] - out["t_sh_execve"]) * 1000, 3)
    if out["t_spawned_line"] and out["t_head"]:
        out["spawnedline_to_head_ms"] = round(
            (out["t_head"] - out["t_spawned_line"]) * 1000, 3)
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--offsets", default="0,40,80,160,200,240")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    results = []
    for off in [float(x) for x in args.offsets.split(",")]:
        for rep in range(args.reps):
            r = trace_run(off)
            r["rep"] = rep
            results.append(r)
            print(json.dumps(r), flush=True)
    out = args.out or HERE / "strace-results.json"
    Path(out).write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
