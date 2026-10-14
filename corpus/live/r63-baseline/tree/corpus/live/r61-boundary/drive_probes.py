#!/usr/bin/env python3
"""r61-boundary driver (independent; scratch only).

Verbatim-extracts run_process + classify_process from the tracked
corpus/fixtures/run_battery.py via ast.get_source_segment and probes two
unprobed diagnostic shapes:

  tree   - a Godot child spawning an OS descendant that outlives it: does the
           harness (subprocess.run timeout) reap/kill the tree or wait?
  margin - slow-start fixture approaching the timeout bound (CASES bound 8s;
           the tracked --probe-timeout bound 3.0s for comparison).

Writes tree-probe-verdicts.json / margin-probe-verdicts.json and raw captures
under this directory. No tracked files touched.
"""
import ast
import hashlib
import json
import os
import re
import resource
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

MARKER_TREE = "TREE_PROBE: expected signature"
MARKER_MARGIN = "MARGIN_PROBE: expected signature"


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


def proc_alive(pid):
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


def proc_stat(pid):
    """Return (state, ppid, cmdline) from /proc, or (None, None, None)."""
    if pid is None or pid <= 0:
        return (None, None, None)
    try:
        text = Path(f"/proc/{pid}/stat").read_text()
        rest = text[text.rindex(")") + 2 :].split()
        state, ppid = rest[0], int(rest[1])
    except (OSError, ValueError, IndexError):
        return (None, None, None)
    try:
        cmd = (
            Path(f"/proc/{pid}/cmdline")
            .read_bytes()
            .replace(b"\0", b" ")
            .decode(errors="replace")
            .strip()
        )
    except OSError:
        cmd = None
    return (state, ppid, cmd)


def parse_pid(output, name):
    m = re.search(rf"{name}=(\d+)", output or "")
    return int(m.group(1)) if m else None


def run_tree_arm(run_process, classify_process, arm, extra_args, bound, outfile):
    out_path = RAW / outfile
    command = [
        GODOT, "--headless", "--path", str(PROJ), "--script",
        "res://tree_probe.gd", "--", *extra_args, f"--out-dir={HERE}",
    ]
    file_map = {
        "hold": "hold.descendant-outlived",
        "detach": "detach.descendant-outlived",
        "hang": "hang.descendant-outlived",
    }
    fname = file_map.get(arm)
    if fname:
        (HERE / fname).unlink(missing_ok=True)
    started = time.monotonic()
    output, code, error = run_process(command, bound)
    elapsed = time.monotonic() - started
    out_path.write_text(output or "")

    godot_pid = parse_pid(output, "TREE_PROBE godot_pid")
    desc_pid = parse_pid(output, "TREE_PROBE spawned_pid")
    record = {
        "case": arm,
        "command": command,
        "bound_seconds": bound,
        "actual_exit": code,
        "error": error,
        "elapsed_seconds": round(elapsed, 3),
        "marker_observed": MARKER_TREE in (output or ""),
        "descendant_pipe_write_captured": "TREE_DESC_AFTER_PARENT_WRITE" in (output or ""),
        "godot_pid": godot_pid,
        "descendant_pid": desc_pid,
        "inner_classification": classify_process(code, error, output or "", 0, MARKER_TREE),
        "godot_alive_at_return": proc_alive(godot_pid),
    }
    d_state, d_ppid, d_cmd = proc_stat(desc_pid)
    record["descendant_alive_at_return"] = proc_alive(desc_pid)
    record["descendant_state_at_return"] = d_state
    record["descendant_ppid_at_return"] = d_ppid
    record["descendant_cmdline_at_return"] = d_cmd

    # Watch the descendant past the point where the harness has already moved
    # on: does the expected outlived-file land, and is the pid still present?
    record["descendant_file"] = fname
    record["descendant_file_landed"] = False
    record["descendant_file_delay_after_return_s"] = None
    record["descendant_alive_after_file"] = None
    if fname:
        deadline = time.monotonic() + 14.0
        while time.monotonic() < deadline:
            if (HERE / fname).exists():
                record["descendant_file_landed"] = True
                record["descendant_file_delay_after_return_s"] = round(
                    time.monotonic() - started - elapsed, 3
                )
                break
            time.sleep(0.25)
        record["descendant_alive_after_file"] = proc_alive(desc_pid)
        fstate, fppid, _ = proc_stat(desc_pid)
        record["descendant_state_after_file"] = fstate
        record["descendant_ppid_after_file"] = fppid
    print(
        f"{arm}: exit={code} err={error!r} elapsed={record['elapsed_seconds']}s "
        f"classify={record['inner_classification']} desc_pid={desc_pid} "
        f"desc_alive_return={record['descendant_alive_at_return']} "
        f"file={record['descendant_file_landed']}",
        flush=True,
    )
    return record


def run_margin_arm(run_process, classify_process, delay, bound):
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
        "marker_observed": MARKER_MARGIN in (output or ""),
        "inner_classification": classify_process(code, error, output or "", 0, MARKER_MARGIN),
    }
    print(
        f"delay={delay} bound={bound}: exit={code} err={error!r} "
        f"elapsed={record['elapsed_seconds']}s marker={record['marker_observed']} "
        f"classify={record['inner_classification']}",
        flush=True,
    )
    return record


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
    }
    print(json.dumps(env, indent=2), flush=True)

    # --- probe 1: process-tree timeout -------------------------------------
    tree_results = [
        run_tree_arm(run_process, classify_process, "clean", [], 3.0, "tree-clean.stdout"),
        run_tree_arm(run_process, classify_process, "hold", ["--spawn-hold"], 3.0, "tree-hold.stdout"),
        run_tree_arm(run_process, classify_process, "detach", ["--spawn-detach"], 3.0, "tree-detach.stdout"),
        run_tree_arm(run_process, classify_process, "hang", ["--spawn-hang"], 3.0, "tree-hang.stdout"),
    ]
    tree_payload = {
        "mode": "process_tree_timeout_four_arm",
        "mechanism": (
            "run_process uses subprocess.run(capture_output, timeout); POSIX "
            "timeout path is kill() on the direct child pid only + wait(); no "
            "process-group signal, no descendant handling; pipe EOF awaited "
            "only inside communicate(timeout)"
        ),
        "environment": env,
        "results": tree_results,
    }
    (HERE / "tree-probe-verdicts.json").write_text(
        json.dumps(tree_payload, indent=2) + "\n"
    )

    if "--tree-only" in sys.argv:
        print("done (tree only)", flush=True)
        return

    # --- probe 2: startup margin -------------------------------------------
    margin_results = []
    for _ in range(8):
        margin_results.append(run_margin_arm(run_process, classify_process, 0.0, 8.0))
    for delay in (5.0, 6.5, 7.0, 7.2, 7.4, 7.6, 8.5):
        margin_results.append(run_margin_arm(run_process, classify_process, delay, 8.0))
    # near-boundary repeats at the observed knee
    for delay in (7.2, 7.3, 7.4, 7.5, 7.2, 7.3, 7.4, 7.5):
        margin_results.append(run_margin_arm(run_process, classify_process, delay, 8.0))
    # tracked --probe-timeout bound (3.0s) margin for comparison
    for delay in (2.0, 2.3, 2.45, 2.55, 2.0, 2.3, 2.45, 2.55):
        margin_results.append(run_margin_arm(run_process, classify_process, delay, 3.0))

    margin_payload = {
        "mode": "startup_margin_sweep",
        "environment": env,
        "results": margin_results,
    }
    (HERE / "margin-probe-verdicts.json").write_text(
        json.dumps(margin_payload, indent=2) + "\n"
    )
    print("done", flush=True)


if __name__ == "__main__":
    main()
