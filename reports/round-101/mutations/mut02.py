#!/usr/bin/env python3
"""mut02 — MUT-2 (r101): forged receipt line in an export row.

Measures which verification clauses detect a forged receipt line against a real
Godot 4.7.2 headless export. All "receipt bytes" are genuine captures of real
runs; the forged arms mutate only the line/artifact under test.

Clause shapes evaluated (all against the same arm bytes):
  landed_export  — verbatim copy of run_battery.py:1877-1880 `classify_export`
                   for the `__godot_export__` row (classify_process with
                   "[ DONE ]" + "savepack" + artifact is_file + size>0).
  magic          — landed_export + artifact first 4 bytes == b"GDPC".
  sha256         — landed_export + artifact sha256 pinned (determinism-row shape).
  line_pin       — generic CASES shape: classify_process(code, error, output,
                   0, receipt_line) — a row that pins a receipt substring only.

Arms:
  V0  real export, real artifact, real receipt              (control)
  V1  real receipt + forged extra success receipt line
  V1b real receipt + duplicate forged "[ DONE ] savepack" marker line
  V2  real receipt + forged ERROR / SCRIPT ERROR line
  V3  real receipt + artifact swapped to junk bytes (wrong magic, size>0)
  V3b real receipt + artifact truncated to 0 bytes
  V3c real receipt + artifact deleted
  V4  real receipt + real PCK with magic patched GDPC->GDPX
  V5  silent `--main-pack` launch output + forged READY receipt line
  V5c real `--main-pack` launch receipt (control for V5)

Usage: python3 reports/round-101/mutations/mut02.py [--run-root DIR]
Scratch default: /var/tmp/r101-mut2-run (repo /tmp is quota-capped on this host).
No tracked file is written; shared files are never touched.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
GODOT = "/usr/bin/godot"
PRESET = "Linux/X11"

PROJECT_GODOT = 'config_version=5\n\n[application]\n\nconfig/name="r101-mut2-scratch"\nconfig/features=PackedStringArray("4.7")\nrun/main_scene="res://main.tscn"\n'
MAIN_TSCN = '[gd_scene load_steps=2 format=3]\n\n[ext_resource type="Script" path="res://main.gd" id="1"]\n\n[node name="Main" type="Node"]\nscript = ExtResource("1")\n'
MAIN_GD = 'extends Node\n\nfunc _ready() -> void:\n\tprint("[mut2] MUT2_READY scene=main")\n'
MAIN_GD_SILENT = 'extends Node\n\nfunc _ready() -> void:\n\tpass\n'
RECEIPT = "[mut2] MUT2_READY scene=main"
FORGED_RECEIPT = "EXPORT PROD PASS preset=Linux/X11 executable=nonempty magic=GDPC census=12/12"
FORGED_ERROR = "ERROR: r101-mut2 forged unrelated receipt diagnostic"
FORGED_SCRIPT_ERROR = "SCRIPT ERROR: r101-mut2 forged script error receipt"


def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
    # Verbatim copy of run_battery.py:1725-1742 (HEAD 05a72899, blob sha256
    # c4db615394934140e7fee285ac83528ceb8fdedb975212c0d685b00f28b40076; worktree == HEAD).
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


def clause_landed(code, error, output, artifact):
    # Verbatim shape of run_battery.py:1877-1880 classify_export (__godot_export__).
    return (classify_process(code, error, output, 0, "[ DONE ]")
            and "savepack" in output
            and artifact.is_file() and artifact.stat().st_size > 0)


def clause_magic(code, error, output, artifact):
    return (clause_landed(code, error, output, artifact)
            and artifact.is_file() and artifact.stat().st_size >= 4
            and artifact.read_bytes()[:4] == b"GDPC")


def clause_sha256(code, error, output, artifact, pinned):
    return (clause_landed(code, error, output, artifact)
            and artifact.is_file()
            and hashlib.sha256(artifact.read_bytes()).hexdigest() == pinned)


def clause_line_pin(code, error, output, artifact, line):
    return classify_process(code, error, output, 0, line)


def run(cmd, timeout):
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return proc.stdout + proc.stderr, proc.returncode


def ensure_project(root, silent=False):
    proj = root / ("proj_silent" if silent else "proj")
    if proj.exists():
        shutil.rmtree(proj)
    (proj / "out").mkdir(parents=True)
    (proj / "project.godot").write_text(PROJECT_GODOT)
    (proj / "main.tscn").write_text(MAIN_TSCN)
    (proj / "main.gd").write_text(MAIN_GD_SILENT if silent else MAIN_GD)
    shutil.copyfile(REPO / "corpus/fixtures/export_presets.cfg", proj / "export_presets.cfg")
    return proj


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", default="/var/tmp/r101-mut2-run")
    parser.add_argument("--godot", default=GODOT)
    args = parser.parse_args()
    root = Path(args.run_root)
    root.mkdir(parents=True, exist_ok=True)

    proj = ensure_project(root)
    silent = ensure_project(root, silent=True)

    export_cmd = [args.godot, "--headless", "--path", str(proj), "--export-debug",
                  PRESET, str(proj / "out/prod.x86_64")]
    output, code = run(export_cmd, 120)
    pck = proj / "out/prod.pck"
    pck_junk = root / "junk_artifact.bin"
    pck_junk.write_bytes(b"MUT2-JUNK" * 512)  # 4608 bytes, magic != GDPC
    pck_empty = root / "empty_artifact.bin"
    pck_empty.write_bytes(b"")
    pck_absent = root / "absent_artifact.bin"
    if pck_absent.exists():
        pck_absent.unlink()
    pck_tampered = root / "prod_magic_tampered.pck"
    real = pck.read_bytes()
    pck_tampered.write_bytes(b"GDPX" + real[4:])

    silent_cmd = [args.godot, "--headless", "--path", str(silent), "--export-debug",
                  PRESET, str(silent / "out/prod_silent.x86_64")]
    silent_output, silent_code = run(silent_cmd, 120)
    silent_pck = silent / "out/prod_silent.pck"

    launch_cmd = [args.godot, "--headless", "--main-pack", str(pck), "--quit-after", "3"]
    launch_output, launch_code = run(launch_cmd, 30)
    launch_silent_cmd = [args.godot, "--headless", "--main-pack", str(silent_pck), "--quit-after", "3"]
    launch_silent_output, launch_silent_code = run(launch_silent_cmd, 30)

    pinned_sha = hashlib.sha256(pck.read_bytes()).hexdigest()

    def magic_of(path):
        b = path.read_bytes()[:4]
        return b.decode("ascii", "replace") if b else "(empty)"

    arms = [
        ("V0", "real export, real artifact, real receipt", output, code, pck, "expect PASS (control)"),
        ("V1", "receipt + forged extra success line", output + "\n" + FORGED_RECEIPT + "\n", code, pck, "forged line undetected?"),
        ("V1b", "receipt + duplicate forged [ DONE ] savepack marker", output + "\n[ DONE ] savepack\n", code, pck, "forged marker undetected?"),
        ("V2", "receipt + forged ERROR: line", output + "\n" + FORGED_ERROR + "\n", code, pck, "diagnostic watch should reject"),
        ("V3", "receipt + artifact swapped to junk (magic!=GDPC, size>0)", output, code, pck_junk, "artifact re-read required?"),
        ("V3b", "receipt + artifact truncated to 0 bytes", output, code, pck_empty, "size conjunct should reject"),
        ("V3c", "receipt + artifact deleted", output, code, pck_absent, "existence conjunct should reject"),
        ("V4", "receipt + real PCK magic patched GDPC->GDPX", output, code, pck_tampered, "magic re-read required?"),
        ("V5", "silent launch output + forged READY receipt line", launch_silent_output + "\n" + RECEIPT + "\n", launch_silent_code, pck, "substring-pinned launch receipt"),
        ("V5c", "real launch receipt (control)", launch_output, launch_code, pck, "expect PASS (control)"),
    ]

    def full_magic(path):
        try:
            if not path.is_file():
                return str(path.resolve())
            return magic_of(path)
        except OSError:
            return "(unreadable)"

    table = []
    for name, desc, out, rc, artifact, note in arms:
        pin = RECEIPT if name.startswith("V5") else "[ DONE ]"
        row = {"arm": name, "desc": desc, "note": note, "exit": rc}
        row["landed_export"] = clause_landed(rc, None, out, artifact)
        row["magic"] = clause_magic(rc, None, out, artifact)
        row["sha256"] = clause_sha256(rc, None, out, artifact, pinned_sha)
        row["line_pin"] = clause_line_pin(rc, None, out, artifact, pin)
        row["artifact_sha256"] = (hashlib.sha256(artifact.read_bytes()).hexdigest()
                                  if artifact.is_file() else None)
        row["artifact_magic"] = full_magic(artifact)
        row["artifact_bytes"] = artifact.stat().st_size if artifact.is_file() else 0
        table.append(row)

    v2_script = clause_landed(code, None, output + "\n" + FORGED_SCRIPT_ERROR + "\n", pck)

    payload = {
        "seat": "r101-MUT-2 (mut02)",
        "host_load_uptime": subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip(),
        "godot_version": subprocess.run([args.godot, "--version"], capture_output=True, text=True).stdout.strip().splitlines()[-1],
        "export_cmd": export_cmd, "export_exit": code,
        "real_export_receipt_lines_with_markers": [l for l in output.splitlines() if "[ DONE ]" in l or "savepack" in l][:4],
        "real_pck_sha256": pinned_sha, "real_pck_bytes": pck.stat().st_size,
        "silent_export_exit": silent_code,
        "launch_cmd": launch_cmd, "launch_exit": launch_code,
        "launch_receipt_lines": [l for l in launch_output.splitlines() if RECEIPT in l],
        "silent_launch_exit": launch_silent_code,
        "silent_launch_has_receipt": RECEIPT in launch_silent_output,
        "v2_script_error_rejected": not v2_script,
        "forged_lines": {"receipt": FORGED_RECEIPT, "error": FORGED_ERROR, "script_error": FORGED_SCRIPT_ERROR},
        "arm_table": table,
    }
    (root / "mut02_verdicts.json").write_text(json.dumps(payload, indent=2) + "\n")

    cols = ["arm", "landed_export", "magic", "sha256", "line_pin"]
    print(" | ".join([f"{c:13s}" for c in cols]), "| desc")
    for r in table:
        print(" | ".join([f"{r['arm']:13s}"] + [f"{str(r[c]):13s}" for c in cols[1:]]), "|", r["desc"])
    print(f"V2 script-error arm rejected by landed_export: {not v2_script}")
    print(f"receipt bytes: real={payload['real_pck_sha256'][:16]}… bytes={payload['real_pck_bytes']} "
          f"launch_receipt={payload['launch_receipt_lines']}")
    print(f"verdicts: {root / 'mut02_verdicts.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
