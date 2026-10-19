extends SceneTree
const TAG := "[r104R1g]"
func _dump(l: String, v) -> void:
	print("%s %s=%s" % [TAG, l, str(v)])
func _initialize() -> void:
	# create_id_for_path determinism: same path -> same id? pure (no registry side effect)?
	var paths := ["res://a.gd", "res://b.gd", "res://sub/deep.gd", "res://assets/thing.gd", "", "uid://x"]
	for p in paths:
		var i1 := ResourceUID.create_id_for_path(p)
		var i2 := ResourceUID.create_id_for_path(p)
		_dump("cidf", "path=[%s] i1=%d i2=%d deterministic=%s text=%s" % [p, i1, i2, str(i1 == i2), ResourceUID.id_to_text(i1)])
		_dump("cidf_registered", "path=[%s] has=%s" % [p, str(ResourceUID.has_id(i1))])
	# cross-check against my earlier run's value for res://nope.gd
	_dump("cidf_nope", ResourceUID.create_id_for_path("res://nope.gd"))
	# create_id randomness
	var a := ResourceUID.create_id()
	var b := ResourceUID.create_id()
	_dump("create_id_distinct", "%d %d %s" % [a, b, str(a != b)])
	# ensure_path on unregistered
	_dump("ensure_path_unreg", ResourceUID.ensure_path("res://not-there.gd"))
	_dump("ensure_path_then_has", "%s" % str(ResourceUID.has_id(ResourceUID.create_id_for_path("res://not-there.gd"))))
	print("PASS res_uid_scr7 arm=cidf")
	quit(0)
