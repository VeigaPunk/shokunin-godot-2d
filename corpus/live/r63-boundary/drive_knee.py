#!/usr/bin/env python3
"""r63-boundary driver 1/2: startup-margin knee sweep (scratch only).

Verbatim-extracts run_process + classify_process from the tracked
corpus/fixtures/run_battery.py via ast.get_source_segment and execs them —
the production code path, not a reimplementation.

Goal (from the lane brief): pin the r61-retained startup-margin knee —
delay in (7.5, 7.6]s under the CASES 8s bound — to +/-0.05s and measure
cross-run variance. Two adjacent transitions are recorded separately:

  * classify knee: last delay whose run still classifies True
    (elapsed < bound; exit 0; no error).
  * marker knee:  last delay whose run still captures the signature in the
    merged stream before the bound fires (marker_observed=True inside a
    TIMEOUT record) — the r61 7.6 run's shape.

Runs are SEQUENTIAL on purpose: elapsed is the measurement; concurrent
godot startups would contaminate it.

Writes knee-sweep-verdicts.json + raw captures under this directory.
No tracked files touched.
"""
import ast
import hashlib
import json
import os
import resource
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNNER = (HERE.parent.parent / "fixtures" / "run_battery.py").resolve()
GODOT = "godot"
PROJ = HERE / "proj"
RAW = HERE / "raw"

MARKER = "MARGIN_PROBE: expected signature"


def extract_runner_functions(runner_path):
    src = runner_path.read_text()
    tree = ast.parse(src)
    segs = {}

    def walk(node):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name in (
                "run_process",
                "classify_process",
            ):
                seg = ast.get_source_segment(src, child)
                assert seg, f"no source segment for {child.name}"
                segs[child.name] = seg
            walk(child)

    walk(tree)
    assert set(segs) == {"run_process", "classify_process"}, segs.keys()
    ns = {"subprocess": subprocess}
    exec(segs["run_process"], ns)
    exec(segs["classify_process"], ns)
    return ns["run_process"], ns["classify_process"], segs


def run_margin_arm(run_process, classify_process, delay, bound, tag=None):
    command = [
        GODOT, "--headless", "--path", str(PROJ), "--script",
        "res://margin_probe.gd", "--", f"--delay={delay}",
    ]
    started = time.monotonic()
    output, code, error = run_process(command, bound)
    elapsed = time.monotonic() - started
    record = {
        "delay_seconds": delay,
        "bound_seconds": bound,
        "actual_exit": code,
        "error": error,
        "elapsed_seconds": round(elapsed, 3),
        # overhead = wall the run spends beyond the requested delay; only
        # meaningful for non-timeout runs (timeout elapsed is bound-censored).
        "overhead_seconds": round(elapsed - delay, 3) if code == 0 else None,
        "marker_observed": MARKER in (output or ""),
        "inner_classification": classify_process(code, error, output or "", 0, MARKER),
    }
    if tag:
        record["tag"] = tag
    (RAW / f"margin-{tag or ('d' + str(delay))}-b{bound}.stdout").write_text(output or "")
    print(
        f"delay={delay} bound={bound}: exit={code} err={error!r} "
        f"elapsed={record['elapsed_seconds']}s "
        f"overhead={record['overhead_seconds']} "
        f"marker={record['marker_observed']} "
        f"classify={record['inner_classification']}",
        flush=True,
    )
    return record


def summarize(results, bound):
    """Per-delay aggregates + derived knee location for one bound."""
    by_delay = {}
    for r in results:
        if r["bound_seconds"] != bound:
            continue
        by_delay.setdefault(r["delay_seconds"], []).append(r)
    rows = []
    overheads = []
    for delay in sorted(by_delay):
        rs = by_delay[delay]
        el = [r["elapsed_seconds"] for r in rs]
        oh = [r["overhead_seconds"] for r in rs if r["overhead_seconds"] is not None]
        overheads.extend(oh)
        rows.append({
            "delay_seconds": delay,
            "n": len(rs),
            "passes": sum(1 for r in rs if r["inner_classification"]),
            "marker_in_partial": sum(1 for r in rs if r["marker_observed"]),
            "elapsed_min": round(min(el), 3),
            "elapsed_max": round(max(el), 3),
            "elapsed_mean": round(statistics.fmean(el), 3),
            "elapsed_stdev": round(statistics.stdev(el), 4) if len(el) > 1 else 0.0,
            "overhead_min": round(min(oh), 3) if oh else None,
            "overhead_max": round(max(oh), 3) if oh else None,
        })
    accepting = [r["delay_seconds"] for r in rows if r["passes"] == r["n"]]
    rejecting = [r["delay_seconds"] for r in rows if r["passes"] == 0]
    marking = [r["delay_seconds"] for r in rows if r["marker_in_partial"] == r["n"]]
    not_marking = [r["delay_seconds"] for r in rows if r["marker_in_partial"] == 0]
    return {
        "bound_seconds": bound,
        "per_delay": rows,
        "classify_knee_delay_bracket": [max(accepting) if accepting else None,
                                        min(rejecting) if rejecting else None],
        "marker_knee_delay_bracket": [max(marking) if marking else None,
                                      min(not_marking) if not_marking else None],
        "overhead_pool_n": len(overheads),
        "overhead_min": round(min(overheads), 3) if overheads else None,
        "overhead_max": round(max(overheads), 3) if overheads else None,
        "overhead_mean": round(statistics.fmean(overheads), 4) if overheads else None,
        "overhead_stdev": round(statistics.stdev(overheads), 4) if len(overheads) > 1 else None,
    }


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    runner_sha = hashlib.sha256(RUNNER.read_bytes()).hexdigest()
    run_process, classify_process, segs = extract_runner_functions(RUNNER)

    env = {
        "godot_version": subprocess.run(
            [GODOT, "--version"], capture_output=True, text=True
        ).stdout.strip(),
        "python": sys.version.split()[0],
        "platform": subprocess.run(
            ["uname", "-srvm"], capture_output=True, text=True
        ).stdout.strip(),
        "runner": str(RUNNER),
        "runner_sha256": runner_sha,
        "rlimit_core": list(resource.getrlimit(resource.RLIMIT_CORE)),
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "cpu": Path("/proc/loadavg").read_text().strip(),
    }
    print(json.dumps(env, indent=2), flush=True)

    results = []

    # Baseline jitter: immediate-exit overhead distribution (n=8).
    for i in range(8):
        results.append(run_margin_arm(run_process, classify_process, 0.0, 8.0,
                                      tag=f"base{i}"))

    # Sanity wing well below the knee (r61: True at 7.3).
    for i in range(2):
        results.append(run_margin_arm(run_process, classify_process, 7.3, 8.0,
                                      tag=f"w730_{i}"))

    # Fine knee sweep: 0.05 steps over the r61 bracket (7.5, 7.6], padded one
    # step each side, n=4 per point — sequential, ~8s each.
    for delay in (7.45, 7.50, 7.55, 7.60, 7.65, 7.70, 7.75):
        for i in range(4):
            results.append(run_margin_arm(run_process, classify_process,
                                          delay, 8.0, tag=f"d{delay}_{i}"))

    # Marker-presence tail: signature should stop being emitted once the
    # delay alone exceeds bound - startup_overhead (~0.36s).
    for delay in (7.9, 8.2):
        for i in range(2):
            results.append(run_margin_arm(run_process, classify_process,
                                          delay, 8.0, tag=f"t{delay}_{i}"))

    # Same knee under the tracked --probe-timeout bound (3.0s): does the
    # overhead budget transfer (r61 predicted ~0.4s headroom)?
    for delay in (2.50, 2.55, 2.60, 2.65):
        for i in range(3):
            results.append(run_margin_arm(run_process, classify_process,
                                          delay, 3.0, tag=f"b3d{delay}_{i}"))

    payload = {
        "mode": "startup_margin_knee_sweep_r63",
        "mechanism": (
            "run_process = subprocess.run(capture_output=True, text=True, "
            "timeout); communicate returns at min(bound, child_exit+EOF); "
            "TIMEOUT -> error set + actual_exit None -> classify False "
            "regardless of marker presence"
        ),
        "environment": env,
        "summaries": [summarize(results, 8.0), summarize(results, 3.0)],
        "results": results,
    }
    out = HERE / "knee-sweep-verdicts.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print("wrote", out, flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    main()
