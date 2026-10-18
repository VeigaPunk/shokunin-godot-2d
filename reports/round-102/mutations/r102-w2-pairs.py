#!/usr/bin/env python3
"""r102-w2 part 3: interleaved flush-vs-bound race, ambient vs own-load phases.

Phase 1 (ambient): 8 pairs of (timestamped flush time, bounded_run bound=0.75) on the
r101 scratch copy.
Phase 2 (own load): 8 spinners + repeated pairs.
Reports: per-phase marker-miss counts, flush-time stats, Fisher exact two-sided.
"""
import json
import math
import os
import selectors
import subprocess
import sys
import threading
import time
from pathlib import Path

GODOT = "/usr/bin/godot"
MARKER = "TIMEOUT_PROBE: expected signature"
W2 = Path("/var/tmp/r102-w2")
R101_SCRATCH = str(W2 / "scratch-r101")
OUT = W2 / "pairs.json"


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


def timestamped(proj, extra_args, bound=8.0):
    command = [GODOT, "--headless", "--path", proj, "--script",
               "res://timeout_probe.gd", "--"] + extra_args
    t0 = time.monotonic()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, bufsize=1)
    lines = []
    threading.Thread(target=lambda: [None for _ in proc.stderr], daemon=True).start()
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
    return {"flush_at": next((t for t, l in lines if MARKER in l), None), "exit": proc.returncode}


def bounded(proj, bound=0.75):
    command = [GODOT, "--headless", "--path", proj, "--script",
               "res://timeout_probe.gd", "--", "--delay-clean"]
    t0 = time.monotonic()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, bufsize=1)
    rec = {"timed_out": False, "marker_observed": False}
    try:
        out, _ = proc.communicate(timeout=bound)
        rec["actual_exit"] = proc.returncode
    except subprocess.TimeoutExpired as exc:
        rec["timed_out"] = True
        if proc.poll() is None:
            proc.kill()
        out, _ = proc.communicate(timeout=3)
        rec["cleanup_exit_code"] = proc.returncode
    rec["elapsed_seconds"] = round(time.monotonic() - t0, 3)
    rec["marker_observed"] = MARKER in out
    rec["stdout_tail"] = out[-60:]
    return rec


def fisher_two_sided(a, b, c, d):
    # NOTE (archival fix): the run that produced pairs.json used an earlier fisher
    # implementation whose enumeration did not fix column margins, so its
    # `fisher` field is invalid (>1, superseded). Corrected two-sided values from
    # this fixed function: bound_miss P1 vs P2 = 1.000, flush_over = 1.000.
    # Correct Fisher: fix both margins, sum prob of tables <= obs.
    r1, r2, c1, n = a + b, c + d, a + c, a + b + c + d

    def prob(t):
        b_, c_, d_ = r1 - t, c1 - t, r2 - c1 + t
        if min(b_, c_, d_) < 0:
            return 0.0
        return math.comb(r1, t) * math.comb(r2, c_) / math.comb(n, c1)

    obs = prob(a)
    total = 0.0
    for t in range(max(0, c1 - r2), min(r1, c1) + 1):
        p = prob(t)
        if p <= obs + 1e-12:
            total += p
    return total


def phase(tag, n, result):
    flushes, bounds = [], []
    for i in range(n):
        c1 = census()
        ts = timestamped(R101_SCRATCH, ["--delay-clean"])
        ts["index"] = i
        ts["census_before"] = c1
        flushes.append(ts)
        c2 = census()
        bd = bounded(R101_SCRATCH)
        bd["index"] = i
        bd["census_before"] = c2
        bounds.append(bd)
        print(f"{tag}[{i}] flush={ts['flush_at']} bound_marker={bd['marker_observed']} "
              f"bound_elapsed={bd['elapsed_seconds']} census_g={c2['godot']} load={c2['load'][0]}", flush=True)
    result[tag] = {"flushes": flushes, "bounds": bounds}
    return flushes, bounds


def main():
    out = {"uptime": subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip()}
    f1, b1 = phase("P1_ambient", 8, out)
    spinners = [subprocess.Popen([sys.executable, "-c", "while True: pass"]) for _ in range(8)]
    try:
        f2, b2 = phase("P2_loaded", 8, out)
    finally:
        for s in spinners:
            s.kill()
        for s in spinners:
            s.wait()
    f3, b3 = phase("P3_recovery", 6, out)

    def summ(fs, bs):
        fl = [f["flush_at"] for f in fs if f["flush_at"] is not None]
        miss = sum(1 for b in bs if not b["marker_observed"])
        over = sum(1 for x in fl if x >= 0.753)
        return {"flush_n": len(fl), "flush_over_0.753": over,
                "flush_median": sorted(fl)[len(fl) // 2] if fl else None,
                "bound_miss": miss, "bound_n": len(bs)}
    s1, s2, s3 = summ(f1, b1), summ(f2, b2), summ(f3, b3)
    out["summary"] = {"P1": s1, "P2": s2, "P3": s3}
    # Fisher: ambient vs loaded bound-miss tables
    p12 = fisher_two_sided(s1["bound_miss"], s1["bound_n"] - s1["bound_miss"],
                          s2["bound_miss"], s2["bound_n"] - s2["bound_miss"])
    p12flush = fisher_two_sided(s1["flush_over_0.753"], s1["flush_n"] - s1["flush_over_0.753"],
                                s2["flush_over_0.753"], s2["flush_n"] - s2["flush_over_0.753"])
    out["fisher"] = {"bound_miss_p12": round(p12, 3), "flush_over_p12": round(p12flush, 3)}
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    print("summary", json.dumps(out["summary"]), "fisher", out["fisher"])
    print("wrote", OUT)


if __name__ == "__main__":
    main()
