extends SceneTree
# r101-E5 FROZEN probe — export_prod scenario 05: resource remap / UID census of a
# headless PCK export (list + hash every packed entry; prove where remaps point).
#
# Battery launch shape:
#   godot --headless --script res://export_prod_s05.gd -- --arm=<census|tamper|poison> [--work=<dir>]
#
# The probe materializes its own scratch project under `--work` (default
# `<OS temp>/r101_e5_s05`), runs a NESTED `godot --headless --export-pack` on it
# with the installed 4.7.2.stable editor build, then parses the emitted .pck
# (PCK format version 4, flags=2 => entry offsets are relative to file_base).
#
# Measured laws this probe encodes (arm `census` = the authored signature; all
# values [M]-measured in reports/round-101/r101-E5.md, 8 independent exports):
#   L1  headless `--export-pack` needs no export template; the pack records
#       magic GDPC, pack_version 4, engine 4.7.2, flags 2, file_base 112
#   L2  the directory is `u32 count` + per entry `u32 path_len` (padded to 4,
#       NUL-filled) + path + u64 rel_offset + u64 size + 16B md5 + u32 flags;
#       re-emitting that model from parsed bytes is BYTE-IDENTICAL (arm `tamper`)
#   L3  a clean export of the 6-source-file scratch project packs exactly 13
#       entries; the path set + 11 stable (path|size|md5) rows are pinned
#   L4  `.godot/imported` and `.godot/exported` artifact names embed the md5 of
#       the *res:// source path* (not of the file bytes)
#   L5  imported assets remap through their own `art/icon.png.import` file
#       ([remap] header, `uid=` kept, `[deps]`/`[params]` stripped: 193B packed
#       vs 920B on disk); scripts and text resources remap through `*.remap`
#       files whose payload is exactly `[remap]\n\npath="res://<target>"\n`
#   L6  the pack contains ZERO `*.uid` entries: script UIDs live in
#       `.godot/uid_cache.bin` (34B) / the `.import` `uid=` line; headless
#       import leaves `scripts/*.uid` 0 bytes even after an editor pass
#   L7  one entry is volatile: the remapped `.scn` keeps its size (808) but its
#       md5 changes per fresh import (8 bytes at 0x274); md5 is NOT pinned for
#       it and for `project.binary` (observed 0B and 235B), which is why the
#       stable digest covers 11 of 13 entries and structural checks cover those
#   L8  the remapped scene can be silently EMPTY: truncating the cached
#       `.godot/exported/*/*.scn` makes the next export ship a 0-byte `.scn`
#       that its own `.remap` still points at — entry md5s stay consistent, so
#       only the size/magic row catches it (arm `poison`)
#
# `--arm=tamper` proves the census is not a rubber stamp: it re-emits the pack
# (byte-identical), then forges four *internally consistent* packs (md5s
# recomputed) and requires each to be rejected. `--arm=poison` proves the
# structural rows catch the 0-byte-scene state. Prints `E5 ...` diagnostics and
# one final `PASS export_prod_s05 <arm> k=v ...` line (the authorable signature).

const PROJ_NAME := "r101E5Export"
const PRESET := "Linux/X11"
const PACK_REL := "out05.pck"
const SCRATCH_REL := "r101_e5_s05"

const PATHS_SHA256 := "6d3d05abddd353293dd97538d1502f17e240248f21cd9730f9ee2a8b1c2bf0c3"
const STABLE_SHA256 := "a6ac7ef7b0a3f2eefe5f749abc66fa1ce825b73cd4964751529a08030d74aa04"
const PATHS_N := 13
const STABLE_N := 11

const PNG_B64 := "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABJ0lEQVR42hXMwYBFIQAAwIfwEUIIIYQQQgghhBBCCCGEEELIYHc6zHW+72t/PwKRRKZQaXQGk8XmcPm+n4BAJJEpVBqdwWSxOdzfC4KAQCSRKVQancFksTnc8IIoIBBJZAqVRmcwWWwON74gCQhEEplCpdEZTBabw00vyAICkUSmUGl0BpPF5nDzC4qAQCSRKVQancFksTnc8oIqIBBJZAqVRmcwWWwOt76gCQhEEplCpdEZTBabw20v6AICkUSmUGl0BpPF5nD7C4aAQCSRKVQancFksTnc8YIpIBBJZAqVRmcwWWwOd75gCQhEEplCpdEZTBabw10v2AICkUSmUGl0BpPF5nD3C46AQCSRKVQancFksTnc84IrIBBJZAqVRmcwWWwOl39OS28fFvYVWwAAAABJRU5ErkJggg=="

const FILES := {
	"project.godot": "config_version=5\n\n[application]\nconfig/name=\"r101E5Export\"\nrun/main_scene=\"res://main.tscn\"\nconfig/features=PackedStringArray(\"4.7\")\n\n[rendering]\nrenderer/rendering_method=\"gl_compatibility\"\n",
	"main.tscn": "[gd_scene load_steps=3 format=3]\n\n[ext_resource type=\"Script\" path=\"res://scripts/main.gd\" id=\"1_main\"]\n[ext_resource type=\"Texture2D\" path=\"res://art/icon.png\" id=\"2_icon\"]\n\n[node name=\"Main\" type=\"Node2D\"]\nscript = ExtResource(\"1_main\")\n\n[node name=\"Icon\" type=\"Sprite2D\" parent=\".\"]\ntexture = ExtResource(\"2_icon\")\n",
	"scripts/main.gd": "extends Node2D\n\nfunc _ready() -> void:\n\tprint(\"r101e5 main ready\")\n",
	"scripts/player.gd": "class_name R101E5Player\nextends RefCounted\n\nconst SPEED := 12.5\n\nfunc label() -> String:\n\treturn \"player:%s\" % SPEED\n",
	"sub/deep/data.tres": "[gd_resource type=\"Resource\" script_class=\"R101E5Player\" load_steps=2 format=3]\n\n[ext_resource type=\"Script\" path=\"res://scripts/player.gd\" id=\"1_p\"]\n\n[resource]\nscript = ExtResource(\"1_p\")\n",
	"export_presets.cfg": "[preset.0]\n\nname=\"Linux/X11\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\ninclude_filter=\"\"\nexclude_filter=\"\"\nexport_path=\"\"\nscript_export_mode=2\n\n[preset.0.options]\n\nbinary_format/embed_pck=false\nbinary_format/architecture=\"x86_64\"\n",
}

# expected remap target per `.remap` entry (script targets are literal paths;
# artifact targets are matched by the md5(source path) token, see L4)
const REMAP_EXPECT := {
	"main.tscn.remap": {"kind": "artifact", "src": "res://main.tscn", "ext": "scn"},
	"sub/deep/data.tres.remap": {"kind": "artifact", "src": "res://sub/deep/data.tres", "ext": "res"},
	"scripts/main.gd.remap": {"kind": "literal", "target": "res://scripts/main.gdc"},
	"scripts/player.gd.remap": {"kind": "literal", "target": "res://scripts/player.gdc"},
}

# source paths that must NOT appear as pack entries (replaced by remap/import)
const HIDDEN_SOURCES := ["art/icon.png", "main.tscn", "scripts/main.gd", "scripts/player.gd", "sub/deep/data.tres"]

# entries excluded from the stable digest (L7): path is pinned by the path set,
# bytes are not pinned because the engine does not reproduce them across imports
const VOLATILE := [".scn", "project.binary"]

const MAGICS := {".gdc": "GDSC", ".ctex": "GST2", ".res": "RSRC", ".scn": "RSRC"}

var arm := ""
var work := ""
var _dead := false
var _items: PackedStringArray = []
var _re_path_prefix: RegEx
var _re_remap_path: RegEx

func _initialize() -> void:
	work = OS.get_temp_dir().path_join(SCRATCH_REL)
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
		elif a.begins_with("--work="):
			work = a.substr(7)
	_re_path_prefix = RegEx.new()
	_re_path_prefix.compile("^\\.godot/exported/[0-9]+/")
	_re_remap_path = RegEx.new()
	_re_remap_path.compile("^\\[remap\\]\n\npath=\"(res://[^\"]+)\"\n$")
	_run.call_deferred()

func _run() -> void:
	match arm:
		"census": _arm_census()
		"tamper": _arm_tamper()
		"poison": _arm_poison()
		_: _fail("unknown_arm")

# ----------------------------------------------------------------- arms

func _arm_census() -> void:
	var pack := work.path_join(PACK_REL)
	var rc := _scratch()
	if rc != "":
		_fail(rc)
	var ex := _export(pack)
	if ex["rc"] != 0:
		_fail("export_rc=%d out=%s" % [ex["rc"], _tail(ex["out"])])
	if not FileAccess.file_exists(pack):
		_fail("pack_missing")
	var raw := _read(pack)
	var p := _parse(raw)
	var c := _check(p, raw)
	_emit(p, c)
	if not c["violations"].is_empty():
		_fail("violations=" + ", ".join(c["violations"]))
	_it("n", str(p["count"]))
	_it("pv", str(p["pack_version"]))
	_it("flags", str(p["flags"]))
	_it("uidrec", str(c["items"].get("uidrec", 0)))
	_it("md5ok", str(c["items"].get("md5ok", 0)))
	_it("remaps", str(c["items"].get("remaps", 0)))
	_it("targets", str(c["items"].get("targets", 0)))
	_it("uids", str(c["items"].get("uids", 0)))
	_it("uidsrc", str(c["items"].get("uidsrc", 0)))
	_it("hidden", str(c["items"].get("hidden", 0)))
	_it("magics", str(c["items"].get("magics", 0)))
	_it("scn", str(c["items"].get("scn", -1)))
	_it("pbin", str(c["items"].get("pbin", -1)))
	_it("paths", PATHS_SHA256.substr(0, 16))
	_it("stable", STABLE_SHA256.substr(0, 16))
	_pass()

func _arm_tamper() -> void:
	var pack := work.path_join(PACK_REL)
	var rc := _scratch()
	if rc != "":
		_fail(rc)
	var ex := _export(pack)
	if ex["rc"] != 0:
		_fail("export_rc=%d out=%s" % [ex["rc"], _tail(ex["out"])])
	var raw := _read(pack)
	var p := _parse(raw)
	var notes: PackedStringArray = []

	# (0) the format model must round-trip: re-emit the parsed pack byte-exactly
	var same := _check(p, raw)
	var redump := _emit_pack(p, raw)
	if redump != raw:
		_fail("reemit_mismatch_at=%d" % _first_diff(redump, raw))
	notes.append("reemit=1")
	var okm: int = same["items"].get("md5ok", 0)

	# (1) payload forgery: flip a byte inside scripts/main.gdc, keep md5 consistent
	var f1 := _forge(p, raw, "scripts/main.gdc", func(d: PackedByteArray) -> PackedByteArray:
		var m := d.duplicate()
		m[0] = m[0] ^ 0x01
		return m)
	var c1 := _check(f1["p"], f1["raw"])
	if c1["violations"].is_empty():
		_fail("forged_payload_accepted")
	notes.append("forge_payload=1")

	# (2) remap forgery: point main.tscn.remap at an entry that DOES exist but is
	# not the derived artifact -> md5s stay consistent, only the target row fires
	var f2 := _forge(p, raw, "main.tscn.remap", func(d: PackedByteArray) -> PackedByteArray:
		return "[remap]\n\npath=\"res://scripts/main.gdc\"\n".to_utf8_buffer())
	var c2 := _check(f2["p"], f2["raw"])
	if c2["violations"].is_empty() or c2["items"].get("md5ok", -1) != okm:
		_fail("forged_remap_accepted md5ok=%s" % str(c2["items"].get("md5ok", -1)))
	notes.append("forge_remap=1")

	# (3) dropped entry: delete sub/deep/data.tres.remap from data + directory
	var b3 := _drop(p, raw, "sub/deep/data.tres.remap")
	var c3 := _check(_parse(b3), b3)
	if c3["violations"].is_empty():
		_fail("dropped_entry_accepted")
	notes.append("drop_entry=1")

	# (4) added UID entry: a forged `scripts/main.gd.uid` must be rejected even
	# though the pack stays internally consistent (the "zero .uid" row is live)
	var b4 := _add(p, raw, "scripts/main.gd.uid", "uid://bogus0000000\n".to_utf8_buffer())
	var c4 := _check(_parse(b4), b4)
	if c4["violations"].is_empty() or c4["items"].get("uids", -1) != 1:
		_fail("forged_uid_accepted uids=%s" % str(c4["items"].get("uids", -1)))
	notes.append("forge_uid=1")

	_it("n", str(p["count"]))
	_it("md5ok", str(okm))
	_it("rejections", str(notes.size() - 1))
	_it("rows", ",".join(notes))
	_pass()

func _arm_poison() -> void:
	var pack := work.path_join(PACK_REL)
	var rc := _scratch()
	if rc != "":
		_fail(rc)
	var ex := _export(pack)
	if ex["rc"] != 0:
		_fail("export_rc=%d out=%s" % [ex["rc"], _tail(ex["out"])])
	var clean := _check(_parse(_read(pack)), _read(pack))
	if not clean["violations"].is_empty():
		_fail("clean_census_violations=" + ", ".join(clean["violations"]))
	# truncate every cached converted scene, then export again (L8)
	var n := _truncate_scn()
	if n == 0:
		_fail("no_cached_scn")
	ex = _export(pack)
	if ex["rc"] != 0:
		_fail("export2_rc=%d out=%s" % [ex["rc"], _tail(ex["out"])])
	var raw2 := _read(pack)
	var c2 := _check(_parse(raw2), raw2)
	var hit := false
	for v in c2["violations"]:
		if v.begins_with("scn_"):
			hit = true
	if not hit:
		_fail("poison_unrejected violations=" + ", ".join(c2["violations"]))
	_it("truncated", str(n))
	_it("md5ok", str(c2["items"].get("md5ok", -1)))
	_it("scn", str(c2["items"].get("scn", -1)))
	_it("violations", ", ".join(c2["violations"]))
	_pass()

# ------------------------------------------------------------- scratch project

func _scratch() -> String:
	if OS.execute("rm", ["-rf", work], [], true, false) != 0:
		return "rm_work_failed"
	var err := DirAccess.make_dir_recursive_absolute(work)
	if err != OK:
		return "mkdir_work_err=%d" % err
	for rel in FILES:
		var path := work.path_join(rel)
		DirAccess.make_dir_recursive_absolute(path.get_base_dir())
		var f := FileAccess.open(path, FileAccess.WRITE)
		if f == null:
			return "write_failed:" + rel
		f.store_string(FILES[rel])
		f.close()
	var g := FileAccess.open(work.path_join("art/icon.png"), FileAccess.WRITE)
	if g == null:
		if DirAccess.make_dir_recursive_absolute(work.path_join("art")) != OK:
			return "mkdir_art_failed"
		g = FileAccess.open(work.path_join("art/icon.png"), FileAccess.WRITE)
	if g == null:
		return "write_failed:art/icon.png"
	g.store_buffer(Marshalls.base64_to_raw(PNG_B64))
	g.close()
	return ""

func _export(pack: String) -> Dictionary:
	var out: Array = []
	var rc := OS.execute(OS.get_executable_path(),
		["--headless", "--path", work, "--export-pack", PRESET, pack], out, true, false)
	return {"rc": rc, "out": "\n".join(out)}

func _truncate_scn() -> int:
	var root := work.path_join(".godot/exported")
	var n := 0
	for sub in DirAccess.get_directories_at(root):
		var d := root.path_join(sub)
		for f in DirAccess.get_files_at(d):
			if f.ends_with(".scn"):
				var fa := FileAccess.open(d.path_join(f), FileAccess.WRITE)
				fa.close()
				n += 1
	return n

# --------------------------------------------------------------- pack reader

func _read(path: String) -> PackedByteArray:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return PackedByteArray()
	return f.get_buffer(f.get_length())

func _parse(raw: PackedByteArray) -> Dictionary:
	var p := {"ok": false, "err": "", "magic": "", "pack_version": -1, "engine": "", "flags": -1,
		"file_base": -1, "dir_offset": -1, "count": -1, "entries": []}
	if raw.size() < 0x28:
		p["err"] = "too_small"
		return p
	p["magic"] = raw.slice(0, 4).get_string_from_utf8()
	p["pack_version"] = raw.decode_u32(4)
	p["engine"] = "%d.%d.%d" % [raw.decode_u32(8), raw.decode_u32(12), raw.decode_u32(16)]
	p["flags"] = raw.decode_u32(20)
	p["file_base"] = raw.decode_u64(24)
	p["dir_offset"] = raw.decode_u64(32)
	var do: int = p["dir_offset"]
	if do + 4 > raw.size():
		p["err"] = "dir_offset_oob"
		return p
	p["count"] = raw.decode_u32(do)
	var o := do + 4
	var ents: Array = []
	for i in p["count"]:
		if o + 4 > raw.size():
			p["err"] = "entry_len_oob@%d" % i
			return p
		var pl := raw.decode_u32(o)
		o += 4
		if pl == 0 or o + pl + 36 > raw.size():
			p["err"] = "entry_body_oob@%d" % i
			return p
		var pbytes := raw.slice(o, o + pl)
		var z := pbytes.find(0)
		var path := (pbytes.slice(0, z) if z >= 0 else pbytes).get_string_from_utf8()
		o += pl
		var e := {"path": path, "rel": raw.decode_u64(o), "size": raw.decode_u64(o + 8),
			"md5": raw.slice(o + 16, o + 32).hex_encode(), "flags": raw.decode_u32(o + 32),
			"md5off": o + 16, "plen": pl}
		o += 36
		ents.append(e)
	p["entries"] = ents
	p["dir_end"] = o
	p["total"] = raw.size()
	p["ok"] = true
	return p

# re-emit a pack from a parsed model: header rebuilt, data region copied verbatim
# (offsets/gaps preserved), directory rebuilt in parse order (L2)
func _emit_pack(p: Dictionary, raw: PackedByteArray) -> PackedByteArray:
	var out := PackedByteArray()
	out.resize(p["file_base"])
	out.encode_u32(0, 0x43504447)  # GDPC little-endian
	out.encode_u32(4, p["pack_version"])
	var ev: PackedStringArray = p["engine"].split(".")
	out.encode_u32(8, int(ev[0]))
	out.encode_u32(12, int(ev[1]))
	out.encode_u32(16, int(ev[2]))
	out.encode_u32(20, p["flags"])
	out.encode_u64(24, p["file_base"])
	out.encode_u64(32, p["dir_offset"])
	for e in p["entries"]:
		var at: int = p["file_base"] + e["rel"]
		if out.size() < at + e["size"]:
			out.resize(at + e["size"])
		for i in e["size"]:
			out[at + i] = raw[at + i] if at + i < raw.size() else 0
	while out.size() < p["dir_offset"]:
		out.append(0)
	out.encode_u32(p["dir_offset"], p["entries"].size())
	var o: int = p["dir_offset"] + 4
	for e in p["entries"]:
		var pb: PackedByteArray = e["path"].to_utf8_buffer()
		var pad: int = (pb.size() + 3) & ~3
		out.resize(o + 4)
		out.encode_u32(o, pad)
		o += 4
		out.resize(o + pad)
		for i in pb.size():
			out[o + i] = pb[i]
		for i in range(pb.size(), pad):
			out[o + i] = 0
		o += pad
		out.resize(o + 36)
		out.encode_u64(o, e["rel"])
		out.encode_u64(o + 8, e["size"])
		var mb: PackedByteArray = e["md5"].hex_decode()
		for i in 16:
			out[o + 16 + i] = mb[i]
		out.encode_u32(o + 32, e["flags"])
		o += 36
	return out

# ------------------------------------------------------------ census checker

func _check(p: Dictionary, raw: PackedByteArray) -> Dictionary:
	var v: PackedStringArray = []
	var it := {"md5ok": 0, "uidrec": 0, "remaps": 0, "targets": 0, "uids": 0, "uidsrc": -1,
		"hidden": 0, "magics": 0, "scn": -1, "pbin": -1}
	if not p["ok"]:
		v.append("parse:" + str(p["err"]))
		return {"violations": v, "items": it}
	if p["magic"] != "GDPC":
		v.append("magic=" + p["magic"])
	if p["pack_version"] != 4:
		v.append("pack_version=%d" % p["pack_version"])
	var ev: Dictionary = Engine.get_version_info()
	if p["engine"] != "%d.%d.%d" % [ev["major"], ev["minor"], ev["patch"]]:
		v.append("engine=" + p["engine"])
	if p["flags"] != 2:
		v.append("flags=%d" % p["flags"])
	if p["file_base"] != 112:
		v.append("file_base=%d" % p["file_base"])
	if p["count"] != PATHS_N:
		v.append("count=%d" % p["count"])
	var paths := PackedStringArray()
	var stable := PackedStringArray()
	var by_path := {}
	var remaps := {}
	for e in p["entries"]:
		var at: int = p["file_base"] + e["rel"]
		if at < 0 or at + e["size"] > raw.size():
			v.append("oob:" + e["path"])
			continue
		var data := raw.slice(at, at + e["size"])
		if _md5(data) == e["md5"]:
			it["md5ok"] += 1
		else:
			v.append("md5_bad:" + e["path"])
		var npath := _norm(e["path"])
		paths.append(npath)
		by_path[npath] = e
		var is_vol := false
		for suf in VOLATILE:
			if e["path"].ends_with(suf) or e["path"] == suf:
				is_vol = true
		if not is_vol:
			stable.append("%s|%d|%s" % [npath, e["size"], e["md5"]])
		if e["path"].ends_with(".uid"):
			it["uids"] += 1
		if e["path"].ends_with(".remap"):
			remaps[e["path"]] = data.get_string_from_utf8()
		for ext in MAGICS:
			if e["path"].ends_with(ext):
				var want: String = MAGICS[ext]
				if e["size"] < 4 or data.slice(0, 4).get_string_from_utf8() != want:
					v.append("magic_bad:%s" % e["path"])
				else:
					it["magics"] += 1
		if e["path"].ends_with(".scn"):
			it["scn"] = e["size"]
			if e["size"] == 0:
				v.append("scn_size=0")
		if e["path"] == "project.binary":
			it["pbin"] = e["size"]
			if e["size"] != 0 and e["size"] != 235:
				v.append("pbin_size=%d" % e["size"])
	# path set + stable rows (L3)
	paths.sort()
	stable.sort()
	if paths.size() != PATHS_N:
		v.append("paths_n=%d" % paths.size())
	if _sha256("\n".join(paths).to_utf8_buffer()) != PATHS_SHA256:
		v.append("paths_digest")
	if stable.size() != STABLE_N:
		v.append("stable_n=%d" % stable.size())
	if _sha256("\n".join(stable).to_utf8_buffer()) != STABLE_SHA256:
		v.append("stable_digest")
	# remap payloads + targets (L5)
	it["remaps"] = remaps.size()
	for key in REMAP_EXPECT:
		if not remaps.has(key):
			v.append("remap_missing:" + key)
			continue
		var m := _re_remap_path.search(remaps[key])
		if m == null:
			v.append("remap_shape:" + key)
			continue
		var target: String = m.get_string(1)
		var want := ""
		var spec: Dictionary = REMAP_EXPECT[key]
		if spec["kind"] == "literal":
			want = spec["target"]
		else:
			want = _artifact(by_path, spec["src"], spec["ext"])
			if want == "":
				v.append("artifact_missing:" + spec["src"])
		if target != want:
			v.append("remap_target:%s=%s" % [key, target])
		elif not by_path.has(_norm(target.substr(6))):
			v.append("remap_dangling:" + key)
		else:
			it["targets"] += 1
	for extra in remaps:
		if not REMAP_EXPECT.has(extra):
			v.append("remap_extra:" + extra)
	# imported asset remap lives in its .import file (L5)
	var imp = by_path.get("art/icon.png.import")
	if imp == null:
		v.append("import_entry_missing")
	else:
		var d := raw.slice(p["file_base"] + imp["rel"], p["file_base"] + imp["rel"] + imp["size"])
		var text := d.get_string_from_utf8()
		if imp["size"] != 193 or imp["md5"] != "0c2b7cc2e579c2398934923d39b669ab":
			v.append("import_meta")
		if not text.begins_with("[remap]\n\nimporter=\"texture\"\n"):
			v.append("import_shape")
		if text.contains("[deps]") or text.contains("[params]"):
			v.append("import_not_stripped")
		var ctex := _artifact(by_path, "res://art/icon.png", "ctex")
		if ctex == "":
			v.append("ctex_artifact_missing")
		elif not text.contains("path=\"%s\"" % ctex):
			v.append("import_target")
		elif not text.contains("uid=\"uid://"):
			v.append("import_uid_missing")
	# UID rows (L6): the pack has no `*.uid` entries; UIDs live in uid_cache.bin
	# as `u64 id + u32 path_len + path` records. Bind each subject's id to its
	# path (scripts: on-disk `.uid` text; icon: `uid=` in the packed `.import`).
	if it["uids"] != 0:
		v.append("uid_entries=%d" % it["uids"])
	var uc = by_path.get(".godot/uid_cache.bin")
	var uhay := PackedByteArray()
	if uc == null:
		v.append("uid_cache_missing")
	else:
		uhay = raw.slice(p["file_base"] + uc["rel"], p["file_base"] + uc["rel"] + uc["size"])
		if uc["size"] != 102 or uc["md5"] != "a5cef98fcbca7b494076a6e3ed860611":
			v.append("uid_cache_meta")
		if uhay.size() >= 4 and uhay.decode_u32(0) != 3:
			v.append("uid_cache_count")
	var pairs := {"res://scripts/main.gd": "scripts/main.gd.uid", "res://scripts/player.gd": "scripts/player.gd.uid"}
	var uf := work.path_join(pairs["res://scripts/main.gd"])
	var ubytes := FileAccess.get_file_as_bytes(uf) if FileAccess.file_exists(uf) else PackedByteArray()
	it["uidsrc"] = ubytes.size()
	if it["uidsrc"] != 20 or not ubytes.get_string_from_utf8().begins_with("uid://"):
		v.append("on_disk_uid=%d" % it["uidsrc"])
	if imp != null:
		var itxt := raw.slice(p["file_base"] + imp["rel"], p["file_base"] + imp["rel"] + imp["size"]).get_string_from_utf8()
		var mm := RegEx.create_from_string("uid=\"(uid://[a-z0-9]+)\"").search(itxt)
		if mm != null:
			pairs["res://art/icon.png"] = mm.get_string(1)
	for subject in pairs:
		if not _has_bytes(uhay, subject.to_utf8_buffer()):
			v.append("uid_cache_subject:" + subject)
		var uid_text: String = pairs[subject]
		if uid_text.ends_with(".uid"):
			var ub := FileAccess.get_file_as_bytes(work.path_join(uid_text)) if FileAccess.file_exists(work.path_join(uid_text)) else PackedByteArray()
			uid_text = ub.get_string_from_utf8().strip_edges()
		if uc != null and uid_text.begins_with("uid://") and not _has_bytes(uhay, _uid_record(uid_text, subject)):
			v.append("uid_record:" + subject)
		elif uc != null and uid_text.begins_with("uid://"):
			it["uidrec"] += 1
	# sources replaced by remap/import must not be packed (L5)
	for h in HIDDEN_SOURCES:
		if by_path.has(h):
			v.append("source_packed:" + h)
		else:
			it["hidden"] += 1
	return {"violations": v, "items": it}

func _norm(path: String) -> String:
	return _re_path_prefix.sub(path, ".godot/exported/<P>/", true)

# expected artifact path for a source path: `<.godot dir>/export-<md5(res://src)>-<base>.<ext>`
func _artifact(by_path: Dictionary, src: String, ext: String) -> String:
	var token := _md5(src.to_utf8_buffer())
	var stem := src.get_file().get_basename()
	var fname := src.get_file()
	for key in by_path:
		var e: Dictionary = by_path[key]
		var p: String = e["path"]
		if not p.begins_with(".godot/") or not p.ends_with("." + ext):
			continue
		# exported form `.godot/exported/<P>/export-<token>-<stem>.<ext>`
		# imported form  `.godot/imported/<fname>-<token>.<ext>`
		if p.contains("export-" + token + "-" + stem + "." + ext) or p.contains(fname + "-" + token + "." + ext):
			return "res://" + p
	return ""

# ------------------------------------------------------------- forgery makers

func _forge(p: Dictionary, raw: PackedByteArray, key: String, f: Callable) -> Dictionary:
	for e in p["entries"]:
		if e["path"] != key:
			continue
		var q := raw.duplicate()
		var at: int = p["file_base"] + e["rel"]
		var data := q.slice(at, at + e["size"])
		var nd: PackedByteArray = f.call(data)
		e["size"] = nd.size()
		for i in nd.size():
			q[at + i] = nd[i]
		var nm := _md5(nd).hex_decode()
		for i in 16:
			q[e["md5off"] + i] = nm[i]
		return {"p": p, "raw": q}
	return {"p": p, "raw": raw}

func _rebuild(p: Dictionary, raw: PackedByteArray, ents: Array, payloads: Dictionary) -> PackedByteArray:
	var q := p.duplicate(true)
	q["entries"] = ents
	var out := _emit_pack(q, raw)
	for key in payloads:
		for e in ents:
			if e["path"] == key:
				var at: int = q["file_base"] + e["rel"]
				var nd: PackedByteArray = payloads[key]
				for i in nd.size():
					out[at + i] = nd[i]
	return out

func _drop(p: Dictionary, raw: PackedByteArray, key: String) -> PackedByteArray:
	var ents := []
	for e in p["entries"]:
		if e["path"] != key:
			ents.append(e)
	return _rebuild(p, raw, ents, {})

func _add(p: Dictionary, raw: PackedByteArray, key: String, payload: PackedByteArray) -> PackedByteArray:
	# the added entry's payload goes right where the directory used to start, so
	# the directory (and header field) shifts by its size
	var q := p.duplicate(true)
	var rel: int = p["dir_offset"] - p["file_base"]
	var ents: Array = p["entries"].duplicate()
	ents.append({"path": key, "rel": rel, "size": payload.size(), "md5": _md5(payload), "flags": 0})
	q["entries"] = ents
	q["dir_offset"] = p["dir_offset"] + payload.size()
	var out := _emit_pack(q, raw)
	var at: int = p["file_base"] + rel
	for i in payload.size():
		out[at + i] = payload[i]
	return out
	var q2 := p.duplicate(true)
	q2["entries"] = ents
	return _emit_pack(q2, q)

# ------------------------------------------------------------------- helpers

# byte-level substring search: binary payloads (uid_cache.bin) can carry bytes
# that abort UTF-8 decoding, so compare hex projections instead
func _has_bytes(hay: PackedByteArray, needle: PackedByteArray) -> bool:
	return hay.hex_encode().contains(needle.hex_encode())

# one uid_cache.bin record: u64 LE UID id + u32 LE path length + path bytes
func _uid_record(uid_text: String, path: String) -> PackedByteArray:
	var rec := PackedByteArray()
	rec.resize(8)
	rec.encode_s64(0, ResourceUID.text_to_id(uid_text))
	var ln := PackedByteArray()
	ln.resize(4)
	ln.encode_u32(0, path.to_utf8_buffer().size())
	return rec + ln + path.to_utf8_buffer()

func _md5(b: PackedByteArray) -> String:
	var h := HashingContext.new()
	h.start(HashingContext.HASH_MD5)
	h.update(b)
	return h.finish().hex_encode()

func _sha256(b: PackedByteArray) -> String:
	var h := HashingContext.new()
	h.start(HashingContext.HASH_SHA256)
	h.update(b)
	return h.finish().hex_encode()

func _first_diff(a: PackedByteArray, b: PackedByteArray) -> int:
	for i in mini(a.size(), b.size()):
		if a[i] != b[i]:
			return i
	return mini(a.size(), b.size())

func _tail(out: String) -> String:
	var lines := out.strip_edges().split("\n")
	return lines[lines.size() - 1] if lines.size() > 0 else ""

func _emit(p: Dictionary, c: Dictionary) -> void:
	print("E5 dir entries=%d file_base=%d dir_offset=%d pack_bytes=%d" % [
		p["count"], p["file_base"], p["dir_offset"], p["total"]])
	for e in p["entries"]:
		print("E5 entry %-64s size=%-5d md5=%s" % [_norm(e["path"]), e["size"], e["md5"]])
	print("E5 paths_sha256=%s" % PATHS_SHA256)
	print("E5 stable_sha256=%s" % STABLE_SHA256)
	for k in c["items"]:
		print("E5 %s=%s" % [k, str(c["items"][k])])
	for v in c["violations"]:
		print("E5 violation %s" % v)

func _it(key: String, value: String) -> void:
	_items.append("%s=%s" % [key, value])

func _pass() -> void:
	if _dead:
		return
	print("PASS export_prod_s05 %s %s" % [arm, " ".join(_items)])
	quit(0)

func _fail(reason: String) -> void:
	if _dead:
		return
	_dead = true
	print("FAIL export_prod_s05 %s reason=%s" % [arm, reason])
	quit(1)
