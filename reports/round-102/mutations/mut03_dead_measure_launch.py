#!/usr/bin/env python3
"""mut03 — dead measure on an export_launch row: skip the real export, echo the receipt.

Builds a scratch host project under /var/tmp/r102-mut3/proj, runs an honest
embedded-binary launch fixture twice (warm determinism), bakes the measured
receipt into a dead-measure variant that performs NO export and NO launch,
then evaluates the acceptance predicates modelled from the battery:

  P1 receipt pin   — classify_process semantics (run_battery.py:1775):
                     rc==0, signature substring present, no unexpected
                     "ERROR:" lines, no SCRIPT ERROR/Parse Error.
  P2 artifact      — pinned embedded binary exists, size>0, ELF magic.
                     Model: run_battery.py probe_export_launch checks
                     (4534-4562: executable.is_file() and size>0).
  P3 recompute     — sha256/size read from the artifact bytes equal the
                     receipt fields (independent readback).
  P4 empty-pre    — out dir empty before the run AND P2 after
                     (probe_export_launch asserts out dir empty pre-export).

Never runs run_battery.py. Commands printed verbatim; evidence under
/var/tmp/r102-mut3/evidence/.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

GODOT = "/usr/bin/godot"
ROOT = Path(os.environ.get("MUT03_ROOT", "/var/tmp/r102-mut3"))
EVIDENCE = ROOT / "evidence"
HOST_PROJ = ROOT / "proj"
RECEIPT_PREFIX = "PASS export_launch_mut03 embed=true"

HOST_PROJECT_GODOT = """config_version=5

[application]

config/name="mut03-host"
config/features=PackedStringArray("4.7")
"""

HONEST_GD = r'''extends SceneTree
# Honest model of an embedded-binary export_launch fixture row: build nested
# project, export with embed_pck=true (private /tmp via unshare), launch the
# self-contained binary with --quit-after, print one deterministic receipt.

const PRESET := "Linux/X11"
const MARKER := "EXPORT_LAUNCH_READY scene=fixture"

const PROJECT_GODOT := "config_version=5\n\n[application]\n\nconfig/name=\"mut03-nproj\"\nconfig/features=PackedStringArray(\"4.7\")\nrun/main_scene=\"res://main.tscn\"\n"
const MAIN_GD := "extends Node\n\nfunc _ready() -> void:\n\tprint(\"EXPORT_LAUNCH_READY scene=fixture\")\n"
const MAIN_TSCN := "[gd_scene load_steps=2 format=3]\n\n[ext_resource type=\"Script\" path=\"res://main.gd\" id=\"1\"]\n\n[node name=\"Main\" type=\"Node\"]\nscript = ExtResource(\"1\")\n"
const PRESETS := "[preset.0]\n\nname=\"Linux/X11\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\ninclude_filter=\"\"\nexclude_filter=\"\"\nexport_path=\"\"\n\n[preset.0.options]\n\nbinary_format/architecture=\"x86_64\"\nbinary_format/embed_pck=true\n"

func _initialize() -> void:
	var root := OS.get_environment("MUT03_ROOT")
	if root.is_empty():
		root = "/var/tmp/r102-mut3"
	var variant := OS.get_environment("MUT03_VARIANT")
	if variant.is_empty():
		variant = "honest"
	var nproj := root + "/" + variant + "/nproj"
	var out_dir := root + "/" + variant + "/out"
	DirAccess.make_dir_recursive_absolute(nproj)
	DirAccess.make_dir_recursive_absolute(out_dir)
	_write(nproj + "/project.godot", PROJECT_GODOT)
	_write(nproj + "/main.gd", MAIN_GD)
	_write(nproj + "/main.tscn", MAIN_TSCN)
	_write(nproj + "/export_presets.cfg", PRESETS)
	var exe := out_dir + "/launch.x86_64"
	var inner := nproj + "/inner.sh"
	_write(inner, "mount -t tmpfs tmpfs /tmp || exit 91\ncd " + nproj + "\nexec " + OS.get_executable_path() + " --headless --path " + nproj + " --export-debug " + PRESET + " " + exe + "\n")
	var log := root + "/" + variant + "/export.log"
	var cmd := "exec > " + log + " 2>&1\nunshare -m --map-root-user /usr/bin/sh " + inner
	var export_rc := OS.execute("/usr/bin/sh", PackedStringArray(["-c", cmd]))
	var exe_bytes := -1
	var exe_sha := "none"
	if FileAccess.file_exists(exe):
		var buf := FileAccess.get_file_as_bytes(exe)
		exe_bytes = buf.size()
		var ctx := HashingContext.new()
		ctx.start(HashingContext.HASH_SHA256)
		ctx.update(buf)
		exe_sha = ctx.finish().hex_encode()
	var launch_rc := -1
	var marker_seen := false
	if export_rc == 0 and exe_bytes > 0:
		var lcmd := "cd " + out_dir + " && ./launch.x86_64 --headless --quit-after 3 > launch_stdout.txt 2>&1; echo $? > launch_rc.txt"
		OS.execute("/usr/bin/sh", PackedStringArray(["-c", lcmd]))
		if FileAccess.file_exists(out_dir + "/launch_rc.txt"):
			launch_rc = int(FileAccess.get_file_as_string(out_dir + "/launch_rc.txt").strip_edges())
		if FileAccess.file_exists(out_dir + "/launch_stdout.txt"):
			marker_seen = FileAccess.get_file_as_string(out_dir + "/launch_stdout.txt").contains(MARKER)
	var sidecar := FileAccess.file_exists(out_dir + "/launch.pck")
	print("PASS export_launch_mut03 embed=true export_rc=%d exe_bytes=%d exe_sha256=%s launch_rc=%d marker=%s quit_after=3 sidecar_pck=%s" % [export_rc, exe_bytes, exe_sha, launch_rc, str(marker_seen), str(sidecar)])
	if export_rc != 0 or exe_bytes <= 0 or launch_rc != 0 or not marker_seen:
		print("FAIL export_launch_mut03 diagnostics export_rc=%d exe_bytes=%d launch_rc=%d marker=%s" % [export_rc, exe_bytes, launch_rc, str(marker_seen)])
		quit(1)
		return
	quit(0)

func _write(path: String, text: String) -> void:
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string(text)
	f.close()
'''

DEAD_GD = r'''extends SceneTree
# Dead-measure variant of the export_launch fixture: performs NO export and
# NO launch. Prints the byte-exact receipt measured from the honest runs.

const RECEIPT := [@RECEIPT@]

func _initialize() -> void:
	for line in RECEIPT:
		print(line)
	quit(0)
'''


def run(cmd, env=None, timeout=300):
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=timeout)
    return proc, time.time() - t0


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def sha256_file(path: Path):
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest(), data


def receipt_lines(stdout: str):
    return [ln for ln in stdout.splitlines() if ln.startswith(RECEIPT_PREFIX)]


def classify_receipt(rc, stdout):
    """classify_process semantics for a script-fixture row (expected_exit=0)."""
    lines = stdout.splitlines()
    unrelated = [ln for ln in lines if "ERROR:" in ln]
    return (rc == 0 and RECEIPT_PREFIX in stdout and not unrelated
            and "SCRIPT ERROR:" not in stdout and "Parse Error:" not in stdout), unrelated


def evaluate(label, rc, stdout, out_dir: Path, pre_empty, golden_sha, golden_bytes,
             elapsed):
    p1, unrelated = classify_receipt(rc, stdout)
    exe = out_dir / "launch.x86_64"
    exists = exe.is_file()
    size = exe.stat().st_size if exists else 0
    elf = False
    sha = None
    if exists and size:
        sha, data = sha256_file(exe)
        elf = data[:4] == b"\x7fELF"
    p2 = bool(exists and size > 0 and elf)
    p3 = bool(p2 and sha == golden_sha and size == golden_bytes)
    p4 = bool(pre_empty and p2)
    return {
        "variant": label, "rc": rc, "elapsed_s": round(elapsed, 2),
        "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
        "receipt_lines": receipt_lines(stdout),
        "unrelated_error_lines": unrelated,
        "P1_receipt_pin": p1, "P2_artifact_elf": p2, "P3_recompute_sha": p3,
        "P4_empty_pre_and_artifact": p4,
        "artifact": {"exists": exists, "bytes": size, "elf": elf, "sha256": sha},
        "pre_out_empty": pre_empty,
    }


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    if ROOT.exists():
        for child in ROOT.iterdir():
            if child.name != "evidence":
                shutil.rmtree(child) if child.is_dir() else child.unlink()
    HOST_PROJ.mkdir(parents=True, exist_ok=True)
    write(HOST_PROJ / "project.godot", HOST_PROJECT_GODOT)
    write(HOST_PROJ / "launch_honest.gd", HONEST_GD)

    env = os.environ.copy()
    env["MUT03_ROOT"] = str(ROOT)
    results = []
    samples = []
    for label in ("cold", "warm_a", "warm_b"):
        variant = "honest"
        out_dir = ROOT / variant / "out"
        pre_empty = (not out_dir.exists()) or (not any(out_dir.iterdir()))
        cmd = [GODOT, "--headless", "--path", str(HOST_PROJ),
               "--script", "res://launch_honest.gd"]
        env_s = dict(env, MUT03_VARIANT=variant)
        print("CMD:", " ".join(cmd), "(MUT03_VARIANT=%s, sample=%s)" % (variant, label))
        proc, elapsed = run(cmd, env=env_s)
        print(proc.stdout)
        if proc.stderr.strip():
            print("STDERR:", proc.stderr.strip())
        (EVIDENCE / ("honest_" + label + ".stdout.txt")).write_text(proc.stdout)
        (EVIDENCE / ("honest_" + label + ".stderr.txt")).write_text(proc.stderr)
        rec = evaluate("honest_" + label, proc.returncode, proc.stdout, out_dir,
                       pre_empty, None, None, elapsed)
        results.append(rec)
        samples.append(rec)

    cold, warm_a, warm_b = samples
    golden_lines = warm_b["receipt_lines"]
    honest_ok = (all(s["P1_receipt_pin"] for s in samples)
                 and warm_a["receipt_lines"] == warm_b["receipt_lines"]
                 and warm_a["artifact"]["sha256"] == warm_b["artifact"]["sha256"]
                 and warm_a["artifact"]["bytes"] == warm_b["artifact"]["bytes"]
                 and warm_b["artifact"]["sha256"] is not None)
    if not golden_lines or not honest_ok:
        print("HONEST MODEL FAILED: receipts/artifacts not stable; aborting", file=sys.stderr)
        (EVIDENCE / "verdicts.json").write_text(json.dumps(
            {"honest_ok": honest_ok, "results": results}, indent=2) + "\n")
        return 1
    golden_sha = samples[-1]["artifact"]["sha256"]
    golden_bytes = samples[-1]["artifact"]["bytes"]
    print("GOLDEN receipt lines (%d), exe sha256=%s bytes=%d" %
          (len(golden_lines), golden_sha, golden_bytes))

    # Dead measure: no export, no launch, byte-exact receipt.
    baked = ",\n".join('"%s"' % ln.replace("\\", "\\\\").replace('"', '\\"')
                       for ln in golden_lines)
    write(HOST_PROJ / "launch_dead.gd", DEAD_GD.replace("@RECEIPT@", baked))

    for label, preseed in (("dead", False), ("dead_stale_artifact", True)):
        variant_dir = ROOT / label
        out_dir = variant_dir / "out"
        if preseed:
            # Copy the honest artifact to the pinned path BEFORE the dead run:
            # models an artifact left over from a previous invocation.
            out_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / "honest" / "out" / "launch.x86_64",
                         out_dir / "launch.x86_64")
        pre_empty = (not out_dir.exists()) or (not any(out_dir.iterdir()))
        cmd = [GODOT, "--headless", "--path", str(HOST_PROJ),
               "--script", "res://launch_dead.gd"]
        env_v = dict(env, MUT03_VARIANT=label)
        print("CMD:", " ".join(cmd), "(MUT03_VARIANT=%s)" % label)
        proc, elapsed = run(cmd, env=env_v)
        print(proc.stdout)
        if proc.stderr.strip():
            print("STDERR:", proc.stderr.strip())
        (EVIDENCE / (label + ".stdout.txt")).write_text(proc.stdout)
        (EVIDENCE / (label + ".stderr.txt")).write_text(proc.stderr)
        rec = evaluate(label, proc.returncode, proc.stdout, out_dir, pre_empty,
                       golden_sha, golden_bytes, elapsed)
        results.append(rec)

    # Wire the accepted predicates as they would sit at integration.
    by = {r["variant"]: r for r in results}
    dead = by["dead"]
    stale = by["dead_stale_artifact"]
    cells = {
        "receipt_only_P1": {"accepts_dead": dead["P1_receipt_pin"],
                            "accepts_dead_stale": stale["P1_receipt_pin"]},
        "artifact_P1_and_P2": {"accepts_dead": dead["P1_receipt_pin"] and dead["P2_artifact_elf"],
                               "accepts_dead_stale": stale["P1_receipt_pin"] and stale["P2_artifact_elf"]},
        "recompute_P1_and_P3": {"accepts_dead": dead["P1_receipt_pin"] and dead["P3_recompute_sha"],
                                "accepts_dead_stale": stale["P1_receipt_pin"] and stale["P3_recompute_sha"]},
        "empty_pre_P1_and_P4": {"accepts_dead": dead["P1_receipt_pin"] and dead["P4_empty_pre_and_artifact"],
                                "accepts_dead_stale": stale["P1_receipt_pin"] and stale["P4_empty_pre_and_artifact"]},
    }
    dead_bytes_equal = (hashlib.sha256(
        (EVIDENCE / "dead.stdout.txt").read_text().encode()).hexdigest()
        == warm_b["stdout_sha256"])
    verdict = {
        "model": "export_launch row, embedded binary (embed_pck=true), --quit-after 3",
        "golden_receipt_lines": golden_lines,
        "golden_exe_sha256": golden_sha,
        "golden_exe_bytes": golden_bytes,
        "dead_stdout_byte_identical_to_honest_s2": dead_bytes_equal,
        "acceptance_cells": cells,
        "results": results,
    }
    (EVIDENCE / "verdicts.json").write_text(json.dumps(verdict, indent=2) + "\n")
    print("\n=== acceptance cells (True = mutant accepted / survives) ===")
    for name, cell in cells.items():
        print("%-22s dead=%s dead_stale=%s" % (name, cell["accepts_dead"],
                                               cell["accepts_dead_stale"]))
    print("dead stdout byte-identical to honest_s2:", dead_bytes_equal)
    print("evidence:", EVIDENCE / "verdicts.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
