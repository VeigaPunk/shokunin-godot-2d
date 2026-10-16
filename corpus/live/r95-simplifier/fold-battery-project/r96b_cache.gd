extends SceneTree
# r96-boundary probe D — cache-mode attack on the scout's L9
# ("REUSE stale / REPLACE identity-stable refresh / IGNORE fresh, path kept").
# Exercises the two DEEP modes the census lists but the scout never ran, the
# shallow-vs-deep refresh of an *external* dependency (hot-reload question), the
# timing/mtime boundary of REUSE staleness, and threaded loading.
#
# Launch: godot --headless --path proj --script res://r96b_cache.gd -- --arm=<arm>
# Arms: deep repl_uncached reuse_delete reuse_delay ignoredeep threaded
var arm := ""
const BASE := "user://r96b"

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"deep_reuse": _arm_deep("reuse", ResourceLoader.CACHE_MODE_REUSE)
		"deep_replace": _arm_deep("replace", ResourceLoader.CACHE_MODE_REPLACE)
		"deep_ignore": _arm_deep("ignore", ResourceLoader.CACHE_MODE_IGNORE)
		"deep_repl_deep": _arm_deep("replace_deep", ResourceLoader.CACHE_MODE_REPLACE_DEEP)
		"deep_ign_deep": _arm_deep("ignore_deep", ResourceLoader.CACHE_MODE_IGNORE_DEEP)
		"repl_uncached": _arm_repl_uncached()
		"reuse_delete": _arm_reuse_delete()
		"reuse_delay": _arm_reuse_delay()
		"ignoredeep": _arm_ignoredeep()
		"threaded": _arm_threaded()
		_: print("FAIL r96b_cache %s reason=unknown_arm" % arm)
	_wipe()
	quit(0)

# ------------------------------------------------------------------ utilities

func _ensure_base() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)

func _wipe() -> void:
	if not DirAccess.dir_exists_absolute(BASE):
		return
	for f in DirAccess.get_files_at(BASE):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(BASE + "/" + f))

func _b(v: bool) -> String:
	return "true" if v else "false"

func _cols(g) -> String:
	return "none" if g == null else str(g.colors)

func _write_grad(path: String, c: Color) -> int:
	var g := Gradient.new()
	g.colors = PackedColorArray([c, Color(0, 0, 0, 1)])
	return ResourceSaver.save(g, path)

func _mk_scene(ext_path: String) -> int:
	var root := Node2D.new()
	root.name = "CacheRoot"
	var line := Line2D.new()
	line.name = "CacheLine"
	line.gradient = ResourceLoader.load(ext_path)
	root.add_child(line)
	line.owner = root
	var ps := PackedScene.new()
	ps.pack(root)
	root.free()
	return ResourceSaver.save(ps, BASE + "/sc.tscn")

func _child_grad(sc) -> Object:
	if sc == null:
		return null
	var inst = sc.instantiate()
	if inst == null:
		return null
	var g = inst.get_child(0).gradient
	inst.free()
	return g

var _parts: PackedStringArray = []

func _p(part: String) -> void:
	_parts.append(part)

func _emit(arm_name: String) -> void:
	print("PASS r96b_cache %s %s" % [arm_name, " ".join(_parts)])
	_parts.clear()

# ------------------------------------------------------------------ arms

func _arm_deep(mode_name: String, mode: int) -> void:
	# one mode per process: no ordering contamination between modes
	_ensure_base()
	var dep := BASE + "/dep.tres"
	var e0 := _write_grad(dep, Color(1, 0, 0, 1))
	var e1 := _mk_scene(dep)
	var sc0 = ResourceLoader.load(BASE + "/sc.tscn")
	var dep0 = ResourceLoader.load(dep)
	var ch0 = _child_grad(sc0)
	var col_before := _cols(ch0)
	var e2 := _write_grad(dep, Color(0, 1, 0, 1))
	var sc = ResourceLoader.load(BASE + "/sc.tscn", "", mode)
	var ch = _child_grad(sc)
	var col_after := _cols(ch)
	var dep_after := _cols(dep0)
	var cached_dep := _cols(ResourceLoader.load(dep))
	print("R96B cache deep mode=%s sc_same=%s ch_col=%s ch_same=%s dep_obj_col=%s cached_dep_col=%s" % [
		mode_name, _b(is_same(sc, sc0)), col_after, _b(is_same(ch, ch0)), dep_after, cached_dep])
	_p("mode=%s save_dep=%s save_sc=%s col_before=%s sc_same=%s ch_col=%s ch_same=%s dep_obj_col=%s cached_dep_col=%s sc_path_kept=%s" % [
		mode_name, error_string(e0), error_string(e1), col_before, _b(is_same(sc, sc0)),
		col_after, _b(is_same(ch, ch0)), dep_after, cached_dep,
		_b(sc.resource_path == BASE + "/sc.tscn")])
	sc0 = null
	dep0 = null
	ch0 = null
	sc = null
	ch = null
	_emit("deep_" + mode_name)

func _arm_repl_uncached() -> void:
	_ensure_base()
	var p := BASE + "/ru.tres"
	_write_grad(p, Color(1, 0, 0, 1))
	var a = ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REPLACE)
	var b = ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REPLACE)
	var c = ResourceLoader.load(p)
	_p("first_col=%s second_same=%s cached_after=%s cached_same=%s" % [
		_cols(a), _b(is_same(a, b)), _b(c != null), _b(is_same(a, c))])
	a = null
	b = null
	c = null
	_emit("repl_uncached")

func _arm_reuse_delete() -> void:
	_ensure_base()
	var p := BASE + "/rd.tres"
	_write_grad(p, Color(1, 0, 0, 1))
	var a = ResourceLoader.load(p)
	var del_ok := DirAccess.remove_absolute(ProjectSettings.globalize_path(p))
	var b = ResourceLoader.load(p)
	var c = ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REUSE)
	_p("del=%s after_delete_same=%s after_delete_col=%s reuse_same=%s exists=%s" % [
		_b(del_ok == OK), _b(is_same(a, b)), _cols(b), _b(is_same(a, c)), _b(ResourceLoader.exists(p))])
	a = null
	b = null
	c = null
	_emit("reuse_delete")

func _arm_reuse_delay() -> void:
	_ensure_base()
	var p := BASE + "/rt.tres"
	_write_grad(p, Color(1, 0, 0, 1))
	var a = ResourceLoader.load(p)
	_write_grad(p, Color(0, 1, 0, 1))
	var b = ResourceLoader.load(p)
	OS.delay_msec(2500)
	var c = ResourceLoader.load(p)
	var d = ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REUSE)
	_p("immediate_same=%s immediate_col=%s after2500ms_same=%s after2500ms_col=%s reuse_same=%s" % [
		_b(is_same(a, b)), _cols(b), _b(is_same(a, c)), _cols(c), _b(is_same(a, d))])
	a = null
	b = null
	c = null
	d = null
	_emit("reuse_delay")

func _arm_ignoredeep() -> void:
	_ensure_base()
	var dep := BASE + "/idep.tres"
	_write_grad(dep, Color(1, 0, 0, 1))
	_mk_scene(dep)
	var cached_sc = ResourceLoader.load(BASE + "/sc.tscn")
	var cached_dep = ResourceLoader.load(dep)
	var fresh_sc = ResourceLoader.load(BASE + "/sc.tscn", "", ResourceLoader.CACHE_MODE_IGNORE_DEEP)
	var fresh_dep = ResourceLoader.load(dep)
	var ch = _child_grad(fresh_sc)
	var after_sc = ResourceLoader.load(BASE + "/sc.tscn")
	_p("fresh_sc_same_cached=%s fresh_sc_path_kept=%s fresh_child_same_cached_dep=%s after_sc_same_cached=%s fresh_dep_same_cached=%s" % [
		_b(is_same(fresh_sc, cached_sc)), _b(fresh_sc.resource_path == BASE + "/sc.tscn"),
		_b(is_same(ch, cached_dep)), _b(is_same(after_sc, cached_sc)), _b(is_same(fresh_dep, cached_dep))])
	cached_sc = null
	cached_dep = null
	fresh_sc = null
	fresh_dep = null
	after_sc = null
	_emit("ignoredeep")

func _arm_threaded() -> void:
	_ensure_base()
	var p := BASE + "/th.tres"
	_write_grad(p, Color(1, 0, 0, 1))
	var req := ResourceLoader.load_threaded_request(p)
	var status := -99
	for i in 200:
		status = ResourceLoader.load_threaded_get_status(p)
		if status == ResourceLoader.THREAD_LOAD_LOADED or status == ResourceLoader.THREAD_LOAD_FAILED or status == ResourceLoader.THREAD_LOAD_INVALID_RESOURCE:
			break
		OS.delay_msec(2)
	var got = null
	if status == ResourceLoader.THREAD_LOAD_LOADED:
		got = ResourceLoader.load_threaded_get(p)
	var cached_after = ResourceLoader.load(p)
	var again = ResourceLoader.load_threaded_get_status(p)
	_p("req=%s status=%d got_col=%s cached_same_as_got=%s status_after=%d has_cached=%s" % [
		error_string(req), status, _cols(got), _b(is_same(cached_after, got)), again,
		_b(ResourceLoader.has_cached(p))])
	got = null
	cached_after = null
	_emit("threaded")
