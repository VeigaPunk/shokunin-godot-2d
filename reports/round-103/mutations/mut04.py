#!/usr/bin/env python3
"""r103-mut4 — header-census ECHO mutation for E4 (must REJECT the echo arm).

Attack class (r103-crit1, seat C1-d): "header census echo (echoed rather than
probed)" — a census arm that reports header fields by echoing bytes it just
read (or constants it copied from a genuine run) and never binds the report to
the presented artifact, so a tampered artifact inherits a genuine-looking
census. This driver builds the discriminator from measured bytes:

  1. setup   — fresh minimal Godot 4.7.2 project under /var/tmp/r103c-M4/,
               real `--export-pack` PCK (ground truth artifact).
  2. probe   — E4-idiom GD census probe (FileAccess.get_buffer +
               PackedByteArray.decode_u32/decode_u64, struct-shaped) with two
               modes: `valid` (judges: magic/version/file_base/dir bounds/
               count/name-table/entry bounds) and `echo` (prints the same
               read-back fields, NO judgment — the vulnerable shape).
  3. forges  — 7 byte-level forgeries of the genuine PCK, each mapped to the
               validation clause that must catch it; g5/g6 keep the header
               VERBATIM (echoed) and mutate only the body — the exact
               header-echo shape at artifact level.
  4. check   — clause matrix + ablation over stored probe records:
               A bind_sha, B bind_bytes, C verdict_ok, D oracle_agree (python
               re-parse of the PRESENTED bytes). Arms: genuine, stale-record
               (record swapped), max-echo (echo record + forged verdict with
               sha/bytes rebased). Required: genuine PASSes; echo arms FAIL
               unless a load-bearing clause is ablated.

Hard rules honoured: run_battery.py is never executed; all scratch lives under
/var/tmp/r103c-M4 (never /tmp: EDQUOT); the repo is read-only from here.

Usage:
  python3 reports/round-103/mutations/mut04.py all
  python3 reports/round-103/mutations/mut04.py setup|probe|forges|check
"""
import argparse
import datetime
import hashlib
import json
import os
import struct
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ROOT = Path("/var/tmp/r103c-M4")
PROJ = ROOT / "proj"
OUTD = ROOT / "out"
FORGES = ROOT / "forges"
LOGS = ROOT / "logs"
RECEIPTS = ROOT / "receipts"
GENUINE = OUTD / "div_m4.pck"
PROJ2 = ROOT / "proj2"
GENUINE2 = OUTD / "div_m4_b.pck"

PROJECT_GODOT = """config_version=5

[application]
config/name="Mut4Census"
run/main_scene="res://main.tscn"
config/features=PackedStringArray("4.7")

[display]
window/size/viewport_width=320
window/size/viewport_height=180
"""

PRESET_CFG = """[preset.0]
name="PCK"
platform="Linux/X11"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path=""
encrypt_pck=false
encrypt_directory=false

[preset.0.options]
binary_format/architecture="x86_64"
binary_format/embed_pck=false
"""

MAIN_GD = "extends Node\n\nfunc _ready() -> void:\n\tprint(\"MUT4_MAIN_OK\")\n\tget_tree().quit(0)\n"

MAIN_TSCN = ('[gd_scene load_steps=2 format=3]\n\n[ext_resource type="Script" path="res://main.gd" id="1"]\n\n'
             '[node name="Main" type="Node"]\nscript = ExtResource("1")\n')

PROBE_GD = r'''extends SceneTree
# r103-mut4 E4-idiom header-census probe. valid mode judges; echo mode only
# echoes the read-back fields (the vulnerable shape being hunted).

var pck := ""
var mode := "valid"

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--pck="):
			pck = a.substr(6)
		elif a.begins_with("--mode="):
			mode = a.substr(7)
	call_deferred("_run")

func _u32(b: PackedByteArray, o: int) -> int:
	if o + 4 > b.size():
		return -1
	return b.decode_u32(o)

func _u64(b: PackedByteArray, o: int) -> int:
	if o + 8 > b.size():
		return -1
	return b.decode_u64(o)

func _ascii(b: PackedByteArray, o: int, n: int) -> String:
	if o + n > b.size():
		return "<oob>"
	return b.slice(o, o + n).get_string_from_ascii()

func _name_at(b: PackedByteArray, o: int, n: int) -> String:
	var s := _ascii(b, o, n)
	var z := s.find("\u0000")
	if z >= 0:
		s = s.substr(0, z)
	return s

func _run() -> void:
	if pck == "":
		print("E4_PROBE_BEGIN mode=%s pck_bytes=0 sha256=none path=" % mode)
		print("E4_PROBE_END mode=%s verdict=REJECT reason=no_pck_arg" % mode)
		quit(2)
		return
	var f := FileAccess.open(pck, FileAccess.READ)
	if f == null:
		print("E4_PROBE_END mode=%s verdict=REJECT reason=open_failed" % mode)
		quit(1)
		return
	var total := f.get_length()
	var b := f.get_buffer(total)
	f.close()
	var sha := FileAccess.get_sha256(pck)
	print("E4_PROBE_BEGIN mode=%s pck_bytes=%d sha256=%s path=%s" % [mode, total, sha, pck])
	var magic := _ascii(b, 0, 4)
	var version := _u32(b, 4)
	var emaj := _u32(b, 8)
	var emin := _u32(b, 12)
	var epat := _u32(b, 16)
	var flags := _u32(b, 20)
	var file_base := _u64(b, 0x18)
	var dir_off := _u64(b, 0x20)
	var reserved_nz := 0
	if b.size() >= 0x70:
		for i in range(0x28, 0x70, 4):
			if b.decode_u32(i) != 0:
				reserved_nz += 1
	var gap_len := -1
	var gap_zero := false
	if file_base >= 0x70 and file_base <= b.size():
		gap_len = file_base - 0x70
		gap_zero = true
		for i in range(0x70, file_base):
			if b[i] != 0:
				gap_zero = false
				break
	var count := -1
	if dir_off >= 0 and dir_off + 4 <= b.size():
		count = b.decode_u32(dir_off)
	print("CENSUS magic=%s version=%d engine=%d.%d.%d flags=%d file_base=%d dir_off=%d reserved_nz=%d gap_len=%d gap_zero=%s count=%d" % [magic, version, emaj, emin, epat, flags, file_base, dir_off, reserved_nz, gap_len, str(gap_zero), count])
	var pos := dir_off + 4
	var n_entries := 0
	var name_table_ok := true
	var entries_bounds_ok := true
	if count >= 0 and count <= 100000:
		for i in range(count):
			if pos + 4 > b.size():
				name_table_ok = false
				break
			var plen := b.decode_u32(pos)
			pos += 4
			if plen > 4096 or pos + plen > b.size():
				name_table_ok = false
				break
			var nm := _name_at(b, pos, plen)
			pos += plen
			if pos + 36 > b.size():
				name_table_ok = false
				break
			var off := b.decode_u64(pos)
			var sz := b.decode_u64(pos + 8)
			var md5 := _hex(b, pos + 16, 16)
			pos += 36
			var abs := off
			if (flags & 2) != 0:
				abs = off + file_base
			if abs < 0 or sz < 0 or abs + sz > b.size():
				entries_bounds_ok = false
			var dm := "<na>"
			if abs >= 0 and abs + 4 <= b.size():
				dm = _ascii(b, abs, 4)
			print("CENSUS_ENTRY i=%d name=%s off=%d abs=%d size=%d md5=%s dmagic=%s" % [i, nm, off, abs, sz, md5, dm])
			n_entries += 1
	else:
		name_table_ok = false
	if count >= 0 and n_entries != count:
		name_table_ok = false
	var magic_ok := magic == "GDPC"
	var version_ok := version >= 1 and version <= 16
	var file_base_ok := file_base >= 0x70 and file_base <= b.size()
	var dir_bounds_ok := dir_off >= 0 and dir_off >= file_base and dir_off + 4 <= b.size()
	var count_ok := count >= 1 and count <= 100000
	var all_ok := magic_ok and version_ok and file_base_ok and dir_bounds_ok and count_ok and name_table_ok and entries_bounds_ok
	if mode == "echo":
		print("ECHO_FIELDS header_provided=true judgment=false bind_sha=%s bind_bytes=%d" % [sha, total])
		print("E4_PROBE_END mode=echo verdict=ECHO reason=none")
		quit(0)
		return
	print("VALIDATE magic_ok=%s version_ok=%s file_base_ok=%s dir_bounds_ok=%s count_ok=%s name_table_ok=%s entries_bounds_ok=%s" % [str(magic_ok), str(version_ok), str(file_base_ok), str(dir_bounds_ok), str(count_ok), str(name_table_ok), str(entries_bounds_ok)])
	var verdict := "OK" if all_ok else "REJECT"
	var reason := "none"
	if not all_ok:
		if not magic_ok:
			reason = "magic"
		elif not version_ok:
			reason = "version"
		elif not file_base_ok:
			reason = "file_base"
		elif not dir_bounds_ok:
			reason = "dir_bounds"
		elif not count_ok:
			reason = "count"
		elif not name_table_ok:
			reason = "name_table"
		else:
			reason = "entries_bounds"
	print("E4_PROBE_END mode=valid verdict=%s reason=%s" % [verdict, reason])
	quit(0 if all_ok else 1)

func _hex(b: PackedByteArray, o: int, n: int) -> String:
	if o + n > b.size():
		return "<oob>"
	return b.slice(o, o + n).hex_encode()
'''


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def sha256_file(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def uptime_line():
    try:
        return subprocess.run(["uptime"], capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception as exc:  # noqa: BLE001
        return f"uptime probe failed: {exc}"


def godot_version():
    try:
        p = subprocess.run(["godot", "--version"], capture_output=True, text=True, timeout=30)
        return (p.stdout + p.stderr).strip().splitlines()[0]
    except Exception as exc:  # noqa: BLE001
        return f"probe failed: {exc}"


def run_cmd(cmd, timeout=120, env=None):
    started = time.monotonic()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
        return {"command": cmd, "exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr,
                "wall_seconds": round(time.monotonic() - started, 3)}
    except subprocess.TimeoutExpired as exc:
        return {"command": cmd, "exit": None, "error": f"TIMEOUT after {timeout}s",
                "stdout": (exc.stdout or "") if isinstance(exc.stdout, str) else "",
                "stderr": (exc.stderr or "") if isinstance(exc.stderr, str) else "",
                "wall_seconds": round(time.monotonic() - started, 3)}
    except OSError as exc:
        return {"command": cmd, "exit": None, "error": str(exc), "stdout": "", "stderr": "",
                "wall_seconds": round(time.monotonic() - started, 3)}


def receipt(name, payload):
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    payload = dict(payload)
    payload.setdefault("phase", name)
    payload.setdefault("timestamp", now())
    payload.setdefault("uptime", uptime_line())
    payload.setdefault("godot_version", godot_version())
    payload.setdefault("head", subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
                                              capture_output=True, text=True).stdout.strip())
    path = RECEIPTS / f"{name}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n")
    print(f"[receipt] {path}")
    return payload


# ---- independent python oracle (re-parse of the presented artifact bytes) ----
def oracle_census(path: Path):
    b = path.read_bytes()
    n = len(b)
    out = {"file": str(path), "bytes": n, "sha256": hashlib.sha256(b).hexdigest(),
           "read_ok": False, "reason": None}
    if n < 0x70:
        out["reason"] = "short_header"
        return out
    out["magic"] = b[0:4].decode("latin1")
    (out["version"], out["engine_major"], out["engine_minor"], out["engine_patch"],
     out["flags"]) = struct.unpack_from("<5I", b, 4)
    out["file_base"], = struct.unpack_from("<Q", b, 0x18)
    out["dir_off"], = struct.unpack_from("<Q", b, 0x20)
    out["reserved_nz"] = sum(1 for i in range(0x28, 0x70, 4) if struct.unpack_from("<I", b, i)[0] != 0)
    fb = out["file_base"]
    out["gap_len"] = (fb - 0x70) if 0x70 <= fb <= n else -1
    out["gap_zero"] = (0x70 <= fb <= n and all(x == 0 for x in b[0x70:fb]))
    if out["magic"] != "GDPC":
        out["reason"] = "magic"
        return out
    if not (1 <= out["version"] <= 16):
        out["reason"] = "version"
        return out
    if not (0x70 <= fb <= n):
        out["reason"] = "file_base"
        return out
    dir_off = out["dir_off"]
    if not (dir_off >= fb and dir_off + 4 <= n):
        out["reason"] = "dir_bounds"
        return out
    count, = struct.unpack_from("<I", b, dir_off)
    out["count"] = count
    if count > 100000:
        out["reason"] = "count"
        return out
    pos = dir_off + 4
    entries = []
    for _ in range(count):
        if pos + 4 > n:
            out["reason"] = "name_len_oob"
            return out
        plen, = struct.unpack_from("<I", b, pos)
        pos += 4
        if plen > 4096 or pos + plen > n:
            out["reason"] = "name_oob"
            return out
        name = b[pos:pos + plen].split(b"\x00")[0].decode("utf-8", "replace")
        pos += plen
        if pos + 36 > n:
            out["reason"] = "entry_oob"
            return out
        off, size = struct.unpack_from("<QQ", b, pos)
        md5 = b[pos + 16:pos + 32].hex()
        pos += 36
        abs_off = off + fb if (out["flags"] & 2) else off
        if abs_off < 0 or abs_off + size > n:
            out["reason"] = "data_oob"
            return out
        entries.append({"name": name, "off": off, "abs": abs_off, "size": size, "md5": md5})
    out["entries"] = entries
    out["read_ok"] = True
    out["reason"] = None
    return out


# ---- probe record parsing ----
def parse_record(text: str):
    rec = {"census": {}, "entries": [], "validate": {}, "verdict": None, "reason": None,
           "sha256": None, "pck_bytes": None, "echo": False}
    for line in text.splitlines():
        if line.startswith("E4_PROBE_BEGIN "):
            for tok in line.split()[1:]:
                if "=" in tok:
                    k, v = tok.split("=", 1)
                    if k == "sha256":
                        rec["sha256"] = v
                    elif k == "pck_bytes":
                        try:
                            rec["pck_bytes"] = int(v)
                        except ValueError:
                            pass
        elif line.startswith("CENSUS "):
            for tok in line.split()[1:]:
                if "=" in tok:
                    k, v = tok.split("=", 1)
                    rec["census"][k] = v
        elif line.startswith("CENSUS_ENTRY "):
            e = {}
            for tok in line.split()[1:]:
                if "=" in tok:
                    k, v = tok.split("=", 1)
                    e[k] = v
            rec["entries"].append(e)
        elif line.startswith("VALIDATE "):
            for tok in line.split()[1:]:
                if "=" in tok:
                    k, v = tok.split("=", 1)
                    rec["validate"][k] = v
        elif line.startswith("ECHO_FIELDS "):
            rec["echo"] = True
        elif line.startswith("E4_PROBE_END "):
            for tok in line.split()[1:]:
                if "=" in tok:
                    k, v = tok.split("=", 1)
                    if k == "verdict":
                        rec["verdict"] = v
                    elif k == "reason":
                        rec["reason"] = v
    return rec


CENSUS_FIELDS = ("magic", "version", "engine", "flags", "file_base", "dir_off", "reserved_nz", "count")


def record_matches_oracle(rec, orc):
    if not orc.get("read_ok"):
        return False, "oracle_invalid"
    c = rec["census"]
    engine = "%d.%d.%d" % (orc["engine_major"], orc["engine_minor"], orc["engine_patch"])
    want = {"magic": orc["magic"], "version": str(orc["version"]),
            "engine": engine, "flags": str(orc["flags"]), "file_base": str(orc["file_base"]),
            "dir_off": str(orc["dir_off"]), "reserved_nz": str(orc["reserved_nz"]),
            "count": str(orc["count"])}
    for k in CENSUS_FIELDS:
        if c.get(k) != want[k]:
            return False, f"field:{k}:{c.get(k)}!={want[k]}"
    if len(rec["entries"]) != len(orc["entries"]):
        return False, f"entry_count:{len(rec['entries'])}!={len(orc['entries'])}"
    for r, o in zip(rec["entries"], orc["entries"]):
        if r.get("name") != o["name"] or r.get("off") != str(o["off"]) or r.get("size") != str(o["size"]):
            return False, f"entry:{r.get('name')}"
    return True, "ok"


def full_check(rec_text, artifact: Path, clauses=("A", "B", "C", "D")):
    rec = parse_record(rec_text)
    orc = oracle_census(artifact)
    res = {}
    sha = sha256_file(artifact)
    res["A_bind_sha"] = (rec["sha256"] == sha)
    res["B_bind_bytes"] = (rec["pck_bytes"] == len(artifact.read_bytes()))
    vals = rec["validate"]
    all_true = bool(vals) and all(v == "true" for v in vals.values())
    res["C_verdict_ok"] = (rec["verdict"] == "OK" and not rec["echo"] and all_true)
    match, why = record_matches_oracle(rec, orc)
    res["D_oracle_agree"] = match
    sel = {k: v for k, v in res.items() if k[0] in clauses}
    return {"pass": all(sel.values()), "clauses_all": res, "clauses_selected": sel,
            "oracle_ok": orc.get("read_ok"), "oracle_reason": orc.get("reason"),
            "oracle_vs_record": why}


# ---- phases ----
def phase_setup(_args):
    for d in (PROJ, OUTD, LOGS):
        d.mkdir(parents=True, exist_ok=True)
    (PROJ / "project.godot").write_text(PROJECT_GODOT)
    (PROJ / "export_presets.cfg").write_text(PRESET_CFG)
    (PROJ / "main.gd").write_text(MAIN_GD)
    (PROJ / "main.tscn").write_text(MAIN_TSCN)
    # second genuine-shaped artifact: same project, same-length string edit in
    # main.gd only (entry names/sizes should match; bytes/sha must differ).
    PROJ2.mkdir(parents=True, exist_ok=True)
    (PROJ2 / "project.godot").write_text(PROJECT_GODOT)
    (PROJ2 / "export_presets.cfg").write_text(PRESET_CFG)
    (PROJ2 / "main.gd").write_text(MAIN_GD.replace("MUT4_MAIN_OK", "MUT4_MAIN_XK"))
    (PROJ2 / "main.tscn").write_text(MAIN_TSCN)
    env = os.environ.copy()
    tmp = ROOT / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    env["TMPDIR"] = str(tmp)
    imp = run_cmd(["godot", "--headless", "--path", str(PROJ), "--import"], timeout=180, env=env)
    exp = run_cmd(["godot", "--headless", "--path", str(PROJ), "--export-pack", "PCK", str(GENUINE)],
                  timeout=180, env=env)
    imp2 = run_cmd(["godot", "--headless", "--path", str(PROJ2), "--import"], timeout=180, env=env)
    exp2 = run_cmd(["godot", "--headless", "--path", str(PROJ2), "--export-pack", "PCK", str(GENUINE2)],
                   timeout=180, env=env)
    (LOGS / "setup_pack.log").write_text(exp["stdout"] + exp["stderr"])
    (LOGS / "setup_pack2.log").write_text(exp2["stdout"] + exp2["stderr"])
    ok = GENUINE.is_file() and exp["exit"] == 0 and GENUINE2.is_file() and exp2["exit"] == 0
    payload = {"verdict": "PASS" if ok else "FAIL",
               "import": {k: imp[k] for k in ("exit", "wall_seconds")},
               "export": {k: exp[k] for k in ("exit", "wall_seconds")},
               "import2": {k: imp2[k] for k in ("exit", "wall_seconds")},
               "export2": {k: exp2[k] for k in ("exit", "wall_seconds")},
               "export_tail": (exp["stdout"] + exp["stderr"]).splitlines()[-4:],
               "export2_tail": (exp2["stdout"] + exp2["stderr"]).splitlines()[-4:],
               "genuine": {"path": str(GENUINE), "bytes": GENUINE.stat().st_size if GENUINE.is_file() else None,
                           "sha256": sha256_file(GENUINE)},
               "genuine2": {"path": str(GENUINE2), "bytes": GENUINE2.stat().st_size if GENUINE2.is_file() else None,
                            "sha256": sha256_file(GENUINE2)},
               "preset_cfg_sha256": sha256_file(PROJ / "export_presets.cfg")}
    receipt("setup", payload)
    print(f"{payload['verdict']} setup (pck={payload['genuine']['bytes']}B, pck2={payload['genuine2']['bytes']}B)")
    return 0 if ok else 1


def write_probe():
    PROJ.mkdir(parents=True, exist_ok=True)
    (PROJ / "probe.gd").write_text(PROBE_GD)
    return sha256_file(PROJ / "probe.gd")


def run_probe(pck: Path, mode: str, timeout=60):
    env = os.environ.copy()
    tmp = ROOT / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    env["TMPDIR"] = str(tmp)
    cmd = ["godot", "--headless", "--path", str(PROJ), "--script", "res://probe.gd", "--",
           f"--pck={pck}", f"--mode={mode}"]
    return run_cmd(cmd, timeout=timeout, env=env)


def phase_probe(args):
    assert GENUINE.is_file(), "run setup first"
    probe_sha = write_probe()
    results = {}
    for mode in ("valid", "echo"):
        run = run_probe(GENUINE, mode)
        text = run["stdout"] + run["stderr"]
        results[mode] = {"exit": run["exit"], "wall_seconds": run["wall_seconds"],
                         "stdout_lines": run["stdout"].splitlines(),
                         "stderr_lines": run["stderr"].splitlines(),
                         "capture_bytes": len(text.encode())}
    valid = results["valid"]
    ok = valid["exit"] == 0 and any("verdict=OK" in ln for ln in valid["stdout_lines"])
    receipt("probe-genuine", {"verdict": "PASS" if ok else "FAIL", "probe_gd_sha256": probe_sha,
                              "genuine_sha256": sha256_file(GENUINE), "modes": results})
    print(f"{'PASS' if ok else 'FAIL'} probe genuine (exit={valid['exit']}, "
          f"{len(valid['stdout_lines'])} stdout lines)")
    return 0 if ok else 1


FORGERIES = ["g1_magic", "g2_version", "g3_count", "g4_entry_off", "g5_trunc64", "g6_trunc512", "g7_dir_lie"]
CLAUSE_OF = {"g1_magic": "magic_ok", "g2_version": "version_ok", "g3_count": "name_table_ok",
             "g4_entry_off": "entries_bounds_ok", "g5_trunc64": "name_table_ok",
             "g6_trunc512": "dir_bounds_ok", "g7_dir_lie": "dir_bounds_ok"}


def phase_forges(_args):
    assert GENUINE.is_file(), "run setup first"
    FORGES.mkdir(parents=True, exist_ok=True)
    src = GENUINE.read_bytes()
    n = len(src)
    orc = oracle_census(GENUINE)
    assert orc["read_ok"], "genuine oracle failed"
    dir_off = orc["dir_off"]
    pos = dir_off + 4
    plen, = struct.unpack_from("<I", src, pos)
    pos += 4 + plen
    entry_off_pos = pos
    made = {}
    variants = {
        "g1_magic": (lambda b: b.__setitem__(slice(0, 4), b"GDQC"), "u32@0x00 -> 'GDQC'"),
        "g2_version": (lambda b: struct.pack_into("<I", b, 4, 99), "u32@0x04 -> 99"),
        "g3_count": (lambda b: struct.pack_into("<I", b, dir_off, orc["count"] + 1000),
                     f"u32@dir_off({dir_off}) -> count+1000"),
        "g4_entry_off": (lambda b: struct.pack_into("<Q", b, entry_off_pos, n + 4096),
                         f"u64@entry0.off({entry_off_pos}) -> bytes+4096"),
        "g5_trunc64": (lambda b: None, "header intact, cut last 64B (HEADER-ECHO shape)"),
        "g6_trunc512": (lambda b: None, "header intact, cut last 512B (dir_off > bytes)"),
        "g7_dir_lie": (lambda b: struct.pack_into("<Q", b, 0x20, n + 12345), "u64@0x20 (dir_off) -> bytes+12345"),
    }
    for name in FORGERIES:
        b = bytearray(src)
        fn, desc = variants[name]
        fn(b)
        if name.startswith("g5") or name.startswith("g6"):
            b = b[:n - (64 if name == "g5_trunc64" else 512)]
        p = FORGES / f"{name}.pck"
        p.write_bytes(bytes(b))
        made[name] = {"path": str(p), "bytes": len(b), "sha256": sha256_file(p), "mutation": desc,
                      "expect_clause": CLAUSE_OF[name]}
    payload = {"verdict": "PASS", "genuine": {"bytes": n, "sha256": sha256_file(GENUINE),
                                              "dir_off": dir_off, "count": orc["count"],
                                              "entry0_off_field_at": entry_off_pos},
               "forgeries": made}
    receipt("forges", payload)
    for name in FORGERIES:
        print(f"forge {name}: {made[name]['bytes']}B sha={made[name]['sha256'][:12]} ({made[name]['mutation']})")
    return 0


def phase_check(_args):
    assert GENUINE.is_file(), "run setup first"
    write_probe()
    artifact = {name: FORGES / f"{name}.pck" for name in FORGERIES}
    valid_records, echo_records = {}, {}
    valid_runs = {}
    for name, p in [("genuine", GENUINE)] + list(artifact.items()):
        run = run_probe(p, "valid")
        valid_runs[name] = run
        valid_records[name] = run["stdout"] + run["stderr"]
        erun = run_probe(p, "echo")
        echo_records[name] = erun["stdout"] + erun["stderr"]
    # arm construction
    arms = {}
    arms["genuine"] = {"record": valid_records["genuine"], "artifact": GENUINE,
                       "note": "valid-mode record over the genuine artifact"}
    arms["stale-record"] = {"record": valid_records["genuine"], "artifact": artifact["g5_trunc64"],
                            "note": "genuine record presented for a truncated artifact"}
    arms["other-run-record"] = {"record": valid_records["genuine"], "artifact": GENUINE2,
                                "note": "genuine record of run A presented for the second genuine export B "
                                        "(both artifacts valid; only bindings separate them)"}
    # max-echo: echo-mode record for the forgery, verdict/validation forged, bindings rebased
    for name in FORGERIES:
        orc = oracle_census(artifact[name])
        rec0 = parse_record(echo_records[name])
        lines = [ln for ln in echo_records[name].splitlines() if not ln.startswith("ECHO_FIELDS ")]
        forged = "\n".join(lines) + "\n"
        forged = forged.replace(f"sha256={rec0['sha256']}", f"sha256={orc['sha256']}")
        forged = forged.replace(f"pck_bytes={rec0['pck_bytes']}", f"pck_bytes={len(artifact[name].read_bytes())}")
        forged = forged.replace("E4_PROBE_END mode=echo verdict=ECHO reason=none",
                                "VALIDATE magic_ok=true version_ok=true file_base_ok=true "
                                "dir_bounds_ok=true count_ok=true name_table_ok=true entries_bounds_ok=true\n"
                                "E4_PROBE_END mode=valid verdict=OK reason=none")
        arms[f"max-echo-{name}"] = {"record": forged, "artifact": artifact[name],
                                    "note": "echo record (fields echoed, no judgment) + forged VALIDATE/verdict "
                                            "+ sha/bytes rebased to the presented artifact"}
    matrix = {}
    ablations = {"full": ("A", "B", "C", "D"), "drop-bind": ("C", "D"), "drop-oracle": ("A", "B", "C")}
    for arm, spec in arms.items():
        row = {}
        for ab, clauses in ablations.items():
            row[ab] = full_check(spec["record"], spec["artifact"], clauses)
        matrix[arm] = {"note": spec["note"], "artifact": str(spec["artifact"]),
                       "result": {ab: matrix_verdict(row[ab]) for ab in ablations},
                       "detail": {ab: {"clauses_selected": row[ab]["clauses_selected"],
                                       "clauses_all": row[ab]["clauses_all"],
                                       "oracle_ok": row[ab]["oracle_ok"],
                                       "oracle_reason": row[ab]["oracle_reason"],
                                       "oracle_vs_record": row[ab]["oracle_vs_record"]}
                                  for ab in ablations}}
    # in-engine half: what does the honest probe say about each forgery?
    probe_truth = {}
    for name in FORGERIES:
        rec = parse_record(valid_records[name])
        expect = CLAUSE_OF[name].replace("_ok", "")
        probe_truth[name] = {"probe_verdict": rec["verdict"], "probe_reason": rec["reason"],
                             "expect_reason": expect,
                             "close": (rec["verdict"] == "REJECT" and rec["reason"] == expect)}
    genuine_rec = parse_record(valid_records["genuine"])
    # header-echo equality: census fields of genuine vs g5 (header kept verbatim)
    g5_echo = parse_record(echo_records["g5_trunc64"])
    fields_equal = all(genuine_rec["census"].get(k) == g5_echo["census"].get(k) for k in CENSUS_FIELDS)
    sha_a, sha_b = sha256_file(GENUINE), sha256_file(GENUINE2)
    ok = (matrix["genuine"]["result"]["full"] == "PASS"
          and matrix["stale-record"]["result"]["full"] == "FAIL"
          and matrix["other-run-record"]["result"]["full"] == "FAIL"
          and sha_a != sha_b
          and all(probe_truth[n]["close"] for n in FORGERIES)
          and fields_equal
          and all(matrix[f"max-echo-{n}"]["result"]["full"] == "FAIL" for n in FORGERIES)
          and all(matrix[f"max-echo-{n}"]["result"]["drop-oracle"] == "PASS" for n in FORGERIES))
    payload = {"verdict": "PASS" if ok else "FAIL",
               "genuine": {"valid": {"exit": valid_runs["genuine"]["exit"], "verdict": genuine_rec["verdict"],
                                     "sha256_record": genuine_rec["sha256"], "census": genuine_rec["census"]},
                           "artifact_sha256": sha_a},
               "genuine2": {"sha256": sha_b, "path": str(GENUINE2)},
               "probe_truth_per_forgery": probe_truth,
               "header_echo_fields_equal_genuine_vs_g5": fields_equal,
               "arm_matrix": matrix,
               "required_reading": "the echoed header fields are IDENTICAL for genuine and the body-tampered "
                                   "g5/g6; the honest probe still rejects them via the validation clauses it "
                                   "computes itself; a forged echo record survives A/B/C only when the "
                                   "oracle-over-presented-bytes clause (D) is absent — D and the bind pair "
                                   "(A,B) are load-bearing"}
    receipt("check", payload)
    print(f"{payload['verdict']} check (genuine full={matrix['genuine']['result']['full']}, "
          f"stale full={matrix['stale-record']['result']['full']}, "
          f"other-run full={matrix['other-run-record']['result']['full']}, "
          f"max-echo full all FAIL={all(matrix[f'max-echo-{n}']['result']['full'] == 'FAIL' for n in FORGERIES)}, "
          f"echo-equal={fields_equal})")
    return 0 if ok else 1


def matrix_verdict(row):
    return "PASS" if row["pass"] else "FAIL"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="phase", required=True)
    for name, fn in (("setup", phase_setup), ("probe", phase_probe),
                     ("forges", phase_forges), ("check", phase_check)):
        p = sub.add_parser(name)
        p.set_defaults(func=fn)
    p = sub.add_parser("all")
    p.set_defaults(func=lambda _a: (phase_setup(_a) or phase_probe(_a) or phase_forges(_a) or phase_check(_a)))
    args = parser.parse_args()
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
