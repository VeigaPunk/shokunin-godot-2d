extends SceneTree

const TAG := "[r104R1d]"

func _dump(label: String, v) -> void:
	print("%s %s=%s" % [TAG, label, str(v)])

func _initialize() -> void:
	var argv := OS.get_cmdline_user_args()
	var arm := "loadbyuid"
	for a in argv:
		if a.begins_with("--arm="):
			arm = a.substr(6)
	match arm:
		"loadbyuid": _arm_loadbyuid()
		"remapmiss": _arm_remapmiss()
		"dupuid": _arm_dupuid()
		"collision": _arm_collision()
		_: _dump("unknown_arm", arm)
	print("PASS res_uid_scr4 arm=%s" % arm)
	quit(0)

func _arm_loadbyuid() -> void:
	for u in ["uid://cfo35nu5y4frk", "uid://bq1a2b3c4d5e6", "uid://zzzzzzzzzzzzz", "uid://cq7f8g9h0j1k2"]:
		var r = ResourceLoader.load(u)
		_dump("load", "%s null=%s class=%s path=%s" % [u, str(r == null), (r.get_class() if r != null else "-"), (r.resource_path if r != null else "-")])
		var e := ResourceLoader.exists(u)
		_dump("exists", "%s -> %s" % [u, str(e)])
	# uid path form in FileAccess
	_dump("file_exists_uid", FileAccess.file_exists("uid://cfo35nu5y4frk"))
	_dump("get_file_as_string_uid_len", FileAccess.get_file_as_string("uid://cfo35nu5y4frk").length())

func _arm_remapmiss() -> void:
	_dump("import_exists", FileAccess.file_exists("res://tiny.png.import"))
	_dump("dest_exists", FileAccess.file_exists("res://.godot/imported/tiny.png-4c2a616b3090ed27619d4dea97b52b2a.ctex"))
	var r = ResourceLoader.load("res://tiny.png")
	_dump("load_src_null", r == null)
	if r != null:
		_dump("load_src_class", r.get_class())
	var d = ResourceLoader.load("res://.godot/imported/tiny.png-4c2a616b3090ed27619d4dea97b52b2a.ctex")
	_dump("load_dest_null", d == null)
	if d != null:
		_dump("load_dest_class", d.get_class())
		_dump("load_dest_respath", d.resource_path)
	_dump("exists_src", ResourceLoader.exists("res://tiny.png"))
	_dump("exists_dest", ResourceLoader.exists("res://.godot/imported/tiny.png-4c2a616b3090ed27619d4dea97b52b2a.ctex"))

func _arm_dupuid() -> void:
	# two .uid files carrying the SAME declared uid text
	for p in ["res://assets/thing.gd", "res://sub/deep.gd"]:
		_dump("uidfile", "%s = %s" % [p, FileAccess.get_file_as_string(p + ".uid").strip_edges()])
	var t := FileAccess.get_file_as_string("res://assets/thing.gd.uid").strip_edges()
	var i := ResourceUID.text_to_id(t)
	_dump("shared_id", i)
	_dump("shared_has", ResourceUID.has_id(i))
	_dump("shared_path", ResourceUID.get_id_path(i))
	_dump("deep_path", ResourceUID.get_id_path(ResourceUID.text_to_id("uid://cq7f8g9h0j1k2")))

func _arm_collision() -> void:
	# what does the cache say for the colliding id, and what paths map to it
	var f := FileAccess.open("res://.godot/uid_cache.bin", FileAccess.READ)
	if f == null:
		_dump("cachebin", "ABSENT")
		return
	var cnt := f.get_32()
	_dump("count", cnt)
	var by_id := {}
	var seen := []
	for i in range(cnt):
		var id := f.get_64()
		var slen := f.get_32()
		var sp := f.get_buffer(slen).get_string_from_utf8()
		seen.append("%s -> %s" % [sp, ResourceUID.id_to_text(id)])
		if by_id.has(id):
			_dump("DUP_IN_CACHE", "%s : %s AND %s" % [id, by_id[id], sp])
		by_id[id] = sp
	_dump("all", " ;; ".join(seen))
