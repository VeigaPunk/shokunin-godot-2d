extends SceneTree
# r96 scout DISCOVERY probe #3 — leak trigger, ext-id determinism, bundle pinning, flags follow-ups.
var arm := ""
const BASE := "user://r96"

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"leak1": _leak(true, true)
		"leak2": _leak(false, true)
		"leak3": _leak(true, false)
		"leak4": _leak(false, false)
		"extid": _extid()
		"pin": _pin()
		"chgpath": _chgpath()
		"edit2": _edit2()
		_: print("R96 discover3 unknown_arm=%s" % arm)
	quit(0)

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

func _text(p: String) -> String:
	var f := FileAccess.open(p, FileAccess.READ)
	if f == null:
		return "<none>"
	var t := f.get_as_text()
	f.close()
	return t

func _err(code: int) -> String:
	return "%s(%d)" % [error_string(code), code]

func _pack(n: Node) -> PackedScene:
	var ps := PackedScene.new()
	var e: int = ps.pack(n)
	if e != OK:
		print("R96 pack_error=%s" % _err(e))
	return ps

# --- leak trigger -----------------------------------------------------------
func _leak(null_refs: bool, use_node: bool) -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var ext := BASE + "/leak_ext.tres"
	var g := Gradient.new()
	g.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 1, 0, 1)])
	print("R96 leak save_ext=%s" % _err(ResourceSaver.save(g, ext)))
	var loaded = ResourceLoader.load(ext)
	if use_node:
		var line := Line2D.new()
		line.name = "LeakLine"
		line.gradient = loaded
		var r := Node2D.new()
		r.name = "LeakRoot"
		r.add_child(line)
		line.owner = r
		var ps := _pack(r)
		print("R96 leak scene=%s" % _err(ResourceSaver.save(ps, BASE + "/leak.tscn")))
		r.free()
	if null_refs:
		loaded = null
	print("R96 leak done null_refs=%s use_node=%s" % [null_refs, use_node])

# --- ext id determinism -----------------------------------------------------
func _extid() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var ext := BASE + "/extid_ext.tres"
	var g := Gradient.new()
	g.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 0, 1, 1)])
	print("R96 extid save_ext=%s" % _err(ResourceSaver.save(g, ext)))
	var loaded = ResourceLoader.load(ext)
	var mk := func() -> PackedScene:
		var line := Line2D.new()
		line.name = "ExtLine"
		line.gradient = loaded
		var r := Node2D.new()
		r.name = "ExtRoot"
		r.add_child(line)
		line.owner = r
		return _pack(r)
	var ps1: PackedScene = mk.call()
	var ps2: PackedScene = mk.call()
	print("R96 extid save1=%s sha1=%s" % [_err(ResourceSaver.save(ps1, BASE + "/extid1.tscn")), _sha(BASE + "/extid1.tscn")])
	print("R96 extid save2=%s sha2=%s" % [_err(ResourceSaver.save(ps2, BASE + "/extid2.tscn")), _sha(BASE + "/extid2.tscn")])
	print("R96 extid text1=%s" % _text(BASE + "/extid1.tscn").replace("\n", "|"))
	print("R96 extid text2=%s" % _text(BASE + "/extid2.tscn").replace("\n", "|"))
	print("R96 extid id_for_path=%s" % loaded.get_id_for_path(ext))
	# pin the ext id via set_id_for_path on the resource
	var g2 := Gradient.new()
	var ext2 := BASE + "/extid_ext2.tres"
	print("R96 extid save_ext2=%s" % _err(ResourceSaver.save(g2, ext2)))
	g2.set_id_for_path(ext2, "7")
	var line2 := Line2D.new()
	line2.name = "PinnedLine"
	line2.gradient = g2
	var r2 := Node2D.new()
	r2.name = "PinnedRoot"
	r2.add_child(line2)
	line2.owner = r2
	var ps3 := _pack(r2)
	print("R96 extid pinned_save=%s text=%s" % [_err(ResourceSaver.save(ps3, BASE + "/extid3.tscn")), _text(BASE + "/extid3.tscn").replace("\n", "|")])
	line2.gradient = null
	line2.free()
	r2.free()
	loaded = null

# --- bundle pinning ---------------------------------------------------------
func _pin() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	# scene with a subresource + 2 nodes: pin node_ids and the subresource id
	var r := Node2D.new()
	r.name = "PinRoot"
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
	var keys := PackedStringArray()
	for k in d.keys():
		keys.append(str(k))
	keys.sort()
	print("R96 pin keys=%s" % ",".join(keys))
	print("R96 pin node_ids=%s" % str(d.get("node_ids")))
	print("R96 pin names=%s" % str(d.get("names")))
	print("R96 pin variants=%s" % str(d.get("variants")))
	print("R96 pin id_paths=%s" % str(d.get("id_paths")))
	print("R96 pin nodes=%s" % str(d.get("nodes")))
	var p1 := BASE + "/pin1.tscn"
	print("R96 pin save1=%s sha=%s" % [_err(ResourceSaver.save(ps, p1)), _sha(p1)])
	print("R96 pin text1=%s" % _text(p1).replace("\n", "|"))
	# pin the node ids in the bundle and re-save
	var d2: Dictionary = ps._get_bundled_scene()
	d2["node_ids"] = [111111, 222222]
	var ps2 := PackedScene.new()
	ps2._set_bundled_scene(d2)
	var p2 := BASE + "/pin2.tscn"
	print("R96 pin save2=%s sha=%s" % [_err(ResourceSaver.save(ps2, p2)), _sha(p2)])
	print("R96 pin text2=%s" % _text(p2).replace("\n", "|"))
	# reconstruct the same pinned bundle from scratch -> same sha?
	var d3: Dictionary = ps._get_bundled_scene()
	d3["node_ids"] = [111111, 222222]
	var ps3 := PackedScene.new()
	ps3._set_bundled_scene(d3)
	print("R96 pin save3=%s sha=%s same_as_2=%s" % [_err(ResourceSaver.save(ps3, BASE + "/pin3.tscn")), _sha(BASE + "/pin3.tscn"), _sha(BASE + "/pin3.tscn") == _sha(p2)])
	print("R96 pin instantiate_ok=%s" % (ps2.instantiate() != null))
	r.free()

# --- FLAG_CHANGE_PATH with a res:// path ------------------------------------
func _chgpath() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var g := Gradient.new()
	var rp := "res://r96_chg.tres"
	var e := ResourceSaver.save(g, rp, ResourceSaver.FLAG_CHANGE_PATH)
	print("R96 chgpath res_save=%s path_after=%s cached=%s" % [_err(e), g.resource_path, is_same(ResourceLoader.load(rp), g)])
	if FileAccess.file_exists(rp):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(rp))
	var g2 := Gradient.new()
	var up := BASE + "/chg.tres"
	var e2 := ResourceSaver.save(g2, up, ResourceSaver.FLAG_CHANGE_PATH | ResourceSaver.FLAG_RELATIVE_PATHS)
	print("R96 chgpath user_save=%s path_after=%s" % [_err(e2), g2.resource_path])
	var g3 := Gradient.new()
	print("R96 chgpath again=%s path_after=%s exists=%s" % [_err(ResourceSaver.save(g3, up)), g3.resource_path, FileAccess.file_exists(up)])

# --- editable instance, correct direction -----------------------------------
func _edit2() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var r := Node2D.new()
	r.name = "ERoot"
	var c := Node2D.new()
	c.name = "EChild"
	r.add_child(c)
	c.owner = r
	var ps := _pack(r)
	var p := BASE + "/edit2.tscn"
	print("R96 edit2 save=%s" % _err(ResourceSaver.save(ps, p)))
	var back: PackedScene = ResourceLoader.load(p)
	for state in [0, 1, 2, 3]:
		var inst := back.instantiate(state)
		var kid := inst.get_child(0)
		print("R96 edit2 state=%d root_editable_of_kid=%s kid_editable_of_root=%s placeholder=%s" % [
			state, kid.is_editable_instance(inst), inst.is_editable_instance(kid), kid.get_scene_instance_load_placeholder()])
	var inst2 := back.instantiate()
	inst2.set_editable_instance(inst2.get_child(0), true)
	print("R96 edit2 set_editable_readback=%s" % inst2.is_editable_instance(inst2.get_child(0)))
	inst2.get_child(0).set_scene_instance_load_placeholder(true)
	print("R96 edit2 placeholder_readback=%s" % inst2.get_child(0).get_scene_instance_load_placeholder())
	inst2.free()
	back = null
