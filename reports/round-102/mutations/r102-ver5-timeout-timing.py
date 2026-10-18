#!/usr/bin/env python3
"""V5 timestamped probe: measures banner/marker ARRIVAL times per line (reader threads),
for the 3 arms plus bound counterfactuals for slow_clean_old_bound.
Writes /var/tmp/r102-ver5/logs/timing-matrix.json.
"""
import json, subprocess, time, threading

GODOT = "godot"
SCRATCH = "/var/tmp/r102-ver5/scratch"
MARKER = "TIMEOUT_PROBE: expected signature"
CONFIGS = [("slow_clean_old_bound_0.75", ["--delay-clean"], 0.75),
           ("slow_clean_old_bound_1.0", ["--delay-clean"], 1.0),
           ("slow_clean_old_bound_1.5", ["--delay-clean"], 1.5),
           ("slow_clean_new_bound_3.0", ["--delay-clean"], 3.0),
           ("hold_open_new_bound_3.0", ["--hold-open"], 3.0)]
REPS = 3

def timed_run(case, extra, bound):
    cmd = [GODOT, "--headless", "--path", SCRATCH, "--script", "res://timeout_probe.gd", "--"] + extra
    t0 = time.monotonic()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    out_lines, err_lines = [], []

    def rd(stream, sink):
        try:
            for line in stream:
                sink.append([round(time.monotonic() - t0, 3), line.rstrip("\n")])
        except Exception:
            pass

    t1 = threading.Thread(target=rd, args=(p.stdout, out_lines), daemon=True)
    t2 = threading.Thread(target=rd, args=(p.stderr, err_lines), daemon=True)
    t1.start(); t2.start()
    timed_out = False
    try:
        p.wait(timeout=bound)
    except subprocess.TimeoutExpired:
        timed_out = True
        p.kill()
        p.wait()
    t1.join(5); t2.join(5)
    elapsed = round(time.monotonic() - t0, 3)
    banner = [t for t, l in out_lines if l.startswith("Godot Engine v")]
    marker = [t for t, l in out_lines if MARKER in l]
    return {"case": case, "bound": bound, "timed_out": timed_out, "rc": p.returncode,
            "elapsed": elapsed, "t_banner": banner[0] if banner else None,
            "t_marker": marker[0] if marker else None,
            "stdout_lines": out_lines, "err_line_count": len(err_lines),
            "err_lines": err_lines[:5]}

def main():
    matrix = {"reps": REPS, "loadavg_start": open("/proc/loadavg").read().split()[0:3], "runs": []}
    for rep in range(1, REPS + 1):
        for case, extra, bound in CONFIGS:
            r = timed_run(case, extra, bound)
            r["rep"] = rep
            matrix["runs"].append(r)
            print("rep%d %-28s to=%s rc=%s elapsed=%s t_banner=%s t_marker=%s" %
                  (rep, case, r["timed_out"], r["rc"], r["elapsed"], r["t_banner"], r["t_marker"]))
    matrix["loadavg_end"] = open("/proc/loadavg").read().split()[0:3]
    with open("/var/tmp/r102-ver5/logs/timing-matrix.json", "w") as f:
        json.dump(matrix, f, indent=2)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
