extends SceneTree
# r101-E7 — export_prod scenario 07: unknown-preset refusal.
#
# All observations below were measured on this host with
# Godot 4.7.2.stable.arch_linux.ed1daf0bf, headless editor, real templates.
#
#   R1 unknown preset name -> exit 1; stderr is EXACTLY the 5+2*census-line template that
#      echoes the CLI token and the project's real preset census; no artifact; stdout shows
#      first_scan_filesystem but never savepack.
#   R2 lookup is case-sensitive: "linux/x11" refuses and echoes "linux/x11".
#   R3 "--export-release" with no preset argument echoes the editor default "--editor".
#   R4 unknown name + no path is byte-identical (stdout AND stderr) to unknown name + path:
#      name resolution precedes path validation.
#   R5 known name + no path is a DIFFERENT class ("doesn't have a default export path"),
#      also exit 1, still no artifact.
#   R6 empty preset name is NOT a refusal: the editor idles until the harness bound kills it
#      (rc=124 observed over both 40 s and 180 s bounds), stderr empty, no artifact.
#   R7 a preset literally named "NoSuchPreset" exports (exit 0, GDPC artifact), so the
#      refusal tracks preset presence, not the literal token.
#   R8 --export-debug and --export-pack refuse with the same template bytes as --export-release.
#   R9 a preset cfg missing include_filter/exclude_filter injects four schema ERROR lines
#      (core/io/config_file.cpp:60) before the refusal; exact matching must reject that.
#
# The row is forgery-resistant because acceptance is (rc, exact stderr bytes, absent artifact,
# stdout without savepack) against the reconstructed template, cross-checked with the preset
# census parsed from export_presets.cfg, and seven mutants must all be rejected.
#
# Run: godot --headless --path <scratch project> --script res://export_prod_s07.gd [-- --root=DIR]
# Scratch defaults to /tmp/r101-export-prod-s07 and falls back to /var/tmp (host /tmp is a
# quota-limited tmpfs; the probe row below records whichever scratch root was actually used).

const CENSUS_A := ["Linux/X11", "Alt/Thing"]
const REFUSAL_SHA := "a13d75810de09e6bbea890bb6db3ce149fe3cc687eed08289144c8ed17432123"
const PATH_ERR_SHA := "faead2109c9fc50c0b97158abc8d0b2b8cbe612ca8ff1d2c196b4e04a1ceee68"
const SPARSE_SHA := "d7ec2e5b5c7ea46aac940d251760e90c2a091700eacc7c5ab38a21074ec7e6fd"
const BOUND_S := 120
const EMPTY_BOUND_S := 40

var scratch := ""
var godot := ""
var out_dir := ""
var failures := PackedStringArray()
var arms := 0
var refusals := 0
var controls := 0
var mutants := 0
var mutant_rejects := 0

func _initialize() -> void:
	_run.call_deferred()

func _run() -> void:
	godot = OS.get_executable_path()
	scratch = _pick_root()
	if scratch == "":
		print("s07 ASSERTION FAILED: no writable scratch root")
		quit(2)
		return
	out_dir = scratch + "/out"
	if not scratch.begins_with("/tmp/") and not scratch.begins_with("/var/tmp/") and not scratch.begins_with("/home/"):
		print("s07 ASSERTION FAILED: refusing scratch root outside /tmp,/var/tmp,/home: %s" % scratch)
		quit(2)
		return
	if scratch.length() < 8:
		print("s07 ASSERTION FAILED: scratch root too short")
		quit(2)
		return
	# Stale artifacts from an earlier run must not be able to satisfy this run's checks.
	OS.execute("rm", ["-rf", out_dir], [], false, false)
	DirAccess.make_dir_recursive_absolute(out_dir)
	print("ROW s07 probe godot=%s root=%s timeout_bin=%s" % [
		str(Engine.get_version_info().get("string", "?")), scratch,
		str(FileAccess.file_exists("/usr/bin/timeout"))])

	var proj_a := scratch + "/proj_a"
	var proj_adj := scratch + "/proj_adj"
	var proj_sparse := scratch + "/proj_sparse"
	_check(_write_project(proj_a, [{"name": "Linux/X11"}, {"name": "Alt/Thing"}], false),
		"scratch project A not writable")
	_check(_write_project(proj_adj, [{"name": "NoSuchPreset"}], false),
		"scratch project adjacent not writable")
	_check(_write_project(proj_sparse, [{"name": "Linux/X11"}], true),
		"scratch project sparse not writable")
	_check(_census(proj_a) == CENSUS_A, "census parse of project A drifted")

	# ---- arms -------------------------------------------------------------
	var r_unknown := _arm("unknown_path", proj_a,
		["--export-release", "NoSuchPreset", out_dir + "/unknown.pck"], BOUND_S)
	refusals += 1
	arms += 1
	_check(r_unknown.rc == 1, "unknown_path rc=%d expected 1" % r_unknown.rc)
	_check(r_unknown.file_rc == r_unknown.rc, "unknown_path rc file/exec disagree")
	var c_unknown := _classify(r_unknown, "NoSuchPreset", CENSUS_A)
	_check(bool(c_unknown.ok), "unknown_path not classified as refusal: %s" % str(c_unknown))
	_check(r_unknown.out.contains("first_scan_filesystem"), "refusal stdout lacks editor scan receipt")
	_check(_sha(r_unknown.err) == REFUSAL_SHA, "refusal stderr hash drifted")

	var r_known := _arm("known_path", proj_a,
		["--export-release", "Linux/X11", out_dir + "/known.pck"], BOUND_S)
	controls += 1
	arms += 1
	_check(r_known.rc == 0, "known_path rc=%d expected 0" % r_known.rc)
	_check(r_known.err.size() == 0, "known_path stderr=%dB expected 0" % r_known.err.size())
	_check(r_known.artifact >= 1024 and r_known.magic == "GDPC",
		"known_path artifact bytes=%d magic=%s" % [r_known.artifact, r_known.magic])
	_check(r_known.out.contains("savepack") and r_known.out.contains("res://main.tscn.remap")
		and r_known.out.contains("res://project.binary"), "known_path pack receipts missing")

	var r_case := _arm("case_swap", proj_a,
		["--export-release", "linux/x11", out_dir + "/case.pck"], BOUND_S)
	refusals += 1
	arms += 1
	_check(r_case.rc == 1, "case_swap rc=%d expected 1 (case-sensitive lookup)" % r_case.rc)
	_check(bool(_classify(r_case, "linux/x11", CENSUS_A).ok), "case_swap not classified as refusal")

	var r_noargs := _arm("no_args", proj_a,
		["--export-release"], BOUND_S)
	refusals += 1
	arms += 1
	_check(r_noargs.rc == 1, "no_args rc=%d expected 1" % r_noargs.rc)
	_check(bool(_classify(r_noargs, "--editor", CENSUS_A).ok), "no_args does not echo the editor default")

	var r_nopath := _arm("unknown_no_path", proj_a,
		["--export-release", "NoSuchPreset"], BOUND_S)
	refusals += 1
	arms += 1
	_check(bool(_classify(r_nopath, "NoSuchPreset", CENSUS_A).ok), "unknown_no_path not classified as refusal")
	_check(r_nopath.err == r_unknown.err and r_nopath.out == r_unknown.out,
		"unknown_no_path: name resolution does not precede path validation")
	_check(r_nopath.artifact < 0, "unknown_no_path left an artifact")

	var r_empty := _arm("empty_name", proj_a,
		["--export-release", "", out_dir + "/empty.pck"], EMPTY_BOUND_S)
	arms += 1
	_check(r_empty.rc == 124, "empty_name rc=%d expected timeout-bound 124" % r_empty.rc)
	_check(r_empty.err.size() == 0, "empty_name stderr=%dB expected 0 (no refusal)" % r_empty.err.size())
	_check(r_empty.artifact < 0, "empty_name left an artifact")
	_check(not r_empty.out.contains("savepack"), "empty_name reached the packer")

	var r_adj := _arm("adjacent_exists", proj_adj,
		["--export-release", "NoSuchPreset", out_dir + "/adjacent.pck"], BOUND_S)
	controls += 1
	arms += 1
	_check(r_adj.rc == 0, "adjacent_exists rc=%d expected 0 (preset named NoSuchPreset exists)" % r_adj.rc)
	_check(r_adj.err.size() == 0, "adjacent_exists stderr=%dB expected 0" % r_adj.err.size())
	_check(r_adj.artifact >= 1024 and r_adj.magic == "GDPC",
		"adjacent_exists artifact bytes=%d magic=%s" % [r_adj.artifact, r_adj.magic])

	var r_debug := _arm("debug_unknown", proj_a,
		["--export-debug", "NoSuchPreset", out_dir + "/debug.pck"], BOUND_S)
	refusals += 1
	arms += 1
	_check(r_debug.rc == 1, "debug_unknown rc=%d expected 1" % r_debug.rc)
	_check(bool(_classify(r_debug, "NoSuchPreset", CENSUS_A).ok), "debug_unknown class differs from release")

	var r_pack := _arm("pack_unknown", proj_a,
		["--export-pack", "NoSuchPreset", out_dir + "/pack.pck"], BOUND_S)
	refusals += 1
	arms += 1
	_check(r_pack.rc == 1, "pack_unknown rc=%d expected 1" % r_pack.rc)
	_check(bool(_classify(r_pack, "NoSuchPreset", CENSUS_A).ok), "pack_unknown class differs from release")

	var r_path := _arm("known_no_path", proj_a,
		["--export-release", "Linux/X11"], BOUND_S)
	refusals += 1
	arms += 1
	_check(r_path.rc == 1, "known_no_path rc=%d expected 1" % r_path.rc)
	_check(r_path.err == _path_error("Linux/X11"), "known_no_path stderr is not the path-error class")
	_check(_sha(r_path.err) == PATH_ERR_SHA, "path-error stderr hash drifted")
	_check(r_path.artifact < 0, "known_no_path left an artifact")
	_check(not bool(_classify(r_path, "Linux/X11", CENSUS_A).ok),
		"path-error class wrongly accepted as an unknown-preset refusal")

	var r_sparse := _arm("sparse_unknown", proj_sparse,
		["--export-release", "NoSuchPreset", out_dir + "/sparse.pck"], BOUND_S)
	refusals += 1
	arms += 1
	_check(r_sparse.rc == 1, "sparse_unknown rc=%d expected 1" % r_sparse.rc)
	_check(r_sparse.err == _sparse_expected(), "sparse_unknown stderr prefix/order drifted")
	_check(_sha(r_sparse.err) == SPARSE_SHA, "sparse refusal stderr hash drifted")
	_check(not bool(_classify(r_sparse, "NoSuchPreset", CENSUS_A).ok),
		"schema-prefixed stderr wrongly accepted as an exact refusal")

	# ---- forgery mutants: every one must be rejected by the same classifier ----
	var base := {"rc": 1, "err": r_unknown.err, "artifact": -1, "out": r_unknown.out,
		"file_rc": 1, "ms": 0, "magic": "", "tag": "mutant"}
	_mutant("name_swap", _classify(_with(base, {"err": _refusal("Linux/X11", CENSUS_A)}),
		"NoSuchPreset", CENSUS_A))
	_mutant("rc_forged", _classify(_with(base, {"rc": 0}), "NoSuchPreset", CENSUS_A))
	_mutant("artifact_forged", _classify(_with(base, {"artifact": 1248}), "NoSuchPreset", CENSUS_A))
	_mutant("census_spoof", _classify(_with(base, {"err": _refusal("NoSuchPreset",
		["Linux/X11", "NoSuchPreset"])}), "NoSuchPreset", CENSUS_A))
	_mutant("control_splice", _classify(_with(base, {"err": r_known.err + r_unknown.err,
		"artifact": r_known.artifact, "out": r_known.out}), "NoSuchPreset", CENSUS_A))
	var truncated: PackedByteArray = r_unknown.err.slice(0, r_unknown.err.size() - 49)
	_mutant("truncated_tail", _classify(_with(base, {"err": truncated}), "NoSuchPreset", CENSUS_A))
	_mutant("sparse_prefix", _classify(r_sparse, "NoSuchPreset", CENSUS_A))

	# Self-consistency: the classifier accepts every observed real refusal byte string.
	_check(bool(_classify(r_debug, "NoSuchPreset", CENSUS_A).ok)
		and bool(_classify(r_pack, "NoSuchPreset", CENSUS_A).ok),
		"real mode-variant refusals rejected by the classifier")

	# ---- verdict -----------------------------------------------------------
	if failures.is_empty():
		print("PASS export_prod_s07 arms=%d refusals=%d controls=%d bounded_no_refusal=1 mutants=%d/%d rejection_class=exact-bytes-rc-artifact" % [
			arms, refusals, controls, mutant_rejects, mutants])
		quit(0)
	else:
		print("s07 ASSERTION FAILED: %s" % "; ".join(failures))
		quit(2)

# ---- harness ---------------------------------------------------------------

func _pick_root() -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--root="):
			return a.substr(7)
	for candidate in ["/tmp/r101-export-prod-s07", "/var/tmp/r101-export-prod-s07"]:
		if _probe_write(candidate):
			return candidate
	return ""

func _probe_write(dir: String) -> bool:
	DirAccess.make_dir_recursive_absolute(dir)
	var p := dir + "/.write-probe"
	var f := FileAccess.open(p, FileAccess.WRITE)
	if f == null:
		return false
	f.store_string("x")
	f.close()
	var g := FileAccess.open(p, FileAccess.READ)
	var ok := g != null and g.get_length() == 1
	if g != null:
		g.close()
	DirAccess.remove_absolute(p)
	return ok

func _put(path: String, text: String) -> bool:
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		return false
	f.store_string(text)
	f.close()
	return true

func _write_project(dir: String, presets: Array, sparse: bool) -> bool:
	if not dir.begins_with("/tmp/") and not dir.begins_with("/var/tmp/") and not dir.begins_with("/home/"):
		return false
	if dir.length() < 8:
		return false
	OS.execute("rm", ["-rf", dir], [], false, false)
	DirAccess.make_dir_recursive_absolute(dir)
	var ok := _put(dir + "/project.godot",
		"[application]\nconfig/name=\"r101e7\"\nconfig/features=PackedStringArray(\"4.7\")\nrun/main_scene=\"res://main.tscn\"\n")
	ok = _put(dir + "/main.tscn",
		"[gd_scene format=3 uid=\"uid://cr101e7main\"]\n\n[node name=\"Main\" type=\"Node2D\"]\n") and ok
	var cfg := ""
	for i in presets.size():
		cfg += "[preset.%d]\nname=\"%s\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\n" % [i, presets[i]["name"]]
		cfg += "dedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\n"
		if not sparse:
			cfg += "include_filter=\"\"\nexclude_filter=\"\"\n"
		cfg += "export_path=\"\"\n\n[preset.%d.options]\nbinary_format/architecture=\"x86_64\"\n\n" % i
	return _put(dir + "/export_presets.cfg", cfg) and ok

func _census(dir: String) -> Array:
	var f := FileAccess.open(dir + "/export_presets.cfg", FileAccess.READ)
	if f == null:
		return []
	var out: Array = []
	for line in f.get_as_text().split("\n"):
		if line.begins_with("name=\"") and line.ends_with("\""):
			out.append(line.substr(6, line.length() - 7))
	return out

func _arm(tag: String, project: String, args: Array, bound: int) -> Dictionary:
	# The artifact under test is exactly the path handed to the CLI; arms that pass no
	# output path get a sentinel that must never appear.
	var out_path := out_dir + "/" + tag + ".none.pck"
	for a in args:
		if str(a).ends_with(".pck"):
			out_path = str(a)
	var script_path := out_dir + "/" + tag + ".sh"
	var rc_path := out_dir + "/" + tag + ".rc"
	var args_s := ""
	for a in args:
		args_s += " '" + str(a).replace("'", "'\\''") + "'"
	var sh := "#!/bin/sh\ncd '%s' || exit 99\n/usr/bin/timeout %d '%s' --headless --path '%s'%s >'%s.stdout' 2>'%s.stderr'\nrc=$?\necho \"$rc\" > '%s'\nexit \"$rc\"\n" % [
		project, bound, godot, project, args_s, out_path, out_path, rc_path]
	_put(script_path, sh)
	var t0 := Time.get_ticks_msec()
	var exec_rc := OS.execute("/bin/sh", [script_path], [], false, false)
	var ms := Time.get_ticks_msec() - t0
	var file_rc := -1
	var rf := FileAccess.open(rc_path, FileAccess.READ)
	if rf != null:
		file_rc = int(rf.get_as_text().strip_edges())
		rf.close()
	var out := _text(out_path + ".stdout")
	var err := _bytes(out_path + ".stderr")
	var art := -1
	var magic := ""
	if FileAccess.file_exists(out_path):
		var ab := FileAccess.get_file_as_bytes(out_path)
		art = ab.size()
		if art >= 4:
			magic = ab.slice(0, 4).get_string_from_utf8()
	var row := {"tag": tag, "rc": exec_rc, "file_rc": file_rc, "ms": ms, "err": err,
		"out": out, "artifact": art, "magic": magic}
	print("ROW s07 %s rc=%d file_rc=%d ms=%d stderr=%dB sha=%s artifact=%d magic=%s" % [
		tag, exec_rc, file_rc, ms, err.size(), _sha(err).substr(0, 16), art, magic])
	return row

func _classify(row: Dictionary, name: String, census: Array) -> Dictionary:
	var expected := _refusal(name, census)
	var err: PackedByteArray = row["err"]
	var out: String = row["out"]
	var verdict := {
		"rc": int(row["rc"]) == 1,
		"stderr_exact": err.size() == expected.size() and _sha(err) == _sha(expected),
		"no_artifact": int(row["artifact"]) < 0,
		"no_pack_stdout": not out.contains("savepack"),
	}
	verdict["ok"] = verdict["rc"] and verdict["stderr_exact"] and verdict["no_artifact"] and verdict["no_pack_stdout"]
	return verdict

func _mutant(tag: String, verdict: Dictionary) -> void:
	mutants += 1
	var rejected: bool = not bool(verdict["ok"])
	if rejected:
		mutant_rejects += 1
	else:
		failures.append("mutant %s accepted" % tag)
	print("ROW s07 mutant %s verdict=%s rc=%s stderr_exact=%s no_artifact=%s no_pack_stdout=%s" % [
		tag, "reject" if rejected else "ACCEPT", str(verdict["rc"]),
		str(verdict["stderr_exact"]), str(verdict["no_artifact"]), str(verdict["no_pack_stdout"])])

func _with(base: Dictionary, patch: Dictionary) -> Dictionary:
	var copy := base.duplicate()
	for k in patch:
		copy[k] = patch[k]
	return copy

func _refusal(name: String, census: Array) -> PackedByteArray:
	var lines := PackedStringArray()
	lines.append("ERROR: Invalid export preset name: %s." % name)
	lines.append("The following presets were detected in this project's `export_presets.cfg`:")
	lines.append("")
	for p in census:
		lines.append("        \"%s\"" % p)
	lines.append("")
	lines.append("   at: _fs_changed (editor/editor_node.cpp:1417)")
	return ("\n".join(lines) + "\n").to_utf8_buffer()

func _path_error(name: String) -> PackedByteArray:
	return ("ERROR: Export preset \"%s\" doesn't have a default export path, and none was specified.\n   at: _fs_changed (editor/editor_node.cpp:1417)\n" % name).to_utf8_buffer()

func _sparse_expected() -> PackedByteArray:
	var lines := PackedStringArray()
	for key in ["include_filter", "exclude_filter", "include_filter", "exclude_filter"]:
		lines.append("ERROR: Couldn't find the given section \"preset.0\" and key \"%s\", and no default was given." % key)
		lines.append("   at: get_value (core/io/config_file.cpp:60)")
	return ("\n".join(lines) + "\n").to_utf8_buffer() + _refusal("NoSuchPreset", ["Linux/X11"])

func _check(cond: bool, msg: String) -> void:
	if not cond:
		failures.append(msg)
		print("FAIL s07 ", msg)

func _sha(buf: PackedByteArray) -> String:
	if buf.is_empty():
		# HashingContext.update() rejects a zero-length buffer and prints an engine ERROR line;
		# an empty digest must not pollute this fixture's own classified output.
		return "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(buf)
	return ctx.finish().hex_encode()

func _bytes(path: String) -> PackedByteArray:
	if not FileAccess.file_exists(path):
		return PackedByteArray()
	return FileAccess.get_file_as_bytes(path)

func _text(path: String) -> String:
	return _bytes(path).get_string_from_utf8()
