extends SceneTree
const TAG := "[r104R1f]"
func _dump(l: String, v) -> void:
	print("%s %s=%s" % [TAG, l, str(v)])
func _initialize() -> void:
	var consts := ClassDB.class_get_integer_constant_list("ResourceUID", true)
	_dump("int_consts", "|".join(consts))
	for c in consts:
		_dump("const", "%s=%s" % [c, str(ClassDB.class_get_integer_constant("ResourceUID", c))])
	_dump("invalid_id", ResourceUID.INVALID_ID)
	_dump("get_id_path_invalid", ResourceUID.get_id_path(ResourceUID.INVALID_ID))
	_dump("has_id_invalid", ResourceUID.has_id(ResourceUID.INVALID_ID))
	_dump("id_to_text_0", ResourceUID.id_to_text(0))
	_dump("id_to_text_1", ResourceUID.id_to_text(1))
	# 2^63 boundary
	_dump("id_to_text_2p63m1", ResourceUID.id_to_text(9223372036854775807))
	_dump("text_to_id_roundtrip_max", ResourceUID.text_to_id(ResourceUID.id_to_text(9223372036854775807)))
	print("PASS res_uid_scr6 arm=consts")
	quit(0)
