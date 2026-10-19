extends SceneTree

const TAG := "[r104R1]"

func _dump(label: String, v) -> void:
	print("%s %s=%s" % [TAG, label, str(v)])

func _initialize() -> void:
	var argv := OS.get_cmdline_user_args()
	var arm := "dump"
	for a in argv:
		if a.begins_with("--arm="):
			arm = a.substr(6)
	match arm:
		"dump": _arm_dump()
		"forms": _arm_forms()
		"roundtrip": _arm_roundtrip()
		"load": _arm_load()
		"persist": _arm_persist()
		"collide": _arm_collide()
		_: _dump("unknown_arm", arm)
	print("PASS res_uid_scr1 arm=%s" % arm)
	quit(0)

func _arm_dump() -> void:
	var methods := ClassDB.class_get_method_list("ResourceUID", true)
	var names := []
	for m in methods:
		names.append(m["name"])
	names.sort()
	_dump("resource_uid_methods", "|".join(names))
	_dump("singleton", Engine.has_singleton("ResourceUID"))
	var sing := Engine.get_singleton("ResourceUID")
	_dump("singleton_class", sing.get_class() if sing != null else "null")
	_dump("uid_prefix_const", "uid://")

func _arm_forms() -> void:
	# builtin ids from the engine: ResourceUID.BuiltinID enum
	_dump("builtin_invalid", ResourceUID.INVALID_ID)
	_dump("builtin_text_invalid", ResourceUID.id_to_text(ResourceUID.INVALID_ID))
	for name in ["RESOURCES_UID", "MAIN_SCENE_UID", "INTERNAL_START", "INTERNAL_END"]:
		if name in ResourceUID:
			_dump("builtin_%s" % name, ResourceUID[name])
		else:
			_dump("builtin_%s" % name, "ABSENT")
	# custom id text forms
	for t in ["uid://bq1a2b3c4d5e6", "uid://cq7f8g9h0j1k2", "uid://0", "uid://a", "uid://zzzzzzzzzzzzz", "uid://b", "uid://"]:
		var got := ResourceUID.text_to_id(t)
		_dump("text_to_id(%s)" % t, got)
		if got != ResourceUID.INVALID_ID:
			_dump("id_to_text(%d)" % got, ResourceUID.id_to_text(got))
	# non-prefixed text
	for t in ["bq1a2b3c4d5e6", "res://assets/thing.gd", "", "uid:/b"]:
		_dump("text_to_id_nonuid(%s)" % t, ResourceUID.text_to_id(t))

func _arm_roundtrip() -> void:
	var uid_path := "res://assets/thing.gd"
	_dump("has_id_before", ResourceUID.has_id(ResourceUID.text_to_id("uid://bq1a2b3c4d5e6")))
	_dump("get_id_path_before", ResourceUID.get_id_path(ResourceUID.text_to_id("uid://bq1a2b3c4d5e6")))
	var newid := ResourceUID.create_id()
	_dump("create_id", newid)
	_dump("create_id_text", ResourceUID.id_to_text(newid))
	_dump("create_id_invalid", newid == ResourceUID.INVALID_ID)
	ResourceUID.add_id(newid, uid_path)
	_dump("has_id_after_add", ResourceUID.has_id(newid))
	_dump("get_id_path_after_add", ResourceUID.get_id_path(newid))
	_dump("get_id_path_unknown", ResourceUID.get_id_path(ResourceUID.text_to_id("uid://zzzzzzzzzzzzz")))
	_dump("has_id_unknown", ResourceUID.has_id(ResourceUID.text_to_id("uid://zzzzzzzzzzzzz")))
	# overwrite existing mapping
	ResourceUID.add_id(newid, "res://assets/other.gd")
	_dump("get_id_path_after_second_add", ResourceUID.get_id_path(newid))
	# set_id form
	var s := ResourceUID.text_to_id("uid://bq1a2b3c4d5e6")
	ResourceUID.set_id(s, "res://assets/thing.gd")
	_dump("after_set_id", ResourceUID.get_id_path(s))
	# remove
	ResourceUID.remove_id(newid)
	_dump("has_id_after_remove", ResourceUID.has_id(newid))
	# same path two ids
	var i2 := ResourceUID.create_id()
	ResourceUID.add_id(i2, "res://assets/thing.gd")
	_dump("two_ids_same_path", "%s|%s" % [ResourceUID.get_id_path(s), ResourceUID.get_id_path(i2)])

func _arm_load() -> void:
	var p := "res://assets/thing.gd"
	var a := ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REUSE)
	var b := ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REUSE)
	_dump("reuse_identity", a == b)
	_dump("reuse_rid_equal", a.get_instance_id() == b.get_instance_id())
	var c := ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_IGNORE)
	_dump("ignore_identity_vs_reuse", c == a)
	_dump("ignore_rid_vs_reuse", c.get_instance_id() == a.get_instance_id())
	var d := ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REUSE)
	_dump("reuse_after_ignore_identity", d.get_instance_id() == a.get_instance_id())
	_dump("reuse_after_ignore_equals_ignore", d.get_instance_id() == c.get_instance_id())
	var e := ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REPLACE)
	_dump("replace_rid_vs_reuse", e.get_instance_id() == a.get_instance_id())
	var f := ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REUSE)
	_dump("reuse_after_replace_vs_replace", f.get_instance_id() == e.get_instance_id())
	_dump("reuse_deep_rid_vs_reuse", "MEMBER_ABSENT_SEE_ENUM_CENSUS")
	_dump("cached_paths_has", ResourceLoader.has_cached(p))
	var res := ResourceLoader.load("res://assets/plain.txt", "", ResourceLoader.CACHE_MODE_REUSE)
	_dump("load_plain_txt", res)
	_dump("load_missing", ResourceLoader.load("res://assets/nope.gd", "", ResourceLoader.CACHE_MODE_REUSE))

func _arm_persist() -> void:
	var p := "res://sub/deep.gd"
	_dump("uidfile_text_deep", FileAccess.get_file_as_string("res://sub/deep.gd.uid").strip_edges())
	var tid := ResourceUID.text_to_id("uid://cq7f8g9h0j1k2")
	_dump("deep_uid_has_id", ResourceUID.has_id(tid))
	_dump("deep_uid_get_id_path", ResourceUID.get_id_path(tid))
	_dump("uidfile_exists_thing", FileAccess.file_exists("res://assets/thing.gd.uid"))
	_dump("uid_cache_exists", FileAccess.file_exists("res://.godot/uid_cache.bin"))

func _arm_collide() -> void:
	# force a duplicate id: two .uid files carrying the same uid text
	var t := "uid://bq1a2b3c4d5e6"
	var i := ResourceUID.text_to_id(t)
	_dump("collide_id", i)
	_dump("collide_path_a", ResourceUID.get_id_path(i))
	ResourceUID.add_id(i, "res://assets/plain.txt")
	_dump("collide_path_b_after_add", ResourceUID.get_id_path(i))
