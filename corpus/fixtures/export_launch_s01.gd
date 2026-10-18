extends SceneTree
# export_launch_s01 — r102 C1: embedded-binary launch receipt (seat E1).
#
# Scenario: export the scratch project with `binary_format/embed_pck=true`, then
# prove the produced binary is self-contained:
#   * it boots from an isolated directory containing no .pck at all (the binary
#     is renamed into a fresh dir before launch),
#   * rc=0, stdout marker `EXPORT_LAUNCH_S01 boot embed`, frames exactly 1..3
#     under `--quit-after 3`,
#   * size lower bound vs the pck+template sum and exact structural accounting:
#     the pack header sits exactly at the template boundary, the file ends in a
#     12-byte trailer (u64 packed size + GDPC magic), and
#     binary_bytes == template_bytes + pck_bytes + 12, so
#     binary_bytes >= template_bytes + pck_bytes.
#     `--arm=embed_ref` additionally re-exports the project as a standalone pack
#     (also serving as the r101-law warm-up) and pins the independent reference
#     sum binary_bytes >= template_bytes + ref_pck_bytes; the default `embed`
#     arm skips that second invocation to stay well inside the 8s fixture bound
#     (a lone cold embedded export was measured 3/3 green on fresh projects:
#     2026-10-18, export ~2.3-2.5s + boot ~0.8s each).
#
# Battery launch shape (8s fixture bound):
#   godot --headless --path <fixture proj> --script res://export_launch_s01.gd -- --arm=embed
#
# Arms / rows:
#   embed     (row export_launch_s01_embed_selfcontained)   ~4s
#   embed_ref (row export_launch_s01_embed_selfcontained_ref, adds ref.pck) ~6.5s
#   neg       (row export_launch_s01_mutated_pck_refusal): destroy the embedded
#             pack header magic at the template boundary and relaunch. The same
#             binary must NOT boot: no marker, verbatim missing-pck refusal in
#             the launched binary's stderr. Measured class on this host: the
#             engine prints `ERROR: Error: Couldn't load project data at path
#             "<cwd>". Is the .pck file missing?` and does NOT self-exit (killed
#             at the bound, rc=124). neg reuses <root>/s01/out/embed.x86_64 when
#             present (adjacent-row pattern, cf. r101 det_a/det_b, no export at
#             all); `--no-reuse` forces it to export its own <root>/s01neg pair.
#             Both neg paths emit the same PASS line.
#
# Scratch policy: <root>/<variant>/{proj,out,iso,logs}, <root> = first candidate
# of EXPORT_LAUNCH_ROOT, $TMPDIR/export_launch, <engine user-data dir>/export_launch,
# /tmp/export_launch that passes a 4096-byte write+readback probe. Nested engine
# output is redirected to <root>/<variant>/logs/*.log; PASS lines carry only
# derived booleans, counts and sizes — host paths appear only in DIAG lines.
#
# /tmp isolation: the 4.7.2 packer serializes project.binary through a fixed
# /tmp/tmpproject.binary-<rand> temp path ($TMPDIR is not honored); under the
# host's per-user /tmp quota that write can fail with EDQUOT and the packer
# silently stores a 0-byte project.binary. Exports therefore run inside
# `unshare -m --map-root-user sh -c 'mount -t tmpfs ... /tmp; ...'` when user
# namespaces are available (r101 E0 finding, same probe as export_prod.gd).
#
# Measured 2026-10-18 on godot 4.7.2.stable.arch_linux.ed1daf0bf, load ~7-25:
# fixture baseline ~0.8s, nested export ~2.3-2.5s, embedded launch ~0.8s.

const PRESET := "Linux/X11"
const RELEASE_TEMPLATE := "linux_release.x86_64"
const MARKER := "EXPORT_LAUNCH_S01 boot embed"
const FRAME_PREFIX := "EXPORT_LAUNCH_S01_FRAME "
const QUIT_AFTER := 3
const BOOT_BOUND := 4
const NEG_BOUND := 2
const TMP_PATH := "/usr/bin/timeout"
const TRAILER_BYTES := 12

const PROJECT_GODOT := "config_version=5\n\n[application]\nconfig/name=\"ExportLaunchS01\"\nrun/main_scene=\"res://main.tscn\"\nconfig/features=PackedStringArray(\"4.7\")\n\n[display]\nwindow/size/viewport_width=320\nwindow/size/viewport_height=180\n"
const PRESETS_CFG := "[preset.0]\nname=\"Linux/X11\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\ninclude_filter=\"\"\nexclude_filter=\"\"\nexport_path=\"\"\n\n[preset.0.options]\nbinary_format/architecture=\"x86_64\"\nbinary_format/embed_pck=true\n"
const MAIN_GD := "extends Node\n\nvar frames := 0\n\nfunc _ready() -> void:\n\tprint(\"EXPORT_LAUNCH_S01 boot embed\")\n\nfunc _process(_delta: float) -> void:\n\tframes += 1\n\tprint(\"EXPORT_LAUNCH_S01_FRAME %d\" % frames)\n"
const MAIN_TSCN := "[gd_scene load_steps=2 format=3]\n\n[ext_resource type=\"Script\" path=\"res://main.gd\" id=\"1\"]\n\n[node name=\"Main\" type=\"Node\"]\nscript = ExtResource(\"1\")\n"

var arm := ""
var reuse := true
var _items: PackedStringArray = []
var _root := ""
var _unshare := false


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
		elif a == "--no-reuse":
			reuse = false
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
			_arm_embed("s01", false)
		"embed_ref":
			_arm_embed("s01", true)
		"neg":
			_arm_neg()
		_:
			_fail("unknown_arm")


# ------------------------------------------------------------------ receipts

func _fail(reason: String) -> void:
	print("FAIL export_launch %s reason=%s" % [arm, reason])
	quit(1)


func _ok() -> void:
	print("PASS export_launch %s %s" % [arm, " ".join(_items)])
	quit(0)


func _it(key: String, value) -> void:
	_items.append("%s=%s" % [key, str(value)])


func _diag(key: String, value) -> void:
	print("EXPORT_LAUNCH_DIAG %s %s=%s" % [arm, key, str(value)])


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


func _out_dir(variant: String) -> String:
	return _variant_dir(variant).path_join("out")


func _iso_dir(variant: String) -> String:
	return _variant_dir(variant).path_join("iso")


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


func _head4(path: String) -> PackedByteArray:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return PackedByteArray()
	var b := f.get_buffer(4)
	f.close()
	return b


func _clear_dir(dir: String) -> void:
	var d := DirAccess.open(dir)
	if d == null:
		return
	for name in d.get_files():
		DirAccess.remove_absolute(dir.path_join(name))


func _run_logged(body: String, log_path: String, isolate := false) -> int:
	_mkdir(log_path.get_base_dir())
	var script := body
	if isolate and _unshare:
		script = "mount -t tmpfs -o size=64M tmpfs /tmp || exit 97\n" + body
		script = "unshare -m --map-root-user /usr/bin/sh -c " + _q(script)
	_diag("nested", body.replace("\n", " ; "))
	return OS.execute("/usr/bin/sh", PackedStringArray(["-c", "exec > " + _q(log_path) + " 2>&1\n" + script]))


# ------------------------------------------------------------------ projects

func _build_project(variant: String) -> bool:
	var proj := _proj_dir(variant)
	if not _mkdir(proj) or not _mkdir(_out_dir(variant)) or not _mkdir(_iso_dir(variant)):
		return false
	_clear_dir(_iso_dir(variant))
	_write_text(proj.path_join("project.godot"), PROJECT_GODOT)
	_write_text(proj.path_join("export_presets.cfg"), PRESETS_CFG)
	_write_text(proj.path_join("main.gd"), MAIN_GD)
	_write_text(proj.path_join("main.tscn"), MAIN_TSCN)
	return true


func _export(variant: String, mode: String, out_path: String) -> int:
	var proj := _proj_dir(variant)
	if FileAccess.file_exists(out_path):
		DirAccess.remove_absolute(out_path)
	var log_path := _log_path(variant, "%s_%s" % [mode, arm])
	var body := "cd " + _q(proj) + "\n" + _q(_godot()) + " --headless --path " + _q(proj) + " --export-" + mode + " " + _q(PRESET) + " " + _q(out_path)
	return _run_logged(body, log_path, true)


func _template_path() -> String:
	var v := Engine.get_version_info()
	var ver := "%d.%d.%d.%s" % [v["major"], v["minor"], v["patch"], v["status"]]
	var candidates: PackedStringArray = []
	if OS.get_environment("XDG_DATA_HOME") != "":
		candidates.append(OS.get_environment("XDG_DATA_HOME").path_join("godot/export_templates").path_join(ver).path_join(RELEASE_TEMPLATE))
	if OS.get_environment("HOME") != "":
		candidates.append(OS.get_environment("HOME").path_join(".local/share/godot/export_templates").path_join(ver).path_join(RELEASE_TEMPLATE))
	candidates.append("/usr/local/share/godot/export_templates/%s/%s" % [ver, RELEASE_TEMPLATE])
	candidates.append("/usr/share/godot/export_templates/%s/%s" % [ver, RELEASE_TEMPLATE])
	for c in candidates:
		if FileAccess.file_exists(c):
			return c
	return ""


# Parses the embedded-binary structure. ref_pck may be "" (not exported);
# the independent reference fields are then -1/false. Returns {} after _fail().
func _parse_binary(binary: String, ref_pck: String) -> Dictionary:
	var tpl_path := _template_path()
	if tpl_path == "":
		_fail("template_not_found")
		return {}
	var template_bytes := _file_size(tpl_path)
	var binary_bytes := _file_size(binary)
	if template_bytes <= 0 or binary_bytes <= template_bytes:
		_fail("artifact_size_invalid:%d:%d" % [template_bytes, binary_bytes])
		return {}
	var f := FileAccess.open(binary, FileAccess.READ)
	if f == null:
		_fail("binary_unreadable")
		return {}
	f.seek(template_bytes)
	var boundary := f.get_buffer(4)
	f.seek(binary_bytes - TRAILER_BYTES)
	var tail := f.get_buffer(TRAILER_BYTES)
	f.close()
	var pck_bytes := -1
	if tail.size() == TRAILER_BYTES:
		pck_bytes = tail[0] | (tail[1] << 8) | (tail[2] << 16) | (tail[3] << 24)
	var ref_pck_bytes := _file_size(ref_pck) if ref_pck != "" else -1
	var p: Dictionary = {
		"binary": binary,
		"template_bytes": template_bytes,
		"binary_bytes": binary_bytes,
		"pck_bytes": pck_bytes,
		"pck_at_template_boundary": boundary.size() == 4 and boundary.get_string_from_utf8() == "GDPC",
		"trailer_magic": tail.size() == TRAILER_BYTES and tail.slice(8, 12).get_string_from_utf8() == "GDPC",
		"ge_template_plus_pck": pck_bytes > 0 and binary_bytes >= template_bytes + pck_bytes,
		"accounting_exact": pck_bytes > 0 and template_bytes + pck_bytes + TRAILER_BYTES == binary_bytes,
		"ref_pck_bytes": ref_pck_bytes,
		"ref_ge_template_plus_pck": ref_pck_bytes > 0 and binary_bytes >= template_bytes + ref_pck_bytes,
	}
	_diag("elf_prefix_equal", _head4(binary) == _head4(tpl_path))
	return p


func _emit_structure(p: Dictionary) -> void:
	_it("pck_at_template_boundary", p["pck_at_template_boundary"])
	_it("trailer_magic", p["trailer_magic"])
	_it("accounting_exact", p["accounting_exact"])
	_it("ge_template_plus_pck", p["ge_template_plus_pck"])
	_it("template_bytes", p["template_bytes"])
	_it("pck_bytes", p["pck_bytes"])
	_it("binary_bytes", p["binary_bytes"])
	if int(p["ref_pck_bytes"]) > 0:
		_it("ref_pck_bytes", p["ref_pck_bytes"])
		_it("ref_ge_template_plus_pck", p["ref_ge_template_plus_pck"])


func _structure_ok(p: Dictionary) -> bool:
	if not (p["pck_at_template_boundary"] and p["trailer_magic"] and p["accounting_exact"] and p["ge_template_plus_pck"]):
		return false
	if int(p["ref_pck_bytes"]) > 0:
		return p["ref_ge_template_plus_pck"]
	return true


# Full path: build, optional warm-up pack export (+ reference), embedded release
# export, structural parse. Returns {} after a FAIL.
func _prepare(variant: String, with_ref: bool) -> Dictionary:
	if not _build_project(variant):
		return {}
	var out := _out_dir(variant)
	var ref_pck := out.path_join("ref.pck") if with_ref else ""
	var binary := out.path_join("embed.x86_64")
	if with_ref:
		# Warm-up first: the r101 E0 law measured the first export of an
		# unimported project as corrupt (same-root re-exports were deterministic).
		var warm := _export(variant, "pack", ref_pck)
		if warm != 0 or not FileAccess.file_exists(ref_pck):
			_fail("warmup_pack_export_failed:%d" % warm)
			return {}
	var rel := _export(variant, "release", binary)
	if rel != 0 or not FileAccess.file_exists(binary):
		_fail("embed_export_failed:%d" % rel)
		return {}
	return _parse_binary(binary, ref_pck)


# ------------------------------------------------------------------- launches

func _launch_isolated(variant: String, binary: String, log_name: String, bound_s: int) -> Dictionary:
	var iso := _iso_dir(variant)
	if not _mkdir(iso):
		return {}
	var dest := iso.path_join(binary.get_file())
	if FileAccess.file_exists(dest):
		DirAccess.remove_absolute(dest)
	var rerr := DirAccess.rename_absolute(binary, dest)
	if rerr != OK:
		_fail("iso_rename_failed:%d" % rerr)
		return {}
	var bound := ""
	if FileAccess.file_exists(TMP_PATH):
		bound = TMP_PATH + " -k 1 %d " % bound_s
	_diag("launch_bound", bound_s)
	var log_path := _log_path(variant, log_name)
	var body := "cd " + _q(iso) + "\n" + bound + _q(dest) + " --headless --quit-after " + str(QUIT_AFTER)
	var code := _run_logged(body, log_path)
	var text := FileAccess.get_file_as_string(log_path)
	return {"exit": code, "text": text, "iso": iso, "dest": dest}


func _iso_pck_count(iso: String) -> int:
	var n := 0
	var d := DirAccess.open(iso)
	if d == null:
		return -1
	for name in d.get_files():
		if name.ends_with(".pck"):
			n += 1
	return n


func _iso_file_count(iso: String) -> int:
	var d := DirAccess.open(iso)
	if d == null:
		return -1
	return d.get_files().size()


func _frames_of(text: String) -> PackedInt32Array:
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


# ---------------------------------------------------------------------- arms

func _arm_embed(variant: String, with_ref: bool) -> void:
	var p := _prepare(variant, with_ref)
	if p.is_empty():
		return
	if not _structure_ok(p):
		_fail("structure_check_failed:boundary=%s:trailer=%s:accounting=%s:ge=%s" % [p["pck_at_template_boundary"], p["trailer_magic"], p["accounting_exact"], p["ge_template_plus_pck"]])
		return
	var launch := _launch_isolated(variant, p["binary"], "launch_embed", BOOT_BOUND)
	if launch.is_empty():
		return
	var text: String = launch["text"]
	var frames := _frames_of(text)
	var marker := text.contains(MARKER)
	var boot_exit: int = launch["exit"]
	var pcks := _iso_pck_count(launch["iso"])
	_diag("launch_exit", boot_exit)
	_diag("launch_log_bytes", text.length())
	_it("boot", "embed")
	_it("exit", boot_exit)
	_it("quit_after", QUIT_AFTER)
	_it("frames", _fmt_ints(frames))
	_it("extra", _fmt_ints(frames) != "[1,2,3]")
	_it("marker", marker)
	_it("iso_files", _iso_file_count(launch["iso"]))
	_it("no_adjacent_pck", pcks == 0)
	_emit_structure(p)
	if boot_exit != 0 or not marker or _fmt_ints(frames) != "[1,2,3]":
		_fail("embedded_boot_incomplete:exit=%d:marker=%s:frames=%s" % [boot_exit, marker, _fmt_ints(frames)])
		_items.clear()
		return
	_ok()


func _reuse_source() -> String:
	for candidate in [_out_dir("s01").path_join("embed.x86_64"), _iso_dir("s01").path_join("embed.x86_64")]:
		if FileAccess.file_exists(candidate):
			return candidate
	return ""


func _arm_neg() -> void:
	var p := {}
	var launch_variant := "s01neg"
	var reused := _reuse_source()
	if reuse and reused != "":
		_diag("source", "reused_s01")
		p = _parse_binary(reused, "")
		if p.is_empty():
			return
		if not _mkdir(_out_dir(launch_variant)) or not _mkdir(_iso_dir(launch_variant)):
			return
		_clear_dir(_iso_dir(launch_variant))
		var copy := _out_dir(launch_variant).path_join("embed_mut.x86_64")
		if FileAccess.file_exists(copy):
			DirAccess.remove_absolute(copy)
		var cp := OS.execute("/usr/bin/sh", PackedStringArray(["-c", "exec > /dev/null 2>&1\n/usr/bin/cp -f " + _q(p["binary"]) + " " + _q(copy)]))
		if cp != 0:
			_fail("mutation_copy_failed:%d" % cp)
			return
		p["binary"] = copy
	else:
		_diag("source", "exported_s01neg")
		p = _prepare(launch_variant, false)
		if p.is_empty():
			return
	if not p["pck_at_template_boundary"]:
		_fail("negative_baseline_not_embedded")
		return
	# Destroy the embedded pack header magic at the template boundary.
	var f := FileAccess.open(p["binary"], FileAccess.READ_WRITE)
	if f == null:
		_fail("mutation_open_failed")
		return
	f.seek(p["template_bytes"])
	f.store_buffer("ZZZZ".to_utf8_buffer())
	f.close()
	# Re-parse the mutated artifact so the emitted structure fields describe it
	# (boundary magic destroyed, trailer and accounting untouched).
	var mp := _parse_binary(p["binary"], "")
	if mp.is_empty():
		return
	var launch := _launch_isolated(launch_variant, p["binary"], "launch_neg", NEG_BOUND)
	if launch.is_empty():
		return
	var text: String = launch["text"]
	var rc: int = launch["exit"]
	var marker := text.contains(MARKER)
	var refusal := text.contains("Couldn't load project data at path") and text.contains("Is the .pck file missing?")
	_diag("mutant_exit", rc)
	_diag("mutant_log_bytes", text.length())
	_it("mutated_header", true)
	_it("marker", marker)
	_it("refusal", "missing_pck_refusal" if refusal else "other")
	_it("exit_rc", rc)
	_it("bounded_kill", rc == 124)
	_emit_structure(mp)
	if marker or not refusal or rc != 124:
		_fail("mutation_control_class:marker=%s:refusal=%s:rc=%d" % [marker, refusal, rc])
		_items.clear()
		return
	_ok()
