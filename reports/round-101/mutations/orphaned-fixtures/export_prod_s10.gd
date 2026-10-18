extends SceneTree
##
## export_prod scenario 10 (owner r101-E10): icon and `.uid` census of an exported pack.
##
## Standalone:  godot --headless --script corpus/fixtures/export_prod_s10.gd
## Scratch:     /tmp/r101-E10/s10  (self-contained; exports a fresh project, never repo state)
##
## Observed engine: 4.7.2.stable.arch_linux.ed1daf0bf, templates 4.7.2.stable (linux_release.x86_64).
## Every assertion below is derived from bytes this script itself wrote, or from bytes it read
## back out of the produced pack. No literal UID is pinned: Godot mints a fresh random UID per
## project, so the pin is the *cross-consistency* between pack, disk sidecars and text carriers.

const SCRATCH_ROOT := "/tmp/r101-E10"
const PROJ := SCRATCH_ROOT + "/s10"
const OUT_PCK := PROJ + "/out/game.pck"
const OUT_ZIP := PROJ + "/out/game.zip"
const PRESET := "Linux/X11"

const PROJECT_GODOT := """config_version=5

[application]

config/name="s10_probe"
run/main_scene="res://main.tscn"
config/features=PackedStringArray("4.7", "GL Compatibility")
config/icon="res://icon.svg"

[rendering]

renderer/rendering_method="gl_compatibility"
"""
const ICON_SVG := """<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128"><rect width="128" height="128" fill="#478cbf"/><circle cx="64" cy="64" r="40" fill="#ffffff"/></svg>
"""
const PROBE_GD := """extends Node

const MARK := "s10_probe_actor"
"""
const MAIN_TSCN := """[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://probe_actor.gd" id="1"]

[node name="Main" type="Node"]
script = ExtResource("1")
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
export_path="out/game.pck"
patches=PackedStringArray()
encryption_include_filters=""
encryption_exclude_filters=""
seed=0
encrypt_pck=false
encrypt_directory=false

[preset.0.options]

binary_format/architecture="x86_64"
binary_format/embed_pck=false
"""

const ICON_SRC_BYTES := 166
const UID_SIDECAR_SCRIPT := "res://probe_actor.gd.uid"
const UID_CACHE := "res://.godot/uid_cache.bin"
const ICON_SRC := "res://icon.svg"
const ICON_IMPORT := "res://icon.svg.import"

var _rows: Array[String] = []
var _fails: Array[String] = []


func _initialize() -> void:
	var exe := OS.get_executable_path()
	_build_project()
	var exported := _export(exe)
	var pck := _parse_pck(FileAccess.get_file_as_bytes(OUT_PCK))
	_row("scratch", PROJ)
	_row("godot", exe)
	_row("engine", Engine.get_version_info()["string"])
	_scenario_header(pck, exported)
	_scenario_icon(pck)
	_scenario_uid_census(pck)
	_scenario_uid_carriers(pck)
	_scenario_zip_cross_reader(pck)
	_scenario_forgery_rejection(pck)
	_finish()


# ---------------------------------------------------------------- project build

func _build_project() -> void:
	_rm_rf(PROJ)
	DirAccess.make_dir_recursive_absolute(PROJ + "/out")
	var files := {
		"project.godot": [PROJECT_GODOT, 0],
		"icon.svg": [ICON_SVG, ICON_SRC_BYTES],
		"probe_actor.gd": [PROBE_GD, 0],
		"main.tscn": [MAIN_TSCN, 0],
		"export_presets.cfg": [PRESETS_CFG, 0],
	}
	var shapes := {"project.godot": 239, "icon.svg": ICON_SRC_BYTES, "probe_actor.gd": 46, "main.tscn": 156, "export_presets.cfg": 446}
	for name in files.keys():
		var text: String = files[name][0]
		var want := text.to_utf8_buffer().size()
		var on_disk := _write_text(PROJ + "/" + name, text)
		if on_disk != want:
			_fail("write:" + name, "wrote %d want %d" % [on_disk, want])
		if on_disk != shapes[name]:
			_fail("shape:" + name, "utf8 %d observed-literal %d" % [on_disk, shapes[name]])
	_row("src_shapes", _join(["project.godot=239", "icon.svg=166", "probe_actor.gd=46", "main.tscn=156", "export_presets.cfg=446"]))


func _write_text(path: String, text: String) -> int:
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		_fail("open_write", path)
		return -1
	f.store_string(text)
	f.close()
	var back := FileAccess.get_file_as_bytes(path)
	return back.size()


func _rm_rf(dir_path: String) -> void:
	var d := DirAccess.open(dir_path)
	if d == null:
		return
	d.list_dir_begin()
	var n := d.get_next()
	while n != "":
		if n != "." and n != "..":
			var p := dir_path.path_join(n)
			if d.current_is_dir():
				_rm_rf(p)
			else:
				DirAccess.remove_absolute(p)
		n = d.get_next()
	d.list_dir_end()
	DirAccess.remove_absolute(dir_path)


# ---------------------------------------------------------------- export

func _export(exe: String) -> Dictionary:
	var out := []
	var rc := OS.execute(exe, ["--headless", "--path", PROJ, "--export-pack", PRESET, OUT_PCK], out, true)
	var log := " ".join(out)
	var saved := _count(log, "Storing File:")
	if rc != 0:
		_fail("export:rc", str(rc))
	if saved == 0:
		_fail("export:no_store", log.substr(0, 400))
	var out2 := []
	var rc2 := OS.execute(exe, ["--headless", "--path", PROJ, "--export-pack", PRESET, OUT_ZIP], out2, true)
	if rc2 != 0:
		_fail("export:zip_rc", str(rc2))
	_row("export_receipt", "pck_rc=%d zip_rc=%d stored=%d pck_bytes=%d zip_bytes=%d" % [
		rc, rc2, saved, FileAccess.get_file_as_bytes(OUT_PCK).size(), FileAccess.get_file_as_bytes(OUT_ZIP).size()])
	return {"rc": rc, "rc2": rc2, "stored": saved}


func _count(hay: String, needle: String) -> int:
	var n := 0
	var i := hay.find(needle)
	while i != -1:
		n += 1
		i = hay.find(needle, i + needle.length())
	return n


# ---------------------------------------------------------------- PCK reader

## Pack format (v4, observed): magic u32 "GDPC"; format u32; ver major/minor/patch u32x3;
## pack_flags u32; file_base u64; table_offset u64; reserved to file_base; then at table_offset:
## file_count u32 and, per file, path_len u32 (already 4-aligned), path bytes (NUL padded),
## ofs u64, size u64, md5 16, flags u32. Entry offsets are relative to file_base.
func _parse_pck(d: PackedByteArray) -> Dictionary:
	var res := {"ok": false, "magic": "", "format": -1, "ver": "", "flags": -1, "file_base": -1, "table": -1, "entries": [], "bytes": d}
	if d.size() < 128:
		_fail("pck:short", str(d.size()))
		return res
	if d.slice(0, 4).get_string_from_ascii() != "GDPC":
		_fail("pck:magic", d.slice(0, 4).hex_encode())
		return res
	res["magic"] = "GDPC"
	res["format"] = d.decode_u32(4)
	res["ver"] = "%d.%d.%d" % [d.decode_u32(8), d.decode_u32(12), d.decode_u32(16)]
	res["flags"] = d.decode_u32(20)
	res["file_base"] = d.decode_u64(24)
	res["table"] = d.decode_u64(32)
	var p := int(res["table"])
	var count := d.decode_u32(p)
	p += 4
	for i in range(count):
		var pl := d.decode_u32(p)
		p += 4
		# Pack paths are stored WITHOUT the "res://" prefix (observed: "icon.svg",
		# ".godot/uid_cache.bin"); re-add it so every expectation below speaks res://.
		# path_len already includes the 4-byte padding, so trailing NULs must be dropped
		# from the bytes (not from a decoded String) to avoid NUL-in-text warnings.
		var raw := d.slice(p, p + pl)
		while raw.size() > 0 and raw[raw.size() - 1] == 0:
			raw.resize(raw.size() - 1)
		var path := "res://" + raw.get_string_from_ascii()
		p += pl
		var ofs := d.decode_u64(p)
		var size := d.decode_u64(p + 8)
		p += 16
		var md5 := d.slice(p, p + 16).hex_encode()
		p += 16
		var flags := d.decode_u32(p)
		p += 4
		var body := d.slice(int(res["file_base"]) + int(ofs), int(res["file_base"]) + int(ofs) + int(size))
		var entry := {"path": path, "size": int(size), "sha256": _sha256(body), "md5_ok": _md5(body) == md5, "flags": int(flags), "body": body}
		if not entry["md5_ok"]:
			_fail("pck:md5", path)
		res["entries"].append(entry)
	res["ok"] = true
	return res


# ---------------------------------------------------------------- scenarios

func _scenario_header(pck: Dictionary, exported: Dictionary) -> void:
	_row("hdr", "magic=%s format=%d ver=%s flags=%d file_base=%d table=%d" % [
		pck["magic"], pck["format"], pck["ver"], pck["flags"], pck["file_base"], pck["table"]])
	var vi := Engine.get_version_info()
	var want_ver := "%d.%d.%d" % [vi["major"], vi["minor"], vi["patch"]]
	if String(pck["ver"]) != want_ver:
		_fail("hdr:ver", "%s vs engine %s" % [pck["ver"], want_ver])
	_check(int(pck["entries"].size()) == 10, "count", "file_count=%d" % pck["entries"].size())
	_check(exported["stored"] == 10, "log_count", "stored_lines=%d" % exported["stored"])
	var paths := PackedStringArray()
	for e in pck["entries"]:
		paths.append(e["path"])
	paths.sort()
	_row("path_set_sha256", _sha256(paths[0].to_utf8_buffer()) + " " + ",".join(paths))
	_row("count", "entries=%d md5_all_ok=%s" % [paths.size(), str(_all_md5(pck))])


func _scenario_icon(pck: Dictionary) -> void:
	var svg: Dictionary = _entry(pck, ICON_SRC)
	var imp: Dictionary = _entry(pck, ICON_IMPORT)
	_check(svg["size"] == ICON_SRC_BYTES, "icon:src_size", "pack=%d disk=%d" % [svg["size"], FileAccess.get_file_as_bytes(PROJ + "/icon.svg").size()])
	var imp_text: String = imp["body"].get_string_from_utf8()
	var ref: String = _extract(imp_text, "path=\"", "\"")
	var ctex: Dictionary = _entry(pck, ref if ref.begins_with("res://") else ("res://" + ref))
	_row("icon_entries", "src=%d import=%d ctex=%d ref=%s" % [svg["size"], imp["size"], ctex["size"], ref])
	_check(ctex["size"] > 600, "icon:ctex_size", str(ctex["size"]))
	_check(ctex["body"].slice(0, 4).get_string_from_ascii() == "GST2", "icon:ctex_magic", ctex["body"].slice(0, 4).hex_encode())
	_check(ref.begins_with("res://.godot/imported/") and ref.ends_with(".ctex"), "icon:ref_shape", ref)
	var proj_text: String = FileAccess.get_file_as_bytes(PROJ + "/project.godot").get_string_from_utf8()
	var icon_setting: String = _extract(proj_text, "config/icon=\"", "\"")
	_check(icon_setting == ICON_SRC, "icon:setting", icon_setting)
	_check(_has(pck, icon_setting), "icon:setting_packed", icon_setting)
	_row("icon_sha256", "src=%s ctex=%s" % [svg["sha256"].substr(0, 16), ctex["sha256"].substr(0, 16)])


func _scenario_uid_census(pck: Dictionary) -> void:
	var uid_files: Array[String] = []
	var uid_ish: Array[String] = []
	for e in pck["entries"]:
		var p: String = e["path"]
		if p.ends_with(".uid"):
			uid_files.append(p)
		if p.to_lower().contains("uid"):
			uid_ish.append(p)
	_row("uid_sidecar_packed", "count=%d %s" % [uid_files.size(), ",".join(uid_files)])
	_check(uid_files.size() == 0, "uid:no_sidecar_entries", ",".join(uid_files))
	_check(uid_ish.size() == 1 and uid_ish[0] == UID_CACHE, "uid:only_cache", ",".join(uid_ish))
	_check(FileAccess.file_exists(PROJ + "/probe_actor.gd.uid"), "uid:sidecar_on_disk", "missing")
	_check(not FileAccess.file_exists(PROJ + "/icon.svg.uid"), "uid:no_icon_sidecar", "icon.svg.uid exists")


func _scenario_uid_carriers(pck: Dictionary) -> void:
	var disk_cache: PackedByteArray = FileAccess.get_file_as_bytes(PROJ + "/.godot/uid_cache.bin")
	var packed_cache: Dictionary = _entry(pck, UID_CACHE)
	_check(packed_cache["sha256"] == _sha256(disk_cache), "uid:cache_identity", "pack_sha=%s disk_sha=%s" % [String(packed_cache["sha256"]).substr(0, 16), _sha256(disk_cache).substr(0, 16)])
	var cache: Dictionary = _parse_uid_cache(packed_cache["body"])
	var sidecar_text: String = FileAccess.get_file_as_bytes(PROJ + "/probe_actor.gd.uid").get_string_from_utf8().strip_edges()
	var script_id: int = ResourceUID.text_to_id(sidecar_text)
	var imp_text: String = _entry(pck, ICON_IMPORT)["body"].get_string_from_utf8()
	var icon_id: int = ResourceUID.text_to_id(_extract(imp_text, "uid=\"", "\""))
	# ResourceUID.has_id() consults the *current* process registry, which knows nothing about the
	# scratch project's UIDs; validity is therefore pinned via text_to_id != INVALID_ID.
	_check(script_id != ResourceUID.INVALID_ID and sidecar_text.begins_with("uid://"), "uid:sidecar_text", sidecar_text)
	var script_hit: int = cache.get("res://probe_actor.gd", -1)
	var icon_hit: int = cache.get("res://icon.svg", -1)
	_row("uid_cache", "entries=%d script=%s icon=%s cache_bytes=%d" % [
		cache.size(), _uid_str(script_hit), _uid_str(icon_hit), packed_cache["size"]])
	_check(cache.size() == 2, "uid:cache_count", str(cache.size()))
	_check(script_hit == script_id, "uid:script_match", "%s vs sidecar %s" % [_uid_str(script_hit), _uid_str(script_id)])
	_check(icon_hit == icon_id, "uid:icon_match", "%s vs import %s" % [_uid_str(icon_hit), _uid_str(icon_id)])
	# Byte search is done on the hex rendering: PackedByteArray.find() takes a byte value, not a
	# subsequence, so a hex String search is the honest way to look for an 8-byte UID in the pack.
	var whole_hex: String = pck["bytes"].hex_encode()
	var needle: String = _uid_bytes(script_id).hex_encode()
	var occ: int = _count(whole_hex, needle)
	var occ_be: int = _count(whole_hex, _uid_bytes(script_id, true).hex_encode())
	var gdc_hex: String = _entry(pck, "res://probe_actor.gdc")["body"].hex_encode()
	var in_gdc: int = _count(gdc_hex, needle)
	_check(occ >= 1, "uid:transit_present", "occ=%d first_at=%d" % [occ, whole_hex.find(needle) / 2])
	_check(occ_be == 0, "uid:no_big_endian", str(occ_be))
	_check(in_gdc == 0, "uid:not_in_gdc", "gdc carries script uid")
	var carriers := PackedStringArray()
	var in_cache := 0
	for e in pck["entries"]:
		var hits: int = _count(String(e["body"].hex_encode()), needle)
		if hits > 0:
			carriers.append("%s(%d)" % [e["path"], hits])
			if String(e["path"]) == UID_CACHE:
				in_cache = hits
	_check(in_cache == 1 and carriers.size() >= 1, "uid:carrier_set", "in_cache=%d carriers=%s" % [in_cache, ",".join(carriers)])
	_row("uid_transit", "script_uid_occ=%d be_occ=%d in_gdc=%d carriers=%s remap=%s" % [
		occ, occ_be, in_gdc, ",".join(carriers),
		_entry(pck, "res://probe_actor.gd.remap")["body"].get_string_from_utf8().replace("\n", "\\n")])


## uid_cache.bin layout (observed): u32 count, then per entry u64 uid (little endian) +
## u32 path_len + path bytes (already 4-aligned).
func _parse_uid_cache(d: PackedByteArray) -> Dictionary:
	var out := {}
	if d.size() < 4:
		return out
	var n := d.decode_u32(0)
	var p := 4
	for i in range(n):
		var uid := d.decode_u64(p)
		p += 8
		var pl := d.decode_u32(p)
		p += 4
		out[d.slice(p, p + pl).get_string_from_ascii()] = uid
		p += pl
	return out


func _uid_bytes(id: int, big_endian: bool = false) -> PackedByteArray:
	var b := PackedByteArray()
	for i in range(8):
		var shift := (8 * (7 - i)) if big_endian else (8 * i)
		b.append((id >> shift) & 0xFF)
	return b


func _scenario_zip_cross_reader(pck: Dictionary) -> void:
	var z := ZIPReader.new()
	var oerr := z.open(OUT_ZIP)
	if oerr != OK:
		_fail("zip:open", str(oerr))
		return
	var names := z.get_files()
	names.sort()
	var zip_names := PackedStringArray()
	for n in names:
		zip_names.append("res://" + String(n))
	var pack_names := PackedStringArray()
	for e in pck["entries"]:
		pack_names.append(e["path"])
	zip_names.sort()
	pack_names.sort()
	_check(",".join(zip_names) == ",".join(pack_names), "zip:path_set", "%d vs %d" % [zip_names.size(), pack_names.size()])
	var mismatched: Array[String] = []
	for e in pck["entries"]:
		# ZIP entries are stored without the "res://" prefix, unlike GenFile paths.
		var body := z.read_file(String(e["path"]).trim_prefix("res://"))
		if body.size() != e["size"] or _sha256(body) != e["sha256"]:
			mismatched.append(e["path"])
		_check(not String(e["path"]).ends_with(".uid"), "zip:uid_entry", e["path"])
	z.close()
	_check(mismatched.size() == 0, "zip:bytes_match", ",".join(mismatched))
	_row("zip_census", "entries=%d paths_match=true bytes_match=%s" % [zip_names.size(), str(mismatched.size() == 0)])


func _scenario_forgery_rejection(pck: Dictionary) -> void:
	var good := _census(pck)
	_check(_census_ok(good), "forgery:baseline", "the real census failed verification")
	var forged_removed := good.duplicate(true)
	forged_removed["paths"].erase("res://icon.svg.import")
	var forged_added := good.duplicate(true)
	forged_added["paths"].append("res://probe_actor.gd.uid")
	forged_added["sizes"]["res://probe_actor.gd.uid"] = 20
	var forged_size := good.duplicate(true)
	forged_size["sizes"][UID_CACHE] = int(good["sizes"].get(UID_CACHE, 0)) + 1
	var forged_cache := good.duplicate(true)
	forged_cache["uid_cache"] = {}
	var rejected := [
		not _census_ok(forged_removed),
		not _census_ok(forged_added),
		not _census_ok(forged_size),
		not _census_ok(forged_cache),
	]
	_row("forgery_controls", "removed=%s added_uid_sidecar=%s size_delta=%s empty_cache=%s" % [
		str(rejected[0]), str(rejected[1]), str(rejected[2]), str(rejected[3])])
	for i in range(rejected.size()):
		_check(rejected[i], "forgery:rejected_%d" % i, "forgery accepted")


func _census(pck: Dictionary) -> Dictionary:
	var c := {"paths": [], "sizes": {}, "sha256": {}, "uid_cache": _parse_uid_cache(_entry(pck, UID_CACHE)["body"])}
	for e in pck["entries"]:
		c["paths"].append(e["path"])
		c["sizes"][e["path"]] = e["size"]
		c["sha256"][e["path"]] = e["sha256"]
	c["paths"].sort()
	return c


## Fail-closed census verifier: a census is only accepted if it is internally consistent and
## matches the byte-level facts this scenario pins (icon triple present, zero .uid entries,
## two-entry uid cache carrying the icon and script UIDs).
func _census_ok(c: Dictionary) -> bool:
	if not c["paths"].has(ICON_SRC) or not c["paths"].has(ICON_IMPORT):
		return false
	for p in c["paths"]:
		if p.ends_with(".uid"):
			return false
	if not c["sha256"].has(UID_CACHE):
		return false
	var cache: Dictionary = c["uid_cache"]
	if cache.size() != 2 or not cache.has("res://icon.svg") or not cache.has("res://probe_actor.gd"):
		return false
	# The declared uid_cache size must equal what the parsed content implies
	# (u32 count + per entry: 8-byte uid + 4-byte exact path length + path bytes).
	var want_bytes := 4
	for p in cache.keys():
		want_bytes += 12 + String(p).length()
	if int(c["sizes"].get(UID_CACHE, -1)) != want_bytes:
		return false
	var ctex_seen := false
	for p in c["paths"]:
		if p.begins_with("res://.godot/imported/icon.svg-") and p.ends_with(".ctex"):
			ctex_seen = c["sizes"][p] > 600
	return ctex_seen


# ---------------------------------------------------------------- helpers

func _entry(pck: Dictionary, path: String) -> Dictionary:
	for e in pck["entries"]:
		if e["path"] == path:
			return e
	_fail("missing_entry", path)
	return {"path": path, "size": -1, "sha256": "", "md5_ok": false, "flags": -1, "body": PackedByteArray()}


func _has(pck: Dictionary, path: String) -> bool:
	for e in pck["entries"]:
		if e["path"] == path:
			return true
	return false


func _all_md5(pck: Dictionary) -> bool:
	for e in pck["entries"]:
		if not e["md5_ok"]:
			return false
	return true


func _extract(text: String, pre: String, post: String) -> String:
	var a := text.find(pre)
	if a == -1:
		_fail("extract", pre)
		return ""
	a += pre.length()
	var b := text.find(post, a)
	if b == -1:
		return text.substr(a)
	return text.substr(a, b - a)


func _sha256(b: PackedByteArray) -> String:
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(b)
	return ctx.finish().hex_encode()


func _md5(b: PackedByteArray) -> String:
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_MD5)
	ctx.update(b)
	return ctx.finish().hex_encode()


func _uid_str(id: int) -> String:
	return "none" if id == -1 else "uid://" + str(id)


func _join(parts: Array) -> String:
	return " ".join(PackedStringArray(parts))


func _row(name: String, value: String) -> void:
	_rows.append("ROW %s = %s" % [name, value])
	print(_rows[-1])


func _check(cond: bool, name: String, detail: String) -> void:
	if cond:
		_row("ok " + name, detail)
	else:
		_fail(name, detail)


func _fail(name: String, detail: String) -> void:
	_fails.append("%s: %s" % [name, detail])
	print("FAIL %s = %s" % [name, detail])


func _finish() -> void:
	if _fails.is_empty():
		print("PASS export_prod_s10 icon_pack_entries=3 uid_file_entries=0 uid_cache_entries=2 uid_cache_pack_eq_disk=1 script_uid_transit=uid_cache zip_cross_reader_match=1 forgeries_rejected=4/4")
		quit(0)
	else:
		print("FAIL export_prod_s10 failures=%d %s" % [_fails.size(), _join(_fails)])
		quit(1)
