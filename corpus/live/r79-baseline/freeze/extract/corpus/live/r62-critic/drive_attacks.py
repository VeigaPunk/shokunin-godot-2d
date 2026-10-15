#!/usr/bin/env python3
"""r62-critic adversarial driver (scratch-only; independent reproduction).

Verbatim-extracts run_process + classify_process from the tracked
corpus/fixtures/run_battery.py via ast.get_source_segment and attacks the
r61-boundary pipe-EOF attribution that r62 pins as tracked rows:

  attack (a) - the observed TIMEOUT is actually child-liveness, not pipe-EOF:
      * nopipe-descendant arms (detach) that stay ALIVE past the bound but
        hold no pipes must NOT delay classification (would falsify if they did)
      * early_release: a pipe-holding descendant released well inside the
        bound must return promptly at its EOF, not time out (else falsified)
      * stderr_only / stdout_only: is the block any-captured-pipe or
        stdout-specific?
      * hold_pair vs pair_short: does EOF wait for the LAST pipe holder?
  attack (b) - new rows pass for the wrong reason:
      * hold_silent vs hang_hold: identical verdict-record shape for
        dead-child-pipe-hold vs live-child-hang — any row keying only on
        (error=TIMEOUT, actual_exit=None, verdict) cannot attribute cause
      * spoof: descendant writes the signature line into the captured pipe
        AFTER the child's exit -> signature presence is origin-blind
      * flood: >64KiB of post-parent-death descendant writes land in the
        captured output of a TIMEOUT record
  attack (c) - scheduling race: sweep descendant hold time across the 3.0s
      bound to locate the accept/reject knee and measure the flip margin.

Writes attack-verdicts.json, bound-sweep.json and raw captures under this
directory. No tracked files touched.
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
MARKER = "PIPE_CRITIC: expected signature"


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
    if pid is None or pid <= 0:
        return (None, None, None)
    try:
        text = Path(f"/proc/{pid}/stat").read_text()
        rest = text[text.rindex(")") + 2:].split()
        state, ppid = rest[0], int(rest[1])
    except (OSError, ValueError, IndexError):
        return (None, None, None)
    return (state, ppid, None)


def parse_pids(output):
    godot = re.search(r"PIPE_CRITIC godot_pid= *(\d+)", output or "")
    spawned = [int(m) for m in re.findall(r"PIPE_CRITIC spawned_pid= *(\d+)", output or "")]
    return (int(godot.group(1)) if godot else None), spawned


def run_arm(run_process, classify_process, name, extra_args, bound, outlived=None,
            watch_seconds=0.0):
    """Run one adversarial arm through the verbatim production path."""
    outfile = RAW / f"{name}.stdout"
    if outlived:
        (HERE / outlived).unlink(missing_ok=True)
    command = [GODOT, "--headless", "--path", str(PROJ), "--script",
               "res://pipe_critic_probe.gd", "--", *extra_args,
               f"--out-dir={HERE}"]
    started = time.monotonic()
    output, code, error = run_process(command, bound)
    elapsed = time.monotonic() - started
    outfile.write_text(output or "")
    godot_pid, desc_pids = parse_pids(output)
    record = {
        "case": name,
        "command": command,
        "bound_seconds": bound,
        "actual_exit": code,
        "error": error,
        "elapsed_seconds": round(elapsed, 3),
        "marker_observed": MARKER in (output or ""),
        "desc_post_parent_write_captured": "DESC_POST_PARENT_WRITE" in (output or ""),
        "desc_flood_lines_captured": len(re.findall(r"DESC_FLOOD_\d+", output or "")),
        "godot_pid": godot_pid,
        "descendant_pids": desc_pids,
        "inner_classification": classify_process(code, error, output or "", 0, MARKER),
        "godot_alive_at_return": proc_alive(godot_pid),
        "descendants_alive_at_return": [proc_alive(p) for p in desc_pids],
        "descendant_ppids_at_return": [proc_stat(p)[1] for p in desc_pids],
        "output_line_count": len((output or "").splitlines()),
    }
    if outlived:
        record["descendant_file"] = outlived
        record["descendant_file_landed"] = False
        deadline = time.monotonic() + watch_seconds
        while time.monotonic() < deadline:
            if (HERE / outlived).exists():
                record["descendant_file_landed"] = True
                record["descendant_file_delay_after_return_s"] = round(
                    time.monotonic() - started - elapsed, 3)
                break
            time.sleep(0.2)
        record["descendants_alive_after_watch"] = [proc_alive(p) for p in desc_pids]
    print(f"{name}: exit={code} err={error!r} elapsed={record['elapsed_seconds']}s "
          f"classify={record['inner_classification']} marker={record['marker_observed']} "
          f"godot_alive={record['godot_alive_at_return']} "
          f"desc_alive={record['descendants_alive_at_return']}", flush=True)
    return record


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    runner_sha = hashlib.sha256(RUNNER.read_bytes()).hexdigest()
    run_process, classify_process, segs = extract_runner_functions(RUNNER)
    env = {
        "godot_version": subprocess.run([GODOT, "--version"], capture_output=True,
                                        text=True).stdout.strip(),
        "python": sys.version.split()[0],
        "platform": subprocess.run(["uname", "-srvm"], capture_output=True,
                                   text=True).stdout.strip(),
        "runner": str(RUNNER),
        "runner_sha256": runner_sha,
        "sh": subprocess.run(["readlink", "-f", "/usr/bin/sh"], capture_output=True,
                             text=True).stdout.strip(),
        "started_utc": datetime.now(timezone.utc).isoformat(),
    }
    print(json.dumps(env, indent=2), flush=True)

    B = 3.0
    arms = [
        # attribution falsification set (attack a)
        ("clean", [], B, None, 0.0),
        ("hold_silent", ["--spawn-hold=5"], B, "hold.outlived", 7.0),
        ("hold_write", ["--spawn-hold-write"], B, "hold_write.outlived", 7.0),
        ("early_release", ["--spawn-hold=1.2"], B, None, 0.0),
        ("detach_alive", ["--spawn-detach=6"], B, "detach.outlived", 8.0),
        ("stderr_only", ["--spawn-stderr-only=5"], B, None, 0.0),
        ("stdout_only", ["--spawn-stdout-only=5"], B, None, 0.0),
        ("hold_pair_long", ["--spawn-pair=1.0,5"], B, None, 0.0),
        ("hold_pair_short", ["--spawn-pair=1.0,1.4"], B, None, 0.0),
        # wrong-reason set (attack b)
        ("hang_hold", ["--hang=30", "--spawn-hold=5"], B, "hang_hold.outlived", 7.0),
        ("hang_detach", ["--hang=30", "--spawn-detach=6"], B, "hang_detach.outlived", 8.0),
        ("spoof", ["--no-signature", "--spawn-spoof=0.6"], B, None, 0.0),
        ("spoof_hold", ["--no-signature", "--spawn-spoof=5"], B, None, 0.0),
        ("flood", ["--spawn-flood=5"], B, None, 0.0),
    ]
    # fixture hooks for the hang arms' outlived files are land-file only in
    # hold/detach modes; hang_hold uses spawn-hold which already lands
    # hold.outlived -> reuse that name; hang_detach -> detach.outlived would
    # collide with detach_alive's watch, so use distinct watch via the file
    # written by the same command. (See driver note: hang arms reuse files.)
    records = []
    for name, args, bound, outlived, watch in arms:
        if name == "hang_hold":
            outlived = "hold.outlived"
        if name == "hang_detach":
            outlived = "detach.outlived"
        records.append(run_arm(run_process, classify_process, name, args, bound,
                               outlived=outlived, watch_seconds=watch))

    payload = {
        "mode": "r62_critic_pipe_attribution_attacks",
        "environment": env,
        "marker": MARKER,
        "results": records,
    }
    (HERE / "attack-verdicts.json").write_text(json.dumps(payload, indent=2) + "\n")

    # ---- attack (c): bound-knee sweep on silent hold -----------------------
    sweep = []
    for hold in (2.2, 2.4, 2.5, 2.55, 2.6, 2.7, 2.5, 2.6):
        rec = run_arm(run_process, classify_process, f"sweep_hold_{hold}",
                      ["--spawn-hold=" + str(hold)], B)
        rec["hold_seconds"] = hold
        sweep.append(rec)
    (HERE / "bound-sweep.json").write_text(json.dumps(
        {"mode": "descendant_hold_bound_sweep", "bound_seconds": B,
         "environment": env, "results": sweep}, indent=2) + "\n")
    print("done", flush=True)


if __name__ == "__main__":
    main()
