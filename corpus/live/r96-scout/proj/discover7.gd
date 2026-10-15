extends SceneTree
# r96 scout DISCOVERY probe #7 — set_uid on binary; pinned-determinism on a second,
# independent construction (3 nodes + ext resource + nested subresource).
var arm := ""
const BASE := "user://r96"

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"setuid_res": _setuid_res()
		"pin_general": _pin_general()
		_: print("R96 discover7 unknown_arm=%s" % arm)
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
	return ctx.finish().hex_encode()

func _text(p: String) -> String:
	var f := FileAccess.open(p, FileAccess.READ)
	if f == null:
		return "<none>"
	var t := f.get_as_text()
	f.close()
	return t

func _err(code: int) -> String:
	return "%s(%d)" % [error_string(code), code]

func _setuid_res() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var g := Gradient.new()
	var p := BASE + "/setuid.res"
	print("R96 setuid_res save=%s sha=%s" % [_err(ResourceSaver.save(g, p)), _sha(p).substr(0, 16)])
	var before := _sha(p)
	ResourceSaver.set_uid(p, 4242)
	print("R96 setuid_res after_set sha=%s changed=%s uid=%d has=%s" % [
		_sha(p).substr(0, 16), _sha(p) != before, ResourceLoader.get_resource_uid(p), ResourceUID.has_id(4242)])
	var back = ResourceLoader.load(p)
	print("R96 setuid_res reload=%s" % (back != null))
	back = null

func _pin_general() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var ext_path := BASE + "/pin_ext.tres"
	var grad := Gradient.new()
	grad.colors = PackedColorArray([Color(0.2, 0.4, 0.6, 1), Color(0.8, 0.6, 0.4, 1)])
	print("R96 pin_general ext_save=%s" % _err(ResourceSaver.save(grad, ext_path)))
	var loaded = ResourceLoader.load(ext_path)
	var build := func() -> PackedScene:
		var r := Node2D.new()
		r.name = "GenRoot"
		r.position = Vector2(1, 2)
		var a := Node2D.new()
		a.name = "GenA"
		var b := Line2D.new()
		b.name = "GenB"
		b.gradient = loaded
		var g := Gradient.new()
		g.resource_scene_unique_id = "gensub"
		var gt := GradientTexture2D.new()
		gt.gradient = g
		var spr := Sprite2D.new()
		spr.name = "GenC"
		spr.texture = gt
		r.add_child(a)
		r.add_child(b)
		r.add_child(spr)
		a.owner = r
		b.owner = r
		spr.owner = r
		var ps := PackedScene.new()
		ps.pack(r)
		r.free()
		var d: Dictionary = ps._get_bundled_scene()
		d["node_ids"] = [700001, 700002, 700003]
		var ps2 := PackedScene.new()
		ps2._set_bundled_scene(d)
		return ps2
	var ps_a: PackedScene = build.call()
	var ps_b: PackedScene = build.call()
	var p1 := BASE + "/gen1.tscn"
	var p2 := BASE + "/gen2.tscn"
	var e1 := ResourceSaver.save(ps_a, p1)
	var e2 := ResourceSaver.save(ps_b, p2)
	print("R96 pin_general save1=%s sha1=%s save2=%s sha2=%s same=%s" % [
		_err(e1), _sha(p1), _err(e2), _sha(p2), _sha(p1) == _sha(p2)])
	print("R96 pin_general text=%s" % _text(p1).replace("\n", "|"))
	var inst = ps_a.instantiate()
	print("R96 pin_general inst_kids=%d owner_ok=%s ext_is_loaded=%s" % [
		inst.get_child_count(), inst.get_child(0).owner == inst, is_same(inst.get_child(1).gradient, loaded)])
	inst.free()
	loaded = null
