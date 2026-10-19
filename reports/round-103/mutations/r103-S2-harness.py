#!/usr/bin/env python3
"""r102-S2 runner: battery-staging replica + launch + verbatim classifier.

Subcommands:
  stage <fixtures-dir> <scratch-dir>
  run   <scratch-dir> <rows.json> <out.json>
  compare <a.json> <b.json>            # raw + masked receipt diff
  classify <rows.json> <receipts.json> # PASS/FAIL via run_battery.py's own rules

Launch shape is run_battery.py's execute(): [godot --headless --path SCRATCH
--script res://FIXTURE -- FLAGS], merged stdout+stderr, per-process timeout 25s
(harness non-export bound is 8s; 25s chosen so load slowness is not a verdict —
r101-simp3 precedent). Never runs run_battery.py.
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TIMEOUT = 25


def stage(fixtures, scratch, stamp=None):
    fixtures = Path(fixtures)
    scratch = Path(scratch)
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir(parents=True)
    for item in sorted(fixtures.iterdir()):
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, scratch / item.name)
        else:
            shutil.copy2(item, scratch / item.name)
    stamp = stamp or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    project_file = scratch / "project.godot"
    text = project_file.read_text()
    text = text.replace('config/name="MechanicOneShotTest"',
                        f'config/name="MechanicOneShotTest-{stamp}"', 1)
    project_file.write_text(text)
    shutil.copy2(scratch / "controls" / "pickup.tscn", scratch / "pickup.tscn")
    chain = scratch / "causal_chain.gd"
    ctext = chain.read_text()
    anchor = "    await process_frame\n    var old := current_scene"
    assert anchor in ctext, "causal fixture changed; cannot apply scratch-only readiness fix"
    chain.write_text(ctext.replace(anchor, "    await process_frame\n    await process_frame\n    var old := current_scene", 1))
    print(f"staged {scratch}")


def run_rows(scratch, rows_path, out_path):
    rows = json.load(open(rows_path))
    scratch = Path(scratch)
    out = []
    for r in rows:
        cmd = ["godot", "--headless", "--path", str(scratch),
               "--script", "res://" + r["script"], "--", *r["flags"]]
        t0 = datetime.now(timezone.utc)
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
            output = proc.stdout + proc.stderr
            code, error = proc.returncode, None
        except subprocess.TimeoutExpired as exc:
            so = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            se = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            output, code, error = so + se, None, f"TIMEOUT after {TIMEOUT} seconds"
        except OSError as exc:
            output, code, error = str(exc), None, f"launch error: {exc}"
        dt = (datetime.now(timezone.utc) - t0).total_seconds()
        rec = {**r, "command": cmd, "actual_exit": code, "error": error,
               "output": output, "launch_s": round(dt, 3)}
        out.append(rec)
        status = "TIMEOUT" if error else f"rc={code}"
        print(f"{r['name']:<34} {status:<10} {dt:6.2f}s out={len(output)}B")
    json.dump(out, open(out_path, "w"), indent=1)
    print(f"wrote {out_path} rows={len(out)}")


def run_streams(scratch, rows_path, out_path):
    """Same launch shape as run_rows, but stdout/stderr stay separate so the
    byte-identity claim can be stated per stream (run_battery.py merges them:
    output = proc_stdout + proc_stderr)."""
    rows = json.load(open(rows_path))
    scratch = Path(scratch)
    out = []
    for r in rows:
        cmd = ["godot", "--headless", "--path", str(scratch),
               "--script", "res://" + r["script"], "--", *r["flags"]]
        t0 = datetime.now(timezone.utc)
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
            so, se, code, error = proc.stdout, proc.stderr, proc.returncode, None
        except subprocess.TimeoutExpired as exc:
            so = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            se = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            so, se, code, error = so, se, None, f"TIMEOUT after {TIMEOUT} seconds"
        except OSError as exc:
            so, se, code, error = "", str(exc), None, f"launch error: {exc}"
        dt = (datetime.now(timezone.utc) - t0).total_seconds()
        sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
        rec = {**r, "command": cmd, "actual_exit": code, "error": error,
               "stdout": so, "stderr": se,
               "stdout_sha256": sha(so), "stderr_sha256": sha(se),
               "merged_sha256": sha(so + se), "launch_s": round(dt, 3)}
        out.append(rec)
        print(f"{r['name']:<34} rc={code} stdout={len(so)}B/{rec['stdout_sha256'][:12]} "
              f"stderr={len(se)}B/{rec['stderr_sha256'][:12]} {dt:.2f}s")
    json.dump(out, open(out_path, "w"), indent=1)
    print(f"wrote {out_path} rows={len(out)}")


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


def classify(rows_path, receipts_path):
    rows = {r["name"]: r for r in json.load(open(rows_path))}
    receipts = json.load(open(receipts_path))
    n_pass = 0
    for rec in receipts:
        r = rows[rec["name"]]
        code, error, output = rec["actual_exit"], rec["error"], rec["output"]
        signature = r["evidence"]
        allowed = r["expected_errors"]
        lines = output.splitlines()
        unrelated = [ln for ln in lines if "ERROR:" in ln
                     and not any(allowed_error(ln, a) for a in allowed)]
        passed = (code == r["expected_exit"] and error is None and signature in output
                  and not unrelated and "SCRIPT ERROR:" not in output
                  and "Parse Error:" not in output)
        n_pass += passed
        rec["verdict"] = "PASS" if passed else "FAIL"
        if not passed:
            why = []
            if code != r["expected_exit"]:
                why.append(f"exit {code}!={r['expected_exit']}")
            if error:
                why.append(error)
            if signature not in output:
                why.append("sig-missing")
            if unrelated:
                why.append(f"unrelated-err={unrelated[:2]}")
            if "SCRIPT ERROR:" in output:
                why.append("SCRIPT ERROR")
            if "Parse Error:" in output:
                why.append("Parse Error")
            print(f"FAIL {rec['name']}: {'; '.join(why)}")
    json.dump(receipts, open(receipts_path, "w"), indent=1)
    print(f"classified {len(receipts)} rows: PASS={n_pass} FAIL={len(receipts) - n_pass}")
    return n_pass == len(receipts)


MASK = [
    (re.compile(r"pm=(\w+)"), "pm=MASK"),
    (re.compile(r"proc=\d+"), "proc=MASK"),
    (re.compile(r"res://([\w/]+)\.gd:(\d+)"), r"res://\1.gd:MASK"),
]


def mask(text):
    for rx, rep in MASK:
        text = rx.sub(rep, text)
    return text


def compare(a_path, b_path):
    a = {r["name"]: r for r in json.load(open(a_path))}
    b = {r["name"]: r for r in json.load(open(b_path))}
    assert set(a) == set(b)
    raw_diffs, masked_diffs, rc_diffs = [], [], []
    for name in a:
        ra, rb = a[name], b[name]
        if ra["actual_exit"] != rb["actual_exit"]:
            rc_diffs.append((name, ra["actual_exit"], rb["actual_exit"]))
        if ra["output"] != rb["output"]:
            raw_diffs.append(name)
            if mask(ra["output"]) != mask(rb["output"]):
                masked_diffs.append(name)
    print(f"rows={len(a)} rc_diffs={len(rc_diffs)} raw_diffs={len(raw_diffs)} masked_diffs={len(masked_diffs)}")
    for name, x, y in rc_diffs:
        print(f"  RC  {name}: {x} vs {y}")
    for name in raw_diffs:
        print(f"  RAW {name}")
        if name in masked_diffs:
            print("      (masked diff too)")
    for name in masked_diffs:
        la = a[name]["output"].splitlines()
        lb = b[name]["output"].splitlines()
        for i in range(min(len(la), len(lb))):
            if mask(la[i]) != mask(lb[i]):
                print(f"      L{i}: A={la[i][:160]!r}")
                print(f"      L{i}: B={lb[i][:160]!r}")
                break


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "stage":
        stage(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    elif cmd == "run":
        run_rows(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "runstreams":
        run_streams(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "compare":
        compare(sys.argv[2], sys.argv[3])
    elif cmd == "classify":
        ok = classify(sys.argv[2], sys.argv[3])
        sys.exit(0 if ok else 1)
    else:
        raise SystemExit(f"unknown subcommand {cmd}")
