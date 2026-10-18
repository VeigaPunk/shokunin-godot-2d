extends SceneTree
# export_launch_s03 — r102 C1 launch-matrix row: the STOCK (non-embedded) export
# template binary refuses `--main-pack`, while the SAME pack runs when the same
# flag is passed to the editor build, and also runs on the same template binary
# when the pack is found at the automatic sibling path (no path override).
#
# Battery launch shape (one arm per process):
#   godot --headless --path <fixture proj> --script res://export_launch_s03.gd -- --arm=<arm>
#
# Arms and the CASES rows that pin their PASS lines:
#   refuse   -> export_launch_s03_mainpack_refusal
#               `<out>/s03.x86_64 --headless --quit-after 3 --main-pack <pck>`
#               rc=1, stdout empty, stderr carries the verbatim
#               "`--main-pack` was specified on the command line, but this Godot
#               binary was compiled without support for path overrides. Aborting."
#               plus the `disable_path_overrides=no` hint; a second run whose
#               --main-pack argument does not exist gives byte-identical stderr
#               (the abort precedes any pack access), and a valid sibling
#               `<out>/s03.pck` is present for both runs (r101-crit5 F7 wording:
#               state WHICH binary carries the flag — that binary is the stock
#               release template, not the editor).
#   contrast -> export_launch_s03_editor_mainpack_contrast
#               `godot --headless --main-pack <pck> --quit-after 3` from an
#               empty cwd: rc=0, stderr 0 bytes, boot marker + exactly 3 frames
#               => the same pack is loadable; --main-pack itself is not broken.
#   sibling  -> export_launch_s03_template_sibling_pack
#               `<out>/s03.x86_64 --headless --quit-after 3` with NO flag and
#               `<out>/s03.pck` adjacent: rc=0, stderr 0 bytes, same marker and
#               frames => the refusal is the path-override flag alone, not a
#               broken binary/pack.
#   all      -> runs the three arms above in one process (3 PASS lines).
#
# Evidence rule: nested Godot output is NEVER echoed. The harness classifier
# rejects any line containing `ERROR:` (`run_battery.py` classify_process), so
# each nested run is redirected to <root>/logs/*.out|*.err and the PASS lines
# carry only derived booleans, counts, sizes, digests and the refusal text
# aligned after its prefix — the literal `ERROR: ` prefix is emitted as
# prefix_hex=4552524f523a20. Unpinned-but-measured fields go to S03_DIAG lines.
#
# Scratch policy: root = EXPORT_LAUNCH_S03_ROOT, else
# <engine user data dir>/export_launch_s03/<sha1(project_dir)[0..11]>, else
# $TMPDIR/export_launch_s03/<hash>, else /tmp/export_launch_s03/<hash>; the
# first candidate passing a 4096-byte write+readback probe wins. The per-project
# hash keeps one run's artifacts (and the sibling-pack control) isolated from
# every other run while letting the three arms of one row family share them.
# The engine user-data dir is preferred over /tmp because this host's /tmp
# intermittently rejects even multi-KB writes with EDQUOT (r101 E0 F1/F3).
#
# Staging (measured 2026-10-18, godot 4.7.2.stable.arch_linux.ed1daf0bf):
#   * `--export-pack "Linux/X11"` and `--export-release "Linux/X11"` produced a
#     BYTE-IDENTICAL pack for the same project (sha256 9226340359c916a2…,
#     1944 B, 7 entries, project.binary 172 B "ECFG").
#   * the binary `--export-release` writes is a byte copy of
#     ~/.local/share/godot/export_templates/4.7.2.stable/linux_release.x86_64
#     (sha256 d9f79ab89b5ae369… for both; same finding in r101-crit5 F7), so the
#     fixture exports the cheap pack and stages the template binary itself with
#     `cp -l` (hardlink when scratch and the templates share a device) and a
#     `cp` fallback whose sha is verified against the template.
#   * the /tmp EDQUOT window can make the packer store a 0-byte project.binary
#     while the export still exits 0 (r101 E0 F1); the pack is therefore parsed
#     in-fixture and a structurally broken pack is re-exported once inside
#     `unshare -m --map-root-user` with a private /tmp when user namespaces work.
#
# Measured receipts (this host, 3/3 byte-identical reps per arm; load ~7-9):
#   refuse  : rc=1 in 33 ms, stdout 0 B, stderr 265 B sha256 785a6ba9162e8c9d…,
#             lines: refusal 136 B / hint 92 B / "" / "   at: setup (main/main.cpp:1892)"
#   contrast: rc=0 in 870 ms, stdout 185 B (banner 4.7.2.stable.arch_linux.*)
#   sibling : rc=0 in 815 ms, stdout 157 B (banner 4.7.2.stable.official.*)
#   export  : --export-pack 1912-1974 ms on this minimal project.

const PRESET := "Linux/X11"
const TEMPLATE_BIN := "linux_release.x86_64"
const EXPORT_BIN := "s03.x86_64"
const EXPORT_PCK := "s03.pck"
const MARKER_BOOT := "S03_MARKER boot scene=main"
const MARKER_FRAME := "S03_MARKER frame="
const LAUNCH_FRAMES := 3
# Verbatim stderr line 1 of the refusal, minus its "ERROR: " prefix.
const REFUSAL_FRAG := "`--main-pack` was specified on the command line, but this Godot binary was compiled without support for path overrides. Aborting."
const REFUSAL_HINT := "`disable_path_overrides=no` SCons option when compiling Godot."
const REFUSAL_AT := "at: setup (main/main.cpp:"
const ERROR_PREFIX_HEX := "4552524f523a20"
const PROJECT_GODOT := "config_version=5\n\n[application]\nconfig/name=\"ExportLaunchS03\"\nrun/main_scene=\"res://main.tscn\"\nconfig/features=PackedStringArray(\"4.7\")\n\n[display]\nwindow/size/viewport_width=320\nwindow/size/viewport_height=180\n"
const MAIN_GD := "extends Node\n\nvar frames := 0\n\nfunc _ready() -> void:\n\tprint(\"S03_MARKER boot scene=main\")\n\nfunc _process(_delta: float) -> void:\n\tframes += 1\n\tprint(\"S03_MARKER frame=%d\" % frames)\n"
const MAIN_TSCN := "[gd_scene load_steps=2 format=3]\n\n[ext_resource type=\"Script\" path=\"res://main.gd\" id=\"1\"]\n\n[node name=\"Main\" type=\"Node\"]\nscript = ExtResource(\"1\")\n"
const EXPORT_PRESETS := "[preset.0]\nname=\"Linux/X11\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\ninclude_filter=\"\"\nexclude_filter=\"\"\nexport_path=\"\"\n\n[preset.0.options]\nbinary_format/architecture=\"x86_64\"\nbinary_format/embed_pck=false\n"

var arm := ""
var fresh := false
var _root := ""
var _proj := ""
var _out := ""
var _logs := ""
var _neutral := ""
var _xdg := ""
var _unshare := false
var _failed := false
var _items: PackedStringArray = []
var _pack := {}
var _bin_sha := ""
var _template_sha := ""
var _link_mode := ""
var _export_passes := 0
var _export_rc := -1
var _export_ms := 0
var _artifacts_reused := false
var _started_ms := 0


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
		elif a == "--fresh":
			fresh = true
	call_deferred("_run")


func _run() -> void:
	_started_ms = Time.get_ticks_msec()
	_root = _pick_root()
	if _root == "":
		_fail("no_writable_scratch_root")
		return
	_proj = _root.path_join("proj")
	_out = _root.path_join("out")
	_logs = _root.path_join("logs")
	_neutral = _root.path_join("neutral")
	_xdg = _root.path_join("xdg")
	for d in [_proj, _out, _logs, _neutral, _xdg]:
		_mkdir(d)
	_unshare = _probe_unshare()
	_diag("root", _root)
	_diag("userns_tmp_isolation", str(_unshare))
	_diag("editor_bin", _godot())
	_diag("template_bin", _template_path())
	match arm:
		"refuse":
			_arm_refuse()
		"contrast":
			_arm_contrast()
		"sibling":
			_arm_sibling()
		"all":
			_arm_refuse()
			if not _failed:
				_arm_contrast()
			if not _failed:
				_arm_sibling()
			if not _failed:
				quit(0)
		_:
			_fail("unknown_arm")


# ------------------------------------------------------------------ receipts

func _fail(reason: String) -> void:
	_failed = true
	print("FAIL export_launch_s03 %s reason=%s" % [arm, reason])
	quit(1)


func _ok() -> void:
	_diag("wall_ms", str(Time.get_ticks_msec() - _started_ms))
	print("PASS export_launch_s03 %s %s" % [arm, " ".join(_items)])
	quit(0)


func _it(key: String, value) -> void:
	_items.append("%s=%s" % [key, str(value)])


func _diag(key: String, value) -> void:
	print("S03_DIAG %s %s=%s" % [arm, key, str(value)])


func _rc_class(rc: int) -> String:
	if rc == 0:
		return "zero"
	return "nonzero_exit" if rc > 0 else "launch_error"


func _fmt_ints(values: Array) -> String:
	var parts: PackedStringArray = []
	for v in values:
		parts.append(str(v))
	return "[" + ",".join(parts) + "]"


# ------------------------------------------------------------------- scratch

func _pick_root() -> String:
	var candidates: PackedStringArray = []
	var override := OS.get_environment("EXPORT_LAUNCH_S03_ROOT")
	if override != "":
		candidates.append(override)
	var project_dir := ProjectSettings.globalize_path("res://")
	var key := _sha256_text(project_dir).substr(0, 12)
	candidates.append(OS.get_user_data_dir().path_join("export_launch_s03").path_join(key))
	if OS.get_environment("TMPDIR") != "":
		candidates.append(OS.get_environment("TMPDIR").path_join("export_launch_s03").path_join(key))
	candidates.append("/tmp/export_launch_s03/" + key)
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


func _template_path() -> String:
	var override := OS.get_environment("EXPORT_LAUNCH_S03_TEMPLATE")
	if override != "":
		return override
	var v := Engine.get_version_info()
	var version := "%d.%d.%d.%s" % [v["major"], v["minor"], v["patch"], v["status"]]
	# <xdg>/godot/app_userdata/<name> -> <xdg>/godot
	var godot_dir := OS.get_user_data_dir().get_base_dir().get_base_dir()
	return godot_dir.path_join("export_templates").path_join(version).path_join(TEMPLATE_BIN)


func _q(s: String) -> String:
	return "'" + s.replace("'", "'\\''") + "'"


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


func _read_text(path: String) -> String:
	return FileAccess.get_file_as_bytes(path).get_string_from_utf8()


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


func _sha256_bytes(bytes: PackedByteArray) -> String:
	if bytes.is_empty():
		# HashingContext.update() rejects a zero-length buffer with an engine
		# error; an empty stream has no digest to report.
		return ""
	var ctx := HashingContext.new()
	if ctx.start(HashingContext.HASH_SHA256) != OK:
		return ""
	if ctx.update(bytes) != OK:
		return ""
	return ctx.finish().hex_encode()


func _sha256_file(path: String) -> String:
	# sha256sum for the 70 MiB template binary; HashingContext for everything
	# else would need the whole file in memory, which is fine for the pack.
	var output: Array = []
	var rc := OS.execute("/usr/bin/sha256sum", PackedStringArray([path]), output, true)
	if rc != 0 or output.is_empty():
		return ""
	return str(output[0]).split(" ")[0]


# ----------------------------------------------------------------- execution

func _shell_merged(body: String, log_path: String) -> int:
	return OS.execute("/usr/bin/sh", PackedStringArray(["-c", "exec > " + _q(log_path) + " 2>&1\n" + body]))


func _run_split(cwd: String, exe: String, args: PackedStringArray, tag: String) -> Dictionary:
	var out_log := _logs.path_join(tag + ".out")
	var err_log := _logs.path_join(tag + ".err")
	DirAccess.remove_absolute(out_log)
	DirAccess.remove_absolute(err_log)
	var cmd := "cd " + _q(cwd) + "\n/usr/bin/env " + _q("XDG_DATA_HOME=" + _xdg) + " " + _q(exe)
	for a in args:
		cmd += " " + _q(a)
	cmd += " > " + _q(out_log) + " 2> " + _q(err_log)
	_diag("nested_" + tag, cmd.replace("\n", " ; "))
	var rc := OS.execute("/usr/bin/sh", PackedStringArray(["-c", cmd]))
	return {"rc": rc, "stdout": _read_text(out_log), "stderr": _read_text(err_log),
			"stdout_bytes": _file_size(out_log), "stderr_bytes": _file_size(err_log)}


# ------------------------------------------------------------------- project

func _build_project() -> bool:
	_mkdir(_proj)
	if not _write_text(_proj.path_join("project.godot"), PROJECT_GODOT):
		return false
	if not _write_text(_proj.path_join("main.gd"), MAIN_GD):
		return false
	if not _write_text(_proj.path_join("main.tscn"), MAIN_TSCN):
		return false
	return _write_text(_proj.path_join("export_presets.cfg"), EXPORT_PRESETS)


func _parse_pack(path: String) -> Dictionary:
	var bytes := FileAccess.get_file_as_bytes(path)
	var info := {"magic": "", "entries": 0, "bytes": bytes.size(), "pbin_size": -1, "pbin_ecfg": false, "pbin_off": -1, "dir_off": 0, "read_ok": not bytes.is_empty()}
	if bytes.size() < 0x28:
		return info
	info["magic"] = bytes.slice(0, 4).get_string_from_ascii()
	if info["magic"] != "GDPC":
		return info
	var dir_off := bytes.decode_u64(0x20)
	info["dir_off"] = int(dir_off)
	if dir_off <= 0 or dir_off + 4 > bytes.size():
		return info
	var count := int(bytes.decode_u32(dir_off))
	info["entries"] = count
	var pos := dir_off + 4
	for _i in count:
		if pos + 4 > bytes.size():
			break
		var name_len := int(bytes.decode_u32(pos))
		pos += 4
		if pos + name_len + 36 > bytes.size():
			break
		# Directory names are NUL-padded to a 4-byte boundary and the stored
		# length includes that padding (measured: "project.binary\0\0", len 16).
		# Cut the padding at the first NUL and decode as ASCII: decoding the
		# padding as UTF-8 emits "Unicode parsing error ... Unexpected NUL
		# character" on stderr, which the row must not carry.
		var raw_name := bytes.slice(pos, pos + name_len)
		var nul := raw_name.find(0)
		if nul >= 0:
			raw_name = raw_name.slice(0, nul)
		var name := raw_name.get_string_from_ascii()
		pos += name_len
		var offset := bytes.decode_u64(pos)
		pos += 8
		var size := bytes.decode_u64(pos)
		pos += 8
		pos += 16
		pos += 4
		if name == "project.binary":
			info["pbin_size"] = int(size)
			info["pbin_off"] = int(offset)
			if size >= 4 and offset + 4 <= bytes.size():
				info["pbin_ecfg"] = bytes.slice(offset, offset + 4).get_string_from_ascii() == "ECFG"
	return info


func _export_pack(isolate: bool) -> int:
	var log_path := _logs.path_join("export_pack.log")
	var body := "cd " + _q(_proj) + "\n" + _q(_godot()) + " --headless --path " + _q(_proj) + " --export-pack " + _q(PRESET) + " " + _q(_out.path_join(EXPORT_PCK))
	if isolate and _unshare:
		# Private /tmp for the packer's fixed /tmp/tmpproject.binary-* temp path.
		body = "mount -t tmpfs -o size=64M tmpfs /tmp || exit 97\n" + body
		body = "unshare -m --map-root-user /usr/bin/sh -c " + _q(body)
	_diag("export_isolated", str(isolate))
	_diag("export_cmd", body.replace("\n", " ; "))
	return _shell_merged(body, log_path)


func _pack_gate(info: Dictionary) -> bool:
	# Structural gate only: GDPC magic, a non-empty entry table and a non-zero
	# project.binary size. That is the r101-E0 F1 tripwire (a /tmp EDQUOT window
	# makes the packer store a 0-byte project.binary while the export exits 0).
	# Loadability is deliberately NOT asserted here — the contrast and sibling
	# arms run this same pack and assert the boot marker plus the frame vector.
	return info["magic"] == "GDPC" and int(info["entries"]) > 0 and int(info["pbin_size"]) > 0


func _ensure_artifacts() -> bool:
	var bin_path := _out.path_join(EXPORT_BIN)
	var pck_path := _out.path_join(EXPORT_PCK)
	var template := _template_path()
	if not FileAccess.file_exists(template):
		_diag("template_missing", template)
		_fail("no_stock_template_binary")
		return false
	if not fresh and FileAccess.file_exists(pck_path) and FileAccess.file_exists(bin_path):
		var cached := _parse_pack(pck_path)
		if _pack_gate(cached):
			_pack = cached
			_artifacts_reused = true
	_diag("artifacts_reused", str(_artifacts_reused))
	if _pack.is_empty():
		if not _build_project():
			return false
		DirAccess.remove_absolute(pck_path)
		DirAccess.remove_absolute(bin_path)
		var started := Time.get_ticks_msec()
		while _export_passes < 2:
			_export_passes += 1
			_export_rc = _export_pack(_export_passes > 1)
			if _export_rc == 0:
				var info := _parse_pack(pck_path)
				_diag("pack_probe", "pass=%d read_ok=%s bytes=%s magic=%s dir_off=%s entries=%s pbin_size=%s pbin_ecfg=%s" % [_export_passes, str(info["read_ok"]), str(info["bytes"]), str(info["magic"]), str(info["dir_off"]), str(info["entries"]), str(info["pbin_size"]), str(info["pbin_ecfg"])])
				if _pack_gate(info):
					_pack = info
					break
		_export_ms = Time.get_ticks_msec() - started
		if _pack.is_empty():
			_fail("export_pack_unusable rc=%d pbin_size=%s" % [_export_rc, str(_pack.get("pbin_size", -1))])
			return false
	# Stage the stock template binary as <out>/s03.x86_64. `ln` keeps the
	# template's inode (zero extra space) where scratch and the templates share a
	# device; `cp` is the cross-device fallback. Either way the staged bytes must
	# hash to the template's sha, which is what --export-release also writes.
	_template_sha = _sha256_file(template)
	if not FileAccess.file_exists(bin_path) or _sha256_file(bin_path) != _template_sha:
		DirAccess.remove_absolute(bin_path)
		if OS.execute("/usr/bin/sh", PackedStringArray(["-c", "ln " + _q(template) + " " + _q(bin_path)])) == 0:
			_link_mode = "hardlink"
		else:
			_link_mode = "copy"
			if OS.execute("/usr/bin/sh", PackedStringArray(["-c", "cp " + _q(template) + " " + _q(bin_path)])) != 0:
				_link_mode = "failed"
				_fail("stage_template_binary_failed")
				return false
		if _sha256_file(bin_path) != _template_sha:
			_link_mode = "sha_mismatch"
			_fail("staged_binary_sha_mismatch")
			return false
	else:
		_link_mode = "reused"
	_bin_sha = _sha256_file(bin_path)
	var staged_ok := _bin_sha == _template_sha
	_diag("pack_bytes", str(_pack["bytes"]))
	_diag("pack_entries", str(_pack["entries"]))
	_diag("pbin_size", str(_pack["pbin_size"]))
	_diag("pbin_ecfg", str(_pack["pbin_ecfg"]))
	_diag("pack_sha256", _sha256_file(pck_path))
	_diag("bin_bytes", str(_file_size(bin_path)))
	_diag("bin_sha256", _bin_sha)
	_diag("template_sha256", _template_sha)
	_diag("bin_is_template_copy", str(staged_ok))
	_diag("link_mode", _link_mode)
	_diag("export_passes", str(_export_passes))
	_diag("export_rc", str(_export_rc))
	_diag("export_ms", str(_export_ms))
	if not staged_ok:
		_fail("staged_binary_not_template")
		return false
	return true


# ---------------------------------------------------------------------- arms

func _classify_refusal(result: Dictionary) -> Dictionary:
	var err: String = result["stderr"]
	var lines := err.split("\n")
	var frag := ""
	var at_line := ""
	for line in lines:
		if frag == "" and line.begins_with("ERROR: ") and line.contains("was specified on the command line"):
			frag = line.substr(7)
		if at_line == "" and line.contains(REFUSAL_AT):
			at_line = line.strip_edges()
	return {"frag": frag, "at_line": at_line,
			"prefix_hex": err.substr(0, 7).to_utf8_buffer().hex_encode() if err.length() >= 7 else "",
			"hint_present": err.contains(REFUSAL_HINT),
			"stderr_bytes": result["stderr_bytes"],
			"stdout_bytes": result["stdout_bytes"],
			"stderr_sha256": _sha256_bytes(err.to_utf8_buffer())}


func _arm_refuse() -> void:
	_items = []
	if not _ensure_artifacts():
		return
	var bin_path := _out.path_join(EXPORT_BIN)
	var pck_path := _out.path_join(EXPORT_PCK)
	var args := PackedStringArray(["--headless", "--quit-after", str(LAUNCH_FRAMES), "--main-pack", pck_path])
	var run1 := _run_split(_out, bin_path, args, "refuse_existing")
	# Counterfactual: the same binary and cwd, --main-pack argument absent from disk.
	var run2 := _run_split(_out, bin_path, PackedStringArray(["--headless", "--quit-after", str(LAUNCH_FRAMES), "--main-pack", _root.path_join("absent.pck")]), "refuse_missing")
	var c1 := _classify_refusal(run1)
	var c2 := _classify_refusal(run2)
	_diag("refusal_stderr_sha256", str(c1["stderr_sha256"]))
	_diag("refusal_missing_stderr_sha256", str(c2["stderr_sha256"]))
	_diag("refusal_at_line", str(c1["at_line"]))
	_diag("refusal_lines", str(run1["stderr"].split("\n").size() - 1))
	_diag("sibling_pack_present", str(FileAccess.file_exists(pck_path)))
	var at_cpp := ""
	if c1["at_line"].contains("main/main.cpp:"):
		at_cpp = c1["at_line"].get_slice("main/main.cpp:", 1).get_slice(")", 0)
	_diag("at_main_cpp_line", at_cpp)
	if c1["frag"] != REFUSAL_FRAG:
		_fail("refusal_fragment_mismatch got=%s" % str(c1["frag"]))
		return
	if c1["prefix_hex"] != ERROR_PREFIX_HEX:
		_fail("refusal_prefix_hex_mismatch got=%s" % str(c1["prefix_hex"]))
		return
	if not c1["hint_present"]:
		_fail("refusal_hint_missing")
		return
	if c1["at_line"] == "":
		_fail("refusal_at_line_missing")
		return
	if run1["rc"] != 1:
		_fail("refusal_rc_not_1 got=%d" % run1["rc"])
		return
	if int(c1["stdout_bytes"]) != 0:
		_fail("refusal_stdout_not_empty bytes=%d" % int(c1["stdout_bytes"]))
		return
	if c2["frag"] != REFUSAL_FRAG or run2["rc"] != 1 or c1["stderr_sha256"] != c2["stderr_sha256"]:
		_fail("refusal_not_unconditional rc=%d sha1=%s sha2=%s" % [run2["rc"], str(c1["stderr_sha256"]), str(c2["stderr_sha256"])])
		return
	_it("binary", "exported_stock_template")
	_it("flag", "--main-pack")
	_it("rc", run1["rc"])
	_it("rc_class", _rc_class(run1["rc"]))
	_it("stdout_bytes", int(c1["stdout_bytes"]))
	_it("stderr_bytes", int(c1["stderr_bytes"]))
	_it("prefix_hex", c1["prefix_hex"])
	_it("hint_present", str(c1["hint_present"]).to_lower())
	_it("at_line_present", "true")
	_it("unconditional", "true")
	_it("sibling_pack_present", str(FileAccess.file_exists(pck_path)).to_lower())
	_it("frag", REFUSAL_FRAG)
	_ok()


func _arm_contrast() -> void:
	_items = []
	if not _ensure_artifacts():
		return
	var pck_path := _out.path_join(EXPORT_PCK)
	var run := _run_split(_neutral, _godot(), PackedStringArray(["--headless", "--main-pack", pck_path, "--quit-after", str(LAUNCH_FRAMES)]), "contrast_editor")
	var parsed := _markers(run["stdout"])
	_diag("contrast_banner", _banner(run["stdout"]))
	_diag("contrast_stdout_bytes", str(run["stdout_bytes"]))
	_diag("contrast_stderr_bytes", str(run["stderr_bytes"]))
	if run["rc"] != 0:
		_fail("contrast_rc_not_0 got=%d" % run["rc"])
		return
	if int(run["stderr_bytes"]) != 0:
		_fail("contrast_stderr_not_empty bytes=%d" % int(run["stderr_bytes"]))
		return
	if not _markers_ok(parsed):
		return
	if not _banner_ok(run["stdout"]):
		return
	_it("binary", "editor")
	_it("flag", "--main-pack")
	_it("rc", run["rc"])
	_it("rc_class", _rc_class(run["rc"]))
	_it("stderr_bytes", int(run["stderr_bytes"]))
	_it("stdout_bytes", int(run["stdout_bytes"]))
	_it("boot_lines", int(parsed["boot"]))
	_it("frames", _fmt_ints(parsed["frames"]))
	_it("extra_marker_lines", "false")
	_it("banner_version", _version_prefix())
	_ok()


func _arm_sibling() -> void:
	_items = []
	if not _ensure_artifacts():
		return
	var bin_path := _out.path_join(EXPORT_BIN)
	var pck_path := _out.path_join(EXPORT_PCK)
	var run := _run_split(_out, bin_path, PackedStringArray(["--headless", "--quit-after", str(LAUNCH_FRAMES)]), "sibling_template")
	var parsed := _markers(run["stdout"])
	_diag("sibling_banner", _banner(run["stdout"]))
	_diag("sibling_stdout_bytes", str(run["stdout_bytes"]))
	_diag("sibling_stderr_bytes", str(run["stderr_bytes"]))
	_diag("sibling_pack_path", pck_path)
	if not FileAccess.file_exists(pck_path):
		_fail("sibling_pack_missing")
		return
	if run["rc"] != 0:
		_fail("sibling_rc_not_0 got=%d" % run["rc"])
		return
	if int(run["stderr_bytes"]) != 0:
		_fail("sibling_stderr_not_empty bytes=%d" % int(run["stderr_bytes"]))
		return
	if not _markers_ok(parsed):
		return
	if not _banner_ok(run["stdout"]):
		return
	_it("binary", "exported_stock_template")
	_it("flag", "none")
	_it("rc", run["rc"])
	_it("rc_class", _rc_class(run["rc"]))
	_it("stderr_bytes", int(run["stderr_bytes"]))
	_it("stdout_bytes", int(run["stdout_bytes"]))
	_it("boot_lines", int(parsed["boot"]))
	_it("frames", _fmt_ints(parsed["frames"]))
	_it("extra_marker_lines", "false")
	_it("banner_version", _version_prefix())
	_it("sibling_pack_load", "true")
	_ok()


# ------------------------------------------------------------------ markers

func _markers(stdout: String) -> Dictionary:
	var boot := 0
	var frames: Array = []
	var extra := false
	for line in stdout.split("\n"):
		if line == MARKER_BOOT:
			boot += 1
		elif line.begins_with(MARKER_FRAME):
			frames.append(int(line.substr(MARKER_FRAME.length())))
		elif line.contains("S03_MARKER"):
			extra = true
	return {"boot": boot, "frames": frames, "extra": extra}


func _markers_ok(parsed: Dictionary) -> bool:
	var expected: Array = []
	for i in range(1, LAUNCH_FRAMES + 1):
		expected.append(i)
	if int(parsed["boot"]) != 1:
		_fail("boot_marker_count_%d" % int(parsed["boot"]))
		return false
	if parsed["frames"] != expected:
		_fail("frame_vector_mismatch got=%s want=%s" % [_fmt_ints(parsed["frames"]), _fmt_ints(expected)])
		return false
	if bool(parsed["extra"]):
		_fail("extra_marker_line")
		return false
	return true


func _banner(stdout: String) -> String:
	for line in stdout.split("\n"):
		if line.begins_with("Godot Engine v"):
			return line
	return ""


func _version_prefix() -> String:
	var v := Engine.get_version_info()
	return "%d.%d.%d" % [v["major"], v["minor"], v["patch"]]


func _banner_ok(stdout: String) -> bool:
	var banner := _banner(stdout)
	if banner == "":
		_fail("banner_missing")
		return false
	if not banner.begins_with("Godot Engine v" + _version_prefix() + "."):
		_fail("banner_version_mismatch got=%s" % banner)
		return false
	return true
