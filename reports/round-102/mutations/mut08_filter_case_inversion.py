#!/usr/bin/env python3
"""mut08 — r102 seat M8 (2D lane): filter-case inversion on the s04 probe.

Ground truth + inversion mutants, all with real Godot 4.7.2 headless runs on
scratch under /var/tmp/r102-mut8 (never /tmp: EDQUOT on this host).

s04 contract under attack (C1 launch matrix, "filter case-sensitivity probe"):
a headless export preset whose include_filter/exclude_filter match case-variant
non-resource assets; the exported pack is censused. The battery row accepts by
exact-signature substring (run_battery.py execute(): command shape line 1912,
timeout 8s line 1913; classify_process lines 1775-1792, replicated below).

Arm table (include_filter, exclude_filter):
  INC_LOWER      "*.txt"     ""       case probe (lowercase pattern)
  INC_UPPER      "*.TXT"     ""       case probe (uppercase pattern)
  XCONFLICT      "*.txt"     "*.TXT"  within-preset include/exclude case test
  XCONFLICT_INV  "*.TXT"     "*.txt"  MUTANT: XCONFLICT case-flip (literals swapped)
  MD_LOWER       "*.md"      ""       second-extension case witness
  MD_UPPER       "*.MD"      ""       second-extension case witness
  ROLE_SWAP      "*.md"      "*.txt"  include/exclude role swap vs INC_LOWER
                                      (artifact-visible inversion control)

Mutation analysis:
  A. case-flip artifact inversion: the honest XCONFLICT expectation is evaluated
     against the case-flip mutant arm's REAL bytes (and shas compared).
  A2. role-swap control: the honest INC_LOWER expectation against the role-swap
     arm's REAL bytes (an inversion whose census really differs).
  B. expectation-level inversion: honest measured include/exclude sets are
     swapped inside the expected receipt line; evaluated against the honest
     arm's REAL captured bytes and against the swapped-line-fixture model:
     honest must ACCEPT, swapped must REJECT.
  C. escape analysis: if case arms produce equal membership the case axis is
     behavior-preserving; report it instead of claiming discrimination.

Evidence rule: every claim cites a captured command + raw output; receipts are
written to /var/tmp/r102-mut8/receipt.json.
"""
import hashlib
import json
import os
import re
import shlex
import struct
import subprocess
import time

GODOT = os.environ.get("GODOT", "godot")
ROOT = "/var/tmp/r102-mut8"
PROJ = os.path.join(ROOT, "proj")
OUT = os.path.join(ROOT, "out")

ASSETS = {
    "data/alpha.txt": "ALPHA_LOWER_MARKER\n",
    "data/ALPHA.TXT": "ALPHA_UPPER_MARKER\n",
    "data/Beta.TxT": "BETA_MIXED_MARKER\n",
    "data/notes.md": "NOTES_CONTROL_MARKER\n",
}
DATA_DOMAIN = sorted("res://" + p for p in ASSETS)

ARMS = [
    ("INC_LOWER", "*.txt", ""),
    ("INC_UPPER", "*.TXT", ""),
    ("XCONFLICT", "*.txt", "*.TXT"),
    ("XCONFLICT_INV", "*.TXT", "*.txt"),  # case-flip mutant of XCONFLICT
    ("MD_LOWER", "*.md", ""),
    ("MD_UPPER", "*.MD", ""),
    ("ROLE_SWAP", "*.md", "*.txt"),  # include/exclude role swap vs INC_LOWER
]

PROJECT_GODOT = """config_version=5

[application]

config/name="r102-mut8-s04"
run/main_scene="res://main.tscn"
"""

MAIN_TSCN = """[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://main.gd" id="1"]

[node name="S04" type="Node2D"]
script = ExtResource("1")
"""

MAIN_GD = """extends Node2D


func _ready() -> void:
	var entries: Array[String] = []
	_walk("res://", entries)
	entries.sort()
	print("S04_CENSUS_BEGIN count=", entries.size())
	for e in entries:
		print("s04_entry: ", e)
	print("S04_CENSUS_END")
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

ENGINE_RE = re.compile(r"^s04_entry: (res://\S+)$", re.M)
STORED_RE = re.compile(r"Storing File:\s*(\S+)")
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def run(cmd, timeout):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           timeout=timeout)
        out = (p.stdout + p.stderr).decode("utf-8", "replace")
        return {"cmd": cmd, "rc": p.returncode, "out": out,
                "secs": round(time.time() - t0, 2)}
    except subprocess.TimeoutExpired as exc:
        so = exc.stdout or b""
        se = exc.stderr or b""
        return {"cmd": cmd, "rc": None,
                "out": (so + se).decode("utf-8", "replace"),
                "secs": round(time.time() - t0, 2), "timeout": True}
    except OSError as exc:
        return {"cmd": cmd, "rc": None, "out": str(exc),
                "secs": round(time.time() - t0, 2), "oserror": True}


def write_preset(inc, exc):
    cfg = f"""[preset.0]
name="s04"
platform="Linux/X11"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter="{inc}"
exclude_filter="{exc}"
export_path=""

[preset.0.options]
binary_format/architecture="x86_64"
"""
    with open(os.path.join(PROJ, "export_presets.cfg"), "w") as fh:
        fh.write(cfg)


def build_project():
    os.makedirs(os.path.join(PROJ, "data"), exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    for rel, body in ASSETS.items():
        with open(os.path.join(PROJ, rel), "w") as fh:
            fh.write(body)
    with open(os.path.join(PROJ, "project.godot"), "w") as fh:
        fh.write(PROJECT_GODOT)
    with open(os.path.join(PROJ, "main.tscn"), "w") as fh:
        fh.write(MAIN_TSCN)
    with open(os.path.join(PROJ, "main.gd"), "w") as fh:
        fh.write(MAIN_GD)


def parse_pck(data):
    """GDPC directory parse, format 4 layout (r101 mut09 precedent, same build)."""
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
            off += 16  # md5
            (eflags,) = struct.unpack_from("<I", data, off); off += 4
            if flags & 1:
                off += 16 + 4
            data_off = file_base + ofs if flags & 2 else ofs
            norm = name if name.startswith("res://") else "res://" + name
            if not all(32 <= ord(c) < 127 for c in norm):
                res["reason"] = f"path parse lost sync at entry: {name!r}"
                return res
            entries.append({"path": norm, "offset": data_off, "size": size,
                            "eflags": eflags, "bounds_ok": data_off + size <= len(data)})
        res.update({"ok": True, "fmt": fmt, "version": [vmaj, vmin, vpat],
                    "flags": flags, "file_base": file_base,
                    "dir_offset": dir_offset, "count": count, "entries": entries})
    except struct.error as exc:
        res["reason"] = f"struct error: {exc!r}"
    return res


def extract_stored(out):
    stored = []
    for line in out.splitlines():
        m = STORED_RE.search(line)
        if m:
            p = ANSI_RE.sub("", m.group(1)).rstrip(",;")
            if not p.startswith("res://"):
                p = "res://" + p.lstrip("./")
            stored.append(p)
    return sorted(set(stored))


def data_only(seq):
    return sorted(p for p in seq if p.startswith("res://data/"))


def case_sensitive_from(sets):
    low, up = sets.get("INC_LOWER", []), sets.get("INC_UPPER", [])
    if low == ["res://data/alpha.txt"] and up == ["res://data/ALPHA.TXT"]:
        return True
    if low and low == up:
        return False
    return None


def fmt_line(arm, inc, exc, inc_set, exc_set, case_sensitive):
    cs = {True: "true", False: "false", None: "unknown"}[case_sensitive]
    return ("PASS export_launch_s04 arm=%s case_sensitive=%s inc_filter=%s "
            "exc_filter=%s inc_set=[%s] exc_set=[%s]"
            % (arm, cs, inc, exc, "|".join(inc_set), "|".join(exc_set)))


def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
    """Verbatim replica of run_battery.py:1775-1792 (r101 tree, read-only copy).
    allowed_errors is unused here (s04 pins no ERROR lines)."""
    lines = output.splitlines()

    def allowed_error(line, allowed):
        stripped = line.strip()
        if stripped == allowed:
            return True
        if allowed.endswith(","):
            return stripped.startswith(allowed) and stripped.count("ERROR:") == 1
        return False

    unrelated_errors = [line for line in lines if "ERROR:" in line
                        and not any(allowed_error(line, allowed)
                                    for allowed in allowed_errors)]
    return (code == expected_exit and error is None and signature in output
            and not unrelated_errors and "SCRIPT ERROR:" not in output
            and "Parse Error:" not in output)


def atomic_claims_hold(output, claims_in, claims_out):
    """Set-pin semantics over real census bytes: every claimed-present entry
    line occurs, every claimed-absent entry line does not."""
    present = all(("s04_entry: " + p) in output for p in claims_in)
    absent = all(("s04_entry: " + p) not in output for p in claims_out)
    return {"present": present, "absent": absent, "hold": present and absent}


def main():
    build_project()
    receipt = {"godot": GODOT, "root": ROOT, "arms": {}, "analysis": {}}

    # /tmp isolation probe (r101 E0: packer writes a fixed /tmp temp path).
    tmp_probe = run(["sh", "-c",
                     "dd if=/dev/zero of=/tmp/r102-mut8-probe bs=1M count=5 "
                     "2>/dev/null && rm -f /tmp/r102-mut8-probe"], 30)
    unshare = run(["unshare", "-m", "--map-root-user", "sh", "-c",
                   "mount -t tmpfs tmpfs /tmp && echo UNSHARE_OK"], 30)
    use_unshare = unshare["rc"] == 0 and "UNSHARE_OK" in unshare["out"]
    receipt["env"] = {"tmp_5mb_writable": tmp_probe["rc"] == 0,
                      "unshare_ok": use_unshare,
                      "tmp_probe_out": tmp_probe["out"][-200:],
                      "unshare_out": unshare["out"][-200:]}
    print(f"MUT08_ENV tmp_5mb_writable={tmp_probe['rc'] == 0} "
          f"unshare={use_unshare}")

    def godot_cmd(args):
        base = [GODOT] + args
        if use_unshare:
            return ["unshare", "-m", "--map-root-user", "sh", "-c",
                    "mount -t tmpfs tmpfs /tmp && exec " + shlex.join(base)]
        return base

    imp = run(godot_cmd(["--headless", "--path", PROJ, "--import"]), 180)
    print(f"MUT08_IMPORT rc={imp['rc']} secs={imp['secs']} timeouts={imp.get('timeout', False)}")
    receipt["import"] = {k: imp[k] for k in ("cmd", "rc", "secs")}
    receipt["import"]["tail"] = imp["out"][-500:]

    # Warmup export (r101 E0 cold-export anomaly: first export of an unimported
    # project is corrupt; measured packs are warm-warm).
    write_preset("*.md", "")
    warm = run(godot_cmd(["--headless", "--path", PROJ, "--export-pack", "s04",
                          os.path.join(OUT, "_warmup.pck")]), 180)
    warm_pck = os.path.join(OUT, "_warmup.pck")
    print(f"MUT08_WARMUP rc={warm['rc']} secs={warm['secs']} "
          f"bytes={os.path.getsize(warm_pck) if os.path.isfile(warm_pck) else 0}")
    receipt["warmup"] = {k: warm[k] for k in ("cmd", "rc", "secs")}

    for arm, inc, exc in ARMS:
        write_preset(inc, exc)
        pck = os.path.join(OUT, arm + ".pck")
        if os.path.isfile(pck):
            os.remove(pck)
        exp = run(godot_cmd(["--headless", "--path", PROJ, "--export-pack",
                             "s04", pck]), 180)
        entry = {"arm": arm, "include_filter": inc, "exclude_filter": exc,
                 "export_cmd": exp["cmd"], "export_rc": exp["rc"],
                 "export_secs": exp["secs"],
                 "export_timeout": exp.get("timeout", False),
                 "export_tail": exp["out"][-700:],
                 "artifact_bytes": 0, "sha256": None, "pck_ok": False,
                 "bin_entries": [], "engine_rc": None,
                 "engine_entries": [], "engine_raw": "", "log_stored": []}
        if os.path.isfile(pck) and os.path.getsize(pck) > 0:
            blob = open(pck, "rb").read()
            entry["artifact_bytes"] = len(blob)
            entry["sha256"] = hashlib.sha256(blob).hexdigest()
            binr = parse_pck(blob)
            entry["pck_ok"] = binr["ok"]
            entry["pck_reason"] = binr.get("reason")
            entry["bin_entries"] = sorted(e["path"] for e in binr.get("entries", []))
            eng = run(godot_cmd(["--headless", "--main-pack", pck,
                                 "--quit-after", "3"]), 120)
            entry["engine_rc"] = eng["rc"]
            entry["engine_timeout"] = eng.get("timeout", False)
            entry["engine_entries"] = sorted(ENGINE_RE.findall(eng["out"]))
            entry["engine_raw"] = eng["out"]
        entry["log_stored"] = extract_stored(exp["out"])
        entry["in_engine"] = data_only(entry["engine_entries"])
        entry["in_bin"] = data_only(entry["bin_entries"])
        entry["in_log"] = data_only(entry["log_stored"])
        census_agree = (entry["in_engine"] == entry["in_bin"] == entry["in_log"])
        entry["census_agree"] = census_agree
        print(f"MUT08_ARM arm={arm} inc={inc!r} exc={exc!r} "
              f"export_rc={entry['export_rc']} secs={entry['export_secs']} "
              f"bytes={entry['artifact_bytes']} sha={entry['sha256']}")
        print(f"MUT08_CENSUS arm={arm} engine={json.dumps(entry['in_engine'])} "
              f"bin={json.dumps(entry['in_bin'])} log={json.dumps(entry['in_log'])} "
              f"agree={census_agree}")
        receipt["arms"][arm] = entry

    # Warm-warm determinism (r101 law): same-root re-exports byte-identical;
    # the case-flip pair must stay byte-identical in sample 2 as well.
    det = {}
    for arm in ("XCONFLICT", "XCONFLICT_INV"):
        inc, exc = [(i, e) for (a, i, e) in ARMS if a == arm][0]
        write_preset(inc, exc)
        pck = os.path.join(OUT, arm + "_s2.pck")
        if os.path.isfile(pck):
            os.remove(pck)
        r2 = run(godot_cmd(["--headless", "--path", PROJ, "--export-pack",
                            "s04", pck]), 180)
        sha2 = hashlib.sha256(open(pck, "rb").read()).hexdigest() if os.path.isfile(pck) else None
        det[arm] = {"rc": r2["rc"], "sha256_sample2": sha2,
                    "sample1": receipt["arms"][arm]["sha256"],
                    "stable": sha2 == receipt["arms"][arm]["sha256"]}
        print(f"MUT08_DETERMINISM arm={arm} sample2_rc={r2['rc']} "
              f"sha_equal={det[arm]['stable']} sha2={sha2}")
    det["caseflip_pair_byte_identical_sample2"] = (
        det["XCONFLICT"]["sha256_sample2"] == det["XCONFLICT_INV"]["sha256_sample2"])
    receipt["analysis"]["determinism"] = det
    print(f"MUT08_CASEFLIP_PAIR sample2_identical={det['caseflip_pair_byte_identical_sample2']}")

    sets = {a: receipt["arms"][a]["in_engine"] for a, _, _ in ARMS}
    cs = case_sensitive_from(sets)
    print(f"MUT08_CASE_SENSITIVE derived={cs} sets={json.dumps(sets, sort_keys=True)}")
    receipt["analysis"]["case_sensitive"] = cs

    # ---- A. case-flip artifact inversion: honest XCONFLICT pin vs mutant bytes.
    hon = receipt["arms"]["XCONFLICT"]
    mut = receipt["arms"]["XCONFLICT_INV"]
    hon_in = hon["in_engine"]
    hon_out = [p for p in DATA_DOMAIN if p not in hon_in]
    hon_line = fmt_line("XCONFLICT", hon["include_filter"], hon["exclude_filter"],
                        hon_in, hon_out, cs)
    mut_in = mut["in_engine"]
    mut_out = [p for p in DATA_DOMAIN if p not in mut_in]
    mut_line = fmt_line("XCONFLICT_INV", mut["include_filter"],
                        mut["exclude_filter"], mut_in, mut_out, cs)
    artifact = {
        "honest_line": hon_line,
        "mutant_line": mut_line,
        "honest_expectation_accepts_honest_output":
            classify_process(0, None, hon_line + "\n", 0, hon_line),
        "honest_expectation_accepts_mutant_output":
            classify_process(0, None, mut_line + "\n", 0, hon_line),
        "honest_include_entry_in_mutant_census":
            all(("s04_entry: " + p) in mut["engine_raw"] for p in hon_in),
        "mutant_real_include": mut_in,
        "sets_differ": hon_in != mut_in,
        "sha_equal": hon["sha256"] == mut["sha256"],
        "bytes_equal": hon["artifact_bytes"] == mut["artifact_bytes"],
    }
    print(f"MUT08_ARTIFACT_INVERSION {json.dumps(artifact, sort_keys=True)}")
    receipt["analysis"]["artifact_inversion"] = artifact

    # ---- A2. artifact-visible control: ROLE_SWAP (*.md in / *.txt out) is the
    # value-inversion of INC_LOWER whose real census differs; the honest
    # INC_LOWER expectation must reject it on real bytes.
    role = receipt["arms"]["ROLE_SWAP"]
    role_in = role["in_engine"]
    role_out = [p for p in DATA_DOMAIN if p not in role_in]
    role_line = fmt_line("ROLE_SWAP", role["include_filter"],
                         role["exclude_filter"], role_in, role_out, cs)
    a2 = {
        "role_line": role_line,
        "role_census_differs_from_inc_lower": role_in != sets["INC_LOWER"],
        "honest_inc_lower_entries_in_role_census":
            all(("s04_entry: " + p) in role["engine_raw"] for p in sets["INC_LOWER"]),
        "honest_expectation_accepts_role_output":
            classify_process(0, None, role_line + "\n", 0, hon_line),
    }
    print(f"MUT08_ROLE_SWAP_CONTROL {json.dumps(a2, sort_keys=True)}")
    receipt["analysis"]["role_swap_control"] = a2

    # ---- B. expectation-level inversion on every honest arm: swap the
    # expected include set with the expected exclude set; claims are evaluated
    # against that arm's REAL captured engine bytes.
    expectation = {}
    for arm, inc, exc in ARMS[:3]:
        e = receipt["arms"][arm]
        inc_set = e["in_engine"]
        exc_set = [p for p in DATA_DOMAIN if p not in inc_set]
        honest_line = fmt_line(arm, inc, exc, inc_set, exc_set, cs)
        swapped_line = fmt_line(arm, inc, exc, exc_set, inc_set, cs)
        raw = e["engine_raw"]
        honest_claims = atomic_claims_hold(raw, inc_set, exc_set)
        swapped_claims = atomic_claims_hold(raw, exc_set, inc_set)
        row_rejects_swapped_fixture = not classify_process(
            0, None, swapped_line + "\n", 0, honest_line)
        row = {
            "honest_line": honest_line,
            "swapped_line": swapped_line,
            "line_content_swapped": honest_line != swapped_line,
            "honest_atomic_claims": honest_claims,
            "swapped_atomic_claims": swapped_claims,
            "honest_whole_line_in_engine_stdout":
                classify_process(0, None, raw, 0, honest_line),
            "swapped_whole_line_in_engine_stdout":
                classify_process(0, None, raw, 0, swapped_line),
            "row_rejects_swapped_line_fixture": row_rejects_swapped_fixture,
            "swapped_rejected": bool(honest_claims["hold"]
                                     and not swapped_claims["hold"]
                                     and row_rejects_swapped_fixture),
        }
        print(f"MUT08_EXPECTATION_SWAP arm={arm} "
              f"swapped_rejected={row['swapped_rejected']} "
              f"honest_atomic={honest_claims['hold']} "
              f"swapped_atomic={swapped_claims['hold']} "
              f"row_rejects_swapped_fixture={row_rejects_swapped_fixture}")
        expectation[arm] = row
    receipt["analysis"]["expectation_swap"] = expectation

    # ---- C. escape analysis / honesty.
    md_low = receipt["arms"]["MD_LOWER"]["in_engine"]
    md_up = receipt["arms"]["MD_UPPER"]["in_engine"]
    if md_low == md_up == ["res://data/notes.md"]:
        cs2 = False
    elif md_low == ["res://data/notes.md"] and md_up == []:
        cs2 = True
    else:
        cs2 = None
    verdict = {
        "case_semantics": {True: "case_sensitive", False: "case_insensitive",
                           None: "undetermined"}[cs],
        "case_semantics_second_extension": {True: "case_sensitive",
                                            False: "case_insensitive",
                                            None: "undetermined"}[cs2],
        "case_flip_mutant_byte_identical": (hon["sha256"] == mut["sha256"]),
        "case_flip_detectable_from_artifacts": not (hon["sha256"] == mut["sha256"]),
        "expectation_swap_rejected_all_honest_arms": all(
            v["swapped_rejected"] and not v["swapped_whole_line_in_engine_stdout"]
            for v in expectation.values()),
        "role_swap_artifact_inversion_rejected": bool(
            not a2["honest_expectation_accepts_role_output"]
            and not a2["honest_inc_lower_entries_in_role_census"]
            and a2["role_census_differs_from_inc_lower"]),
        "triangulation_ok": all(receipt["arms"][a]["census_agree"] for a, _, _ in ARMS),
    }
    print("MUT08_VERDICT " + json.dumps(verdict, sort_keys=True))
    receipt["verdict"] = verdict
    path = os.path.join(ROOT, "receipt.json")
    with open(path, "w") as fh:
        json.dump(receipt, fh, indent=1)
    print(f"MUT08_RECEIPT {path}")


if __name__ == "__main__":
    main()
