#!/usr/bin/env python3
"""r103-S3: run the 12 r97 CASES rows against a staged scratch project with the
harness's own launch shape (`godot --headless --path <p> --script
res://stree_lattice.gd -- <flags>`, 8 s bound) and the harness's own
classify_process semantics over merged stdout+stderr.

Signatures are extracted from the live run_battery.py (read-only) so the
runner cannot drift from the pinned rows.

usage: run_rows.py <scratch> <out.json> <harness.py> [arm_filter]
"""
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import time

scratch, out_path, harness_path = sys.argv[1], sys.argv[2], sys.argv[3]
arm_filter = sys.argv[4] if len(sys.argv) > 4 else None

ROWS = [
    ("stree_lattice_census", ["--arm=census"]),
    ("stree_lattice_group_order", ["--arm=group_order"]),
    ("stree_lattice_group_order_rev", ["--arm=group_order", "--rev"]),
    ("stree_lattice_group_flags", ["--arm=group_flags"]),
    ("stree_lattice_group_lifecycle", ["--arm=group_lifecycle"]),
    ("stree_lattice_group_setters", ["--arm=group_setters"]),
    ("stree_lattice_signal_order", ["--arm=signal_order"]),
    ("stree_lattice_signal_flags", ["--arm=signal_flags"]),
    ("stree_lattice_defer_ladder", ["--arm=defer_ladder"]),
    ("stree_lattice_defer_slots", ["--arm=defer_slots"]),
    ("stree_lattice_defer_order", ["--arm=defer_order"]),
    ("stree_lattice_scene_probe", ["--arm=scene_probe"]),
]

harness = pathlib.Path(harness_path).read_text()
sig_map = {}
pattern = re.compile(
    r"\('(stree_lattice_[a-z_]+)', 'stree_lattice\.gd', \[[^\]]*\], 0,\s*\n\s*'([^']*)'\)")
for m in pattern.finditer(harness):
    sig_map[m.group(1)] = m.group(2)
assert len(sig_map) == 12, f"extracted {len(sig_map)} signatures, want 12"


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


records = []
for name, flags in ROWS:
    if arm_filter and arm_filter not in name:
        continue
    command = ["godot", "--headless", "--path", scratch, "--script",
               "res://stree_lattice.gd", "--", *flags]
    started = time.time()
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=8)
        rc, err, stdout, stderr = proc.returncode, None, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        rc, err = None, "TIMEOUT after 8 seconds"
        stdout = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
    merged = stdout + stderr
    signature = sig_map[name]
    unrelated = [line for line in merged.splitlines() if "ERROR:" in line]
    passed = (rc == 0 and err is None and signature in merged
              and not unrelated and "SCRIPT ERROR:" not in merged
              and "Parse Error:" not in merged)
    records.append({
        "case": name, "flags": flags, "rc": rc, "error": err,
        "sig_present": signature in merged, "verdict": "PASS" if passed else "FAIL",
        "unrelated_errors": unrelated,
        "stdout_sha256": sha(stdout), "stderr_sha256": sha(stderr),
        "merged_sha256": sha(merged), "elapsed": round(time.time() - started, 3),
        "stdout": stdout, "stderr": stderr,
    })

pathlib.Path(out_path).write_text(json.dumps(records, indent=1) + "\n")
for rec in records:
    print(f"{rec['verdict']} {rec['case']} rc={rec['rc']} sig={rec['sig_present']} "
          f"merged_sha={rec['merged_sha256'][:16]} {rec['elapsed']}s")
