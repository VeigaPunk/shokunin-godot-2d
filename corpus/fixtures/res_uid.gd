extends SceneTree
# r104-E0 — C1 fixture: ResourceLoader / ResourceUID UID-cache lattice.
#
# Coverage gap this closes: scene_io_lattice.gd:438 (`_arm_uid`) probes the
# in-memory ResourceUID API only; nothing in the corpus touches the ON-DISK uid
# cache, the `.uid` sidecar / `.import` remap resolution, load-by-uid object
# identity, or UID persistence across processes.
#
# Every arm prints exactly ONE `PASS res_uid <arm> <k=v> ...` line; `R104 <arm> ...`
# lines are diagnostics. No absolute paths, instance ids, RIDs or process-dependent
# tokens are printed: all scratch lives under the fixed `user://r104e0` base and is
# removed again by _wipe(). Shape tokens (`_shape`) replace path/uid literals so a
# pin cannot encode a host path.
#
# Arms that make the engine print ERROR diagnostics on stderr are listed with their
# exact lines in reports/round-104/r104-E0.md (the battery concatenates stdout +
# stderr, so those rows need expected_errors entries keyed by the case name).
#
# Launch: godot --headless --path <proj> --script res://res_uid.gd -- --arm=<arm>
# Arms: text path collide cache modes import persist missing
const BASE := "user://r104e0"

var arm := ""
var _parts: PackedStringArray = []

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(_g(BASE))
	match arm:
		"text": _arm_text()
		"path": _arm_path()
		"collide": _arm_collide()
		"cache": _arm_cache()
		"modes": _arm_modes()
		"import": _arm_import()
		"persist": _arm_persist()
		"missing": _arm_missing()
		_: print("FAIL res_uid %s reason=unknown_arm" % arm)
	_wipe()
	quit(0)

# ------------------------------------------------------------------ utilities

func _b(v: bool) -> String:
	return "true" if v else "false"

func _g(p: String) -> String:
	return ProjectSettings.globalize_path(p)

func _shape(s: String) -> String:
	if s.begins_with("uid://"):
		return "uid"
	if s.begins_with("res://") or s.begins_with("user://"):
		return "path"
	if s == "":
		return "empty"
	return "other"

func _p(part: String) -> void:
	_parts.append(part)

func _emit(arm_name: String) -> void:
	print("PASS res_uid %s %s" % [arm_name, " ".join(_parts)])
	_parts.clear()

func _mk_grad(c: Color) -> Gradient:
	var g := Gradient.new()
	g.colors = PackedColorArray([c, Color(0, 0, 0, 1)])
	return g

func _cols(o) -> String:
	return "none" if o == null else str(o.colors)

func _w(path: String, text: String) -> void:
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string(text)
	f.close()

func _wipe() -> void:
	var g := _g(BASE)
	if not DirAccess.dir_exists_absolute(g):
		return
	var d := DirAccess.open(g)
	if d == null:
		return
	d.include_hidden = true
	for sub in d.get_directories():
		_rm_tree(g + "/" + sub)
	for f in d.get_files():
		DirAccess.remove_absolute(g + "/" + f)

func _rm_tree(path: String) -> void:
	var d := DirAccess.open(path)
	if d == null:
		return
	d.include_hidden = true
	for sub in d.get_directories():
		_rm_tree(path + "/" + sub)
	for f in d.get_files():
		DirAccess.remove_absolute(path + "/" + f)
	DirAccess.remove_absolute(path)

func _spawn(project_dir: String, script_path: String, extra: Array = []) -> Dictionary:
	var args := ["--headless", "--path", project_dir]
	if script_path != "":
		args.append("--script")
		args.append(script_path)
	args.append_array(extra)
	var out: Array = []
	var code := OS.execute(OS.get_executable_path(), args, out, true)
	return {"code": code, "text": "\n".join(PackedStringArray(out)), "tries": 1}

# Retry wrapper for the reader child: this host intermittently launches a headless
# child with a null getcwd ("Parameter getcwd(real_current_dir_name, 2048) is null"
# at drivers/unix/dir_access_unix.cpp:739 -> "Invalid project path ... aborting"),
# a spawn-environment flake that has nothing to do with what the arm asserts.
# The retry keeps the *outcome* fields deterministic; `tries` is diagnostic only.
func _spawn_reader(project_dir: String, script_path: String) -> Dictionary:
	var res := {}
	for i in 4:
		res = _spawn(project_dir, script_path)
		res["tries"] = i + 1
		if _child_line(res["text"], "CHILD ") != "":
			break
	return res

func _child_line(text: String, prefix: String) -> String:
	for line in text.split("\n"):
		if line.begins_with(prefix):
			return line
	return ""

func _child_field(line: String, key: String) -> String:
	for tok in line.split(" "):
		if tok.begins_with(key + "="):
			return tok.substr(key.length() + 1)
	return ""

# ------------------------------------------------------------------ arms

func _arm_text() -> void:
	var dec := PackedStringArray()
	for s in ["uid://a", "uid://9", "uid://z", "uid://0", "uid://bqk3m5n7qar1", "uid://b",
			"uid://", "uid://aaaa"]:
		dec.append("%s=%d" % [s, ResourceUID.text_to_id(s)])
	_p("decode=%s" % ",".join(dec))
	_p("alias_empty_eq_aaaa=%s alias_0_eq_z=%s a0=%d z25=%d" % [
		_b(ResourceUID.text_to_id("uid://") == ResourceUID.text_to_id("uid://aaaa")),
		_b(ResourceUID.text_to_id("uid://0") == ResourceUID.text_to_id("uid://z")),
		ResourceUID.text_to_id("uid://a"), ResourceUID.text_to_id("uid://z")])
	var rt_ok := true
	var first_bad := "none"
	for v in [0, 1, 35, 36, 2 ** 31 - 1, 2 ** 31, 9223372036854775807]:
		if ResourceUID.text_to_id(ResourceUID.id_to_text(v)) != v:
			rt_ok = false
			first_bad = str(v)
	_p("roundtrip_int63max=%s first_bad=%s" % [_b(rt_ok), first_bad])
	# `2 ** 63` OVERFLOWS GDScript's int64 to INT64_MIN, so a `minted >= 2 ** 63`
	# comparison is trivially true (measured: 2**63 == -9223372036854775808). The
	# bound is spelled as a literal; the overflow itself is pinned as a fact.
	var pow2_63: int = 2 ** 63
	_p("pow2_63_overflows=%s pow2_63_val=%d int64_max=%d" % [
		_b(pow2_63 < 0), pow2_63, 9223372036854775807])
	var minted: int = ResourceUID.create_id()
	var m_text := ResourceUID.id_to_text(minted)
	var m_back: int = ResourceUID.text_to_id(m_text)
	_p("minted_positive=%s minted_le_int64max=%s minted_text_shape=%s minted_roundtrip=%s" % [
		_b(minted > 0), _b(minted <= 9223372036854775807), _shape(m_text),
		_b(m_back == minted)])
	var bad := ResourceUID.text_to_id("not-a-uid")
	_p("invalid_text_id=%d invalid_text_back=%s empty_text_id=%d invalid_const=%d" % [
		bad, ResourceUID.id_to_text(bad), ResourceUID.text_to_id(""), ResourceUID.INVALID_ID])
	_emit("text")

func _arm_path() -> void:
	var p := BASE + "/path.tres"
	var e := ResourceSaver.save(_mk_grad(Color(1, 0, 0, 1)), p)
	var after_save: String = ResourceUID.path_to_uid(p)
	var ensure_val := str(ResourceUID.ensure_path(p))
	var after_ensure: String = ResourceUID.path_to_uid(p)
	_p("save=%s after_save_shape=%s ensure_shape=%s after_ensure_shape=%s after_ensure_same=%s" % [
		error_string(e), _shape(after_save), _shape(ensure_val), _shape(after_ensure),
		_b(after_ensure == after_save)])
	var echo_proj: String = ResourceUID.path_to_uid("res://project.godot")
	var echo_missing: String = ResourceUID.path_to_uid("res://absent_xyz.tres")
	_p("echo_proj_is_path=%s echo_missing_is_path=%s" % [
		_b(echo_proj == "res://project.godot"), _b(echo_missing == "res://absent_xyz.tres")])
	var ghost: int = ResourceUID.create_id()
	var ghost_back: String = ResourceUID.uid_to_path(ResourceUID.id_to_text(ghost))
	var bad_back: String = ResourceUID.uid_to_path("not-a-uid")
	var empty_back: String = ResourceUID.uid_to_path("")
	_p("ghost_back_empty=%s bad_back_empty=%s empty_back_empty=%s" % [
		_b(ghost_back == ""), _b(bad_back == ""), _b(empty_back == "")])
	var absent_id: int = ResourceUID.create_id()
	var absent_back: String = ResourceUID.uid_to_path(ResourceUID.id_to_text(absent_id))
	_p("unknown_uid_to_path_empty=%s ghost_text_shape=%s" % [
		_b(absent_back == ""), _shape(ResourceUID.id_to_text(absent_id))])
	var q := BASE + "/path2.tres"
	var c1: int = ResourceUID.create_id_for_path(q)
	var c2: int = ResourceUID.create_id_for_path(q)
	_p("create_for_path_deterministic=%s registered=%s id_path_empty=%s" % [
		_b(c1 == c2), _b(ResourceUID.has_id(c1)), _b(ResourceUID.get_id_path(c1) == "")])
	_emit("path")

func _arm_collide() -> void:
	var path := BASE + "/coll.tres"
	var ia: int = ResourceUID.create_id()
	var ib: int = ResourceUID.create_id()
	ResourceUID.add_id(ia, path)
	ResourceUID.add_id(ib, path)
	var fwd_ia := ResourceUID.get_id_path(ia)
	var fwd_ib := ResourceUID.get_id_path(ib)
	var rev: String = ResourceUID.path_to_uid(path)
	_p("two_ids_one_path fwd_ia_kept=%s fwd_ib_kept=%s rev_shape=%s rev_is_ib=%s rev_is_ia=%s" % [
		_b(fwd_ia == path), _b(fwd_ib == path), _shape(rev),
		_b(ResourceUID.text_to_id(rev) == ib), _b(ResourceUID.text_to_id(rev) == ia)])
	var one := ResourceUID.create_id()
	ResourceUID.add_id(one, BASE + "/c1.tres")
	ResourceUID.add_id(one, BASE + "/c2.tres")
	var fwd2 := ResourceUID.get_id_path(one)
	_p("one_id_two_paths fwd_keeps_first=%s" % _b(fwd2 == BASE + "/c1.tres"))
	# set_id/remove_id only operate on an id the table already knows: both are
	# silent no-ops on an unregistered id (measured; they print
	# `Condition "!unique_ids.has(p_id)" is true.` and change nothing), and the
	# subsequent get_id_path then echoes the queried uid — a per-process random
	# string, so the arm must never query an id that set_id refused.
	var fresh: int = ResourceUID.create_id()
	ResourceUID.set_id(fresh, BASE + "/s.tres")
	_p("set_id_unregistered_registers=%s" % _b(ResourceUID.has_id(fresh)))
	var known: int = ResourceUID.create_id()
	ResourceUID.add_id(known, BASE + "/s.tres")
	ResourceUID.set_id(known, BASE + "/s2.tres")
	_p("set_id_registered_retargets=%s" % _b(ResourceUID.get_id_path(known) == BASE + "/s2.tres"))
	ResourceUID.remove_id(known)
	_p("remove_id_registered_clears=%s" % _b(not ResourceUID.has_id(known)))
	_emit("collide")

func _arm_cache() -> void:
	var p := BASE + "/cache.tres"
	ResourceSaver.save(_mk_grad(Color(1, 0, 0, 1)), p)
	var custom: int = ResourceUID.create_id()
	ResourceUID.add_id(custom, p)
	var uid_text := ResourceUID.id_to_text(custom)
	var l1 = ResourceLoader.load(p)
	var l2 = ResourceLoader.load(p)
	var lu = ResourceLoader.load(uid_text)
	_p("same_path=%s same_uid=%s loaders_same=%s" % [
		_b(is_same(l1, l2)), _b(is_same(l1, lu)), _b(lu.get_class() == l1.get_class())])
	var rp: String = lu.resource_path
	_p("uid_load_path_is_p=%s uid_load_path_shape=%s" % [
		_b(rp == p), _shape(rp)])
	_p("has_cached path=%s uid=%s exists_path=%s exists_uid=%s" % [
		_b(ResourceLoader.has_cached(p)), _b(ResourceLoader.has_cached(uid_text)),
		_b(ResourceLoader.exists(p)), _b(ResourceLoader.exists(uid_text))])
	var gid: int = ResourceLoader.get_resource_uid(p)
	# the uid-argument form resolves back to the same custom id; the raw id is
	# random per process, so only the equality relation is pinned
	_p("get_resource_uid_is_custom=%s get_resource_uid_uidarg_is_custom=%s" % [
		_b(gid == custom), _b(ResourceLoader.get_resource_uid(uid_text) == custom)])
	var missing = ResourceLoader.load(BASE + "/absent_zzz.tres")
	_p("missing_load_null=%s missing_has_cached=%s missing_exists=%s" % [
		_b(missing == null), _b(ResourceLoader.has_cached(BASE + "/absent_zzz.tres")),
		_b(ResourceLoader.exists(BASE + "/absent_zzz.tres"))])
	# a .tres saved to disk is NOT auto-registered in the uid cache
	var v := BASE + "/volatile.tres"
	ResourceSaver.save(_mk_grad(Color(0, 0, 1, 1)), v)
	_p("unregistered_tres path_to_uid_echo=%s get_resource_uid=%d load_ok=%s" % [
		_b(ResourceUID.path_to_uid(v) == v), ResourceLoader.get_resource_uid(v),
		_b(ResourceLoader.load(v) != null)])
	_emit("cache")

func _arm_modes() -> void:
	var p := BASE + "/modes.tres"
	ResourceSaver.save(_mk_grad(Color(1, 0, 0, 1)), p)
	var custom: int = ResourceUID.create_id()
	ResourceUID.add_id(custom, p)
	var uid_text := ResourceUID.id_to_text(custom)
	var l0 = ResourceLoader.load(p)
	var rep: Array = []
	for pair in [["reuse", ResourceLoader.CACHE_MODE_REUSE], ["replace", ResourceLoader.CACHE_MODE_REPLACE],
			["ignore", ResourceLoader.CACHE_MODE_IGNORE], ["repl_deep", ResourceLoader.CACHE_MODE_REPLACE_DEEP],
			["ign_deep", ResourceLoader.CACHE_MODE_IGNORE_DEEP]]:
		var m = ResourceLoader.load(p, "", pair[1])
		var u = ResourceLoader.load(uid_text)
		rep.append("%s:s%d/u%d" % [pair[0], 1 if is_same(m, l0) else 0, 1 if is_same(u, l0) else 0])
	_p("modes_same_as_l0=%s" % ",".join(rep))
	# REPLACE is an identity-stable refresh of the on-disk content
	var l0_col := _cols(l0)
	ResourceSaver.save(_mk_grad(Color(0, 1, 0, 1)), p)
	var after_reuse = ResourceLoader.load(p)
	var after_replace = ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REPLACE)
	_p("stale_reuse_same=%s stale_reuse_col=%s replace_same_obj=%s replace_col=%s" % [
		_b(is_same(after_reuse, l0)), _cols(after_reuse),
		_b(is_same(after_replace, l0)), _cols(after_replace)])
	# load-by-uid follows the path cache and keeps the source path
	var lu = ResourceLoader.load(uid_text)
	_p("uid_after_replace_same=%s uid_path_kept=%s" % [
		_b(is_same(lu, l0)), _b(lu.resource_path == p)])
	_emit("modes")

func _arm_import() -> void:
	var proj := BASE + "/iproj"
	var gproj := _g(proj)
	DirAccess.make_dir_recursive_absolute(gproj)
	_w(proj + "/project.godot",
		"[application]\nconfig/name=\"R104E0Import\"\nconfig/features=PackedStringArray(\"4.7\")\n")
	var img := Image.create(2, 2, false, Image.FORMAT_RGBA8)
	img.fill(Color(1, 0, 0, 1))
	img.save_png(proj + "/tex.png")
	_w(proj + "/reader.gd",
		"extends SceneTree\n" +
		"func _initialize() -> void:\n" +
		"\tvar src := \"res://tex.png\"\n" +
		"\tvar u: String = ResourceUID.path_to_uid(src)\n" +
		"\tvar a = ResourceLoader.load(src)\n" +
		"\tvar b = ResourceLoader.load(u) if u.begins_with(\"uid://\") else null\n" +
		"\tprint(\"CHILD uid_is_uid=%s same=%s exists_uid=%s cls=%s\" % [" +
		"\"true\" if u.begins_with(\"uid://\") else \"false\", " +
		"\"true\" if (a != null and b != null and is_same(a, b)) else \"false\", " +
		"\"true\" if ResourceLoader.exists(u) else \"false\", " +
		"a.get_class() if a != null else \"null\"])\n" +
		"\tquit(0)\n")
	# The child process is spawned with a bounded retry: this host intermittently
	# launches a headless child with a null getcwd ("Parameter getcwd(...) is null"
	# at drivers/unix/dir_access_unix.cpp:739 -> "Invalid project path ... aborting"),
	# which is a spawn-environment flake, not a fixture assertion. Retrying keeps the
	# arm's *outcome* fields (cache/import/uid identity) deterministic; the attempt
	# count is printed as a diagnostic only, never pinned.
	var imp := {"code": -1, "text": ""}
	var tries := 0
	while tries < 4 and DirAccess.dir_exists_absolute(gproj):
		tries += 1
		imp = _spawn(gproj, "", ["--import"])
		if FileAccess.file_exists(proj + "/.godot/uid_cache.bin"):
			break
	var cache_exists := FileAccess.file_exists(proj + "/.godot/uid_cache.bin")
	var import_file := FileAccess.file_exists(proj + "/tex.png.import")
	var read := _spawn_reader(gproj, "res://reader.gd")
	var line := _child_line(read["text"], "CHILD ")
	print("R104 import_tries=%d reader_tries=%d" % [tries, read["tries"]])
	_p("import_code=%d cache_written=%s import_file_written=%s reader_code=%d" % [
		imp["code"], _b(cache_exists), _b(import_file), read["code"]])
	_p("uid_is_uid=%s same_by_uid=%s exists_uid=%s cls=%s" % [
		_child_field(line, "uid_is_uid"), _child_field(line, "same"),
		_child_field(line, "exists_uid"), _child_field(line, "cls")])
	_emit("import")

func _arm_persist() -> void:
	var proj := BASE + "/xproj"
	var gproj := _g(proj)
	DirAccess.make_dir_recursive_absolute(gproj + "/.godot")
	_w(proj + "/project.godot",
		"[application]\nconfig/name=\"R104E0Persist\"\nconfig/features=PackedStringArray(\"4.7\")\n")
	_w(proj + "/target.txt", "hello\n")
	var id := ResourceUID.text_to_id("uid://bqk3m5n7qar1")
	var cf := FileAccess.open(proj + "/.godot/uid_cache.bin", FileAccess.WRITE)
	cf.store_32(1)
	cf.store_64(id)
	var b := "res://target.txt".to_utf8_buffer()
	cf.store_32(b.size())
	cf.store_buffer(b)
	cf.close()
	var bytes := FileAccess.get_file_as_bytes(proj + "/.godot/uid_cache.bin").size()
	_w(proj + "/reader.gd",
		"extends SceneTree\n" +
		"func _initialize() -> void:\n" +
		"\tvar u: String = ResourceUID.path_to_uid(\"res://target.txt\")\n" +
		"\tvar tid: int = ResourceUID.text_to_id(\"uid://bqk3m5n7qar1\")\n" +
		"\tprint(\"CHILD uid_is_uid=%s back=%s has_id=%s id_path=%s\" % [" +
		"\"true\" if u.begins_with(\"uid://\") else \"false\", " +
		"ResourceUID.uid_to_path(u), " +
		"\"true\" if ResourceUID.has_id(tid) else \"false\", " +
		"ResourceUID.get_id_path(tid)])\n" +
		"\tquit(0)\n")
	var read := _spawn_reader(gproj, "res://reader.gd")
	var line := _child_line(read["text"], "CHILD ")
	print("R104 persist_reader_tries=%d" % read["tries"])
	_p("cache_bytes=%d reader_code=%d" % [bytes, read["code"]])
	_p("uid_is_uid=%s back_is_target=%s has_id=%s id_path_is_target=%s" % [
		_child_field(line, "uid_is_uid"),
		_b(_child_field(line, "back") == "res://target.txt"),
		_child_field(line, "has_id"),
		_b(_child_field(line, "id_path") == "res://target.txt")])
	_emit("persist")

func _arm_missing() -> void:
	var ghost: int = ResourceUID.create_id()
	var ghost_text := ResourceUID.id_to_text(ghost)
	_p("ghost_has_id=%s ghost_path_empty=%s ghost_uid_to_path_empty=%s" % [
		_b(ResourceUID.has_id(ghost)), _b(ResourceUID.get_id_path(ghost) == ""),
		_b(ResourceUID.uid_to_path(ghost_text) == "")])
	var bogus: int = ResourceUID.text_to_id("uid://zzzzzzzzzzzzzzz")
	var bogus_text := ResourceUID.id_to_text(bogus)
	var bogus_path: String = ResourceUID.uid_to_path(bogus_text)
	var bogus_echo: String = ResourceUID.path_to_uid(BASE + "/never.tres")
	_p("bogus_in_range=%s bogus_has_id=%s bogus_path_empty=%s absent_path_echo_is_path=%s" % [
		_b(bogus >= 0), _b(ResourceUID.has_id(bogus)), _b(bogus_path == ""),
		_b(bogus_echo == BASE + "/never.tres")])
	var unknown_load = ResourceLoader.load("uid://bqk3m5n7qar1")
	var unknown_exists := ResourceLoader.exists("uid://bqk3m5n7qar1")
	_p("unknown_uid_load_null=%s unknown_uid_exists=%s" % [
		_b(unknown_load == null), _b(unknown_exists)])
	var id_zero := ResourceUID.text_to_id("uid://")
	_p("id_zero_encodes=%s id_zero_has_id=%s" % [
		ResourceUID.id_to_text(id_zero), _b(ResourceUID.has_id(id_zero))])
	_emit("missing")
