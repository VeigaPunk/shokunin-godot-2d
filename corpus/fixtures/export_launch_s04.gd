extends SceneTree
# export_launch_s04 — r102 E4: export include/exclude filter case-sensitivity probe
# (r102 C1 export-launch matrix). Probe-style: every emitted boolean is a
# measurement of the actual exported pack; no filter behavior is assumed.
#
# Battery launch shape (one process; measured ~5.0 s at host load 7-9):
#   godot --headless --path <fixtures proj> --script res://export_launch_s04.gd
# Optional flags after `--` (standalone probing only, not battery-pinned):
#   --arm=both|lower|upper_excl   (default both; single arms run one export cold)
#
# The fixture builds a scratch project whose `case/` dir holds an extension-case
# ladder plus controls:
#   one.txt  TWO.TXT  three.TxT   plain files, mixed-case extensions
#   other.dat                     plain file no token targets (selectivity control)
#   g_low.gd                      script resource (expect .remap + .gdc)
#   g_up.GD                       uppercase script-class extension
# Two exports, one PASS census line each:
#   A filter_lower      include=case/*.txt  exclude=none
#   B filter_upper_excl include=case/*.TXT  exclude=case/ONE.TXT,case/G_LOW.GD
# A-vs-B discriminators (measured, 2026-10-18): include token case and dir case
# are ignored (lowercase token pulled TWO.TXT/three.TxT; uppercase token pulled
# one.txt/three.TxT); exclude matches case-insensitively AND applies to resources
# (wrong-case case/G_LOW.GD token removes g_low.gd's compiled .remap/.gdc), while
# the untargeted raw case/g_up.GD survives; other_in stays false in both (the
# include filter is selective, not "include everything"). Exploratory receipt for
# the pure case question: tokens case/*.txt, case/*.TXT, case/*.TxT, CASE/*.txt and
# res://case/*.txt produced BYTE-IDENTICAL packs (same sha256) on the probe project.
#
# Scratch policy (r101 export_prod law): root = EXPORT_LAUNCH_S04_ROOT env →
# $TMPDIR/export_launch_s04 → <engine user-data dir>/export_launch_s04 →
# /tmp/export_launch_s04, first candidate passing a 4096-byte write+readback probe.
# Exports run under `unshare -m --map-root-user` with a private tmpfs /tmp when user
# namespaces are available: the 4.7.2 packer serializes project.binary through a
# fixed /tmp/tmpproject.binary-<rand> path ($TMPDIR is not honored) and under the
# host /tmp quota that write can silently produce a 0-byte project.binary with exit
# 0. pbin_size<=0 is therefore a FAIL (honest environment failure), never a pass.
# Nested godot output is redirected to scratch logs and never echoed; PASS lines
# carry only derived booleans, counts, digests and sizes.

const PRESET := "Linux/X11"
const INC_LOWER := "case/*.txt"
const INC_UPPER := "case/*.TXT"
const EXC_UPPER := "case/ONE.TXT,case/G_LOW.GD"
const PRESET_TMPL := "[preset.0]\nname=\"Linux/X11\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\ninclude_filter=\"@INC@\"\nexclude_filter=\"@EXC@\"\nexport_path=\"\"\n\n[preset.0.options]\nbinary_format/architecture=\"x86_64\"\n"
const PROJECT_GODOT := "config_version=5\n\n[application]\nconfig/name=\"ExportLaunchS04\"\nrun/main_scene=\"res://main.tscn\"\nconfig/features=PackedStringArray(\"4.7\")\n\n[display]\nwindow/size/viewport_width=320\nwindow/size/viewport_height=180\n"
const MAIN_GD := "extends Node\n\nfunc _ready() -> void:\n\tprint(\"EXPORT_LAUNCH_S04 main\")\n"
const MAIN_TSCN := "[gd_scene load_steps=2 format=3]\n\n[ext_resource type=\"Script\" path=\"res://main.gd\" id=\"1\"]\n\n[node name=\"Main\" type=\"Node\"]\nscript = ExtResource(\"1\")\n"
const G_LOW_GD := "extends Node\n\nfunc _ready() -> void:\n\tprint(\"g_low\")\n"
const G_UP_GD := "extends Node\n\nfunc _ready() -> void:\n\tprint(\"g_up\")\n"

var arm := "both"
var _failed := false
var _root := ""
var _proj := ""
var _out := ""
var _unshare := false


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")


func _run() -> void:
	_root = _pick_root()
	_diag("root", _root)
	if _root == "":
		_fail("no_writable_scratch_root")
		return
	_unshare = _probe_unshare()
	_diag("userns_tmp_isolation", _unshare)
	_proj = _root.path_join("launch_s04").path_join("proj")
	_out = _root.path_join("launch_s04").path_join("out")
	_build()
	if _failed:
		return
	match arm:
		"lower":
			_export_and_emit(INC_LOWER, "", "filter_lower")
		"upper_excl":
			_export_and_emit(INC_UPPER, EXC_UPPER, "filter_upper_excl")
		"both":
			_export_and_emit(INC_LOWER, "", "filter_lower")
			if _failed:
				return
			_export_and_emit(INC_UPPER, EXC_UPPER, "filter_upper_excl")
		_:
			_fail("unknown_arm")
			return
	if _failed:
		return
	quit(0)


# ------------------------------------------------------------------ receipts

func _fail(reason: String) -> void:
	print("FAIL export_launch_s04 %s reason=%s" % [arm, reason])
	_failed = true
	quit(1)


func _emit(kind: String, fields: PackedStringArray) -> void:
	print("PASS export_launch_s04 %s %s" % [kind, " ".join(fields)])


func _diag(key: String, value) -> void:
	print("EXPORT_S04_DIAG %s %s=%s" % [arm, key, str(value)])


# ------------------------------------------------------------------- scratch

func _pick_root() -> String:
	var candidates: PackedStringArray = []
	if OS.get_environment("EXPORT_LAUNCH_S04_ROOT") != "":
		candidates.append(OS.get_environment("EXPORT_LAUNCH_S04_ROOT"))
	if OS.get_environment("TMPDIR") != "":
		candidates.append(OS.get_environment("TMPDIR").path_join("export_launch_s04"))
	candidates.append(OS.get_user_data_dir().path_join("export_launch_s04"))
	candidates.append("/tmp/export_launch_s04")
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
	var cmd := "exec > /dev/null 2>&1\nunshare -m --map-root-user /usr/bin/sh -c 'mount -t tmpfs -o size=16M tmpfs /tmp && test -w /tmp'"
	return OS.execute("/usr/bin/sh", PackedStringArray(["-c", cmd])) == 0


func _godot() -> String:
	var exe := OS.get_executable_path()
	return exe if exe != "" else "/usr/bin/godot"


func _q(s: String) -> String:
	return "'" + s.replace("'", "'\\''") + "'"


func _run_logged(body: String, log_path: String, isolate := false) -> int:
	_mkdir(log_path.get_base_dir())
	var script := body
	if isolate and _unshare:
		# Private /tmp for the packer's fixed tmpproject.binary temp path.
		script = "mount -t tmpfs -o size=64M tmpfs /tmp || exit 97\n" + body
		script = "unshare -m --map-root-user /usr/bin/sh -c " + _q(script)
	_diag("nested", body.replace("\n", " ; "))
	return OS.execute("/usr/bin/sh", PackedStringArray(["-c", "exec > " + _q(log_path) + " 2>&1\n" + script]))


func _mkdir(path: String) -> bool:
	if DirAccess.dir_exists_absolute(path):
		return true
	var err := DirAccess.make_dir_recursive_absolute(path)
	if err != OK:
		_fail("mkdir_failed:%s:%d" % [path, err])
		return false
	return true


func _write_text(path: String, text: String) -> bool:
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		_fail("write_failed:" + path)
		return false
	f.store_string(text)
	f.close()
	return true


func _file_size(path: String) -> int:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return -1
	var size := f.get_length()
	f.close()
	return size


func _sha256_text(text: String) -> String:
	var ctx := HashingContext.new()
	if ctx.start(HashingContext.HASH_SHA256) != OK:
		return ""
	if ctx.update(text.to_utf8_buffer()) != OK:
		return ""
	return ctx.finish().hex_encode()


# ------------------------------------------------------------------ project

func _preset(inc: String, exc: String) -> String:
	return PRESET_TMPL.replace("@INC@", inc).replace("@EXC@", exc)


func _build() -> void:
	_mkdir(_proj.path_join("case"))
	_mkdir(_out)
	_write_text(_proj.path_join("project.godot"), PROJECT_GODOT)
	_write_text(_proj.path_join("main.gd"), MAIN_GD)
	_write_text(_proj.path_join("main.tscn"), MAIN_TSCN)
	_write_text(_proj.path_join("case/one.txt"), "alpha\n")
	_write_text(_proj.path_join("case/TWO.TXT"), "bravo\n")
	_write_text(_proj.path_join("case/three.TxT"), "charlie\n")
	_write_text(_proj.path_join("case/other.dat"), "delta\n")
	_write_text(_proj.path_join("case/g_low.gd"), G_LOW_GD)
	_write_text(_proj.path_join("case/g_up.GD"), G_UP_GD)
	_write_text(_proj.path_join("export_presets.cfg"), _preset(INC_LOWER, ""))


# --------------------------------------------------------------------- arms

func _export_and_emit(inc: String, exc: String, kind: String) -> void:
	_write_text(_proj.path_join("export_presets.cfg"), _preset(inc, exc))
	if _failed:
		return
	var pck := _out.path_join(kind + ".pck")
	var log_path := _root.path_join("launch_s04").path_join("logs").path_join(kind + ".log")
	var body := "cd " + _q(_proj) + "\n" + _q(_godot()) + " --headless --path " + _q(_proj) + " --export-pack " + _q(PRESET) + " " + _q(pck)
	var code := _run_logged(body, log_path, true)
	if code != 0 or not FileAccess.file_exists(pck):
		_fail("export_failed:%s:%d" % [kind, code])
		return
	var census := _census_pck(pck)
	if census.is_empty() or census["magic"] != "GDPC":
		_fail("pck_parse_failed:%s" % kind)
		return
	var entries: Dictionary = census["entries"]
	var pbin := _entry_size(entries, "project.binary")
	if pbin <= 0:
		_fail("pbin_zero:%s" % kind)
		return
	var fields := PackedStringArray()
	fields.append("include=%s" % inc)
	fields.append("exclude=%s" % (exc if exc != "" else "-"))
	fields.append("one_in=%s" % entries.has("case/one.txt"))
	fields.append("two_in=%s" % entries.has("case/TWO.TXT"))
	fields.append("three_in=%s" % entries.has("case/three.TxT"))
	fields.append("other_in=%s" % entries.has("case/other.dat"))
	fields.append("up_raw=%s" % entries.has("case/g_up.GD"))
	fields.append("up_remap=%s" % entries.has("case/g_up.GD.remap"))
	fields.append("up_gdc=%s" % entries.has("case/g_up.gdc"))
	fields.append("low_raw=%s" % entries.has("case/g_low.gd"))
	fields.append("low_remap=%s" % entries.has("case/g_low.gd.remap"))
	fields.append("low_gdc=%s" % entries.has("case/g_low.gdc"))
	fields.append("entry_count=%d" % int(census["count"]))
	fields.append("names_sha256=%s" % _names_digest(entries))
	fields.append("pbin_size=%d" % pbin)
	fields.append("bytes=%d" % _file_size(pck))
	_emit(kind, fields)


# ------------------------------------------------------------------- census

func _census_pck(path: String) -> Dictionary:
	var bytes := FileAccess.get_file_as_bytes(path)
	if bytes.size() < 0x28 or bytes.decode_u32(0) != 0x43504447:
		return {}
	var base := bytes.decode_u64(0x18)
	var dir_off := bytes.decode_u64(0x20)
	if dir_off + 4 > bytes.size():
		return {}
	var count := bytes.decode_u32(dir_off)
	var off := dir_off + 4
	var entries := {}
	for i in count:
		if off + 4 > bytes.size():
			return {}
		var plen := bytes.decode_u32(off)
		off += 4
		if off + plen + 36 > bytes.size():
			return {}
		var name_end := off
		while name_end < off + plen and bytes[name_end] != 0:
			name_end += 1
		var name := bytes.slice(off, name_end).get_string_from_utf8()
		off += plen
		off = ((off + 3) / 4) * 4
		var foff := bytes.decode_u64(off)
		var size := bytes.decode_u64(off + 8)
		var flags := bytes.decode_u32(off + 32)
		off += 36
		if base + foff + size > bytes.size():
			return {}
		entries[name] = {"size": size, "offset": foff, "flags": flags}
	return {"magic": "GDPC", "count": count, "file_base": base, "dir_offset": dir_off, "entries": entries}


func _entry_size(entries: Dictionary, name: String) -> int:
	if not entries.has(name):
		return -1
	return int(entries[name].get("size", -1))


func _names_digest(entries: Dictionary) -> String:
	var names := PackedStringArray(entries.keys())
	names.sort()
	return _sha256_text("\n".join(names))
