extends SceneTree
# export_div_s05 — r103 C1: editor-settings / override surfaces of the headless
# export run (seat E5). Actual behavior only.
#
# Scenario: a two-file child project (`main.tscn` + `notes.tres` — the pair the
# r103-E5 hand probes used) is exported with `--export-pack` under a
# fixture-owned XDG_CONFIG_HOME, so every probe observes the editor-config
# surface the CLI export actually uses: the store the engine resolves as
#   $XDG_CONFIG_HOME/godot/editor_settings-<major>.<minor>.tres
# (measured: a bare `--export-pack` run creates it, 17728 B on this host, and
# also creates feature_profiles/ script_templates/ text_editor_themes/).
#
#   arm=store (row export_div_s05_editor_settings_store)
#     export#1 into a fresh cfg root -> the run itself creates the store; then
#     one known EditorSettings key
#     (`filesystem/external_programs/terminal_emulator`) is overwritten with a
#     marker value and export#2 runs against the crafted store. PASS demands the
#     two packs are byte-identical (editor-settings CONTENTS do not reach the
#     Linux/X11 pack) and that the export did not rewrite the store (same
#     sha256, marker still present).
#
#   arm=heal (row export_div_s05_editor_settings_corrupt)
#     export#0 into a fresh cfg root records the default store (bytes+sha256);
#     the store is then overwritten with non-tres garbage and export#1 runs.
#     PASS demands the run still exits 0 (editor settings fail OPEN), the
#     verbatim refusal class is present in the nested log, and the store was
#     HEALED to the byte-identical default (same bytes+sha256) — while the pack
#     equals the pre-corruption pack.
#
#   arm=ctb (row export_div_s05_project_setting_ctb)
#     `editor/export/convert_text_resources_to_binary` is an EDITOR-PREFIXED
#     *project* setting honored by the export run (measured: effective default
#     `true`; explicit false ships `main.tscn`/`notes.tres` as text and keeps
#     only the script's own compile remap — single-path hand-probe pack shas
#     3390d9a1… default vs a774d6e3… false; `.remap` counts 3 vs 1).
#     export#1: project.godot carries `=false` -> text pack. `res://override.cfg`
#     is then added next to it with `[editor]
#     export/convert_text_resources_to_binary=true` and export#2 runs. PASS
#     demands pack#2 is byte-identical to pack#1 (the EXPORT RUN ignores
#     override.cfg for this setting; override.cfg is not packed), while a
#     SOURCE run of that very directory (game mode, `--path`) prints
#     `DIV_S05_CTB true` — the runtime honors the override. One directory, two
#     consumers, two answers: the C1 divergence this seat pins.
#
# Receipt line (verbatim, parsed here only):
#   DIV_S05_CTB <true|false|unset>   (child main scene, source run)
# PASS lines carry derived booleans, entry-name classes and entry counts only.
# Pack sha256 and editor-settings digests/bytes are evidence, never pins: packs
# embed scene `node_ids` seeded per project PATH (two fresh scratch roots differ
# in exactly 20 bytes — offsets 939-942 and 2052-2067, both inside the `node_ids`
# block — and are byte-equal otherwise, while the same path repeated gives an
# identical pack), and the editor store embeds host paths. Both therefore appear
# only in EXPORT_DIV_DIAG lines and as equality booleans. Nested engine output is
# never echoed; host paths are never pinned (the r102 export_launch evidence rule).
#
# Measured laws (hand probes + fixture runs 2026-10-18, godot
# 4.7.2.stable.arch_linux.ed1daf0bf, load 1.8-7.9, under /var/tmp/r103c-E5):
#   - default/unset and explicit `=true` both export .tscn/.tres as binary
#     (.godot/exported/<id>/export-<md5>-main.scn + -notes.res, 3 `.remap`
#     entries, 9 entries, hand-probe pack sha 3390d9a1…);
#   - explicit `=false` ships `main.tscn` (149 B) + `notes.tres` (71 B) as text;
#     only the script still compiles and remaps (`main.gdc` + `main.gd.remap`),
#     so a text pack is 7 entries with 1 `.remap`;
#   - override.cfg: the export run ignores it both ways (silent project +
#     override false -> still binary; explicit false + override true -> still
#     text), the runtime honors it both ways (false/true respectively), and it
#     never appears among pack entries;
#   - corrupt store -> exit 0, `ERROR: Could not load editor settings from
#     path: <cfg>/godot/editor_settings-4.7.tres` (preceded by the resource
#     Parse Error / Failed loading resource pair), store healed to the default
#     17728 B with the pre-corruption sha256, pack unchanged;
#   - crafted valid store -> pack unchanged and store NOT rewritten;
#   - pack-equality checks always compare two packs from the SAME root, so the
#     path seeding above cancels out; reports/round-103/mutations/r103-E5-mutants.py
#     proves every arm's checks bite (3/3 mutants fail with the predicted reason).
#
# Scratch: <root>/div_s05/{proj,out,logs,cfgA,cfgB,cfgC}, <root> = first
# writable of $EXPORT_DIV_ROOT, $EXPORT_LAUNCH_ROOT, <engine user-data dir>,
# $TMPDIR, then /tmp (4096-byte write+readback probe; user-data preferred over
# $TMPDIR//tmp on purpose — /tmp carries EDQUOT here and the packer's fixed
# tmpproject.binary temp runs under unshare+tmpfs 64M when available).
#
# Battery launch shape (8 s fixture bound):
#   godot --headless --path <scratch proj> --script res://export_div_s05.gd -- --arm=<arm>

const VARIANT := "div_s05"
const PRESET := "Pack"
const QUIT_AFTER := 3
const RUN_BOUND := 5
const TIMEOUT_PATH := "/usr/bin/timeout"
const CTB_KEY := "editor/export/convert_text_resources_to_binary"
const MARKER := "/nonexistent/s05-marker"
const MARKER_KEY := "filesystem/external_programs/terminal_emulator"
const MARK_READ := "DIV_S05_CTB "
const GARBAGE := "S05_CORRUPT_NOT_A_TRES\n"
const CLASS_LOAD := "Could not load editor settings from path: "
const CLASS_PARSE := "Parse Error: Expected '['."
const CLASS_RES := "Failed loading resource: "

const CHILD_HEAD := "config_version=5\n\n[application]\nconfig/name=\"ExportDivS05\"\nrun/main_scene=\"res://main.tscn\"\nconfig/features=PackedStringArray(\"4.7\")\n\n[display]\nwindow/size/viewport_width=320\nwindow/size/viewport_height=180\n"
const CHILD_FALSE := "\n[editor]\n\nexport/convert_text_resources_to_binary=false\n"
const CHILD_OVERRIDE := "\n[editor]\n\nexport/convert_text_resources_to_binary=true\n"
const CHILD_PRESETS := "[preset.0]\nname=\"Pack\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\ninclude_filter=\"\"\nexclude_filter=\"\"\nexport_path=\"\"\n\n[preset.0.options]\nbinary_format/architecture=\"x86_64\"\nbinary_format/embed_pck=true\n"
const CHILD_MAIN := "extends Node\n\nfunc _ready() -> void:\n\tprint(\"DIV_S05_CTB %s\" % str(ProjectSettings.get_setting(\"editor/export/convert_text_resources_to_binary\", \"unset\")))\n\tget_tree().quit(0)\n"
const CHILD_TSCN := "[gd_scene load_steps=2 format=3]\n\n[ext_resource type=\"Script\" path=\"res://main.gd\" id=\"1\"]\n\n[node name=\"Main\" type=\"Node\"]\nscript = ExtResource(\"1\")\n"
const CHILD_TRES := "[gd_resource type=\"Resource\" format=3]\n\n[resource]\nresource_name=\"s05\"\n"

var arm := ""
var _root := ""
var _unshare := false


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	if arm == "":
		arm = "store"
	call_deferred("_run")


func _run() -> void:
	_root = _pick_root()
	_diag("root", _root)
	if _root == "":
		_fail("no_writable_scratch_root")
		return
	if not _template_exists():
		_fail("template_binary_not_found")
		return
	_unshare = _probe_unshare()
	_diag("userns_tmp_isolation", _unshare)
	match arm:
		"store":
			_arm_store()
		"heal":
			_arm_heal()
		"ctb":
			_arm_ctb()
		_:
			_fail("unknown_arm")


# ------------------------------------------------------------------ receipts

func _fail(reason: String) -> void:
	print("FAIL export_div s05 arm=%s reason=%s" % [arm, reason])
	quit(1)


func _verdict(fields: PackedStringArray, bad: String) -> void:
	if bad == "":
		print("PASS export_div s05 arm=%s %s" % [arm, " ".join(fields)])
		quit(0)
	else:
		print("FAIL export_div s05 arm=%s reason=%s %s" % [arm, bad, " ".join(fields)])
		quit(1)


func _diag(key: String, value) -> void:
	print("EXPORT_DIV_DIAG %s %s=%s" % [arm, key, str(value)])


# ------------------------------------------------------------------- scratch

func _pick_root() -> String:
	var candidates: PackedStringArray = []
	if OS.get_environment("EXPORT_DIV_ROOT") != "":
		candidates.append(OS.get_environment("EXPORT_DIV_ROOT"))
	if OS.get_environment("EXPORT_LAUNCH_ROOT") != "":
		candidates.append(OS.get_environment("EXPORT_LAUNCH_ROOT"))
	candidates.append(OS.get_user_data_dir().path_join("export_div_s05"))
	if OS.get_environment("TMPDIR") != "":
		candidates.append(OS.get_environment("TMPDIR").path_join("export_div_s05"))
	candidates.append("/tmp/export_div_s05")
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


func _vdir() -> String:
	return _root.path_join(VARIANT)


func _out_dir() -> String:
	return _vdir().path_join("out")


func _log_path(name: String) -> String:
	return _vdir().path_join("logs").path_join(name + ".log")


func _mkdir(path: String) -> bool:
	if DirAccess.dir_exists_absolute(path):
		return true
	var err := DirAccess.make_dir_recursive_absolute(path)
	if err != OK:
		_fail("mkdir_failed:%s:%d" % [path, err])
		return false
	return true


func _wipe_dir(dir: String) -> void:
	if not DirAccess.dir_exists_absolute(dir):
		return
	for d in DirAccess.get_directories_at(dir):
		_wipe_dir(dir.path_join(d))
	for f in DirAccess.get_files_at(dir):
		DirAccess.remove_absolute(dir.path_join(f))
	DirAccess.remove_absolute(dir)


func _write_text(path: String, text: String) -> bool:
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		_fail("write_failed:" + path)
		return false
	f.store_string(text)
	f.close()
	return true


func _read_text(path: String) -> String:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return "<missing>"
	var s := f.get_as_text()
	f.close()
	return s


func _size_of(path: String) -> int:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return -1
	var n := f.get_length()
	f.close()
	return n


func _sha_of(path: String) -> String:
	if not FileAccess.file_exists(path):
		return ""
	return FileAccess.get_sha256(path)


func _run_logged(body: String, log_path: String, isolate := false) -> int:
	_mkdir(log_path.get_base_dir())
	var script := body
	if isolate and _unshare:
		# Private /tmp for the packer's fixed tmpproject.binary temp (r101-E0).
		script = "mount -t tmpfs -o size=64M tmpfs /tmp || exit 97\n" + body
		script = "unshare -m --map-root-user /usr/bin/sh -c " + _q(script)
	_diag("nested", body.replace("\n", " ; "))
	return OS.execute("/usr/bin/sh", PackedStringArray(["-c", "exec > " + _q(log_path) + " 2>&1\n" + script]))


func _template_exists() -> bool:
	var v := Engine.get_version_info()
	var ver := "%d.%d.%d.%s" % [v["major"], v["minor"], v["patch"], v["status"]]
	var candidates: PackedStringArray = []
	if OS.get_environment("XDG_DATA_HOME") != "":
		candidates.append(OS.get_environment("XDG_DATA_HOME").path_join("godot/export_templates").path_join(ver).path_join("linux_release.x86_64"))
	if OS.get_environment("HOME") != "":
		candidates.append(OS.get_environment("HOME").path_join(".local/share/godot/export_templates").path_join(ver).path_join("linux_release.x86_64"))
	candidates.append("/usr/local/share/godot/export_templates/%s/linux_release.x86_64" % ver)
	candidates.append("/usr/share/godot/export_templates/%s/linux_release.x86_64" % ver)
	for c in candidates:
		if FileAccess.file_exists(c):
			return true
	return false


func _store_name() -> String:
	var v := Engine.get_version_info()
	return "editor_settings-%d.%d.tres" % [v["major"], v["minor"]]


func _store_path(cfg_root: String) -> String:
	return cfg_root.path_join("godot").path_join(_store_name())


# --------------------------------------------------------------- pack census

func _pack_names(path: String) -> PackedStringArray:
	var names := PackedStringArray()
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return names
	var head := f.get_buffer(0x28)
	if head.size() < 0x28 or head.slice(0, 4).get_string_from_ascii() != "GDPC":
		return names
	var dir_off := head.decode_u64(0x20)
	if dir_off <= 0 or dir_off >= f.get_length():
		return names
	f.seek(dir_off)
	var count := f.get_32()
	for i in count:
		if f.get_position() + 4 > f.get_length():
			break
		var nlen := f.get_32()
		var raw := f.get_buffer(nlen)
		var cut := raw.size()
		for b in raw.size():
			if raw[b] == 0:
				cut = b
				break
		names.append(raw.slice(0, cut).get_string_from_utf8())
		f.seek(f.get_position() + 8 + 8 + 16 + 4)
	f.close()
	return names


func _classify(names: PackedStringArray) -> Dictionary:
	var scen := "none"
	var res := "none"
	var remaps := 0
	for n in names:
		if n == "main.tscn":
			scen = "text"
		elif n.ends_with("-main.scn"):
			scen = "bin"
		if n == "notes.tres":
			res = "text"
		elif n.ends_with("-notes.res"):
			res = "bin"
		if n.ends_with(".remap"):
			remaps += 1
	return {"entries": names.size(), "scen": scen, "res": res, "remaps": remaps}


func _class_fields(c: Dictionary) -> PackedStringArray:
	return PackedStringArray(["entries=%d" % c["entries"], "scen=%s" % c["scen"], "res=%s" % c["res"], "remaps=%d" % c["remaps"]])


# ------------------------------------------------------------------ children

func _build_project(explicit_false: bool) -> bool:
	var proj := _vdir().path_join("proj")
	if not _mkdir(proj) or not _mkdir(_out_dir()) or not _mkdir(_vdir().path_join("logs")):
		return false
	var text: String = CHILD_HEAD
	if explicit_false:
		text += CHILD_FALSE
	_write_text(proj.path_join("project.godot"), text)
	_write_text(proj.path_join("export_presets.cfg"), CHILD_PRESETS)
	_write_text(proj.path_join("main.gd"), CHILD_MAIN)
	_write_text(proj.path_join("main.tscn"), CHILD_TSCN)
	_write_text(proj.path_join("notes.tres"), CHILD_TRES)
	return true


func _export(pack: String, cfg_root: String, log_name: String) -> int:
	var proj := _vdir().path_join("proj")
	if FileAccess.file_exists(pack):
		DirAccess.remove_absolute(pack)
	var body := "cd " + _q(proj) + "\nenv XDG_CONFIG_HOME=" + _q(cfg_root) + " " + _q(_godot()) + " --headless --path " + _q(proj) + " --export-pack " + _q(PRESET) + " " + _q(pack)
	return _run_logged(body, _log_path(log_name), true)


func _source_run(cfg_root: String, log_name: String) -> Dictionary:
	var proj := _vdir().path_join("proj")
	var bound := ""
	if FileAccess.file_exists(TIMEOUT_PATH):
		bound = TIMEOUT_PATH + " -k 1 %d " % RUN_BOUND
	var body := "cd " + _q(proj) + "\nenv XDG_CONFIG_HOME=" + _q(cfg_root) + " " + bound + _q(_godot()) + " --headless --path " + _q(proj) + " --quit-after %d" % QUIT_AFTER
	var code := _run_logged(body, _log_path(log_name))
	return {"exit": code, "text": FileAccess.get_file_as_string(_log_path(log_name))}


func _ctb_of(text: String) -> String:
	for l in text.split("\n"):
		if l.begins_with(MARK_READ):
			return l.substr(MARK_READ.length()).strip_edges()
	return ""


func _log_has(path: String, needle: String) -> bool:
	return FileAccess.get_file_as_string(path).contains(needle)


# ---------------------------------------------------------------------- arms

func _arm_store() -> void:
	_wipe_dir(_vdir())
	if not _build_project(false):
		return
	var cfg := _vdir().path_join("cfgA")
	if not _mkdir(cfg):
		return
	var fields := PackedStringArray()
	var pack_a := _out_dir().path_join("store_a.pck")
	var code_a := _export(pack_a, cfg, "store_export_a")
	if code_a != 0 or not FileAccess.file_exists(pack_a):
		_verdict(fields, "export_a_failed:%d" % code_a)
		return
	var store := _store_path(cfg)
	if not FileAccess.file_exists(store):
		_verdict(fields, "store_not_created_by_export")
		return
	var bytes_default := _size_of(store)
	var sha_default := _sha_of(store)
	_diag("store_default", "%s bytes=%d" % [sha_default, bytes_default])
	fields.append("store_created=true")
	fields.append("store_bytes_nonzero=%s" % (bytes_default > 0))
	if not _craft_marker(store):
		_verdict(fields, "marker_craft_failed")
		return
	var sha_marked := _sha_of(store)
	var bytes_marked := _size_of(store)
	fields.append("marker_applied=%s" % (sha_marked != "" and sha_marked != sha_default))
	if sha_marked == "" or sha_marked == sha_default:
		_verdict(fields, "marker_not_applied")
		return
	var pack_b := _out_dir().path_join("store_b.pck")
	var code_b := _export(pack_b, cfg, "store_export_b")
	if code_b != 0 or not FileAccess.file_exists(pack_b):
		_verdict(fields, "export_b_failed:%d" % code_b)
		return
	var sha_a := _sha_of(pack_a)
	var sha_b := _sha_of(pack_b)
	if sha_a == "" or sha_b == "":
		_verdict(fields, "pack_sha_unavailable")
		return
	var class_a := _classify(_pack_names(pack_a))
	var class_b := _classify(_pack_names(pack_b))
	var marked_now := _size_of(store) == bytes_marked and _sha_of(store) == sha_marked
	_diag("pack_sha256_b", sha_b)
	fields.append_array(_class_fields(class_b))
	fields.append("pack_eq=%s" % (sha_a == sha_b))
	fields.append("store_untouched=%s" % marked_now)
	fields.append("marker_kept=%s" % FileAccess.get_file_as_string(store).contains(MARKER))
	var bad := ""
	if sha_a != sha_b:
		bad = "crafted_store_changed_pack:[%s!=%s]" % [sha_a.substr(0, 12), sha_b.substr(0, 12)]
	elif not marked_now:
		bad = "store_rewritten_by_export"
	elif not FileAccess.get_file_as_string(store).contains(MARKER):
		bad = "marker_lost"
	elif class_a["scen"] != class_b["scen"] or class_a["res"] != class_b["res"]:
		bad = "pack_class_drift"
	_verdict(fields, bad)


func _arm_heal() -> void:
	_wipe_dir(_vdir())
	if not _build_project(false):
		return
	var cfg := _vdir().path_join("cfgB")
	if not _mkdir(cfg):
		return
	var fields := PackedStringArray()
	var pack_0 := _out_dir().path_join("heal_0.pck")
	var code_0 := _export(pack_0, cfg, "heal_export_0")
	if code_0 != 0 or not FileAccess.file_exists(pack_0):
		_verdict(fields, "export_0_failed:%d" % code_0)
		return
	var store := _store_path(cfg)
	if not FileAccess.file_exists(store):
		_verdict(fields, "store_not_created_by_export")
		return
	var bytes_default := _size_of(store)
	var sha_default := _sha_of(store)
	_diag("store_default", "%s bytes=%d" % [sha_default, bytes_default])
	fields.append("default_store_bytes=%d" % bytes_default)
	if not _write_text(store, GARBAGE):
		return
	_diag("corrupted_store", "%s bytes=%d" % [_sha_of(store), _size_of(store)])
	var pack_1 := _out_dir().path_join("heal_1.pck")
	var code_1 := _export(pack_1, cfg, "heal_export_1")
	fields.append("corrupt_export_exit=%d" % code_1)
	if code_1 != 0 or not FileAccess.file_exists(pack_1):
		_verdict(fields, "export_1_failed_after_corrupt_store:%d" % code_1)
		return
	var log_path := _log_path("heal_export_1")
	var class_ok := _log_has(log_path, CLASS_LOAD) and _log_has(log_path, CLASS_PARSE) and _log_has(log_path, CLASS_RES) and _log_has(log_path, store)
	fields.append("refusal_class_ok=%s" % class_ok)
	var healed_bytes := _size_of(store)
	var healed_sha := _sha_of(store)
	var healed := healed_bytes == bytes_default and healed_sha == sha_default
	fields.append("heal_eq_default=%s" % healed)
	fields.append("heal_bytes=%d" % healed_bytes)
	var sha_0 := _sha_of(pack_0)
	var sha_1 := _sha_of(pack_1)
	if sha_0 == "" or sha_1 == "":
		_verdict(fields, "pack_sha_unavailable")
		return
	var class_1 := _classify(_pack_names(pack_1))
	_diag("pack_sha256_1", sha_1)
	fields.append_array(_class_fields(class_1))
	fields.append("pack_eq=%s" % (sha_0 == sha_1))
	var bad := ""
	if not class_ok:
		bad = "refusal_class_missing_in_log"
	elif not healed:
		bad = "store_not_healed:[%d,%s]" % [healed_bytes, healed_sha.substr(0, 12)]
	elif sha_0 != sha_1:
		bad = "corrupt_store_changed_pack:[%s!=%s]" % [sha_0.substr(0, 12), sha_1.substr(0, 12)]
	_verdict(fields, bad)


func _arm_ctb() -> void:
	_wipe_dir(_vdir())
	if not _build_project(true):
		return
	var cfg := _vdir().path_join("cfgC")
	if not _mkdir(cfg):
		return
	var fields := PackedStringArray()
	var pack_t := _out_dir().path_join("ctb_text.pck")
	var code_t := _export(pack_t, cfg, "ctb_export_text")
	if code_t != 0 or not FileAccess.file_exists(pack_t):
		_verdict(fields, "export_text_failed:%d" % code_t)
		return
	var names_t := _pack_names(pack_t)
	var class_t := _classify(names_t)
	fields.append_array(_class_fields(class_t))
	fields.append("no_ovr_scen=%s" % class_t["scen"])
	fields.append("script_compiled=%s" % names_t.has("main.gdc"))
	var proj := _vdir().path_join("proj")
	if not _write_text(proj.path_join("override.cfg"), CHILD_OVERRIDE):
		return
	var pack_o := _out_dir().path_join("ctb_ovr.pck")
	var code_o := _export(pack_o, cfg, "ctb_export_ovr")
	if code_o != 0 or not FileAccess.file_exists(pack_o):
		_verdict(fields, "export_ovr_failed:%d" % code_o)
		return
	var names_o := _pack_names(pack_o)
	var class_o := _classify(names_o)
	fields.append("ovr_scen=%s" % class_o["scen"])
	fields.append("ovr_res=%s" % class_o["res"])
	fields.append("ovr_cfg_packed=%s" % names_o.has("override.cfg"))
	var sha_t := _sha_of(pack_t)
	var sha_o := _sha_of(pack_o)
	if sha_t == "" or sha_o == "":
		_verdict(fields, "pack_sha_unavailable")
		return
	_diag("pack_sha256_ovr", sha_o)
	fields.append("pack_eq=%s" % (sha_t == sha_o))
	var source := _source_run(cfg, "ctb_source_run")
	var ctb := _ctb_of(source["text"])
	fields.append("runtime_exit=%d" % source["exit"])
	fields.append("runtime_ctb=%s" % (ctb if ctb != "" else "<missing>"))
	var bad := ""
	if class_t["scen"] != "text" or class_t["res"] != "text":
		bad = "explicit_false_not_text_pack:[%s,%s]" % [class_t["scen"], class_t["res"]]
	elif not names_t.has("main.gdc"):
		bad = "script_not_compiled_when_ctb_false"
	elif sha_t != sha_o:
		bad = "override_cfg_changed_export_pack:[%s!=%s]" % [sha_t.substr(0, 12), sha_o.substr(0, 12)]
	elif names_o.has("override.cfg"):
		bad = "override_cfg_packed"
	elif source["exit"] != 0:
		bad = "runtime_exit:%d" % source["exit"]
	elif ctb != "true":
		bad = "runtime_override_not_honored:[%s]" % ctb
	_verdict(fields, bad)


# ------------------------------------------------------------------- helpers

func _craft_marker(store: String) -> bool:
	var text := _read_text(store)
	var key := MARKER_KEY + " = "
	var marker_line := MARKER_KEY + " = \"" + MARKER + "\""
	if text.contains(key):
		var lines := text.split("\n")
		for i in lines.size():
			if lines[i].begins_with(key):
				lines[i] = marker_line
				return _write_text(store, "\n".join(lines))
		return false
	var anchor := "[resource]"
	var idx := text.find(anchor)
	if idx < 0:
		return false
	var at := idx + anchor.length()
	return _write_text(store, text.substr(0, at) + "\ns05_marker = \"" + MARKER + "\"" + text.substr(at))
