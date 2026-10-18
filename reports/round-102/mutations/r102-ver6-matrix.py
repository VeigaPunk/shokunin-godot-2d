#!/usr/bin/env python3
"""V6 C2 verifier harness — faithful port of run_battery.py timeout-probe driver
(lines 5314-5401) + replication modes for D2's matrix.

Read-only w.r.t. repo. All state under /var/tmp/r102-ver6/.
Modes:
  clean        : 3 arms, driver-identical logic + predicates
  interleaved  : same arms while ~20 rapid godot spawns overlap (2 burst styles)
  postkill     : SIGKILL 6 held-open godot probes (unreaped -> zombies), then arms
  latency      : N live-timestamped bare/delay runs -> launch->marker latency vs 0.75 bound
  bound-diag B : delayed-clean arm under custom bound B (diagnostic only, never a pin)
"""
import argparse, json, os, signal, subprocess, sys, threading, time

GODOT = os.environ.get("VER6_GODOT", "godot")
MARKER = "TIMEOUT_PROBE: expected signature"
TP = "/var/tmp/r102-ver6/tp"
TPN = "/var/tmp/r102-ver6/tp-noise"
OUT = "/var/tmp/r102-ver6/out"
os.makedirs(OUT, exist_ok=True)

def uptime():
    return open("/proc/loadavg").read().split()[:3]

def cmd_for(scratch, extra):
    return [GODOT, "--headless", "--path", scratch, "--script", "res://timeout_probe.gd", "--"] + extra

def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
    """Port of run_battery.py L1775-1792."""
    lines = output.splitlines()
    def allowed_error(line, allowed):
        stripped = line.strip()
        if stripped == allowed:
            return True
        if allowed.endswith(","):
            return stripped.startswith(allowed) and stripped.count("ERROR:") == 1
        return False
    unrelated_errors = [line for line in lines if "ERROR:" in line
                        and not any(allowed_error(line, allowed) for allowed in allowed_errors)]
    return (code == expected_exit and error is None and signature in output
            and not unrelated_errors and "SCRIPT ERROR:" not in output and "Parse Error:" not in output)

def bounded_run(case, extra_args, bound, cleanup=3, expected_exit=0):
    """Port of run_battery.py bounded_run (L5322-5369), same field set + t values."""
    command = cmd_for(TP, extra_args)
    record = {"case": case, "command": command, "expected_exit": expected_exit,
              "timeout_seconds": bound, "cleanup_seconds": cleanup,
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
            record["raw_stdout"], record["raw_stderr"] = out, err
            record["marker_observed"] = MARKER in out
            record["process_was_running"] = process.poll() is None
            record["error"] = f"TIMEOUT after {bound} seconds"
            if process.poll() is None:
                process.kill()
            more_out, more_err = process.communicate(timeout=cleanup)
            record["raw_stdout"], record["raw_stderr"] = more_out or "", more_err or ""
            record["cleanup_exit_code"] = process.returncode
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        record["error"] = f"launch/read/cleanup error: {exc}"
        if process is not None and process.poll() is None:
            process.kill()
            try:
                process.communicate(timeout=cleanup)
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

def eval_predicates(probe_results):
    old, new, hold = probe_results
    old_rejects = (old["timed_out"] and old["marker_observed"]
                   and old["inner_classification"] is False
                   and old["direct_child_alive_after_cleanup"] is False)
    new_accepts = (not new["timed_out"] and new["actual_exit"] == 0
                   and new["marker_observed"] and new["inner_classification"] is True)
    hold_rejects = (hold["timed_out"] and hold["marker_observed"]
                    and hold["inner_classification"] is False
                    and hold["direct_child_alive_after_cleanup"] is False)
    same_script = all(r["command"][r["command"].index("--script") + 1] == "res://timeout_probe.gd" for r in probe_results)
    same_expected_exit = all(r["expected_exit"] == 0 for r in probe_results)
    meta_pass = old_rejects and new_accepts and hold_rejects and same_script and same_expected_exit
    return {"old_rejects": old_rejects, "new_accepts": new_accepts, "hold_rejects": hold_rejects,
            "same_script": same_script, "same_expected_exit": same_expected_exit, "meta_pass": meta_pass}

def run_arms(tag, notes=""):
    results = [bounded_run("slow_clean_old_bound", ["--delay-clean"], 0.75),
               bounded_run("slow_clean_new_bound", ["--delay-clean"], 3.0),
               bounded_run("hold_open_new_bound", ["--hold-open"], 3.0)]
    preds = eval_predicates(results)
    payload = {"tag": tag, "notes": notes, "loadavg": uptime(), "marker": MARKER,
               "results": results, "predicates": preds,
               "verdict": "PASS" if preds["meta_pass"] else "FAIL"}
    path = os.path.join(OUT, f"{tag}.json")
    open(path, "w").write(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"tag": tag, "predicates": preds, "verdict": payload["verdict"],
                      "elapsed": [r["elapsed_seconds"] for r in results],
                      "marker": [r["marker_observed"] for r in results]}, default=str))
    return payload

def spawn_godot(scratch):
    return subprocess.Popen(cmd_for(scratch, []), stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)

def noise_burst(n=20, style="burst"):
    procs = []
    if style == "burst":
        for _ in range(n):
            procs.append(spawn_godot(TPN))
    else:
        for i in range(n):
            procs.append(spawn_godot(TPN))
            for p in procs[-4:-3]:
                try: p.wait(timeout=5)
                except Exception: pass
            time.sleep(0.35)
    for p in procs:
        try: p.wait(timeout=30)
        except Exception: p.kill()

def zombies():
    z = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            stat = open(f"/proc/{pid}/stat").read()
            comm = stat[stat.index("(") + 1:stat.rindex(")")]
            state = stat[stat.rindex(")") + 2]
            if state == "Z":
                z.append((pid, comm))
        except Exception:
            pass
    return z

def mode_clean(reps):
    for i in range(reps):
        run_arms(f"clean-r{i+1}", f"rep {i+1}/{reps}")
        time.sleep(0.5)

def mode_interleaved():
    for style in ("burst", "spread"):
        t = threading.Thread(target=noise_burst, args=(20, style))
        t.start()
        run_arms(f"interleaved-{style}", f"20 rapid spawns style={style}")
        t.join()
        time.sleep(0.5)

def mode_postkill(n=6):
    held = [subprocess.Popen(cmd_for(TP, ["--hold-open"]), stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL) for _ in range(n)]
    time.sleep(2.0)
    for p in held:
        p.send_signal(signal.SIGKILL)
    time.sleep(0.4)
    z_before = zombies()
    print(json.dumps({"zombies_after_kill": z_before}))
    for i in range(2):
        run_arms(f"postkill-r{i+1}", f"{n} SIGKILLed held-open godot (unreaped); zombies={z_before}")
        time.sleep(0.3)
    print(json.dumps({"zombies_after_arms": zombies(), "held_returncodes_unset": [p.returncode for p in held]}))

def mode_latency(reps, bound=6.0):
    rows = []
    for i in range(reps):
        for extra, kind in (([], "bare"), (["--delay-clean"], "delay")):
            t0 = time.monotonic()
            p = subprocess.Popen(cmd_for(TP, extra), stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True, bufsize=1)
            t_marker = [None]
            def reader():
                for line in p.stdout:
                    if line.strip() == MARKER and t_marker[0] is None:
                        t_marker[0] = round(time.monotonic() - t0, 3)
            th = threading.Thread(target=reader, daemon=True)
            th.start()
            p.wait(timeout=bound)
            t_exit = round(time.monotonic() - t0, 3)
            th.join(timeout=2)
            rows.append({"kind": kind, "t_marker": t_marker[0], "t_exit": t_exit,
                         "rc": p.returncode, "loadavg": uptime()})
    payload = {"mode": "latency", "bound_compared": 0.75, "rows": rows}
    open(os.path.join(OUT, "latency.json"), "w").write(json.dumps(payload, indent=2) + "\n")
    for r in rows:
        print(json.dumps(r))

def mode_bound_diag(bound):
    for b in bound:
        r = bounded_run("slow_clean_old_bound_diag", ["--delay-clean"], b)
        print(json.dumps({"bound": b, "timed_out": r["timed_out"], "marker_observed": r["marker_observed"],
                          "elapsed_seconds": r["elapsed_seconds"], "error": r["error"],
                          "inner_classification": r["inner_classification"]}))

def mode_kill075(reps):
    rows = []
    for i in range(reps):
        t0 = time.monotonic()
        p = subprocess.Popen(cmd_for(TP, ["--delay-clean"]), stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True, bufsize=1)
        t_marker = [None]
        acc = []
        def reader():
            for line in p.stdout:
                acc.append(line)
                if line.strip() == MARKER and t_marker[0] is None:
                    t_marker[0] = round(time.monotonic() - t0, 3)
        th = threading.Thread(target=reader, daemon=True)
        th.start()
        time.sleep(max(0.0, 0.75 - (time.monotonic() - t0)))
        alive = p.poll() is None
        if alive:
            p.kill()
        th.join(timeout=3)
        joined = "".join(acc)
        rows.append({"t_marker": t_marker[0],
                     "pred_marker_by_075": t_marker[0] is not None and t_marker[0] <= 0.75,
                     "alive_at_kill": alive,
                     "marker_in_accumulated_stdout": MARKER in joined,
                     "elapsed": round(time.monotonic() - t0, 3),
                     "loadavg": uptime()})
    print(json.dumps({"mode": "kill075", "bound": 0.75, "rows": rows}))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["clean", "interleaved", "postkill", "latency", "bound-diag", "kill075"])
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--bound", type=float, nargs="+", default=[0.75, 1.5])
    ap.add_argument("--postkill-n", type=int, default=6)
    a = ap.parse_args()
    print(json.dumps({"mode": a.mode, "godot": GODOT, "scratch": TP, "loadavg_start": uptime()}))
    if a.mode == "clean":
        mode_clean(a.reps)
    elif a.mode == "interleaved":
        mode_interleaved()
    elif a.mode == "postkill":
        mode_postkill(a.postkill_n)
    elif a.mode == "latency":
        mode_latency(a.reps)
    elif a.mode == "bound-diag":
        mode_bound_diag(a.bound)
    elif a.mode == "kill075":
        mode_kill075(a.reps)

if __name__ == "__main__":
    main()
