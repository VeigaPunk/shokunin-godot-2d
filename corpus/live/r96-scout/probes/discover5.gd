extends SceneTree
# r96 scout DISCOVERY probe #5 — subresource-id sequence, ResourceSaver.set_uid, uid= load path.
var arm := ""
const BASE := "user://r96"

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"subid_seq": _subid_seq()
		"setuid": _setuid()
		"uidload": _uidload()
		"chgpath3": _chgpath3()
		_: print("R96 discover5 unknown_arm=%s" % arm)
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

func _subid(text: String) -> String:
	var idpos := text.find("id=\"")
	if idpos < 0:
		return ""
	var rest := text.substr(idpos + 4)
	return rest.substr(0, rest.find("\""))

func _mk_scene() -> PackedScene:
	var r := Node2D.new()
	r.name = "SeqRoot"
	var line := Line2D.new()
	line.name = "SeqLine"
	var g := Gradient.new()
	line.gradient = g
	r.add_child(line)
	line.owner = r
	var ps := PackedScene.new()
	ps.pack(r)
	r.free()
	return ps

func _subid_seq() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var ps := _mk_scene()
	var p := BASE + "/seq0.tscn"
	print("R96 subid_seq n0=%s err=%s" % [_subid(_text(p)) if ResourceSaver.save(ps, p) == OK else "save_fail", _err(ResourceSaver.save(ps, p))])
	for extra in [1, 2, 3]:
		for i in extra:
			Gradient.new()
		var ps2 := _mk_scene()
		var p2 := BASE + "/seq%d.tscn" % extra
		var e := ResourceSaver.save(ps2, p2)
		print("R96 subid_seq extra=%d subid=%s err=%s" % [extra, _subid(_text(p2)), _err(e)])
	var a := Gradient.new()
	var b := Gradient.new()
	print("R96 subid_seq two_fresh_ids=%s,%s" % [a.resource_scene_unique_id, b.resource_scene_unique_id])
	a.resource_scene_unique_id = "pinned_a"
	print("R96 subid_seq pinned=%s fresh_b=%s" % [a.resource_scene_unique_id, b.resource_scene_unique_id])

func _setuid() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var g := Gradient.new()
	var p := BASE + "/setuid.tres"
	ResourceSaver.set_uid(p, 4242)
	var e := ResourceSaver.save(g, p)
	print("R96 setuid save=%s head=%s id_for_path=%d uid=%d" % [_err(e), _text(p).split("\n")[0],
		ResourceSaver.get_resource_id_for_path(p), ResourceLoader.get_resource_uid(p)])
	var r := Node2D.new()
	r.name = "SetUidRoot"
	var line := Line2D.new()
	line.name = "SetUidLine"
	var loaded = ResourceLoader.load(p)
	line.gradient = loaded
	r.add_child(line)
	line.owner = r
	var ps := PackedScene.new()
	ps.pack(r)
	var p2 := BASE + "/setuid.tscn"
	print("R96 setuid scene=%s text=%s" % [_err(ResourceSaver.save(ps, p2)), _text(p2).replace("\n", "|")])
	line.gradient = null
	r.free()
	loaded = null

func _uidload() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var g := Gradient.new()
	g.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 0, 1, 1)])
	var ext := BASE + "/uidload_ext.tres"
	print("R96 uidload ext_save=%s" % _err(ResourceSaver.save(g, ext)))
	# hand-written scene with a uid= line the registry does not know
	var body := "[gd_scene format=3]\n\n[ext_resource type=\"Gradient\" uid=\"uid://bqk3m5n7qar1\" path=\"user://r96/uidload_ext.tres\" id=\"1_zzzzz\"]\n\n[node name=\"URoot\" type=\"Node2D\"]\n\n[node name=\"ULine\" type=\"Line2D\" parent=\".\"]\ngradient = ExtResource(\"1_zzzzz\")\n"
	var f := FileAccess.open(BASE + "/uidload.tscn", FileAccess.WRITE)
	f.store_string(body)
	f.close()
	var back: PackedScene = ResourceLoader.load(BASE + "/uidload.tscn")
	var inst = back.instantiate() if back != null else null
	print("R96 uidload loaded=%s inst=%s grad_is_loaded=%s grad_path=%s" % [
		back != null, inst != null,
		inst != null and is_same(inst.get_child(0).gradient, ResourceLoader.load(ext)),
		inst.get_child(0).gradient.resource_path if inst != null else "n/a"])
	if inst != null:
		inst.free()

func _chgpath3() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var g := Gradient.new()
	var p := BASE + "/cp3.tres"
	ResourceSaver.set_uid(p, 999)
	print("R96 chgpath3 save=%s path_after=%s head=%s" % [_err(ResourceSaver.save(g, p, ResourceSaver.FLAG_CHANGE_PATH)), g.resource_path, _text(p).split("\n")[0]])
	var g2 := Gradient.new()
	g2.set_path(p)
	print("R96 chgpath3 setpath_collision_path=%s" % g2.resource_path)
