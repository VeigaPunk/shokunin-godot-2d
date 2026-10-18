#!/usr/bin/env python3
"""MUT-6 — timeout truncation on the export launch probe.

Faithfully replicates the `--probe-export-launch` launch path from
corpus/fixtures/run_battery.py:4438-4529 (run_process 1698, classify_process
1725) against adversarial exported Linux/X11 payloads, scratch-only under
/tmp/r101-mut6. NEVER runs run_battery.py.

Questions:
  Q1 timeout truncation: when the launched exported app is killed at the 5 s
     bound, what exactly is captured, and does the probe's assertion accept
     or reject it? (fail-open vs fail-closed)
  Q2 receipt replay: does the recorded receipt alone let a truncated row be
     replayed as "signature seen"? Which receipt fields distinguish it?
  Q3 channel seam: the probe classifies the MERGED stdout+stderr string
     (run_battery.py:4481/4486). Can a startup "signature" that no stream
     ever printed as a line be synthesized (stderr-only / split seam)?
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FIXTURES = REPO / "corpus" / "fixtures"
EXPECTED = "EXPORT_LAUNCH_READY scene=fixture"


def run_process(command, timeout_seconds, env=None):  # run_battery.py:1698 verbatim
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout_seconds, env=env)
        return proc.stdout + proc.stderr, proc.returncode, None
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        output += (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return output, None, f"TIMEOUT after {timeout_seconds} seconds"
    except OSError as exc:
        return str(exc), None, f"launch error: {exc}"


def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
    # run_battery.py:1725-1742 verbatim (allowed_errors unused here)
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


PAYLOADS = {
    # label: (with_event-style body lines, expected startup event emitted)
    "baseline_positive": ('    print("EXPORT_LAUNCH_READY scene=fixture")\n    get_tree().quit()\n', True),
    "baseline_negative": ('    get_tree().quit()\n', False),
    # signature, then block main thread past the 5 s launch bound
    "positive_then_hang": ('    print("EXPORT_LAUNCH_READY scene=fixture")\n    OS.delay_msec(60000)\n', True),
    # signature survives the truncation prefix, late ERROR never emitted before kill
    "truncation_tail_loss": ('    print("EXPORT_LAUNCH_READY scene=fixture")\n    OS.delay_msec(6000)\n'
                             '    printerr("ERROR: late fault")\n    get_tree().quit()\n', True),
    # no event at all, blocks instead of clean exit
    "negative_hang": ('    OS.delay_msec(60000)\n', False),
    # signature only ever on stderr
    "stderr_only_signature": ('    printerr("EXPORT_LAUNCH_READY scene=fixture")\n    get_tree().quit()\n', True),
    # no stream contains the line; merged stdout+stderr yields it across the seam
    "seam_split_signature": ('    printraw("EXPORT_LAUNCH_READY scene=")\n'
                             '    printerr("fixture")\n    get_tree().quit()\n', True),
    # legitimate but slow: prints at ~3.5 s, inside the 5 s bound
    "slow_positive_3500ms": ('    OS.delay_msec(3500)\n    print("EXPORT_LAUNCH_READY scene=fixture")\n'
                             '    get_tree().quit()\n', True),
}


RETRY_LOG = []


def retry(fn, label, attempts=4, delay=4.0):
    """Host /tmp is a contended 16G tmpfs; sibling seats' exports intermittently
    make writes fail with EDQUOT/ENOSPC. Retry with backoff, log every event."""
    last = None
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except OSError as exc:
            last = exc
            RETRY_LOG.append({"label": label, "attempt": attempt, "error": f"{type(exc).__name__}: {exc}"})
            print(f"RETRY {label} attempt {attempt} failed: {type(exc).__name__}: {exc}", flush=True)
            time.sleep(delay * attempt)
    raise last


def build_scratch(work):
    scratch = work / "scratch"
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir(parents=True)
    for item in FIXTURES.iterdir():  # run_battery.py:1675-1687 mirror
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        dst = scratch / item.name
        if item.is_dir():
            retry(lambda s=item, d=dst: shutil.copytree(s, d), f"copytree {item.name}")
        else:
            retry(lambda s=item, d=dst: shutil.copy2(s, d), f"copy2 {item.name}")
    retry(lambda: shutil.copy2(scratch / "controls" / "pickup.tscn", scratch / "pickup.tscn"), "stage pickup.tscn")
    return scratch


def configure(project, body):
    (project / "export_launch.tscn").write_text(
        '[gd_scene load_steps=2 format=3]\n\n'
        '[ext_resource type="Script" path="res://export_launch.gd" id="1"]\n\n'
        '[node name="ExportLaunch" type="Node"]\nscript = ExtResource("1")\n')
    (project / "export_launch.gd").write_text('extends Node\n\nfunc _ready() -> void:\n' + body)
    pf = project / "project.godot"
    text = pf.read_text()
    text = text.replace('config/features=PackedStringArray("4.7")\n',
                        'config/features=PackedStringArray("4.7")\nrun/main_scene="res://export_launch.tscn"\n', 1)
    pf.write_text(text)


def tail_hex(data, n=80):
    return data.encode()[len(data.encode()) - n:].hex() if data else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--godot", default="godot")
    ap.add_argument("--work", default="/tmp/r101-mut6")
    args = ap.parse_args()
    work = Path(args.work)
    work.mkdir(parents=True, exist_ok=True)
    receipt = {"work": str(work), "expected_signature": EXPECTED,
               "load": subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip()}
    scratch = build_scratch(work)
    print(f"MUT6 scratch={scratch} load={receipt['load']}", flush=True)
    results = []
    for label, (body, with_event) in PAYLOADS.items():
        project = work / label
        if project.exists():
            shutil.rmtree(project)
        retry(lambda: shutil.copytree(scratch, project, ignore=shutil.ignore_patterns(".godot", "out")),
              f"copytree payload {label}")
        configure(project, body)
        out_dir = project / "out"
        out_dir.mkdir(exist_ok=True)
        exe = (out_dir / "fixture-launch.x86_64").resolve()
        export_cmd = [args.godot, "--headless", "--path", str(project),
                      "--export-debug", "Linux/X11", str(exe)]
        export_attempts = 0
        for export_attempts in range(1, 4):
            for stale in out_dir.iterdir():
                stale.unlink()
            t0 = time.monotonic()
            try:
                exp_output, exp_code, exp_error = run_process(export_cmd, 60)
            except OSError as exc:  # tmpfs contention mid-export
                exp_output, exp_code, exp_error = str(exc), None, f"launch error: {exc}"
                RETRY_LOG.append({"label": f"export {label}", "attempt": export_attempts,
                                  "error": f"{type(exc).__name__}: {exc}"})
            exp_secs = round(time.monotonic() - t0, 2)
            exp_ok = (classify_process(exp_code, exp_error, exp_output, 0, "[ DONE ]")
                      and "savepack" in exp_output and exe.is_file() and exe.stat().st_size > 0)
            if exp_ok:
                break
            print(f"RETRY export {label} attempt {export_attempts}: exit={exp_code} "
                  f"err={exp_error!r} tail={exp_output.strip().splitlines()[-2:]}", flush=True)
            time.sleep(4 * export_attempts)
        pack = exe.with_suffix(".pck")
        row = {"case": label, "expected_startup_event": with_event,
               "export_exit": exp_code, "export_error": exp_error, "export_seconds": exp_secs,
               "export_attempts": export_attempts,
               "export_bytes": exe.stat().st_size if exe.is_file() else 0,
               "pack_bytes": pack.stat().st_size if pack.is_file() else 0,
               "pack_sha256": hashlib.sha256(pack.read_bytes()).hexdigest() if pack.is_file() else None}
        # ---- faithful replication of run_battery.py:4474-4490 ----
        launch_cmd = [str(exe), "--headless"]
        launch_cwd = str(out_dir)
        launch_output, launch_code, launch_error = "", None, "export failed; launch skipped"
        raw = None
        if exp_ok:
            t0 = time.monotonic()
            try:
                proc = subprocess.run(launch_cmd, cwd=launch_cwd, capture_output=True, text=True, timeout=5)
                launch_output, launch_code, launch_error = proc.stdout + proc.stderr, proc.returncode, None
            except subprocess.TimeoutExpired as exc:
                launch_output = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
                launch_output += (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
                launch_code, launch_error = None, "TIMEOUT after 5 seconds"
                row["timeout_exc_stdout_type"] = type(exc.stdout).__name__
                row["timeout_exc_cmd"] = exc.cmd
            row["launch_seconds"] = round(time.monotonic() - t0, 2)
            # auxiliary raw launch: streams kept separate (not probe code path)
            try:
                rp = subprocess.run(launch_cmd, cwd=launch_cwd, capture_output=True, text=True, timeout=5)
                raw = {"exit": rp.returncode, "stdout": rp.stdout, "stderr": rp.stderr, "error": None}
            except subprocess.TimeoutExpired as exc:
                out = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode(errors="replace")
                err = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or b"").decode(errors="replace")
                raw = {"exit": None, "stdout": out, "stderr": err, "error": "TIMEOUT after 5 seconds"}
        signature_lines = [ln.strip() for ln in launch_output.splitlines() if ln.strip() == EXPECTED]
        asserted = (exp_ok and classify_process(launch_code, launch_error, launch_output, 0, EXPECTED)
                    and len(signature_lines) == 1
                    and not (Path(launch_cwd) / "project.godot").exists()
                    and not (Path(launch_cwd) / "export_launch.gd").exists()
                    and not (Path(launch_cwd) / "export_launch.tscn").exists())
        clean_without_signature = (launch_code == 0 and launch_error is None
                                   and "SCRIPT ERROR:" not in launch_output and "Parse Error:" not in launch_output
                                   and "ERROR:" not in launch_output)
        row.update({
            "launch_exit": launch_code, "launch_error": launch_error,
            "launch_output": launch_output.strip().splitlines(),
            "launch_output_repr": repr(launch_output[:400]),
            "launch_output_tail_hex": tail_hex(launch_output),
            "signature_lines": len(signature_lines),
            "same_signature_assertion": asserted,
            "clean_process_without_signature": clean_without_signature,
            "naive_receipt_replay_accept": len(signature_lines) == 1,
            "full_receipt_replay_accept": (launch_code == 0 and launch_error is None
                                           and len(signature_lines) == 1),
            "raw_streams": raw,
        })
        print(f"{label}: exp_ok={exp_ok} launch_exit={launch_code} launch_error={launch_error!r} "
              f"sig_lines={len(signature_lines)} asserted={asserted} "
              f"naive_replay={row['naive_receipt_replay_accept']} "
              f"full_replay={row['full_receipt_replay_accept']} exp_s={exp_secs} "
              f"launch_s={row.get('launch_seconds')}", flush=True)
        results.append(row)
        for item in list(out_dir.iterdir()):
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
    receipt["results"] = results
    receipt["payloads"] = {k: v[0] for k, v in PAYLOADS.items()}
    receipt["retry_log"] = RETRY_LOG
    receipt_path = work / "mut06-receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"MUT6 receipt: {receipt_path}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
