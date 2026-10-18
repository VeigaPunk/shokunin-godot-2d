#!/usr/bin/env python3
"""MUT-3: dead measure on the C1 `export_prod` lattice (remove the real
measurement, keep the echo receipt).

Mutation: the measurement block of a C1-style PCK receipt probe (magic / size /
sha256 read back from the exported artifact) is replaced by hardcoded golden
constants.  The mutated probe keeps printing the identical receipt row, so on
the honest path it is byte-indistinguishable from the real one.  This script
measures which acceptance predicates can still tell the two apart:

  P1 receipt_only   substring pin of the golden receipt row (naive pin)
  P2 battery_shape  rc==0 + row signature + artifact exists + size>0
                    (shape of the `__godot_export__` classify in
                     corpus/fixtures/run_battery.py:1877-1880)
  P3 recompute      independent readback: artifact exists, magic==GDPC, and
                    the receipt values equal the bytes on disk

Expected (mutation-test model):
  honest path       live == dead (masked; every predicate PASS)
  tampered artifact P1/P2 FOOLED by dead; P3 kills
  missing artifact  P1 FOOLED by dead; P2 and P3 kill

Exit 0 when the observed matrix matches the model, 1 on divergence.

Usage: python3 mut03_dead_measure.py [--force-export]
Scratch only (/tmp/r101-mut03/).  Never touches corpus/fixtures or run_battery.py.
"""
import argparse
import hashlib
import pathlib
import re
import shlex
import shutil
import subprocess
import sys

GODOT = "/usr/bin/godot"
ROOT = pathlib.Path("/tmp/r101-mut03")
PROJ = ROOT / "proj"
OUT = ROOT / "out"
EVID = ROOT / "evidence"
PCK = OUT / "r101mut03.pck"
TAMPERED = OUT / "tampered.pck"
MISSING = OUT / "missing.pck"
LIVE_SCRIPT = "res://probe_mut03_live.gd"
DEAD_SCRIPT = "res://probe_mut03_dead.gd"

PROJECT_GODOT = """config_version=5

[application]
config/name="r101mut03"
run/main_scene="res://main.tscn"
config/features=PackedStringArray("4.7")
"""

MAIN_TSCN = """[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://main.gd" id="1"]

[node name="Main" type="Node2D"]
script = ExtResource("1")
"""

MAIN_GD = """extends Node2D

func _ready() -> void:
\tprint("MUT03_MAIN_READY")
"""

PRESET_CFG = """[preset.0]
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

[preset.0.options]
binary_format/architecture="x86_64"
"""

# The measurement block is bracketed by the two marker comments; mut03 swaps
# exactly that block for hardcoded golden constants ("dead measure").
PROBE_TEMPLATE = "\n".join([
    "extends SceneTree",
    "# r101 MUT-3 probe: one PCK receipt row per path argument.",
    "",
    "func _initialize() -> void:",
    "\t_run.call_deferred()",
    "",
    "func _run() -> void:",
    "\tvar all_ok := true",
    "\tfor p in OS.get_cmdline_user_args():",
    "\t\tvar r: Dictionary = _measure(p)",
    "\t\tvar verdict := \"PASS\" if r[\"ok\"] else \"FAIL\"",
    "\t\tprint(\"MUT03_ROW pck=%s magic=%s size=%d sha256=%s verdict=%s\" % [p, r[\"magic\"], r[\"size\"], r[\"sha\"], verdict])",
    "\t\tall_ok = all_ok and bool(r[\"ok\"])",
    "\tquit(0 if all_ok else 1)",
    "",
    "func _measure(path: String) -> Dictionary:",
    "\t# MEASURE-BEGIN",
    "\tvar f := FileAccess.open(path, FileAccess.READ)",
    "\tif f == null:",
    "\t\treturn {\"ok\": false, \"magic\": \"OPEN_FAIL\", \"size\": -1, \"sha\": \"none\"}",
    "\tvar magic := f.get_buffer(4).get_string_from_ascii()",
    "\tf.close()",
    "\tvar raw := FileAccess.get_file_as_bytes(path)",
    "\tvar size := raw.size()",
    "\tvar ctx := HashingContext.new()",
    "\tctx.start(HashingContext.HASH_SHA256)",
    "\tctx.update(raw)",
    "\tvar sha := ctx.finish().hex_encode()",
    "\treturn {\"ok\": magic == \"GDPC\" and size >= 256, \"magic\": magic, \"size\": size, \"sha\": sha}",
    "\t# MEASURE-END",
    "",
])

DEAD_BLOCK = "\n".join([
    "\tvar magic := \"GDPC\"",
    "\tvar size := {size}",
    "\tvar sha := \"{sha}\"",
    "\treturn {\"ok\": true, \"magic\": magic, \"size\": size, \"sha\": sha}",
])

ROW_RE = re.compile(
    r"^MUT03_ROW pck=(?P<pck>\S+) magic=(?P<magic>\S+) size=(?P<size>-?\d+) "
    r"sha256=(?P<sha>\S+) verdict=(?P<verdict>PASS|FAIL)$")
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def write_if_missing(path, text):
    if not path.exists():
        path.write_text(text)


def ensure_project():
    PROJ.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    EVID.mkdir(parents=True, exist_ok=True)
    write_if_missing(PROJ / "project.godot", PROJECT_GODOT)
    write_if_missing(PROJ / "main.tscn", MAIN_TSCN)
    write_if_missing(PROJ / "main.gd", MAIN_GD)
    write_if_missing(PROJ / "export_presets.cfg", PRESET_CFG)


def run(cmd, timeout):
    print("MUT03 CMD " + shlex.join(cmd))
    proc = subprocess.run(cmd, capture_output=True, timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def ensure_pck(force):
    if PCK.is_file() and not force:
        data = PCK.read_bytes()
        if data[:4] == b"GDPC":
            print(f"MUT03 reuse real pck path={PCK} bytes={len(data)}")
            return data
    cmd = [GODOT, "--headless", "--path", str(PROJ), "--export-pack", "Linux/X11", str(PCK)]
    rc, out, err = run(cmd, 300)
    (EVID / "export.stdout.txt").write_bytes(out)
    (EVID / "export.stderr.txt").write_bytes(err)
    print(f"MUT03 export rc={rc} stdout_bytes={len(out)} stderr_bytes={len(err)}")
    for line in ANSI_RE.sub("", (out + b"\n" + err).decode("utf-8", "replace")).splitlines():
        if line.strip() and ("ERROR" in line or "WARNING" in line or "savepack" in line or "Storing" in line):
            print("MUT03 export.line " + line.strip())
    data = PCK.read_bytes() if PCK.is_file() else b""
    if data[:4] != b"GDPC":
        print(f"MUT03 FAIL export produced no GDPC pck: magic={data[:4]!r} bytes={len(data)}")
        sys.exit(2)
    return data


def write_probes(golden):
    live = PROBE_TEMPLATE
    assert live.count("# MEASURE-BEGIN") == 1 and live.count("# MEASURE-END") == 1
    dead = re.sub(r"\t# MEASURE-BEGIN\n.*?\n\t# MEASURE-END",
                  DEAD_BLOCK.replace("{size}", str(golden["size"])).replace("{sha}", golden["sha"]),
                  live, count=1, flags=re.S)
    assert dead != live and "# MEASURE-BEGIN" not in dead
    (PROJ / "probe_mut03_live.gd").write_text(live)
    (PROJ / "probe_mut03_dead.gd").write_text(dead)
    (EVID / "probe_mut03_live.gd").write_text(live)
    (EVID / "probe_mut03_dead.gd").write_text(dead)


def run_probe(script_res, paths, tag):
    cmd = [GODOT, "--headless", "--path", str(PROJ), "--script", script_res, "--", *paths]
    rc, out, err = run(cmd, 120)
    (EVID / f"{tag}.stdout.txt").write_bytes(out)
    (EVID / f"{tag}.stderr.txt").write_bytes(err)
    return rc, out, err


def rows_of(out_bytes):
    text = ANSI_RE.sub("", out_bytes.decode("utf-8", "replace"))
    rows = []
    for line in text.splitlines():
        m = ROW_RE.match(line)
        if m:
            rows.append(m.groupdict())
    return rows


def receipt_only(out_bytes, golden):
    text = ANSI_RE.sub("", out_bytes.decode("utf-8", "replace"))
    return "magic=GDPC" in text and f"sha256={golden['sha']}" in text


def battery_shape(rc, out_bytes, artifact):
    return (rc == 0 and b"MUT03_ROW" in out_bytes
            and artifact.is_file() and artifact.stat().st_size > 0)


def recompute(out_bytes, golden):
    rows = rows_of(out_bytes)
    if not rows:
        return False
    for r in rows:
        p = pathlib.Path(r["pck"])
        if not p.is_file():
            return False
        data = p.read_bytes()
        if data[:4] != b"GDPC" or r["magic"] != "GDPC":
            return False
        if len(data) != int(r["size"]) or hashlib.sha256(data).hexdigest() != r["sha"]:
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force-export", action="store_true")
    args = ap.parse_args()

    ensure_project()
    real = ensure_pck(args.force_export)
    golden = {"size": len(real), "sha": hashlib.sha256(real).hexdigest(), "magic": real[:4].decode("latin1")}
    print(f"MUT03 GROUND_TRUTH real magic={golden['magic']} size={golden['size']} sha256={golden['sha']}")

    TAMPERED.write_bytes(b"GDXX" + real[4:])
    if MISSING.exists():
        MISSING.unlink()
    print(f"MUT03 GROUND_TRUTH tampered magic={TAMPERED.read_bytes()[:4].decode('latin1')} size={TAMPERED.stat().st_size}")
    print(f"MUT03 GROUND_TRUTH missing exists={MISSING.exists()} path={MISSING}")

    write_probes(golden)

    runs = [
        ("live_honest", LIVE_SCRIPT, [str(PCK)], PCK),
        ("dead_honest", DEAD_SCRIPT, [str(PCK)], PCK),
        ("live_tampered", LIVE_SCRIPT, [str(TAMPERED)], TAMPERED),
        ("dead_tampered", DEAD_SCRIPT, [str(TAMPERED)], TAMPERED),
        ("live_missing", LIVE_SCRIPT, [str(MISSING)], MISSING),
        ("dead_missing", DEAD_SCRIPT, [str(MISSING)], MISSING),
    ]
    results = {}
    for tag, script_res, paths, artifact in runs:
        rc, out, err = run_probe(script_res, paths, tag)
        p1 = receipt_only(out, golden)
        p2 = battery_shape(rc, out, artifact)
        p3 = recompute(out, golden)
        rows = rows_of(out)
        results[tag] = {"rc": rc, "p1": p1, "p2": p2, "p3": p3, "rows": rows,
                        "out_sha": hashlib.sha256(out).hexdigest()}
        print(f"MUT03 RUN {tag} rc={rc} p1_receipt_only={p1} p2_battery_shape={p2} p3_recompute={p3} "
              f"stdout_sha256={results[tag]['out_sha']} stderr_bytes={len(err)}")
        for r in rows:
            print(f"MUT03 ROW {tag} " + " ".join(f"{k}={v}" for k, v in r.items()))

    masked = (results["live_honest"]["rows"] == results["dead_honest"]["rows"]
              and results["live_honest"]["rc"] == results["dead_honest"]["rc"])
    print(f"MUT03 MASKED positive_path rows_identical={masked} "
          f"live_stdout_sha={results['live_honest']['out_sha']} dead_stdout_sha={results['dead_honest']['out_sha']}")

    model = {
        "live_honest": {"rc": 0, "p1": True, "p2": True, "p3": True},
        "dead_honest": {"rc": 0, "p1": True, "p2": True, "p3": True},
        "live_tampered": {"rc": 1, "p1": False, "p2": False, "p3": False},
        "dead_tampered": {"rc": 0, "p1": True, "p2": True, "p3": False},
        "live_missing": {"rc": 1, "p1": False, "p2": False, "p3": False},
        "dead_missing": {"rc": 0, "p1": True, "p2": False, "p3": False},
    }
    ok = masked
    for tag, exp in model.items():
        got = results[tag]
        for key, want in exp.items():
            if got[key] != want:
                print(f"MUT03 DIFF {tag}.{key} expected={want} observed={got[key]}")
                ok = False

    print("MUT03 VERDICT dead_measure_masked_on_honest_path=%s" % masked)
    print("MUT03 VERDICT dead+tampered: receipt_only=%s battery_shape=%s recompute=%s"
          % ("FOOLED" if results['dead_tampered']['p1'] else "REJECTED",
             "FOOLED" if results['dead_tampered']['p2'] else "REJECTED",
             "KILLED" if not results['dead_tampered']['p3'] else "FOOLED"))
    print("MUT03 VERDICT dead+missing: receipt_only=%s battery_shape=%s recompute=%s"
          % ("FOOLED" if results['dead_missing']['p1'] else "REJECTED",
             "FOOLED" if results['dead_missing']['p2'] else "REJECTED",
             "KILLED" if not results['dead_missing']['p3'] else "FOOLED"))
    print("MUT03 " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
