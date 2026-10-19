extends SceneTree

const TAG := "[r104R1b]"

func _dump(label: String, v) -> void:
	print("%s %s=%s" % [TAG, label, str(v)])

func _initialize() -> void:
	var argv := OS.get_cmdline_user_args()
	var arm := "canon"
	for a in argv:
		if a.begins_with("--arm="):
			arm = a.substr(6)
	match arm:
		"canon": _arm_canon()
		"cache": _arm_cache()
		"remap": _arm_remap()
		"persist": _arm_persist()
		"ids": _arm_ids()
		_: _dump("unknown_arm", arm)
	print("PASS res_uid_scr2 arm=%s" % arm)
	quit(0)

func _arm_canon() -> void:
	# does id_to_text(text_to_id(t)) == t ? and is text_to_id(id_to_text(i)) == i ?
	var samples := ["uid://bq1a2b3c4d5e6", "uid://cq7f8g9h0j1k2", "uid://0", "uid://a", "uid://b",
		"uid://zzzzzzzzzzzzz", "uid://ctkshoiimsrhf", "uid://cq7f8hah0j1k2", "uid://1", "uid://v",
		"uid://10", "uid://ba", "uid://ab", "uid://aa", "uid://10000000000000"]
	for t in samples:
		var i := ResourceUID.text_to_id(t)
		var back := ResourceUID.id_to_text(i)
		var i2 := ResourceUID.text_to_id(back)
		_dump("canon", "t=%s i=%d back=%s stable=%s idstable=%s" % [t, i, back, str(back == t), str(i2 == i)])
	# case sensitivity
	for t in ["uid://A", "uid://B", "uid://BQ1A2B3C4D5E6", "UID://b"]:
		_dump("case", "t=%s -> %d" % [t, ResourceUID.text_to_id(t)])
	# length limit / overflow
	for t in ["uid://zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz", "uid://1" + "0".repeat(40)]:
		var i := ResourceUID.text_to_id(t)
		_dump("long", "t=%s -> %d back=%s" % [t, i, ResourceUID.id_to_text(i)])
	# negative / INVALID_ID text
	_dump("id_to_text(-1)", ResourceUID.id_to_text(-1))
	_dump("text_to_id(uid://<invalid>)", ResourceUID.text_to_id("uid://<invalid>"))

func _arm_cache() -> void:
	var p := "res://assets/thing.gd"
	var a := ResourceLoader.load(p)
	var b := ResourceLoader.load(p)
	_dump("gd_default_identity", a.get_instance_id() == b.get_instance_id())
	var q := "res://data/res.tres"
	var r1 := ResourceLoader.load(q, "", ResourceLoader.CACHE_MODE_REUSE)
	var r2 := ResourceLoader.load(q, "", ResourceLoader.CACHE_MODE_REUSE)
	_dump("tres_reuse_rid_equal", r1.get_instance_id() == r2.get_instance_id())
	var r3 := ResourceLoader.load(q, "", ResourceLoader.CACHE_MODE_IGNORE)
	_dump("tres_ignore_rid_vs_reuse", r3.get_instance_id() == r1.get_instance_id())
	_dump("tres_ignore_equals_reuse", r3 == r1)
	var r4 := ResourceLoader.load(q, "", ResourceLoader.CACHE_MODE_REUSE)
	_dump("tres_reuse_after_ignore_vs_first", r4.get_instance_id() == r1.get_instance_id())
	_dump("tres_reuse_after_ignore_vs_ignore", r4.get_instance_id() == r3.get_instance_id())
	var r5 := ResourceLoader.load(q, "", ResourceLoader.CACHE_MODE_REPLACE)
	_dump("tres_replace_rid_vs_reuse", r5.get_instance_id() == r1.get_instance_id())
	var r6 := ResourceLoader.load(q, "", ResourceLoader.CACHE_MODE_REUSE)
	_dump("tres_reuse_after_replace_vs_replace", r6.get_instance_id() == r5.get_instance_id())
	_dump("tres_has_cached", ResourceLoader.has_cached(q))
	# cache_mode enum census
	var ms := ClassDB.class_get_method_list("ResourceLoader", true)
	for m in ms:
		if m["name"] == "load":
			for arg in m["args"]:
				_dump("load_arg", "%s type=%d hint=%d hint_string=%s" % [arg["name"], arg["type"], arg["hint"], arg["hint_string"]])

func _arm_remap() -> void:
	# imported asset: .import remap -> .godot/imported/*.ctex
	var p := "res://tiny.png"
	_dump("import_file_exists", FileAccess.file_exists("res://tiny.png.import"))
	var txt := FileAccess.get_file_as_string("res://tiny.png.import")
	_dump("import_text_len", txt.length())
	for line in txt.split("\n"):
		if line.begins_with("path=") or line.begins_with("uid=") or line.begins_with("[") or line.begins_with("source_file=") or line.begins_with("dest_files="):
			_dump("import_line", line)
	var r := ResourceLoader.load(p)
	_dump("load_imported_null", r == null)
	if r != null:
		_dump("load_imported_class", r.get_class())
		_dump("load_imported_path", r.resource_path)
	var rp := ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_IGNORE)
	_dump("imported_ignore_null", rp == null)
	# raw file via type hint
	var raw := ResourceLoader.load(p, "Image")
	_dump("load_as_Image_null", raw == null)
	if raw != null:
		_dump("load_as_Image_class", raw.get_class())
	# load the imported artifact path directly
	var dest := ""
	for line in txt.split("\n"):
		if line.begins_with("dest_files="):
			dest = line.substr(11).strip_edges().trim_prefix("[\"").trim_suffix("\"]")
	_dump("dest_files_parsed", dest)
	if dest != "":
		var d := ResourceLoader.load("res://" + dest)
		_dump("load_dest_null", d == null)
		if d != null:
			_dump("load_dest_class", d.get_class())
			_dump("load_dest_path", d.resource_path)

func _arm_persist() -> void:
	_dump("uid_cache_exists", FileAccess.file_exists("res://.godot/uid_cache.bin"))
	var f := FileAccess.open("res://.godot/uid_cache.bin", FileAccess.READ)
	if f == null:
		_dump("uid_cache_open", "FAILED")
		return
	_dump("uid_cache_len", f.get_length())
	var hdr := f.get_buffer(4)
	_dump("uid_cache_magic", hdr.get_string_from_ascii())
	var cnt := f.get_32()
	_dump("uid_cache_count", cnt)
	var rows := []
	for i in range(min(cnt, 12)):
		var id := f.get_64()
		var slen := f.get_32()
		var sp := f.get_buffer(slen).get_string_from_utf8()
		rows.append("%d=%s" % [id, sp])
	_dump("uid_cache_rows", "|".join(rows))
	# custom .uid registration
	for t in ["uid://bq1a2b3c4d5e6", "uid://cq7f8g9h0j1k2"]:
		var i := ResourceUID.text_to_id(t)
		_dump("reg", "%s has=%s path=%s" % [t, str(ResourceUID.has_id(i)), ResourceUID.get_id_path(i)])
	_dump("path_to_uid_thing", ResourceUID.path_to_uid("res://assets/thing.gd"))
	_dump("path_to_uid_deep", ResourceUID.path_to_uid("res://sub/deep.gd"))
	_dump("path_to_uid_tiny", ResourceUID.path_to_uid("res://tiny.png"))
	_dump("path_to_uid_absent", ResourceUID.path_to_uid("res://nope.gd"))
	_dump("ensure_path_thing", ResourceUID.ensure_path("res://assets/thing.gd"))
	_dump("create_id_for_path_nonexist", ResourceUID.create_id_for_path("res://nope.gd"))
	_dump("uid_to_path_str", ResourceUID.uid_to_path("uid://bq1a2b3c4d5e6"))
	_dump("uid_to_path_absent", ResourceUID.uid_to_path("uid://zzzzzzzzzzzzz"))
	_dump("uid_to_path_malformed", ResourceUID.uid_to_path("nope"))

func _arm_ids() -> void:
	var t := "res://assets/thing.gd"
	var s := FileAccess.get_file_as_string(t)
	_dump("thing_gd_text", s.replace("\n", "\\n"))
	# does a .tscn with uid= resolve?
	var s2 := FileAccess.get_file_as_string("res://scene.tscn")
	_dump("scene_text_len", s2.length())
	for line in s2.split("\n"):
		if line.begins_with("[") or line.begins_with("uid="):
			_dump("scene_line", line)
	var ps := ResourceLoader.load("res://scene.tscn")
	_dump("scene_load_null", ps == null)
	if ps != null:
		_dump("scene_root", ps.get_class())
