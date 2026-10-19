extends SceneTree
# export_div_s02 — r103 C1: exported-project `user://` isolation (seat E2).
#
# Scenario: export the child project as a self-contained Linux/X11 binary
# (embed_pck=true — the same embedded template build the r102 launch matrix
# pinned), then run THAT binary under controlled XDG_DATA_HOME / HOME pairs
# and read back its user:// store from the harness side.
#
#   arm=iso  (row export_div_s02_user_iso)
#     run1  XDG_DATA_HOME=xdgA HOME=homeA -> child prints prior=<none> (fresh
#           store), writes user://div_s02_state.txt, exits 0; harness reads the
#           store back and demands exactly `run1`.
#     run2  same env -> child prints prior=run1 (persistence visible to a
#           second process); store ends exactly `run1,run2`.
#     isolation sentinel: with XDG_DATA_HOME set, nothing may appear under
#           homeA/.local (a build that consulted HOME would have written there).
#
#   arm=xdg  (row export_div_s02_xdg_override)
#     run3  XDG_DATA_HOME=xdgB HOME=homeA -> fresh store `run3` under xdgB
#           with the child's own printed user dir resolving under xdgB: a
#           different XDG_DATA_HOME is a different user dir (override honored),
#           while homeA — the dir a XDG-ignoring build uses — stays ignored.
#     run4  XDG_DATA_HOME unset (env -u), HOME=homeC -> prior=<none>, store
#           `run4` under homeC/.local/share/godot/app_userdata/<name>/ (the
#           default resolution law, the counterpart of the override).
#     The arm reuses <root>/div_s02/out/div_s02.x86_64 from arm=iso when
#     present (adjacent-row pattern, cf. r102 export_launch_s02 neg) and
#     exports its own otherwise, so it also passes standalone.
#
# Child receipt lines (verbatim, parsed by the harness):
#   DIV_S02_USERDIR <globalized user:// path>  (absolute, with trailing '/')
#   DIV_S02_READ prior=<none|comma-joined run tags>
#   DIV_S02_WRITE ok=<bool>
# PASS lines carry only derived booleans, literals and store contents; host
# paths appear only in EXPORT_DIV_DIAG lines and in the unpinned trailing
# `proj=` field (same evidence rule as the r102 export_launch family: nested
# engine output is never echoed).
#
# Measured laws, hand probe 2026-10-18 on godot 4.7.2.stable.arch_linux.ed1daf0bf
# (load 3.3): exported binary resolves user:// to
#   $XDG_DATA_HOME/godot/app_userdata/<config name>/   when XDG is set,
#   $HOME/.local/share/godot/app_userdata/<config name>/ otherwise;
# run2 prior=run1 (persistence); a second XDG root starts empty; with XDG set
# nothing was created under HOME. Export ~1.9 s, child boot ~0.9 s.
#
# Scratch: <root>/div_s02/{proj,out,logs,xdgA,homeA,xdgB,homeC}, <root> = first
# writable of $EXPORT_DIV_ROOT, $EXPORT_LAUNCH_ROOT, <engine user-data dir>,
# $TMPDIR, then /tmp (4096-byte write+readback probe). User-data is preferred
# over $TMPDIR//tmp on purpose: the export runs under unshare+tmpfs /tmp
# (r101-E0 EDQUOT mitigation for the packer's fixed tmpproject.binary temp), and
# if the export TARGET lived under that tmpfs the ~73 MB artifact could exceed
# the 64 MB mount. Nested engine output is redirected to logs only.
#
# Battery launch shape (8 s fixture bound):
#   godot --headless --path <scratch proj> --script res://export_div_s02.gd -- --arm=<arm>

const VARIANT := "div_s02"
const PRESET := "Embed"
const TEMPLATE := "linux_release.x86_64"
const QUIT_AFTER := 3
const RUN_BOUND := 5
const TIMEOUT_PATH := "/usr/bin/timeout"
const STORE := "div_s02_state.txt"
const TAG_R1 := "run1"
const TAG_R2 := "run2"
const TAG_R3 := "run3"
const TAG_R4 := "run4"
const NONE := "<none>"
const MARK_USERDIR := "DIV_S02_USERDIR "
const MARK_READ := "DIV_S02_READ prior="
const MARK_WRITE := "DIV_S02_WRITE ok="

const CHILD_PROJECT := "config_version=5\n\n[application]\nconfig/name=\"ExportDivS02\"\nrun/main_scene=\"res://main.tscn\"\nconfig/features=PackedStringArray(\"4.7\")\n\n[display]\nwindow/size/viewport_width=320\nwindow/size/viewport_height=180\n"
const CHILD_PRESETS := "[preset.0]\nname=\"Embed\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\ninclude_filter=\"\"\nexclude_filter=\"\"\nexport_path=\"\"\n\n[preset.0.options]\nbinary_format/architecture=\"x86_64\"\nbinary_format/embed_pck=true\n"
const CHILD_MAIN := "extends Node\n\nfunc _ready() -> void:\n\tvar tag := \"run?\"\n\tfor a in OS.get_cmdline_user_args():\n\t\tif a.begins_with(\"--tag=\"):\n\t\t\ttag = a.substr(6)\n\tprint(\"DIV_S02_USERDIR %s\" % ProjectSettings.globalize_path(\"user://\"))\n\tvar store := \"user://div_s02_state.txt\"\n\tvar prior := \"<none>\"\n\tvar r := FileAccess.open(store, FileAccess.READ)\n\tif r != null:\n\t\tprior = r.get_as_text().strip_edges().replace(\"\\n\", \",\")\n\t\tr.close()\n\tprint(\"DIV_S02_READ prior=%s\" % prior)\n\tvar w := FileAccess.open(store, FileAccess.WRITE)\n\tif w == null:\n\t\tprint(\"DIV_S02_WRITE ok=false\")\n\t\tget_tree().quit(1)\n\t\treturn\n\tvar next := tag if prior == \"<none>\" else prior + \",\" + tag\n\tw.store_string(next)\n\tw.close()\n\tprint(\"DIV_S02_WRITE ok=%s\" % FileAccess.file_exists(store))\n\tget_tree().quit(0)\n"
const CHILD_TSCN := "[gd_scene load_steps=2 format=3]\n\n[ext_resource type=\"Script\" path=\"res://main.gd\" id=\"1\"]\n\n[node name=\"Main\" type=\"Node\"]\nscript = ExtResource(\"1\")\n"

var arm := ""
var _root := ""
var _unshare := false


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	if arm == "":
		arm = "iso"
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
		"iso":
			_arm_iso()
		"xdg":
			_arm_xdg()
		_:
			_fail("unknown_arm")


# ------------------------------------------------------------------ receipts

func _fail(reason: String) -> void:
	print("FAIL export_div s02 arm=%s reason=%s" % [arm, reason])
	quit(1)


func _verdict(fields: PackedStringArray, bad: String) -> void:
	if bad == "":
		print("PASS export_div s02 arm=%s %s" % [arm, " ".join(fields)])
		quit(0)
	else:
		print("FAIL export_div s02 arm=%s reason=%s %s" % [arm, bad, " ".join(fields)])
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
	candidates.append(OS.get_user_data_dir().path_join("export_div_s02"))
	if OS.get_environment("TMPDIR") != "":
		candidates.append(OS.get_environment("TMPDIR").path_join("export_div_s02"))
	candidates.append("/tmp/export_div_s02")
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
	# Instance listing with include_hidden: the static *_at getters and the
	# default instance listing both skip dot-entries (measured 2026-10-18 on
	# godot 4.7.2: get_directories_at returns [] for a dir holding only
	# `.hid`, while include_hidden=true returns [".hid"]). homeC is wiped on
	# every xdg-arm run and its payload lives under homeC/.local, so without
	# this the second run on the same root sees prior=run4 and FAILs
	# run4_read_not_none (r103-E2 validation, receipts in r103-E2.md).
	var d := DirAccess.open(dir)
	if d == null:
		return
	d.include_hidden = true
	for sub in d.get_directories():
		_wipe_dir(dir.path_join(sub))
	for f in d.get_files():
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


func _run_logged(body: String, log_path: String, isolate := false) -> int:
	_mkdir(log_path.get_base_dir())
	var script := body
	if isolate and _unshare:
		# Private /tmp for the packer's fixed tmpproject.binary temp path.
		script = "mount -t tmpfs -o size=64M tmpfs /tmp || exit 97\n" + body
		script = "unshare -m --map-root-user /usr/bin/sh -c " + _q(script)
	_diag("nested", body.replace("\n", " ; "))
	return OS.execute("/usr/bin/sh", PackedStringArray(["-c", "exec > " + _q(log_path) + " 2>&1\n" + script]))


func _template_exists() -> bool:
	var v := Engine.get_version_info()
	var ver := "%d.%d.%d.%s" % [v["major"], v["minor"], v["patch"], v["status"]]
	var candidates: PackedStringArray = []
	if OS.get_environment("XDG_DATA_HOME") != "":
		candidates.append(OS.get_environment("XDG_DATA_HOME").path_join("godot/export_templates").path_join(ver).path_join(TEMPLATE))
	if OS.get_environment("HOME") != "":
		candidates.append(OS.get_environment("HOME").path_join(".local/share/godot/export_templates").path_join(ver).path_join(TEMPLATE))
	candidates.append("/usr/local/share/godot/export_templates/%s/%s" % [ver, TEMPLATE])
	candidates.append("/usr/share/godot/export_templates/%s/%s" % [ver, TEMPLATE])
	for c in candidates:
		if FileAccess.file_exists(c):
			return true
	return false


# ------------------------------------------------------------------ children

func _build_child_project() -> bool:
	var proj := _vdir().path_join("proj")
	if not _mkdir(proj) or not _mkdir(_out_dir()) or not _mkdir(_vdir().path_join("logs")):
		return false
	_write_text(proj.path_join("project.godot"), CHILD_PROJECT)
	_write_text(proj.path_join("export_presets.cfg"), CHILD_PRESETS)
	_write_text(proj.path_join("main.gd"), CHILD_MAIN)
	_write_text(proj.path_join("main.tscn"), CHILD_TSCN)
	return true


func _export(bin: String) -> int:
	var proj := _vdir().path_join("proj")
	if FileAccess.file_exists(bin):
		DirAccess.remove_absolute(bin)
	var body := "cd " + _q(proj) + "\n" + _q(_godot()) + " --headless --path " + _q(proj) + " --export-release " + _q(PRESET) + " " + _q(bin)
	return _run_logged(body, _log_path("export"), true)


func _run_child(bin: String, log_name: String, env_prefix: String, tag: String) -> Dictionary:
	var log_path := _log_path(log_name)
	var bound := ""
	if FileAccess.file_exists(TIMEOUT_PATH):
		bound = TIMEOUT_PATH + " -k 1 %d " % RUN_BOUND
	var body := env_prefix + bound + _q(bin) + " --headless --quit-after %d -- --tag=%s" % [QUIT_AFTER, tag]
	var code := _run_logged(body, log_path)
	return {"exit": code, "text": FileAccess.get_file_as_string(log_path)}


func _userdir_of(text: String) -> String:
	var line := ""
	for l in text.split("\n"):
		if l.begins_with(MARK_USERDIR):
			line = l.substr(MARK_USERDIR.length()).strip_edges()
			break
	while line.ends_with("/"):
		line = line.substr(0, line.length() - 1)
	return line


func _prior_of(text: String) -> String:
	for l in text.split("\n"):
		if l.begins_with(MARK_READ):
			return l.substr(MARK_READ.length()).strip_edges()
	return ""


func _write_ok(text: String) -> bool:
	for l in text.split("\n"):
		if l.begins_with(MARK_WRITE):
			return l.substr(MARK_WRITE.length()).strip_edges() == "true"
	return false


func _disp(prior: String) -> String:
	return "none" if prior == NONE else prior


# ---------------------------------------------------------------------- arms

func _arm_iso() -> void:
	_wipe_dir(_vdir())
	if not _build_child_project():
		return
	var bin := _out_dir().path_join("div_s02.x86_64")
	var code := _export(bin)
	if code != 0 or not FileAccess.file_exists(bin):
		_fail("export_failed:%d" % code)
		return
	var xdg_a := _vdir().path_join("xdgA")
	var home_a := _vdir().path_join("homeA")
	if not _mkdir(xdg_a) or not _mkdir(home_a):
		return
	var env_a := "env XDG_DATA_HOME=" + _q(xdg_a) + " HOME=" + _q(home_a) + " "
	var fields := PackedStringArray()
	var r1 := _run_child(bin, "iso_run1", env_a, TAG_R1)
	if r1["exit"] != 0:
		_verdict(fields, "run1_exit:%d" % r1["exit"])
		return
	var udir1 := _userdir_of(r1["text"])
	if udir1 == "":
		_verdict(fields, "run1_userdir_line_missing")
		return
	var prior1 := _prior_of(r1["text"])
	fields.append("r1_read=%s" % _disp(prior1))
	fields.append("r1_exit=0")
	if not _write_ok(r1["text"]):
		_verdict(fields, "run1_write_not_ok")
		return
	var store := udir1.path_join(STORE)
	var after1 := _read_text(store)
	if after1 != TAG_R1:
		_verdict(fields, "store_after_run1_not_run1:[%s]" % after1)
		return
	var r2 := _run_child(bin, "iso_run2", env_a, TAG_R2)
	if r2["exit"] != 0:
		_verdict(fields, "run2_exit:%d" % r2["exit"])
		return
	var prior2 := _prior_of(r2["text"])
	fields.append("r2_read=%s" % _disp(prior2))
	fields.append("r2_exit=0")
	var final_store := _read_text(store)
	var home_local := DirAccess.dir_exists_absolute(home_a.path_join(".local"))
	fields.append("store=[%s]" % final_store)
	fields.append("store_under_xdg=%s" % store.begins_with(xdg_a))
	fields.append("userdir_under_xdg=%s" % udir1.begins_with(xdg_a))
	fields.append("home_store_absent=%s" % (not home_local))
	fields.append("proj=" + _vdir().path_join("proj"))
	var bad := ""
	if prior1 != NONE:
		bad = "run1_read_not_none:[%s]" % prior1
	elif prior2 != TAG_R1:
		bad = "persistence_missing:[%s]" % prior2
	elif final_store != "run1,run2":
		bad = "store_final_mismatch:[%s]" % final_store
	elif not store.begins_with(xdg_a):
		bad = "store_outside_xdg"
	elif not udir1.begins_with(xdg_a):
		bad = "userdir_not_under_xdg:[%s]" % udir1
	elif home_local:
		bad = "home_fallback_used"
	_verdict(fields, bad)


func _arm_xdg() -> void:
	if not _mkdir(_vdir()):
		return
	if not _build_child_project():
		return
	var bin := _out_dir().path_join("div_s02.x86_64")
	if not FileAccess.file_exists(bin):
		var code := _export(bin)
		if code != 0 or not FileAccess.file_exists(bin):
			_fail("export_failed:%d" % code)
			return
	else:
		_diag("reuse_binary", true)
	var xdg_b := _vdir().path_join("xdgB")
	var home_a := _vdir().path_join("homeA")
	var home_c := _vdir().path_join("homeC")
	_wipe_dir(xdg_b)
	_wipe_dir(home_c)
	if not _mkdir(xdg_b) or not _mkdir(home_c):
		return
	var fields := PackedStringArray()
	var env_b := "env XDG_DATA_HOME=" + _q(xdg_b) + " HOME=" + _q(home_a) + " "
	var r3 := _run_child(bin, "xdg_run3", env_b, TAG_R3)
	if r3["exit"] != 0:
		_verdict(fields, "run3_exit:%d" % r3["exit"])
		return
	var udir3 := _userdir_of(r3["text"])
	if udir3 == "":
		_verdict(fields, "run3_userdir_line_missing")
		return
	var prior3 := _prior_of(r3["text"])
	var store_b := udir3.path_join(STORE)
	var s_b := _read_text(store_b)
	fields.append("r3_read=%s" % _disp(prior3))
	fields.append("r3_exit=0")
	fields.append("store_b=[%s]" % s_b)
	fields.append("store_b_under_xdg=%s" % store_b.begins_with(xdg_b))
	fields.append("r3_userdir_under_xdg=%s" % udir3.begins_with(xdg_b))
	var env_c := "env -u XDG_DATA_HOME HOME=" + _q(home_c) + " "
	var r4 := _run_child(bin, "xdg_run4", env_c, TAG_R4)
	if r4["exit"] != 0:
		_verdict(fields, "run4_exit:%d" % r4["exit"])
		return
	var udir4 := _userdir_of(r4["text"])
	if udir4 == "":
		_verdict(fields, "run4_userdir_line_missing")
		return
	var prior4 := _prior_of(r4["text"])
	var store_c := udir4.path_join(STORE)
	var s_c := _read_text(store_c)
	var home_local4 := home_c.path_join(".local")
	fields.append("r4_read=%s" % _disp(prior4))
	fields.append("r4_exit=0")
	fields.append("store_c=[%s]" % s_c)
	fields.append("r4_userdir_under_home=%s" % udir4.begins_with(home_local4))
	var store_a := _vdir().path_join("xdgA").path_join("godot/app_userdata/ExportDivS02").path_join(STORE)
	fields.append("xdg_a_store=[%s]" % _read_text(store_a))
	fields.append("proj=" + _vdir().path_join("proj"))
	var bad := ""
	if prior3 != NONE:
		bad = "run3_read_not_none:[%s]" % prior3
	elif s_b != TAG_R3:
		bad = "store_b_mismatch:[%s]" % s_b
	elif not store_b.begins_with(xdg_b):
		bad = "store_b_outside_xdg"
	elif not udir3.begins_with(xdg_b):
		bad = "run3_userdir_not_under_xdg:[%s]" % udir3
	elif prior4 != NONE:
		bad = "run4_read_not_none:[%s]" % prior4
	elif s_c != TAG_R4:
		bad = "store_c_mismatch:[%s]" % s_c
	elif not udir4.begins_with(home_local4):
		bad = "run4_userdir_not_under_home:[%s]" % udir4
	_verdict(fields, bad)
