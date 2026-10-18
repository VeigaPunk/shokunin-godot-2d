extends SceneTree
# export_launch_s02 — r102 C1: embedded-PCK export launch receipt.
#
# Battery launch shape (one arm per process, 8s fixture bound):
#   godot --headless --path <scratch> --script res://export_launch_s02.gd -- --arm=embed
#
# Arms and the CASES rows that pin their PASS lines:
#   embed    -> export_launch_s02_embedded_quit_frames
#               (embed_pck=true release export; no .pck sibling; trailer proves the
#                pack is appended; boot from a dir holding only the binary with
#                --quit-after 5 yields the exact frame vector [1..5], extra=false)
#   contrast -> export_launch_s02_nonembed_contrast
#               (same project with embed_pck=false; sibling .pck present; binary
#                byte size == template size; boots with its .pck; run alone in a
#                dir without the .pck -> verbatim project-data-missing refusal,
#                observed as non-self-exiting, bounded by an external timeout)
#
# Evidence rule: nested Godot output is never echoed — every nested shell is
# redirected to <root>/<variant>/logs/*.log, and PASS lines carry only derived
# booleans, counts and the parsed frame vector. Operational failures print FAIL
# and exit 1 (the pinned signatures end at exit=0; trailing fields are
# diagnostics and are allowed to drift, they only follow the pinned text).
#
# Scratch policy: each arm builds under <root>/<variant>/{proj,out,logs}, where
# <root> is the first candidate of EXPORT_LAUNCH_ROOT, $TMPDIR/export_launch_s02,
# <engine user-data dir>/export_launch_s02 and /tmp/export_launch_s02 that
# passes a 4096-byte write+readback probe (same policy as export_prod.gd; /tmp
# measurably rejects multi-KB writes with EDQUOT on this host). Variant dirs are
# wiped at arm start so a stale sibling .pck can never fake the receipt.
#
# TMP isolation (measured 2026-10-18, r101 E0/E2): the 4.7.2 packer serializes
# project.binary through a FIXED /tmp/tmpproject.binary-<rand> path and swallows
# an EDQUOT write into a 0-byte project.binary; exports therefore run under
# `unshare -m --map-root-user sh -c 'mount -t tmpfs … /tmp; …'` when user
# namespaces are available (diagnosed as EXPORT_LAUNCH_DIAG userns=true|false).
#
# Measured 2026-10-18 on godot 4.7.2.stable.arch_linux.ed1daf0bf, host load ~8:
# embedded export ~1.7s, boot ~0.7s; template linux_release.x86_64 73519416 B,
# embedded binary 73521464 B = template + pack 2036 B + u64 pack size + "GDPC".

const PRESET := "Linux/X11"
const RELEASE_TEMPLATE := "linux_release.x86_64"
const MARKER := "LAUNCH_S02_MARKER"
const FRAME_PREFIX := "LAUNCH_S02_FRAME "
const MISSING_PCK_CLASS := "Couldn't load project data at path"
const MISSING_PCK_HINT := "Is the .pck file missing?"
const GDPC := 0x43504447
const EMBED_FRAMES := 5
const CONTRAST_FRAMES := 2
const MISSING_PCK_TIMEOUT := 2
const FIXTURE_ROOT_ENV := "EXPORT_LAUNCH_ROOT"
const TEMPLATE_ENV := "EXPORT_LAUNCH_TEMPLATE"

const MAIN_GD := "extends Node\n\nvar frames := 0\n\nfunc _ready() -> void:\n\tprint(\"LAUNCH_S02_MARKER boot=true\")\n\nfunc _process(_delta: float) -> void:\n\tframes += 1\n\tprint(\"LAUNCH_S02_FRAME %d\" % frames)\n"
const MAIN_TSCN := "[gd_scene load_steps=2 format=3]\n\n[ext_resource type=\"Script\" path=\"res://main.gd\" id=\"1\"]\n\n[node name=\"Main\" type=\"Node\"]\nscript = ExtResource(\"1\")\n"

var arm := ""
var _items: PackedStringArray = []
var _root := ""
var _unshare := false


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")


func _run() -> void:
	if arm == "":
		arm = "embed"
	_root = _pick_root()
	_diag("root", _root)
	if _root == "":
		_fail("no_writable_scratch_root")
		return
	_unshare = _probe_unshare()
	_diag("userns_tmp_isolation", _unshare)
	match arm:
		"embed":
			_arm_embed()
		"contrast":
			_arm_contrast()
		_:
			_fail("unknown_arm")


# ------------------------------------------------------------------ receipts

func _fail(reason: String) -> void:
	print("FAIL export_launch s02 arm=%s reason=%s" % [arm, reason])
	quit(1)


func _fail_fields(reason: String) -> void:
	print("FAIL export_launch s02 arm=%s reason=%s %s" % [arm, reason, " ".join(_items)])
	quit(1)


func _ok() -> void:
	print("PASS export_launch s02 arm=%s %s" % [arm, " ".join(_items)])
	quit(0)


func _it(key: String, value) -> void:
	_items.append("%s=%s" % [key, str(value)])


func _diag(key: String, value) -> void:
	print("EXPORT_LAUNCH_DIAG %s %s=%s" % [arm, key, str(value)])


# ------------------------------------------------------------------- scratch

func _pick_root() -> String:
	var candidates: PackedStringArray = []
	if OS.get_environment(FIXTURE_ROOT_ENV) != "":
		candidates.append(OS.get_environment(FIXTURE_ROOT_ENV))
	if OS.get_environment("TMPDIR") != "":
		candidates.append(OS.get_environment("TMPDIR").path_join("export_launch_s02"))
	# User-data dir before /tmp: /tmp intermittently rejects even multi-KB
	# writes with EDQUOT on this host, which kills pack output.
	candidates.append(OS.get_user_data_dir().path_join("export_launch_s02"))
	candidates.append("/tmp/export_launch_s02")
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


func _variant_dir(variant: String) -> String:
	return _root.path_join(variant)


func _proj_dir(variant: String) -> String:
	return _variant_dir(variant).path_join("proj")


func _out_dir(variant: String) -> String:
	return _variant_dir(variant).path_join("out")


func _log_path(variant: String, name: String) -> String:
	return _variant_dir(variant).path_join("logs").path_join(name + ".log")


func _mkdir(path: String) -> bool:
	if DirAccess.dir_exists_absolute(path):
		return true
	var err := DirAccess.make_dir_recursive_absolute(path)
	if err != OK:
		_fail("mkdir_failed:%s:%d" % [path, err])
		return false
	return true


func _rm_rf(path: String) -> void:
	if not DirAccess.dir_exists_absolute(path):
		return
	var d := DirAccess.open(path)
	if d == null:
		return
	for f in d.get_files():
		DirAccess.remove_absolute(path.path_join(f))
	for sub in d.get_directories():
		_rm_rf(path.path_join(sub))
	DirAccess.remove_absolute(path)


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


func _read_at(path: String, offset: int, count: int) -> PackedByteArray:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null or offset < 0 or offset + count > f.get_length():
		if f != null:
			f.close()
		return PackedByteArray()
	f.seek(offset)
	var buf := f.get_buffer(count)
	f.close()
	return buf


func _read_tail(path: String, count: int) -> PackedByteArray:
	var size := _file_size(path)
	if size < count:
		return PackedByteArray()
	return _read_at(path, size - count, count)


func _run_logged(body: String, log_path: String, isolate := false) -> int:
	_mkdir(log_path.get_base_dir())
	var script := body
	if isolate and _unshare:
		# Private /tmp for the packer's fixed tmpproject.binary temp path.
		script = "mount -t tmpfs -o size=64M tmpfs /tmp || exit 97\n" + body
		script = "unshare -m --map-root-user /usr/bin/sh -c " + _q(script)
	return OS.execute("/usr/bin/sh", PackedStringArray(["-c", "exec > " + _q(log_path) + " 2>&1\n" + script]))


# ------------------------------------------------------------------ projects

func _preset_cfg(embed: bool) -> String:
	return "[preset.0]\nname=\"Linux/X11\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\ninclude_filter=\"\"\nexclude_filter=\"\"\nexport_path=\"\"\n\n[preset.0.options]\nbinary_format/architecture=\"x86_64\"\nbinary_format/embed_pck=%s\n" % ("true" if embed else "false")


func _build_project(variant: String, embed: bool) -> String:
	var proj := _proj_dir(variant)
	_mkdir(proj)
	_mkdir(_out_dir(variant))
	_write_text(proj.path_join("project.godot"), "config_version=5\n\n[application]\nconfig/name=\"LaunchS02\"\nrun/main_scene=\"res://main.tscn\"\nconfig/features=PackedStringArray(\"4.7\")\n\n[display]\nwindow/size/viewport_width=320\nwindow/size/viewport_height=180\n")
	_write_text(proj.path_join("export_presets.cfg"), _preset_cfg(embed))
	_write_text(proj.path_join("main.gd"), MAIN_GD)
	_write_text(proj.path_join("main.tscn"), MAIN_TSCN)
	return proj


func _template_path() -> String:
	var override := OS.get_environment(TEMPLATE_ENV)
	if override != "" and FileAccess.file_exists(override):
		return override
	var data_home := OS.get_environment("XDG_DATA_HOME")
	if data_home == "":
		var home := OS.get_environment("HOME")
		if home == "":
			return ""
		data_home = home.path_join(".local/share")
	var root := data_home.path_join("godot/export_templates")
	var v := Engine.get_version_info()
	var want := "%d.%d.%d.%s" % [v["major"], v["minor"], v["patch"], v["status"]]
	var dirs: PackedStringArray = []
	dirs.append(root.path_join(want))
	var d := DirAccess.open(root)
	if d != null:
		for sub in d.get_directories():
			dirs.append(root.path_join(sub))
	for dir in dirs:
		var bin := dir.path_join(RELEASE_TEMPLATE)
		if not FileAccess.file_exists(bin):
			continue
		if FileAccess.get_file_as_string(dir.path_join("version.txt")).strip_edges() == want:
			return bin
	return ""


func _export(variant: String, out_path: String) -> int:
	var proj := _proj_dir(variant)
	var body := "cd " + _q(proj) + "\n" + _q(_godot()) + " --headless --path " + _q(proj) + " --export-release " + _q(PRESET) + " " + _q(out_path)
	return _run_logged(body, _log_path(variant, "export"), true)


func _boot(exe: String, cwd: String, quit_after: int, timeout_secs: int, log_name: String, variant: String) -> Array:
	var log_path := _log_path(variant, log_name)
	var body := "cd " + _q(cwd) + "\n/usr/bin/timeout " + str(timeout_secs) + " " + _q(exe) + " --headless --quit-after " + str(quit_after)
	var code := _run_logged(body, log_path, false)
	return [code, FileAccess.get_file_as_string(log_path), log_path]


# ------------------------------------------------------------------ analysis

func _frames(text: String) -> PackedInt32Array:
	var out := PackedInt32Array()
	for line in text.split("\n"):
		if line.begins_with(FRAME_PREFIX):
			out.append(line.substr(FRAME_PREFIX.length()).strip_edges().to_int())
	return out


func _marker_lines(text: String) -> int:
	var n := 0
	for line in text.split("\n"):
		if line.begins_with(MARKER):
			n += 1
	return n


func _range(n: int) -> PackedInt32Array:
	var out := PackedInt32Array()
	for i in n:
		out.append(i + 1)
	return out


func _fmt_ints(values: PackedInt32Array) -> String:
	var parts := PackedStringArray()
	for v in values:
		parts.append(str(v))
	return "[%s]" % ",".join(parts)


func _has_pck(dir: String) -> bool:
	var d := DirAccess.open(dir)
	if d == null:
		return false
	for f in d.get_files():
		if f.ends_with(".pck"):
			return true
	return false


# ---------------------------------------------------------------------- arms

func _arm_embed() -> void:
	_rm_rf(_variant_dir("embed"))
	var proj := _build_project("embed", true)
	var out_dir := _out_dir("embed")
	var exe := out_dir.path_join("s02.x86_64")
	var template := _template_path()
	if template == "":
		_fail("template_binary_not_found")
		return
	_diag("template", template)
	var code := _export("embed", exe)
	if code != 0 or not FileAccess.file_exists(exe):
		_fail("export_exit:%d" % code)
		return
	var bin_bytes := _file_size(exe)
	var template_bytes := _file_size(template)
	var pck_sibling := _has_pck(out_dir)
	var tail := _read_tail(exe, 12)
	var trailer_gdpc := tail.size() == 12 and tail.decode_u32(8) == GDPC
	var pack_size := 0
	var trailer_size_consistent := false
	var pack_magic_at_start := false
	if trailer_gdpc:
		pack_size = tail.decode_u64(0)
		trailer_size_consistent = bin_bytes - 12 - pack_size == template_bytes
		var head := _read_at(exe, bin_bytes - 12 - pack_size, 4)
		pack_magic_at_start = head.size() == 4 and head.decode_u32(0) == GDPC
	var run := _boot(exe, out_dir, EMBED_FRAMES, 6, "run", "embed")
	var rc: int = run[0]
	var text: String = run[1]
	var frames := _frames(text)
	var extra := _fmt_ints(frames) != _fmt_ints(_range(EMBED_FRAMES))
	_it("embed", true)
	_it("pck_sibling", pck_sibling)
	_it("trailer_gdpc", trailer_gdpc)
	_it("trailer_size_consistent", trailer_size_consistent)
	_it("pack_magic_at_start", pack_magic_at_start)
	_it("bin_gt_template", bin_bytes > template_bytes)
	_it("quit_after", EMBED_FRAMES)
	_it("frames", _fmt_ints(frames))
	_it("extra", extra)
	_it("marker_lines", _marker_lines(text))
	_it("exit", rc)
	_it("bin_bytes", bin_bytes)
	_it("template_bytes", template_bytes)
	_it("pack_bytes", pack_size)
	_it("proj", proj)
	if rc != 0 or pck_sibling or not trailer_gdpc or not trailer_size_consistent or not pack_magic_at_start or extra or bin_bytes <= template_bytes:
		_fail_fields("receipt_mismatch")
		return
	_ok()


func _arm_contrast() -> void:
	_rm_rf(_variant_dir("contrast"))
	_build_project("contrast", false)
	var out_dir := _out_dir("contrast")
	var exe := out_dir.path_join("s02c.x86_64")
	var template := _template_path()
	if template == "":
		_fail("template_binary_not_found")
		return
	_diag("template", template)
	var code := _export("contrast", exe)
	if code != 0 or not FileAccess.file_exists(exe):
		_fail("export_exit:%d" % code)
		return
	var bin_bytes := _file_size(exe)
	var template_bytes := _file_size(template)
	var pck := exe.get_basename() + ".pck"
	var pck_sibling := FileAccess.file_exists(pck)
	var pck_bytes := _file_size(pck)
	var run := _boot(exe, out_dir, CONTRAST_FRAMES, 6, "run_with_pck", "contrast")
	var rc: int = run[0]
	var text: String = run[1]
	var frames := _frames(text)
	var extra := _fmt_ints(frames) != _fmt_ints(_range(CONTRAST_FRAMES))
	var alone := _variant_dir("contrast").path_join("alone")
	_mkdir(alone)
	var alone_exe := alone.path_join("s02c.x86_64")
	if DirAccess.copy_absolute(exe, alone_exe) != OK:
		_fail("copy_alone_failed")
		return
	# copy_absolute does not preserve the executable bit (measured: mode 0644).
	if OS.execute("/usr/bin/chmod", PackedStringArray(["+x", alone_exe])) != 0:
		_fail("chmod_alone_failed")
		return
	var bare := _boot(alone_exe, alone, CONTRAST_FRAMES, MISSING_PCK_TIMEOUT, "run_without_pck", "contrast")
	var bare_rc: int = bare[0]
	var bare_text: String = bare[1]
	var class_hit := bare_text.contains(MISSING_PCK_CLASS) and bare_text.contains(MISSING_PCK_HINT)
	var killed: bool = bare_rc == 124
	_it("embed", false)
	_it("pck_sibling", pck_sibling)
	_it("bin_eq_template", bin_bytes == template_bytes)
	_it("quit_after", CONTRAST_FRAMES)
	_it("frames", _fmt_ints(frames))
	_it("extra", extra)
	_it("marker_lines", _marker_lines(text))
	_it("exit", rc)
	_it("without_pck_class", "project_data_missing" if class_hit else "other")
	_it("without_pck_selfexit", not killed)
	_it("without_pck_killed", killed)
	_it("bin_bytes", bin_bytes)
	_it("template_bytes", template_bytes)
	_it("pck_bytes", pck_bytes)
	if rc != 0 or not pck_sibling or bin_bytes != template_bytes or extra or not class_hit or not killed:
		_fail_fields("receipt_mismatch")
		return
	_ok()
