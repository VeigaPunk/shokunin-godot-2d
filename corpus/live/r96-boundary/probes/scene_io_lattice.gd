extends SceneTree
# r96 scout FROZEN probe — PackedScene / ResourceSaver / ResourceLoader round-trip lattice.
# Battery launch shape:
#   godot --headless --path proj --script res://scene_io_lattice.gd -- --arm=<name>
# Arm parse is the battery convention (OS.get_cmdline_user_args + "--arm=" prefix
# scan); every arm prints its own name on the PASS line, so a silent `_:` fallback
# is impossible to miss.  Exactly ONE `PASS scene_io_lattice <arm> <k=v> ...` line
# per arm is the authorable signature; `R96 <arm> ...` lines are diagnostics.
# No instance ids / RIDs / addresses / process-dependent tokens are printed; all
# paths are relative to the fixed user://r96 base (removed again by _wipe()).
#
# Measured laws encoded here (all [M], see reports/round-96/r96-scout.md):
#   L1 `PackedScene.pack()` is an INSTANCE method returning Error; an empty
#      PackedScene has can_instantiate()=false; `Resource.bundled` is the only
#      PackedScene property
#   L2 pack() keeps a node only if node.owner == the pack root: ownerless nodes and
#      nodes owned by an intermediate node are dropped; set_owner refuses a
#      non-ancestor and self (owner stays null)
#   L3 a save is byte-stable for one in-memory resource, but a *scene* save is NOT
#      byte-stable across processes: every node carries a random `unique_id=` in
#      the .tscn/.scn
#   L4 subresource ids (id="Gradient_xxxxx") are minted at first save from
#      resource_scene_unique_id (settable => pinnable); ext_resource ids (1_xxxxx)
#      are random per save and NOT controllable through set_id_for_path
#   L5 byte determinism recipe: pin the bundle node_ids + resource_scene_unique_id
#      => the saved .tscn is byte-identical across processes (sha256 pinned below)
#   L6 headless saves never emit uid:// and never mint one: no header uid, no ext
#      uid, get_resource_id_for_path / get_resource_uid stay -1 for saved paths,
#      and ResourceUID registration does not change the emitted text
#   L7 plain resources (.tres/.res) ARE byte-stable across processes; a PackedScene
#      saved as .scn and as .res is the same binary; unknown extensions are refused
#      with ERR_FILE_UNRECOGNIZED(15), silently (no engine ERROR) and create nothing
#   L8 ResourceSaver.save does not set resource_path and does not create missing
#      directories (ERR_CANT_OPEN(19)); take_over_path / set_path DO claim the cache
#   L9 CACHE_MODE_REPLACE reloads the on-disk content into the SAME cached object
#      (identity-stable refresh); CACHE_MODE_IGNORE returns a fresh uncached object
#      that still carries resource_path; default REUSE returns stale content after
#      an external write
#  L10 subresources are shared by every instantiation AND with the source object
#      (mutations leak) unless resource_local_to_scene = true
#  L11 FLAG_CHANGE_PATH is a no-op on this build; FLAG_BUNDLE_RESOURCES inlines
#      external resources as sub_resources; FLAG_COMPRESS shrinks .res; a
#      BIG_ENDIAN .res reloads as zeroed data (no endian detection)
#  L12 the four GEN_EDIT_STATE_* values are observationally identical in headless;
#      set_editable_instance / scene_instance_load_placeholder round-trip in memory
#  L13 a relative save path resolves against the project dir (engine CWD)

var arm := ""
const BASE := "user://r96"

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"census": _arm_census()
		"pack_basic": _arm_pack_basic()
		"ownership": _arm_ownership()
		"formats": _arm_formats()
		"det": _arm_det()
		"uid": _arm_uid()
		"takeover": _arm_takeover()
		"cache": _arm_cache()
		"subres": _arm_subres()
		"extres": _arm_extres()
		"editstate": _arm_editstate()
		"refuse": _arm_refuse()
		"edges": _arm_edges()
		_: print("FAIL scene_io_lattice %s reason=unknown_arm" % arm)
	_wipe()
	quit(0)

# ------------------------------------------------------------------ utilities

func _b(v: bool) -> String:
	return "true" if v else "false"

func _sha(p: String) -> String:
	var f := FileAccess.open(p, FileAccess.READ)
	if f == null:
		return "none"
	var bytes := f.get_buffer(f.get_length())
	f.close()
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(bytes)
	return ctx.finish().hex_encode()

func _size(p: String) -> int:
	var f := FileAccess.open(p, FileAccess.READ)
	if f == null:
		return -1
	var n := f.get_length()
	f.close()
	return n

func _text(p: String) -> String:
	var f := FileAccess.open(p, FileAccess.READ)
	if f == null:
		return "<none>"
	var t := f.get_as_text()
	f.close()
	return t

func _head(p: String) -> String:
	return _text(p).split("\n")[0]

func _err(code: int) -> String:
	return "%s(%d)" % [error_string(code), code]

func _pack(n: Node) -> PackedScene:
	var ps := PackedScene.new()
	ps.pack(n)
	return ps

func _names(st: SceneState) -> String:
	var out := PackedStringArray()
	for i in st.get_node_count():
		out.append(st.get_node_name(i))
	return ",".join(out)

func _mk_root(name: String) -> Node2D:
	var r := Node2D.new()
	r.name = name
	return r

func _mk_child(parent: Node, name: String, pos: Vector2) -> Node2D:
	var c := Node2D.new()
	c.name = name
	c.position = pos
	parent.add_child(c)
	c.owner = parent
	return c

func _ensure_base() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)

func _wipe() -> void:
	if not DirAccess.dir_exists_absolute(BASE):
		return
	for f in DirAccess.get_files_at(BASE):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(BASE + "/" + f))

func _subid(text: String) -> String:
	var idpos := text.find("id=\"")
	if idpos < 0:
		return ""
	var rest := text.substr(idpos + 4)
	return rest.substr(0, rest.find("\""))

var _parts: PackedStringArray = []

func _p(part: String) -> void:
	_parts.append(part)

func _emit(arm_name: String) -> void:
	print("PASS scene_io_lattice %s %s" % [arm_name, " ".join(_parts)])
	_parts.clear()

func _mask_unique(t: String) -> String:
	var out := t
	var pos := out.find("unique_id=")
	while pos >= 0:
		var end := pos + 10
		while end < out.length() and out[end] >= "0" and out[end] <= "9":
			end += 1
		out = out.substr(0, pos + 10) + "#" + out.substr(end, out.length() - end)
		pos = out.find("unique_id=", pos + 11)
	return out

# ---------------------------------------------------------------------- arms

func _arm_census() -> void:
	var ps_methods := PackedStringArray()
	for m in ClassDB.class_get_method_list("PackedScene", true):
		ps_methods.append(m.name)
	ps_methods.sort()
	var saver_methods := PackedStringArray()
	for m in ClassDB.class_get_method_list("ResourceSaver", true):
		saver_methods.append(m.name)
	saver_methods.sort()
	var saver_consts := PackedStringArray()
	for c in ClassDB.class_get_integer_constant_list("ResourceSaver", true):
		saver_consts.append("%s=%d" % [c, ClassDB.class_get_integer_constant("ResourceSaver", c)])
	var loader_methods := PackedStringArray()
	for m in ClassDB.class_get_method_list("ResourceLoader", true):
		loader_methods.append(m.name)
	loader_methods.sort()
	var loader_consts := PackedStringArray()
	for c in ClassDB.class_get_integer_constant_list("ResourceLoader", true):
		loader_consts.append("%s=%d" % [c, ClassDB.class_get_integer_constant("ResourceLoader", c)])
	var uid_methods := PackedStringArray()
	for m in ClassDB.class_get_method_list("ResourceUID", true):
		uid_methods.append(m.name)
	uid_methods.sort()
	var uid_consts := PackedStringArray()
	for c in ClassDB.class_get_integer_constant_list("ResourceUID", true):
		uid_consts.append("%s=%d" % [c, ClassDB.class_get_integer_constant("ResourceUID", c)])
	var res_props := PackedStringArray()
	for p in ClassDB.class_get_property_list("Resource", true):
		res_props.append(p.name)
	res_props.sort()
	var ss_methods := PackedStringArray()
	for m in ClassDB.class_get_method_list("SceneState", true):
		ss_methods.append(m.name)
	ss_methods.sort()
	var ps_consts := PackedStringArray()
	for c in ClassDB.class_get_integer_constant_list("PackedScene", true):
		ps_consts.append("%s=%d" % [c, ClassDB.class_get_integer_constant("PackedScene", c)])
	print("R96 census engine=%s" % Engine.get_version_info().string)
	_p("ps_methods=%s ps_props=bundled ps_consts=%s" % [
		",".join(ps_methods), ",".join(ps_consts)])
	_p("saver_methods=%s saver_flags=%s" % [
		",".join(saver_methods), ",".join(saver_consts)])
	_p("loader_methods=%s loader_modes=%s" % [
		",".join(loader_methods), ",".join(loader_consts)])
	_p("uid_methods=%s uid_consts=%s" % [",".join(uid_methods), ",".join(uid_consts)])
	_p("res_props=%s" % ",".join(res_props))
	_p("ss_methods=%s" % ",".join(ss_methods))
	_p("empty_can_instantiate=%s pack_is_instance_method=true" % _b(PackedScene.new().can_instantiate()))
	_emit("census")

func _arm_pack_basic() -> void:
	_ensure_base()
	var root := _mk_root("Root")
	root.position = Vector2(10, 20)
	var child := _mk_child(root, "Child", Vector2(3, 4))
	var ps := _pack(root)
	var st := ps.get_state()
	var pcounts := PackedStringArray()
	for i in st.get_node_count():
		pcounts.append(str(st.get_node_property_count(i)))
	var path := BASE + "/basic.tscn"
	var e := ResourceSaver.save(ps, path)
	var sha1 := _sha(path)
	var size1 := _size(path)
	var text := _text(path)
	var head := _head(path)
	var back: PackedScene = ResourceLoader.load(path)
	var inst := back.instantiate()
	var kid := inst.get_child(0)
	var path2 := BASE + "/basic2.tscn"
	var e2 := ResourceSaver.save(back, path2)
	print("R96 pack_basic head=%s text=%s" % [head, _mask_unique(text).replace("\n", "|")])
	_p("save=%s can=%s nodes=%d names=%s pcounts=%s types=%s state_path_empty=%s header=%s has_uid=%s has_unique_id=%s size_in_190_200=%s sha_len=%d" % [
		_err(e), _b(ps.can_instantiate()), st.get_node_count(), _names(st), ",".join(pcounts),
		"%s,%s" % [st.get_node_type(0), st.get_node_type(1)], _b(st.get_path() == ""), head,
		_b("uid=" in head), _b("unique_id=" in text), _b(size1 >= 190 and size1 <= 200), sha1.length()])
	_p("inst_name=%s inst_pos=%s kids=%d kid_name=%s kid_pos=%s kid_owner_root=%s scene_file_is_path=%s back_path_is_path=%s resave=%s resave_same_in_process=%s load_cached_identity=%s" % [
		inst.name, str(inst.position), inst.get_child_count(), kid.name, str(kid.position),
		_b(kid.owner == inst), _b(inst.scene_file_path == path), _b(back.resource_path == path),
		_err(e2), _b(_sha(path2) == sha1), _b(is_same(ResourceLoader.load(path), back))])
	inst.free()
	root.free()
	_emit("pack_basic")

func _arm_ownership() -> void:
	_ensure_base()
	var root := _mk_root("Root")
	var owned := _mk_child(root, "Owned", Vector2(1, 1))
	var orphan := Node2D.new()
	orphan.name = "Orphan"
	root.add_child(orphan)
	var deep := Node2D.new()
	deep.name = "Deep"
	owned.add_child(deep)
	deep.owner = owned
	var ps := _pack(root)
	var st := ps.get_state()
	var path := BASE + "/own.tscn"
	var e := ResourceSaver.save(ps, path)
	var text := _text(path)
	var other := Node2D.new()
	other.name = "Other"
	var bad := Node2D.new()
	bad.name = "Bad"
	root.add_child(bad)
	bad.owner = other
	var bad_owner_null := bad.owner == null
	var selfown := Node2D.new()
	selfown.name = "SelfOwn"
	root.add_child(selfown)
	selfown.owner = selfown
	var self_owner_null := selfown.owner == null
	var cleared := Node2D.new()
	cleared.name = "Cleared"
	root.add_child(cleared)
	cleared.owner = root
	cleared.owner = null
	var sub := _mk_child(root, "SubRoot", Vector2.ZERO)
	var ps2 := _pack(sub)
	var r3 := _mk_root("R3")
	_mk_child(r3, "C3", Vector2(1, 2))
	var ps3 := _pack(r3)
	var inst := ps.instantiate()
	var owner_paths := PackedStringArray()
	for i in st.get_node_count():
		owner_paths.append("%s:%s:%s" % [st.get_node_name(i), st.get_node_path(i), st.get_node_owner_path(i)])
	print("R96 ownership text=%s" % _mask_unique(text).replace("\n", "|"))
	_p("save=%s packed_nodes=%d packed_names=%s orphan_dropped=%s deep_dropped=%s bad_owner_refused=%s self_owner_refused=%s cleared_owner_null=%s" % [
		_err(e), st.get_node_count(), _names(st), _b(not ("Orphan" in _names(st))),
		_b(not ("Deep" in _names(st))), _b(bad_owner_null), _b(self_owner_null), _b(cleared.owner == null)])
	_p("child_of_tree_nodes=%d unparented_nodes=%d inst_child_owner_root=%s owner_paths=%s" % [
		ps2.get_state().get_node_count(), ps3.get_state().get_node_count(),
		_b(inst.get_child(0).owner == inst), ",".join(owner_paths)])
	inst.free()
	root.free()
	r3.free()
	other.free()
	_emit("ownership")

func _arm_formats() -> void:
	_ensure_base()
	var grad := Gradient.new()
	grad.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 0, 1, 1)])
	var res_tres := BASE + "/fmt.tres"
	var res_res := BASE + "/fmt.res"
	var e_tres := ResourceSaver.save(grad, res_tres)
	var e_res := ResourceSaver.save(grad, res_res)
	var back_tres = ResourceLoader.load(res_tres)
	var back_res = ResourceLoader.load(res_res)
	var refused := PackedStringArray()
	for ext: String in ["tscn", "tres.bak", "resx", "json"]:
		refused.append("%s=%s" % [ext, _err(ResourceSaver.save(grad, BASE + "/ref." + ext))])
	var root := _mk_root("FmtRoot")
	var ps := _pack(root)
	var scn := BASE + "/scene.scn"
	var res2 := BASE + "/scene.res"
	var e_scn := ResourceSaver.save(ps, scn)
	var e_res2 := ResourceSaver.save(ps, res2)
	var scene_tres_refused := ResourceSaver.save(ps, BASE + "/scene.tres")
	print("R96 formats tres_text=%s" % _text(res_tres).replace("\n", "|"))
	_p("grad_tres=%s size=%d sha=%s header=%s colors_match=%s grad_res=%s size=%d sha=%s magic=%s colors_match=%s text_eq_bin=%s" % [
		_err(e_tres), _size(res_tres), _sha(res_tres), _head(res_tres),
		_b(back_tres != null and back_tres.colors == grad.colors),
		_err(e_res), _size(res_res), _sha(res_res), _head(res_res),
		_b(back_res != null and back_res.colors == grad.colors),
		_b(FileAccess.get_file_as_bytes(res_tres) == FileAccess.get_file_as_bytes(res_res))])
	_p("grad_refused=%s refused_files_absent=%s scene_scn=%s scene_res=%s scn_eq_res=%s both_reload=%s scene_tres_refused=%s" % [
		",".join(refused),
		_b(not FileAccess.file_exists(BASE + "/ref.tscn") and not FileAccess.file_exists(BASE + "/ref.json")),
		_err(e_scn), _err(e_res2),
		_b(FileAccess.get_file_as_bytes(scn) == FileAccess.get_file_as_bytes(res2)),
		_b((ResourceLoader.load(scn) as PackedScene).can_instantiate() and (ResourceLoader.load(res2) as PackedScene).can_instantiate()),
		_err(scene_tres_refused)])
	root.free()
	_emit("formats")

func _arm_det() -> void:
	_ensure_base()
	var mk := func() -> PackedScene:
		var r := _mk_root("DetRoot")
		r.position = Vector2(5, 6)
		var line := Line2D.new()
		line.name = "Line"
		var g := Gradient.new()
		g.colors = PackedColorArray([Color(0.1, 0.2, 0.3, 1), Color(0.4, 0.5, 0.6, 1)])
		line.gradient = g
		r.add_child(line)
		line.owner = r
		var ps := _pack(r)
		r.free()
		return ps
	var a: PackedScene = mk.call()
	var b: PackedScene = mk.call()
	var p1 := BASE + "/det1.tscn"
	var p2 := BASE + "/det2.tscn"
	var p3 := BASE + "/det3.tscn"
	var e1 := ResourceSaver.save(a, p1)
	var e2 := ResourceSaver.save(b, p2)
	var e3 := ResourceSaver.save(a, p3)
	var text_a := _text(p1)
	var mk_pinned := func() -> PackedScene:
		var r := _mk_root("PinRoot")
		var line := Line2D.new()
		line.name = "PinLine"
		var g := Gradient.new()
		g.colors = PackedColorArray([Color(0.25, 0.5, 0.75, 1), Color(0, 0, 0, 1)])
		g.resource_scene_unique_id = "subpinned"
		line.gradient = g
		r.add_child(line)
		line.owner = r
		var ps := _pack(r)
		var d: Dictionary = ps._get_bundled_scene()
		r.free()
		d["node_ids"] = [111111, 222222]
		var ps2 := PackedScene.new()
		ps2._set_bundled_scene(d)
		return ps2
	var ps_pin: PackedScene = mk_pinned.call()
	var ps_pin2: PackedScene = mk_pinned.call()
	var p4 := BASE + "/pin1.tscn"
	var p5 := BASE + "/pin2.tscn"
	var e4 := ResourceSaver.save(ps_pin, p4)
	var e5 := ResourceSaver.save(ps_pin2, p5)
	var text_pin := _text(p4)
	var bundle: Dictionary = a._get_bundled_scene()
	var bkeys := PackedStringArray()
	for k in bundle.keys():
		bkeys.append(str(k))
	bkeys.sort()
	var inst_pin := ps_pin.instantiate()
	print("R96 det text_a=%s" % _mask_unique(text_a).replace("\n", "|"))
	print("R96 det text_pin=%s" % text_pin.replace("\n", "|"))
	_p("save=%s same_obj_resave=%s unpinned_sha_len=%d two_builds_same=%s subid_minted=%s subid_settable=%s bundle_keys=%s bundle_version=%d node_ids_len=%d" % [
		_err(e1), _err(e3), _sha(p1).length(), _b(_sha(p1) == _sha(p2)),
		_b(_subid(text_a).begins_with("Gradient_")), _b("id=\"subpinned\"" in text_pin),
		",".join(bkeys), int(bundle.get("version", -1)), (bundle.get("node_ids") as Array).size()])
	_p("pinned_save=%s pinned_save2=%s pinned_sha=%s two_pinned_builds_same=%s pinned_unique_ids=%s instantiate_ok=%s" % [
		_err(e4), _err(e5), _sha(p4), _b(_sha(p4) == _sha(p5)),
		_b("unique_id=111111" in text_pin and "unique_id=222222" in text_pin), _b(inst_pin != null)])
	inst_pin.free()
	_emit("det")

func _arm_uid() -> void:
	_ensure_base()
	var created := ResourceUID.create_id()
	var created_text := ResourceUID.id_to_text(created)
	var created_unregistered := not ResourceUID.has_id(created)
	var created_path_empty := ResourceUID.get_id_path(created) == ""
	var sample := "uid://bqk3m5n7qar1"
	var sid := ResourceUID.text_to_id(sample)
	var bad := ResourceUID.text_to_id("not-a-uid")
	var grad := Gradient.new()
	var p := BASE + "/uid.tres"
	var e := ResourceSaver.save(grad, p)
	var head := _head(p)
	var saver_id_before := ResourceSaver.get_resource_id_for_path(p)
	var loader_uid_before := ResourceLoader.get_resource_uid(p)
	ResourceUID.add_id(4242, p)
	var uid_of_path_after := ResourceLoader.get_resource_uid(p)
	var saver_id_after := ResourceSaver.get_resource_id_for_path(p)
	var root := _mk_root("UidRoot")
	var line := Line2D.new()
	line.name = "UidLine"
	var ext := BASE + "/uid_ext.tres"
	ResourceSaver.save(grad, ext)
	ResourceUID.add_id(4343, ext)
	var loaded = ResourceLoader.load(ext)
	line.gradient = loaded
	root.add_child(line)
	line.owner = root
	var ps := _pack(root)
	var p2 := BASE + "/uid.tscn"
	var e2 := ResourceSaver.save(ps, p2)
	var text2 := _text(p2)
	print("R96 uid tres_head=%s scene_text=%s" % [head, _mask_unique(text2).replace("\n", "|")])
	_p("create_id_text_prefix=%s create_id_unregistered=%s get_id_path_unknown_empty=%s roundtrip=%d roundtrip_text=%s invalid_text=%d invalid_text_back=%s invalid_id=%d" % [
		_b(created_text.begins_with("uid://")), _b(created_unregistered), _b(created_path_empty), sid,
		ResourceUID.id_to_text(sid), bad, ResourceUID.id_to_text(bad), ResourceUID.INVALID_ID])
	_p("tres_save=%s header_has_uid=%s saver_id_before=%d loader_uid_before=%d loader_uid_after_add=%d saver_id_after_add=%d" % [
		_err(e), _b("uid=" in head), saver_id_before, loader_uid_before, uid_of_path_after, saver_id_after])
	_p("scene_save=%s ext_line_has_uid=%s header_has_uid=%s any_uid_token=%s" % [
		_err(e2), _b("uid=" in text2), _b("uid=" in _head(p2)), _b("uid://" in text2)])
	root.free()
	_emit("uid")

func _arm_takeover() -> void:
	_ensure_base()
	var a := Gradient.new()
	a.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 1, 0, 1)])
	var p := BASE + "/to.tres"
	var e := ResourceSaver.save(a, p)
	var path_after_save := a.resource_path
	var l1 = ResourceLoader.load(p)
	var b := Gradient.new()
	b.take_over_path(p)
	var after_b_is_b := is_same(ResourceLoader.load(p), b)
	var b_path := b.resource_path
	var a_path := a.resource_path
	var c := Gradient.new()
	c.take_over_path(p)
	var after_c_is_c := is_same(ResourceLoader.load(p), c)
	var b_displaced := b.resource_path == ""
	var disk_sha := _sha(p)
	_p("save=%s path_after_save_empty=%s load_after_save_is_new=%s b_wins=%s b_path_is_p=%s a_path_empty=%s c_wins=%s b_displaced=%s disk_sha=%s disk_unchanged=%s exists=%s exists_missing=%s has_cached=%s get_cached_ref=%s deps_empty=%s" % [
		_err(e), _b(path_after_save == ""), _b(not is_same(l1, a)), _b(after_b_is_b), _b(b_path == p),
		_b(a_path == ""), _b(after_c_is_c), _b(b_displaced), disk_sha, _b(disk_sha == _sha(p)),
		_b(ResourceLoader.exists(p)), _b(not ResourceLoader.exists(BASE + "/nope.tres")),
		_b(ResourceLoader.has_cached(p)), _b(ResourceLoader.get_cached_ref(p) != null),
		_b(ResourceLoader.get_dependencies(p).is_empty())])
	l1 = null
	_emit("takeover")

func _arm_cache() -> void:
	_ensure_base()
	var p := BASE + "/cache.tres"
	var a := Gradient.new()
	a.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 0, 0, 1)])
	var e := ResourceSaver.save(a, p)
	var cached = ResourceLoader.load(p)
	var same_default := is_same(ResourceLoader.load(p), cached)
	var ign = ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_IGNORE)
	var ign2 = ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_IGNORE)
	var b := Gradient.new()
	b.colors = PackedColorArray([Color(0, 1, 0, 1), Color(0, 0, 0, 1)])
	var e2 := ResourceSaver.save(b, p)
	var stale = ResourceLoader.load(p)
	var stale_colors := str(stale.colors)
	var repl = ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REPLACE)
	var repl_is_cached := is_same(repl, cached)
	var repl_colors := str(repl.colors)
	var after_repl_is_repl := is_same(ResourceLoader.load(p), repl)
	var ign3 = ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_IGNORE)
	var ign3_colors := str(ign3.colors)
	var reuse_mode := is_same(ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REUSE), repl)
	_p("save=%s default_identity=%s ignore_distinct=%s ignore_path_kept=%s ignore_two_distinct=%s" % [
		_err(e), _b(same_default), _b(not is_same(ign, cached)), _b(ign.resource_path == p), _b(not is_same(ign, ign2))])
	_p("external_write=%s stale_after_write=%s repl_same_object=%s repl_refreshed=%s after_repl_identity=%s ignore_refreshed=%s reuse_is_repl=%s cached_now_refreshed=%s exists_dir=%s exists_empty=%s" % [
		_err(e2), stale_colors, _b(repl_is_cached), repl_colors, _b(after_repl_is_repl),
		ign3_colors, _b(reuse_mode), str(cached.colors),
		_b(ResourceLoader.exists(BASE)), _b(ResourceLoader.exists(""))])
	cached = null
	stale = null
	repl = null
	ign = null
	ign2 = null
	ign3 = null
	_emit("cache")

func _arm_subres() -> void:
	_ensure_base()
	var root := _mk_root("SubRoot")
	var line := Line2D.new()
	line.name = "Line"
	var g := Gradient.new()
	g.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 0, 1, 1)])
	line.gradient = g
	root.add_child(line)
	line.owner = root
	var ps := _pack(root)
	var p := BASE + "/sub.tscn"
	var e := ResourceSaver.save(ps, p)
	var text := _text(p)
	var i1 := ps.instantiate()
	var i2 := ps.instantiate()
	var g1: Gradient = i1.get_child(0).gradient
	var g2: Gradient = i2.get_child(0).gradient
	var shared := is_same(g1, g2)
	var src_shared := is_same(g1, g)
	g1.colors = PackedColorArray([Color(0, 1, 0, 1), Color(1, 1, 0, 1)])
	var leak := g2.colors == g1.colors
	var root2 := _mk_root("LocalRoot")
	var line2 := Line2D.new()
	line2.name = "LocalLine"
	var g3 := Gradient.new()
	g3.resource_local_to_scene = true
	line2.gradient = g3
	root2.add_child(line2)
	line2.owner = root2
	var ps2 := _pack(root2)
	var p2 := BASE + "/sub_local.tscn"
	var e2 := ResourceSaver.save(ps2, p2)
	var text2 := _text(p2)
	var j1 := ps2.instantiate()
	var j2 := ps2.instantiate()
	var h1: Gradient = j1.get_child(0).gradient
	var h2: Gradient = j2.get_child(0).gradient
	h1.colors = PackedColorArray([Color(0, 0, 1, 1), Color(0, 1, 1, 1)])
	var local_leak := h2.colors == h1.colors
	var gt := GradientTexture2D.new()
	gt.gradient = g
	var spr := Sprite2D.new()
	spr.name = "Spr"
	spr.texture = gt
	var root3 := _mk_root("NestRoot")
	root3.add_child(spr)
	spr.owner = root3
	var ps3 := _pack(root3)
	var p3 := BASE + "/sub_nest.tscn"
	var e3 := ResourceSaver.save(ps3, p3)
	var text3 := _text(p3)
	var subid := _subid(text)
	var nested_shares_subid := subid != "" and ("SubResource(\"%s\")" % subid) in text3
	var dup_shallow = g.duplicate()
	var dup_deep = g.duplicate(true)
	print("R96 subres text=%s" % _mask_unique(text.replace(subid, "#")).replace("\n", "|"))
	print("R96 subres text_local=%s" % _mask_unique(text2).replace("\n", "|"))
	_p("save=%s subid=%s subid_present=%s shared_across_instances=%s shared_with_source=%s mutation_leaks=%s" % [
		_err(e), subid, _b("SubResource(" in text), _b(shared), _b(src_shared), _b(leak)])
	_p("local_save=%s flag_in_file=%s local_shared=%s local_leak=%s" % [
		_err(e2), _b("resource_local_to_scene = true" in text2), _b(is_same(h1, h2)), _b(local_leak)])
	_p("nest_save=%s nested_reuses_subid=%s dup_shallow_distinct=%s dup_deep_distinct=%s" % [
		_err(e3), _b(nested_shares_subid), _b(not is_same(dup_shallow, g)), _b(not is_same(dup_deep, g))])
	i1.free()
	i2.free()
	j1.free()
	j2.free()
	spr.texture = null
	gt = null
	root.free()
	root2.free()
	root3.free()
	_emit("subres")

func _arm_extres() -> void:
	_ensure_base()
	var grad := Gradient.new()
	grad.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 1, 0, 1)])
	var ext := BASE + "/ext.tres"
	var e_ext := ResourceSaver.save(grad, ext)
	var loaded = ResourceLoader.load(ext)
	var mk := func() -> PackedScene:
		var root := _mk_root("ExtRoot")
		var line := Line2D.new()
		line.name = "ExtLine"
		line.gradient = loaded
		root.add_child(line)
		line.owner = root
		var ps := _pack(root)
		root.free()
		return ps
	var ps1: PackedScene = mk.call()
	var ps2: PackedScene = mk.call()
	var p1 := BASE + "/ext1.tscn"
	var p2 := BASE + "/ext2.tscn"
	var p1b := BASE + "/ext1b.tscn"
	var e1 := ResourceSaver.save(ps1, p1)
	var e2 := ResourceSaver.save(ps2, p2)
	var e1b := ResourceSaver.save(ps1, p1b)
	var t1 := _text(p1)
	var t2 := _text(p2)
	var id1 := _subid(t1)
	var id2 := _subid(t2)
	var id1b := _subid(_text(p1b))
	var gen_id_len := str(loaded.generate_scene_unique_id()).length()
	var inst := ps1.instantiate()
	var inst2 := ps1.instantiate()
	var is_loaded := is_same(inst.get_child(0).gradient, loaded)
	var two_share := is_same(inst.get_child(0).gradient, inst2.get_child(0).gradient)
	var deps := ResourceLoader.get_dependencies(p1)
	var p3 := BASE + "/ext_bundle.tscn"
	var e3 := ResourceSaver.save(ps1, p3, ResourceSaver.FLAG_BUNDLE_RESOURCES)
	var t3 := _text(p3)
	var root4 := _mk_root("NoPathRoot")
	var line4 := Line2D.new()
	line4.name = "NoPathLine"
	line4.gradient = grad
	root4.add_child(line4)
	line4.owner = root4
	var ps4 := _pack(root4)
	var p4 := BASE + "/ext_nopath.tscn"
	var e4 := ResourceSaver.save(ps4, p4)
	var t4 := _text(p4)
	var p5 := BASE + "/ext_rel.tscn"
	var e5 := ResourceSaver.save(ps1, p5, ResourceSaver.FLAG_RELATIVE_PATHS)
	var t5 := _text(p5)
	print("R96 extres t1=%s" % _mask_unique(t1.replace(id1, "#")).replace("\n", "|"))
	print("R96 extres t3=%s" % _mask_unique(t3.replace(_subid(t3), "#")).replace("\n", "|"))
	print("R96 extres t4=%s" % _mask_unique(t4).replace("\n", "|"))
	_p("ext_save=%s save=%s save2=%s save_same_obj=%s ext_line=%s id_prefix=%s id_stable_across_saves=%s id_stable_same_obj_resave=%s gen_id_len=%d" % [
		_err(e_ext), _err(e1), _err(e2), _err(e1b), _b("ext_resource" in t1), _b(id1.begins_with("1_")),
		_b(id1 == id2), _b(id1 == id1b), gen_id_len])
	_p("inst_is_loaded=%s two_instances_share=%s inst_path_is_ext=%s deps=%s" % [
		_b(is_loaded), _b(two_share), _b(inst.get_child(0).gradient.resource_path == ext), str(deps)])
	_p("bundle_flag=%s inlined_as_subresource=%s no_ext_line=%s nopath_save=%s serialized_as_subresource=%s no_ext_line=%s relative_flag=%s keeps_path=%s" % [
		_err(e3), _b("sub_resource" in t3), _b(not ("ext_resource" in t3)),
		_err(e4), _b("sub_resource" in t4), _b(not ("ext_resource" in t4)),
		_err(e5), _b("path=\"user://r96/ext.tres\"" in t5)])
	inst.free()
	inst2.free()
	root4.free()
	loaded = null
	_emit("extres")

func _arm_editstate() -> void:
	_ensure_base()
	var root := _mk_root("EditRoot")
	_mk_child(root, "EditChild", Vector2(2, 3))
	var ps := _pack(root)
	var p := BASE + "/edit.tscn"
	var e := ResourceSaver.save(ps, p)
	var back: PackedScene = ResourceLoader.load(p)
	var rows := PackedStringArray()
	for state in [PackedScene.GEN_EDIT_STATE_DISABLED, PackedScene.GEN_EDIT_STATE_INSTANCE,
			PackedScene.GEN_EDIT_STATE_MAIN, PackedScene.GEN_EDIT_STATE_MAIN_INHERITED]:
		var inst := back.instantiate(state)
		var kid := inst.get_child(0)
		rows.append("s%d[kids=%d,owner=%s,name=%s,ph=%s,ed=%s]" % [
			state, inst.get_child_count(), _b(kid.owner == inst), inst.name,
			_b(kid.get_scene_instance_load_placeholder()), _b(inst.is_editable_instance(kid))])
		inst.free()
	var inst2 := back.instantiate()
	var kid2 := inst2.get_child(0)
	inst2.set_editable_instance(kid2, true)
	var editable_readback := inst2.is_editable_instance(kid2)
	kid2.set_scene_instance_load_placeholder(true)
	var placeholder_readback := kid2.get_scene_instance_load_placeholder()
	var unique_before := kid2.is_unique_name_in_owner()
	kid2.set_unique_name_in_owner(true)
	var unique_after := kid2.is_unique_name_in_owner()
	_p("save=%s states=%s scene_file_is_path=%s part_of_edited=%s" % [
		_err(e), "|".join(rows), _b(inst2.scene_file_path == p), _b(inst2.is_part_of_edited_scene())])
	_p("editable_readback=%s placeholder_readback=%s unique_name_before=%s unique_name_after=%s root_placeholder=%s" % [
		_b(editable_readback), _b(placeholder_readback), _b(unique_before), _b(unique_after),
		_b(inst2.get_scene_instance_load_placeholder())])
	inst2.free()
	root.free()
	back = null
	_emit("editstate")

func _arm_refuse() -> void:
	_ensure_base()
	var root := _mk_root("RefRoot")
	var ps := _pack(root)
	var empty := PackedScene.new()
	var missing_dir := "user://r96_absent_dir_xyz/deep/x.tscn"
	DirAccess.remove_absolute(ProjectSettings.globalize_path("user://r96_absent_dir_xyz"))
	var e_missing_dir := ResourceSaver.save(ps, missing_dir)
	var g := Gradient.new()
	var e_null := ResourceSaver.save(null, BASE + "/null.tscn")
	var e_empty_path := ResourceSaver.save(g, "")
	var e_no_ext := ResourceSaver.save(g, BASE + "/noext")
	var e_dir := ResourceSaver.save(g, BASE)
	var load_missing = ResourceLoader.load(BASE + "/nope.tscn")
	var load_dir = ResourceLoader.load(BASE)
	var load_empty = ResourceLoader.load("")
	var ps_null := PackedScene.new()
	var pack_null_err: int = ps_null.pack(null)
	var inst_empty = empty.instantiate()
	var rel_name := "r96_relative.tres"
	var e_rel := ResourceSaver.save(Gradient.new(), rel_name)
	var rel_exists := FileAccess.file_exists(rel_name)
	var p := BASE + "/collide.tres"
	ResourceSaver.save(Gradient.new(), p)
	var loaded = ResourceLoader.load(p)
	var other := Gradient.new()
	other.set_path(p)
	var collide_refused := other.resource_path == ""
	var in_project_dir := FileAccess.file_exists("res://" + rel_name)
	if in_project_dir:
		DirAccess.remove_absolute(ProjectSettings.globalize_path("res://" + rel_name))
	_p("save_missing_dir=%s no_file=%s save_null=%s save_empty_path=%s save_no_ext=%s save_dir=%s" % [
		_err(e_missing_dir), _b(not FileAccess.file_exists(missing_dir)), _err(e_null),
		_err(e_empty_path), _err(e_no_ext), _err(e_dir)])
	_p("load_missing_null=%s load_dir_null=%s load_empty_null=%s pack_null=%s empty_can_instantiate=%s empty_instantiate_null=%s" % [
		_b(load_missing == null), _b(load_dir == null), _b(load_empty == null),
		_err(pack_null_err), _b(empty.can_instantiate()), _b(inst_empty == null)])
	_p("relative_save=%s relative_file_created=%s relative_in_project_dir=%s deleted=%s set_path_collision_refused=%s" % [
		_err(e_rel), _b(rel_exists), _b(in_project_dir), _b(not FileAccess.file_exists(rel_name)), _b(collide_refused)])
	loaded = null
	root.free()
	_emit("refuse")

func _arm_edges() -> void:
	_ensure_base()
	var root := _mk_root("NameRoot")
	var ps := _pack(root)
	var p := BASE + "/edge.tscn"
	var e := ResourceSaver.save(ps, p)
	var back: PackedScene = ResourceLoader.load(p)
	var i1 := back.instantiate()
	var i2 := back.instantiate()
	var i3 := back.instantiate()
	var i4 := back.instantiate()
	var holder := Node.new()
	holder.name = "Holder"
	holder.add_child(i1)
	holder.add_child(i2)
	var added_names := "%s,%s" % [i1.name, i2.name]
	var ps_b := _pack(root)
	var packed_twice_same := is_same(ps_b, ps)
	var g_root := _mk_root("GRoot")
	var g_child := _mk_child(g_root, "GChild", Vector2.ZERO)
	g_child.add_to_group("grp_a", true)
	g_child.add_to_group("grp_b", true)
	var gps := _pack(g_root)
	var gst := gps.get_state()
	var gpath := BASE + "/grp.tscn"
	var ge := ResourceSaver.save(gps, gpath)
	var gtext := _text(gpath)
	var ginst := gps.instantiate()
	var inst_groups := PackedStringArray()
	for grp in ginst.get_child(0).get_groups():
		inst_groups.append(str(grp))
	inst_groups.sort()
	var o_root := _mk_root("ORoot")
	var o_child := _mk_child(o_root, "OChild", Vector2.ZERO)
	var o_grand := Node2D.new()
	o_grand.name = "OGrand"
	o_child.add_child(o_grand)
	o_grand.owner = o_root
	var ops := _pack(o_root)
	var ost := ops.get_state()
	var owner_paths := PackedStringArray()
	for i in ost.get_node_count():
		owner_paths.append("%s:%s:%s" % [ost.get_node_name(i), ost.get_node_path(i), ost.get_node_owner_path(i)])
	print("R96 edges groups_text=%s" % _mask_unique(gtext).replace("\n", "|"))
	_p("save=%s inst_names=%s,%s added_names=%s auto_renamed=%s state_path_is_p=%s duplicate_cls=%s packed_twice_same_object=%s" % [
		_err(e), i3.name, i4.name, added_names,
		_b(added_names != "NameRoot,NameRoot"), _b(back.get_state().get_path() == p),
		back.duplicate().get_class(), _b(packed_twice_same)])
	_p("groups_save=%s state_groups=%s inst_groups=%s owner_paths=%s" % [
		_err(ge), str(gst.get_node_groups(1)), ",".join(inst_groups), ",".join(owner_paths)])
	ginst.free()
	i3.free()
	i4.free()
	holder.free()
	root.free()
	g_root.free()
	o_root.free()
	_emit("edges")
