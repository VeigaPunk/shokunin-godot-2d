extends SceneTree
#
# export_prod_s09 — scenario 09 of the export_prod lattice.
#
# A production-shaped project whose scenes and scripts are nested two and three
# levels deep is built from byte-pinned sources under <temp>/r101_export_prod_s09,
# exported headless to a PCK, the pack's directory table is censused byte-exactly,
# and the pack is launched through --main-pack for a frame-bounded run receipt.
#
# Arms (--arm=NAME):
#   census            (default) — build + export + census, no launch.
#   run                         — build + export + census + --main-pack receipt.
#   both                        — alias of run, the scenario's single-row name.
#   sensitivity                 — same project plus one UNREFERENCED script three
#                                 levels deep: the census must grow by exactly
#                                 that .gdc + .remap pair while the run receipt
#                                 (not taken on this arm) is unaffected.
#   negative_empty_pbin         — expected negative: the shipped pack with its
#                                 `project.binary` payload zeroed must be
#                                 refused at launch with no receipt.
#
# The census is a pure function of the exported pack bytes; it is what catches a
# nested file that failed to reach the pack. The run receipt is what catches a
# STRUCTURALLY VALID pack that cannot boot — in particular the measured
# 0-byte `project.binary` glitch (entry list identical, pack 176 B smaller, exit
# code still 0 on export, runtime then refuses with "Corrupted header in binary
# project.binary (not ECFG)"). Export is retried while that entry is empty so the
# receipt stays deterministic; the retry count is printed as a tail diagnostic.
#
# Precondition measured on this host: `res://.godot/exported/` must exist before
# the export, else every scene fails with "Unable to save export scene file" and
# the pack is written 0 bytes long while the export still exits 0.

const ROOT_NAME := "r101_export_prod_s09"
const PRESET := "Linux/X11"
const PACK_NAME := "s09.pck"
const MARK := "S09_RUN"
const MAX_EXPORTS := 3

const PROJ_GODOT := """config_version=5

[application]

config/name="R101S09Nested"
run/main_scene="res://scenes/main.tscn"
config/features=PackedStringArray("4.7")
"""

const PRESETS_CFG := """[preset.0]

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

const MAIN_TSCN := """[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://scripts/main.gd" id="1_main"]

[node name="Main" type="Node2D"]
script = ExtResource("1_main")
"""

const DEEP_TSCN := """[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://scripts/core/deep/util.gd" id="1_util"]

[node name="LevelDeep" type="Node2D"]
script = ExtResource("1_util")
"""

const MAIN_GD := """extends Node2D

const DEEP_SCENE := preload("res://scenes/levels/deep/level_deep.tscn")
const GREET := preload("res://scripts/core/greet.gd")


func _ready() -> void:
	var deep := DEEP_SCENE.instantiate()
	add_child(deep)
	var current := get_tree().current_scene
	print("S09_RUN main=_ready main_scene=", current.name if current else "<none>",
		" deep_root=", deep.name, " deep_tag=", deep.tag(),
		" greet=", GREET.line(), " engine=", Engine.get_version_info().string)
"""

const GREET_GD := """extends RefCounted

const GREETING := "r101s09_greet"


static func line() -> String:
	return GREETING
"""

const UTIL_GD := """extends Node

const TAG := "r101s09_deep_util"


func tag() -> String:
	return TAG
"""

# Measured census of the exported pack: source-derived entries only (entries
# under `.godot/` are engine-generated and counted separately as dot_n).
const ARMS := ["census", "run", "both", "sensitivity", "negative_empty_pbin"]
const EXTRA_GD := """extends Node

const EXTRA := "r101s09_extra"
"""
const EXPECT_ENTRIES := 13
const EXPECT_DOT_N := 4
const EXPECT_DEEP3 := 3
const EXPECT_DEEP2 := 2
const EXPECT_GDC_SIZES := [190, 210, 665]
const EXPECT_REMAP_SIZES := [39, 45, 49, 97, 103]
const SENS_ENTRIES := 15
const SENS_DEEP3 := 5
const SENS_GDC_SIZES := [123, 190, 210, 665]
const SENS_REMAP_SIZES := [39, 45, 49, 50, 97, 103]
const EXPECT_PATHS := [
	".godot/exported/133200997/export-3a0f57f805b8ac00de64601972f6b315-level_deep.scn",
	".godot/exported/133200997/export-3ad5c15c4f3250da0cc7c1af1770d85f-main.scn",
	".godot/global_script_class_cache.cfg",
	".godot/uid_cache.bin",
	"project.binary",
	"scenes/levels/deep/level_deep.tscn.remap",
	"scenes/main.tscn.remap",
	"scripts/core/deep/util.gd.remap",
	"scripts/core/deep/util.gdc",
	"scripts/core/greet.gd.remap",
	"scripts/core/greet.gdc",
	"scripts/main.gd.remap",
	"scripts/main.gdc",
]

var _root := ""
var _proj := ""
var _out := ""
var _pack := ""
var _exe := ""
var _export_ms := 0
var _run_ms := 0
var _exports := 0
var _arm := "census"


func _initialize() -> void:
	var user_args := OS.get_cmdline_user_args()
	for arg in user_args:
		if arg.begins_with("--arm="):
			_arm = arg.trim_prefix("--arm=")
	if _arm not in ARMS:
		_fail("unknown arm '" + _arm + "' (expected " + ", ".join(ARMS) + ")")
		return
	_exe = OS.get_executable_path()
	_root = OS.get_temp_dir().path_join(ROOT_NAME)
	_proj = _root.path_join("nested")
	_out = _root.path_join("out")
	_pack = _out.path_join(PACK_NAME)
	_rm_rf(_root)
	if not _write_project():
		return
	var census := _export_until_usable()
	if census.is_empty():
		return
	if _arm == "negative_empty_pbin":
		_negative_empty_pbin(census)
		return
	if _arm == "census" or _arm == "sensitivity":
		print(_line(census, ""))
		quit(0)
		return
	var receipt := _launch(_pack)
	if receipt.is_empty():
		return
	print(_line(census, receipt))
	quit(0)


func _write_project() -> bool:
	var files := {
		"project.godot": PROJ_GODOT,
		"export_presets.cfg": PRESETS_CFG,
		"scenes/main.tscn": MAIN_TSCN,
		"scenes/levels/deep/level_deep.tscn": DEEP_TSCN,
		"scripts/main.gd": MAIN_GD,
		"scripts/core/greet.gd": GREET_GD,
		"scripts/core/deep/util.gd": UTIL_GD,
	}
	# sensitivity arm: one extra script three levels deep that NOTHING references.
	# Measured: export_filter="all_resources" still packs it as .gdc + .remap
	# (extra.gdc=123, extra.gd.remap=50), so the census grows by exactly that pair.
	if _arm == "sensitivity":
		files["scripts/core/deep/extra.gd"] = EXTRA_GD
	for rel in files:
		var path := _proj.path_join(rel)
		DirAccess.make_dir_recursive_absolute(path.get_base_dir())
		var f := FileAccess.open(path, FileAccess.WRITE)
		if f == null:
			_fail("cannot write " + path)
			return false
		f.store_string(files[rel])
		f.close()
	# Measured precondition: the export writes its customized scene files here and
	# silent-fails (0-byte pack, exit 0) when the directory is absent.
	DirAccess.make_dir_recursive_absolute(_proj.path_join(".godot/exported"))
	DirAccess.make_dir_recursive_absolute(_out)
	return true


func _strip_ansi(s: String) -> String:
	var re := RegEx.new()
	re.compile("\u001b\\[[0-9;]*m")
	return re.sub(s, "", true)


func _diag(raw: String) -> String:
	var clean := _strip_ansi(raw)
	return clean.substr(maxi(0, clean.length() - 240)).replace("ERROR:", "ERR:").replace("\n", "\\n")


func _export_until_usable() -> Dictionary:
	var census := {}
	for attempt in MAX_EXPORTS:
		var out: Array = []
		var started := Time.get_ticks_msec()
		var code := OS.execute(_exe, PackedStringArray([
			"--headless", "--path", _proj, "--export-pack", PRESET, _pack]), out, true)
		_export_ms = Time.get_ticks_msec() - started
		_exports += 1
		var raw: String = out[0] if out.size() > 0 else ""
		var text := _strip_ansi(raw)
		if code != 0 or not text.contains("[ DONE ] savepack"):
			_fail("export attempt %d rc=%d chars=%d savepack=%s tail=[%s]" % [
				attempt + 1, code, text.length(), text.contains("[ DONE ] savepack"), _diag(raw)])
			return {}
		census = _census(_pack)
		if census.is_empty():
			return {}
		if int(census["pbin_size"]) > 0:
			break
	if not _assert_census(census):
		return {}
	return census


func _census(pack_path: String) -> Dictionary:
	var bytes := FileAccess.get_file_as_bytes(pack_path)
	if bytes.size() < 112:
		_fail("pack too small: " + str(bytes.size()) + " bytes")
		return {}
	if bytes.slice(0, 4).get_string_from_utf8() != "GDPC":
		_fail("pack magic mismatch")
		return {}
	var pack_version := bytes.decode_u32(4)
	if pack_version != 4:
		_fail("unexpected pack format version " + str(pack_version))
		return {}
	var file_base := bytes.decode_u64(24)
	var dir_offset := bytes.decode_u64(32)
	if dir_offset >= bytes.size():
		_fail("directory offset outside pack: " + str(dir_offset))
		return {}
	var count := bytes.decode_u32(dir_offset)
	var off := int(dir_offset) + 4
	var paths := []
	var sizes := {}
	var table := {}
	var pbin_size := -1
	var max_end := 0
	for i in count:
		if off + 4 > bytes.size():
			_fail("directory truncated at entry " + str(i))
			return {}
		var plen := bytes.decode_u32(off)
		off += 4
		if off + plen > bytes.size():
			_fail("directory path truncated at entry " + str(i))
			return {}
		# The table stores NUL-padded paths (measured: "project.binary\x00\x00");
		# stored length is the padded length. Trailing NULs are trimmed on the
		# bytes, not after decoding — get_string_from_utf8() would replace them
		# with U+FFFD and log a Unicode parsing error per padded entry.
		var raw_path := bytes.slice(off, off + plen)
		var path_end := raw_path.size()
		while path_end > 0 and raw_path[path_end - 1] == 0:
			path_end -= 1
		var path := raw_path.slice(0, path_end).get_string_from_utf8()
		off += (int(plen) + 3) & ~3
		var data_off := bytes.decode_u64(off)
		var data_size := bytes.decode_u64(off + 8)
		off += 16 + 16 + 4
		paths.append(path)
		sizes[path] = int(data_size)
		table[path] = {"off": int(data_off), "size": int(data_size)}
		if path == "project.binary":
			pbin_size = int(data_size)
		max_end = maxi(max_end, int(file_base) + int(data_off) + int(data_size))
	if off != bytes.size():
		_fail("directory parse ended at " + str(off) + " of " + str(bytes.size()))
		return {}
	if max_end > bytes.size():
		_fail("entry data extends past pack end")
		return {}
	paths.sort()
	var gdc := []
	var remap := []
	var deep3 := 0
	var deep2 := 0
	var dot_n := 0
	for p: String in paths:
		if p.begins_with("."):
			dot_n += 1
			continue
		var segments := p.split("/")
		if p.ends_with(".gdc"):
			gdc.append(sizes[p])
		elif p.ends_with(".remap"):
			remap.append(sizes[p])
		if segments.size() == 4:
			deep3 += 1
		elif segments.size() == 3:
			deep2 += 1
	gdc.sort()
	remap.sort()
	return {
		"entries": count, "paths": paths, "dot_n": dot_n,
		"deep3": deep3, "deep2": deep2, "gdc": gdc, "remap": remap,
		"pbin_size": pbin_size, "bytes": bytes.size(), "file_base": int(file_base),
		"table": table, "sha256": FileAccess.get_sha256(pack_path),
	}


func _assert_census(census: Dictionary) -> bool:
	var sens := _arm == "sensitivity"
	var want_entries: int = SENS_ENTRIES if sens else EXPECT_ENTRIES
	var want_deep3: int = SENS_DEEP3 if sens else EXPECT_DEEP3
	var want_gdc: Array = SENS_GDC_SIZES if sens else EXPECT_GDC_SIZES
	var want_remap: Array = SENS_REMAP_SIZES if sens else EXPECT_REMAP_SIZES
	var want_paths: Array = EXPECT_PATHS.duplicate()
	if sens:
		want_paths.append("scripts/core/deep/extra.gd.remap")
		want_paths.append("scripts/core/deep/extra.gdc")
		want_paths.sort()
	var problems := []
	if int(census["entries"]) != want_entries:
		problems.append("entries=%d" % census["entries"])
	if int(census["dot_n"]) != EXPECT_DOT_N:
		problems.append("dot_n=%d" % census["dot_n"])
	if int(census["deep3"]) != want_deep3:
		problems.append("deep3=%d" % census["deep3"])
	if int(census["deep2"]) != EXPECT_DEEP2:
		problems.append("deep2=%d" % census["deep2"])
	if census["gdc"] != want_gdc:
		problems.append("gdc=" + str(census["gdc"]))
	if census["remap"] != want_remap:
		problems.append("remap=" + str(census["remap"]))
	if census["paths"] != want_paths:
		problems.append("paths=" + str(census["paths"]))
	if int(census["pbin_size"]) <= 0:
		problems.append("pbin_size=%d" % census["pbin_size"])
	if not problems.is_empty():
		_fail("census mismatch: " + ", ".join(problems))
		return false
	return true


func _launch(pack_path: String) -> String:
	var run := _launch_pack(pack_path)
	var text: String = run["text"]
	for line in text.split("\n"):
		if line.begins_with(MARK):
			if int(run["code"]) != 0:
				_fail("run receipt printed but exit=%d" % int(run["code"]))
				return ""
			return line.strip_edges()
	_fail("no " + MARK + " receipt from --main-pack run (rc=%d) tail=[%s]" % [
		int(run["code"]), _diag(run["raw"])])
	return ""


func _launch_pack(pack_path: String) -> Dictionary:
	var out: Array = []
	var started := Time.get_ticks_msec()
	var code := OS.execute(_exe, PackedStringArray([
		"--headless", "--main-pack", pack_path, "--quit-after", "3"]), out, true)
	_run_ms = Time.get_ticks_msec() - started
	var raw: String = out[0] if out.size() > 0 else ""
	return {"code": code, "raw": raw, "text": _strip_ansi(raw)}


func _negative_empty_pbin(census: Dictionary) -> void:
	var corrupt := _corrupt_pbin(census)
	if corrupt == "":
		return
	var run := _launch_pack(corrupt)
	var text: String = run["text"]
	var not_ecfg := text.contains("Corrupted header in binary project.binary (not ECFG)")
	var load_fail := text.contains("Couldn't load file 'res://project.binary', error code 16")
	var receipt := false
	for line in text.split("\n"):
		if line.begins_with(MARK):
			receipt = true
	# Measured refusal shape for THIS corruption (payload zeroed, entry size kept):
	# the loader reports the ECFG header mismatch and cannot load project.binary;
	# no MARK line is ever printed. The exit code is LAUNCH-SHAPE dependent and is
	# therefore diagnostic only: 1 under OS.execute (which also reports "no main
	# scene defined", 3/3 reps) but 0 from a shell redirect (3/3 reps) on the same
	# pack bytes. The pinned fact is the refusal + absent receipt.
	if not not_ecfg or not load_fail or receipt:
		_fail("expected negative did not reproduce: rc=%d not_ecfg=%s load_fail=%s receipt=%s tail=[%s]" % [
			int(run["code"]), not_ecfg, load_fail, receipt, _diag(run["raw"])])
		return
	print("ERROR: EXPORT_PROD_S09 EXPECTED NEGATIVE: zeroed project.binary refused at launch signature=PROJECT_BINARY_NOT_ECFG receipt=absent | rc=%d" % int(run["code"]))
	quit(2)


func _corrupt_pbin(census: Dictionary) -> String:
	var table: Dictionary = census["table"]
	if not table.has("project.binary") or int(table["project.binary"]["size"]) <= 0:
		_fail("no project.binary entry to corrupt")
		return ""
	var data := FileAccess.get_file_as_bytes(_pack)
	var start := int(census["file_base"]) + int(table["project.binary"]["off"])
	var size := int(table["project.binary"]["size"])
	if start + size > data.size():
		_fail("project.binary entry outside pack")
		return ""
	for i in size:
		data[start + i] = 0
	var corrupt := _out.path_join("s09_corrupt.pck")
	var f := FileAccess.open(corrupt, FileAccess.WRITE)
	if f == null:
		_fail("cannot write " + corrupt)
		return ""
	f.store_buffer(data)
	f.close()
	return corrupt


func _line(census: Dictionary, receipt: String) -> String:
	var head := "PASS export_prod_s09 %s entries=%d deep3=%d deep2=%d gdc=%s remap=%s pbin_ok=%d" % [
		_arm, census["entries"], census["deep3"], census["deep2"],
		str(census["gdc"]).replace(" ", ""), str(census["remap"]).replace(" ", ""),
		1 if int(census["pbin_size"]) > 0 else 0]
	if receipt != "":
		head += " receipt=" + receipt
	return head + " | paths=%s pck_bytes=%d pck_sha256=%s exports=%d export_ms=%d run_ms=%d" % [
		str(census["paths"]).replace(" ", ""), census["bytes"], census["sha256"],
		_exports, _export_ms, _run_ms]


func _fail(why: String) -> void:
	print("ERROR: EXPORT_PROD_S09 ASSERTION FAILED: " + why)
	quit(2)


func _rm_rf(path: String) -> void:
	var dir := DirAccess.open(path)
	if dir == null:
		return
	for sub in dir.get_directories():
		_rm_rf(path.path_join(sub))
	dir = DirAccess.open(path)
	if dir == null:
		return
	for file in dir.get_files():
		DirAccess.remove_absolute(path.path_join(file))
	dir = null
	DirAccess.remove_absolute(path)
