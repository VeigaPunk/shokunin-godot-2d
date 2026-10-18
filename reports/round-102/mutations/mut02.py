#!/usr/bin/env python3
"""r102 M2 / mut02: refusal-class spoof mutation for the export_launch matrix.

Spoof shape (the seat's target): a launch that ACTUALLY SUCCEEDED (rc=0, success
marker on stdout, embedded self-contained binary doing the real work) but whose
stderr carries a foreign line that mimics the stock-template `--main-pack`
refusal verbatim. A refusal-class classifier must REJECT this artifact from the
refusal class (anchor rc / stdout), not be fooled by stderr text.

Arms (all run for real, streams captured separately):
  A_genuine_refusal : stock (non-embed) template binary + --main-pack <pck>
  B_genuine_success : embedded (embed_pck=true) self-contained binary
  C_spoof           : wrapper: refusal line -> stderr, then exec embedded binary
                      (launch succeeds; foreign stderr mimic present)
  D_shallow_refusal : wrapper: refusal line -> stderr, exit 1 (no engine banner)

Clause matrix (each a direct-execution replica over the captured bytes):
  weak_merged    : refusal_substr in stdout+stderr                     -> refusal
  weak_stderr    : refusal_substr in stderr                            -> refusal
  rc_anchored    : rc==1 and refusal_substr in merged                  -> refusal
  rc_marker      : refusal iff rc==1 and no marker on stdout; success
                   iff rc==0 and marker count==1                       -> refusal/success
  rc_banner      : rc==1 and refusal and engine banner on stdout       -> refusal

Never runs run_battery.py; scratch-only under /var/tmp/r102-mut2/.
Writes /var/tmp/r102-mut2/out/mut02_verdicts.json (evidence) and prints it.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/var/tmp/r102-mut2")
PROJ = ROOT / "proj"
OUT = PROJ / "out"
VERD = ROOT / "out"
GODOT = "/usr/bin/godot"

MARKER = "EXPORT_LAUNCH_READY scene=fixture"
REFUSAL_SUBSTR = "compiled without support for path overrides"
# Verbatim bytes as measured from the stock template binary (backticks included;
# r101 prose dropped them -- this is the byte-exact form).
REFUSAL_LINE = ("ERROR: `--main-pack` was specified on the command line, but this Godot "
                "binary was compiled without support for path overrides. Aborting.")
REFUSAL_HINT = ("To be able to use it, use the `disable_path_overrides=no` SCons option "
                "when compiling Godot.")

PROJECT_GODOT = """config_version=5

[application]

config/name="R102Mut2Launch"
run/main_scene="res://main.tscn"
config/features=PackedStringArray("4.7")

[display]

window/size/viewport_width=320
window/size/viewport_height=180
"""

MAIN_GD = f'''extends Node


func _ready() -> void:
	print("{MARKER}")
	get_tree().quit()
'''

MAIN_TSCN = ('[gd_scene load_steps=2 format=3]\n\n'
             '[ext_resource type="Script" path="res://main.gd" id="1"]\n\n'
             '[node name="Main" type="Node"]\nscript = ExtResource("1")\n')

# Two presets in one file: stock (non-embed) and embedded.
EXPORT_PRESETS = """[preset.0]

name="Linux/X11"
platform="Linux/X11"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path=""
patches=PackedStringArray()
encryption_include_filters=""
encryption_exclude_filters=""
seed=0
encrypt_pck=false
encrypt_directory=false
script_export_mode=2

[preset.0.options]

custom_template/debug=""
custom_template/release=""
debug/export_console_wrapper=1
binary_format/embed_pck=false
texture_format/s3tc_bptc=true
texture_format/etc2_astc=false

[preset.1]

name="Linux/X11 Embed"
platform="Linux/X11"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path=""
patches=PackedStringArray()
encryption_include_filters=""
encryption_exclude_filters=""
seed=0
encrypt_pck=false
encrypt_directory=false
script_export_mode=2

[preset.1.options]

custom_template/debug=""
custom_template/release=""
debug/export_console_wrapper=1
binary_format/embed_pck=true
texture_format/s3tc_bptc=true
"""


def run(cmd, cwd=None, timeout=120):
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return {
        "command": [str(c) for c in cmd],
        "cwd": str(cwd) if cwd else None,
        "exit": proc.returncode,
        "wall_ms": round((time.time() - t0) * 1000),
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def sha256_file(p: Path):
    if not p.is_file():
        return None, 0
    b = p.read_bytes()
    return hashlib.sha256(b).hexdigest(), len(b)


def refusal_clauses(rec, marker=MARKER, substr=REFUSAL_SUBSTR):
    merged = rec["stdout"] + rec["stderr"]
    weak_merged = substr in merged
    weak_stderr = substr in rec["stderr"]
    rc_anchored = (rec["exit"] == 1 and substr in merged)
    marker_n = sum(1 for line in rec["stdout"].splitlines() if line.strip() == marker)
    banner = "4.7.2" in rec["stdout"]
    if rec["exit"] == 1 and substr in merged and marker_n == 0:
        rc_marker = "refusal"
    elif rec["exit"] == 0 and marker_n == 1:
        rc_marker = "success"
    else:
        rc_marker = "neither"
    rc_empty = bool(rec["exit"] == 1 and rec["stdout"] == "" and substr in rec["stderr"])
    return {
        "weak_merged_refusal": weak_merged,
        "weak_stderr_refusal": weak_stderr,
        "rc_anchored_refusal": rc_anchored,
        "rc_marker_class": rc_marker,
        "rc_empty_stdout_refusal": rc_empty,
        "marker_lines_on_stdout": marker_n,
        "banner_on_stdout": banner,
    }


def main():
    if ROOT.exists():
        shutil.rmtree(ROOT)
    PROJ.mkdir(parents=True)
    OUT.mkdir(parents=True)
    VERD.mkdir(parents=True)

    (PROJ / "project.godot").write_text(PROJECT_GODOT)
    (PROJ / "main.gd").write_text(MAIN_GD)
    (PROJ / "main.tscn").write_text(MAIN_TSCN)
    (PROJ / "export_presets.cfg").write_text(EXPORT_PRESETS)

    evidence = {
        "seat": "r102-mut2",
        "scratch": str(ROOT),
        "godot": GODOT,
        "uptime_at_start": subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip(),
        "godot_version": subprocess.run([GODOT, "--version"], capture_output=True, text=True).stdout.strip(),
        "arms": {},
        "clauses": {},
    }

    # Import first (cold-export anomaly law: first export of an unimported
    # project is corrupt; warm-warm only).
    imp = run([GODOT, "--headless", "--path", str(PROJ), "--import"], timeout=180)
    evidence["import"] = {k: imp[k] for k in ("command", "exit", "wall_ms")}

    stock_bin = (OUT / "stock.x86_64").resolve()
    embed_bin = (OUT / "embed.x86_64").resolve()
    exports = {}
    for label, preset, dest in (("stock", "Linux/X11", stock_bin),
                                ("embed", "Linux/X11 Embed", embed_bin)):
        # export twice: second pass is the warm-warm receipt (law from r101)
        for rep in (1, 2):
            r = run([GODOT, "--headless", "--path", str(PROJ),
                     "--export-release", preset, str(dest)], timeout=180)
            exports[f"{label}_rep{rep}"] = {k: r[k] for k in ("command", "exit", "wall_ms")}
            exports[f"{label}_rep{rep}"]["done"] = "[ DONE ]" in r["stdout"] + r["stderr"]
    evidence["exports"] = exports
    stock_pck = (OUT / "stock.pck").resolve()
    evidence["artifacts"] = {
        "stock_bin": {"path": str(stock_bin)} | dict(zip(("sha256", "bytes"), sha256_file(stock_bin))),
        "stock_pck": {"path": str(stock_pck)} | dict(zip(("sha256", "bytes"), sha256_file(stock_pck))),
        "embed_bin": {"path": str(embed_bin)} | dict(zip(("sha256", "bytes"), sha256_file(embed_bin))),
        "sidecar_pck_for_embed": (OUT / "embed.pck").exists(),
    }

    # Arm A: genuine refusal — stock template binary + --main-pack.
    armA = run([str(stock_bin), "--headless", "--main-pack", str(stock_pck),
                "--quit-after", "5"], cwd=str(OUT), timeout=30)

    # Arm B: genuine success — embedded self-contained binary.
    armB = run([str(embed_bin), "--headless", "--quit-after", "5"], cwd=str(OUT), timeout=30)

    # Arm C: the spoof — refusal line to stderr, then exec the real embedded
    # binary; the launch itself succeeds. `exec` keeps rc/stdout of the real run.
    spoof = OUT / "spoof.sh"
    spoof.write_text(
        "#!/bin/sh\n"
        f"printf '%s\\n' '{REFUSAL_LINE}' >&2\n"
        f"printf '%s\\n' '{REFUSAL_HINT}' >&2\n"
        f'exec "$(dirname "$0")/embed.x86_64" --headless --quit-after 5\n')
    spoof.chmod(0o755)
    armC = run([str(spoof)], cwd=str(OUT), timeout=30)

    # Arm D: shallow refusal — the same verbatim two-line stderr block, rc=1,
    # empty stdout, no engine work.
    shallow = OUT / "shallow.sh"
    shallow.write_text(
        "#!/bin/sh\n"
        f"printf '%s\\n' '{REFUSAL_LINE}' >&2\n"
        f"printf '%s\\n' '{REFUSAL_HINT}' >&2\n"
        "exit 1\n")
    shallow.chmod(0o755)
    armD = run([str(shallow)], cwd=str(OUT), timeout=30)

    for label, rec in (("A_genuine_refusal", armA), ("B_genuine_success", armB),
                       ("C_spoof", armC), ("D_shallow_refusal", armD)):
        evidence["arms"][label] = {
            "command": rec["command"],
            "exit": rec["exit"],
            "wall_ms": rec["wall_ms"],
            "stdout_lines": rec["stdout"].strip().splitlines(),
            "stderr_lines": rec["stderr"].strip().splitlines(),
            "stdout_sha256": hashlib.sha256(rec["stdout"].encode()).hexdigest(),
            "stderr_sha256": hashlib.sha256(rec["stderr"].encode()).hexdigest(),
        }
        evidence["clauses"][label] = refusal_clauses(rec)

    # Verbatim-block comparison: genuine refusal block vs the spoof's two-line
    # prefix (byte-exact, backticks included).
    genuine_block = [l.rstrip() for l in armA["stderr"].rstrip("\n").split("\n")]
    spoof_block = [l.rstrip() for l in armC["stderr"].rstrip("\n").split("\n")]
    genuine_ref_line = next((l.strip() for l in armA["stderr"].splitlines()
                             if REFUSAL_SUBSTR in l), None)
    spoof_ref_line = next((l.strip() for l in armC["stderr"].splitlines()
                           if REFUSAL_SUBSTR in l), None)
    evidence["foreign_line_byte_identity"] = {
        "genuine_refusal_line": genuine_ref_line,
        "spoof_stderr_line": spoof_ref_line,
        "byte_identical": genuine_ref_line == spoof_ref_line and genuine_ref_line is not None,
    }
    evidence["foreign_block_prefix_byte_identity"] = {
        "genuine_block_prefix": genuine_block[:2],
        "spoof_block": spoof_block,
        "prefix_byte_identical": spoof_block == genuine_block[:2],
    }
    evidence["refusal_block_lines"] = genuine_block
    # Exact-block clause: rc=1, empty stdout, stderr == genuine block byte-for-byte.
    for label, rec in (("A_genuine_refusal", armA), ("B_genuine_success", armB),
                       ("C_spoof", armC), ("D_shallow_refusal", armD)):
        block = ([l.rstrip() for l in rec["stderr"].rstrip("\n").split("\n")]
                 if rec["stderr"] else [])
        evidence["clauses"][label]["exact_block_refusal"] = bool(
            rec["exit"] == 1 and rec["stdout"] == "" and block == genuine_block)

    # Battery-row-level replicas: r102-era classify_process over merged output.
    def classify_process(code, error, output, expected_exit, signature):
        return (code == expected_exit and error is None and signature in output
                and "SCRIPT ERROR:" not in output and "Parse Error:" not in output)

    # classify_streams replica (r89-fold): signature on stdout, stderr must be empty/allowed.
    def classify_streams(code, error, stdout, stderr, expected_exit, signature):
        if code != expected_exit or error is not None or signature not in stdout:
            return False
        return not stderr.strip()

    row_replica = {}
    for label, rec in (("A_genuine_refusal", armA), ("B_genuine_success", armB),
                       ("C_spoof", armC), ("D_shallow_refusal", armD)):
        merged = rec["stdout"] + rec["stderr"]
        row_replica[label] = {
            "row_expect_exit0_marker_merged": classify_process(rec["exit"], None, merged, 0, MARKER),
            "row_expect_exit0_marker_streams": classify_streams(rec["exit"], None, rec["stdout"], rec["stderr"], 0, MARKER),
            "row_expect_exit1_refusal_merged": classify_process(rec["exit"], None, merged, 1, REFUSAL_SUBSTR),
            "row_expect_exit1_refusal_streams": classify_streams(rec["exit"], None, rec["stdout"], rec["stderr"], 1, REFUSAL_SUBSTR),
        }
    evidence["row_level_replicas"] = row_replica

    # In-engine stage: replicate the export_prod.gd arm idiom (SceneTree +
    # OS.execute with `exec > log 2>&1` redirection) against the same arms, so
    # the spoof is exercised at the layer export_launch.gd will classify from.
    probe_gd = '''extends SceneTree

const REFUSAL := "compiled without support for path overrides"
const MARKER := "EXPORT_LAUNCH_READY scene=fixture"

var arm := "genuine"


func _initialize() -> void:
\tfor a in OS.get_cmdline_user_args():
\t\tif a.begins_with("--arm="):
\t\t\tarm = a.trim_prefix("--arm=")
\trun_arm()
\tquit(0)


func _q(s: String) -> String:
\treturn "'" + s.replace("'", "'\\\\''") + "'"


func run_arm() -> void:
\tvar out_dir := "@OUT@"
\tvar log_path := out_dir.path_join("probe_" + arm + ".log")
\tvar body := ""
\tif arm == "genuine":
\t\tbody = "cd " + _q(out_dir) + "\\n" + _q("@STOCK_BIN@") + " --headless --main-pack " + _q("@STOCK_PCK@") + " --quit-after 5"
\telse:
\t\tbody = "cd " + _q(out_dir) + "\\n" + _q("@SPOOF@")
\tvar code := OS.execute("/usr/bin/sh", PackedStringArray(["-c", "exec > " + _q(log_path) + " 2>&1\\n" + body]))
\tvar log_text := FileAccess.get_file_as_string(log_path)
\tvar refusal_seen := log_text.contains(REFUSAL)
\tvar marker_seen := log_text.contains(MARKER)
\tvar text_only := refusal_seen
\tvar rc_anchored := code == 1 and refusal_seen
\tvar rc_marker := "neither"
\tif code == 1 and not marker_seen and refusal_seen:
\t\trc_marker = "refusal"
\telif code == 0 and marker_seen:
\t\trc_marker = "success"
\tvar exact_block_ok := code == 1 and log_text.begins_with("ERROR: `--main-pack` was specified on the command line, but this Godot binary was compiled without support for path overrides. Aborting.\\nTo be able to use it, use the `disable_path_overrides=no` SCons option when compiling Godot.\\n")
\tprint("ROW arm=%s nested_exit=%d refusal_seen=%s marker_seen=%s" % [arm, code, str(refusal_seen), str(marker_seen)])
\tprint("CLASS arm=%s text_only=%s rc_anchored=%s rc_marker=%s exact_block=%s" % [arm, str(text_only), str(rc_anchored), rc_marker, str(exact_block_ok)])
\tif text_only:
\t\tprint("FIXTURE_STYLE arm=%s naive_text_pass=true anchored_pass=%s" % [arm, str(rc_anchored)])
\tprint("PROBE_DONE arm=%s" % arm)
'''
    probe = PROJ / "probe.gd"
    probe.write_text(probe_gd.replace("@STOCK_BIN@", str(stock_bin))
                             .replace("@STOCK_PCK@", str(stock_pck))
                             .replace("@SPOOF@", str(spoof))
                             .replace("@OUT@", str(OUT)))
    evidence["in_engine_probe"] = {}
    for arm_arg in ("genuine", "spoof"):
        r = run([GODOT, "--headless", "--path", str(PROJ), "--script",
                 "res://probe.gd", "--", "--arm=" + arm_arg], timeout=60)
        evidence["in_engine_probe"][arm_arg] = {
            "command": r["command"],
            "exit": r["exit"],
            "wall_ms": r["wall_ms"],
            "stdout_lines": r["stdout"].strip().splitlines(),
            "stderr_lines": r["stderr"].strip().splitlines()[:6],
        }

    payload = json.dumps(evidence, indent=1)
    (VERD / "mut02_verdicts.json").write_text(payload + "\n")
    print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
