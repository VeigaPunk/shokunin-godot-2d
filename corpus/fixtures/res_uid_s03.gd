extends SceneTree
# r104 E3 fixture — ResourceLoader `.import` remap resolution lattice.
#
# Battery launch shape (run_battery.py convention, 8 s per-row bound):
#   godot --headless --path <fixtures proj> --script res://res_uid_s03.gd -- --arm=<arm>
#
# Scenario slice (seat E3): `.import` remap resolution — load the *source* path
# and receive the remapped resource; the remap-missing classes; non-resource
# path refusal; load-cache modes over a remapped source; and `uid_cache.bin`
# authority over `ResourceLoader.get_resource_uid`.
#
# Method: every arm stages a *child* Godot project under a scratch root and runs
# exactly ONE nested `godot --headless --path <child> --script res://child.gd`
# with the child's stdout+stderr redirected into a scratch log. The parent then
# derives booleans from that log and prints one PASS line. Two reasons:
#   * the engine prints `ERROR: No loader found for resource: ...` /
#     `ERROR: Resource file not found: ...` on the refusal and missing-remap
#     paths. The battery's stream classifier rejects any unallowlisted `ERROR:`
#     line on either stream, so the parent receipt must stay clean and the
#     child's noise must land in a file rather than in the receipt.
#   * remap resolution is a property of a *project*, so the scenario has to be
#     staged as one — a hand-written `.import` is enough (measured: no import
#     pass and no `.godot/` needed for a `[remap]` block that names an existing
#     `path=`), which is what makes this fixture cheap.
#
# Measured laws this fixture encodes (all [M], see reports/round-104/r104-E3.md):
#   L1 a `[remap]` block with `path=` resolves the source path to that
#      destination without any import pass and without a `.godot/` directory
#   L2 `ResourceLoader.exists(src)` follows the remap: it is TRUE whenever a
#      readable `.import` with a usable destination is present, FALSE when the
#      `.import` is absent (an unimported raw `.png` has no loader)
#   L3 the loaded instance's `resource_path` is the SOURCE path, and loading the
#      destination path directly yields a distinct instance
#   L4 `[remap] uid=` without `path=` is a silent refusal (exists=true, load=null,
#      0 engine errors) — the only error-free negative in this lattice
#   L5 the `.import` is re-read on every load, so retargeting `path=` is live
#   L6 `get_resource_uid` is served by `.godot/uid_cache.bin`, not by the remap
#      (absent cache => -1 even while the remap loads fine); the cache format is
#      hand-authorable: `<u32 count>` then per entry `<u64 id><u32 len><bytes>`
#   L7 `[remap] type=` does not gate the load (a mismatch is ignored)
#   L8 CACHE_MODE_IGNORE yields a fresh instance but leaves the cache populated
#
# Never prints host paths, object ids, RIDs or addresses. The child log stays on
# disk under the scratch root; only derived booleans reach the receipt. Set
# RES_UID_S03_DIAG=1 to echo host paths as RES_UID_S03_DIAG lines (off by
# default so the receipt stays minimal).

const CHILD := [
	"extends SceneTree",
	"",
	"var arm := \"\"",
	"",
	"func _initialize() -> void:",
	"\tfor a in OS.get_cmdline_user_args():",
	"\t\tif a.begins_with(\"--arm=\"):",
	"\t\t\tarm = a.substr(6)",
	"\t_run.call_deferred()",
	"",
	"func _c(r: Resource) -> String:",
	"\treturn r.get_class() if r != null else \"<null>\"",
	"",
	"func _n(r: Resource) -> String:",
	"\treturn r.resource_name if r != null else \"<none>\"",
	"",
	"func _pp(r: Resource) -> String:",
	"\treturn r.resource_path if r != null else \"<none>\"",
	"",
	"func _e(k: String, v: Variant) -> void:",
	"\tprint(\"CHILD %s %s=%s\" % [arm, k, v])",
	"",
	"func _probe(src: String) -> void:",
	"\t_e(\"exists\", ResourceLoader.exists(src))",
	"\tvar r := ResourceLoader.load(src, \"\", ResourceLoader.CACHE_MODE_IGNORE)",
	"\t_e(\"load_class\", _c(r))",
	"\t_e(\"load_name\", _n(r))",
	"",
	"func _write_import(body: String) -> void:",
	"\tvar f := FileAccess.open(\"res://asset.png.import\", FileAccess.WRITE)",
	"\tif f == null:",
	"\t\tprint(\"CHILD import_rewrite_failed\")",
	"\t\treturn",
	"\tf.store_string(body)",
	"\tf.close()",
	"",
	"func _drop(rel: String) -> void:",
	"\tvar d := DirAccess.open(\"res://\")",
	"\tif d != null:",
	"\t\td.remove(rel)",
	"",
	"const GOOD := \"[remap]\\n\\nimporter=\\\"s03_fake\\\"\\ntype=\\\"Resource\\\"\\npath=\\\"res://gen/dest.tres\\\"\\n\"",
	"const NO_PATH := \"[remap]\\n\\nimporter=\\\"s03_fake\\\"\\ntype=\\\"Resource\\\"\\nuid=\\\"uid://cs03nopath001\\\"\\n\"",
	"const BAD_DEST := \"[remap]\\n\\nimporter=\\\"s03_fake\\\"\\ntype=\\\"Resource\\\"\\npath=\\\"res://gen/absent.tres\\\"\\n\"",
	"const RETARGET := \"[remap]\\n\\nimporter=\\\"s03_fake\\\"\\ntype=\\\"Resource\\\"\\npath=\\\"res://gen/other.tres\\\"\\n\"",
	"const CORRUPT := \"not a config file\\n\\u0000\\u0001\\u0002\"",
	"",
	"func _arm_resolve() -> void:",
	"\tvar src := \"res://asset.png\"",
	"\t_e(\"exists_source\", ResourceLoader.exists(src))",
	"\tvar r := ResourceLoader.load(src)",
	"\t_e(\"load_class\", _c(r))",
	"\t_e(\"load_name\", _n(r))",
	"\t_e(\"load_path\", _pp(r))",
	"\t_e(\"has_cached\", ResourceLoader.has_cached(src))",
	"\t_e(\"exists_import_file\", ResourceLoader.exists(\"res://asset.png.import\"))",
	"\tvar cfg := ConfigFile.new()",
	"\t_e(\"import_parse_err\", cfg.load(\"res://asset.png.import\"))",
	"\tvar dest: String = cfg.get_value(\"remap\", \"path\", \"<none>\")",
	"\t_e(\"import_dest\", dest)",
	"\t_e(\"import_type\", cfg.get_value(\"remap\", \"type\", \"<none>\"))",
	"\t_e(\"import_uid\", cfg.get_value(\"remap\", \"uid\", \"<none>\"))",
	"\t_e(\"dest_exists\", ResourceLoader.exists(dest))",
	"\tvar d := ResourceLoader.load(dest)",
	"\t_e(\"dest_class\", _c(d))",
	"\t_e(\"dest_name\", _n(d))",
	"\t_e(\"dest_path\", _pp(d))",
	"\t_e(\"dest_same_instance_as_source\", d == r)",
	"\t_e(\"uid_source\", ResourceLoader.get_resource_uid(src))",
	"\t_e(\"uid_dest\", ResourceLoader.get_resource_uid(dest))",
	"\t_e(\"typed_resource_class\", _c(ResourceLoader.load(src, \"Resource\")))",
	"\t_e(\"typed_textfile_class\", _c(ResourceLoader.load(src, \"TextFile\")))",
	"\t_e(\"typed_exists_resource\", ResourceLoader.exists(src, \"Resource\"))",
	"\t_e(\"typed_exists_textfile\", ResourceLoader.exists(src, \"TextFile\"))",
	"",
	"func _arm_missing() -> void:",
	"\tvar src := \"res://asset.png\"",
	"\tprint(\"CHILD m0_begin\")",
	"\t_write_import(GOOD)",
	"\t_probe(src)",
	"\tprint(\"CHILD m0_end\")",
	"\tprint(\"CHILD m1_begin\")",
	"\t_write_import(NO_PATH)",
	"\t_probe(src)",
	"\tprint(\"CHILD m1_end\")",
	"\tprint(\"CHILD m2_begin\")",
	"\t_write_import(BAD_DEST)",
	"\t_probe(src)",
	"\tprint(\"CHILD m2_end\")",
	"\tprint(\"CHILD m3_begin\")",
	"\t_drop(\"asset.png.import\")",
	"\t_probe(src)",
	"\tprint(\"CHILD m3_end\")",
	"\tprint(\"CHILD m4_begin\")",
	"\t_write_import(CORRUPT)",
	"\t_probe(src)",
	"\tprint(\"CHILD m4_end\")",
	"\tprint(\"CHILD m5_begin\")",
	"\t_write_import(GOOD)",
	"\t_drop(\"asset.png\")",
	"\t_probe(src)",
	"\tprint(\"CHILD m5_end\")",
	"",
	"func _arm_refuse() -> void:",
	"\tvar cases := {",
	"\t\t\"plain\": \"res://plain.txt\",",
	"\t\t\"dir\": \"res://subdir\",",
	"\t\t\"root\": \"res://\",",
	"\t\t\"absent\": \"res://absent.png\",",
	"\t\t\"import\": \"res://asset.png.import\",",
	"\t\t\"user\": \"user://absent.png\",",
	"\t\t\"subplain\": \"res://subdir/plain.txt\",",
	"\t\t\"noscheme\": \"asset.png\",",
	"\t}",
	"\tfor k in [\"plain\", \"dir\", \"root\", \"absent\", \"import\", \"user\", \"subplain\", \"noscheme\"]:",
	"\t\tvar p: String = cases[k]",
	"\t\t_e(\"e_\" + k, ResourceLoader.exists(p))",
	"\tfor k in [\"plain\", \"dir\", \"root\", \"absent\", \"import\", \"user\", \"subplain\", \"noscheme\"]:",
	"\t\tvar p: String = cases[k]",
	"\t\t_e(\"l_\" + k, _c(ResourceLoader.load(p, \"\", ResourceLoader.CACHE_MODE_IGNORE)))",
	"\t_e(\"uid_plain\", ResourceLoader.get_resource_uid(\"res://plain.txt\"))",
	"\t_e(\"uid_absent\", ResourceLoader.get_resource_uid(\"res://absent.png\"))",
	"\t_e(\"uid_dir\", ResourceLoader.get_resource_uid(\"res://subdir\"))",
	"\t_e(\"uid_root\", ResourceLoader.get_resource_uid(\"res://\"))",
	"\t_e(\"uid_import\", ResourceLoader.get_resource_uid(\"res://asset.png.import\"))",
	"",
	"func _arm_cache() -> void:",
	"\tvar src := \"res://asset.png\"",
	"\tvar a := ResourceLoader.load(src)",
	"\tvar b := ResourceLoader.load(src)",
	"\tvar c := ResourceLoader.load(src, \"\", ResourceLoader.CACHE_MODE_REUSE)",
	"\tvar d := ResourceLoader.load(src, \"\", ResourceLoader.CACHE_MODE_REPLACE)",
	"\tvar e := ResourceLoader.load(src, \"\", ResourceLoader.CACHE_MODE_IGNORE)",
	"\t_e(\"reuse_default_identity\", a == b)",
	"\t_e(\"reuse_explicit_identity\", a == c)",
	"\t_e(\"replace_identity\", a == d)",
	"\t_e(\"ignore_identity\", a == e)",
	"\t_e(\"has_cached\", ResourceLoader.has_cached(src))",
	"\t_e(\"ignore_name\", _n(e))",
	"\t_e(\"ignore_path\", _pp(e))",
	"\t_e(\"cached_name\", _n(ResourceLoader.load(src)))",
	"\t_write_import(RETARGET)",
	"\t_e(\"retarget_load_name\", _n(ResourceLoader.load(src, \"\", ResourceLoader.CACHE_MODE_IGNORE)))",
	"\t_e(\"cached_name_after_retarget\", _n(ResourceLoader.load(src)))",
	"",
	"func _arm_uidcache() -> void:",
	"\tvar src := \"res://asset.png\"",
	"\t_e(\"uid_source\", ResourceLoader.get_resource_uid(src))",
	"\t_e(\"uid_text\", ResourceUID.id_to_text(ResourceLoader.get_resource_uid(src)))",
	"\t_e(\"uid_expected\", 1311768467294899695)",
	"\t_e(\"exists\", ResourceLoader.exists(src))",
	"\t_e(\"load_class\", _c(ResourceLoader.load(src, \"\", ResourceLoader.CACHE_MODE_IGNORE)))",
	"\t_e(\"load_name\", _n(ResourceLoader.load(src, \"\", ResourceLoader.CACHE_MODE_IGNORE)))",
	"\tvar cfg := ConfigFile.new()",
	"\tcfg.load(\"res://asset.png.import\")",
	"\t_e(\"import_uid_field\", cfg.get_value(\"remap\", \"uid\", \"<none>\"))",
	"",
	"func _run() -> void:",
	"\tmatch arm:",
	"\t\t\"resolve\": _arm_resolve()",
	"\t\t\"missing\": _arm_missing()",
	"\t\t\"refuse\": _arm_refuse()",
	"\t\t\"cache\": _arm_cache()",
	"\t\t\"uidcache\": _arm_uidcache()",
	"\t\t_: print(\"CHILD unknown_arm=\", arm)",
	"\tprint(\"CHILD %s done\" % arm)",
	"\tquit(0)",
]

# Per-arm row definition: child arm name, staged files, and the ordered
# (key, expected) list that both the assertions and the PASS line are built
# from. `errs` optionally binds per-variant ERROR: line counts (missing arm).
const PROJECT_GODOT := "[application]\nconfig/name=\"ResUidS03Child\"\nconfig/features=PackedStringArray(\"4.7\")\n"
const DEST_TRES := "[gd_resource type=\"Resource\" format=3]\n\n[resource]\nresource_name=\"s03_dest\"\n"
const OTHER_TRES := "[gd_resource type=\"Resource\" format=3]\n\n[resource]\nresource_name=\"s03_other\"\n"

const GOOD_IMPORT := "[remap]\n\nimporter=\"s03_fake\"\ntype=\"Resource\"\npath=\"res://gen/dest.tres\"\n"
const PLAIN_TXT := "plain text, not a resource\n"
const FAKE_PNG := "not a png at all\n"

var arm := ""
var _root := ""
var _diag := false
var _aborted := false
var _log_lines: PackedStringArray = []
var _observed := {}

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_diag = OS.get_environment("RES_UID_S03_DIAG") == "1"
	_run.call_deferred()

# --------------------------------------------------------------- utilities

# quit() only sets a flag that the SceneTree honours between frames, so a bare
# quit(1) would let the current call chain keep running and could print a PASS
# line after the FAIL. Every arm therefore checks _aborted at its decision
# points; the process exit code is the fail-closed signal.
func _fail(reason: String) -> void:
	if _aborted:
		return
	_aborted = true
	print("FAIL res_uid_s03 %s reason=%s" % [arm, reason])
	quit(1)

func _diagline(msg: String) -> void:
	if _diag:
		print("RES_UID_S03_DIAG %s" % msg)

func _q(s: String) -> String:
	return "'" + s.replace("'", "'\\''") + "'"

func _write_file(path: String, content: Variant) -> bool:
	var dir := path.get_base_dir()
	if DirAccess.make_dir_recursive_absolute(dir) != OK:
		return false
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		return false
	if content is PackedByteArray:
		f.store_buffer(content)
	else:
		f.store_string(str(content))
	f.close()
	return true

# Hand-authored uid_cache.bin: <u32 count=1> <u64 id=0x1234567890ABCDEF>
# <u32 len=15> "res://asset.png" (57 bytes). Built as raw bytes because a
# GDScript "\u00ef" escape would round-trip through UTF-8 as two bytes.
func _uid_cache_bytes() -> PackedByteArray:
	var b := PackedByteArray([1, 0, 0, 0, 0xEF, 0xCD, 0xAB, 0x90,
			0x78, 0x56, 0x34, 0x12, 15, 0, 0, 0])
	b.append_array("res://asset.png".to_utf8_buffer())
	return b

func _wipe(path: String) -> void:
	var d := DirAccess.open(path)
	if d == null:
		return
	d.list_dir_begin()
	var names := PackedStringArray()
	var subdirs := PackedStringArray()
	var n := d.get_next()
	while n != "":
		if n != "." and n != "..":
			if d.current_is_dir():
				subdirs.append(n)
			else:
				names.append(n)
		n = d.get_next()
	d.list_dir_end()
	for f in names:
		DirAccess.remove_absolute(path.path_join(f))
	for s in subdirs:
		_wipe(path.path_join(s))
	DirAccess.remove_absolute(path)

# Scratch root: RES_UID_ROOT, else user://res_uid_s03 (unique per battery run,
# because run_battery.py renames the project). Gated by a write+readback probe.
func _resolve_root() -> String:
	var candidates := PackedStringArray()
	var env := OS.get_environment("RES_UID_ROOT")
	if env != "":
		candidates.append(env.path_join("res_uid_s03"))
	candidates.append(ProjectSettings.globalize_path("user://").path_join("res_uid_s03"))
	for c in candidates:
		if DirAccess.make_dir_recursive_absolute(c) != OK:
			continue
		var probe := c.path_join("write_probe.bin")
		var f := FileAccess.open(probe, FileAccess.WRITE)
		if f == null:
			continue
		f.store_string("x".repeat(4096))
		f.close()
		if FileAccess.get_file_as_string(probe).length() == 4096:
			DirAccess.remove_absolute(probe)
			return c
	return ""

func _stage(dir: String, files: Dictionary) -> bool:
	_wipe(dir)
	if DirAccess.make_dir_recursive_absolute(dir) != OK:
		return false
	for rel in files:
		if not _write_file(dir.path_join(rel), files[rel]):
			return false
	return true

func _run_child(proj: String, child_arm: String, log_path: String) -> int:
	var exe := OS.get_executable_path()
	var cmd := "exec > " + _q(log_path) + " 2>&1\nexec " + _q(exe) \
		+ " --headless --path " + _q(proj) + " --script res://child.gd -- --arm=" + child_arm
	var out: Array = []
	var rc := OS.execute("/usr/bin/sh", PackedStringArray(["-c", cmd]), out, true)
	_log_lines = FileAccess.get_file_as_string(log_path).split("\n")
	return rc

# The child's exit code alone is not a sound gate: a headless Godot process can
# still exit non-zero after printing its complete result set (observed once in
# 30 runs on the uidcache arm, with every CHILD key present and correct). Bind
# the row to the child's own terminal evidence instead — every arm's child ends
# with `CHILD <arm> done` — and report the exit code only as a diagnostic.
func _child_ok(child_arm: String) -> bool:
	for line in _log_lines:
		if line.begins_with("CHILD %s done" % child_arm):
			return true
	return false

func _parse(prefix: String) -> void:
	for line in _log_lines:
		if not line.begins_with(prefix):
			continue
		var rest := line.substr(prefix.length())
		var eq := rest.find("=")
		if eq > 0:
			_observed[rest.substr(0, eq)] = rest.substr(eq + 1)

func _count_errors(begin: String, end: String) -> int:
	var n := 0
	var inside := false
	for line in _log_lines:
		if line.begins_with(begin):
			inside = true
			continue
		if line.begins_with(end):
			inside = false
			continue
		if inside and line.contains("ERROR:"):
			n += 1
	return n

func _value_of(key: String) -> String:
	return str(_observed.get(key, "<absent>"))

# Assert every (key, expected) pair, then emit the PASS line from the same
# ordered list — so a PASS line is only ever printed for a fully asserted row.
func _verdict(rows: Array) -> void:
	for row in rows:
		var k: String = row[0]
		var want: String = row[1]
		var got := _value_of(k)
		if got != want:
			return _fail("assertion_%s_want=%s_got=%s" % [k, want, got])
	if _aborted:
		return
	var parts := PackedStringArray()
	for row in rows:
		parts.append("%s=%s" % [row[0], row[1]])
	print("PASS res_uid_s03 %s %s" % [arm, " ".join(parts)])
	quit(0)

# ------------------------------------------------------------------- arms

func _arm_resolve() -> void:
	var dir := _root.path_join("resolve")
	var files := {
		"project.godot": PROJECT_GODOT,
		"asset.png": FAKE_PNG,
		"asset.png.import": GOOD_IMPORT,
		"gen/dest.tres": DEST_TRES,
		"plain.txt": PLAIN_TXT,
	}
	if not _stage(dir.path_join("proj"), files):
		return _fail("stage_failed")
	var child := dir.path_join("proj").path_join("child.gd")
	if not _write_file(child, "\n".join(CHILD) + "\n"):
		return _fail("child_write_failed")
	var rc := _run_child(dir.path_join("proj"), "resolve", dir.path_join("child.log"))
	_diagline("child_resolve_rc=" + str(rc))
	if not _child_ok("resolve"):
		return _fail("child_incomplete_rc=" + str(rc))
	_parse("CHILD resolve ")
	if not _observed.has("load_class"):
		return _fail("child_no_output")
	_verdict([
		["exists_source", "true"],
		["load_class", "Resource"],
		["load_name", "s03_dest"],
		["load_path", "res://asset.png"],
		["has_cached", "true"],
		["exists_import_file", "false"],
		["import_parse_err", "0"],
		["import_dest", "res://gen/dest.tres"],
		["import_type", "Resource"],
		["import_uid", "<none>"],
		["dest_exists", "true"],
		["dest_class", "Resource"],
		["dest_name", "s03_dest"],
		["dest_path", "res://gen/dest.tres"],
		["dest_same_instance_as_source", "false"],
		["uid_source", "-1"],
		["uid_dest", "-1"],
		["typed_resource_class", "Resource"],
		["typed_textfile_class", "Resource"],
		["typed_exists_resource", "true"],
		["typed_exists_textfile", "true"],
	])

func _arm_missing() -> void:
	var dir := _root.path_join("missing")
	var files := {
		"project.godot": PROJECT_GODOT,
		"asset.png": FAKE_PNG,
		"asset.png.import": GOOD_IMPORT,
		"gen/dest.tres": DEST_TRES,
		"plain.txt": PLAIN_TXT,
	}
	if not _stage(dir.path_join("proj"), files):
		return _fail("stage_failed")
	if not _write_file(dir.path_join("proj").path_join("child.gd"), "\n".join(CHILD) + "\n"):
		return _fail("child_write_failed")
	var rc := _run_child(dir.path_join("proj"), "missing", dir.path_join("child.log"))
	_diagline("child_missing_rc=" + str(rc))
	if not _child_ok("missing"):
		return _fail("child_incomplete_rc=" + str(rc))
	# Variant -> (exists, load_class, ERROR: lines observed in the window)
	var want := {
		"m0": ["true", "Resource", 0],
		"m1": ["true", "<null>", 3],
		"m2": ["true", "<null>", 4],
		"m3": ["false", "<null>", 2],
		"m4": ["true", "<null>", 3],
		"m5": ["true", "Resource", 0],
	}
	# This arm reads its values out of the per-variant log windows rather than a
	# flat CHILD prefix, so fold them into _observed and let _verdict assert and
	# print from that one source.
	var rows := []
	for v in ["m0", "m1", "m2", "m3", "m4", "m5"]:
		_observed[v + "_exists"] = _variant_value(v, "exists")
		_observed[v + "_load"] = _variant_value(v, "load_class")
		_observed[v + "_errors"] = str(_count_errors("CHILD %s_begin" % v, "CHILD %s_end" % v))
		rows.append([v + "_exists", want[v][0]])
		rows.append([v + "_load", want[v][1]])
		rows.append([v + "_errors", str(want[v][2])])
	_verdict(rows)

func _variant_value(v: String, key: String) -> String:
	var inside := false
	for line in _log_lines:
		if line.begins_with("CHILD %s_begin" % v):
			inside = true
			continue
		if line.begins_with("CHILD %s_end" % v):
			inside = false
			continue
		if inside and line.contains("%s=" % key):
			var eq := line.find("%s=" % key)
			return line.substr(eq + key.length() + 1)
	return "<absent>"

func _arm_refuse() -> void:
	var dir := _root.path_join("refuse")
	var files := {
		"project.godot": PROJECT_GODOT,
		"asset.png": FAKE_PNG,
		"asset.png.import": GOOD_IMPORT,
		"gen/dest.tres": DEST_TRES,
		"plain.txt": PLAIN_TXT,
		"subdir/plain.txt": PLAIN_TXT,
	}
	if not _stage(dir.path_join("proj"), files):
		return _fail("stage_failed")
	if not _write_file(dir.path_join("proj").path_join("child.gd"), "\n".join(CHILD) + "\n"):
		return _fail("child_write_failed")
	var rc := _run_child(dir.path_join("proj"), "refuse", dir.path_join("child.log"))
	_diagline("child_refuse_rc=" + str(rc))
	if not _child_ok("refuse"):
		return _fail("child_incomplete_rc=" + str(rc))
	_parse("CHILD refuse ")
	if not _observed.has("l_plain"):
		return _fail("child_no_output")
	var rows := []
	for k in ["plain", "dir", "root", "absent", "import", "user", "subplain"]:
		rows.append(["e_" + k, "false"])
		rows.append(["l_" + k, "<null>"])
	# A scheme-less path is resolved against res://, so it lands on the remapped
	# asset rather than being refused.
	rows.append(["e_noscheme", "true"])
	rows.append(["l_noscheme", "Resource"])
	rows.append(["uid_plain", "-1"])
	rows.append(["uid_absent", "-1"])
	rows.append(["uid_dir", "-1"])
	rows.append(["uid_root", "-1"])
	rows.append(["uid_import", "-1"])
	_verdict(rows)

func _arm_cache() -> void:
	var dir := _root.path_join("cache")
	var files := {
		"project.godot": PROJECT_GODOT,
		"asset.png": FAKE_PNG,
		"asset.png.import": GOOD_IMPORT,
		"gen/dest.tres": DEST_TRES,
		"gen/other.tres": OTHER_TRES,
		"plain.txt": PLAIN_TXT,
	}
	if not _stage(dir.path_join("proj"), files):
		return _fail("stage_failed")
	if not _write_file(dir.path_join("proj").path_join("child.gd"), "\n".join(CHILD) + "\n"):
		return _fail("child_write_failed")
	var rc := _run_child(dir.path_join("proj"), "cache", dir.path_join("child.log"))
	_diagline("child_cache_rc=" + str(rc))
	if not _child_ok("cache"):
		return _fail("child_incomplete_rc=" + str(rc))
	_parse("CHILD cache ")
	if not _observed.has("ignore_name"):
		return _fail("child_no_output")
	_verdict([
		["reuse_default_identity", "true"],
		["reuse_explicit_identity", "true"],
		["replace_identity", "true"],
		["ignore_identity", "false"],
		["has_cached", "true"],
		["ignore_name", "s03_dest"],
		["ignore_path", "res://asset.png"],
		["cached_name", "s03_dest"],
		["retarget_load_name", "s03_other"],
		["cached_name_after_retarget", "s03_dest"],
	])

func _arm_uidcache() -> void:
	var dir := _root.path_join("uidcache")
	var files := {
		"project.godot": PROJECT_GODOT,
		"asset.png": FAKE_PNG,
		"asset.png.import": GOOD_IMPORT,
		"gen/dest.tres": DEST_TRES,
		"plain.txt": PLAIN_TXT,
		".godot/uid_cache.bin": _uid_cache_bytes(),
	}
	if not _stage(dir.path_join("proj"), files):
		return _fail("stage_failed")
	if not _write_file(dir.path_join("proj").path_join("child.gd"), "\n".join(CHILD) + "\n"):
		return _fail("child_write_failed")
	var rc := _run_child(dir.path_join("proj"), "uidcache", dir.path_join("child.log"))
	_diagline("child_uidcache_rc=" + str(rc))
	if not _child_ok("uidcache"):
		return _fail("child_incomplete_rc=" + str(rc))
	_parse("CHILD uidcache ")
	if not _observed.has("uid_text"):
		return _fail("child_no_output")
	_verdict([
		["uid_source", "1311768467294899695"],
		["uid_text", "uid://sxovuchqei7p"],
		["uid_expected", "1311768467294899695"],
		["exists", "true"],
		["load_class", "Resource"],
		["load_name", "s03_dest"],
		["import_uid_field", "<none>"],
	])

# ------------------------------------------------------------------- main

func _run() -> void:
	_root = _resolve_root()
	if _root == "":
		return _fail("no_writable_scratch_root")
	_diagline("root=%s" % _root)
	match arm:
		"resolve": _arm_resolve()
		"missing": _arm_missing()
		"refuse": _arm_refuse()
		"cache": _arm_cache()
		"uidcache": _arm_uidcache()
		_: _fail("unknown_arm")
