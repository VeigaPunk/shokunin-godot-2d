extends SceneTree
# r96 scout DISCOVERY probe — PackedScene / ResourceSaver / ResourceLoader round-trip.
# Launch shape:
#   godot --headless --path proj --script res://discover.gd -- --arm=<name>
# Prints `R96 <arm> <key>=<value>` diagnostics. NOT a battery row (discovery only).
# Everything is written under user://r96/ (never res://, never the tracked tree).

var arm := ""
var _garbage: Array[Node] = []
const BASE := "user://r96"

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"census": _census()
		"pack_basic": _pack_basic()
		"ownership": _ownership()
		"formats": _formats()
		"det": _det()
		"uid": _uid()
		"takeover": _takeover()
		"cache": _cache()
		"subres": _subres()
		"extres": _extres()
		"editstate": _editstate()
		"refuse": _refuse()
		"edges": _edges()
		_: print("R96 discover unknown_arm=%s" % arm)
	_free_all()
	quit(0)

func _free_all() -> void:
	for n in _garbage:
		if is_instance_valid(n):
			n.free()
	_garbage.clear()

func _mk(n: Node) -> Node:
	_garbage.append(n)
	return n

func _ensure_base() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)

# ------------------------------------------------------------------ utilities

func _sha(p: String) -> String:
	var f := FileAccess.open(p, FileAccess.READ)
	if f == null:
		return "none"
	var bytes := f.get_buffer(f.get_length())
	f.close()
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(bytes)
	return ctx.finish().hex_encode().substr(0, 16)

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

func _lines(p: String, n: int) -> String:
	var parts := _text(p).split("\n")
	var out := PackedStringArray()
	for i in range(min(n, parts.size())):
		out.append(parts[i])
	return "|".join(out)

func _methods(cls: String) -> String:
	var out := PackedStringArray()
	for m in ClassDB.class_get_method_list(cls, true):
		out.append(m.name)
	out.sort()
	return ",".join(out)

func _props(cls: String) -> String:
	var out := PackedStringArray()
	for p in ClassDB.class_get_property_list(cls, true):
		out.append(p.name)
	out.sort()
	return ",".join(out)

func _consts(cls: String) -> String:
	var out := PackedStringArray()
	for c in ClassDB.class_get_integer_constant_list(cls, true):
		out.append("%s=%d" % [c, ClassDB.class_get_integer_constant(cls, c)])
	return ",".join(out)

func _signals(cls: String) -> String:
	var out := PackedStringArray()
	for s in ClassDB.class_get_signal_list(cls, true):
		out.append(s.name)
	out.sort()
	return ",".join(out)

func _err(code: int) -> String:
	return "%s(%d)" % [error_string(code), code]

func _pack(n: Node) -> PackedScene:
	var ps := PackedScene.new()
	var e: int = ps.pack(n)
	if e != OK:
		print("R96 pack_error=%s" % _err(e))
	return ps

# ------------------------------------------------------------------- arms

func _census() -> void:
	print("R96 census godot=%s" % Engine.get_version_info().string)
	print("R96 census ps_methods=%s" % _methods("PackedScene"))
	print("R96 census ps_props=%s" % _props("PackedScene"))
	print("R96 census ps_consts=%s" % _consts("PackedScene"))
	print("R96 census ps_signals=%s" % _signals("PackedScene"))
	print("R96 census saver_methods=%s" % _methods("ResourceSaver"))
	print("R96 census saver_consts=%s" % _consts("ResourceSaver"))
	print("R96 census loader_methods=%s" % _methods("ResourceLoader"))
	print("R96 census loader_consts=%s" % _consts("ResourceLoader"))
	print("R96 census uid_methods=%s" % _methods("ResourceUID"))
	print("R96 census res_props=%s" % _props("Resource"))
	print("R96 census res_methods=%s" % _methods("Resource"))
	print("R96 census ss_methods=%s" % _methods("SceneState"))
	print("R96 census node_props_owner=%s" % _props("Node"))
	print("R96 census can_instantiate_empty=%s" % PackedScene.new().can_instantiate())

func _pack_basic() -> void:
	_ensure_base()
	var root := Node2D.new()
	root.name = "Root"
	root.position = Vector2(10, 20)
	var child := Sprite2D.new()
	child.name = "Child"
	child.position = Vector2(3, 4)
	root.add_child(child)
	child.owner = root
	var ps := _pack(root)
	print("R96 pack_basic cls=%s can=%s" % [ps.get_class(), ps.can_instantiate()])
	var st: SceneState = ps.get_state()
	var names := PackedStringArray()
	var types := PackedStringArray()
	var pcounts := PackedStringArray()
	for i in st.get_node_count():
		names.append(st.get_node_name(i))
		types.append(st.get_node_type(i))
		pcounts.append(str(st.get_node_property_count(i)))
	print("R96 pack_basic state_nodes=%d names=%s types=%s pcounts=%s path=%s" % [
		st.get_node_count(), ",".join(names), ",".join(types), ",".join(pcounts), st.get_path()])
	print("R96 pack_basic root_props=%s" % [_prop_dump(st, 0)])
	var path := BASE + "/basic.tscn"
	var err := ResourceSaver.save(ps, path)
	print("R96 pack_basic save=%s size=%d sha=%s" % [_err(err), _size(path), _sha(path)])
	print("R96 pack_basic head=%s" % _lines(path, 6))
	var back: PackedScene = ResourceLoader.load(path)
	print("R96 pack_basic back_cls=%s back_path=%s" % [back.get_class(), back.resource_path])
	var inst := back.instantiate()
	print("R96 pack_basic inst_name=%s inst_pos=%s scene_file=%s kids=%d kid=%s kid_pos=%s kid_owner=%s" % [
		inst.name, str(inst.position), inst.scene_file_path, inst.get_child_count(),
		inst.get_child(0).name, str(inst.get_child(0).position), inst.get_child(0).owner])
	print("R96 pack_basic inst_cls=%s resave=%s" % [inst.get_class(), _err(ResourceSaver.save(back, BASE + "/basic2.tscn"))])
	print("R96 pack_basic resave_sha=%s resave_same=%s" % [_sha(BASE + "/basic2.tscn"), _sha(BASE + "/basic2.tscn") == _sha(path)])

func _prop_dump(st: SceneState, idx: int) -> String:
	var out := PackedStringArray()
	for i in st.get_node_property_count(idx):
		out.append("%s=%s" % [st.get_node_property_name(idx, i), str(st.get_node_property_value(idx, i))])
	return "|".join(out)

func _ownership() -> void:
	_ensure_base()
	var root := Node2D.new()
	root.name = "Root"
	var owned := Node2D.new()
	owned.name = "Owned"
	var orphan := Node2D.new()
	orphan.name = "Orphan"
	var deep := Node2D.new()
	deep.name = "Deep"
	root.add_child(owned)
	root.add_child(orphan)
	owned.add_child(deep)
	owned.owner = root
	deep.owner = owned
	print("R96 ownership pre owner_orphan=%s owner_deep=%s" % [orphan.owner, deep.owner])
	var ps := _pack(root)
	var st: SceneState = ps.get_state()
	var names := PackedStringArray()
	for i in st.get_node_count():
		names.append(st.get_node_name(i))
	print("R96 ownership packed_nodes=%d names=%s" % [st.get_node_count(), ",".join(names)])
	var path := BASE + "/own.tscn"
	print("R96 ownership save=%s" % _err(ResourceSaver.save(ps, path)))
	print("R96 ownership text=%s" % _text(path).replace("\n", "|"))
	# owner = a non-ancestor
	var other := Node2D.new()
	other.name = "Other"
	var bad := Node2D.new()
	bad.name = "Bad"
	root.add_child(bad)
	bad.owner = other
	print("R96 ownership bad_owner_readback=%s" % bad.owner)
	# owner = self
	var selfown := Node2D.new()
	selfown.name = "SelfOwn"
	root.add_child(selfown)
	selfown.owner = selfown
	print("R96 ownership self_owner_readback=%s" % selfown.owner)
	# owner cleared after being set
	var cleared := Node2D.new()
	cleared.name = "Cleared"
	root.add_child(cleared)
	cleared.owner = root
	cleared.owner = null
	print("R96 ownership cleared_owner=%s" % cleared.owner)
	# pack a node that has a parent (root of pack is a child)
	var child_root := Node2D.new()
	child_root.name = "SubRoot"
	root.add_child(child_root)
	child_root.owner = root
	var ps2 := _pack(child_root)
	print("R96 ownership pack_child_of_tree can=%s nodes=%d" % [ps2.can_instantiate(), ps2.get_state().get_node_count()])
	# pack a node with an unowned root that itself has no owner but a child owned by it
	var r3 := Node2D.new()
	r3.name = "R3"
	var c3 := Node2D.new()
	c3.name = "C3"
	r3.add_child(c3)
	c3.owner = r3
	var ps3 := _pack(r3)
	print("R96 ownership pack_unparented nodes=%d" % ps3.get_state().get_node_count())

func _formats() -> void:
	_ensure_base()
	var grad := Gradient.new()
	grad.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 0, 1, 1)])
	for ext: String in ["tres", "res", "tscn", "tres.bak", "resx", "json"]:
		var p := BASE + "/fmt." + ext
		var err := ResourceSaver.save(grad, p)
		print("R96 formats grad.%s save=%s size=%d sha=%s head=%s" % [ext, _err(err), _size(p), _sha(p), _lines(p, 2)])
		if err == OK:
			var back = ResourceLoader.load(p)
			print("R96 formats grad.%s back_cls=%s eq=%s" % [ext, str(back.get_class()) if back != null else "null",
				str(back.colors) if back != null and back is Gradient else "n/a"])
	var root := Node2D.new()
	root.name = "FmtRoot"
	var ps := _pack(root)
	for ext: String in ["tscn", "scn", "tres", "res", "json"]:
		var p := BASE + "/scene." + ext
		var err := ResourceSaver.save(ps, p)
		print("R96 formats scene.%s save=%s size=%d sha=%s head=%s" % [ext, _err(err), _size(p), _sha(p), _lines(p, 2)])
		if err == OK:
			var back = ResourceLoader.load(p)
			print("R96 formats scene.%s back=%s can=%s" % [ext, str(back.get_class()) if back != null else "null",
				str(back.can_instantiate()) if back is PackedScene else "n/a"])
	# binary vs text same resource
	print("R96 formats grad_tres_eq_res=%s" % (FileAccess.get_file_as_bytes(BASE + "/fmt.tres") == FileAccess.get_file_as_bytes(BASE + "/fmt.res")))

func _det() -> void:
	_ensure_base()
	var mk := func() -> PackedScene:
		var r := Node2D.new()
		r.name = "DetRoot"
		r.position = Vector2(5, 6)
		var c := Line2D.new()
		c.name = "Line"
		var g := Gradient.new()
		g.colors = PackedColorArray([Color(0.1, 0.2, 0.3, 1), Color(0.4, 0.5, 0.6, 1)])
		c.gradient = g
		r.add_child(c)
		c.owner = r
		return _pack(r)
	var a: PackedScene = mk.call()
	var b: PackedScene = mk.call()
	var p1 := BASE + "/det1.tscn"
	var p2 := BASE + "/det2.tscn"
	var p3 := BASE + "/det3.tscn"
	print("R96 det a=%s b=%s" % [_err(ResourceSaver.save(a, p1)), _err(ResourceSaver.save(b, p2))])
	print("R96 det sha1=%s sha2=%s same_objs=%s" % [_sha(p1), _sha(p2), _sha(p1) == _sha(p2)])
	print("R96 det save_again=%s sha_again=%s stable=%s" % [_err(ResourceSaver.save(a, p3)), _sha(p3), _sha(p3) == _sha(p1)])
	print("R96 det head1=%s" % _lines(p1, 1))
	print("R96 det text1=%s" % _text(p1).replace("\n", "|"))
	print("R96 det text2=%s" % _text(p2).replace("\n", "|"))
	var g1: Gradient = a.get_state().get_node_property_value(1, _find_prop(a.get_state(), 1, "gradient"))
	print("R96 det subid_a=%s" % g1.resource_scene_unique_id)
	var g2 := Gradient.new()
	print("R96 det fresh_gradient_subid=%s len=%d" % [g2.resource_scene_unique_id, g2.resource_scene_unique_id.length()])
	g2.resource_scene_unique_id = "pinned1"
	print("R96 det pinned_readback=%s" % g2.resource_scene_unique_id)
	var c := Line2D.new()
	c.name = "Pinned"
	c.gradient = g2
	var r2 := Node2D.new()
	r2.name = "PinnedRoot"
	r2.add_child(c)
	c.owner = r2
	var pc := _pack(r2)
	var p4 := BASE + "/det4.tscn"
	print("R96 det pinned_save=%s sha=%s text=%s" % [_err(ResourceSaver.save(pc, p4)), _sha(p4), _text(p4).replace("\n", "|")])

func _find_prop(st: SceneState, idx: int, prop: String) -> int:
	for i in st.get_node_property_count(idx):
		if st.get_node_property_name(idx, i) == prop:
			return i
	return -1

func _uid() -> void:
	_ensure_base()
	print("R96 uid api=%s" % _methods("ResourceUID"))
	print("R96 uid consts=%s" % _consts("ResourceUID"))
	var id := ResourceUID.create_id()
	print("R96 uid created_text=%s has=%s path_of_new=%s" % [ResourceUID.id_to_text(id), ResourceUID.has_id(id), ResourceUID.get_id_path(id)])
	var t := "uid://bqk3m5n7p9r1"
	print("R96 uid text_to_id=%d back=%s" % [ResourceUID.text_to_id(t), ResourceUID.id_to_text(ResourceUID.text_to_id(t))])
	print("R96 uid bad_text=%d bad_back=%s" % [ResourceUID.text_to_id("not-a-uid"), ResourceUID.id_to_text(0)])
	var p := BASE + "/uid.tres"
	var grad := Gradient.new()
	print("R96 uid save=%s" % _err(ResourceSaver.save(grad, p)))
	print("R96 uid head=%s" % _lines(p, 2))
	var head := _lines(p, 1)
	var uid_start := head.find("uid=\"")
	var file_uid := ""
	if uid_start >= 0:
		var rest := head.substr(uid_start + 5)
		file_uid = rest.substr(0, rest.find("\""))
	print("R96 uid file_uid=%s id=%d path_for_id=%s" % [file_uid, ResourceUID.text_to_id(file_uid), ResourceUID.get_id_path(ResourceUID.text_to_id(file_uid))])
	print("R96 uid save_again=%s head2=%s stable=%s" % [_err(ResourceSaver.save(grad, p)), _lines(p, 1), _lines(p, 1) == head])
	ResourceUID.set_id(1234567, BASE + "/uid2.tres")
	print("R96 uid set_id_before path=%s has=%s" % [ResourceUID.get_id_path(1234567), ResourceUID.has_id(1234567)])
	var g2 := Gradient.new()
	print("R96 uid save2=%s head=%s" % [_err(ResourceSaver.save(g2, BASE + "/uid2.tres")), _lines(BASE + "/uid2.tres", 1)])
	ResourceUID.add_id(7654321, BASE + "/uid3.tres")
	print("R96 uid add_id path=%s" % ResourceUID.get_id_path(7654321))
	var g3 := Gradient.new()
	print("R96 uid save3=%s head=%s" % [_err(ResourceSaver.save(g3, BASE + "/uid3.tres")), _lines(BASE + "/uid3.tres", 1)])
	print("R96 uid after_add has=%s path=%s" % [ResourceUID.has_id(7654321), ResourceUID.get_id_path(7654321)])

func _takeover() -> void:
	_ensure_base()
	var a := Gradient.new()
	a.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 1, 0, 1)])
	var p := BASE + "/to.tres"
	print("R96 takeover save=%s" % _err(ResourceSaver.save(a, p)))
	var l1 = ResourceLoader.load(p)
	print("R96 takeover cache_identity=%s path=%s" % [is_same(l1, a), a.resource_path])
	var b := Gradient.new()
	b.take_over_path(p)
	print("R96 takeover after_b_load_is_b=%s b_path=%s a_path=%s" % [is_same(ResourceLoader.load(p), b), b.resource_path, a.resource_path])
	var c := Gradient.new()
	c.take_over_path(p)
	print("R96 takeover after_c_load_is_c=%s b_path=%s" % [is_same(ResourceLoader.load(p), c), b.resource_path])
	print("R96 takeover file_unchanged=%s head=%s" % [_sha(p), _lines(p, 2)])
	print("R96 takeover exists=%s exists_false=%s" % [ResourceLoader.exists(p), ResourceLoader.exists(BASE + "/nope.tres")])
	print("R96 takeover get_deps=%s" % ResourceLoader.get_dependencies(p))
	print("R96 takeover get_cached_ref=%s" % ResourceLoader.has_cached(p))
	ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_IGNORE)
	print("R96 takeover has_cached_after_ignore=%s" % ResourceLoader.has_cached(p))

func _cache() -> void:
	_ensure_base()
	var p := BASE + "/cache.tres"
	var g := Gradient.new()
	g.colors = PackedColorArray([Color(0.5, 0.5, 0.5, 1), Color(1, 1, 1, 1)])
	print("R96 cache save=%s" % _err(ResourceSaver.save(g, p)))
	var a = ResourceLoader.load(p)
	var b = ResourceLoader.load(p)
	print("R96 cache default_same=%s" % is_same(a, b))
	var c = ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_IGNORE)
	print("R96 cache ignore_same=%s ignore_path=%s ignore_cls=%s" % [is_same(a, c), c.resource_path, c.get_class()])
	var d = ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_IGNORE)
	print("R96 cache ignore_two_same=%s" % is_same(c, d))
	var e = ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REPLACE)
	print("R96 cache replace_same_as_a=%s same_as_e=%s a_still=%s" % [is_same(a, e), is_same(ResourceLoader.load(p), e), a.colors])
	print("R96 cache reuse=%s" % is_same(ResourceLoader.load(p), ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REUSE)))
	print("R96 cache exists_dir=%s exists_empty=%s" % [ResourceLoader.exists(BASE), ResourceLoader.exists("")])
	print("R96 cache load_missing=%s" % str(ResourceLoader.load(BASE + "/missing.tres")))
	print("R96 cache load_wrong_type=%s" % str(ResourceLoader.load(p, "PackedScene")))
	print("R96 cache load_by_res=%s" % str(ResourceLoader.load("res://project.godot")))

func _subres() -> void:
	_ensure_base()
	var r := Node2D.new()
	r.name = "SubRoot"
	var line := Line2D.new()
	line.name = "Line"
	var g := Gradient.new()
	g.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 0, 1, 1)])
	line.gradient = g
	r.add_child(line)
	line.owner = r
	var ps := _pack(r)
	var p := BASE + "/sub.tscn"
	print("R96 subres save=%s" % _err(ResourceSaver.save(ps, p)))
	print("R96 subres text=%s" % _text(p).replace("\n", "|"))
	var i1 := ps.instantiate()
	var i2 := ps.instantiate()
	var g1: Gradient = i1.get_child(0).gradient
	var g2: Gradient = i2.get_child(0).gradient
	print("R96 subres shared_across_instances=%s src_shared=%s" % [is_same(g1, g2), is_same(g1, g)])
	g1.colors = PackedColorArray([Color(0, 1, 0, 1), Color(1, 1, 0, 1)])
	print("R96 subres mutation_leaks=%s" % (g2.colors == g1.colors))
	var g3 := Gradient.new()
	g3.resource_local_to_scene = true
	var l2 := Line2D.new()
	l2.name = "LocalLine"
	l2.gradient = g3
	var r2 := Node2D.new()
	r2.name = "LocalRoot"
	r2.add_child(l2)
	l2.owner = r2
	var ps2 := _pack(r2)
	var p2 := BASE + "/sub_local.tscn"
	print("R96 subres local_save=%s text=%s" % [_err(ResourceSaver.save(ps2, p2)), _text(p2).replace("\n", "|")])
	var j1 := ps2.instantiate()
	var j2 := ps2.instantiate()
	var h1: Gradient = j1.get_child(0).gradient
	var h2: Gradient = j2.get_child(0).gradient
	print("R96 subres local_shared=%s h1_local=%s" % [is_same(h1, h2), h1.resource_local_to_scene])
	h1.colors = PackedColorArray([Color(0, 0, 1, 1), Color(0, 1, 1, 1)])
	print("R96 subres local_mutation_leaks=%s" % (h2.colors == h1.colors))
	# duplicate semantics
	var dup_shallow: Gradient = g.duplicate()
	var dup_deep: Gradient = g.duplicate(true)
	print("R96 subres dup_shallow_distinct=%s eq_colors=%s" % [not is_same(dup_shallow, g), dup_shallow.colors == g.colors])
	print("R96 subres dup_deep=%s" % (not is_same(dup_deep, g)))
	# nested subresource
	var gt := GradientTexture2D.new()
	gt.gradient = g
	var spr := Sprite2D.new()
	spr.name = "Spr"
	spr.texture = gt
	var r3 := Node2D.new()
	r3.name = "NestRoot"
	r3.add_child(spr)
	spr.owner = r3
	var ps3 := _pack(r3)
	var p3 := BASE + "/sub_nest.tscn"
	print("R96 subres nest_save=%s text=%s" % [_err(ResourceSaver.save(ps3, p3)), _text(p3).replace("\n", "|")])

func _extres() -> void:
	_ensure_base()
	var grad := Gradient.new()
	grad.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 1, 0, 1)])
	var ext := BASE + "/ext.tres"
	print("R96 extres save_ext=%s" % _err(ResourceSaver.save(grad, ext)))
	var loaded = ResourceLoader.load(ext)
	var line := Line2D.new()
	line.name = "ExtLine"
	line.gradient = loaded
	var r := Node2D.new()
	r.name = "ExtRoot"
	r.add_child(line)
	line.owner = r
	var ps := _pack(r)
	var p := BASE + "/ext.tscn"
	print("R96 extres save=%s" % _err(ResourceSaver.save(ps, p)))
	print("R96 extres text=%s" % _text(p).replace("\n", "|"))
	var back: PackedScene = ResourceLoader.load(p)
	var inst := back.instantiate()
	print("R96 extres inst_grad_is_loaded=%s" % is_same(inst.get_child(0).gradient, loaded))
	print("R96 extres inst_grad_path=%s" % inst.get_child(0).gradient.resource_path)
	var inst2 := back.instantiate()
	print("R96 extres two_instances_share_ext=%s" % is_same(inst.get_child(0).gradient, inst2.get_child(0).gradient))
	print("R96 extres deps=%s" % ResourceLoader.get_dependencies(p))
	var r2 := Node2D.new()
	r2.name = "FlagRoot"
	var line2 := Line2D.new()
	line2.name = "L2"
	line2.gradient = loaded
	r2.add_child(line2)
	line2.owner = r2
	var ps2 := _pack(r2)
	var p2 := BASE + "/ext_rel.tscn"
	print("R96 extres rel_save=%s text=%s" % [_err(ResourceSaver.save(ps2, p2, ResourceSaver.FLAG_RELATIVE_PATHS)), _text(p2).replace("\n", "|")])

func _editstate() -> void:
	_ensure_base()
	var r := Node2D.new()
	r.name = "EditRoot"
	var c := Node2D.new()
	c.name = "EditChild"
	r.add_child(c)
	c.owner = r
	var ps := _pack(r)
	var p := BASE + "/edit.tscn"
	print("R96 editstate save=%s" % _err(ResourceSaver.save(ps, p)))
	var back: PackedScene = ResourceLoader.load(p)
	for state in [PackedScene.GEN_EDIT_STATE_DISABLED, PackedScene.GEN_EDIT_STATE_INSTANCE, PackedScene.GEN_EDIT_STATE_MAIN, PackedScene.GEN_EDIT_STATE_MAIN_INHERITED]:
		var inst := back.instantiate(state)
		var kid := inst.get_child(0) if inst.get_child_count() > 0 else null
		print("R96 editstate state=%d root_name=%s kids=%d kid_owner_root=%s kid_placeholder=%s scene_file=%s" % [
			state, inst.name, inst.get_child_count(), str(kid.owner == inst) if kid != null else "n/a",
			str(inst.is_scene_instance_load_placeholder()) if inst.has_method("is_scene_instance_load_placeholder") else "n/a",
			inst.scene_file_path])
	var plain := ps.instantiate()
	print("R96 editstate plain_owner_kid=%s default_inst_name=%s" % [plain.get_child(0).owner, plain.name])
	# is_editable_instance / editable flags
	print("R96 editstate editable_methods=%s" % _methods("Node"))
	var inst3 := back.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	print("R96 editstate inst_has_owner=%s" % (inst3.get_child(0).owner == inst3))

func _refuse() -> void:
	_ensure_base()
	print("R96 refuse save_null=%s" % _err(ResourceSaver.save(null, BASE + "/null.tscn")))
	print("R96 refuse save_empty_path=%s" % _err(ResourceSaver.save(Gradient.new(), "")))
	print("R96 refuse save_into_res=%s" % _err(ResourceSaver.save(Gradient.new(), "res://r96_forbidden.tres")))
	print("R96 refuse load_missing=%s" % str(ResourceLoader.load(BASE + "/nope.tscn")))
	print("R96 refuse pack_null=%s" % str(_pack(null)))
	var empty := PackedScene.new()
	print("R96 refuse empty_can=%s instantiate=%s" % [empty.can_instantiate(), str(empty.instantiate())])
	var g := Gradient.new()
	print("R96 refuse bad_ext=%s" % _err(ResourceSaver.save(g, BASE + "/weird.xyz")))
	print("R96 refuse no_ext=%s" % _err(ResourceSaver.save(g, BASE + "/noext")))
	print("R96 refuse dir_as_file=%s" % _err(ResourceSaver.save(g, BASE)))
	print("R96 refuse load_dir=%s" % str(ResourceLoader.load(BASE)))
	print("R96 refuse load_empty=%s" % str(ResourceLoader.load("")))
	print("R96 refuse save_relative=%s" % _err(ResourceSaver.save(g, "relative_path.tres")))

func _edges() -> void:
	_ensure_base()
	# instantiate root naming
	var r := Node2D.new()
	r.name = "NameRoot"
	var ps := _pack(r)
	var p := BASE + "/edge.tscn"
	print("R96 edges save=%s" % _err(ResourceSaver.save(ps, p)))
	var back: PackedScene = ResourceLoader.load(p)
	var i1 := back.instantiate()
	var i2 := back.instantiate()
	print("R96 edges names=%s,%s" % [i1.name, i2.name])
	var holder := Node.new()
	holder.name = "Holder"
	holder.add_child(i1)
	holder.add_child(i2)
	print("R96 edges added_names=%s,%s" % [i1.name, i2.name])
	print("R96 edges root_owner=%s scene_file=%s" % [i1.owner, i1.scene_file_path])
	print("R96 edges packed_twice_same=%s" % is_same(_pack(r), _pack(r)))
	print("R96 edges state_path=%s" % back.get_state().get_path())
	print("R96 edges groups: %s" % str(_groups_probe()))
	print("R96 edges duplicate_scene=%s" % str(back.duplicate().get_class()))

func _groups_probe() -> String:
	_ensure_base()
	var r := Node2D.new()
	r.name = "GRoot"
	var c := Node2D.new()
	c.name = "GChild"
	r.add_child(c)
	c.owner = r
	c.add_to_group("grp_a", true)
	c.add_to_group("grp_b", true)
	var ps := _pack(r)
	var st: SceneState = ps.get_state()
	var out := PackedStringArray()
	for i in st.get_node_count():
		out.append("%s:%s" % [st.get_node_name(i), str(st.get_node_groups(i))])
	var p := BASE + "/grp.tscn"
	var e := ResourceSaver.save(ps, p)
	var inst := ps.instantiate()
	return "save=%s groups=%s text=%s inst_groups=%s" % [error_string(e), ",".join(out),
		_text(p).replace("\n", "|"), str(inst.get_child(0).get_groups())]
