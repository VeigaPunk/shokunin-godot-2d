extends SceneTree
const TAG := "[r104R1h]"
func _dump(l: String, v) -> void:
	print("%s %s=%s" % [TAG, l, str(v)])
func _initialize() -> void:
	var d := {}
	for m in ClassDB.class_get_method_list("ResourceLoader", true):
		if m["name"] == "load":
			for arg in m["args"]:
				if arg["name"] == "cache_mode":
					d = arg
	_dump("load_cache_mode_arg_hint", str(d))
	# enum constants of ResourceLoader
	var ec := []
	for c in ClassDB.class_get_enum_list("ResourceLoader", true):
		ec.append(str(c))
	_dump("enums", "|".join(ec))
	var names := ["CACHE_MODE_IGNORE","CACHE_MODE_REUSE","CACHE_MODE_REPLACE","CACHE_MODE_IGNORE_DEEP","CACHE_MODE_REPLACE_DEEP"]
	for n in names:
		_dump("enum", "%s=%s" % [n, str(ResourceLoader[n]) if n in ResourceLoader else "ABSENT"])
	# deep modes actually load?
	var q := "res://data/res.tres"
	var r1 := ResourceLoader.load(q, "", ResourceLoader.CACHE_MODE_REUSE)
	_dump("v1", r1.get("v"))
	var f := FileAccess.open(q, FileAccess.WRITE)
	f.store_string("[gd_resource type=\"Resource\" script_class=\"R104Thing\" load_steps=2 format=3]\n\n[ext_resource type=\"Script\" path=\"res://assets/thing.gd\" id=\"1_a\"]\n\n[resource]\nscript = ExtResource(\"1_a\")\nv = 777\n")
	f.close()
	var ig := ResourceLoader.load(q, "", ResourceLoader.CACHE_MODE_IGNORE_DEEP)
	_dump("ignore_deep_v", ig.get("v"))
	_dump("ignore_deep_same_rid", ig.get_instance_id() == r1.get_instance_id())
	var rp := ResourceLoader.load(q, "", ResourceLoader.CACHE_MODE_REPLACE_DEEP)
	_dump("replace_deep_v", rp.get("v"))
	_dump("replace_deep_same_rid_as_ignore_deep", rp.get_instance_id() == ig.get_instance_id())
	var back := ResourceLoader.load(q, "", ResourceLoader.CACHE_MODE_REUSE)
	_dump("reuse_after_replace_deep_v", back.get("v"))
	_dump("reuse_after_replace_deep_same_rid", back.get_instance_id() == rp.get_instance_id())
	print("PASS res_uid_scr8 arm=modes")
	quit(0)
