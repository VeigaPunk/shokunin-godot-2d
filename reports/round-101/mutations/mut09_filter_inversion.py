#!/usr/bin/env python3
"""MUT-9 (r101, 2D lane) — export filter include<->exclude inversion.

Ground-truth probe + mutant for the C1 export_prod scenario "include/exclude filter".

What it does, all with real Godot 4.7.2 headless runs on a scratch project:
  1. builds /var/tmp/r101-mut9/proj (falls back from /tmp when EDQUOT) with
     non-resource files (data/*.txt, data/*.md) + one scene/script;
  2. exports 5 PCK arms via `godot --headless --export-pack` differing only in
     include_filter / exclude_filter (arm table below);
  3. censuses each PCK two ways: (a) engine truth — runs the pack via
     `--main-pack` and lets main.gd enumerate res:// through DirAccess;
     (b) independent binary parse of the GDPC directory;
  4. applies the MUT-9 inversion mutant (A4 = A3 with include/exclude values
     swapped) and reports which pin shapes reject it and which are blind.

Arms (preset name, include_filter, exclude_filter):
  A0_inc_all   "*.txt"            ""                -> all txt non-resources in
  A1_inc_exc   "*.txt"            "data/skip.txt"   -> exclude wins on match
  A2_conflict  "data/keep.txt"    "data/keep.txt"   -> same file both sides
  A3_names     "data/keep.txt"    "data/skip.txt"   -> 1 txt in
  A4_names_inv "data/skip.txt"    "data/keep.txt"   -> MUTANT: A3 swapped

Verdict logic is printed as MUT09_* lines; receipt.json holds raw captures.
Never touches the lane repo (only /var/tmp scratch).
"""
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
import time

GODOT = os.environ.get("GODOT", "godot")

ARMS = [
    ("A0_inc_all", "*.txt", ""),
    ("A1_inc_exc", "*.txt", "data/skip.txt"),
    ("A2_conflict", "data/keep.txt", "data/keep.txt"),
    ("A3_names", "data/keep.txt", "data/skip.txt"),
    ("A4_names_inv", "data/skip.txt", "data/keep.txt"),  # MUT-9 mutant of A3
]
MUTANT_OF = {"A4_names_inv": "A3_names", "A3_names": "A4_names_inv"}

PROJECT_GODOT = """config_version=5

[application]

config/name="r101-mut9"
run/main_scene="res://main.tscn"
"""

MAIN_TSCN = """[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://main.gd" id="1"]

[node name="Mut9" type="Node2D"]
script = ExtResource("1")
"""

MAIN_GD = """extends Node2D


func _ready() -> void:
	var entries: Array[String] = []
	_walk("res://", entries)
	entries.sort()
	print("CENSUS_BEGIN count=", entries.size())
	for e in entries:
		print("entry: ", e)
	print("CENSUS_END")
	get_tree().quit()


func _walk(dir_path: String, out: Array[String]) -> void:
	var d := DirAccess.open(dir_path)
	if d == null:
		return
	d.list_dir_begin()
	var name := d.get_next()
	while name != "":
		if name != "." and name != "..":
			var full := dir_path.path_join(name)
			if d.current_is_dir():
				_walk(full, out)
			else:
				out.append(full)
		name = d.get_next()
"""


def pick_root() -> str:
    for cand in ("/tmp/r101-mut9", "/var/tmp/r101-mut9"):
        try:
            os.makedirs(cand, exist_ok=True)
            probe = os.path.join(cand, ".wtest")
            with open(probe, "w") as fh:
                fh.write("ok")
            os.remove(probe)
            return cand
        except OSError as exc:
            print(f"MUT09_SCRATCH root={cand} writable=False err={exc!r}")
    raise SystemExit("no writable scratch root")


def run(cmd, timeout):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           timeout=timeout)
        return {"cmd": cmd, "rc": p.returncode, "out": p.stdout.decode("utf-8", "replace"),
                "secs": round(time.time() - t0, 2)}
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or b"").decode("utf-8", "replace")
        return {"cmd": cmd, "rc": None, "out": out, "secs": round(time.time() - t0, 2),
                "timeout": True}


def build_project(root):
    proj = os.path.join(root, "proj")
    for d in ("data",):
        os.makedirs(os.path.join(proj, d), exist_ok=True)
    with open(os.path.join(proj, "project.godot"), "w") as fh:
        fh.write(PROJECT_GODOT)
    with open(os.path.join(proj, "main.tscn"), "w") as fh:
        fh.write(MAIN_TSCN)
    with open(os.path.join(proj, "main.gd"), "w") as fh:
        fh.write(MAIN_GD)
    with open(os.path.join(proj, "data", "keep.txt"), "w") as fh:
        fh.write("KEEP_MARKER\n")
    with open(os.path.join(proj, "data", "skip.txt"), "w") as fh:
        fh.write("SKIP_MARKER\n")
    with open(os.path.join(proj, "data", "notes.md"), "w") as fh:
        fh.write("NOTES_MARKER\n")
    parts = []
    for i, (name, inc, exc) in enumerate(ARMS):
        parts.append(f"""[preset.{i}]
name="{name}"
platform="Linux/X11"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter="{inc}"
exclude_filter="{exc}"
export_path=""

[preset.{i}.options]
binary_format/architecture="x86_64"
""")
    with open(os.path.join(proj, "export_presets.cfg"), "w") as fh:
        fh.write("\n".join(parts))
    return proj


CENSUS_RE = re.compile(r"^entry: (res://\S+)$", re.M)


def engine_census(pack_path):
    r = run([GODOT, "--headless", "--main-pack", pack_path, "--quit-after", "3"], 120)
    entries = CENSUS_RE.findall(r["out"])
    return r, entries


def parse_pck(path):
    data = open(path, "rb").read()
    res = {"ok": False, "bytes": len(data)}
    if data[:4] != b"GDPC":
        res["reason"] = f"magic={data[:4]!r}"
        return res
    off = 4
    (fmt,) = struct.unpack_from("<I", data, off); off += 4
    if fmt >= 2:
        (vmaj, vmin, vpat) = struct.unpack_from("<III", data, off); off += 12
    else:
        (vmaj, vmin, vpat) = (0, 0, 0)
    (flags,) = struct.unpack_from("<I", data, off); off += 4
    (file_base,) = struct.unpack_from("<Q", data, off); off += 8
    dir_offset = None
    if fmt >= 4:
        (dir_offset,) = struct.unpack_from("<Q", data, off); off += 8
    off += (18 * 4 if fmt >= 4 else 16 * 4)
    if fmt >= 4 and dir_offset is not None:
        off = dir_offset
    (count,) = struct.unpack_from("<I", data, off); off += 4
    entries = []
    try:
        for _ in range(count):
            (plen,) = struct.unpack_from("<I", data, off); off += 4
            raw = data[off:off + plen]; off += plen
            while off % 4:
                off += 1
            name = raw.split(b"\x00")[0].decode("utf-8", "replace")
            (ofs,) = struct.unpack_from("<Q", data, off); off += 8
            (size,) = struct.unpack_from("<Q", data, off); off += 8
            md5 = data[off:off + 16]; off += 16
            (eflags,) = struct.unpack_from("<I", data, off); off += 4
            if flags & 1:
                off += 16 + 4
            data_off = file_base + ofs if flags & 2 else ofs
            # format 4 stores paths relative to res:// (measured on 4.7.2 bytes)
            norm = name if name.startswith("res://") else "res://" + name
            if "\x00" in norm or not all(32 <= ord(c) < 127 for c in norm):
                res["reason"] = f"path parse lost sync at entry: {name!r}"
                return res
            entries.append({"path": norm, "offset": data_off, "size": size,
                            "eflags": eflags,
                            "bounds_ok": data_off + size <= len(data),
                            "md5": md5.hex()})
        res.update({"ok": True, "fmt": fmt, "version": [vmaj, vmin, vpat],
                    "flags": flags, "file_base": file_base,
                    "dir_offset": dir_offset, "count": count,
                    "entries": entries})
    except struct.error as exc:
        res["reason"] = f"struct error: {exc!r}"
    return res


def main():
    root = pick_root()
    print(f"MUT09_ROOT {root}")
    proj = build_project(root)
    out_dir = os.path.join(root, "out")
    os.makedirs(out_dir, exist_ok=True)
    receipt = {"root": root, "godot": GODOT, "arms": {}, "runs": []}

    imp = run([GODOT, "--headless", "--path", proj, "--import"], 180)
    receipt["runs"].append({"step": "import", **{k: imp[k] for k in ("cmd", "rc", "secs")}})
    print(f"MUT09_IMPORT rc={imp['rc']} secs={imp['secs']}")

    for name, inc, exc in ARMS:
        pck = os.path.join(out_dir, name + ".pck")
        exp = run([GODOT, "--headless", "--path", proj, "--export-pack", name, pck], 180)
        receipt["runs"].append({"step": f"export {name}",
                                **{k: exp[k] for k in ("cmd", "rc", "secs", "timeout")
                                   if k in exp}})
        ok = os.path.isfile(pck) and os.path.getsize(pck) > 0
        sha = hashlib.sha256(open(pck, "rb").read()).hexdigest() if ok else None
        print(f"MUT09_EXPORT arm={name} rc={exp['rc']} bytes="
              f"{os.path.getsize(pck) if ok else 0} sha256={sha}")
        entry = {"include_filter": inc, "exclude_filter": exc, "rc": exp["rc"],
                 "ok": ok, "bytes": os.path.getsize(pck) if ok else 0,
                 "sha256": sha,
                 "export_log_stored": sorted(
                     re.findall(r"Storing File: (res://[^\x1b\s]+)", exp["out"])),
                 "export_tail": exp["out"][-600:]}
        if ok:
            eng, eng_entries = engine_census(pck)
            binr = parse_pck(pck)
            entry["engine_rc"] = eng["rc"]
            entry["engine_entries"] = sorted(eng_entries)
            entry["engine_tail"] = eng["out"][-800:]
            entry["bin_ok"] = binr["ok"]
            entry["bin_reason"] = binr.get("reason")
            entry["bin_count"] = binr.get("count")
            entry["bin_entries"] = sorted(e["path"] for e in binr.get("entries", []))
            entry["bin_bounds_ok"] = all(e["bounds_ok"] for e in binr.get("entries", []))
            print(f"MUT09_CENSUS arm={name} engine=" + json.dumps(entry["engine_entries"]))
            print(f"MUT09_BIN arm={name} ok={binr['ok']} "
                  f"reason={binr.get('reason', '-')} entries="
                  + json.dumps(entry["bin_entries"]))
        receipt["arms"][name] = entry

    def block(entries):
        return ("CENSUS_BEGIN count=%d\n" % len(entries)
                + "".join(f"entry: {e}\n" for e in entries) + "CENSUS_END")

    # ---- discrimination: does the pin shape see the include<->exclude inversion?
    report = {}
    a3, a4 = receipt["arms"].get("A3_names", {}), receipt["arms"].get("A4_names_inv", {})
    if a3.get("ok") and a4.get("ok"):
        e3, e4 = a3["engine_entries"], a4["engine_entries"]
        report["A3_count"] = len(e3)
        report["A4_count"] = len(e4)
        report["count_equal"] = len(e3) == len(e4)
        report["size_equal"] = a3["bytes"] == a4["bytes"]
        report["sha_differs"] = a3["sha256"] != a4["sha256"]
        report["entry_set_differs"] = e3 != e4
        report["A3_txt"] = [e for e in e3 if e.endswith(".txt")]
        report["A4_txt"] = [e for e in e4 if e.endswith(".txt")]
        report["bin_agrees_engine_A3"] = a3["bin_entries"] == e3
        report["bin_agrees_engine_A4"] = a4["bin_entries"] == e4
        report["export_log_agrees_engine_A3"] = a3["export_log_stored"] == e3
        report["export_log_agrees_engine_A4"] = a4["export_log_stored"] == e4
        report["all_bounds_ok"] = all(
            receipt["arms"][n].get("bin_bounds_ok", False)
            for n, _, _ in ARMS if receipt["arms"][n].get("ok"))

        b3, b4 = block(e3), block(e4)
        single = "entry: res://data/keep.txt"
        report["single_line_pin_hits_A3"] = single in b3
        report["single_line_pin_hits_A4_honest"] = single in b4
        report["single_line_pin_rejects_inversion"] = single not in b4
        report["full_block_pin_rejects_inversion"] = b3 not in b4
        report["count_only_pin_passes_inversion"] = (f"count={len(e3)}" in b3
                                                     and f"count={len(e4)}" in b4)
        report["magic_only_pin_passes_inversion"] = bool(a3["ok"] and a4["ok"])
        # F2-style forgery: an extra entry line injected INSIDE the true block
        forged = b3.replace("CENSUS_END",
                            "entry: res://data/forged_extra.txt\nCENSUS_END")
        report["forged_inside_block_passes_single_line_pin"] = single in forged
        report["forged_inside_block_passes_full_block_pin"] = b3 in forged
    receipt["discrimination"] = report

    print("MUT09_DISCRIM " + json.dumps(report, indent=1, sort_keys=True))
    verdict = {
        "count_size_magic_pins_blind_to_inversion": bool(
            report.get("count_equal") and report.get("size_equal")
            and report.get("magic_only_pin_passes_inversion")),
        "single_line_and_block_pins_reject_inversion": bool(
            report.get("single_line_pin_rejects_inversion")
            and report.get("full_block_pin_rejects_inversion")),
        "full_block_pin_rejects_forged_extra_line": not report.get(
            "forged_inside_block_passes_full_block_pin", True),
        "triangulation_bin_engine_log": bool(
            report.get("bin_agrees_engine_A3") and report.get("bin_agrees_engine_A4")
            and report.get("export_log_agrees_engine_A3")
            and report.get("export_log_agrees_engine_A4")),
    }
    print("MUT09_VERDICT " + json.dumps(verdict, sort_keys=True))
    with open(os.path.join(root, "receipt.json"), "w") as fh:
        json.dump(receipt, fh, indent=1)
    print(f"MUT09_RECEIPT {os.path.join(root, 'receipt.json')}")


if __name__ == "__main__":
    main()
