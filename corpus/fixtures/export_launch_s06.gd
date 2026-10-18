extends SceneTree
# export_launch_s06 — r102 C1 patch-mode probe: does `--export-patch` / preset
# patch export work against an r101-style (bare, non-embedded) base pack?
# Actual behavior only; refusal classes verbatim in the fixture constants.
#
# Battery launch shape (one arm per process, 8s fixture bound):
#   godot --headless --path <fixture proj> --script res://export_launch_s06.gd -- --arm=<arm>
#
# Arms (the PASS lines each arm prints are the registerable rows):
#   base       -> s06_base, s06_base_det, s06_fallback
#   patch      -> s06_changed          (hub: writes out/base.pck + out/patch1.pck;
#                                       patch1 = main.gdc + payload delta only)
#   patch_det  -> s06_det              (adjacent: requires patch arm artifacts)
#   union      -> s06_union            (adjacent: requires patch arm artifacts)
#   nochange   -> s06_nochange
#   refusals   -> s06_refusal_missing, s06_refusal_novalue, s06_refusal_badpreset
#   preset     -> s06_preset           (equal_to_patch1 field needs patch arm)
#   delta      -> s06_delta            (writes out/dbase.pck + out/don.pck)
#   delta_rt   -> s06_delta_runtime    (adjacent: requires delta arm artifacts)
#   runtime    -> s06_runtime, s06_patch_alone
#                                      (adjacent: requires patch arm artifacts)
#   e2e_export -> s06_e2e_export       (writes e2e/out/game.x86_64 + game.pck + patch.pck)
#   e2e_run    -> s06_e2e_run          (adjacent: requires e2e_export artifacts)
#
# Adjacency means the arm reads another arm's artifacts from the same scratch
# root (r101 det_a -> det_b precedent). Every such arm FAILs with an explicit
# `..._artifacts_missing` reason when run without its producer.
#
# Measured 2026-10-18 on godot 4.7.2.stable.arch_linux.ed1daf0bf (host load ~7-9,
# /var/tmp/r102-E6 scratch): one nested --export-pack of this project ~1.8s,
# --export-patch ~1.5s, --export-release (73.5MB template binary) ~3s, nested
# --main-pack run ~0.4s. Every arm is capped at two nested exports (or two
# nested runs) so the worst case stays ~6s against the 8s battery bound.
#
# Scratch root policy mirrors export_prod.gd: EXPORT_LAUNCH_ROOT, then
# EXPORT_PROD_ROOT, $TMPDIR, the engine user-data dir, /tmp — first candidate
# passing a 4096-byte write+readback (this host's /tmp intermittently returns
# EDQUOT). Exports run under `unshare -m` with a private tmpfs /tmp when the
# user namespace is available: the 4.7.2 packer serializes project.binary
# through a fixed /tmp path (r101 E0), and under quota pressure that write
# fails silently and corrupts the pack while the export still exits 0.
#
# Evidence rule: nested Godot output is redirected to <root>/<variant>/logs/*.log
# and never echoed; PASS lines carry only derived booleans, counts, sizes and
# digests. No absolute paths appear in PASS lines.

const PRESET := "Linux/X11"
const BAD_PRESET := "No Such Preset"
const PRESET_ERR := "Invalid export preset name: No Such Preset."
const PATCH_LOAD_ERR := "Could not load patch pack with path"
const NO_CHANGES_ERR := "No files or changes to export."
const NO_VALUE_ERR := "Missing comma-separated list of patches after --patches, aborting."
const MARK_V1 := "E6_S06_MARK v1"
const MARK_V2 := "E6_S06_MARK v2"
const PAYLOAD_V1 := "payload-v1\n"
const PAYLOAD_V2 := "payload-v2\n"
const PAYLOAD_V3 := "payload-v3\n"
const BIG_LEN_V2 := 8648
const MAIN_TSCN := "[gd_scene load_steps=2 format=3]\n\n[ext_resource type=\"Script\" path=\"res://main.gd\" id=\"1\"]\n\n[node name=\"Main\" type=\"Node\"]\nscript = ExtResource(\"1\")\n"
const CHECK_GD := "extends SceneTree\n\nfunc _initialize() -> void:\n\tprint(\"E6_S06_CHK before=\", FileAccess.get_file_as_string(\"res://patch/payload.txt\").strip_edges())\n\tvar ok := ProjectSettings.load_resource_pack(OS.get_environment(\"E6_S06_PATCH\"), true)\n\tprint(\"E6_S06_CHK load=\", ok)\n\tprint(\"E6_S06_CHK after=\", FileAccess.get_file_as_string(\"res://patch/payload.txt\").strip_edges())\n\tquit(0)\n"
const CHECK_DELTA_GD := "extends SceneTree\n\nfunc _initialize() -> void:\n\tvar f := FileAccess.get_file_as_string(\"res://patch/big.txt\")\n\tprint(\"E6_S06_DCHK before_changed=\", f.contains(\"line 0060: CHANGED\"), \" len=\", f.length())\n\tvar ok := ProjectSettings.load_resource_pack(OS.get_environment(\"E6_S06_PATCH\"), true)\n\tvar g := FileAccess.get_file_as_string(\"res://patch/big.txt\")\n\tprint(\"E6_S06_DCHK load=\", ok, \" after_changed=\", g.contains(\"line 0060: CHANGED\"), \" after_len=\", g.length())\n\tquit(0)\n"
const PATCHBOOT_GD := "extends Node\n\nfunc _init() -> void:\n\tvar dir := OS.get_executable_path().get_base_dir()\n\tvar f := dir.path_join(\"patch.pck\")\n\tif FileAccess.file_exists(f):\n\t\tprint(\"E6_S06_LOAD patch.pck ok=\", ProjectSettings.load_resource_pack(f, true))\n"

var arm := ""
var _root := ""
var _unshare := false
var _godot_path := ""


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")


func _run() -> void:
	_root = _pick_root()
	_godot_path = _godot()
	_diag("root", _root)
	if _root == "":
		_fail("no_writable_scratch_root")
		return
	_unshare = _probe_unshare()
	_diag("userns_tmp_isolation", _unshare)
	match arm:
		"base":
			_arm_base()
		"patch":
			_arm_patch()
		"patch_det":
			_arm_patch_det()
		"union":
			_arm_union()
		"nochange":
			_arm_nochange()
		"refusals":
			_arm_refusals()
		"preset":
			_arm_preset()
		"delta":
			_arm_delta()
		"delta_rt":
			_arm_delta_rt()
		"runtime":
			_arm_runtime()
		"e2e_export":
			_arm_e2e_export()
		"e2e_run":
			_arm_e2e_run()
		_:
			_fail("unknown_arm")


# ------------------------------------------------------------------ receipts

func _fail(reason: String) -> void:
	print("FAIL export_launch s06 %s reason=%s" % [arm, reason])
	quit(1)


func _emit(kind: String, fields: PackedStringArray) -> void:
	print("PASS export_launch %s %s" % [kind, " ".join(fields)])


func _diag(key: String, value) -> void:
	print("EXPORT_LAUNCH_S06_DIAG %s %s=%s" % [arm, key, str(value)])


# ------------------------------------------------------------------- scratch

func _pick_root() -> String:
	var candidates: PackedStringArray = []
	for env_name in ["EXPORT_LAUNCH_ROOT", "EXPORT_PROD_ROOT"]:
		if OS.get_environment(env_name) != "":
			candidates.append(OS.get_environment(env_name).path_join("export_launch_s06"))
	if OS.get_environment("TMPDIR") != "":
		candidates.append(OS.get_environment("TMPDIR").path_join("export_launch_s06"))
	candidates.append(OS.get_user_data_dir().path_join("export_launch_s06"))
	candidates.append("/tmp/export_launch_s06")
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


func _variant_dir(variant: String) -> String:
	return _root.path_join(variant)


func _proj_dir(variant: String) -> String:
	return _variant_dir(variant).path_join("proj")


func _out_dir(variant: String) -> String:
	return _variant_dir(variant).path_join("out")


func _log_path(variant: String, tag: String) -> String:
	return _variant_dir(variant).path_join("logs").path_join(tag + ".log")


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


func _file_len(path: String) -> int:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return -1
	var n := f.get_length()
	f.close()
	return n


func _sha256_file(path: String) -> String:
	var ctx := HashingContext.new()
	if ctx.start(HashingContext.HASH_SHA256) != OK:
		return ""
	if ctx.update(FileAccess.get_file_as_bytes(path)) != OK:
		return ""
	return ctx.finish().hex_encode()


func _sha256_text(text: String) -> String:
	var ctx := HashingContext.new()
	if ctx.start(HashingContext.HASH_SHA256) != OK:
		return ""
	if ctx.update(text.to_utf8_buffer()) != OK:
		return ""
	return ctx.finish().hex_encode()


func _byte_diff_count(a: String, b: String) -> int:
	var ba := FileAccess.get_file_as_bytes(a)
	var bb := FileAccess.get_file_as_bytes(b)
	var n := absi(ba.size() - bb.size())
	var shared := mini(ba.size(), bb.size())
	for i in shared:
		if ba[i] != bb[i]:
			n += 1
	return n


func _run_logged(body: String, log_path: String, isolate := false) -> int:
	_mkdir(log_path.get_base_dir())
	var script := body
	if isolate and _unshare:
		script = "mount -t tmpfs -o size=64M tmpfs /tmp || exit 97\n" + body
		script = "unshare -m --map-root-user /usr/bin/sh -c " + _q(script)
	return OS.execute("/usr/bin/sh", PackedStringArray(["-c", "exec > " + _q(log_path) + " 2>&1\n" + script]))


# -------------------------------------------------------------- project build

func _main_gd(ver: String) -> String:
	return "extends Node\n\nfunc _ready() -> void:\n\tprint(\"E6_S06_MARK %s\")\n\tprint(\"E6_S06_PAYLOAD \", FileAccess.get_file_as_string(\"res://patch/payload.txt\").strip_edges())\n" % ver


func _big_txt(changed: bool) -> String:
	var lines := ""
	for i in 120:
		if changed and i == 60:
			lines += "line %04d: CHANGED %s\n" % [i, "x".repeat(60)]
		else:
			lines += "line %04d: %s\n" % [i, "x".repeat(60)]
	return lines


func _preset_cfg(extra_top := "", extra_opt := "") -> String:
	return "[preset.0]\nname=\"Linux/X11\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\ninclude_filter=\"patch/*\"\nexclude_filter=\"\"\nexport_path=\"\"\n" + extra_top + "\n[preset.0.options]\nbinary_format/architecture=\"x86_64\"\n" + extra_opt


func _build(variant: String, opts := {}) -> String:
	var proj := _proj_dir(variant)
	_mkdir(proj.path_join("patch"))
	_mkdir(_out_dir(variant))
	var extra_opt := ""
	if bool(opts.get("embed_pck_false", false)):
		extra_opt = "binary_format/embed_pck=false\n"
	_write_text(proj.path_join("export_presets.cfg"), _preset_cfg("", extra_opt))
	var autoload := ""
	if bool(opts.get("autoload", false)):
		autoload = "\n[autoload]\npatchboot=\"*res://patchboot.gd\"\n"
	_write_text(proj.path_join("project.godot"), "config_version=5\n\n[application]\nconfig/name=\"E6S06\"\nrun/main_scene=\"res://main.tscn\"\nconfig/features=PackedStringArray(\"4.7\")\n" + autoload + "\n[display]\nwindow/size/viewport_width=320\nwindow/size/viewport_height=180\n")
	_write_text(proj.path_join("main.gd"), _main_gd("v1"))
	_write_text(proj.path_join("main.tscn"), MAIN_TSCN)
	_write_text(proj.path_join("patch/payload.txt"), PAYLOAD_V1)
	# check.gd rides in every base pack so the runtime/delta arms can reuse the
	# patch/delta arm's artifacts instead of paying their own export.
	_write_text(proj.path_join("check.gd"), CHECK_GD)
	if bool(opts.get("check_delta", false)):
		_write_text(proj.path_join("check_delta.gd"), CHECK_DELTA_GD)
		_write_text(proj.path_join("patch/big.txt"), _big_txt(false))
	if bool(opts.get("patchboot", false)):
		_write_text(proj.path_join("patchboot.gd"), PATCHBOOT_GD)
	return proj


func _mutate_v2(proj: String) -> void:
	_write_text(proj.path_join("main.gd"), _main_gd("v2"))
	_write_text(proj.path_join("patch/payload.txt"), PAYLOAD_V2)


func _mutate_payload_v3(proj: String) -> void:
	_write_text(proj.path_join("patch/payload.txt"), PAYLOAD_V3)


func _mutate_big_v2(proj: String) -> void:
	_write_text(proj.path_join("patch/big.txt"), _big_txt(true))


# ---------------------------------------------------------------- invocations

func _run_export_raw(variant: String, args: String, tag: String) -> int:
	var proj := _proj_dir(variant)
	var body := "cd " + _q(proj) + "\n" + _q(_godot_path) + " --headless --path " + _q(proj) + " " + args
	return _run_logged(body, _log_path(variant, tag), true)


func _export(variant: String, mode: String, out_path: String, tag: String, extra := "") -> int:
	var args := "--export-" + mode + " " + _q(PRESET) + " " + _q(out_path)
	if extra != "":
		args += " " + extra
	return _run_export_raw(variant, args, tag)


func _run_pack(variant: String, tag: String, args: String, env_prefix := "") -> int:
	var body := "cd /\n" + env_prefix + _q(_godot_path) + " " + args
	return _run_logged(body, _log_path(variant, tag))


func _run_exe(variant: String, tag: String, exe: String, args: String) -> int:
	var body := "cd /\n" + _q(exe) + " " + args
	return _run_logged(body, _log_path(variant, tag))


func _log_text(variant: String, tag: String) -> String:
	return FileAccess.get_file_as_string(_log_path(variant, tag))


# ------------------------------------------------------------------- censuses

func _census_pck(path: String) -> Dictionary:
	var bytes := FileAccess.get_file_as_bytes(path)
	if bytes.size() < 0x28 or bytes.decode_u32(0) != 0x43504447:
		return {}
	var base := bytes.decode_u64(0x18)
	var dir_off := bytes.decode_u64(0x20)
	var flags := bytes.decode_u32(0x14)
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
		var eflags := bytes.decode_u32(off + 32)
		off += 36
		if base + foff + size > bytes.size():
			return {}
		entries[name] = {"size": size, "offset": foff, "flags": eflags}
	return {"magic": "GDPC", "count": count, "flags": flags, "file_base": base, "dir_offset": dir_off, "entries": entries}


func _census_or_fail(path: String, what: String) -> Dictionary:
	var census := _census_pck(path)
	if census.is_empty():
		_fail(what + "_pck_parse_failed")
	return census


func _entry_size(entries: Dictionary, name: String) -> int:
	if not entries.has(name):
		return -1
	return int(entries[name].get("size", -1))


func _entry_flags(entries: Dictionary, name: String) -> int:
	if not entries.has(name):
		return -1
	return int(entries[name].get("flags", -1))


func _names_digest(entries: Dictionary) -> String:
	var names := PackedStringArray(entries.keys())
	names.sort()
	return _sha256_text("\n".join(names))


# ---------------------------------------------------------------------- arms

func _arm_base() -> void:
	var proj := _build("base")
	var out := _out_dir("base")
	var b1 := out.path_join("base1.pck")
	var fb := out.path_join("fallback.pck")
	if _export("base", "pack", b1, "e_base1") != 0 or not FileAccess.file_exists(b1):
		_fail("base1_export_failed")
		return
	# --export-patch with no --patches exports a full pack (no refusal).
	if _export("base", "patch", fb, "e_fallback") != 0 or not FileAccess.file_exists(fb):
		_fail("fallback_export_failed")
		return
	var census := _census_or_fail(fb, "base")
	if census.is_empty():
		return
	var entries: Dictionary = census["entries"]
	var f := PackedStringArray()
	f.append("magic=%s" % census["magic"])
	f.append("count=%d" % census["count"])
	f.append("flags=%d" % census["flags"])
	f.append("pbin_size=%d" % _entry_size(entries, "project.binary"))
	f.append("payload_size=%d" % _entry_size(entries, "patch/payload.txt"))
	f.append("names_sha256=%s" % _names_digest(entries))
	f.append("bytes=%d" % _file_size(fb))
	_emit("s06_base", f)
	var d := PackedStringArray()
	d.append("equal=%s" % (_sha256_file(b1) == _sha256_file(fb)))
	d.append("diff=%d" % _byte_diff_count(b1, fb))
	d.append("samples=2")
	d.append("modes=pack+patch_nopatches")
	d.append("bytes=%d" % _file_size(fb))
	_emit("s06_base_det", d)
	var fbf := PackedStringArray()
	fbf.append("exit=0")
	fbf.append("count=%d" % census["count"])
	fbf.append("equal_to_base=true")
	_emit("s06_fallback", fbf)
	_diag("proj", proj)
	quit(0)


func _arm_patch() -> void:
	var proj := _build("patch")
	var out := _out_dir("patch")
	var base := out.path_join("base.pck")
	var p1 := out.path_join("patch1.pck")
	if _export("patch", "pack", base, "e_base") != 0 or not FileAccess.file_exists(base):
		_fail("base_export_failed")
		return
	_mutate_v2(proj)
	var code := _export("patch", "patch", p1, "e_patch1", "--patches " + _q(base))
	if code != 0 or not FileAccess.file_exists(p1):
		_fail("patch_export_failed:%d" % code)
		return
	var census := _census_or_fail(p1, "patch")
	if census.is_empty():
		return
	var entries: Dictionary = census["entries"]
	var f := PackedStringArray()
	f.append("count=%d" % census["count"])
	f.append("main_gdc=%s" % entries.has("main.gdc"))
	f.append("payload=%s" % entries.has("patch/payload.txt"))
	f.append("pbin=%s" % entries.has("project.binary"))
	f.append("cache=%s" % entries.has(".godot/global_script_class_cache.cfg"))
	f.append("bytes=%d" % _file_size(p1))
	_emit("s06_changed", f)
	quit(0)


func _arm_patch_det() -> void:
	var proj := _build("patch")
	var out := _out_dir("patch")
	var base := out.path_join("base.pck")
	var p1 := out.path_join("patch1.pck")
	var p2 := out.path_join("patch2.pck")
	if not (FileAccess.file_exists(base) and FileAccess.file_exists(p1)):
		_fail("patch_arm_artifacts_missing")
		return
	_mutate_v2(proj)
	var code := _export("patch", "patch", p2, "e_patch2", "--patches " + _q(base))
	if code != 0 or not FileAccess.file_exists(p2):
		_fail("patch2_export_failed:%d" % code)
		return
	var d := PackedStringArray()
	d.append("equal=%s" % (_sha256_file(p1) == _sha256_file(p2)))
	d.append("diff=%d" % _byte_diff_count(p1, p2))
	d.append("samples=2")
	d.append("bytes=%d" % _file_size(p2))
	_emit("s06_det", d)
	quit(0)


func _arm_union() -> void:
	var proj := _build("union")
	var out := _out_dir("union")
	var own_base := out.path_join("base.pck")
	var p2 := out.path_join("p2.pck")
	var p1 := _out_dir("patch").path_join("patch1.pck")
	if not FileAccess.file_exists(p1):
		_fail("patch_arm_artifacts_missing")
		return
	if _export("union", "pack", own_base, "e_base") != 0 or not FileAccess.file_exists(own_base):
		_fail("base_export_failed")
		return
	_mutate_v2(proj)
	_mutate_payload_v3(proj)
	# p1 (hub) contains main.gdc v2 and payload v2; the source main.gdc is v2
	# too. With the own base listed first and p1 second, a first-pack-only
	# differ would re-store main.gdc (v2 != v1); union semantics skip it and
	# store only the still-different payload.
	var code := _export("union", "patch", p2, "e_p2", "--patches " + _q(own_base + "," + p1))
	if code != 0 or not FileAccess.file_exists(p2):
		_fail("p2_export_failed:%d" % code)
		return
	var census := _census_or_fail(p2, "union")
	if census.is_empty():
		return
	var entries: Dictionary = census["entries"]
	var f := PackedStringArray()
	f.append("count=%d" % census["count"])
	f.append("only_payload=%s" % (census["count"] == 1 and entries.has("patch/payload.txt")))
	f.append("main_repacked=%s" % entries.has("main.gdc"))
	f.append("bytes=%d" % _file_size(p2))
	_emit("s06_union", f)
	quit(0)


func _arm_nochange() -> void:
	var proj := _build("nochange")
	var out := _out_dir("nochange")
	var base := out.path_join("base.pck")
	var nc := out.path_join("nc.pck")
	if _export("nochange", "pack", base, "e_base") != 0 or not FileAccess.file_exists(base):
		_fail("base_export_failed")
		return
	var code := _export("nochange", "patch", nc, "e_nc", "--patches " + _q(base))
	var log_text := _log_text("nochange", "e_nc")
	var census: Dictionary = _census_pck(nc) if FileAccess.file_exists(nc) else {}
	var f := PackedStringArray()
	f.append("exit=%d" % code)
	f.append("class=%s" % ("no_files_or_changes" if log_text.contains(NO_CHANGES_ERR) else "other"))
	f.append("stub_exists=%s" % FileAccess.file_exists(nc))
	f.append("stub_bytes=%d" % _file_size(nc))
	f.append("stub_files=%d" % (int(census.get("count", 0)) if not census.is_empty() else 0))
	_emit("s06_nochange", f)
	quit(0)


func _arm_refusals() -> void:
	_build("refusals")
	var out := _out_dir("refusals")
	var missing := out.path_join("missing.pck")
	var c1 := _export("refusals", "patch", out.path_join("r1.pck"), "e_missing", "--patches " + _q(missing))
	var t1 := _log_text("refusals", "e_missing")
	var f1 := PackedStringArray()
	f1.append("exit=%d" % c1)
	f1.append("class=%s" % ("could_not_load_patch_pack" if t1.contains(PATCH_LOAD_ERR) else "other"))
	f1.append("artifacts=%d" % (1 if FileAccess.file_exists(out.path_join("r1.pck")) else 0))
	f1.append("log_bytes=%d" % t1.length())
	_emit("s06_refusal_missing", f1)
	var c2 := _run_export_raw("refusals", "--export-patch " + _q(PRESET) + " " + _q(out.path_join("r2.pck")) + " --patches", "e_novalue")
	var t2 := _log_text("refusals", "e_novalue")
	var f2 := PackedStringArray()
	f2.append("exit=%d" % c2)
	f2.append("class=%s" % ("missing_patches_list" if t2.contains(NO_VALUE_ERR) else "other"))
	f2.append("log_bytes=%d" % t2.length())
	_emit("s06_refusal_novalue", f2)
	var c3 := _run_export_raw("refusals", "--patches " + _q(missing) + " --export-patch " + _q(BAD_PRESET) + " " + _q(out.path_join("r3.pck")), "e_badpreset")
	var t3 := _log_text("refusals", "e_badpreset")
	var f3 := PackedStringArray()
	f3.append("exit=%d" % c3)
	f3.append("class=%s" % ("invalid_export_preset_name" if t3.contains(PRESET_ERR) else "other"))
	f3.append("patch_load_reached=%s" % t3.contains(PATCH_LOAD_ERR))
	f3.append("artifacts=%d" % (1 if FileAccess.file_exists(out.path_join("r3.pck")) else 0))
	_emit("s06_refusal_badpreset", f3)
	quit(0)


func _arm_preset() -> void:
	var proj := _build("preset")
	var out := _out_dir("preset")
	var base := out.path_join("base.pck")
	var pre := out.path_join("preset.pck")
	if _export("preset", "pack", base, "e_base") != 0 or not FileAccess.file_exists(base):
		_fail("base_export_failed")
		return
	_mutate_v2(proj)
	# Preset-level base-pack list (the "Base Packs" section of the Patching tab).
	var cfg := _preset_cfg("patches=PackedStringArray(\"%s\")\n" % base, "")
	_write_text(proj.path_join("export_presets.cfg"), cfg)
	var code := _export("preset", "patch", pre, "e_preset")
	if code != 0 or not FileAccess.file_exists(pre):
		_fail("preset_patch_export_failed:%d" % code)
		return
	var census := _census_or_fail(pre, "preset")
	if census.is_empty():
		return
	var hub_p1 := _out_dir("patch").path_join("patch1.pck")
	var eq := "unknown"
	if FileAccess.file_exists(hub_p1):
		eq = str(_sha256_file(hub_p1) == _sha256_file(pre))
	var f := PackedStringArray()
	f.append("count=%d" % census["count"])
	f.append("mode_used_preset_packs=true")
	f.append("equal_to_patch1=%s" % eq)
	f.append("bytes=%d" % _file_size(pre))
	_emit("s06_preset", f)
	quit(0)


func _arm_delta() -> void:
	var proj := _build("delta", {"check_delta": true})
	var out := _out_dir("delta")
	var dbase := out.path_join("dbase.pck")
	var don := out.path_join("don.pck")
	if _export("delta", "pack", dbase, "e_dbase") != 0 or not FileAccess.file_exists(dbase):
		_fail("dbase_export_failed")
		return
	_mutate_big_v2(proj)
	_write_text(proj.path_join("export_presets.cfg"), _preset_cfg("patch_delta_encoding=true\n", ""))
	var code := _export("delta", "patch", don, "e_don", "--patches " + _q(dbase))
	if code != 0 or not FileAccess.file_exists(don):
		_fail("don_export_failed:%d" % code)
		return
	var cn := _census_or_fail(don, "delta_on")
	if cn.is_empty():
		return
	var en: Dictionary = cn["entries"]
	var sn := _entry_size(en, "patch/big.txt")
	var f := PackedStringArray()
	f.append("raw_size=%d" % _file_len(dbase.get_base_dir().get_base_dir().path_join("proj/patch/big.txt")))
	f.append("on_size=%d" % sn)
	f.append("on_flags=%d" % _entry_flags(en, "patch/big.txt"))
	f.append("on_smaller=%s" % (sn > 0 and _file_len(proj.path_join("patch/big.txt")) > sn))
	f.append("on_bytes=%d" % _file_size(don))
	_emit("s06_delta", f)
	quit(0)


func _arm_delta_rt() -> void:
	var out := _out_dir("delta")
	var dbase := out.path_join("dbase.pck")
	var don := out.path_join("don.pck")
	if not (FileAccess.file_exists(dbase) and FileAccess.file_exists(don)):
		_fail("delta_arm_artifacts_missing")
		return
	var code := _run_pack("delta", "r_delta", "--headless --main-pack " + _q(dbase) + " --script res://check_delta.gd", "E6_S06_PATCH=" + _q(don) + " ")
	var t := _log_text("delta", "r_delta")
	var f := PackedStringArray()
	f.append("exit=%d" % code)
	f.append("before_changed=%s" % t.contains("E6_S06_DCHK before_changed=true"))
	f.append("load=%s" % t.contains("load=true"))
	f.append("after_changed=%s" % t.contains("after_changed=true"))
	f.append("after_len_8648=%s" % t.contains("after_len=%d" % BIG_LEN_V2))
	_emit("s06_delta_runtime", f)
	quit(0)


func _arm_runtime() -> void:
	var hub := _out_dir("patch")
	var base := hub.path_join("base.pck")
	var patch := hub.path_join("patch1.pck")
	if not (FileAccess.file_exists(base) and FileAccess.file_exists(patch)):
		_fail("patch_arm_artifacts_missing")
		return
	var rc := _run_pack("runtime", "r_compose", "--headless --main-pack " + _q(base) + " --script res://check.gd", "E6_S06_PATCH=" + _q(patch) + " ")
	var tr := _log_text("runtime", "r_compose")
	var f := PackedStringArray()
	f.append("exit=%d" % rc)
	f.append("before=%s" % ("payload-v1" if tr.contains("before=payload-v1") else "other"))
	f.append("load=%s" % tr.contains("load=true"))
	f.append("after=%s" % ("payload-v2" if tr.contains("after=payload-v2") else "other"))
	_emit("s06_runtime", f)
	# A patch pack alone (no base, no project.binary) exits 0 and boots nothing.
	var ra := _run_pack("runtime", "r_alone", "--headless --main-pack " + _q(patch) + " --quit-after 2")
	var ta := _log_text("runtime", "r_alone")
	var fa := PackedStringArray()
	fa.append("exit=%d" % ra)
	fa.append("marker_absent=%s" % (not ta.contains("E6_S06_MARK")))
	fa.append("frames_absent=%s" % (not ta.contains("E6_S06_PAYLOAD")))
	_emit("s06_patch_alone", fa)
	quit(0)


func _arm_e2e_export() -> void:
	var proj := _build("e2e", {"embed_pck_false": true, "autoload": true, "patchboot": true})
	var out := _out_dir("e2e")
	var exe := out.path_join("game.x86_64")
	var pck := out.path_join("game.pck")
	var patch := out.path_join("patch.pck")
	var code := _run_export_raw("e2e", "--export-release " + _q(PRESET) + " " + _q(exe), "e_release")
	if code != 0 or not (FileAccess.file_exists(exe) and FileAccess.file_exists(pck)):
		_fail("release_export_failed:%d" % code)
		return
	_mutate_v2(proj)
	var pc := _export("e2e", "patch", patch, "e_patch", "--patches " + _q(pck))
	if pc != 0 or not FileAccess.file_exists(patch):
		_fail("patch_export_failed:%d" % pc)
		return
	var census := _census_or_fail(patch, "e2e")
	if census.is_empty():
		return
	var f := PackedStringArray()
	f.append("binary_bytes=%d" % _file_size(exe))
	f.append("base_pck_bytes=%d" % _file_size(pck))
	f.append("patch_bytes=%d" % _file_size(patch))
	f.append("patch_count=%d" % census["count"])
	_emit("s06_e2e_export", f)
	quit(0)


func _arm_e2e_run() -> void:
	var out := _out_dir("e2e")
	var exe := out.path_join("game.x86_64")
	var pck := out.path_join("game.pck")
	var patch := out.path_join("patch.pck")
	if not (FileAccess.file_exists(exe) and FileAccess.file_exists(pck) and FileAccess.file_exists(patch)):
		_fail("e2e_export_arm_artifacts_missing")
		return
	# Baseline run must not see the patch pack: hold it aside, then restore.
	var held := patch + ".hold"
	var hidden := false
	if FileAccess.file_exists(patch):
		hidden = DirAccess.rename_absolute(patch, held) == OK
	var r1 := _run_exe("e2e", "r_nopatch", exe, "--headless --quit-after 3")
	var t1 := _log_text("e2e", "r_nopatch")
	if hidden:
		DirAccess.rename_absolute(held, patch)
	var r2 := _run_exe("e2e", "r_patch", exe, "--headless --quit-after 3")
	var t2 := _log_text("e2e", "r_patch")
	var f := PackedStringArray()
	f.append("nopatch_exit=%d" % r1)
	f.append("patch_hidden=%s" % hidden)
	f.append("nopatch_mark=%s" % ("v1" if t1.contains(MARK_V1) else "other"))
	f.append("nopatch_payload=%s" % ("payload-v1" if t1.contains("E6_S06_PAYLOAD payload-v1") else "other"))
	f.append("patch_exit=%d" % r2)
	f.append("patch_mark=%s" % ("v2" if t2.contains(MARK_V2) else "other"))
	f.append("patch_payload=%s" % ("payload-v2" if t2.contains("E6_S06_PAYLOAD payload-v2") else "other"))
	f.append("load_ok=%s" % t2.contains("ok=true"))
	_emit("s06_e2e_run", f)
	quit(0)
