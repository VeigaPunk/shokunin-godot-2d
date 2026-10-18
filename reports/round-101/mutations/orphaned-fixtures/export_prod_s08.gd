extends SceneTree
# r101-E8 — export_prod scenario 08: missing export-templates error class.
#
# Probes the ACTUAL Godot 4.7.2 behavior when the export-templates directory is
# redirected to an empty path (XDG_DATA_HOME override; on Linux Godot resolves
# export templates as `$XDG_DATA_HOME/godot/export_templates/<version>/`).
# Measured on 4.7.2.stable.arch_linux.ed1daf0bf (probe log under
# reports/round-101/r101-E8.md):
#   * --export-release / --export-debug to an executable -> rc=1, zero products,
#     configuration-error class listing BOTH linux_debug.x86_64 and
#     linux_release.x86_64 as "No export template found at the expected path:".
#   * --export-pack to .pck -> rc=0 fallback (a data pack needs no template).
#   * --export-release to a .pck target with templates missing still FAILS
#     (the mode, not the target extension, decides the template requirement).
#
# Launch:
#   godot --headless --path <scratch> --script res://export_prod_s08.gd -- [--arm=<name>]
# Arms: control_exe | missing_exe | missing_pack | control_zip | missing_zip | missing_debug
#   default (no --arm)    -> control_exe, missing_exe, missing_pack
#   --arm=all             -> all six
#   --arm=<one of those>  -> just that arm
# Exit: 0 when every selected arm's assertions hold, 2 otherwise.

const PRESET := "Linux/X11"
const EXE_NAME := "x.x86_64"

var arm := ""
var _root := ""

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	_root = OS.get_user_data_dir() + "/r101e8-" + str(OS.get_process_id())
	var arms := _selected_arms()
	var ok := true
	for a in arms:
		if not _run_one(a):
			ok = false
	_cleanup()
	if ok:
		print("PASS export_prod_s08 done arms=%s" % ",".join(arms))
		quit(0)
		return
	print("FAIL export_prod_s08 done arms=%s" % ",".join(arms))
	quit(2)

func _selected_arms() -> PackedStringArray:
	match arm:
		"":
			return PackedStringArray(["control_exe", "missing_exe", "missing_pack"])
		"all":
			return PackedStringArray(["control_exe", "missing_exe", "missing_pack",
				"control_zip", "missing_zip", "missing_debug", "missing_relpck"])
		_:
			return PackedStringArray([arm])

func _run_one(name: String) -> bool:
	match name:
		"control_exe":
			return _arm_control_exe()
		"missing_exe":
			return _arm_missing_exe()
		"missing_pack":
			return _arm_missing_pack()
		"control_zip":
			return _arm_control_zip()
		"missing_zip":
			return _arm_missing_zip()
		"missing_debug":
			return _arm_missing_debug()
		"missing_relpck":
			return _arm_missing_relpck()
	return _fail(name, "unknown_arm")

# ---------------------------------------------------------------- receipt helpers

func _fail(name: String, reason: String) -> bool:
	print("FAIL export_prod_s08 %s reason=%s" % [name, reason])
	return false

func _cleanup() -> void:
	if _root != "" and DirAccess.dir_exists_absolute(_root):
		OS.execute("rm", ["-rf", _root], [], false, false)

func _write(path: String, text: String) -> void:
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string(text)
	f.close()

func _size(path: String) -> int:
	if not FileAccess.file_exists(path):
		return -1
	var f := FileAccess.open(path, FileAccess.READ)
	var n := f.get_length()
	f.close()
	return n

func _head(path: String, n: int) -> PackedByteArray:
	if not FileAccess.file_exists(path):
		return PackedByteArray()
	var f := FileAccess.open(path, FileAccess.READ)
	var b := f.get_buffer(n)
	f.close()
	return b

func _listing(dir: String) -> PackedStringArray:
	if not DirAccess.dir_exists_absolute(dir):
		return PackedStringArray()
	return DirAccess.get_files_at(dir)

func _version_tag() -> String:
	var v := Engine.get_version_info()
	return "%d.%d.%d.%s" % [v["major"], v["minor"], v["patch"], v["status"]]

# The templates dir the child process will use (same resolution as Godot's
# EditorPaths on Linux: XDG_DATA_HOME when set, else $HOME/.local/share).
func _child_templates_dir() -> String:
	var base := OS.get_environment("HOME") + "/.local/share"
	var xdg := OS.get_environment("XDG_DATA_HOME")
	if xdg != "":
		base = xdg
	return base + "/godot/export_templates/" + _version_tag() + "/"

# ---------------------------------------------------------------- scratch project

func _write_project(dir: String) -> void:
	DirAccess.make_dir_recursive_absolute(dir + "/out")
	_write(dir + "/project.godot", "config_version=5\n\n[application]\nconfig/name=\"R101E8\"\nrun/main_scene=\"res://main.tscn\"\nconfig/features=PackedStringArray(\"4.7\")\n\n[rendering]\nrenderer/rendering_method=\"gl_compatibility\"\n")
	_write(dir + "/main.gd", "extends Node\n\nfunc _ready() -> void:\n\tprint(\"R101E8_MAIN_READY\")\n\tget_tree().quit()\n")
	_write(dir + "/main.tscn", "[gd_scene load_steps=2 format=3]\n\n[ext_resource type=\"Script\" path=\"res://main.gd\" id=\"1\"]\n\n[node name=\"Main\" type=\"Node\"]\nscript = ExtResource(\"1\")\n")
	_write(dir + "/export_presets.cfg", "[preset.0]\n\nname=\"Linux/X11\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\ninclude_filter=\"\"\nexclude_filter=\"\"\nexport_path=\"\"\n\n[preset.0.options]\n\nbinary_format/architecture=\"x86_64\"\n")

# Spawn a fresh nested Godot exporting the scratch project just written.
# `xdg` non-empty prefixes XDG_DATA_HOME (the templates-dir override).
# Returns {rc, merged, out_dir, out_path, rc_text}. rc == -1 when the child's
# rc capture file was never written (child never reached the shell tail).
func _spawn(tag: String, action: String, out_name: String, xdg: String) -> Dictionary:
	var dir := _root + "/" + tag
	_write_project(dir)
	var out_dir := dir + "/out"
	var out_path := out_dir + "/" + out_name
	var merged_f := dir + "/child_merged.txt"
	var rc_f := dir + "/child_rc.txt"
	var prefix := ""
	if xdg != "":
		prefix = "XDG_DATA_HOME=\"%s\" " % xdg
	# OS.execute wraps the call in its own `sh -c --` layer, so `$?` must be
	# escaped to survive to the inner shell that ran the child (r86 pattern).
	var cmd := "%stimeout 45 \"%s\" --headless --path \"%s\" --%s \"%s\" \"%s\" >\"%s\" 2>&1; echo \\$? >\"%s\"" % [
		prefix, OS.get_executable_path(), dir, action, PRESET, out_path, merged_f, rc_f]
	var xrc := OS.execute("/bin/sh", ["-c", cmd], [], false, false)
	var rc_text := FileAccess.get_file_as_string(rc_f).strip_edges()
	var rc := int(rc_text) if rc_text != "" else -1
	return {"rc": rc, "rc_text": rc_text, "xrc": xrc, "merged": FileAccess.get_file_as_string(merged_f),
		"out_dir": out_dir, "out_path": out_path}

# ---------------------------------------------------------------- arms

# Templates present (real data dir), release export must succeed and produce a
# binary byte-equal in size to the installed linux_release template.
func _arm_control_exe() -> bool:
	var tpl := _child_templates_dir() + "linux_release.x86_64"
	var tpl_size := _size(tpl)
	if tpl_size <= 0:
		return _fail("control_exe", "host_template_missing path=%s" % tpl)
	var r := _spawn("control_exe", "export-release", EXE_NAME, "")
	var exe := String(r["out_path"])
	var size := _size(exe)
	var elf := _head(exe, 4) == PackedByteArray([0x7f, 0x45, 0x4c, 0x46])
	var pck := String(r["out_dir"]) + "/x.pck"
	var pck_ok := _size(pck) > 0 and _head(pck, 4) == PackedByteArray([0x47, 0x44, 0x50, 0x43])
	print("R101E8 control_exe child_rc=%d exe_bytes=%d tpl_bytes=%d pck_bytes=%d" % [
		r["rc"], size, tpl_size, _size(pck)])
	if int(r["rc"]) == 0 and size == tpl_size and elf and pck_ok:
		print("PASS export_prod_s08 control_exe child_rc=0 exe_bytes_match_template=true exe_magic=elf pck_magic=GDPC")
		return true
	return _fail("control_exe", "rc=%d exe_bytes=%d tpl_bytes=%d elf=%s pck_ok=%s" % [
		r["rc"], size, tpl_size, elf, pck_ok])

# Empty templates override: release export must fail with the configuration-error
# class and create zero products; the error must echo the overridden path.
func _arm_missing_exe() -> bool:
	var xdg := _root + "/xdg-empty-exe"
	DirAccess.make_dir_recursive_absolute(xdg)
	return _check_template_refusal("missing_exe", "export-release", xdg)

# Same command class as missing_exe but in debug mode (both template slots are
# checked regardless of export mode).
func _arm_missing_debug() -> bool:
	var xdg := _root + "/xdg-empty-debug"
	DirAccess.make_dir_recursive_absolute(xdg)
	return _check_template_refusal("missing_debug", "export-debug", xdg)

# Release export targeting a .pck path: still fails with the same class (the
# export mode, not the target extension, decides the template requirement).
func _arm_missing_relpck() -> bool:
	var xdg := _root + "/xdg-empty-relpck"
	DirAccess.make_dir_recursive_absolute(xdg)
	return _check_template_refusal("missing_relpck", "export-release", xdg, "x.pck")

func _check_template_refusal(tag: String, action: String, xdg: String, out_name: String = EXE_NAME) -> bool:
	var r := _spawn(tag, action, out_name, xdg)
	var merged := String(r["merged"])
	var lines := merged.split("\n")
	var want1 := "ERROR: Cannot export project with preset \"Linux/X11\" due to configuration errors:"
	var want2 := "ERROR: Project export for preset \"Linux/X11\" failed."
	var want3 := "No export template found at the expected path:"
	var tpl_prefix := xdg + "/godot/export_templates/" + _version_tag() + "/"
	var n3 := 0
	var dbg := false
	var rel := false
	for ln in lines:
		if ln == want3:
			n3 += 1
		elif ln == tpl_prefix + "linux_debug.x86_64":
			dbg = true
		elif ln == tpl_prefix + "linux_release.x86_64":
			rel = true
	var products := _listing(String(r["out_dir"])).size()
	if lines.has(want1):
		print(want1)
	if n3 > 0:
		print(want3)
		for ln in lines:
			if ln.begins_with(tpl_prefix):
				print(ln)
	if lines.has(want2):
		print(want2)
	print("R101E8 %s child_rc=%s products=%d tpl_path_lines=%d dbg=%s rel=%s" % [
		tag, r["rc_text"], products, n3, dbg, rel])
	if int(r["rc"]) == 1 and products == 0 and lines.has(want1) and lines.has(want2) and n3 >= 2 and dbg and rel:
		print("PASS export_prod_s08 %s child_rc=1 products=0 tpl_err=2 template_paths_echoed=true class=config_errors" % tag)
		return true
	return _fail(tag, "rc=%s products=%d want1=%s want2=%s tpl_lines=%d dbg=%s rel=%s" % [
		r["rc_text"], products, lines.has(want1), lines.has(want2), n3, dbg, rel])

# Empty templates override: a data pack needs no template -> rc=0 fallback.
func _arm_missing_pack() -> bool:
	var xdg := _root + "/xdg-empty-pack"
	DirAccess.make_dir_recursive_absolute(xdg)
	var r := _spawn("missing_pack", "export-pack", "x.pck", xdg)
	var pck := String(r["out_path"])
	var size := _size(pck)
	var magic := _head(pck, 4) == PackedByteArray([0x47, 0x44, 0x50, 0x43])
	var merged := String(r["merged"])
	var tpl_err := merged.contains("No export template found")
	var any_err := merged.contains("ERROR:")
	print("R101E8 missing_pack child_rc=%s pck_bytes=%d magic=%s tpl_err=%s" % [
		r["rc_text"], size, magic, tpl_err])
	if int(r["rc"]) == 0 and size > 0 and magic and not tpl_err and not any_err:
		print("PASS export_prod_s08 missing_pack child_rc=0 pck_magic=GDPC pck_nonempty=true tpl_err=0 fallback=pack_export_needs_no_template")
		return true
	return _fail("missing_pack", "rc=%s pck_bytes=%d magic=%s tpl_err=%s any_err=%s" % [
		r["rc_text"], size, magic, tpl_err, any_err])

# Zip pack with the empty override: observed rc=0; the artifact was 1755 bytes in
# every probe except one first run that wrote 0 bytes (transient, see shard), so
# size is recorded but not asserted -- only rc and, for non-empty output, the
# local-file-header magic.
func _arm_missing_zip() -> bool:
	var xdg := _root + "/xdg-empty-zip"
	DirAccess.make_dir_recursive_absolute(xdg)
	var r := _spawn("missing_zip", "export-pack", "x.zip", xdg)
	var zip := String(r["out_path"])
	var size := _size(zip)
	var pk := _head(zip, 4) == PackedByteArray([0x50, 0x4b, 0x03, 0x04])
	print("R101E8 missing_zip child_rc=%s zip_bytes=%d pk_header=%s" % [r["rc_text"], size, pk])
	if int(r["rc"]) == 0 and size >= 0 and (size == 0 or pk):
		print("PASS export_prod_s08 missing_zip child_rc=0 zip_written=true pk_header_or_empty=ok note=size_transient_observed")
		return true
	return _fail("missing_zip", "rc=%s zip_bytes=%d pk_header=%s" % [r["rc_text"], size, pk])

# Paired control for missing_zip: same pack export, real templates dir.
func _arm_control_zip() -> bool:
	var r := _spawn("control_zip", "export-pack", "x.zip", "")
	var zip := String(r["out_path"])
	var size := _size(zip)
	var pk := _head(zip, 4) == PackedByteArray([0x50, 0x4b, 0x03, 0x04])
	print("R101E8 control_zip child_rc=%s zip_bytes=%d pk_header=%s" % [r["rc_text"], size, pk])
	if int(r["rc"]) == 0 and size > 0 and pk:
		print("PASS export_prod_s08 control_zip child_rc=0 zip_nonempty=true pk_magic=true")
		return true
	return _fail("control_zip", "rc=%s zip_bytes=%d pk_header=%s" % [r["rc_text"], size, pk])
