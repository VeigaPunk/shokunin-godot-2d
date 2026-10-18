extends SceneTree
# export_launch — r102 C1 launch-matrix harness: proves the two Linux/X11
# release launch mechanics against the real 4.7.2 export pipeline:
#
#   embed_pck=true  -> ONE self-contained artifact: a template binary with the
#                      PCK appended. It boots from any directory with
#                      `--quit-after N` and no sidecar file present.
#   embed_pck=false -> stock template binary + `<name>.pck` sidecar. The
#                      binary boots the sidecar sitting next to it, and it
#                      REFUSES `--main-pack` with "compiled without support for
#                      path overrides" (disable_path_overrides=no); the editor
#                      build boots the same pack, so the refusal is a property
#                      of the exported template build, not of the pack.
#
# Battery launch shape (one arm per process, 8s fixture bound):
#   godot --headless --path <fixture proj> --script res://export_launch.gd -- --arm=<arm>
#
# Arms and the PASS lines that rows pin (suggested row names in r102-E0-spec):
#   embed -> embed_boot       (embedded binary, isolated cwd, marker + exact
#                              --quit-after frame vector)
#            embed_census     (single artifact, no sidecar, binary tail magic)
#            embed_refusal    (embedded build refuses --main-pack too)
#   stock -> stock_boot       (stock binary boots its adjacent sidecar)
#            stock_census     (two artifacts, PCK magic/size)
#   probe -> refusal          (stock binary --main-pack refusal class, verbatim)
#            editor_boot      (editor binary boots the SAME pck: contrast)
#            hole             (binary without its sidecar: distinct error class)
#
# Scratch policy: every arm builds its project under <root>/<variant>/proj and
# writes artifacts under <root>/<variant>/{moved,out}; <root> is the first
# candidate of EXPORT_LAUNCH_ROOT, $TMPDIR/export_launch, <engine user-data
# dir>/export_launch and /tmp/export_launch that passes a 4096-byte
# write+readback probe. Host paths appear only in EXPORT_LAUNCH_DIAG lines,
# never inside the pinned PASS lines.
#
# TMP isolation (measured 2026-10-18, r101 E0): the 4.7.2 packer serializes
# project.binary through a FIXED temp path /tmp/tmpproject.binary-<rand>
# (strace-verified; $TMPDIR is not honored), and under a full per-user /tmp
# quota that write(2) returns EDQUOT — the packer ignores the error, stores a
# 0-byte project.binary and the exported artifact then fails to load its own
# settings while the export still exits 0. Exports therefore run inside
# `unshare -m --map-root-user sh -c 'mount -t tmpfs ... /tmp; ...'` (private
# /tmp) when user namespaces are available; a broken artifact shows up as a
# failed boot, never as a silent PASS.
#
# Evidence rule: nested Godot output is never echoed — every nested shell is
# redirected to <root>/<variant>/logs/*.log and PASS lines carry only derived
# booleans, counts and magic strings. Operational failures (export crash,
# missing artifact) print FAIL and exit 1.
#
# Measured 2026-10-18 on godot 4.7.2.stable.arch_linux.ed1daf0bf (host load
# 7-9): export ~2s, template launch ~0.6-0.9s, refusal ~0.01s, missing-sidecar
# timeout probe 2s — every arm stays under the 8s bound.

const PRESET_EMBED := "EmbedPck"
const PRESET_STOCK := "Stock"
const REFUSAL := "compiled without support for path overrides"
const DISABLE_HINT := "disable_path_overrides=no"
const MISSING_DATA := "Couldn't load project data at path"
const MISSING_HINT := "Is the .pck file missing?"
const BOOT_MARKER := "EXPORT_LAUNCH_MAIN boot scene=main"
const FRAME_PREFIX := "EXPORT_LAUNCH_FRAME "
const EXPECTED_FRAMES := "[1,2,3]"
const QUIT_FRAMES := 3
const HOLE_TIMEOUT := 2

const MAIN_GD := "extends Node\n\nvar frames := 0\n\nfunc _ready() -> void:\n\tprint(\"EXPORT_LAUNCH_MAIN boot scene=main\")\n\nfunc _process(_delta: float) -> void:\n\tframes += 1\n\tprint(\"EXPORT_LAUNCH_FRAME %d\" % frames)\n"
const MAIN_TSCN := "[gd_scene load_steps=2 format=3]\n\n[ext_resource type=\"Script\" path=\"res://main.gd\" id=\"1\"]\n\n[node name=\"Main\" type=\"Node\"]\nscript = ExtResource(\"1\")\n"
const PROJECT_GODOT := "config_version=5\n\n[application]\nconfig/name=\"ExportLaunch\"\nrun/main_scene=\"res://main.tscn\"\nconfig/features=PackedStringArray(\"4.7\")\n\n[display]\nwindow/size/viewport_width=320\nwindow/size/viewport_height=180\n"

var arm := ""
var opt := {}
var _items: PackedStringArray = []
var _root := ""
var _unshare := false


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
		elif a.begins_with("--"):
			var kv := a.substr(2).split("=", true, 1)
			opt[kv[0]] = kv[1] if kv.size() > 1 else "1"
	call_deferred("_run")


func _run() -> void:
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
		"stock":
			_arm_stock()
		"probe":
			_arm_probe()
		_:
			_fail("unknown_arm")


# ------------------------------------------------------------------ receipts

func _fail(reason: String) -> void:
	print("FAIL export_launch %s reason=%s" % [arm, reason])
	quit(1)


func _diag(key: String, value) -> void:
	print("EXPORT_LAUNCH_DIAG %s %s=%s" % [arm, key, str(value)])


func _emit(kind: String, fields: PackedStringArray) -> void:
	print("PASS export_launch %s %s" % [kind, " ".join(fields)])


# ------------------------------------------------------------------- scratch

func _pick_root() -> String:
	var candidates: PackedStringArray = []
	if OS.get_environment("EXPORT_LAUNCH_ROOT") != "":
		candidates.append(OS.get_environment("EXPORT_LAUNCH_ROOT"))
	if OS.get_environment("TMPDIR") != "":
		candidates.append(OS.get_environment("TMPDIR").path_join("export_launch"))
	candidates.append(OS.get_user_data_dir().path_join("export_launch"))
	candidates.append("/tmp/export_launch")
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


func _run_logged(body: String, log_path: String, isolate := false) -> int:
	_mkdir(log_path.get_base_dir())
	var script := body
	if isolate and _unshare:
		# Private /tmp for the packer's fixed tmpproject.binary temp path.
		script = "mount -t tmpfs -o size=64M tmpfs /tmp || exit 97\n" + body
		script = "unshare -m --map-root-user /usr/bin/sh -c " + _q(script)
	_diag("nested", body.replace("\n", " ; "))
	return OS.execute("/usr/bin/sh", PackedStringArray(["-c", "exec > " + _q(log_path) + " 2>&1\n" + script]))


# ------------------------------------------------------------------ projects

func _build_project(variant: String) -> String:
	var proj := _proj_dir(variant)
	_mkdir(proj)
	_clear_dir(_variant_dir(variant).path_join("moved"))
	_clear_dir(_variant_dir(variant).path_join("out"))
	_clear_dir(_variant_dir(variant).path_join("hole"))
	_write_text(proj.path_join("project.godot"), PROJECT_GODOT)
	_write_text(proj.path_join("export_presets.cfg"), "[preset.0]\nname=\"EmbedPck\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\ninclude_filter=\"\"\nexclude_filter=\"\"\nexport_path=\"\"\n\n[preset.0.options]\nbinary_format/architecture=\"x86_64\"\nbinary_format/embed_pck=true\n\n[preset.1]\nname=\"Stock\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\ninclude_filter=\"\"\nexclude_filter=\"\"\nexport_path=\"\"\n\n[preset.1.options]\nbinary_format/architecture=\"x86_64\"\nbinary_format/embed_pck=false\n")
	_write_text(proj.path_join("main.gd"), MAIN_GD)
	_write_text(proj.path_join("main.tscn"), MAIN_TSCN)
	return proj


func _export(variant: String, preset: String, out_path: String) -> int:
	var proj := _proj_dir(variant)
	var body := "cd " + _q(proj) + "\n" + _q(_godot()) + " --headless --path " + _q(proj) + " --export-release " + _q(preset) + " " + _q(out_path)
	return _run_logged(body, _log_path(variant, "export"), true)


# ---------------------------------------------------------------------- arms

func _arm_embed() -> void:
	var proj := _build_project("embed")
	var moved := _variant_dir("embed").path_join("moved")
	_mkdir(moved)
	var bin := moved.path_join("embed.x86_64")
	var code := _export("embed", PRESET_EMBED, bin)
	if code != 0 or not FileAccess.file_exists(bin):
		_fail("embed_export_failed:%d" % code)
		return
	var run_log := _log_path("embed", "run")
	var run_code := _run_logged("cd " + _q(moved) + "\n./embed.x86_64 --headless --quit-after %d" % QUIT_FRAMES, run_log)
	var text := FileAccess.get_file_as_string(run_log)
	var frames := _frame_numbers(text)
	var boot := PackedStringArray()
	boot.append("boot=%s" % text.contains(BOOT_MARKER))
	boot.append("frames=%s" % _fmt_ints(frames))
	boot.append("extra=%s" % (_fmt_ints(frames) != EXPECTED_FRAMES))
	boot.append("exit=%d" % run_code)
	boot.append("cwd=isolated")
	_emit("embed_boot", boot)
	var files := _files_in(moved)
	var census := PackedStringArray()
	census.append("artifacts=%d" % files.size())
	census.append("sidecar_pck=%d" % _files_matching(moved, ".pck"))
	census.append("tail_magic=%s" % _tail_magic(bin))
	census.append("binary_bytes=%d" % _file_size(bin))
	_emit("embed_census", census)
	# The embedded build is the same template build: path overrides refused.
	var ref_log := _log_path("embed", "refusal")
	var ref_code := _run_logged("cd /\n" + _q(bin) + " --headless --main-pack " + _q(_variant_dir("embed").path_join("none.pck")) + " --quit-after %d" % QUIT_FRAMES, ref_log)
	var ref_text := FileAccess.get_file_as_string(ref_log)
	var ref := PackedStringArray()
	ref.append("rc=%d" % ref_code)
	ref.append("class=%s" % ("path_overrides_disabled" if ref_text.contains(REFUSAL) else "other"))
	ref.append("hint=%s" % ("disable_path_overrides_no" if ref_text.contains(DISABLE_HINT) else "missing"))
	ref.append("log_bytes=%d" % ref_text.length())
	_emit("embed_refusal", ref)
	_diag("project", proj)
	quit(0)


func _arm_stock() -> void:
	var proj := _build_project("stock")
	var out_dir := _variant_dir("stock").path_join("out")
	_mkdir(out_dir)
	var bin := out_dir.path_join("stock.x86_64")
	var code := _export("stock", PRESET_STOCK, bin)
	if code != 0 or not FileAccess.file_exists(bin):
		_fail("stock_export_failed:%d" % code)
		return
	var boot_log := _log_path("stock", "sidecar_boot")
	var run_code := _run_logged("cd " + _q(out_dir) + "\n./stock.x86_64 --headless --quit-after %d" % QUIT_FRAMES, boot_log)
	var text := FileAccess.get_file_as_string(boot_log)
	var frames := _frame_numbers(text)
	var boot := PackedStringArray()
	boot.append("boot=%s" % text.contains(BOOT_MARKER))
	boot.append("frames=%s" % _fmt_ints(frames))
	boot.append("extra=%s" % (_fmt_ints(frames) != EXPECTED_FRAMES))
	boot.append("exit=%d" % run_code)
	boot.append("sidecar=cwd")
	_emit("stock_boot", boot)
	var pck := out_dir.path_join("stock.pck")
	var census := PackedStringArray()
	census.append("artifacts=%d" % _files_in(out_dir).size())
	census.append("pck_exists=%s" % FileAccess.file_exists(pck))
	census.append("pck_magic=%s" % _head_magic(pck))
	census.append("pck_bytes=%d" % _file_size(pck))
	census.append("bin_bytes=%d" % _file_size(bin))
	_emit("stock_census", census)
	_diag("project", proj)
	quit(0)


func _arm_probe() -> void:
	var proj := _build_project("probe")
	var out_dir := _variant_dir("probe").path_join("out")
	_mkdir(out_dir)
	var bin := out_dir.path_join("probe.x86_64")
	var code := _export("probe", PRESET_STOCK, bin)
	if code != 0 or not FileAccess.file_exists(bin):
		_fail("probe_export_failed:%d" % code)
		return
	var pck := out_dir.path_join("probe.pck")
	if not FileAccess.file_exists(pck):
		_fail("probe_sidecar_missing")
		return
	# 1. Exported template build + --main-pack: refusal class (verbatim).
	var ref_log := _log_path("probe", "refusal")
	var ref_code := _run_logged("cd " + _q(out_dir) + "\n./probe.x86_64 --headless --main-pack " + _q(pck) + " --quit-after %d" % QUIT_FRAMES, ref_log)
	var ref_text := FileAccess.get_file_as_string(ref_log)
	var refusal := PackedStringArray()
	refusal.append("rc=%d" % ref_code)
	refusal.append("class=%s" % ("path_overrides_disabled" if ref_text.contains(REFUSAL) else "other"))
	refusal.append("hint=%s" % ("disable_path_overrides_no" if ref_text.contains(DISABLE_HINT) else "missing"))
	refusal.append("log_bytes=%d" % ref_text.length())
	_emit("refusal", refusal)
	# 2. Editor build + the SAME pack: boots (contrast -> the pack is loadable).
	var edit_log := _log_path("probe", "editor_boot")
	var edit_code := _run_logged("cd /\n" + _q(_godot()) + " --headless --main-pack " + _q(pck) + " --quit-after %d" % QUIT_FRAMES, edit_log)
	var edit_text := FileAccess.get_file_as_string(edit_log)
	var edit_frames := _frame_numbers(edit_text)
	var editor := PackedStringArray()
	editor.append("boot=%s" % edit_text.contains(BOOT_MARKER))
	editor.append("frames=%s" % _fmt_ints(edit_frames))
	editor.append("extra=%s" % (_fmt_ints(edit_frames) != EXPECTED_FRAMES))
	editor.append("exit=%d" % edit_code)
	_emit("editor_boot", editor)
	# 3. Same binary without its sidecar: distinct error class, keeps running.
	var hole := _variant_dir("probe").path_join("hole")
	_mkdir(hole)
	var hole_bin := hole.path_join("probe.x86_64")
	var copy_code := _run_logged("cp " + _q(bin) + " " + _q(hole_bin) + "\nchmod +x " + _q(hole_bin), _log_path("probe", "hole_copy"))
	if copy_code != 0:
		_fail("hole_copy_failed:%d" % copy_code)
		return
	var hole_log := _log_path("probe", "hole_run")
	var hole_code := _run_logged("cd " + _q(hole) + "\ntimeout %d ./probe.x86_64 --headless --quit-after %d > hole.out 2> hole.err" % [HOLE_TIMEOUT, QUIT_FRAMES], hole_log)
	var hole_out := FileAccess.get_file_as_string(hole.path_join("hole.out"))
	var hole_err := FileAccess.get_file_as_string(hole.path_join("hole.err"))
	var hole_fields := PackedStringArray()
	hole_fields.append("rc=%d" % hole_code)
	hole_fields.append("class=%s" % ("project_data_missing" if hole_err.contains(MISSING_DATA) else "other"))
	hole_fields.append("pck_hint=%s" % hole_err.contains(MISSING_HINT))
	hole_fields.append("stdout_bytes=%d" % hole_out.length())
	hole_fields.append("stderr_bytes=%d" % hole_err.length())
	_emit("hole", hole_fields)
	_diag("project", proj)
	quit(0)


# ------------------------------------------------------------------ analysis

func _clear_dir(dir: String) -> void:
	if not DirAccess.dir_exists_absolute(dir):
		return
	for name in DirAccess.get_files_at(dir):
		DirAccess.remove_absolute(dir.path_join(name))


func _files_in(dir: String) -> PackedStringArray:
	var out := PackedStringArray()
	for name in DirAccess.get_files_at(dir):
		out.append(name)
	out.sort()
	return out


func _files_matching(dir: String, suffix: String) -> int:
	var n := 0
	for name in DirAccess.get_files_at(dir):
		if name.ends_with(suffix):
			n += 1
	return n


func _head_magic(path: String) -> String:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return "missing"
	var b := f.get_buffer(4)
	f.close()
	return b.hex_encode()


func _tail_magic(path: String) -> String:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return "missing"
	f.seek(f.get_length() - 4)
	var b := f.get_buffer(4)
	f.close()
	return b.hex_encode()


func _frame_numbers(text: String) -> PackedInt32Array:
	var out := PackedInt32Array()
	for line in text.split("\n"):
		if line.begins_with(FRAME_PREFIX):
			out.append(line.substr(FRAME_PREFIX.length()).strip_edges().to_int())
	return out


func _fmt_ints(values: PackedInt32Array) -> String:
	var parts := PackedStringArray()
	for v in values:
		parts.append(str(v))
	return "[%s]" % ",".join(parts)
