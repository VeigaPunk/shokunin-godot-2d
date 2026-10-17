extends SceneTree
# r96-boundary probe B — attacks the r96 scout's "unique_id is the ONLY source of variance
# in a scene with no ext resources" claim with scene features the scout never packed:
# signal connections (bundle `conns`), groups (HashMap order), metadata (HashMap order),
# nested/shared/local sub-resources, fractional floats, PackedByteArray/NodePath metas,
# plus a hunt for a PUBLIC lever over the node unique_id.
#
# Launch: godot --headless --path proj --script res://r96b_var.gd -- --arm=<arm>
# Arms: rich conn groups meta lever idstat
var arm := ""
const BASE := "user://r96b"

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"rich": _arm_rich()
		"conn": _arm_conn()
		"groups": _arm_groups()
		"meta": _arm_meta()
		"lever": _arm_lever()
		"idstat": _arm_idstat()
		_: print("FAIL r96b_var %s reason=unknown_arm" % arm)
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

func _sha_str(s: String) -> String:
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(s.to_utf8_buffer())
	return ctx.finish().hex_encode()

func _text(p: String) -> String:
	var f := FileAccess.open(p, FileAccess.READ)
	if f == null:
		return "<none>"
	var t := f.get_as_text()
	f.close()
	return t

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

func _mask_subids(t: String) -> String:
	var out := t
	var pos := out.find("id=\"")
	while pos >= 0:
		var rest := out.substr(pos + 4)
		var val := rest.substr(0, rest.find("\""))
		if val.begins_with("1_"):
			pos = out.find("id=\"", pos + 4)
			continue
		out = out.substr(0, pos + 4) + "#" + out.substr(pos + 4 + val.length(), out.length() - pos - 4 - val.length())
		pos = out.find("id=\"", pos + 4)
	return out

func _flat(t: String) -> String:
	return t.replace("\n", "|")

func _b(v: bool) -> String:
	return "true" if v else "false"

var _parts: PackedStringArray = []

func _p(part: String) -> void:
	_parts.append(part)

func _emit(arm_name: String) -> void:
	print("PASS r96b_var %s %s" % [arm_name, " ".join(_parts)])
	_parts.clear()

# ------------------------------------------------------------------ rich scene

# deliberately feature-rich scene: 6 nodes, 3 sub-resources (one shared, one nested,
# one local_to_scene), scrambled groups, 6 scrambled connections, 8 metadata keys,
# fractional floats, PackedByteArray / NodePath / Color / Dictionary metas
func _build_rich(pin: bool) -> PackedScene:
	var root := Node2D.new()
	root.name = "RichRoot"
	root.position = Vector2(1.5, -2.25)
	root.set_meta("z_last", PackedByteArray([7, 8, 9]))
	root.set_meta("a_first", 1.0)
	root.set_meta("m_dict", {"b": 2, "a": 1, "c": 3, "d": 4})
	root.set_meta("k_np", NodePath("ChildA/ChildB"))
	root.set_meta("c_col", Color(0.5, 0.25, 0.125, 1.0))
	root.set_meta("s_sn", &"sym")
	root.set_meta("f_frac", 0.3333333333333333)
	root.set_meta("i_int", -17)

	var g := Gradient.new()
	g.colors = PackedColorArray([Color(0.1, 0.2, 0.3, 1), Color(0.4, 0.5, 0.6, 1)])
	if pin:
		g.resource_scene_unique_id = "rich_g"
	var tex := GradientTexture2D.new()
	tex.gradient = g
	tex.width = 8
	tex.height = 4
	if pin:
		tex.resource_scene_unique_id = "rich_tex"
	var lg := Gradient.new()
	lg.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 0, 1, 1)])
	lg.resource_local_to_scene = true
	if pin:
		lg.resource_scene_unique_id = "rich_lg"

	var names := ["ChildA", "ChildB", "ChildC", "ChildD", "ChildE"]
	var kids: Array[Node2D] = []
	for i in names.size():
		var c := Node2D.new()
		c.name = names[i]
		c.position = Vector2(float(i) * 1.5, float(i) / 3.0)
		root.add_child(c)
		c.owner = root
		kids.append(c)
	kids[0].add_to_group(&"grp_c", true)
	kids[0].add_to_group(&"grp_a", true)
	kids[0].add_to_group(&"grp_b", true)
	kids[1].add_to_group(&"grp_z", true)
	kids[1].add_to_group(&"grp_m", true)
	kids[2].add_to_group(&"grp_a", true)
	kids[2].add_to_group(&"grp_z", true)

	var l0 := Line2D.new()
	l0.name = "Line0"
	l0.gradient = g
	kids[0].add_child(l0)
	l0.owner = root
	var l1 := Line2D.new()
	l1.name = "Line1"
	l1.gradient = g
	kids[1].add_child(l1)
	l1.owner = root
	var l2 := Line2D.new()
	l2.name = "Line2"
	l2.gradient = lg
	kids[2].add_child(l2)
	l2.owner = root
	var spr := Sprite2D.new()
	spr.name = "Sprite"
	spr.texture = tex
	kids[3].add_child(spr)
	spr.owner = root

	# scrambled connect order; targets all inside the packed tree
	root.connect(&"renamed", Callable(kids[3], &"get_path"), Object.CONNECT_PERSIST)
	root.connect(&"renamed", Callable(kids[1], &"get_path"), Object.CONNECT_PERSIST)
	kids[2].connect(&"renamed", Callable(kids[4], &"get_path"), Object.CONNECT_PERSIST)
	kids[0].connect(&"renamed", Callable(kids[2], &"get_path"), Object.CONNECT_PERSIST)
	kids[1].connect(&"renamed", Callable(kids[0], &"get_path"), Object.CONNECT_PERSIST)
	kids[3].connect(&"renamed", Callable(kids[1], &"get_path"), Object.CONNECT_PERSIST)

	var ps := PackedScene.new()
	ps.pack(root)
	root.free()
	return ps

func _arm_rich() -> void:
	_ensure_base()
	var ps: PackedScene = _build_rich(false)
	var p := BASE + "/rich.tscn"
	var e := ResourceSaver.save(ps, p)
	var t := _text(p)
	var u_only := _mask_unique(t)
	var u_sub := _mask_subids(u_only)
	print("R96B var rich text_uonly=%s" % _flat(u_only))
	# pinned rebuild: node_ids from the bundle + pinned sub ids
	var ps2: PackedScene = _build_rich(true)
	var d: Dictionary = ps2._get_bundled_scene()
	var n: int = (d.get("node_ids") as Array).size()
	var pinned_ids: Array = []
	for i in n:
		pinned_ids.append(100001 + i)
	d["node_ids"] = pinned_ids
	var ps3 := PackedScene.new()
	ps3._set_bundled_scene(d)
	var p2 := BASE + "/rich_pin.tscn"
	var e2 := ResourceSaver.save(ps3, p2)
	var t2 := _text(p2)
	print("R96B var rich text_pinned=%s" % _flat(t2))
	_p("save=%s nodes=%d sha_uonly=%s sha_u_sub=%s pinned_save=%s pinned_nodes=%d pinned_sha=%s pinned_uonly=%s" % [
		error_string(e), n, _sha_str(u_only), _sha_str(u_sub),
		error_string(e2), n, _sha_str(t2), _sha_str(_mask_unique(t2))])
	ps = null
	ps2 = null
	ps3 = null
	_emit("rich")

func _arm_conn() -> void:
	_ensure_base()
	var root := Node2D.new()
	root.name = "ConnRoot"
	var kids: Array[Node2D] = []
	for i in 6:
		var c := Node2D.new()
		c.name = "N%d" % i
		root.add_child(c)
		c.owner = root
		kids.append(c)
	# 6 connections, scrambled order, two of them from the same source signal
	kids[0].connect(&"renamed", Callable(kids[5], &"get_path"), Object.CONNECT_PERSIST)
	kids[0].connect(&"renamed", Callable(kids[2], &"get_path"), Object.CONNECT_PERSIST)
	kids[3].connect(&"renamed", Callable(kids[1], &"get_path"), Object.CONNECT_PERSIST)
	kids[1].connect(&"renamed", Callable(kids[4], &"get_path"), Object.CONNECT_PERSIST)
	kids[2].connect(&"renamed", Callable(kids[0], &"get_path"), Object.CONNECT_PERSIST)
	kids[4].connect(&"renamed", Callable(kids[3], &"get_path"), Object.CONNECT_PERSIST)
	var ps := PackedScene.new()
	ps.pack(root)
	root.free()
	var p := BASE + "/conn.tscn"
	var e := ResourceSaver.save(ps, p)
	var t := _text(p)
	var lines := PackedStringArray()
	for ln in t.split("\n"):
		if ln.begins_with("[connection"):
			lines.append(ln)
	print("R96B var conn connections=%s" % "|".join(lines))
	_p("save=%s nconn=%d conns=%s sha_uonly=%s" % [
		error_string(e), lines.size(), "|".join(lines), _sha_str(_mask_unique(t))])
	ps = null
	_emit("conn")

func _arm_groups() -> void:
	_ensure_base()
	var root := Node2D.new()
	root.name = "GrpRoot"
	var a := Node2D.new()
	a.name = "GA"
	root.add_child(a)
	a.owner = root
	a.add_to_group(&"zulu", true)
	a.add_to_group(&"alpha", true)
	a.add_to_group(&"mike", true)
	a.add_to_group(&"bravo", true)
	var b := Node2D.new()
	b.name = "GB"
	root.add_child(b)
	b.owner = root
	b.add_to_group(&"mike", true)
	b.add_to_group(&"zulu", true)
	var ps := PackedScene.new()
	ps.pack(root)
	root.free()
	var p := BASE + "/groups.tscn"
	var e := ResourceSaver.save(ps, p)
	var t := _text(p)
	var lines := PackedStringArray()
	for ln in _mask_unique(t).split("\n"):
		if "groups=" in ln:
			lines.append(ln)
	print("R96B var groups lines=%s" % "|".join(lines))
	_p("save=%s lines=%s sha_uonly=%s" % [error_string(e), "|".join(lines), _sha_str(_mask_unique(t))])
	ps = null
	_emit("groups")

func _arm_meta() -> void:
	_ensure_base()
	var root := Node2D.new()
	root.name = "MetaRoot"
	var keys := ["k08", "k03", "k11", "k01", "k07", "k02", "k10", "k05"]
	for i in keys.size():
		root.set_meta(keys[i], i * 1000)
	var ps := PackedScene.new()
	ps.pack(root)
	root.free()
	var p := BASE + "/meta.tscn"
	var e := ResourceSaver.save(ps, p)
	var t := _text(p)
	var lines := PackedStringArray()
	for ln in t.split("\n"):
		if ln.begins_with("metadata/"):
			lines.append(ln)
	print("R96B var meta lines=%s" % "|".join(lines))
	_p("save=%s lines=%s sha_uonly=%s" % [error_string(e), "|".join(lines), _sha_str(_mask_unique(t))])
	ps = null
	_emit("meta")

func _arm_lever() -> void:
	_ensure_base()
	var node_methods := PackedStringArray()
	for m in ClassDB.class_get_method_list("Node", true):
		if String(m.name).find("unique") >= 0 or String(m.name).find("scene_") >= 0:
			node_methods.append(m.name)
	var has_get := ClassDB.class_has_method("Node", "get_scene_unique_id")
	var has_set := ClassDB.class_has_method("Node", "set_scene_unique_id")
	var readback := ""
	var text_has := "n/a"
	var ps_ref: PackedScene = null
	if has_set:
		var root := Node2D.new()
		root.name = "LeverRoot"
		var c := Node2D.new()
		c.name = "LeverChild"
		root.add_child(c)
		c.owner = root
		root.call("set_scene_unique_id", "leverA")
		c.call("set_scene_unique_id", "leverB")
		readback = "%s,%s" % [str(root.call("get_scene_unique_id")), str(c.call("get_scene_unique_id"))]
		var ps := PackedScene.new()
		ps.pack(root)
		root.free()
		var p := BASE + "/lever.tscn"
		var e := ResourceSaver.save(ps, p)
		var t := _text(p)
		text_has = _b(("unique_id=leverA" in t) or ("unique_id=leverB" in t))
		print("R96B var lever text=%s" % _flat(t))
		ps_ref = ps
	_p("has_get=%s has_set=%s node_methods=%s readback=%s text_has_setter_value=%s" % [
		_b(has_get), _b(has_set), ",".join(node_methods), readback, text_has])
	ps_ref = null
	_emit("lever")

func _arm_idstat() -> void:
	_ensure_base()
	var root := Node2D.new()
	root.name = "IdRoot"
	for i in 199:
		var c := Node2D.new()
		c.name = "I%03d" % i
		root.add_child(c)
		c.owner = root
	var ps := PackedScene.new()
	ps.pack(root)
	root.free()
	var d: Dictionary = ps._get_bundled_scene()
	var ids: Array = d.get("node_ids", [])
	var distinct := {}
	var minv := 4294967296
	var maxv := -1
	var gt2p31 := 0
	for v in ids:
		distinct[v] = true
		minv = mini(minv, int(v))
		maxv = maxi(maxv, int(v))
		if int(v) > 2147483647:
			gt2p31 += 1
	# huge / boundary pinned ids on a 5-node scene
	var root2 := Node2D.new()
	root2.name = "PinRoot"
	for i in 4:
		var c := Node2D.new()
		c.name = "P%d" % i
		root2.add_child(c)
		c.owner = root2
	var ps2 := PackedScene.new()
	ps2.pack(root2)
	root2.free()
	var d2: Dictionary = ps2._get_bundled_scene()
	d2["node_ids"] = [1, 2147483647, 2147483648, 4294967295, 999999999999]
	var ps3 := PackedScene.new()
	ps3._set_bundled_scene(d2)
	var p := BASE + "/idstat.tscn"
	var e := ResourceSaver.save(ps3, p)
	var t := _text(p)
	var found := PackedStringArray()
	for v in [1, 2147483647, 2147483648, 4294967295, 999999999999]:
		found.append(_b("unique_id=%d" % v in t))
	var inst := ps3.instantiate()
	_p("n=%d distinct=%d min=%d max=%d gt2p31=%d pin_save=%s pin_found=%s instantiate_ok=%s" % [
		ids.size(), distinct.size(), minv, maxv, gt2p31, error_string(e), ",".join(found), _b(inst != null)])
	print("R96B var idstat sample=%s" % ",".join(ids.slice(0, 8).map(func(v): return str(v))))
	inst.free()
	ps = null
	ps2 = null
	ps3 = null
	_emit("idstat")
