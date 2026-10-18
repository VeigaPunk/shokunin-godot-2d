#!/usr/bin/env python3
"""Instrumented replication of run_battery.py probe_timeout bounded_run (:5322-5369).

Repo is read-only for this tool. Scratch + outputs live under /var/tmp/r102-D4.
Usage:
  bounded_probe.py exact <case> <bound> [-- extra args...]
  bounded_probe.py observe <bound> [-- extra args...]      # timestamped incremental read
  bounded_probe.py census <bound> <kill_after> [-- extra args...]
  bounded_probe.py strace <bound> <tracefile> [-- extra args...]
  bounded_probe.py desccensus <bound>                      # descendant_pipe_probe --spawn-hold
"""
import json
import os
import selectors
import signal
import subprocess
import sys
import time

GODOT = "/usr/bin/godot"
SCRATCH = "/var/tmp/r102-D4/scratch"
TIMEOUT_SCRIPT = "res://timeout_probe.gd"
DESC_SCRIPT = "res://descendant_pipe_probe.gd"
MARKER = "TIMEOUT_PROBE: expected signature"


def census(pid):
    info = {"pid": pid, "status": {}, "threads": [], "children": []}
    try:
        with open(f"/proc/{pid}/status") as fh:
            for line in fh:
                key, _, val = line.partition(":")
                info["status"][key.strip()] = val.strip()
    except OSError as exc:
        info["status_error"] = str(exc)
    try:
        info["threads"] = sorted(os.listdir(f"/proc/{pid}/task"))
    except OSError as exc:
        info["threads_error"] = str(exc)
    for entry in sorted(os.listdir("/proc")):
        if not entry.isdigit():
            continue
        try:
            with open(f"/proc/{entry}/stat") as fh:
                stat = fh.read()
        except OSError:
            continue
        fields = stat[stat.rfind(")") + 2:].split()
        if len(fields) < 2:
            continue
        state, ppid = fields[0], int(fields[1])
        if ppid != pid:
            continue
        try:
            with open(f"/proc/{entry}/cmdline", "rb") as fh:
                cmdline = fh.read().replace(b"\0", b" ").decode(errors="replace").strip()
        except OSError:
            cmdline = ""
        info["children"].append({"pid": int(entry), "state": state, "cmdline": cmdline})
    try:
        with open(f"/proc/{pid}/wchan") as fh:
            info["status"]["wchan"] = fh.read().strip()
    except OSError:
        pass
    return info


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


def make_command(extra):
    return [GODOT, "--headless", "--path", SCRATCH, "--script", TIMEOUT_SCRIPT, "--"] + extra


def bounded_run(case, command, bound, script=sys.argv[0]):
    """Exact copy of the driver's bounded_run body (instrumentation added, order preserved)."""
    record = {"case": case, "command": command, "expected_exit": 0,
              "timeout_seconds": bound, "cleanup_seconds": 3,
              "actual_exit": None, "error": None, "marker_observed": False,
              "timed_out": False, "process_was_running": False,
              "direct_child_alive_after_cleanup": None, "raw_stdout": "", "raw_stderr": ""}
    process = None
    started_at = time.monotonic()
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, bufsize=1)
        record["pid"] = process.pid
        try:
            out, err = process.communicate(timeout=bound)
            record["raw_stdout"], record["raw_stderr"] = out, err
            record["actual_exit"] = process.returncode
        except subprocess.TimeoutExpired as exc:
            record["timed_out"] = True
            record["timeout_raised_at_s"] = round(time.monotonic() - started_at, 4)
            out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            err = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            record["exc_stdout_repr"] = repr(out)
            record["exc_stdout_type"] = type(exc.stdout).__name__
            record["raw_stdout"], record["raw_stderr"] = out, err
            record["marker_observed"] = MARKER in out
            record["process_was_running"] = process.poll() is None
            record["error"] = f"TIMEOUT after {bound} seconds"
            record["pre_kill_census"] = census(process.pid)
            if process.poll() is None:
                process.kill()
            record["kill_sent_at_s"] = round(time.monotonic() - started_at, 4)
            more_out, more_err = process.communicate(timeout=3)
            record["second_communicate_repr"] = repr(more_out)
            record["second_communicate_type"] = type(more_out).__name__
            record["second_communicate_equals_first"] = (more_out == out)
            record["raw_stdout"], record["raw_stderr"] = more_out or "", more_err or ""
            record["cleanup_exit_code"] = process.returncode
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        record["error"] = f"launch/read/cleanup error: {exc}"
        if process is not None and process.poll() is None:
            process.kill()
            try:
                process.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                record["error"] += "; direct-child cleanup timed out"
    finally:
        if process is not None:
            record["actual_exit"] = None if record["timed_out"] else process.poll()
            record["direct_child_alive_after_cleanup"] = process.poll() is None
            record["post_cleanup_pid_alive"] = pid_alive(process.pid)
    record["elapsed_seconds"] = round(time.monotonic() - started_at, 3)
    record["marker_observed"] = MARKER in record["raw_stdout"]
    record["inner_classification"] = classify(record)
    return record


def classify(record):
    """Driver classify_process semantics for expected_exit=0 (see run_battery.py)."""
    if record["actual_exit"] == 0 and record["error"] is None and MARKER in record["raw_stdout"]:
        return True
    return False


def predicates(results):
    old, new, hold = results
    return {
        "old_rejects": bool(old["timed_out"] and old["marker_observed"]
                            and old["inner_classification"] is False
                            and old["direct_child_alive_after_cleanup"] is False),
        "new_accepts": bool((not new["timed_out"]) and new["actual_exit"] == 0
                            and new["marker_observed"] and new["inner_classification"] is True),
        "hold_rejects": bool(hold["timed_out"] and hold["marker_observed"]
                             and hold["inner_classification"] is False
                             and hold["direct_child_alive_after_cleanup"] is False),
    }


def cmd_exact(argv):
    case, bound = argv[0], float(argv[1])
    extra = argv[argv.index("--") + 1:] if "--" in argv else []
    rec = bounded_run(case, make_command(extra), bound)
    print(json.dumps(rec, indent=1))
    return rec


def cmd_observe(argv):
    """Incremental line-timestamped read (no communicate): when do lines arrive?"""
    bound = float(argv[0])
    extra = argv[argv.index("--") + 1:] if "--" in argv else []
    command = make_command(extra)
    started = time.monotonic()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    sel = selectors.DefaultSelector()
    sel.register(proc.stdout, selectors.EVENT_READ)
    sel.register(proc.stderr, selectors.EVENT_READ)
    lines = []
    deadline = started + bound
    while time.monotonic() < deadline and sel.get_map():
        for key, _ in sel.select(max(0.0, min(0.05, deadline - time.monotonic()))):
            chunk = key.fileobj.readline()
            t = round(time.monotonic() - started, 4)
            if chunk:
                stream = "stdout" if key.fileobj is proc.stdout else "stderr"
                lines.append({"t": t, "stream": stream, "line": chunk.rstrip("\n")})
            else:
                sel.unregister(key.fileobj)
    exited = proc.poll()
    if exited is None:
        proc.kill()
    out, err = proc.communicate(timeout=3)
    ended = round(time.monotonic() - started, 4)
    rec = {"case": "observe", "command": command, "bound": bound, "lines": lines,
           "lines_after_incremental_drain": {"stdout": out, "stderr": err},
           "exit": proc.returncode, "exited_before_bound": exited is not None,
           "end_s": ended, "marker_t_incremental": next((l["t"] for l in lines if MARKER in l["line"]), None),
           "header_t_incremental": next((l["t"] for l in lines if l["line"].startswith("Godot Engine v")), None)}
    print(json.dumps(rec, indent=1))
    return rec


def cmd_census(argv):
    """hold arm + /proc census while it runs; SIGKILL at kill_after; post-cleanup census."""
    bound = float(argv[0])
    kill_after = float(argv[1])
    extra = argv[argv.index("--") + 1:] if "--" in argv else ["--hold-open"]
    command = make_command(extra)
    started = time.monotonic()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    samples = []
    while time.monotonic() - started < kill_after:
        time.sleep(min(0.5, max(0.01, kill_after - (time.monotonic() - started))))
        c = census(proc.pid)
        c["t"] = round(time.monotonic() - started, 3)
        c["status"] = {k: v for k, v in c["status"].items()
                       if k in ("State", "Threads", "VmRSS", "voluntary_ctxt_switches", "nonvoluntary_ctxt_switches", "wchan")}
        c["threads"] = len(c["threads"])
        samples.append(c)
    alive_at_kill = proc.poll() is None
    if alive_at_kill:
        proc.kill()
    out, err = proc.communicate(timeout=3)
    rec = {"case": "census", "command": command, "samples": samples, "alive_at_kill": alive_at_kill,
           "exit": proc.returncode, "raw_stdout": out, "raw_stderr": err,
           "kill_at_s": kill_after, "pid_alive_post": pid_alive(proc.pid),
           "elapsed_s": round(time.monotonic() - started, 3)}
    print(json.dumps(rec, indent=1))
    return rec


def cmd_strace(argv):
    bound = float(argv[0])
    tracefile = argv[1]
    extra = argv[argv.index("--") + 1:] if "--" in argv else []
    inner = make_command(extra)
    command = ["strace", "-f", "-tt", "-T", "-o", tracefile,
               "-e", "trace=process,write,writev,nanosleep,clock_nanosleep"] + inner
    started = time.monotonic()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    godot_pid = None
    while time.monotonic() - started < bound and godot_pid is None:
        time.sleep(0.02)
        for child in census(proc.pid)["children"]:
            if "godot" in child["cmdline"]:
                godot_pid = child["pid"]
    t_found = round(time.monotonic() - started, 3)
    while time.monotonic() - started < bound:
        time.sleep(0.01)
    killed = False
    if godot_pid and pid_alive(godot_pid):
        os.kill(godot_pid, signal.SIGKILL)
        killed = True
    killed_at = round(time.monotonic() - started, 3)
    try:
        out, err = proc.communicate(timeout=6)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate(timeout=3)
    rec = {"case": "strace", "command": command, "godot_pid": godot_pid, "t_found_s": t_found,
           "strace_child_was_killed": killed, "killed_at_s": killed_at,
           "strace_exit": proc.returncode, "raw_stdout": out, "raw_stderr": err,
           "elapsed_s": round(time.monotonic() - started, 3), "tracefile": tracefile}
    print(json.dumps(rec, indent=1))
    return rec


def cmd_desccensus(argv):
    bound = float(argv[0])
    command = [GODOT, "--headless", "--path", SCRATCH, "--script", DESC_SCRIPT, "--", "--spawn-hold"]
    started = time.monotonic()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    godot_children = []
    try:
        out, err = proc.communicate(timeout=bound)
        timed_out = False
        text = (out or "") + (err or "")
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        text = out + err
        godot_children = census(proc.pid)["children"]
        child_exit_at_timeout = proc.poll()
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
    desc_pid = None
    for child in godot_children:
        if "sh" in child["cmdline"] or "sleep" in child["cmdline"]:
            desc_pid = child["pid"]
    rec = {"case": "descendant_pipe_hold_arm_replication", "command": command, "bound": bound,
           "timed_out": timed_out, "child_exit_at_timeout": (proc.returncode if timed_out else None),
           "godot_children_at_timeout": godot_children, "descendant_pid": desc_pid,
           "descendant_alive_at_return": pid_alive(desc_pid),
           "marker_observed": "DESCENDANT_PIPE_PROBE: expected signature" in text,
           "post_exit_write_captured": "DESCENDANT_PIPE_AFTER_EXIT_WRITE" in text,
           "godot_alive_at_return": pid_alive(proc.pid),
           "text": text, "elapsed_s": round(time.monotonic() - started, 3)}
    if pid_alive(desc_pid):
        try:
            os.kill(desc_pid, signal.SIGKILL)
        except OSError:
            pass
    rec["descendant_reaped"] = pid_alive(desc_pid) is False
    print(json.dumps(rec, indent=1))
    return rec


def main():
    mode = sys.argv[1]
    argv = sys.argv[2:]
    if mode == "exact":
        cmd_exact(argv)
    elif mode == "observe":
        cmd_observe(argv)
    elif mode == "census":
        cmd_census(argv)
    elif mode == "strace":
        cmd_strace(argv)
    elif mode == "desccensus":
        cmd_desccensus(argv)
    else:
        raise SystemExit(f"unknown mode {mode}")


if __name__ == "__main__":
    main()
