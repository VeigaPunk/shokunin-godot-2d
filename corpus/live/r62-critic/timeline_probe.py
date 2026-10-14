#!/usr/bin/env python3
"""r62-critic timeline probe (scratch-only).

Faithfully replicates the run_process timeout path (Popen + communicate
(timeout); on TimeoutExpired: kill() direct child + wait() + raise — the
POSIX CPython 3.14 subprocess.run shape) while a monitor thread polls
proc.poll() and scans /proc for descendants. This yields timestamped proof
of WHEN the direct child died vs WHEN the harness call returned — the
quantity a verdict record can never show.

Arms: hold_silent (descendant holds pipes 5s, child exits ~0.4s),
early_release (holds 1.2s), detach (descendant alive, no pipes),
hang (child hangs 30s, detached descendant).

Writes timeline-verdicts.json. No tracked files touched.
"""
import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE / "proj"
GODOT = "godot"
MARKER = "PIPE_CRITIC: expected signature"
BOUND = 3.0


def children_of(ppid):
    found = []
    for ent in os.listdir("/proc"):
        if not ent.isdigit():
            continue
        try:
            text = Path(f"/proc/{ent}/stat").read_text()
            rest = text[text.rindex(")") + 2:].split()
            if int(rest[1]) == ppid:
                found.append(int(ent))
        except (OSError, ValueError, IndexError):
            continue
    return found


def pid_alive(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def run_timeline_arm(name, extra_args):
    command = [GODOT, "--headless", "--path", str(PROJ), "--script",
               "res://pipe_critic_probe.gd", "--", *extra_args,
               f"--out-dir={HERE}"]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, bufsize=1)
    t0 = time.monotonic()
    timeline = {
        "case": name, "command": command, "bound_seconds": BOUND,
        "godot_pid": proc.pid,
        "child_reaped_at_s": None, "child_returncode": None,
        "communicate_ended_at_s": None, "timed_out": None,
        "descendant_pids_seen": [], "descendant_last_alive_s": {},
        "descendant_ppid_after_orphan": {},
        "kill_sent_at_s": None, "wait_returned_at_s": None,
        "marker_in_partial_output": None, "partial_output_lines": None,
    }
    comm_result = {}

    def comm_worker():
        try:
            out, err = proc.communicate(timeout=BOUND)
            comm_result["out"], comm_result["err"] = out, err
            comm_result["timeout"] = False
        except subprocess.TimeoutExpired as exc:
            comm_result["timeout"] = True
            comm_result["exc"] = exc
        comm_result["ended_at"] = time.monotonic() - t0

    worker = threading.Thread(target=comm_worker, daemon=True)
    worker.start()

    seen = set()
    # Monitor loop: direct-child reap time + descendant discovery/liveness.
    while worker.is_alive():
        rc = proc.poll()
        if timeline["child_reaped_at_s"] is None and rc is not None:
            timeline["child_reaped_at_s"] = round(time.monotonic() - t0, 3)
            timeline["child_returncode"] = rc
        for p in children_of(proc.pid):
            if p not in seen:
                seen.add(p)
        for p in list(seen):
            if pid_alive(p):
                timeline["descendant_last_alive_s"][str(p)] = round(
                    time.monotonic() - t0, 3)
        time.sleep(0.02)
    worker.join(timeout=2)
    timeline["communicate_ended_at_s"] = round(comm_result.get("ended_at", -1), 3)
    timeline["timed_out"] = comm_result.get("timeout")
    timeline["descendant_pids_seen"] = sorted(seen)
    # post-return: orphan ppid + last-seen liveness (one more sample)
    for p in sorted(seen):
        alive = pid_alive(p)
        if alive:
            timeline["descendant_last_alive_s"][str(p)] = round(time.monotonic() - t0, 3)
            try:
                text = Path(f"/proc/{p}/stat").read_text()
                rest = text[text.rindex(")") + 2:].split()
                timeline["descendant_ppid_after_orphan"][str(p)] = int(rest[1])
            except (OSError, ValueError, IndexError):
                pass
        else:
            timeline["descendant_last_alive_s"].setdefault(str(p), None)

    # Replicate subprocess.run TimeoutExpired handling (POSIX): kill + wait.
    if comm_result.get("timeout"):
        timeline["kill_sent_at_s"] = round(time.monotonic() - t0, 3)
        if proc.poll() is None:
            proc.kill()
        proc.wait()
        timeline["wait_returned_at_s"] = round(time.monotonic() - t0, 3)
        exc = comm_result["exc"]
        out = exc.stdout or ""
        if isinstance(out, bytes):
            out = out.decode(errors="replace")
        timeline["marker_in_partial_output"] = MARKER in out
        timeline["partial_output_lines"] = len(out.splitlines())
        timeline["post_kill_descendant_alive"] = [pid_alive(p) for p in sorted(seen)]
    else:
        timeline["marker_in_partial_output"] = MARKER in (comm_result.get("out") or "")
        timeline["partial_output_lines"] = len((comm_result.get("out") or "").splitlines())
        timeline["final_returncode"] = proc.returncode
    # close pipe fds like the `with Popen` context in subprocess.run
    if proc.stdout:
        proc.stdout.close()
    if proc.stderr:
        proc.stderr.close()
    print(json.dumps(timeline, indent=None), flush=True)
    return timeline


def main():
    env = {
        "python": sys.version.split()[0],
        "platform": subprocess.run(["uname", "-srvm"], capture_output=True,
                                   text=True).stdout.strip(),
        "godot_version": subprocess.run([GODOT, "--version"], capture_output=True,
                                        text=True).stdout.strip(),
        "started_utc": datetime.now(timezone.utc).isoformat(),
    }
    arms = [
        ("tl_hold_silent", ["--spawn-hold=5"]),
        ("tl_early_release", ["--spawn-hold=1.2"]),
        ("tl_detach", ["--spawn-detach=6"]),
        ("tl_hang", ["--hang=30", "--spawn-detach=6"]),
    ]
    results = [run_timeline_arm(name, args) for name, args in arms]
    payload = {"mode": "popen_communicate_timeline", "environment": env,
               "mechanism_replicated": "subprocess.run POSIX timeout: communicate(timeout) then kill()+wait() direct child only",
               "results": results}
    (HERE / "timeline-verdicts.json").write_text(json.dumps(payload, indent=2) + "\n")
    print("done", flush=True)


if __name__ == "__main__":
    main()
