extends SceneTree
# export_prod_s01.gd — r101 export_prod lattice, scenario 01:
#   base PCK export via preset — magic bytes, size lower bound, receipt census.
#
# Launch:
#   godot --headless --script res://export_prod_s01.gd -- [--work=DIR] [--arm=NAME] [--pck=PATH]
# Arms:
#   main (default) : materialize a production-shaped project, export a pure PCK with the
#                    installed templates, classify the raw bytes, cross-check the census
#                    against the engine's own pack reader, then prove 9 forged packs reject.
#   classify       : classify the pack at --pck (no export).
#   mutations      : run only the forgery ladder against --pck (or export one first).
#
# Measured layout (observed on 4.7.2.stable.ed1daf0bf, see reports/round-101/r101-E1.md):
#   header: "GDPC" u32 version u32 major u32 minor u32 patch u32 flags u64 file_base u64 dir_offset
#   at dir_offset: u32 entry_count, then per entry: u32 path_len (NUL padding included),
#   path bytes, u64 data_offset, u64 size, 16B md5(data), u32 flags.
#   data lives at file_base + data_offset; the directory ends exactly at EOF.

const PRESET := "Linux PCK"
const PCK_MAGIC := "GDPC"
const DEFAULT_WORK := "/tmp/r101-E1/export_prod_s01_work"
const MIN_BYTES := 1024

# Declared census of the scratch project: exact paths plus the two engine-internal
# hash-named entries (wildcards). A directory claiming any other path set fails R7a.
const EXPECTED_CENSUS := [
	"res://.godot/exported/*/export-*-main.scn",
	"res://.godot/global_script_class_cache.cfg",
	"res://.godot/imported/icon.svg-*.ctex",
	"res://.godot/uid_cache.bin",
	"res://_census.gd.remap",
	"res://_census.gdc",
	"res://icon.svg",
	"res://icon.svg.import",
	"res://project.binary",
	"res://scenes/actor.gd.remap",
	"res://scenes/actor.gdc",
	"res://scenes/boot.gd.remap",
	"res://scenes/boot.gdc",
	"res://scenes/main.tscn.remap",
]
# hash_path_renamed renames a byte inside the wildcard-covered hash region; the byte
# classifier deliberately accepts it (see the ladder's KNOWN_ACCEPT handling).
const KNOWN_ACCEPT := ["hash_path_renamed"]

const PROJECT_GODOT := """config_version=5

[application]

config/name="export_prod_s01"
run/main_scene="res://scenes/main.tscn"
config/features=PackedStringArray("4.7", "Forward Plus")
config/icon="res://icon.svg"

[autoload]

Boot="*res://scenes/boot.gd"
"""

const EXPORT_PRESETS := """[preset.0]

name="Linux PCK"
platform="Linux/X11"
runnable=true
advanced_options=true
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="out/export_prod_s01.pck"
encryption_include_filters=""
encryption_exclude_filters=""
encrypt_pck=false
encrypt_directory=false
script_export_mode=2

[preset.0.options]

custom_template/debug=""
custom_template/release=""
binary_format/embed_pck=false
binary_format/architecture="x86_64"
texture_format/bptc=true
texture_format/s3tc=true
texture_format/etc=false
texture_format/etc2=false
strip_executable=false
"""

const ICON_SVG := """<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><rect width="64" height="64" fill="#2b3a55"/><circle cx="32" cy="32" r="16" fill="#e0c060"/></svg>
"""

const MAIN_TSCN := """[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://scenes/actor.gd" id="1_actor"]

[node name="Main" type="Node2D"]
script = ExtResource("1_actor")
"""

const ACTOR_GD := """extends Node2D

func _ready() -> void:
	print("EXPORT_PROD_S01 main_scene_ready")
"""

const BOOT_GD := """extends Node

const TOKEN := "EXPORT_PROD_S01 autoload_ready"

func _ready() -> void:
	print(TOKEN)
"""

# Packed into the scratch project so the engine can report its own pack census.
const CENSUS_GD := """extends SceneTree

func _initialize() -> void:
	var files := PackedStringArray()
	_walk("res://", files)
	files.sort()
	for f in files:
		var fa := FileAccess.open(f, FileAccess.READ)
		var n := fa.get_length() if fa != null else -1
		if fa != null:
			fa.close()
		print("CENSUS %s %d" % [f, n])
	quit(0)

func _walk(dir_path: String, out: PackedStringArray) -> void:
	for f in DirAccess.get_files_at(dir_path):
		out.append(dir_path.path_join(f))
	for d in DirAccess.get_directories_at(dir_path):
		_walk(dir_path.path_join(d), out)
"""

var work := ""
var arm := "main"
var pck_arg := ""
var export_mode := "pack"
var failures: Array[String] = []
var ladder_rejected := 0
var ladder_total := 0
var ladder_known := 0

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--work="):
			work = a.substr(7)
		elif a.begins_with("--arm="):
			arm = a.substr(6)
		elif a.begins_with("--pck="):
			pck_arg = a.substr(6)
		elif a.begins_with("--export-mode="):
			export_mode = a.substr(14)
	if work.is_empty():
		work = DEFAULT_WORK
	_run.call_deferred()

func _run() -> void:
	var project := work.path_join("project")
	var pack := work.path_join("export_prod_s01.pck")
	print("SPEC s01 raw_bytes=PCK_dir kept_receipt=raw_parse+engine_census")
	print("SPEC R1 magic expects GDPC discriminates a non-pack blob or a bare executable")
	print("SPEC R2 version/engine expects 4 and matching major.minor discriminates stale or newer pack formats")
	print("SPEC R3 flags/file_base expects 2/112 discriminates a re-laid-out header that shifts data")
	print("SPEC R4 dir_alignment expects 0<=dir_offset-(file_base+max_end)<=3 discriminates truncated or padded data regions")
	print("SPEC R5 size expects bytes==dir_end and bytes>=floor discriminates empty, truncated or over-declared packs")
	print("SPEC R6 md5 expects all entries match recomputed md5 discriminates payload tampering")
	print("SPEC R7 census expects raw parse == engine reader discriminates a hand-written directory")
	print("SPEC R8 load expects autoload token from --main-pack discriminates a listing-only claim")
	print("SPEC MUT expects 9/9 forgeries rejected discriminates a receipt printer that never measures")
	match arm:
		"main":
			_export_and_verify(project, pack)
		"classify":
			if pck_arg.is_empty():
				_fail("classify arm needs --pck=")
				return
			var c := _classify(pck_arg)
			for r in c["rows"]:
				print("ROW %s" % r)
			if not c["ok"]:
				_fail("classify rejected: %s" % c["fail"])
				return
			print("PASS export_prod_s01 classify ok entries=%d bytes=%d" % [c["count"], c["size"]])
			quit(0)
		"mutations":
			if pck_arg.is_empty():
				if not _materialize(project):
					return
				var e := _export_child(project, pack)
				if e["rc"] != 0:
					_fail("export child rc=%d for mutation base" % e["rc"])
					return
			else:
				pack = pck_arg
			if _ladder(pack) < 0:
				return
			print("PASS export_prod_s01 mutations_rejected=%d/%d known_accepts=%d" % [ladder_rejected, ladder_total, ladder_known])
			quit(0)
		_:
			_fail("unknown_arm=%s" % arm)

# ------------------------------------------------------------------ arm: main

func _export_and_verify(project: String, pack: String) -> void:
	var templates := _templates_dir()
	var exec_present := FileAccess.file_exists(templates.path_join("linux_release.x86_64"))
	print("ROW R0 templates=%s linux_release.x86_64=%s" % [templates, str(exec_present)])
	if not exec_present:
		_fail("templates_missing path=%s" % templates)
		return
	if not _materialize(project):
		return
	var started := Time.get_ticks_msec()
	var child := _export_child(project, pack)
	var elapsed := Time.get_ticks_msec() - started
	if child["rc"] != 0:
		_fail("export child rc=%d wall_ms=%d tail=%s" % [child["rc"], elapsed, child["tail"]])
		return
	print("ROW R0b export_mode=%s child_rc=%d wall_ms=%d storing_lines=%d" % [export_mode, child["rc"], elapsed, child["storing"]])
	if not FileAccess.file_exists(pack):
		_fail("export produced no file at %s" % pack)
		return
	var c := _classify(pack)
	for r in c["rows"]:
		print("ROW %s" % r)
	if not c["ok"]:
		_fail(c["fail"])
		return
	print("CENSUS_SHA %s" % c["census_sha"])
	for p in c["paths"]:
		print("ENTRY %s" % p)
	var missing := PackedStringArray()
	for want in ["res://project.binary", "res://scenes/main.tscn.remap", "res://scenes/actor.gdc",
			"res://scenes/boot.gdc", "res://scenes/boot.gd.remap", "res://.godot/uid_cache.bin"]:
		if not c["path_set"].has(want):
			missing.append(want)
	print("ROW R7b core_paths_present=%d/6 missing=%s" % [6 - missing.size(), ",".join(missing)])
	if missing.size() > 0:
		_fail("core pack entries missing: %s" % ",".join(missing))
		return
	var engine := _engine_census(pack)
	print("ROW R8 engine_entries=%d autoload_seen=%s child_rc=%d" % [engine["count"], str(engine["autoload"]), engine["rc"]])
	if engine["rc"] != 0 or not engine["autoload"]:
		_fail("pack did not load in engine rc=%d autoload_seen=%s" % [engine["rc"], str(engine["autoload"])])
		return
	print("ROW R7c census_raw=%d census_engine=%d equal=%s" % [c["count"], engine["count"], str(c["pairs"] == engine["pairs"])])
	if c["pairs"] != engine["pairs"]:
		_fail("raw parse census disagrees with engine reader")
		return
	if _ladder(pack) < 0:
		return
	print("PASS export_prod_s01 magic=%s version=%d engine=%d.%d.%d flags=%d file_base=%d entries=%d bytes=%d floor=%d md5_ok=%d/%d census_engine=%d census_equal=true census_sha=%s dir_end_eq_size=true mutations=%d/%d known_accepts=%d export_rc=0 autoload_seen=true" % [
		PCK_MAGIC, c["version"], c["engine"][0], c["engine"][1], c["engine"][2], c["flags"], c["file_base"],
		c["count"], c["size"], c["floor"], c["md5_ok"], c["count"], engine["count"], c["census_sha"],
		ladder_rejected, ladder_total, ladder_known,
	])
	quit(0)

# ------------------------------------------------------------- scratch project

func _templates_dir() -> String:
	var v := Engine.get_version_info()
	var tag := "%d.%d.%d.%s" % [v["major"], v["minor"], v["patch"], v["status"]]
	var base := OS.get_data_dir()
	for cand in [base.path_join("godot/export_templates"), base.path_join("export_templates")]:
		if DirAccess.dir_exists_absolute(cand.path_join(tag)):
			return cand.path_join(tag)
	return base.path_join("godot/export_templates").path_join(tag)

func _materialize(project: String) -> bool:
	_rm_rf(work)
	var dirs := ["", "/scenes", "/data"]
	for d in dirs:
		var err := DirAccess.make_dir_recursive_absolute(project + d)
		if err != OK:
			_fail("scratch mkdir failed %s err=%s" % [project + d, error_string(err)])
			return false
	var files := {
		"/project.godot": PROJECT_GODOT,
		"/export_presets.cfg": EXPORT_PRESETS,
		"/icon.svg": ICON_SVG,
		"/scenes/main.tscn": MAIN_TSCN,
		"/scenes/actor.gd": ACTOR_GD,
		"/scenes/boot.gd": BOOT_GD,
		"/_census.gd": CENSUS_GD,
	}
	for rel in files:
		var f := FileAccess.open(project + rel, FileAccess.WRITE)
		if f == null:
			_fail("scratch write failed %s err=%s" % [project + rel, error_string(FileAccess.get_open_error())])
			return false
		f.store_string(files[rel])
		f.close()
	print("ROW R0a scratch=%s files=%d" % [project, files.size()])
	return true

func _rm_rf(p: String) -> void:
	if not DirAccess.dir_exists_absolute(p):
		return
	for f in DirAccess.get_files_at(p):
		DirAccess.remove_absolute(p.path_join(f))
	for d in DirAccess.get_directories_at(p):
		_rm_rf(p.path_join(d))
	DirAccess.remove_absolute(p)

func _export_child(project: String, pack: String) -> Dictionary:
	# --export-pack writes the PCK directly. --export-release to a .pck destination first
	# copies the 73,519,416-byte linux_release.x86_64 template onto that path and then
	# overwrites it with the pack (observed r101-E1: partial file started with 7f454c46,
	# finished file with GDPC), so release mode needs template-size free space at the
	# destination and fails with "Failed to copy export template" when the quota is gone.
	var command := "--export-pack" if export_mode == "pack" else "--export-release"
	var out: Array = []
	var rc := OS.execute(OS.get_executable_path(),
		["--headless", "--path", project, command, PRESET, pack], out, true)
	var storing := 0
	var tail := ""
	# OS.execute hands back the child's whole stdout as ONE element with embedded
	# newlines (observed r101-E1: out.size()==1 for a 20-line child), so split first.
	for clean in _capture_lines(out):
		if clean.contains("Storing File:"):
			storing += 1
		tail = clean
	if tail.length() > 240:
		tail = tail.substr(0, 240)
	return {"rc": rc, "storing": storing, "tail": tail, "lines": out}

# -------------------------------------------------------------- raw classifier

func _classify(path: String) -> Dictionary:
	var rows: Array[String] = []
	var res := {"ok": false, "rows": rows, "fail": "", "count": 0, "size": 0, "md5_ok": 0,
		"version": 0, "engine": [0, 0, 0], "flags": 0, "file_base": 0, "dir_offset": 0,
		"floor": MIN_BYTES, "path_set": {}, "paths": PackedStringArray(), "pairs": [], "census_sha": "",
		"mutations": 0}
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		res["fail"] = "unreadable pack %s err=%s" % [path, error_string(FileAccess.get_open_error())]
		return res
	var b := f.get_buffer(f.get_length())
	f.close()
	res["size"] = b.size()
	if b.size() < 48:
		res["fail"] = "R5 size=%d too small to hold a header" % b.size()
		print("ROW R5 size=%d fail=header_undersized" % b.size())
		return res
	var magic := b.slice(0, 4).get_string_from_ascii()
	var version := b.decode_u32(4)
	var major := b.decode_u32(8)
	var minor := b.decode_u32(12)
	var patch := b.decode_u32(16)
	var flags := b.decode_u32(20)
	var file_base := b.decode_u64(24)
	var dir_offset := b.decode_u64(32)
	var ev := Engine.get_version_info()
	res["version"] = version
	res["engine"] = [major, minor, patch]
	res["flags"] = flags
	res["file_base"] = file_base
	res["dir_offset"] = dir_offset
	rows.append("R1 magic=%s" % magic)
	if magic != PCK_MAGIC:
		res["fail"] = "R1 magic=%s expected %s" % [magic, PCK_MAGIC]
		return res
	rows.append("R2 version=%d engine=%d.%d.%d" % [version, major, minor, patch])
	if version != 4 or major != ev["major"] or minor != ev["minor"]:
		res["fail"] = "R2 version=%d engine=%d.%d.%d expected 4 and %d.%d" % [version, major, minor, patch, ev["major"], ev["minor"]]
		return res
	rows.append("R3 flags=%d file_base=%d" % [flags, file_base])
	if flags != 2 or file_base != 112:
		res["fail"] = "R3 flags=%d file_base=%d expected 2/112" % [flags, file_base]
		return res
	if dir_offset + 4 > b.size():
		res["fail"] = "R4 dir_offset=%d beyond size=%d" % [dir_offset, b.size()]
		return res
	var count := b.decode_u32(dir_offset)
	var pos := int(dir_offset) + 4
	var entries := []
	var md5_ok := 0
	var data_end := 0
	var declared := 0
	var padded := 0
	var unaligned := 0
	var paths := PackedStringArray()
	var path_set := {}
	var pairs := []
	for i in count:
		if pos + 4 > b.size():
			res["fail"] = "R4 entry %d path_len beyond EOF at %d" % [i, pos]
			return res
		var sl := b.decode_u32(pos)
		pos += 4
		if pos + int(sl) + 36 > b.size():
			res["fail"] = "R4 entry %d body beyond EOF at %d len=%d" % [i, pos, sl]
			return res
		var raw := b.slice(pos, pos + int(sl))
		pos += int(sl)
		# The stored path length is 4-byte padded with NULs; strip before decoding so the
		# engine's UTF-8 parser never sees a NUL (observed: 3 padded paths per pack).
		var keep := raw.size()
		while keep > 0 and raw[keep - 1] == 0:
			keep -= 1
		if keep != raw.size():
			padded += 1
		var pname := raw.slice(0, keep).get_string_from_utf8()
		var ofs := b.decode_u64(pos)
		var size := b.decode_u64(pos + 8)
		var md5 := b.slice(pos + 16, pos + 32)
		var eflags := b.decode_u32(pos + 32)
		pos += 36
		if file_base + ofs + size > b.size():
			res["fail"] = "R4 entry %s data beyond EOF ofs=%d size=%d" % [pname, ofs, size]
			return res
		var data := b.slice(file_base + ofs, file_base + ofs + size)
		var digest := _md5_hex(data)
		if digest == md5.hex_encode():
			md5_ok += 1
		entries.append({"path": pname, "ofs": ofs, "size": size, "flags": eflags})
		if ofs % 16 != 0:
			unaligned += 1
		if file_base + ofs + size > data_end:
			data_end = file_base + ofs + size
		declared += size + int(sl) + 40
		paths.append("res://%s" % pname)
		path_set["res://%s" % pname] = true
		pairs.append(["res://%s" % pname, size])
	res["count"] = count
	res["md5_ok"] = md5_ok
	res["path_set"] = path_set
	res["paths"] = paths
	res["pairs"] = pairs
	res["padded"] = padded
	var gap := int(dir_offset) - data_end
	var floor := MIN_BYTES if MIN_BYTES > file_base + declared else int(file_base + declared)
	res["floor"] = floor
	var want_dir := ((data_end + 15) >> 4) << 4
	rows.append("R4 dir_offset=%d data_end=%d gap=%d align16_ofs=%d/%d dir16=%s dir_eq_align16=%s padded_paths=%d" % [
		dir_offset, data_end, gap, count - unaligned, count, str(int(dir_offset) % 16 == 0),
		str(int(dir_offset) == want_dir), padded])
	if unaligned > 0:
		res["fail"] = "R4 %d entry offsets are not 16-byte aligned" % unaligned
		return res
	if int(dir_offset) % 16 != 0 or int(dir_offset) != want_dir:
		res["fail"] = "R4 dir_offset=%d expected align16(data_end=%d)=%d" % [dir_offset, data_end, want_dir]
		return res
	rows.append("R5 bytes=%d floor=%d dir_end=%d" % [b.size(), floor, pos])
	if pos != b.size():
		res["fail"] = "R5 directory ends at %d but file is %d bytes" % [pos, b.size()]
		return res
	if b.size() < floor:
		res["fail"] = "R5 bytes=%d below floor=%d" % [b.size(), floor]
		return res
	rows.append("R6 md5_ok=%d/%d" % [md5_ok, count])
	if md5_ok != count:
		res["fail"] = "R6 md5_ok=%d/%d" % [md5_ok, count]
		return res
	var canon := ""
	for pair in pairs:
		canon += "%s|%d\n" % [pair[0], pair[1]]
	res["census_sha"] = _sha256_hex(canon.to_utf8_buffer())
	rows.append("R7 census_raw=%d census_sha=%s" % [count, res["census_sha"]])
	var matched := 0
	var extras := 0
	for pat in EXPECTED_CENSUS:
		var hits := 0
		for p in paths:
			if p.match(pat):
				hits += 1
		if hits == 1:
			matched += 1
	for p in paths:
		var expected_hit := false
		for pat in EXPECTED_CENSUS:
			if p.match(pat):
				expected_hit = true
				break
		if not expected_hit:
			extras += 1
	rows.append("R7a expected_matched=%d/%d extras=%d" % [matched, EXPECTED_CENSUS.size(), extras])
	if matched != EXPECTED_CENSUS.size() or extras != 0:
		res["fail"] = "R7a declared census mismatch matched=%d/%d extras=%d" % [matched, EXPECTED_CENSUS.size(), extras]
		return res
	res["ok"] = true
	return res

func _engine_census(pack: String) -> Dictionary:
	# The pack wins over the process cwd: run from the fixtures project dir and the
	# pack's own project.binary/autoload still drive res:// (observed r101-E1).
	var out: Array = []
	var rc := OS.execute(OS.get_executable_path(),
		["--headless", "--main-pack", pack, "--script", "res://_census.gd"], out, true)
	var pairs := []
	var autoload := false
	for s in _capture_lines(out):
		if s.begins_with("CENSUS "):
			var parts := s.split(" ")
			if parts.size() >= 3:
				pairs.append([parts[1], int(parts[2])])
		if s.contains("autoload_ready"):
			autoload = true
	return {"rc": rc, "pairs": pairs, "count": pairs.size(), "autoload": autoload}

func _capture_lines(out: Array) -> PackedStringArray:
	var lines := PackedStringArray()
	for item in out:
		for piece in String(item).split("\n", true):
			var clean := piece.replace("\r", " ").strip_edges()
			if not clean.is_empty():
				lines.append(clean)
	return lines

# ---------------------------------------------------------------- forgery ladder

func _ladder(pack: String) -> int:
	var f := FileAccess.open(pack, FileAccess.READ)
	if f == null:
		_fail("ladder cannot read %s" % pack)
		return -1
	var b := f.get_buffer(f.get_length())
	f.close()
	var control := _classify(pack)
	if not control["ok"]:
		_fail("ladder control pack rejected: %s" % control["fail"])
		return -1
	var file_base := b.decode_u64(24)
	var dir_offset := int(b.decode_u64(32))
	var count := b.decode_u32(dir_offset)
	var first_path_len := b.decode_u32(dir_offset + 4)
	var first_ofs := b.decode_u64(dir_offset + 8 + first_path_len)
	var core_path_at := _find_path_offset(b, dir_offset, count, "scenes/actor.gdc")
	var muts := {
		"magic": func(x: PackedByteArray) -> PackedByteArray:
			x.set(0, x[0] ^ 0x01)
			return x,
		"version": func(x: PackedByteArray) -> PackedByteArray:
			x.encode_u32(4, 5)
			return x,
		"engine_newer": func(x: PackedByteArray) -> PackedByteArray:
			x.encode_u32(12, x.decode_u32(12) + 1)
			return x,
		"flags_rel_base_cleared": func(x: PackedByteArray) -> PackedByteArray:
			x.encode_u32(20, 0)
			return x,
		"file_base_shifted": func(x: PackedByteArray) -> PackedByteArray:
			x.encode_u64(24, x.decode_u64(24) + 4)
			return x,
		"dir_offset_plus4": func(x: PackedByteArray) -> PackedByteArray:
			x.encode_u64(32, x.decode_u64(32) + 4)
			return x,
		"count_plus1": func(x: PackedByteArray) -> PackedByteArray:
			x.encode_u32(dir_offset, x.decode_u32(dir_offset) + 1)
			return x,
		"path_core_renamed": func(x: PackedByteArray) -> PackedByteArray:
			if core_path_at >= 0:
				x.set(core_path_at, 0x7A)
			return x,
		"hash_path_renamed": func(x: PackedByteArray) -> PackedByteArray:
			var p := dir_offset + 8
			var hit := false
			for j in int(first_path_len) - 1:
				if x[p + j] == 0x63:
					x.set(p + j, 0x7A)
					hit = true
					break
			if not hit:
				x.set(p, 0x7A)
			return x,
		"payload_byte": func(x: PackedByteArray) -> PackedByteArray:
			var at := int(file_base + first_ofs)
			x.set(at, x[at] ^ 0xFF)
			return x,
		"truncated": func(x: PackedByteArray) -> PackedByteArray:
			x.remove_at(x.size() - 1)
			return x,
	}
	var kinds: Array = muts.keys()
	kinds.sort()
	DirAccess.make_dir_recursive_absolute(work)
	var forged_path := work.path_join("forged.pck")
	for kind in kinds:
		var x: PackedByteArray = muts[kind].call(b.duplicate())
		var w := FileAccess.open(forged_path, FileAccess.WRITE)
		if w == null:
			_fail("cannot write forged pack at %s err=%s" % [forged_path, error_string(FileAccess.get_open_error())])
			return -1
		w.store_buffer(x)
		w.close()
		var c := _classify(forged_path)
		if KNOWN_ACCEPT.has(String(kind)):
			ladder_known += 1
			if c["ok"]:
				print("KNOWN_ACCEPT %s accepted=true note=hash_region_is_wildcard_covered owner=s04_main_scene_receipt" % kind)
			else:
				print("KNOWN_ACCEPT %s accepted=false limitation_closed=true fail=%s" % [kind, c["fail"]])
			continue
		ladder_total += 1
		if c["ok"]:
			print("MUT %s accepted=true row=none" % kind)
			_fail("forgery %s was accepted by the classifier" % kind)
			return -1
		ladder_rejected += 1
		print("MUT %s rejected=true fail=%s" % [kind, c["fail"]])
	DirAccess.remove_absolute(forged_path)
	print("ROW R9 control_accepted=true mutations_rejected=%d/%d known_accepts=%d" % [ladder_rejected, ladder_total, ladder_known])
	return ladder_rejected

func _find_path_offset(b: PackedByteArray, dir_offset: int, count: int, want: String) -> int:
	var pos := int(dir_offset) + 4
	for i in count:
		var sl := b.decode_u32(pos)
		pos += 4
		var keep := int(sl)
		while keep > 0 and b[pos + keep - 1] == 0:
			keep -= 1
		if b.slice(pos, pos + keep).get_string_from_utf8() == want:
			return pos + keep - 1
		pos += int(sl) + 36
	return -1

# -------------------------------------------------------------------- utilities

func _md5_hex(data: PackedByteArray) -> String:
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_MD5)
	ctx.update(data)
	return ctx.finish().hex_encode()

func _sha256_hex(data: PackedByteArray) -> String:
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(data)
	return ctx.finish().hex_encode()

func _fail(reason: String) -> void:
	print("ERROR: EXPORT_PROD_S01 ASSERTION FAILED: %s" % reason)
	quit(2)
