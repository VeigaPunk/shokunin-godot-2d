#!/usr/bin/env python3
"""r62-scout driver (independent; scratch only).

ast.get_source_segment-extracts run_process + classify_process VERBATIM from
the tracked corpus/fixtures/run_battery.py and execs them, so the numbers below
are the production code path on the current runner sha — not a reimplementation.

Three arms of proj/tree_timeout_probe.gd under bound 3.0s:
  clean  - no descendant            -> child-exit-bound control
  hold   - pipe-holding descendant  -> misattributed TIMEOUT (child already dead)
  detach - fd-detached descendant   -> child-exit-bound clean pass (control)

Writes r62-scout-tree-verdicts.json and raw captures under raw/.
"""
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNNER = (HERE.parent.parent / "fixtures" / "run_battery.py").resolve()
GODOT = "godot"
PROJ = HERE / "proj"
RAW = HERE / "raw"
BOUND = 3.0
MARKER = "TREE_TIMEOUT_PROBE: expected signature"


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


def proc_ppid(pid):
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
        return int(stat.rsplit(")", 1)[1].split()[1])
    except OSError:
        return None


def main():
    runner_sha = hashlib.sha256(RUNNER.read_bytes()).hexdigest()
    run_process, classify_process, segs = extract_runner_functions(RUNNER)
    seg_shas = {name: hashlib.sha256(seg.encode()).hexdigest() for name, seg in segs.items()}
    print(f"runner sha256 {runner_sha}")
    for name, sha in seg_shas.items():
        print(f"extracted {name} sha256 {sha}")

    arms = [
        ("clean", []),
        ("hold", ["--spawn-hold"]),
        ("detach", ["--spawn-detach"]),
    ]
    results = []
    for name, extra in arms:
        command = [GODOT, "--headless", "--path", str(PROJ), "--script",
                   "res://tree_timeout_probe.gd", "--", *extra]
        started = time.monotonic()
        output, code, error = run_process(command, BOUND)
        elapsed = time.monotonic() - started
        godot_m = re.search(r"godot_pid=(\d+)", output)
        spawned_m = re.search(r"spawned_pid=(\d+)", output)
        godot_pid = int(godot_m.group(1)) if godot_m else None
        desc_pid = int(spawned_m.group(1)) if spawned_m else None
        record = {
            "arm": name,
            "command": command,
            "bound_seconds": BOUND,
            "elapsed_seconds": round(elapsed, 3),
            "actual_exit": code,
            "error": error,
            "marker_in_output": MARKER in output,
            "descendant_line_in_output": "TREE_DESC_AFTER_PARENT_WRITE" in output,
            "godot_pid": godot_pid,
            "descendant_pid": desc_pid,
            "godot_alive_at_return": proc_alive(godot_pid),
            "descendant_alive_at_return": proc_alive(desc_pid),
            "descendant_ppid_at_return": proc_ppid(desc_pid),
            "expected0_classification": classify_process(code, error, output, 0, MARKER),
            "raw_output": output.strip().splitlines(),
        }
        results.append(record)
        (RAW / f"tree-{name}.stdout").write_text(output)
        print(f"{name}: elapsed={record['elapsed_seconds']}s exit={code} "
              f"error={error!r} classify0={record['expected0_classification']} "
              f"desc_line={record['descendant_line_in_output']} "
              f"godot_alive={record['godot_alive_at_return']} "
              f"desc_alive={record['descendant_alive_at_return']}")

    payload = {
        "mode": "r62_scout_tree_timeout_recheck",
        "runner": str(RUNNER),
        "runner_sha256": runner_sha,
        "extracted_function_sha256": seg_shas,
        "bound_seconds": BOUND,
        "python": sys.version.split()[0],
        "results": results,
    }
    out = HERE / "r62-scout-tree-verdicts.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    sys.exit(main())
