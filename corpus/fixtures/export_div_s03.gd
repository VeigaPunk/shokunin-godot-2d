extends SceneTree
# export_div_s03 — r103 C1: multi-preset sequential export fidelity (seat E3).
#
# Scenario: ONE scratch project carrying two Linux/X11 presets whose
# non-resource include filters are disjoint single-file beacons —
#   PckOnly  embed_pck=false  include tag_pck_only.txt   exclude tag_embed_only.txt
#   Embed    embed_pck=true   include tag_embed_only.txt exclude tag_pck_only.txt
# — exports with `--export-pack` (pack-only: the ~2 KB pack IS the receipt
# surface, the 70+ MB template binary never enters the flow) several presets
# one after another against one shared project dir / one `.godot` cache. The
# divergence surface is cross-contamination: after preset N-1 exported, preset
# N's pack must still carry exactly its own 15-byte beacon entry (name AND
# content byte-verified from the pack's own directory) and no trace of the
# foreign beacon name or content.
#
#   arm=seq  (row export_div_s03_multi_preset_seq)
#     A(PckOnly) then B(Embed) in one fixture session; both packs must exist
#     simultaneously in <vdir>/out, each carrying only its own beacon.
#   arm=order (row export_div_s03_order_invariance)
#     B then A (reverse order, same project dir); each pack byte-compared
#     (sha256) against the arm=seq pack for the SAME preset. Requires seq's
#     artifacts in the same scratch root (adjacent-row pattern, cf. r101
#     export_prod det_b); fails closed with reason=seq_reference_missing when
#     they are absent, so registration order seq -> order is part of the law.
#   arm=repeat (row export_div_s03_repeat_idempotence)
#     the SAME preset exported twice in one session (r1_pck.pck, r2_pck.pck);
#     the sequential artifacts must be byte-identical (sha256) and each carry
#     its own beacon.
#
# PASS lines carry derived booleans, counts, sizes and sha256 digests; the
# sha256 fields are trailing and deliberately UNPINNED: measured 2026-10-18,
# the exported scene cache `.godot/exported/…-main.scn` embeds a random u32
# `node_ids` value (4 bytes, measured at scn offset 491..494) generated on the
# first export in a fresh project dir, so the pack digest varies across fresh
# generations and only stabilizes while that cache file persists (repeat/order
# byte-equality is asserted inside the fixture, not by pinning digests). Host
# paths appear only in EXPORT_DIV_DIAG lines and in the unpinned trailing
# `proj=` field (same evidence rule as the r102 export_launch / r103
# export_div_s02 family: nested engine output is never echoed).
#
# Scratch: <root>/div_s03/{proj,out,logs}; <root> = first writable of
# $EXPORT_DIV_ROOT, $EXPORT_LAUNCH_ROOT, <engine user-data dir>/export_div,
# $TMPDIR/export_div, then /tmp/export_div (4096-byte write+readback probe).
# User-data is preferred over $TMPDIR//tmp on purpose: exports run under
# unshare+tmpfs /tmp (r101-E0 EDQUOT mitigation for the packer's fixed
# tmpproject.binary temp) and the artifact root must not live under that tmpfs.
#
# Note (measured): the shared project dir is never wiped — out/ is rebuilt per
# arm but proj/ (and its .godot cache) persists, which is what makes the
# order/repeat byte-equality law hold across fixture invocations.
#
# Battery launch shape (8 s fixture bound; pack-only export ~2.3 s each, whole
# arm ~5.0-5.3 s wall measured at host load 1.8):
#   godot --headless --path <fixture proj> --script res://export_div_s03.gd -- --arm=<arm>
#
# Measured laws (2026-10-18, godot 4.7.2.stable.arch_linux.ed1daf0bf; see
# reports/round-103/r103-E3.md for verbatim receipts):
#   - sequential multi-preset `--export-pack` both orders: each pack carries
#     exactly its own 15-byte beacon entry (name + md5 verified against the
#     pack's own directory) and no foreign name/content (8 entries each,
#     2000 B PckOnly / 2004 B Embed on this project shape).
#   - reverse order A<->B and same-preset repeat reproduce byte-identical packs
#     while the .godot/exported scene cache persists (sha ref matches true).
#   - pack directory entry offsets are relative to a data base (measured base
#     112 = beacon abs 944 - entry off 832 for this standalone pack), hence the
#     fixture anchors beacon content by absolute search + directory md5.

const VARIANT := "div_s03"
const PRESET_PCK := "PckOnly"
const PRESET_EMB := "Embed"
const TAG_PCK := "tag_pck_only.txt"
const TAG_EMB := "tag_embed_only.txt"
const BEACON_PCK := "S03_BEACON_PCK\n"
const BEACON_EMB := "S03_BEACON_EMB\n"
const OUT_A := "a_pck.pck"
const OUT_B := "b_emb.pck"
const OUT_BO := "bo_emb.pck"
const OUT_AO := "ao_pck.pck"
const OUT_R1 := "r1_pck.pck"
const OUT_R2 := "r2_pck.pck"
const TEMPLATE := "linux_release.x86_64"

const CHILD_PROJECT := "config_version=5\n\n[application]\nconfig/name=\"ExportDivS03\"\nrun/main_scene=\"res://main.tscn\"\nconfig/features=PackedStringArray(\"4.7\")\n\n[display]\nwindow/size/viewport_width=320\nwindow/size/viewport_height=180\n"
const CHILD_PRESETS := "[preset.0]\nname=\"PckOnly\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"tagpck\"\nexport_filter=\"all_resources\"\ninclude_filter=\"tag_pck_only.txt\"\nexclude_filter=\"tag_embed_only.txt\"\nexport_path=\"\"\n\n[preset.0.options]\nbinary_format/architecture=\"x86_64\"\nbinary_format/embed_pck=false\n\n[preset.1]\nname=\"Embed\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"tagembed\"\nexport_filter=\"all_resources\"\ninclude_filter=\"tag_embed_only.txt\"\nexclude_filter=\"tag_pck_only.txt\"\nexport_path=\"\"\n\n[preset.1.options]\nbinary_format/architecture=\"x86_64\"\nbinary_format/embed_pck=true\n"
const CHILD_MAIN := "extends Node\n\nfunc _ready() -> void:\n\tprint(\"DIV_S03_MAIN\")\n"
const CHILD_TSCN := "[gd_scene load_steps=2 format=3]\n\n[ext_resource type=\"Script\" path=\"res://main.gd\" id=\"1\"]\n\n[node name=\"Main\" type=\"Node\"]\nscript = ExtResource(\"1\")\n"

var arm := ""
var _root := ""
var _unshare := false


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	if arm == "":
		arm = "seq"
	call_deferred("_run")


func _run() -> void:
	_root = _pick_root()
	_diag("root", _root)
	if _root == "":
		_fail("no_writable_scratch_root")
		return
	if not _template_exists():
		_fail("template_binary_not_found")
		return
	_unshare = _probe_unshare()
	_diag("userns_tmp_isolation", _unshare)
	match arm:
		"seq":
			_arm_seq()
		"order":
			_arm_order()
		"repeat":
			_arm_repeat()
		_:
			_fail("unknown_arm")


# ------------------------------------------------------------------ receipts

func _fail(reason: String) -> void:
	print("FAIL export_div s03 arm=%s reason=%s" % [arm, reason])
	quit(1)


func _verdict(fields: PackedStringArray, bad: String) -> void:
	if bad == "":
		print("PASS export_div s03 arm=%s %s" % [arm, " ".join(fields)])
		quit(0)
	else:
		print("FAIL export_div s03 arm=%s reason=%s %s" % [arm, bad, " ".join(fields)])
		quit(1)


func _diag(key: String, value) -> void:
	print("EXPORT_DIV_DIAG %s %s=%s" % [arm, key, str(value)])


# ------------------------------------------------------------------- scratch

func _pick_root() -> String:
	var candidates: PackedStringArray = []
	if OS.get_environment("EXPORT_DIV_ROOT") != "":
		candidates.append(OS.get_environment("EXPORT_DIV_ROOT"))
	if OS.get_environment("EXPORT_LAUNCH_ROOT") != "":
		candidates.append(OS.get_environment("EXPORT_LAUNCH_ROOT"))
	candidates.append(OS.get_user_data_dir().path_join("export_div"))
	if OS.get_environment("TMPDIR") != "":
		candidates.append(OS.get_environment("TMPDIR").path_join("export_div"))
	candidates.append("/tmp/export_div")
	for c in candidates:
		DirAccess.make_dir_recursive_absolute(c)
		if _probe_writable(c):
			return c
	return ""


func _probe_writable(dir: String) -> bool:
	var payload := PackedByteArray()
	payload.resize(4096)
	payload.fill(65)
	var probe := dir.path_join(".probe")
	var f := FileAccess.open(probe, FileAccess.WRITE)
	if f == null:
		return false
	f.store_buffer(payload)
	f.close()
	var ok := FileAccess.get_file_as_bytes(probe).size() == payload.size()
	DirAccess.remove_absolute(probe)
	return ok


func _probe_unshare() -> bool:
	var cmd := "exec > /dev/null 2>&1\nunshare -m --map-root-user /usr/bin/sh -c 'mount -t tmpfs -o size=64M tmpfs /tmp && test -w /tmp'"
	return OS.execute("/usr/bin/sh", PackedStringArray(["-c", cmd])) == 0


func _godot() -> String:
	var exe := OS.get_executable_path()
	return exe if exe != "" else "/usr/bin/godot"


func _q(s: String) -> String:
	return "'" + s.replace("'", "'\\''") + "'"


func _vdir() -> String:
	return _root.path_join(VARIANT)


func _proj_dir() -> String:
	return _vdir().path_join("proj")


func _out_dir() -> String:
	return _vdir().path_join("out")


func _log_path(name: String) -> String:
	return _vdir().path_join("logs").path_join(name + ".log")


func _mkdir(path: String) -> bool:
	if DirAccess.dir_exists_absolute(path):
		return true
	var err := DirAccess.make_dir_recursive_absolute(path)
	if err != OK:
		_fail("mkdir_failed:%s:%d" % [path, err])
		return false
	return true


func _wipe_dir(dir: String) -> void:
	if not DirAccess.dir_exists_absolute(dir):
		return
	for d in DirAccess.get_directories_at(dir):
		_wipe_dir(dir.path_join(d))
	for f in DirAccess.get_files_at(dir):
		DirAccess.remove_absolute(dir.path_join(f))
	DirAccess.remove_absolute(dir)


func _write_text(path: String, text: String) -> bool:
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		_fail("write_failed:" + path)
		return false
	f.store_string(text)
	f.close()
	return true


func _run_logged(body: String, log_path: String, isolate := false) -> int:
	_mkdir(log_path.get_base_dir())
	var script := body
	if isolate and _unshare:
		# Private /tmp for the packer's fixed tmpproject.binary temp path.
		script = "mount -t tmpfs -o size=64M tmpfs /tmp || exit 97\n" + body
		script = "unshare -m --map-root-user /usr/bin/sh -c " + _q(script)
	_diag("nested", body.replace("\n", " ; "))
	return OS.execute("/usr/bin/sh", PackedStringArray(["-c", "exec > " + _q(log_path) + " 2>&1\n" + script]))


func _template_exists() -> bool:
	var v := Engine.get_version_info()
	var ver := "%d.%d.%d.%s" % [v["major"], v["minor"], v["patch"], v["status"]]
	var candidates: PackedStringArray = []
	if OS.get_environment("XDG_DATA_HOME") != "":
		candidates.append(OS.get_environment("XDG_DATA_HOME").path_join("godot/export_templates").path_join(ver).path_join(TEMPLATE))
	if OS.get_environment("HOME") != "":
		candidates.append(OS.get_environment("HOME").path_join(".local/share/godot/export_templates").path_join(ver).path_join(TEMPLATE))
	candidates.append("/usr/local/share/godot/export_templates/%s/%s" % [ver, TEMPLATE])
	candidates.append("/usr/share/godot/export_templates/%s/%s" % [ver, TEMPLATE])
	for c in candidates:
		if FileAccess.file_exists(c):
			return true
	return false


# ------------------------------------------------------------------ children

func _prepare() -> bool:
	if not _mkdir(_proj_dir()) or not _mkdir(_out_dir()) or not _mkdir(_vdir().path_join("logs")):
		return false
	_write_text(_proj_dir().path_join("project.godot"), CHILD_PROJECT)
	_write_text(_proj_dir().path_join("export_presets.cfg"), CHILD_PRESETS)
	_write_text(_proj_dir().path_join("main.gd"), CHILD_MAIN)
	_write_text(_proj_dir().path_join("main.tscn"), CHILD_TSCN)
	_write_text(_proj_dir().path_join(TAG_PCK), BEACON_PCK)
	_write_text(_proj_dir().path_join(TAG_EMB), BEACON_EMB)
	return true


func _export_pack(preset: String, out_name: String) -> int:
	var proj := _proj_dir()
	var out := _out_dir().path_join(out_name)
	if FileAccess.file_exists(out):
		DirAccess.remove_absolute(out)
	var body := "cd " + _q(proj) + "\n" + _q(_godot()) + " --headless --path " + _q(proj) + " --export-pack " + _q(preset) + " " + _q(out)
	return _run_logged(body, _log_path("export_" + out_name.get_basename()), true)


func _clear_out() -> void:
	_wipe_dir(_out_dir())
	_mkdir(_out_dir())


# ------------------------------------------------------------------ analysis

func _sha256(bytes: PackedByteArray) -> String:
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(bytes)
	return ctx.finish().hex_encode()


func _md5(bytes: PackedByteArray) -> String:
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_MD5)
	ctx.update(bytes)
	return ctx.finish().hex_encode()


func _find_sub(hay: PackedByteArray, needle: PackedByteArray, from := 0) -> int:
	var n := needle.size()
	if n == 0 or hay.size() < n:
		return -1
	var first := needle[0]
	for i in range(from, hay.size() - n + 1):
		if hay[i] != first:
			continue
		var hit := true
		for j in range(1, n):
			if hay[i + j] != needle[j]:
				hit = false
				break
		if hit:
			return i
	return -1


func _contains_sub(hay: PackedByteArray, needle: PackedByteArray) -> bool:
	return _find_sub(hay, needle, 0) >= 0


func _pack_dir(data: PackedByteArray) -> Dictionary:
	if data.size() < 0x28 or data.slice(0, 4).get_string_from_ascii() != "GDPC":
		return {}
	var dir_off := data.decode_u64(0x20)
	if dir_off + 4 > data.size():
		return {}
	var count := data.decode_u32(dir_off)
	var names := PackedStringArray()
	var sizes := {}
	var md5s := {}
	var pos := dir_off + 4
	for _i in count:
		if pos + 4 > data.size():
			return {}
		var name_len := data.decode_u32(pos)
		pos += 4
		if pos + name_len + 36 > data.size():
			return {}
		var raw := data.slice(pos, pos + name_len)
		pos += name_len
		var nul := -1
		for k in raw.size():
			if raw[k] == 0:
				nul = k
				break
		if nul >= 0:
			raw = raw.slice(0, nul)
		var name := raw.get_string_from_utf8()
		var size := data.decode_u64(pos + 8)
		var md5 := data.slice(pos + 16, pos + 32).hex_encode()
		pos += 8 + 8 + 16 + 4
		names.append(name)
		sizes[name] = size
		md5s[name] = md5
	return {"names": names, "sizes": sizes, "md5s": md5s, "format": data.decode_u32(4), "entries": count}


func _analyze(path: String, own_name: String, own_beacon: String, foreign_name: String, foreign_beacon: String) -> Dictionary:
	var r := {"file": false, "bytes": -1, "format": -1, "entries": -1, "parse": false,
		"beacon": false, "beacon_size": -1, "beacon_bytes": false,
		"foreign_name": false, "foreign_beacon": false, "sha": ""}
	var data := FileAccess.get_file_as_bytes(path)
	if data.is_empty():
		return r
	r["file"] = true
	r["bytes"] = data.size()
	r["sha"] = _sha256(data)
	var d := _pack_dir(data)
	r["parse"] = not d.is_empty()
	if r["parse"]:
		var names: PackedStringArray = d["names"]
		r["format"] = d["format"]
		r["entries"] = d["entries"]
		if names.has(own_name):
			r["beacon"] = true
			var want: PackedByteArray = own_beacon.to_utf8_buffer()
			var md5: String = d["md5s"][own_name]
			r["beacon_size"] = d["sizes"][own_name]
			# Pack entry offsets are relative to a data base (measured 112 for
			# this standalone pack), so pin content by absolute search + the
			# directory's own md5 for the entry -- base-format-proof.
			var i := _find_sub(data, want, 0)
			while i >= 0:
				if want.size() == int(d["sizes"][own_name]) and _md5(data.slice(i, i + want.size())) == md5:
					r["beacon_bytes"] = true
					break
				i = _find_sub(data, want, i + 1)
		r["foreign_name"] = names.has(foreign_name)
	r["foreign_beacon"] = _contains_sub(data, foreign_beacon.to_utf8_buffer())
	return r


func _pack_fields(prefix: String, r: Dictionary) -> PackedStringArray:
	var f := PackedStringArray()
	f.append(prefix + "_bytes=%d" % r["bytes"])
	f.append(prefix + "_format=%d" % r["format"])
	f.append(prefix + "_entries=%d" % r["entries"])
	f.append(prefix + "_beacon=%s" % str(r["beacon"]))
	f.append(prefix + "_beacon_size=%d" % r["beacon_size"])
	f.append(prefix + "_beacon_bytes=%s" % str(r["beacon_bytes"]))
	f.append(prefix + "_foreign_name=%s" % str(r["foreign_name"]))
	f.append(prefix + "_foreign_beacon=%s" % str(r["foreign_beacon"]))
	return f


func _pack_bad(prefix: String, r: Dictionary) -> String:
	if not r["file"]:
		return prefix + "_artifact_missing"
	if not r["parse"]:
		return prefix + "_pack_unparsable"
	if not r["beacon"]:
		return prefix + "_beacon_entry_missing"
	if not r["beacon_bytes"]:
		return prefix + "_beacon_content_mismatch:%d" % r["beacon_size"]
	if r["foreign_name"]:
		return prefix + "_foreign_name_present"
	if r["foreign_beacon"]:
		return prefix + "_foreign_content_present"
	return ""


func _sha_of(path: String) -> String:
	var data := FileAccess.get_file_as_bytes(path)
	if data.is_empty():
		return ""
	return _sha256(data)


# ---------------------------------------------------------------------- arms

func _arm_seq() -> void:
	if not _prepare():
		return
	_clear_out()
	var ex_a := _export_pack(PRESET_PCK, OUT_A)
	var ex_b := _export_pack(PRESET_EMB, OUT_B)
	var a := _analyze(_out_dir().path_join(OUT_A), TAG_PCK, BEACON_PCK, TAG_EMB, BEACON_EMB)
	var b := _analyze(_out_dir().path_join(OUT_B), TAG_EMB, BEACON_EMB, TAG_PCK, BEACON_PCK)
	var fields := PackedStringArray()
	fields.append("order=ab")
	fields.append("a_exit=%d" % ex_a)
	fields.append("b_exit=%d" % ex_b)
	fields.append_array(_pack_fields("a", a))
	fields.append_array(_pack_fields("b", b))
	fields.append("both_present=%s" % str(FileAccess.file_exists(_out_dir().path_join(OUT_A)) and FileAccess.file_exists(_out_dir().path_join(OUT_B))))
	# generation-variable digests: trailing + unpinned (see header law).
	fields.append("a_sha=%s" % a["sha"])
	fields.append("b_sha=%s" % b["sha"])
	fields.append("proj=" + _proj_dir())
	var bad := ""
	if ex_a != 0:
		bad = "a_exit:%d" % ex_a
	elif ex_b != 0:
		bad = "b_exit:%d" % ex_b
	else:
		bad = _pack_bad("a", a)
		if bad == "":
			bad = _pack_bad("b", b)
	_verdict(fields, bad)


func _arm_order() -> void:
	if not _prepare():
		return
	var ref_a_path := _out_dir().path_join(OUT_A)
	var ref_b_path := _out_dir().path_join(OUT_B)
	var have_ref := FileAccess.file_exists(ref_a_path) and FileAccess.file_exists(ref_b_path)
	var ex_b := _export_pack(PRESET_EMB, OUT_BO)
	var ex_a := _export_pack(PRESET_PCK, OUT_AO)
	var a := _analyze(_out_dir().path_join(OUT_AO), TAG_PCK, BEACON_PCK, TAG_EMB, BEACON_EMB)
	var b := _analyze(_out_dir().path_join(OUT_BO), TAG_EMB, BEACON_EMB, TAG_PCK, BEACON_PCK)
	var a_match: bool = have_ref and a["sha"] == _sha_of(ref_a_path)
	var b_match: bool = have_ref and b["sha"] == _sha_of(ref_b_path)
	var fields := PackedStringArray()
	fields.append("order=ba")
	fields.append("b_exit=%d" % ex_b)
	fields.append("a_exit=%d" % ex_a)
	fields.append_array(_pack_fields("b", b))
	fields.append_array(_pack_fields("a", a))
	fields.append("ref=seq")
	fields.append("ref_a_match=%s" % str(a_match))
	fields.append("ref_b_match=%s" % str(b_match))
	# generation-variable digests: trailing + unpinned (see header law).
	fields.append("b_sha=%s" % b["sha"])
	fields.append("a_sha=%s" % a["sha"])
	fields.append("proj=" + _proj_dir())
	var bad := ""
	if ex_b != 0:
		bad = "b_exit:%d" % ex_b
	elif ex_a != 0:
		bad = "a_exit:%d" % ex_a
	else:
		bad = _pack_bad("b", b)
		if bad == "":
			bad = _pack_bad("a", a)
		if bad == "" and not have_ref:
			bad = "seq_reference_missing"
		elif bad == "" and not b_match:
			bad = "b_order_mismatch"
		elif bad == "" and not a_match:
			bad = "a_order_mismatch"
	_verdict(fields, bad)


func _arm_repeat() -> void:
	if not _prepare():
		return
	var ex_1 := _export_pack(PRESET_PCK, OUT_R1)
	var ex_2 := _export_pack(PRESET_PCK, OUT_R2)
	var r1 := _analyze(_out_dir().path_join(OUT_R1), TAG_PCK, BEACON_PCK, TAG_EMB, BEACON_EMB)
	var r2 := _analyze(_out_dir().path_join(OUT_R2), TAG_PCK, BEACON_PCK, TAG_EMB, BEACON_EMB)
	var sha_match: bool = r1["sha"] != "" and r1["sha"] == r2["sha"]
	var fields := PackedStringArray()
	fields.append("preset=" + PRESET_PCK)
	fields.append("r1_exit=%d" % ex_1)
	fields.append("r2_exit=%d" % ex_2)
	fields.append_array(_pack_fields("r1", r1))
	fields.append_array(_pack_fields("r2", r2))
	fields.append("sha_match=%s" % str(sha_match))
	# generation-variable digests: trailing + unpinned (see header law).
	fields.append("r1_sha=%s" % r1["sha"])
	fields.append("r2_sha=%s" % r2["sha"])
	fields.append("proj=" + _proj_dir())
	var bad := ""
	if ex_1 != 0:
		bad = "r1_exit:%d" % ex_1
	elif ex_2 != 0:
		bad = "r2_exit:%d" % ex_2
	else:
		bad = _pack_bad("r1", r1)
		if bad == "":
			bad = _pack_bad("r2", r2)
		if bad == "" and not sha_match:
			bad = "repeat_sha_mismatch"
	_verdict(fields, bad)
