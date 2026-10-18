extends SceneTree
# export_prod_s03 — Linux/X11 PCK export determinism, with an explicit variance bound.
#
# Self-contained: builds a production-shaped scratch project, imports it with the
# installed 4.7.2.stable templates, exports it three times, then parses the PCK v2
# containers itself. Launch shape: `godot --headless --script res://export_prod_s03.gd`.
#
# Measured laws (reports/round-101/r101-E3.md):
#   L1 repeat exports from one import state are byte-identical over the WHOLE file
#      (different output paths and in-place overwrite alike);
#   L2 a fresh re-import of byte-identical sources changes only the converted
#      scene entry: a 4-byte identity field at blob offsets 502..505 plus that
#      entry's md5 in the table. Every other byte is invariant. That is the whole
#      legitimate variance region — the PCK carries no timestamp;
#   L3 a 0-byte project.binary (rc=0, no warning, observed 2/29 runs) is a
#      degenerate pack that the entry census below rejects.
#
# The PASS line pins the comparable region rather than the raw pack sha:
#   stable_census_sha = sha256 over sorted "<path> <size> <md5>\n" lines with the
#                       scene entry excluded (invariant across fresh imports);
#   masked_sha        = sha256 of the pack with the scene data slice and the scene
#                       entry's md5 field zeroed (same invariance, whole file).
#
# Integration note: nested import+export takes ~15-30 s; the battery's default
# 8 s script timeout must be raised for this row (see r101-E3 shard).

const PRESET := "Linux/X11"
const HEADER_SIZE := 112
const ENTRY_COUNT := 11
const PACK_SIZE := 3088
const PBIN_SIZE := 263
const PBIN_MD5 := "61bebee20a3390d3847fc9185313d3be"
const STABLE_CENSUS_SHA := "1a9db77e4af3570a93abac3f4b74508d1ed6cd0537c60030ad48d7a23c54ee55"
const MASKED_SHA := "2f47c672dac538009afbbdd29a7244c9f73bd487975227290eb9ce7ce54a7523"
const SCENE_SUFFIX := "-main.scn"
const PIN_SIZES := {
	".godot/exported/133200997/export-3070c538c03ee49b7677ff960a3f5195-main.scn": 678,
	".godot/exported/133200997/export-6fc1cdc24f874ae6a8480cc5b1afcd3c-settings.res": 263,
	".godot/global_script_class_cache.cfg": 8,
	".godot/imported/icon.png-b6a7fb2db36edd3d95dc42f1dc8c1c5d.ctex": 110,
	".godot/uid_cache.bin": 71,
	"assets/icon.png.import": 193,
	"assets/settings.tres.remap": 101,
	"main.tscn.remap": 97,
	"project.binary": 263,
	"scripts/actor.gd.remap": 40,
	"scripts/actor.gdc": 207,
}

const PROJECT_GODOT := "config_version=5\n\n[application]\n\nconfig/name=\"ExportProdS03\"\nrun/main_scene=\"res://main.tscn\"\nconfig/features=PackedStringArray(\"4.7\", \"GL Compatibility\")\n\n[rendering]\n\nrenderer/rendering_method=\"gl_compatibility\"\n"
const MAIN_TSCN := "[gd_scene load_steps=2 format=3]\n\n[ext_resource type=\"Script\" path=\"res://scripts/actor.gd\" id=\"1_actor\"]\n\n[node name=\"Main\" type=\"Node2D\"]\nscript = ExtResource(\"1_actor\")\n"
const ACTOR_GD := "extends Node2D\n\nconst SPEED := 42.0\n\nfunc _ready() -> void:\n\tprint(\"actor ready\")\n"
const SETTINGS_TRES := "[gd_resource type=\"Resource\" format=3]\n\n[resource]\nresource_name = \"ProdSettings\"\n"
const EXPORT_PRESETS := "[preset.0]\n\nname=\"Linux/X11\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\ninclude_filter=\"\"\nexclude_filter=\"\"\nexport_path=\"build/out.pck\"\n\n[preset.0.options]\nbinary_format/architecture=\"x86_64\"\n"
const ICON_PNG_B64 := "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAYAAADED76LAAAAbUlEQVR4nBXKMRHDMAwAQN8VSKfQEIByMIYQ0FAQ2YwkYqIlVNr38NuPMb6/N8EkWRTNGIdAMEkWRR87fASCSbIo+rPDKRBMkkXR5w6XQDBJFkVfO9wCwSRZFH3v8AgEk2RR9LPDSyCYJIui+QNuMJNBX6i2MAAAAABJRU5ErkJggg=="


var _root := ""


func _initialize() -> void:
	var r := _run()
	if not _root.is_empty():
		_rm_rf(_root)
	print(r.text)
	quit(0 if r.ok else 2)


func _run() -> Dictionary:
	var exe := OS.get_executable_path()
	var root := _scratch_root()
	if root.is_empty():
		return _fail("no_scratch_root", "tmp_and_vartmp_unwritable")
	_root = root
	var proj_a := root + "/p1"
	var proj_b := root + "/p2"
	var pack_a := root + "/p1_a.pck"
	var pack_b := root + "/p1_b.pck"
	var pack_c := root + "/p2_a.pck"

	if not _write_project(proj_a):
		return _fail("write_project", proj_a)
	if _godot(exe, ["--headless", "--path", proj_a, "--import"]) != 0:
		return _fail("import_rc_a", "nonzero")
	if _godot(exe, ["--headless", "--path", proj_a, "--export-release", PRESET, pack_a]) != 0:
		return _fail("export_rc_a", "nonzero")
	var sha_a := FileAccess.get_sha256(pack_a)
	var size_a := _file_size(pack_a)
	if _godot(exe, ["--headless", "--path", proj_a, "--export-release", PRESET, pack_b]) != 0:
		return _fail("export_rc_b", "nonzero")
	if _godot(exe, ["--headless", "--path", proj_a, "--export-release", PRESET, pack_a]) != 0:
		return _fail("export_rc_overwrite", "nonzero")

	var A := _parse(pack_a)
	if not A.ok:
		return _fail("parse_a", A.reason)
	var B := _parse(pack_b)
	if not B.ok:
		return _fail("parse_b", B.reason)

	if size_a != B.size or FileAccess.get_sha256(pack_b) != sha_a:
		return _fail("repeat_differs", "%d/%d" % [size_a, B.size])
	if FileAccess.get_sha256(pack_a) != sha_a:
		return _fail("overwrite_differs", FileAccess.get_sha256(pack_a).left(16))
	if A.size != PACK_SIZE:
		return _fail("pack_size", "%d!=%d" % [A.size, PACK_SIZE])
	if A.magic != 0x43504447 or A.fmt != 4 or A.engine != "4.7.2" or A.pack_version != 2 or A.header_size != HEADER_SIZE:
		return _fail("bad_header", "%x/%d/%s/%d/%d" % [A.magic, A.fmt, A.engine, A.pack_version, A.header_size])
	if A.entries.size() != ENTRY_COUNT:
		return _fail("entry_count", str(A.entries.size()))

	var census_ok := 0
	for path in PIN_SIZES:
		if A.entries.has(path) and A.entries[path].size == PIN_SIZES[path]:
			census_ok += 1
	if census_ok != ENTRY_COUNT:
		return _fail("census_mismatch", "%d/%d" % [census_ok, ENTRY_COUNT])
	if not A.entries.has("project.binary") or A.entries["project.binary"].size != PBIN_SIZE or A.entries["project.binary"].md5 != PBIN_MD5:
		return _fail("degenerate_project_binary", "%d:%s" % [
			A.entries["project.binary"].size, A.entries["project.binary"].md5.left(12)])
	var content_ok := 0
	for path in A.entries:
		if A.entries[path].content_md5 == A.entries[path].md5:
			content_ok += 1
	if content_ok != ENTRY_COUNT:
		return _fail("content_md5", "%d/%d" % [content_ok, ENTRY_COUNT])
	if A.stable_census_sha != STABLE_CENSUS_SHA:
		return _fail("stable_census_sha", A.stable_census_sha.left(16))
	if A.masked_sha != MASKED_SHA:
		return _fail("masked_sha", A.masked_sha.left(16))

	# Variance bound: a fresh import of the same sources may differ only inside the
	# converted-scene entry (its data bytes and its table md5).
	if not _write_project(proj_b):
		return _fail("write_project_b", proj_b)
	if _godot(exe, ["--headless", "--path", proj_b, "--import"]) != 0:
		return _fail("import_rc_b", "nonzero")
	if _godot(exe, ["--headless", "--path", proj_b, "--export-release", PRESET, pack_c]) != 0:
		return _fail("export_rc_c", "nonzero")
	var C := _parse(pack_c)
	if not C.ok:
		return _fail("parse_c", C.reason)
	if C.entries.size() != ENTRY_COUNT:
		return _fail("reimport_entry_count", str(C.entries.size()))
	var scene := ""
	var diff_entries := 0
	var diff_bytes := 0
	for path in A.entries:
		if not C.entries.has(path):
			return _fail("reimport_missing_entry", path)
		if C.entries[path].size != A.entries[path].size:
			return _fail("reimport_entry_size", path)
		if path.ends_with(SCENE_SUFFIX):
			scene = path
			if C.entries[path].md5 != A.entries[path].md5:
				diff_entries += 1
			var da: PackedByteArray = A.entries[path].data
			var db: PackedByteArray = C.entries[path].data
			for i in mini(da.size(), db.size()):
				if da[i] != db[i]:
					diff_bytes += 1
		elif C.entries[path].md5 != A.entries[path].md5:
			return _fail("variance_escaped", path)
	if scene.is_empty():
		return _fail("scene_entry_missing", SCENE_SUFFIX)
	if C.stable_census_sha != STABLE_CENSUS_SHA:
		return _fail("reimport_census_sha", C.stable_census_sha.left(16))
	if C.masked_sha != MASKED_SHA:
		return _fail("reimport_masked_sha", C.masked_sha.left(16))

	return {"ok": true, "text": (
		"PASS export_prod_s03 pck_size=%d entries=%d fmt=%d engine=%s pack_version=%d header=%d "
		+ "repeat_identical=true overwrite_identical=true entry_census=%d/%d "
		+ "stable_census_sha=%s masked_sha=%s project_binary=%d:%s content_md5=%d/%d "
		+ "reimport_diff_entries=%d reimport_diff_bytes=%d reimport_sizes_equal=true")
		% [A.size, A.entries.size(), A.fmt, A.engine, A.pack_version, A.header_size,
			census_ok, ENTRY_COUNT, A.stable_census_sha, A.masked_sha,
			A.entries["project.binary"].size, A.entries["project.binary"].md5,
			content_ok, ENTRY_COUNT, diff_entries, diff_bytes]}


func _fail(code: String, detail: String) -> Dictionary:
	return {"ok": false, "text": "FAIL export_prod_s03 reason=%s detail=%s" % [code, detail]}


func _scratch_root() -> String:
	for base in ["/tmp", "/var/tmp"]:
		var probe := "%s/.r101s03_probe_%d" % [base, OS.get_process_id()]
		var f := FileAccess.open(probe, FileAccess.WRITE)
		if f == null:
			continue
		f.store_string("ok")
		f.close()
		DirAccess.remove_absolute(probe)
		var d := "%s/r101-s03-%d" % [base, OS.get_process_id()]
		_rm_rf(d)
		if DirAccess.make_dir_recursive_absolute(d) == OK:
			return d
	return ""


func _rm_rf(path: String) -> void:
	OS.execute("rm", PackedStringArray(["-rf", path]), [], false, false)


func _file_size(path: String) -> int:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return -1
	var n := f.get_length()
	f.close()
	return n


func _godot(exe: String, args: Array) -> int:
	var out: Array = []
	return OS.execute(exe, PackedStringArray(args), out, true)


func _write(path: String, text: String) -> bool:
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		return false
	f.store_string(text)
	f.close()
	return true


func _write_bytes(path: String, bytes: PackedByteArray) -> bool:
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		return false
	f.store_buffer(bytes)
	f.close()
	return true


func _write_project(dir: String) -> bool:
	if DirAccess.make_dir_recursive_absolute(dir + "/scripts") != OK:
		return false
	if DirAccess.make_dir_recursive_absolute(dir + "/assets") != OK:
		return false
	return (_write(dir + "/project.godot", PROJECT_GODOT)
		and _write(dir + "/main.tscn", MAIN_TSCN)
		and _write(dir + "/scripts/actor.gd", ACTOR_GD)
		and _write(dir + "/assets/settings.tres", SETTINGS_TRES)
		and _write(dir + "/export_presets.cfg", EXPORT_PRESETS)
		and _write_bytes(dir + "/assets/icon.png", Marshalls.base64_to_raw(ICON_PNG_B64)))


func _parse(path: String) -> Dictionary:
	var out := {"ok": false, "reason": "", "size": 0, "magic": 0, "fmt": 0, "engine": "",
		"pack_version": 0, "header_size": 0, "entries": {}, "stable_census_sha": "", "masked_sha": ""}
	if not FileAccess.file_exists(path):
		out.reason = "missing"
		return out
	var b := FileAccess.get_file_as_bytes(path)
	if b.size() < HEADER_SIZE:
		out.reason = "short"
		return out
	out.size = b.size()
	out.magic = b.decode_u32(0)
	out.fmt = b.decode_u32(4)
	out.engine = "%d.%d.%d" % [b.decode_u32(8), b.decode_u32(12), b.decode_u32(16)]
	out.pack_version = b.decode_u32(20)
	out.header_size = b.decode_u32(24)
	var file_base := b.decode_u64(32)
	if out.magic != 0x43504447 or out.header_size != HEADER_SIZE or file_base >= b.size() or file_base < HEADER_SIZE:
		out.reason = "header"
		return out
	var count := b.decode_u32(file_base)
	if count == 0 or count > 64:
		out.reason = "count"
		return out
	var off := file_base + 4
	var entries := {}
	var census := ""
	var masked := b.duplicate()
	for i in count:
		if off + 4 > b.size():
			out.reason = "entry_truncated"
			return out
		var plen := b.decode_u32(off)
		off += 4
		if plen == 0 or plen > 300 or off + plen > b.size():
			out.reason = "path_len"
			return out
		var raw := b.slice(off, off + plen)
		var end := raw.size()
		while end > 0 and raw[end - 1] == 0:
			end -= 1
		var epath := raw.slice(0, end).get_string_from_utf8()
		off += (plen + 3) / 4 * 4
		if off + 36 > b.size():
			out.reason = "entry_truncated"
			return out
		var data_off := b.decode_u64(off)
		var data_size := b.decode_u64(off + 8)
		var md5_at := off + 16
		var md5 := b.slice(md5_at, md5_at + 16).hex_encode()
		off += 36
		var absolute := HEADER_SIZE + data_off
		if absolute + data_size > file_base:
			out.reason = "data_range:" + epath
			return out
		var data := b.slice(absolute, absolute + data_size)
		entries[epath] = {
			"off": data_off, "size": data_size, "md5": md5,
			"content_md5": _hash(HashingContext.HASH_MD5, data), "data": data,
		}
		if not epath.ends_with(SCENE_SUFFIX):
			census += "%s %d %s\n" % [epath, data_size, md5]
		else:
			for k in data_size:
				masked[absolute + k] = 0
			for k in 16:
				masked[md5_at + k] = 0
	var keys := entries.keys()
	keys.sort()
	var sorted_census := ""
	for k in keys:
		if not k.ends_with(SCENE_SUFFIX):
			sorted_census += "%s %d %s\n" % [k, entries[k].size, entries[k].md5]
	out.entries = entries
	out.stable_census_sha = _hash(HashingContext.HASH_SHA256, sorted_census.to_utf8_buffer())
	out.masked_sha = _hash(HashingContext.HASH_SHA256, masked)
	out.ok = true
	return out


func _hash(kind: int, bytes: PackedByteArray) -> String:
	var ctx := HashingContext.new()
	ctx.start(kind)
	ctx.update(bytes)
	return ctx.finish().hex_encode()
