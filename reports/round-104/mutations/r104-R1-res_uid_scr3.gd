extends SceneTree

const TAG := "[r104R1c]"

func _dump(label: String, v) -> void:
	print("%s %s=%s" % [TAG, label, str(v)])

func _initialize() -> void:
	var argv := OS.get_cmdline_user_args()
	var arm := "cachebin"
	for a in argv:
		if a.begins_with("--arm="):
			arm = a.substr(6)
	match arm:
		"cachebin": _arm_cachebin()
		"persist": _arm_persist()
		"bust": _arm_bust()
		"nodisc": _arm_nodisc()
		_: _dump("unknown_arm", arm)
	print("PASS res_uid_scr3 arm=%s" % arm)
	quit(0)

func _arm_cachebin() -> void:
	var f := FileAccess.open("res://.godot/uid_cache.bin", FileAccess.READ)
	if f == null:
		_dump("open", "FAILED")
		return
	var cnt := f.get_32()
	_dump("count", cnt)
	var rows := []
	for i in range(cnt):
		var id := f.get_64()
		var slen := f.get_32()
		var sp := f.get_buffer(slen).get_string_from_utf8()
		rows.append("%d|%s|%s" % [id, sp, ResourceUID.id_to_text(id)])
	_dump("rows", " ;; ".join(rows))
	_dump("eof_remaining", f.get_length() - f.get_position())

func _arm_persist() -> void:
	# is .uid the durable store, or does uid_cache.bin carry it?
	_dump("cachebin_exists", FileAccess.file_exists("res://.godot/uid_cache.bin"))
	for t in ["uid://bq1a2b3c4d5e6", "uid://cq7f8g9h0j1k2"]:
		var i := ResourceUID.text_to_id(t)
		_dump("resolve", "%s has=%s path=%s" % [t, str(ResourceUID.has_id(i)), ResourceUID.get_id_path(i)])
	_dump("uidfile_thing", FileAccess.get_file_as_string("res://assets/thing.gd.uid").strip_edges())
	_dump("uidfile_deep", FileAccess.get_file_as_string("res://sub/deep.gd.uid").strip_edges())
	_dump("uidfile_scr_gd_exists", FileAccess.file_exists("res://res_uid_scr3.gd.uid"))

func _arm_bust() -> void:
	var q := "res://data/res.tres"
	var r1 := ResourceLoader.load(q, "", ResourceLoader.CACHE_MODE_REUSE)
	_dump("v1", r1.get("v"))
	# mutate the file on disk from inside the process
	var f := FileAccess.open(q, FileAccess.WRITE)
	f.store_string("[gd_resource type=\"Resource\" script_class=\"R104Thing\" load_steps=2 format=3]\n\n[ext_resource type=\"Script\" path=\"res://assets/thing.gd\" id=\"1_a\"]\n\n[resource]\nscript = ExtResource(\"1_a\")\nv = 999\n")
	f.close()
	var r2 := ResourceLoader.load(q, "", ResourceLoader.CACHE_MODE_REUSE)
	_dump("reuse_after_disk_change_same_rid", r2.get_instance_id() == r1.get_instance_id())
	_dump("reuse_after_disk_change_v", r2.get("v"))
	var r3 := ResourceLoader.load(q, "", ResourceLoader.CACHE_MODE_IGNORE)
	_dump("ignore_after_disk_change_v", r3.get("v"))
	_dump("ignore_after_disk_change_same_rid", r3.get_instance_id() == r1.get_instance_id())
	var r4 := ResourceLoader.load(q, "", ResourceLoader.CACHE_MODE_REPLACE)
	_dump("replace_after_disk_change_v", r4.get("v"))
	var r5 := ResourceLoader.load(q, "", ResourceLoader.CACHE_MODE_REUSE)
	_dump("reuse_after_replace_v", r5.get("v"))
	_dump("reuse_after_replace_same_rid_as_replace", r5.get_instance_id() == r4.get_instance_id())

func _arm_nodisc() -> void:
	_dump("deep_uidfile_text", FileAccess.get_file_as_string("res://sub/deep.gd.uid").strip_edges())
	_dump("deep_uidfile_absent", not FileAccess.file_exists("res://sub/deep.gd.uid"))
	var tid := ResourceUID.text_to_id(FileAccess.get_file_as_string("res://sub/deep.gd.uid").strip_edges())
	_dump("old_deep_id", tid)
	_dump("old_deep_has", ResourceUID.has_id(tid))
	_dump("old_deep_path", ResourceUID.get_id_path(tid))
