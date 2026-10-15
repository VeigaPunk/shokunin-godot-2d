extends SceneTree
# r96 scout DISCOVERY probe #8 — ext_resource id control: same-object resave,
# resource_scene_unique_id on the referenced resource, generate_scene_unique_id.
var arm := ""
const BASE := "user://r96"

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"extid_same": _extid_same()
		"extid_pin": _extid_pin()
		_: print("R96 discover8 unknown_arm=%s" % arm)
	quit(0)

func _text(p: String) -> String:
	var f := FileAccess.open(p, FileAccess.READ)
	if f == null:
		return "<none>"
	var t := f.get_as_text()
	f.close()
	return t

func _err(code: int) -> String:
	return "%s(%d)" % [error_string(code), code]

func _extid(text: String) -> String:
	var pos := text.find("ext_resource")
	if pos < 0:
		return ""
	var ip := text.find("id=\"", pos)
	if ip < 0:
		return ""
	var rest := text.substr(ip + 4)
	return rest.substr(0, rest.find("\""))

func _build(grad: Resource) -> PackedScene:
	var r := Node2D.new()
	r.name = "E8Root"
	var line := Line2D.new()
	line.name = "E8Line"
	line.gradient = grad
	r.add_child(line)
	line.owner = r
	var ps := PackedScene.new()
	ps.pack(r)
	r.free()
	return ps

func _extid_same() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var g := Gradient.new()
	var ext := BASE + "/e8.tres"
	print("R96 extid_same ext_save=%s" % _err(ResourceSaver.save(g, ext)))
	var loaded = ResourceLoader.load(ext)
	var ps := _build(loaded)
	var p1 := BASE + "/e8_1.tscn"
	var p2 := BASE + "/e8_2.tscn"
	print("R96 extid_same save1=%s id1=%s" % [_err(ResourceSaver.save(ps, p1)), _extid(_text(p1))])
	print("R96 extid_same save2=%s id2=%s same_obj=%s" % [_err(ResourceSaver.save(ps, p2)), _extid(_text(p2)), _extid(_text(p1)) == _extid(_text(p2))])
	print("R96 extid_same gen_scene_unique_id=%s len=%d" % [loaded.generate_scene_unique_id(), loaded.generate_scene_unique_id().length()])
	loaded = null

func _extid_pin() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var g := Gradient.new()
	var ext := BASE + "/e8p.tres"
	print("R96 extid_pin ext_save=%s" % _err(ResourceSaver.save(g, ext)))
	var loaded = ResourceLoader.load(ext)
	loaded.resource_scene_unique_id = "pinned_ext"
	print("R96 extid_pin readback=%s path=%s" % [loaded.resource_scene_unique_id, loaded.resource_path])
	var ps := _build(loaded)
	var p1 := BASE + "/e8p_1.tscn"
	print("R96 extid_pin save=%s text=%s" % [_err(ResourceSaver.save(ps, p1)), _text(p1).replace("\n", "|")])
	# also: set the id on the *scene* resource itself
	var ps2 := _build(loaded)
	ps2.resource_scene_unique_id = "scene_pin"
	var p2 := BASE + "/e8p_2.tscn"
	print("R96 extid_pin scene_save=%s text=%s" % [_err(ResourceSaver.save(ps2, p2)), _text(p2).replace("\n", "|")])
	loaded = null
