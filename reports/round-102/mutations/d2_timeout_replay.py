#!/usr/bin/env python3
"""r102-D2 replay driver — timeout probe arms, pollution + SIGKILL-zombie twist.

Faithfully replicates corpus/fixtures/run_battery.py's bounded_run control flow
(the --probe-timeout block, lines 5314-5402, read-only) with:
  * added byte-accounting fields (pre-timeout exc.stdout vs post-kill drain),
  * a line-timestamped timing probe (boot banner / marker arrival times),
  * counterfactual shadow arms (--delay-clean under bounds 0.75/0.9/1.1/1.5),
  * modes: clean (baseline replication), polluted (20 rapid godot spawns
    interleaved, mild load), sigkill (three mid-run godot instances SIGKILLed
    and left unreaped as live zombies while arms run).

This script NEVER executes run_battery.py. It launches godot directly against a
scratch project under /var/tmp/r102-D2/.

Usage:
  python3 d2_timeout_replay.py --mode clean|polluted|sigkill --reps 2 \
      --proj /var/tmp/r102-D2/proj --out /var/tmp/r102-D2/out
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

MARKER = "TIMEOUT_PROBE: expected signature"
BOOT_MARKER = "BOOT_MARKER: d2"


# --- verbatim copy of run_battery.py classify_process (lines 1775-1792) ----
def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
    lines = output.splitlines()

    def allowed_error(line, allowed):
        stripped = line.strip()
        if stripped == allowed:
            return True
        if allowed.endswith(","):
            return stripped.startswith(allowed) and stripped.count("ERROR:") == 1
        if allowed == "ERROR: chain incomplete":
            return (stripped.startswith("ERROR: chain incomplete collections=")
                    and "scene=SceneB:<Node#" in stripped and "old_alive=false" in stripped
                    and stripped.count("ERROR:") == 1)
        return False

    unrelated_errors = [line for line in lines if "ERROR:" in line
                        and not any(allowed_error(line, allowed) for allowed in allowed_errors)]
    return (code == expected_exit and error is None and signature in output
            and not unrelated_errors and "SCRIPT ERROR:" not in output and "Parse Error:" not in output)
# --------------------------------------------------------------------------


def bounded_run(godot, proj, case, extra_args, bound, cleanup_seconds=3,
                expected_exit=0, signature=MARKER):
    """Copy of run_battery.py bounded_run with added diagnostics.

    Fixture-faithful semantics: on TimeoutExpired, raw_stdout is REPLACED by the
    post-kill communicate() drain; marker_observed is recomputed from that at the
    end. Diagnostics record what each stage saw."""
    command = [godot, "--headless", "--path", str(proj), "--script",
               "res://timeout_probe.gd", "--"] + extra_args
    record = {"case": case, "command": command, "expected_exit": expected_exit,
              "timeout_seconds": bound, "cleanup_seconds": cleanup_seconds,
              "actual_exit": None, "error": None, "marker_observed": False,
              "timed_out": False, "process_was_running": False,
              "direct_child_alive_after_cleanup": None, "raw_stdout": "", "raw_stderr": ""}
    process = None
    started_at = time.monotonic()
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, bufsize=1)
        try:
            out, err = process.communicate(timeout=bound)
            record["raw_stdout"], record["raw_stderr"] = out, err
            record["actual_exit"] = process.returncode
        except subprocess.TimeoutExpired as exc:
            record["timed_out"] = True
            out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            err = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            # --- D2 diagnostics ---
            record["pre_timeout_stdout"] = out
            record["post_drain_stdout"] = None
            # ----------------------
            record["raw_stdout"], record["raw_stderr"] = out, err
            record["marker_observed"] = MARKER in out
            record["process_was_running"] = process.poll() is None
            record["error"] = f"TIMEOUT after {bound} seconds"
            if process.poll() is None:
                process.kill()
            more_out, more_err = process.communicate(timeout=cleanup_seconds)
            record["raw_stdout"], record["raw_stderr"] = more_out or "", more_err or ""
            record["post_drain_stdout"] = record["raw_stdout"]  # D2 diagnostic
            record["cleanup_exit_code"] = process.returncode
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        record["error"] = f"launch/read/cleanup error: {exc}"
        if process is not None and process.poll() is None:
            process.kill()
            try:
                process.communicate(timeout=cleanup_seconds)
            except subprocess.TimeoutExpired:
                record["error"] += "; direct-child cleanup timed out"
    finally:
        if process is not None:
            record["actual_exit"] = None if record["timed_out"] else process.poll()
            record["direct_child_alive_after_cleanup"] = process.poll() is None
    record["elapsed_seconds"] = round(time.monotonic() - started_at, 3)
    record["marker_observed"] = MARKER in record["raw_stdout"]
    record["inner_classification"] = classify_process(
        record["actual_exit"], record["error"], record["raw_stdout"] + record["raw_stderr"],
        expected_exit, MARKER)
    return record


def timed_run(godot, proj, script, extra_args=(), timeout_s=10):
    """Line-timestamped run: time to banner and to script marker (arrival)."""
    command = [godot, "--headless", "--path", str(proj), "--script",
               f"res://{script}", "--"] + list(extra_args)
    t0 = time.monotonic()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, bufsize=1)
    lines = []
    lock = threading.Lock()

    def reader(stream):
        for line in stream:
            with lock:
                lines.append((round(time.monotonic() - t0, 3), line.rstrip("\n")))

    t_out = threading.Thread(target=reader, args=(proc.stdout,), daemon=True)
    t_err = threading.Thread(target=reader, args=(proc.stderr,), daemon=True)
    t_out.start(); t_err.start()
    try:
        proc.wait(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        proc.kill(); proc.wait()
    t_out.join(timeout=2); t_err.join(timeout=2)
    elapsed = round(time.monotonic() - t0, 3)
    first_t = lines[0][0] if lines else None
    boot_t = next((t for t, ln in lines if BOOT_MARKER in ln), None)
    return {"command": command, "exit": proc.returncode, "elapsed_seconds": elapsed,
            "first_byte_t": first_t, "boot_marker_t": boot_t,
            "lines": [{"t": t, "line": ln} for t, ln in lines[:6]]}


def arm_sequence(godot, proj, tag, shadow=False):
    """Faithful three-arm sequence + run_battery.py pass expressions (5314-5402)."""
    expected_exit = 0
    records = {
        "slow_clean_old_bound": bounded_run(godot, proj, "slow_clean_old_bound", ["--delay-clean"], 0.75),
        "slow_clean_new_bound": bounded_run(godot, proj, "slow_clean_new_bound", ["--delay-clean"], 3.0),
        "hold_open_new_bound": bounded_run(godot, proj, "hold_open_new_bound", ["--hold-open"], 3.0),
    }
    o = records["slow_clean_old_bound"]; n = records["slow_clean_new_bound"]; h = records["hold_open_new_bound"]
    old_rejects = (o["timed_out"] and o["marker_observed"] and o["inner_classification"] is False
                   and o["direct_child_alive_after_cleanup"] is False)
    new_accepts = (not n["timed_out"] and n["actual_exit"] == expected_exit
                   and n["marker_observed"] and n["inner_classification"] is True)
    hold_rejects = (h["timed_out"] and h["marker_observed"] and h["inner_classification"] is False
                    and h["direct_child_alive_after_cleanup"] is False)
    meta_pass = old_rejects and new_accepts and hold_rejects
    shadow_records = {}
    if shadow:
        for bound in (0.75, 0.9, 1.1, 1.5):
            shadow_records[f"delay_clean_bound_{bound}"] = bounded_run(
                godot, proj, f"shadow_delay_clean_{bound}", ["--delay-clean"], bound)
    return {"tag": tag, "records": records,
            "conditions": {"old_rejects": old_rejects, "new_accepts": new_accepts,
                           "hold_rejects": hold_rejects, "meta_pass": meta_pass},
            "verdict": "PASS" if meta_pass else "FAIL",
            "shadow": shadow_records}


def godot_processes():
    out = subprocess.run(["ps", "-eo", "pid,ppid,stat,etime,cmd"], capture_output=True, text=True).stdout
    return [ln for ln in out.splitlines() if "godot" in ln and "grep" not in ln]


def mode_clean(args, result):
    for i in range(args.reps):
        result["sequences"].append(arm_sequence(args.godot, args.proj, f"clean_seq_{i+1}", shadow=True))
        result["timing"].append(timed_run(args.godot, args.proj, "boot_marker.gd"))


def mode_polluted(args, result):
    """20 rapid godot spawns interleaved with arms (mild load)."""
    spawns = []
    barrier = threading.Event()

    def polluter():
        for i in range(20):
            if i:
                time.sleep(0.25)
            t = time.monotonic()
            p = subprocess.Popen([args.godot, "--headless", "--path", str(args.proj),
                                  "--script", "res://boot_marker.gd"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            spawns.append({"i": i, "pid": p.pid, "t_rel": round(t - barrier_t0[0], 3), "proc": p})

    barrier_t0 = [time.monotonic()]
    th = threading.Thread(target=polluter)
    th.start()
    for i in range(args.reps):
        result["sequences"].append(arm_sequence(args.godot, args.proj, f"polluted_seq_{i+1}", shadow=True))
    for i in range(2):
        result["timing"].append(timed_run(args.godot, args.proj, "boot_marker.gd"))
    th.join()
    for s in spawns:
        try:
            s["proc"].wait(timeout=5)
            s["exit"] = s["proc"].returncode
        except subprocess.TimeoutExpired:
            s["exit"] = None
        s["dur"] = round(time.monotonic() - barrier_t0[0] - s["t_rel"], 3)
    result["polluter"] = {"count": len(spawns),
                          "spawns": [{"i": s["i"], "t_rel": s["t_rel"], "exit": s.get("exit")}
                                     for s in spawns]}


def mode_sigkill(args, result):
    """SIGKILL three mid-run godot instances, leave them unreaped (zombies)."""
    t0 = time.monotonic()
    victims = []
    for i in range(3):
        p = subprocess.Popen([args.godot, "--headless", "--path", str(args.proj),
                              "--script", "res://timeout_probe.gd", "--", "--hold-open"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        victims.append(p)
    time.sleep(1.0)  # mid-run: engine past boot, probe holding open
    for p in victims:
        try:
            p.kill()  # SIGKILL, no wait() -> unreaped
        except OSError:
            pass
    time.sleep(0.5)
    states = []
    for p in victims:
        stat_path = Path(f"/proc/{p.pid}/stat")
        state = ppid = None
        if stat_path.exists():
            fields = stat_path.read_text().split()
            state, ppid = fields[2], fields[3]
        states.append({"pid": p.pid, "proc_stat_state": state, "proc_stat_ppid": ppid,
                       "driver_pid": os.getpid(), "driver_ppid_match": ppid == str(os.getpid())})
    result["zombies"] = states
    result["ps_during"] = godot_processes()
    for i in range(args.reps):
        result["sequences"].append(arm_sequence(args.godot, args.proj, f"sigkill_seq_{i+1}", shadow=True))
    result["timing"].append(timed_run(args.godot, args.proj, "boot_marker.gd"))
    for p in victims:
        try:
            p.wait(timeout=2)
        except subprocess.TimeoutExpired:
            pass
    result["reaped"] = [{"pid": p.pid, "returncode": p.returncode} for p in victims]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["clean", "polluted", "sigkill"])
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--proj", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--godot", default="godot")
    args = ap.parse_args()

    result = {"mode": args.mode, "reps": args.reps, "proj": str(args.proj),
              "godot": args.godot, "python": sys.version.split()[0],
              "uptime_pre": subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip(),
              "ps_pre": godot_processes(),
              "sequences": [], "timing": [], "warmup": None}
    result["warmup"] = timed_run(args.godot, args.proj, "boot_marker.gd")
    if args.mode == "clean":
        mode_clean(args, result)
    elif args.mode == "polluted":
        mode_polluted(args, result)
    else:
        mode_sigkill(args, result)
    result["ps_post"] = godot_processes()
    result["uptime_post"] = subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip()
    out_path = Path(args.out) / f"{args.mode}.json"
    out_path.write_text(json.dumps(result, indent=2) + "\n")
    for seq in result["sequences"]:
        print(f"{seq['tag']}: verdict={seq['verdict']} conditions={seq['conditions']}")
        for k, r in seq["records"].items():
            print(f"  {k}: timed_out={r['timed_out']} marker={r['marker_observed']} "
                  f"exit={r['actual_exit']} elapsed={r['elapsed_seconds']}")
        for k, r in seq["shadow"].items():
            print(f"  [shadow] {k}: timed_out={r['timed_out']} marker={r['marker_observed']} "
                  f"elapsed={r['elapsed_seconds']}")
    for t in result["timing"]:
        print(f"timing: banner@{t['first_byte_t']}s boot_marker@{t['boot_marker_t']}s exit={t['exit']} elapsed={t['elapsed_seconds']}")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
