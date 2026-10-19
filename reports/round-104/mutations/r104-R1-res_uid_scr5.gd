extends SceneTree
const TAG := "[r104R1e]"
func _dump(l: String, v) -> void:
	print("%s %s=%s" % [TAG, l, str(v)])
func _initialize() -> void:
	var argv := OS.get_cmdline_user_args()
	var arm := "malformed"
	for a in argv:
		if a.begins_with("--arm="):
			arm = a.substr(6)
	match arm:
		"malformed": _m()
		"fa": _fa()
		_: _dump("unknown", arm)
	print("PASS res_uid_scr5 arm=%s" % arm)
	quit(0)
func _m() -> void:
	for p in ["res://bad1.gd", "res://bad2.gd", "res://bad3.gd"]:
		_dump("exists", "%s file=%s" % [p, str(FileAccess.file_exists(p))])
		if FileAccess.file_exists(p + ".uid"):
			var t := FileAccess.get_file_as_string(p + ".uid").strip_edges()
			_dump("uidtext", "%s = [%s] id=%d" % [p, t, ResourceUID.text_to_id(t)])
			_dump("resolve", "%s has=%s path=%s" % [t, str(ResourceUID.has_id(ResourceUID.text_to_id(t))), ResourceUID.get_id_path(ResourceUID.text_to_id(t))])
		var r = ResourceLoader.load(p)
		_dump("load", "%s null=%s" % [p, str(r == null)])
func _fa() -> void:
	var u := "uid://cfo35nu5y4frk"
	_dump("fa_exists", FileAccess.file_exists(u))
	var s := FileAccess.get_file_as_string(u)
	_dump("fa_len", s.length())
	_dump("fa_bytes_hex", s.to_utf8_buffer().hex_encode().substr(0, 60))
	var f := FileAccess.open(u, FileAccess.READ)
	_dump("fa_open_len", f.get_length() if f != null else -1)
	var g := FileAccess.open("res://tiny.png", FileAccess.READ)
	_dump("png_len", g.get_length())
	var h := FileAccess.open("res://.godot/imported/tiny.png-4c2a616b3090ed27619d4dea97b52b2a.ctex", FileAccess.READ)
	_dump("ctex_len", h.get_length())
