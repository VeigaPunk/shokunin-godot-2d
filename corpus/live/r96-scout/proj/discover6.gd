extends SceneTree
# r96 scout DISCOVERY probe #6 — ResourceSaver.set_uid after the file exists.
var arm := ""
const BASE := "user://r96"

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"setuid2": _setuid2()
		_: print("R96 discover6 unknown_arm=%s" % arm)
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

func _setuid2() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var g := Gradient.new()
	g.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 0, 1, 1)])
	var p := BASE + "/setuid2.tres"
	print("R96 setuid2 save=%s head=%s" % [_err(ResourceSaver.save(g, p)), _text(p).split("\n")[0]])
	ResourceSaver.set_uid(p, 4242)
	print("R96 setuid2 after_set head=%s uid=%d id_path=%s has=%s" % [
		_text(p).split("\n")[0], ResourceLoader.get_resource_uid(p),
		ResourceUID.get_id_path(4242), ResourceUID.has_id(4242)])
	var back = ResourceLoader.load(p)
	print("R96 setuid2 reload=%s colors=%s path=%s" % [back != null, str(back.colors) if back != null else "n/a",
		back.resource_path if back != null else "n/a"])
	# scene referencing that path: does the ext_resource line carry the uid?
	var r := Node2D.new()
	r.name = "U2Root"
	var line := Line2D.new()
	line.name = "U2Line"
	line.gradient = back
	r.add_child(line)
	line.owner = r
	var ps := PackedScene.new()
	ps.pack(r)
	var p2 := BASE + "/setuid2.tscn"
	print("R96 setuid2 scene=%s text=%s" % [_err(ResourceSaver.save(ps, p2)), _text(p2).replace("\n", "|")])
	# and the .tscn of a scene saved *to* a path with a registered uid
	var p3 := BASE + "/setuid2_scene.tscn"
	ResourceSaver.set_uid(p3, 7777)
	var e3 := ResourceSaver.save(ps, p3)
	print("R96 setuid2 scene3=%s head=%s uid=%d" % [_err(e3), _text(p3).split("\n")[0], ResourceLoader.get_resource_uid(p3)])
	line.gradient = null
	r.free()
	back = null
