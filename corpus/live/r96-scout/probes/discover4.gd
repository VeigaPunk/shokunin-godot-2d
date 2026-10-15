extends SceneTree
# r96 scout DISCOVERY probe #4 — uid registration, ext id control, chgpath, owner paths.
var arm := ""
const BASE := "user://r96"

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"pin": _pin()
		"extuid": _extuid()
		"extid2": _extid2()
		"chgpath2": _chgpath2()
		"ownerpath": _ownerpath()
		_: print("R96 discover4 unknown_arm=%s" % arm)
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

func _pin() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
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
	d["node_ids"] = [111111, 222222]
	var ps2 := PackedScene.new()
	ps2._set_bundled_scene(d)
	var p2 := BASE + "/pin2.tscn"
	print("R96 pin save=%s sha=%s text=%s" % [_err(ResourceSaver.save(ps2, p2)), _sha(p2), _text(p2).replace("\n", "|")])
	# a second, independently built bundle with the same pins
	var r2 := Node2D.new()
	r2.name = "PinRoot"
	var line2 := Line2D.new()
	line2.name = "PinLine"
	var g2 := Gradient.new()
	g2.colors = PackedColorArray([Color(0.25, 0.5, 0.75, 1), Color(0, 0, 0, 1)])
	g2.resource_scene_unique_id = "subpinned"
	line2.gradient = g2
	r2.add_child(line2)
	line2.owner = r2
	var ps3 := _pack(r2)
	var d3: Dictionary = ps3._get_bundled_scene()
	d3["node_ids"] = [111111, 222222]
	var ps4 := PackedScene.new()
	ps4._set_bundled_scene(d3)
	print("R96 pin save2=%s sha=%s same=%s" % [_err(ResourceSaver.save(ps4, BASE + "/pin4.tscn")), _sha(BASE + "/pin4.tscn"), _sha(BASE + "/pin4.tscn") == _sha(p2)])
	r.free()
	r2.free()

func _extuid() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var ext := BASE + "/extuid.tres"
	var g := Gradient.new()
	g.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 0, 1, 1)])
	print("R96 extuid save_ext=%s" % _err(ResourceSaver.save(g, ext)))
	ResourceUID.add_id(4242, ext)
	print("R96 extuid registered=%s uid_of_path=%d" % [ResourceUID.get_id_path(4242), ResourceLoader.get_resource_uid(ext)])
	var loaded = ResourceLoader.load(ext)
	print("R96 extuid loaded_path=%s id_for_path=%s" % [loaded.resource_path, loaded.get_id_for_path(ext)])
	var line := Line2D.new()
	line.name = "UidLine"
	line.gradient = loaded
	var r := Node2D.new()
	r.name = "UidRoot"
	r.add_child(line)
	line.owner = r
	var ps := _pack(r)
	print("R96 extuid save=%s text=%s" % [_err(ResourceSaver.save(ps, BASE + "/extuid.tscn")), _text(BASE + "/extuid.tscn").replace("\n", "|")])
	var d: Dictionary = ps._get_bundled_scene()
	print("R96 extuid bundle_id_paths=%s" % str(d.get("id_paths")))
	print("R96 extuid bundle_variants=%s" % str(d.get("variants")))
	# what does the loader do with the uid line? round-trip
	var back: PackedScene = ResourceLoader.load(BASE + "/extuid.tscn")
	var inst := back.instantiate()
	print("R96 extuid inst_grad_is_loaded=%s path=%s" % [is_same(inst.get_child(0).gradient, loaded), inst.get_child(0).gradient.resource_path])
	inst.free()
	line.free()
	r.free()
	loaded = null

func _extid2() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var ext := BASE + "/extid2.tres"
	var g := Gradient.new()
	print("R96 extid2 save_ext=%s" % _err(ResourceSaver.save(g, ext)))
	var loaded = ResourceLoader.load(ext)
	loaded.set_id_for_path(ext, "7")
	print("R96 extid2 id_for_path=%s path=%s" % [loaded.get_id_for_path(ext), loaded.resource_path])
	var line := Line2D.new()
	line.name = "IdLine"
	line.gradient = loaded
	var r := Node2D.new()
	r.name = "IdRoot"
	r.add_child(line)
	line.owner = r
	var ps := _pack(r)
	
	print("R96 extid2 save=%s text=%s" % [_err(ResourceSaver.save(ps, BASE + "/extid2.tscn")), _text(BASE + "/extid2.tscn").replace("\n", "|")])
	# deterministic? save a second time from a fresh bundle
	var line2 := Line2D.new()
	line2.name = "IdLine"
	line2.gradient = loaded
	var r2 := Node2D.new()
	r2.name = "IdRoot"
	r2.add_child(line2)
	line2.owner = r2
	var ps2 := _pack(r2)
	print("R96 extid2 save2=%s text=%s" % [_err(ResourceSaver.save(ps2, BASE + "/extid2b.tscn")), _text(BASE + "/extid2b.tscn").replace("\n", "|")])
	line.free()
	r.free()
	line2.free()
	r2.free()
	loaded = null

func _chgpath2() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var p1 := BASE + "/cp1.tres"
	var p2 := BASE + "/cp2.tres"
	var g := Gradient.new()
	print("R96 chgpath2 save1=%s" % _err(ResourceSaver.save(g, p1)))
	var loaded = ResourceLoader.load(p1)
	print("R96 chgpath2 loaded_path=%s" % loaded.resource_path)
	var e := ResourceSaver.save(loaded, p2, ResourceSaver.FLAG_CHANGE_PATH)
	print("R96 chgpath2 save2=%s path_after=%s load_p2_is_same=%s" % [_err(e), loaded.resource_path, is_same(ResourceLoader.load(p2), loaded)])
	var g2 := Gradient.new()
	g2.set_path(p1)
	print("R96 chgpath2 setpath_then_save=%s path_after=%s" % [_err(ResourceSaver.save(g2, p2, ResourceSaver.FLAG_CHANGE_PATH)), g2.resource_path])
	print("R96 chgpath2 exists_p2=%s" % FileAccess.file_exists(p2))

func _ownerpath() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var r := Node2D.new()
	r.name = "ORoot"
	var c := Node2D.new()
	c.name = "OChild"
	var gc := Node2D.new()
	gc.name = "OGrand"
	r.add_child(c)
	c.add_child(gc)
	c.owner = r
	gc.owner = r
	var ps := _pack(r)
	var st: SceneState = ps.get_state()
	var out := PackedStringArray()
	for i in st.get_node_count():
		out.append("%s|type=%s|path=%s|owner=%s|idx=%d|props=%d|groups=%s" % [
			st.get_node_name(i), st.get_node_type(i), st.get_node_path(i), st.get_node_owner_path(i),
			st.get_node_index(i), st.get_node_property_count(i), str(st.get_node_groups(i))])
	print("R96 ownerpath nodes=%d" % st.get_node_count())
	for line in out:
		print("R96 ownerpath %s" % line)
	print("R96 ownerpath save=%s text=%s" % [_err(ResourceSaver.save(ps, BASE + "/ownerpath.tscn")), _text(BASE + "/ownerpath.tscn").replace("\n", "|")])
	var inst := ps.instantiate()
	print("R96 ownerpath inst_child_owner_is_root=%s inst_grand_owner_is_root=%s" % [
		inst.get_child(0).owner == inst, inst.get_child(0).get_child(0).owner == inst])
	inst.free()
	r.free()
