#!/usr/bin/env python3
"""r102-E3 register-shape verifier.

Replays the three proposed CASES rows for corpus/fixtures/export_launch_s03.gd in
the battery's exact launch shape and applies a byte-faithful copy of the harness
classifier (run_battery.py classify_process: expected exit, signature substring of
the merged stdout+stderr, no SCRIPT ERROR:/Parse Error:, no unallowed ERROR:).
run_battery.py itself is NOT executed (lane hard rule 1).

Usage: python3 r102-E3-verify_rows.py [--godot /usr/bin/godot] [--scratch DIR]
"""
import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[3]
FIXTURE = REPO / "corpus" / "fixtures"
SCRIPT = "export_launch_s03.gd"

ROWS = [
    ("export_launch_s03_mainpack_refusal", "refuse", 0,
     "PASS export_launch_s03 refuse binary=exported_stock_template flag=--main-pack rc=1 "
     "rc_class=nonzero_exit stdout_bytes=0 stderr_bytes=265 prefix_hex=4552524f523a20 "
     "hint_present=true at_line_present=true unconditional=true sibling_pack_present=true "
     "frag=`--main-pack` was specified on the command line, but this Godot binary was "
     "compiled without support for path overrides. Aborting."),
    ("export_launch_s03_editor_mainpack_contrast", "contrast", 0,
     "PASS export_launch_s03 contrast binary=editor flag=--main-pack rc=0 rc_class=zero "
     "stderr_bytes=0 stdout_bytes=185 boot_lines=1 frames=[1,2,3] extra_marker_lines=false "
     "banner_version=4.7.2"),
    ("export_launch_s03_template_sibling_pack", "sibling", 0,
     "PASS export_launch_s03 sibling binary=exported_stock_template flag=none rc=0 "
     "rc_class=zero stderr_bytes=0 stdout_bytes=157 boot_lines=1 frames=[1,2,3] "
     "extra_marker_lines=false banner_version=4.7.2 sibling_pack_load=true"),
]


def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
    """Byte-faithful copy of run_battery.py:1725 classify_process with no allowed errors."""
    def allowed_error(line, allowed):
        stripped = line.strip()
        return any(stripped == a for a in allowed)

    unrelated_errors = [line for line in output.splitlines() if "ERROR:" in line
                        and not any(allowed_error(line, allowed) for allowed in allowed_errors)]
    return (code == expected_exit and error is None and signature in output
            and not unrelated_errors and "SCRIPT ERROR:" not in output
            and "Parse Error:" not in output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--godot", default="godot")
    parser.add_argument("--scratch", type=Path,
                        default=Path("/var/tmp/r102-E3/battery/scratch"))
    args = parser.parse_args()

    scratch = args.scratch
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir(parents=True)
    for item in FIXTURE.iterdir():
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, scratch / item.name)
        else:
            shutil.copy2(item, scratch / item.name)

    records = []
    for name, arm, expected_exit, signature in ROWS:
        cmd = [args.godot, "--headless", "--path", str(scratch), "--script", "res://" + SCRIPT,
               "--", "--arm=" + arm]
        started = time.monotonic()
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        elapsed = time.monotonic() - started
        merged = proc.stdout + proc.stderr
        ok = classify_process(proc.returncode, None, merged, expected_exit, signature)
        diag = [l for l in merged.splitlines() if l.startswith("S03_DIAG")]
        records.append({"case": name, "arm": arm, "command": cmd, "actual_exit": proc.returncode,
                        "elapsed_seconds": round(elapsed, 3),
                        "diag": diag,
                        "classify_pass": ok, "merged_has_ERROR_token": "ERROR:" in merged,
                        "stdout_bytes": len(proc.stdout), "stderr_bytes": len(proc.stderr),
                        "signature_found": signature in merged,
                        "unexpected_error_lines": [l for l in merged.splitlines() if "ERROR:" in l]})
        print(f"{'PASS' if ok else 'FAIL'} {name}: exit={proc.returncode} wall={elapsed:.2f}s "
              f"stderr_bytes={len(proc.stderr)} ERROR_token={'ERROR:' in merged}")
    payload = {"rows": records, "verdict": "PASS" if all(r["classify_pass"] for r in records) else "FAIL",
               "classifier": "byte-faithful copy of run_battery.py classify_process (no allowed_errors)"}
    out = scratch.parent / "verify_rows.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"{payload['verdict']} r102-E3 register-shape verification -> {out}")
    return 0 if payload["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
