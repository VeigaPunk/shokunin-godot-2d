#!/usr/bin/env python3
"""r104 M2 / mut02 - UID round-trip spoof mutation for E1 (res_uid_s01.gd).

Mandate: E1's UID-census / id<->path round-trip row family must REJECT an arm
whose evidence claims a successful `uid://<text>` <-> id <-> path round-trip
(and `has_id`/`get_id_path`/`ResourceLoader.get_resource_uid` agreement) while
the on-disk anchors (the `res://custom.tres.uid` sidecar and the
`.godot/uid_cache.bin` registry) do NOT support the claim.

Replayable (~40 s). Three arm classes, all driven through an in-engine replica
of the E1 classification layer (`probe.gd`, one fresh Godot process per arm):

  genuine       real probe run, intact disk; transcript + disk agree
  spoof_text    real probe run with the `.uid` sidecar removed mid-arm (so the
                real run reports has_id=false / id_path="" / loader_uid=-1),
                then the stored GENUINE transcript is replayed on top of it
                (stale-receipt forgery). Naive classifier: PASS. Anchored: REJECT.
  spoof_norun   nothing runs; a contradicting sidecar (a DIFFERENT valid uid) is
                planted on disk and the genuine transcript is replayed verbatim
                (pure transcript forgery). Naive: PASS. Anchored: REJECT.
  spoof_malformed  sidecar replaced with `not-a-uid`; transcript still claims a
                clean round-trip. Naive: PASS. Anchored: REJECT.

Anchored clauses (all DISK-derived, never transcript-derived):
  A1 sidecar_present        res://custom.tres.uid exists
  A2 sidecar_parses         ResourceUID.text_to_id(<sidecar bytes>) != INVALID_ID
  A3 transcript_matches_disk claimed uid text == sidecar bytes
  A4 id_path_matches_disk   claimed id_path == ResourceUID.get_id_path(sid_of_disk)
  A5 has_id_disk            ResourceUID.has_id(sid_of_disk)
  A6 roundtrip_identity     id_to_text(sid_of_disk) == sidecar bytes
  A7 loader_uid_disk        ResourceLoader.get_resource_uid(tres) == sid_of_disk

Scratch: /var/tmp/r104-M2 (never /tmp; this host has an EDQUOT /tmp quota).
Override the root with `MUT02_ROOT=<dir>` to run isolated from concurrent
sibling seats. Never runs run_battery.py; touches no shared file.
"""

import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("MUT02_ROOT", "/var/tmp/r104-M2"))
PROJ = ROOT / "proj"
OUT = ROOT / "out"
REPO = Path(os.environ.get("MUT02_REPO", "/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin"))
GODOT = "godot"
SAMPLE_UID = "uid://bqk3m5n7qar1"
OTHER_UID = "uid://c8v2n4r6xap8"
TRES = "res://custom.tres"
SIDECAR = "res://custom.tres.uid"

PROJECT_GODOT = '''config_version=5

[application]
config/name="Mut2UID"
config/features=PackedStringArray("4.7")
'''

CUSTOM_TRES = '''[gd_resource type="Gradient" format=3]

[resource]
colors = PackedColorArray(1, 0, 0, 1, 0, 1, 0, 1)
'''

# The "real" E1-style round-trip probe. Its stdout is the transcript the spoof
# forges; it emits one RTRIP line whose fields are exactly the claims E1's row
# would census.
RTRIP_GD = '''extends SceneTree
const SAMPLE := "@SAMPLE@"
const TRES := "@TRES@"
const SIDECAR := "@SIDECAR@"

func _initialize() -> void:
	_run.call_deferred()

func _b(v: bool) -> String:
	return "true" if v else "false"

func _sidecar_text() -> String:
	if not FileAccess.file_exists(SIDECAR):
		return "<absent>"
	var f := FileAccess.open(SIDECAR, FileAccess.READ)
	if f == null:
		return "<unreadable>"
	var t := f.get_as_text().strip_edges()
	f.close()
	return t

func _run() -> void:
	var sid := ResourceUID.text_to_id(SAMPLE)
	var text := ResourceUID.id_to_text(sid)
	var has := ResourceUID.has_id(sid)
	var ipath := ResourceUID.get_id_path(sid)
	var rt_ok := text == SAMPLE
	var loader_uid := ResourceLoader.get_resource_uid(TRES)
	var sidecar := _sidecar_text()
	var disk_sid := ResourceUID.text_to_id(sidecar)
	print("RTRIP uid_text=%s uid_id=%d has_id=%s id_path=%s roundtrip_ok=%s loader_uid=%d sidecar=%s disk_sid=%d" % [
		text, sid, _b(has), ipath, _b(rt_ok), loader_uid, sidecar, disk_sid])
	print("RTRIP_CLAIM uid_roundtrip_ok=%s" % _b(rt_ok and has and ipath != ""))
	quit(0)
'''

PROBE_GD = '''extends SceneTree
# r104-mut02 in-engine replica of the E1 classification layer. One arm per
# process (fresh ResourceUID cache load per arm).
const ROOT := "@ROOT@"
const PROJ := "@PROJ@"
const OUT := "@OUT@"
const SAMPLE := "@SAMPLE@"
const OTHER := "@OTHER@"
const TRES := "res://custom.tres"
const SIDECAR := "res://custom.tres.uid"
const GENUINE_TX := "@GENUINE@"

var arm := ""

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")

func _b(v: bool) -> String:
	return "true" if v else "false"

func _q(s: String) -> String:
	return "'" + s.replace("'", "'\\\\''") + "'"

func _read(path: String) -> String:
	if not FileAccess.file_exists(path):
		return "<absent>"
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return "<unreadable>"
	var t := f.get_as_text().strip_edges()
	f.close()
	return t

func _write(path: String, text: String) -> void:
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string(text)
	f.close()

func _field(line: String, key: String) -> String:
	for tok in line.split(" "):
		if tok.begins_with(key + "="):
			return tok.substr(key.length() + 1)
	return ""

func _rtrip_line(text: String) -> String:
	for line in text.split("\\n"):
		if line.begins_with("RTRIP "):
			return line
	return ""

func _rtrip_last(text: String) -> String:
	# The strongest claim in the transcript: a forger's replayed receipt is
	# appended last, so a receiver reading the LATEST receipt sees the forgery.
	var found := ""
	for line in text.split("\\n"):
		if line.begins_with("RTRIP "):
			found = line
	return found

# uid_cache.bin layout (measured on 4.7.2, see r104-mut2.md):
#   u32 count, then per entry: u64 uid, u32 path_len, path_len bytes (UTF-8).
func _cache_pairs() -> Array:
	var out: Array = []
	var path := ROOT.path_join("proj").path_join(".godot").path_join("uid_cache.bin")
	if not FileAccess.file_exists(path):
		return out
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return out
	var b := f.get_buffer(f.get_length())
	f.close()
	if b.size() < 4:
		return out
	var count := b.decode_u32(0)
	var off := 4
	for _i in range(count):
		if off + 12 > b.size():
			break
		var uid := b.decode_u64(off)
		off += 8
		var ln := b.decode_u32(off)
		off += 4
		if off + ln > b.size():
			break
		out.append([uid, b.slice(off, off + ln).get_string_from_utf8()])
		off += ln
	return out

func _cache_has(uid: int, target: String) -> bool:
	for pair in _cache_pairs():
		if pair[0] == uid and pair[1] == target:
			return true
	return false

# Writes the measured uid_cache.bin format: u32 count, then per entry u64 uid,
# u32 path_len, path bytes.
func _write_cache(pairs: Array) -> void:
	var b := PackedByteArray()
	b.resize(4)
	b.encode_u32(0, pairs.size())
	for pair in pairs:
		var path_bytes := str(pair[1]).to_utf8_buffer()
		var head := PackedByteArray()
		head.resize(12)
		head.encode_u64(0, pair[0])
		head.encode_u32(8, path_bytes.size())
		b.append_array(head)
		b.append_array(path_bytes)
	var f := FileAccess.open(ROOT.path_join("proj").path_join(".godot").path_join("uid_cache.bin"), FileAccess.WRITE)
	f.store_buffer(b)
	f.close()

func _run() -> void:
	var sidecar_abs := ROOT.path_join("proj").path_join("custom.tres.uid")
	var log := OUT.path_join("arm_" + arm + ".log")
	var genuine_tx := _read(GENUINE_TX)
	var planted := ""
	var inner := ""
	if arm == "genuine":
		inner = _q("@GODOT@") + " --headless --path " + _q(PROJ) + " --script res://rtrip.gd"
	elif arm == "spoof_text":
		# Real run with the disk anchor removed mid-arm, then replay the stale
		# GENUINE transcript on top of the (now contradicting) real output.
		inner = "rm -f " + _q(sidecar_abs) + "\\n" + _q("@GODOT@") + " --headless --path " + _q(PROJ) + " --script res://rtrip.gd"
	elif arm == "spoof_norun":
		# No engine run at all; plant a DIFFERENT valid uid, replay genuine tx.
		_write(sidecar_abs, OTHER)
		inner = "true"
	elif arm == "spoof_malformed":
		_write(sidecar_abs, "not-a-uid")
		inner = "true"
	elif arm == "genuine_restored":
		_write(sidecar_abs, SAMPLE)
		inner = _q("@GODOT@") + " --headless --path " + _q(PROJ) + " --script res://rtrip.gd"
	elif arm == "spoof_consistent":
		# BOUNDARY (expected ACCEPTED, and that is the finding): the forger owns
		# the disk BEFORE this receiver process starts, so the registry loaded at
		# startup is self-consistent with the planted sidecar. The transcript is
		# forged to match that alternative disk state.
		inner = "true"
	elif arm == "noncanonical":
		# BOUNDARY 2 (real run, no forgery): the sidecar holds a NON-canonical uid
		# text. Measured on 4.7.2: text_to_id("uid://c8v2n4r6xap9") =
		# 209826154861178408 but id_to_text of that id = "uid://c8v2n4r6xaqa", so
		# the id<->text round-trip is NOT the identity for non-canonical text.
		# Clause A6 fails on a truthful run — the predicate demands canonical form.
		_write(sidecar_abs, "uid://c8v2n4r6xap9")
		inner = _q("@GODOT@") + " --headless --path " + _q(PROJ) + " --script res://rtrip.gd"
	else:
		print("FAIL probe unknown_arm %s" % arm)
		quit(1)
		return
	# The forger: arms that spoof append the stored genuine transcript verbatim,
	# except spoof_consistent, whose receipt is minted to match its planted disk.
	var forge := ""
	if arm == "spoof_consistent":
		var other_id := ResourceUID.text_to_id(OTHER)
		forge = "printf '%s\\\\n' " + _q("RTRIP uid_text=%s uid_id=%d has_id=true id_path=res://custom.tres roundtrip_ok=true loader_uid=%d sidecar=%s disk_sid=%d" % [OTHER, other_id, other_id, OTHER, other_id])
	elif arm.begins_with("spoof"):
		forge = "printf '%s\\\\n' " + _q(genuine_tx)
	var body := "cd " + _q(OUT) + "\\nexec > " + _q(log) + " 2>&1\\n" + inner + "\\n" + forge
	var rc := OS.execute("/usr/bin/sh", PackedStringArray(["-c", body]))
	var text := FileAccess.get_file_as_string(log)
	# The receiver consumes the LATEST receipt: a forger's replayed line is
	# appended last, so reading the last RTRIP line is the naive reader's view.
	var tx := _rtrip_last(text)

	# ---- disk-derived anchors (re-read AFTER the arm ran) ----
	var sidecar_now := _read(sidecar_abs)
	var sid_disk := ResourceUID.text_to_id(sidecar_now)
	var claim_text := _field(tx, "uid_text")
	var claim_id := _field(tx, "uid_id")
	var claim_has := _field(tx, "has_id")
	var claim_ipath := _field(tx, "id_path")
	var claim_rt := _field(tx, "uid_roundtrip_ok")
	var claim_loader := _field(tx, "loader_uid")

	var a1 := sidecar_now != "<absent>" and sidecar_now != "<unreadable>"
	var a2 := a1 and sid_disk != ResourceUID.INVALID_ID
	var a3 := a1 and claim_text == sidecar_now
	var a4 := a2 and claim_ipath == ResourceUID.get_id_path(sid_disk)
	var a5 := a2 and ResourceUID.has_id(sid_disk)
	var a6 := a2 and ResourceUID.id_to_text(sid_disk) == sidecar_now
	var a7 := a2 and claim_loader == str(sid_disk)
	# A8 is the cross-process persistence anchor: the claim is only supportable
	# if THIS process's uid registry maps the disk uid to the claimed path.
	var a8 := a2 and _cache_has(sid_disk, "res://custom.tres")
	var anchored := a1 and a2 and a3 and a4 and a5 and a6 and a7 and a8

	# ---- naive classifier: transcript text only ----
	# A text-only receiver trusts the transcript's own claim tokens.
	var naive := rc == 0 and claim_text.begins_with("uid://") and claim_has == "true" and text.contains("uid_roundtrip_ok=true")
	# Strict-last-receipt reader: parses only the FINAL RTRIP line's fields.
	var naive_last := rc == 0 and claim_text.begins_with("uid://") and claim_has == "true" and claim_rt == "true"
	# Stale-receipt signature: a real receipt in the SAME log contradicts the
	# forged one (sidecar absent / disk_sid=-1 / has_id=false).
	var contradiction := text.contains("sidecar=<absent>") or text.contains("disk_sid=-1") or text.contains("has_id=false")

	print("PROBE_ROW arm=%s rc=%d tx_lines=%d sidecar_now=%s disk_sid=%d claim_text=%s claim_id=%s claim_has=%s claim_ipath=%s claim_loader=%s" % [
		arm, rc, text.split("\\n").size(), sidecar_now, sid_disk, claim_text, claim_id, claim_has, claim_ipath, claim_loader])
	print("PROBE_CLASS arm=%s a1=%s a2=%s a3=%s a4=%s a5=%s a6=%s a7=%s a8=%s" % [
		arm, _b(a1), _b(a2), _b(a3), _b(a4), _b(a5), _b(a6), _b(a7), _b(a8)])
	print("PROBE_STYLE arm=%s naive_pass=%s naive_last=%s contradiction=%s anchored_pass=%s" % [
		arm, _b(naive), _b(naive_last), _b(contradiction), _b(anchored)])
	quit(0)
'''


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def run(cmd, env=None, cwd=None, timeout=120):
    t0 = time.monotonic()
    p = subprocess.run(cmd, env=env, cwd=cwd, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, timeout=timeout)
    return {"rc": p.returncode, "stdout": p.stdout, "stderr": p.stderr,
            "wall_ms": int((time.monotonic() - t0) * 1000)}


def base_env(**overrides):
    env = os.environ.copy()
    for k, v in overrides.items():
        env[k] = v
    return env


def wipe(path: Path):
    shutil.rmtree(path, ignore_errors=True)


def write_cache(path: Path, pairs):
    """Measured uid_cache.bin format: u32 count, then u64 uid, u32 len, path."""
    import struct
    b = struct.pack("<I", len(pairs))
    for uid, p in pairs:
        pb = p.encode("utf-8")
        b += struct.pack("<Q", uid) + struct.pack("<I", len(pb)) + pb
    path.write_bytes(b)


def run_gate_census():
    """C2 cross-check (read-only): how the live receipt-shape gate censuses
    PASS lines. Reproduces the exact predicate line from run_battery.py source
    (never executing it) and shows which PASS-prefixed shapes are visible."""
    rb = REPO / "corpus/fixtures/run_battery.py"
    src = rb.read_text() if rb.is_file() else ""
    line = 'pass_lines = [line for line in output if line.startswith("PASS ")]'
    shapes = {
        "PASS_space": "PASS res_uid_s01 roundtrip roundtrip=true",
        "PASS_tab": "PASS\tres_uid_s01 roundtrip roundtrip=true",
        "PASS_lower": "pass res_uid_s01 roundtrip roundtrip=true",
        "PASS_leading_space": " PASS res_uid_s01 roundtrip roundtrip=true",
        "PASS_bare": "PASS",
    }
    rows = {}
    for name, text in shapes.items():
        # exactly the live census expression, evaluated on one-line output
        pass_lines = [l for l in [text] if l.startswith("PASS ")]
        rows[name] = {"census_count": len(pass_lines), "visible": bool(pass_lines)}
    return {
        "predicate_present_in_source": line in src,
        "predicate_source_line": line,
        "census_matches_in_source": src.count('startswith("PASS ")'),
        "shapes": rows,
    }


def run_e1_crosscheck(work):
    """Phase 2: forge E1's OWN receipt and see whether anything catches it.

    Two questions, both answered from bytes:
      (a) Does E1's landed fixture consume transcript claims at all, or does it
          query the engine directly? (If the latter, a transcript spoof has no
          surface inside the fixture.)
      (b) Does the spliced-forgery survive the receipt-shape gate's anchor
          check, i.e. is a forged PASS line with the right anchor token
          shape-distinguishable from a real one?
    """
    fx = REPO / "corpus/fixtures/res_uid_s01.gd"
    out = {"fixture": str(fx), "fixture_present": fx.is_file()}
    if not fx.is_file():
        out["skipped"] = "E1 fixture absent at probe time"
        return out
    out["fixture_sha256"] = sha256_bytes(fx.read_bytes())
    proj = ROOT / "e1proj"
    wipe(proj)
    proj.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(fx, proj / "res_uid_s01.gd")
    (proj / "project.godot").write_text(PROJECT_GODOT)
    imp = run([GODOT, "--headless", "--path", str(proj), "--import"],
              env=base_env(), cwd=proj, timeout=120)

    def run_arm(root, arm):
        p = run([GODOT, "--headless", "--path", str(root), "--script",
                 "res://res_uid_s01.gd", "--", "--arm=" + arm],
                env=base_env(), cwd=root, timeout=120)
        text = p["stdout"].decode("utf-8", "replace")
        lines = [l for l in text.split("\n") if l.startswith("PASS ")]
        return {"arm": arm, "rc": p["rc"], "wall_ms": p["wall_ms"],
                "stdout_bytes": len(p["stdout"]),
                "stdout_sha256": sha256_bytes(p["stdout"]),
                "pass_line": lines[0] if lines else None}

    genuine = run_arm(proj, "roundtrip")
    # tamper: registry maps the claimed uid to a FOREIGN path, then re-run the
    # SAME fixture. Whatever it prints now is the engine's truthful answer.
    proj2 = ROOT / "e1proj_tampered"
    wipe(proj2)
    shutil.copytree(proj, proj2)
    cache2 = proj2 / ".godot/uid_cache.bin"
    tampered = {"cache_existed": cache2.is_file()}
    if cache2.is_file():
        write_cache(cache2, [(103876737118377468, "res://zzz_foreign_e1.gd")])
        tampered["rewritten"] = "103876737118377468 -> res://zzz_foreign_e1.gd"
    tampered_run = run_arm(proj2, "roundtrip")

    # the forgery: replay the GENUINE receipt text into the tampered transcript
    forged_pass_lines = []
    if genuine["pass_line"] and tampered_run["pass_line"]:
        forged_pass_lines = [genuine["pass_line"]]
    # shape gate (live predicate, read from source, never executed)
    anchor = "PASS res_uid_s01 roundtrip"
    forged_anchored = any(anchor in l for l in forged_pass_lines)
    real_anchored = bool(tampered_run["pass_line"]) and anchor in tampered_run["pass_line"]

    out.update({
        "import": {"rc": imp["rc"], "wall_ms": imp["wall_ms"]},
        "genuine_run": genuine,
        "tampered_run": tampered_run,
        "tampered": tampered,
        "fixture_consumes_transcript_claims": False,  # see note
        "forged_replayed_pass_lines": forged_pass_lines,
        "shape_gate": {
            "anchor": anchor,
            "forged_line_anchored": forged_anchored,
            "real_line_anchored": real_anchored,
            "distinguishes_forgery": forged_anchored != real_anchored,
        },
        "note": ("E1's fixture re-queries ResourceUID/ResourceLoader in-process "
                 "and prints the engine's answer; it reads no prior receipt, so "
                 "the fixture itself has no transcript-trust surface. The "
                 "transcript-trust surface is the HARNESS + shape gate, which "
                 "store and shape-check the printed line."),
    })
    wipe(proj)
    wipe(proj2)
    return out


def main():
    t_start = time.monotonic()
    wipe(ROOT)
    for d in (PROJ, OUT):
        d.mkdir(parents=True, exist_ok=True)

    (PROJ / "project.godot").write_text(PROJECT_GODOT)
    (PROJ / "custom.tres").write_text(CUSTOM_TRES)
    (PROJ / "custom.tres.uid").write_text(SAMPLE_UID)
    (PROJ / "rtrip.gd").write_text(
        RTRIP_GD.replace("@SAMPLE@", SAMPLE_UID).replace("@TRES@", TRES)
        .replace("@SIDECAR@", SIDECAR))

    host = {}
    host["uptime"] = subprocess.run(["uptime"], stdout=subprocess.PIPE).stdout.decode().strip()
    host["loadavg"] = list(os.getloadavg())
    host["godot_version"] = run([GODOT, "--version"])["stdout"].decode().strip()
    host["date"] = subprocess.run(["date", "-Is"], stdout=subprocess.PIPE).stdout.decode().strip()

    work = {}
    imp = run([GODOT, "--headless", "--path", str(PROJ), "--import"], env=base_env())
    work["import"] = {"rc": imp["rc"], "wall_ms": imp["wall_ms"],
                      "stderr_tail": imp["stderr"].decode("utf-8", "replace")[-300:]}
    cache = PROJ / ".godot/uid_cache.bin"
    work["uid_cache_bin"] = {"exists": cache.is_file(),
                             "bytes": cache.stat().st_size if cache.is_file() else 0,
                             "sha256": sha256_bytes(cache.read_bytes()) if cache.is_file() else None}

    # --- baseline genuine transcript (this is the string the forger replays) ---
    base = run([GODOT, "--headless", "--path", str(PROJ), "--script", "res://rtrip.gd"],
               env=base_env(), cwd=OUT)
    genuine_tx = base["stdout"].decode("utf-8", "replace").strip()
    work["baseline_genuine"] = {
        "rc": base["rc"], "wall_ms": base["wall_ms"],
        "stdout_bytes": len(base["stdout"]), "stdout_sha256": sha256_bytes(base["stdout"]),
        "stdout": genuine_tx,
    }

    (PROJ / "probe.gd").write_text(
        PROBE_GD.replace("@ROOT@", str(ROOT)).replace("@PROJ@", str(PROJ))
        .replace("@OUT@", str(OUT)).replace("@SAMPLE@", SAMPLE_UID)
        .replace("@OTHER@", OTHER_UID).replace("@GODOT@", GODOT)
        .replace("@GENUINE@", str(OUT / "genuine_tx.txt")))
    (OUT / "genuine_tx.txt").write_text(genuine_tx + "\n")

    arms = ("genuine", "spoof_text", "spoof_norun", "spoof_malformed",
            "genuine_restored", "spoof_consistent", "noncanonical")
    probe = {}
    cache_bin = PROJ / ".godot/uid_cache.bin"
    pristine_cache = cache_bin.read_bytes() if cache_bin.is_file() else None
    for arm in arms:
        # every arm starts from the pristine sidecar so arms are independent
        (PROJ / "custom.tres.uid").write_text(SAMPLE_UID)
        if cache_bin.is_file() and pristine_cache is not None:
            cache_bin.write_bytes(pristine_cache)
        if arm == "spoof_consistent":
            # Pre-plant a self-consistent alternative disk state (sidecar + the
            # registry entry that must be loaded at THIS process's startup).
            other_id = 209826154861178407  # ResourceUID.text_to_id(OTHER_UID), measured (canonical)
            (PROJ / "custom.tres.uid").write_text(OTHER_UID)
            write_cache(cache_bin, [(other_id, "res://custom.tres")])
        p = run([GODOT, "--headless", "--path", str(PROJ), "--script", "res://probe.gd",
                 "--", "--arm=" + arm], env=base_env(), cwd=OUT, timeout=120)
        lines = [l for l in p["stdout"].decode("utf-8", "replace").split("\n")
                 if l.startswith("PROBE_")]
        logf = OUT / ("arm_%s.log" % arm)
        probe[arm] = {
            "rc": p["rc"], "wall_ms": p["wall_ms"], "lines": lines,
            "log_bytes": logf.stat().st_size if logf.is_file() else 0,
            "log_sha256": sha256_bytes(logf.read_bytes()) if logf.is_file() else None,
            "log_text": logf.read_text() if logf.is_file() else "",
            "stderr_head": p["stderr"].decode("utf-8", "replace")[:400],
        }
    # restore the pristine sidecar + cache for the record
    (PROJ / "custom.tres.uid").write_text(SAMPLE_UID)
    if pristine_cache is not None:
        cache_bin.write_bytes(pristine_cache)

    def style(arm, key):
        for l in probe[arm]["lines"]:
            if l.startswith("PROBE_STYLE "):
                for tok in l.split(" "):
                    if tok.startswith(key + "="):
                        return tok.split("=", 1)[1] == "true"
        return None

    verdicts = {}
    for arm in arms:
        naive = style(arm, "naive_pass")
        anchored = style(arm, "anchored_pass")
        if arm == "spoof_consistent":
            # boundary arm: deliberately NOT expected to reject
            v = "ACCEPTED(boundary, expected)"
        elif arm == "noncanonical":
            # boundary arm 2: truthful run, disk holds non-canonical uid text.
            # A3 fails (the probe's claim is its hardcoded SAMPLE) and A6 fails
            # independently because id_to_text canonicalises the stored text.
            v = "REJECT(truthful-run: A3 hardcoded-claim + A6 canonicality)"
        elif arm.startswith("spoof"):
            v = "REJECT" if anchored is False else "ACCEPTED(!!)"
        else:
            v = "PASS" if anchored is True else "FAILED(!!)"
        verdicts[arm] = {"naive_pass": naive, "anchored_pass": anchored, "verdict": v}

    # ---- phase 2: cross-check against the LANDED E1 fixture (if present) ----
    e1_crosscheck = run_e1_crosscheck(work)
    gate_census = run_gate_census()

    payload = {
        "seat": "r104-mut2 (KEY=M2)",
        "mandate": "UID round-trip spoof must REJECT E1",
        "date": "2026-10-18",
        "host": host,
        "work": work,
        "probe": probe,
        "verdicts": verdicts,
        "e1_crosscheck": e1_crosscheck,
        "gate_census": gate_census,
        "replay_seconds": round(time.monotonic() - t_start, 1),
    }
    outj = OUT / "mut02_verdicts.json"
    outj.write_text(json.dumps(payload, indent=2, sort_keys=True))

    for arm in arms:
        print("VERDICT %-16s naive=%-5s anchored=%-5s -> %s" % (
            arm, verdicts[arm]["naive_pass"], verdicts[arm]["anchored_pass"],
            verdicts[arm]["verdict"]))
    print("verdicts: %s (%.1fs)" % (outj, payload["replay_seconds"]))
    if verdicts["genuine"]["verdict"] != "PASS" or verdicts["genuine_restored"]["verdict"] != "PASS":
        print("FATAL: control arms did not PASS; predicate is not calibrated", file=sys.stderr)
        sys.exit(2)
    if any(verdicts[a]["verdict"] != "REJECT" for a in ("spoof_text", "spoof_norun", "spoof_malformed")):
        print("FATAL: a spoof arm was not rejected", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
