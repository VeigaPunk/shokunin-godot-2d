#!/usr/bin/env python3
"""mut03 retarget — dead measure vs the landed corpus/fixtures/export_launch_s02.gd.

Runs the REAL fixture (embed arm) under EXPORT_LAUNCH_ROOT on scratch, captures
its stdout, bakes a dead-measure variant that performs NO export and NO launch
(echoes the exact fixture-emitted lines, exit 0), then evaluates the same
acceptance cells as mut03_dead_measure_launch.py against the real artifact
(<root>/embed/out/s02.x86_64) and the real PASS receipt.

The corpus fixture is only ever READ (copied into scratch); sha256 stamped.
Never runs run_battery.py.
"""
import hashlib
import json
import shutil
import subprocess
import time
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FIXTURE = LANE / "corpus/fixtures/export_launch_s02.gd"
ROOT = Path("/var/tmp/r102-mut3/retarget_s02")
EVIDENCE = ROOT / "evidence"
GODOT = "/usr/bin/godot"
TEMPLATE = Path.home() / ".local/share/godot/export_templates/4.7.2.stable/linux_release.x86_64"
FIXTURE_LINE_PREFIXES = ("PASS ", "FAIL ", "EXPORT_LAUNCH_DIAG ")

DEAD_GD_TEMPLATE = r'''extends SceneTree
# Dead-measure retarget of export_launch_s02.gd: no export, no launch, echoes
# the exact fixture-emitted stdout lines of the honest run.

const LINES := [@LINES@]

func _initialize() -> void:
	for line in LINES:
		print(line)
	quit(0)
'''


def sha256_file(p: Path):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_fixture(tag, script_name, root, timeout=120):
    proj = ROOT / tag / "proj"
    proj.mkdir(parents=True, exist_ok=True)
    (proj / "project.godot").write_text(
        'config_version=5\n\n[application]\n\nconfig/name="mut03-retarget"\n'
        'config/features=PackedStringArray("4.7")\n')
    shutil.copy2(FIXTURE if script_name == "export_launch_s02.gd"
                 else ROOT / "dead_src" / script_name, proj / script_name)
    env = dict(**__import__("os").environ)
    env["EXPORT_LAUNCH_ROOT"] = str(root)
    cmd = [GODOT, "--headless", "--path", str(proj),
           "--script", "res://" + script_name, "--", "--arm=embed"]
    print("CMD: EXPORT_LAUNCH_ROOT=%s %s" % (root, " ".join(cmd)))
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=timeout)
    elapsed = time.time() - t0
    (EVIDENCE / (tag + ".stdout.txt")).write_text(proc.stdout)
    (EVIDENCE / (tag + ".stderr.txt")).write_text(proc.stderr)
    return proc, elapsed


def pck_recompute(exe: Path, template_bytes: int):
    """Independent readback of the s02 trailer contract from artifact bytes."""
    import struct
    out = {}
    if not exe.is_file():
        return {"exists": False}
    d = exe.read_bytes()
    size = len(d)
    out["exists"] = True
    out["bytes"] = size
    out["elf"] = d[:4] == b"\x7fELF"
    tail = d[-12:]
    out["trailer_magic"] = tail[8:12] == b"GDPC"
    pack_size = struct.unpack_from("<Q", tail, 0)[0] if len(tail) == 12 else 0
    out["pack_bytes"] = pack_size
    start = size - 12 - pack_size
    out["pck_start_magic"] = start > 0 and d[start:start + 4] == b"GDPC"
    out["size_consistent"] = size - 12 - pack_size == template_bytes
    return out


def receipt_fields(stdout):
    fields = {}
    for line in stdout.splitlines():
        if line.startswith("PASS export_launch s02 arm=embed"):
            for tok in line.split():
                if "=" in tok:
                    k, v = tok.split("=", 1)
                    fields[k] = v
    return fields


def evaluate(label, proc, elapsed, root: Path, pre_empty, template_bytes):
    stdout = proc.stdout
    lines = stdout.splitlines()
    unrelated = [ln for ln in lines if "ERROR:" in ln]
    p1 = (proc.returncode == 0
          and "PASS export_launch s02 arm=embed embed=true pck_sibling=false" in stdout
          and "trailer_gdpc=true" in stdout and "trailer_size_consistent=true" in stdout
          and "pack_magic_at_start=true" in stdout and "bin_gt_template=true" in stdout
          and "frames=[1,2,3,4,5]" in stdout and "extra=false" in stdout
          and "marker_lines=1" in stdout and "exit=0" in stdout
          and not unrelated and "SCRIPT ERROR:" not in stdout
          and "Parse Error:" not in stdout)
    exe = root / "embed" / "out" / "s02.x86_64"
    rb = pck_recompute(exe, template_bytes)
    fields = receipt_fields(stdout)
    p2 = bool(rb.get("exists") and rb.get("bytes", 0) > 0 and rb.get("elf"))
    p3 = bool(p2 and rb.get("trailer_magic") and rb.get("pck_start_magic")
              and rb.get("size_consistent")
              and fields.get("bin_bytes") == str(rb.get("bytes"))
              and fields.get("pack_bytes") == str(rb.get("pack_bytes")))
    p4 = bool(pre_empty and p3)
    return {"variant": label, "rc": proc.returncode, "elapsed_s": round(elapsed, 2),
            "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
            "receipt_fields": fields, "unrelated_error_lines": unrelated,
            "P1_receipt_pin": p1, "P2_artifact_elf": p2, "P3_recompute": p3,
            "P4_empty_pre_and_artifact": p4, "artifact": rb,
            "pre_out_empty": pre_empty}


def main():
    if ROOT.exists():
        shutil.rmtree(ROOT)
    EVIDENCE.mkdir(parents=True)
    src_sha = sha256_file(FIXTURE)
    src_text = FIXTURE.read_text()
    for anchor in ("func _arm_embed", "PASS export_launch s02 arm=",
                   "EXPORT_LAUNCH_ROOT", "s02.x86_64"):
        assert anchor in src_text, "fixture anchor missing: " + anchor
    print("fixture:", FIXTURE, "sha256:", src_sha)
    template_bytes = TEMPLATE.stat().st_size
    print("template:", TEMPLATE, "bytes:", template_bytes)

    results = []
    honest_root = ROOT / "scratch_honest"
    if honest_root.exists():
        shutil.rmtree(honest_root)
    pre = (not (honest_root / "embed").exists()) or not any((honest_root / "embed").iterdir())
    proc, elapsed = run_fixture("honest_embed", "export_launch_s02.gd", honest_root)
    print(proc.stdout)
    if proc.stderr.strip():
        print("STDERR:", proc.stderr.strip()[:400])
    honest = evaluate("honest_embed", proc, elapsed, honest_root, pre, template_bytes)
    results.append(honest)

    emitted = [ln for ln in proc.stdout.splitlines() if ln.startswith(FIXTURE_LINE_PREFIXES)]
    baked = ",\n".join('"%s"' % ln.replace("\\", "\\\\").replace('"', '\\"')
                       for ln in emitted)
    dead_src = ROOT / "dead_src"
    dead_src.mkdir(parents=True)
    (dead_src / "export_launch_s02_dead.gd").write_text(
        DEAD_GD_TEMPLATE.replace("@LINES@", baked))
    print("dead variant baked from %d fixture-emitted lines" % len(emitted))

    for label, root in (("dead_fresh", ROOT / "scratch_dead_fresh"),
                        ("dead_stale_artifact", honest_root)):
        if label == "dead_fresh" and root.exists():
            shutil.rmtree(root)
        pre = (not (root / "embed").exists()) or not any((root / "embed").iterdir())
        proc, elapsed = run_fixture(label, "export_launch_s02_dead.gd", root)
        print(proc.stdout)
        if proc.stderr.strip():
            print("STDERR:", proc.stderr.strip()[:400])
        rec = evaluate(label, proc, elapsed, root, pre, template_bytes)
        results.append(rec)

    by = {r["variant"]: r for r in results}
    dead, stale = by["dead_fresh"], by["dead_stale_artifact"]
    cells = {
        "receipt_only_P1": {"dead_fresh": dead["P1_receipt_pin"],
                            "dead_stale": stale["P1_receipt_pin"]},
        "P1_and_P2_artifact": {"dead_fresh": dead["P1_receipt_pin"] and dead["P2_artifact_elf"],
                               "dead_stale": stale["P1_receipt_pin"] and stale["P2_artifact_elf"]},
        "P1_and_P3_recompute": {"dead_fresh": dead["P1_receipt_pin"] and dead["P3_recompute"],
                                "dead_stale": stale["P1_receipt_pin"] and stale["P3_recompute"]},
        "P1_and_P4_empty_pre": {"dead_fresh": dead["P1_receipt_pin"] and dead["P4_empty_pre_and_artifact"],
                                "dead_stale": stale["P1_receipt_pin"] and stale["P4_empty_pre_and_artifact"]},
    }
    dead_identical = (by["dead_fresh"]["stdout_sha256"] == honest["stdout_sha256"]
                      or by["dead_stale_artifact"]["stdout_sha256"] == honest["stdout_sha256"])
    verdict = {"fixture_sha256": src_sha, "template_bytes": template_bytes,
               "dead_stdout_byte_identical_to_honest": dead_identical,
               "acceptance_cells": cells, "results": results}
    (EVIDENCE / "verdicts.json").write_text(json.dumps(verdict, indent=2) + "\n")
    print("=== acceptance cells (True = mutant accepted / survives) ===")
    for name, cell in cells.items():
        print("%-24s dead_fresh=%s dead_stale=%s" %
              (name, cell["dead_fresh"], cell["dead_stale"]))
    print("dead stdout byte-identical to honest:", dead_identical)
    print("evidence:", EVIDENCE / "verdicts.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
