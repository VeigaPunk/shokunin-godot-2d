#!/usr/bin/env python3
"""MUT-3 stage 3: dead measure applied to the real C1 lattice harness
`corpus/fixtures/export_prod.gd` (`base` arm).

The `base` arm builds a prod project, exports prod.pck, parses the pack table and
emits 13 receipt items (magic, entry_count, names_sha256, sizes, counts, bytes).
Mutation: the readback/parse slice (existence check + `_census_pck` + `_it`
items) is replaced by the same `_it` calls with golden constants — the artifact
is never read.  Variants, all in /tmp/r101-mut03/proj, run as
`godot --headless --path <proj> --script res://<name>.gd -- --arm=base`:

  lattice_pristine         landed source, golden capture, honest env.
  lattice_control_tampered landed source + magic-byte flip after export.
  lattice_dead_tampered    dead measure + same magic flip.

Model: pristine PASS (golden); control rc=1 FAIL (tamper detected); dead rc=0
with a PASS line byte-identical to pristine even though the pack magic is
corrupted; an independent Python recompute (first 4 bytes != GDPC) is the only
arm that still detects it.

Usage: python3 mut03_lattice_dead_measure.py     (exit 0 = model matched)
Scratch only; reads corpus/fixtures/export_prod.gd, never edits it.
"""
import hashlib
import os
import pathlib
import re
import shlex
import subprocess
import sys

GODOT = "/usr/bin/godot"
ROOT = pathlib.Path("/tmp/r101-mut03")
PROJ = ROOT / "proj"
EVID = ROOT / "evidence"
LROOT = ROOT / "lattice"
SRC = pathlib.Path("corpus/fixtures/export_prod.gd")

EXPORT_LINE = '\tvar code := _export("prod", "pack", pck, "")\n'
SLICE_START = '\tif not FileAccess.file_exists(pck):\n\t\t_fail("pack_missing")\n'
SLICE_END = '\t_it("bytes", _file_size(pck))\n'
TAMPER = (
    "\t# mut03 tamper injection (negative environment: corrupt the pack magic)\n"
    "\tvar _tam := FileAccess.get_file_as_bytes(pck)\n"
    "\tif _tam.size() >= 4:\n"
    "\t\t_tam[0] = _tam[0] ^ 0xFF\n"
    "\t\tvar _tw := FileAccess.open(pck, FileAccess.WRITE)\n"
    "\t\t_tw.store_buffer(_tam)\n"
    "\t\t_tw.close()\n"
)
PASS_RE = re.compile(r"^PASS export_prod base (?P<items>.+)$")
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def write_variant(name, text):
    (PROJ / f"{name}.gd").write_text(text)
    (EVID / f"{name}.gd").write_text(text)


def run_arm(name):
    env = os.environ.copy()
    env["EXPORT_PROD_ROOT"] = str(LROOT)
    cmd = [GODOT, "--headless", "--path", str(PROJ), "--script", f"res://{name}.gd", "--", "--arm=base"]
    print("MUT03-LAT CMD " + shlex.join(cmd))
    proc = subprocess.run(cmd, capture_output=True, timeout=120, env=env)
    out, err = proc.stdout, proc.stderr
    (EVID / f"{name}.stdout.txt").write_bytes(out)
    (EVID / f"{name}.stderr.txt").write_bytes(err)
    text = ANSI_RE.sub("", (out + b"\n" + err).decode("utf-8", "replace"))
    pass_line = next((ln for ln in text.splitlines() if ln.startswith("PASS export_prod base ")), "")
    fail_line = next((ln for ln in text.splitlines() if ln.startswith("FAIL export_prod base ")), "")
    print(f"MUT03-LAT RUN {name} rc={proc.returncode} stdout_sha={hashlib.sha256(out).hexdigest()} "
          f"stderr_bytes={len(err)}")
    print(f"MUT03-LAT RECEIPT {name} {pass_line or fail_line}")
    return {"rc": proc.returncode, "pass_line": pass_line, "fail_line": fail_line,
            "stdout_sha": hashlib.sha256(out).hexdigest()}


def golden_block(pass_line):
    items = pass_line[len("PASS export_prod base "):].split()
    lines = ["\t# mut03 dead measure: receipt kept, artifact never read back"]
    for item in items:
        key, _, value = item.partition("=")
        if value in ("true", "false"):
            lit = value
        elif re.fullmatch(r"-?\d+", value):
            lit = value
        else:
            lit = f'"{value}"'
        lines.append(f'\t_it("{key}", {lit})')
    return "\n".join(lines) + "\n"


def pck_magic(path):
    if not path.is_file():
        return None
    return path.read_bytes()[:4]


def main():
    EVID.mkdir(parents=True, exist_ok=True)
    LROOT.mkdir(parents=True, exist_ok=True)
    src = SRC.read_text()
    print(f"MUT03-LAT SOURCE {SRC} bytes={len(src.encode())} sha256={hashlib.sha256(src.encode()).hexdigest()}")
    arm_start = src.index("func _arm_base() -> void:\n")
    arm_end = src.index("\nfunc _arm_zip() -> void:", arm_start)
    arm_base = src[arm_start:arm_end]
    assert arm_base.count(EXPORT_LINE) == 1
    assert arm_base.count(SLICE_START) == 1 and arm_base.count(SLICE_END) == 1
    a = arm_base.index(SLICE_START)
    b = arm_base.index(SLICE_END, a) + len(SLICE_END)
    assert a < b

    write_variant("lattice_pristine", src)
    p = run_arm("lattice_pristine")
    if not p["pass_line"]:
        print("MUT03-LAT FAIL pristine produced no PASS line; aborting")
        return 1

    control_arm = arm_base.replace(EXPORT_LINE, EXPORT_LINE + TAMPER, 1)
    dead_arm = arm_base[:a] + golden_block(p["pass_line"]) + arm_base[b:]
    dead_arm = dead_arm.replace(EXPORT_LINE, EXPORT_LINE + TAMPER, 1)
    assert "FileAccess.file_exists(pck)" not in dead_arm and "_census_pck(pck)" not in dead_arm
    control = src[:arm_start] + control_arm + src[arm_end:]
    dead = src[:arm_start] + dead_arm + src[arm_end:]
    write_variant("lattice_control_tampered", control)
    write_variant("lattice_dead_tampered", dead)

    c = run_arm("lattice_control_tampered")
    d = run_arm("lattice_dead_tampered")

    pck = LROOT / "prod" / "out" / "prod.pck"
    magic = pck_magic(pck)
    recompute_kills = magic is not None and magic != b"GDPC"
    control_detected = c["rc"] == 1 and c["fail_line"] != ""
    dead_survives = d["rc"] == 0 and d["pass_line"] == p["pass_line"]

    print(f"MUT03-LAT MODEL control_detects_tamper={control_detected} dead_survives_on_tampered={dead_survives} "
          f"dead_receipt_equals_pristine={d['pass_line'] == p['pass_line']} "
          f"artifact_magic_after_dead_run={magic!r} independent_recompute_detects_tamper={recompute_kills}")
    ok = control_detected and dead_survives and recompute_kills
    print("MUT03-LAT " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
