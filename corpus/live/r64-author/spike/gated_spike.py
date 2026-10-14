#!/usr/bin/env python3
"""r64 spike: while-live signature gate timing over descendant_pipe_probe arms."""
import os, re, select, signal, subprocess, sys, time

GODOT = "/usr/bin/godot"
SCRATCH = os.path.expanduser("~/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r64-author/spike/proj")
MARKER = b"DESCENDANT_PIPE_PROBE: expected signature"
POLL_TICK = 0.005


def pid_alive(pid):
    if pid is None or pid <= 0:
        return None
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def gated_run(case, flags, bound):
    rec = {"case": case, "flags": flags, "bound_seconds": bound,
           "timed_out": False, "actual_exit": None, "error": None,
           "marker_observed": False, "marker_observed_at": None,
           "child_alive_at_marker_observation": None,
           "child_alive_after_marker_read": None,
           "dead_observed_at": None, "elapsed_seconds": None,
           "withheld_banner": False, "write_ppid": None,
           "godot_pid": None, "descendant_pid": None}
    cmd = [GODOT, "--headless", "--path", SCRATCH, "--script",
           "res://descendant_pipe_probe.gd", "--"] + flags
    proc = None
    started = time.monotonic()
    pending = b""
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        deadline = started + bound
        pipes = [proc.stdout, proc.stderr]
        while pipes:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                rec["timed_out"] = True
                break
            readable, _, _ = select.select(pipes, [], [],
                                           min(POLL_TICK, max(0.0, remaining)))
            now = time.monotonic()
            if rec["dead_observed_at"] is None and proc.poll() is not None:
                rec["dead_observed_at"] = round(now - started, 6)
            for stream in readable:
                alive_before = proc.poll() is None
                try:
                    chunk = os.read(stream.fileno(), 65536)
                except OSError:
                    chunk = b""
                if not chunk:
                    pipes.remove(stream)
                    continue
                pending += chunk
                alive_after = proc.poll() is None
                if not rec["marker_observed"] and MARKER in pending:
                    rec["marker_observed"] = True
                    rec["marker_observed_at"] = round(now - started, 6)
                    rec["child_alive_at_marker_observation"] = alive_before
                    rec["child_alive_after_marker_read"] = alive_after
        if rec["dead_observed_at"] is None and proc.poll() is not None:
            rec["dead_observed_at"] = round(time.monotonic() - started, 6)
        if rec["timed_out"]:
            rec["error"] = f"TIMEOUT after {bound} seconds"
            for stream in (proc.stdout, proc.stderr):
                try:
                    stream.close()
                except OSError:
                    pass
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=3)
        else:
            proc.wait(timeout=3)
        rec["actual_exit"] = proc.returncode
    except (OSError, ValueError) as exc:
        rec["error"] = f"launch/read error: {exc}"
        if proc is not None and proc.poll() is None:
            proc.kill()
            proc.wait(timeout=3)
    rec["elapsed_seconds"] = round(time.monotonic() - started, 3)
    text = pending.decode(errors="replace")
    rec["withheld_banner"] = "DESCENDANT_PIPE_FORGE child_signature=withheld" in text
    m = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", text)
    rec["godot_pid"] = int(m.group(1)) if m else None
    m = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", text)
    rec["descendant_pid"] = int(m.group(1)) if m else None
    m = re.search(r"DESCENDANT_PIPE_FORGE write_ppid=(\d+)", text)
    rec["write_ppid"] = int(m.group(1)) if m else None
    rec["descendant_alive_at_return"] = pid_alive(rec["descendant_pid"])
    rec["gated_signature_accepted"] = bool(
        rec["marker_observed"] and rec["child_alive_at_marker_observation"])
    # hygiene: reap orphan descendant
    if pid_alive(rec["descendant_pid"]):
        try:
            os.kill(rec["descendant_pid"], signal.SIGKILL)
        except OSError:
            pass
    return rec


ARMS = [("genuine_default", [], 3.0, 3),
        ("genuine_detach", ["--spawn-detach"], 3.0, 3),
        ("forge_release", ["--spawn-forge-release"], 3.0, 3),
        ("forge_hold", ["--spawn-forge-hold"], 3.0, 1)]

for name, flags, bound, reps in ARMS:
    for i in range(reps):
        r = gated_run(f"{name}#{i}", flags, bound)
        lead = (None if r["dead_observed_at"] is None or r["marker_observed_at"] is None
                else round(r["dead_observed_at"] - r["marker_observed_at"], 6))
        print(f"{r['case']:>20} exit={r['actual_exit']} err={r['error']!r} "
              f"marker={r['marker_observed']}@{r['marker_observed_at']} "
              f"dead@{r['dead_observed_at']} lead={lead} "
              f"alive_at_obs={r['child_alive_at_marker_observation']} "
              f"alive_after={r['child_alive_after_marker_read']} "
              f"gate={'ACCEPT' if r['gated_signature_accepted'] else 'REJECT'} "
              f"elapsed={r['elapsed_seconds']}", flush=True)
