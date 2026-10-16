extends SceneTree
# r92 critic seat instrument (NOT part of the fixture corpus): prints the
# measured TileMapLayer property list so the `layer_props=n16[...]` census
# token can be checked against the engine, not against the authored list.

func _initialize() -> void:
	var layer := TileMapLayer.new()
	var db: Array = ClassDB.class_get_property_list("TileMapLayer", true)
	var inst: Array = layer.get_property_list()
	var names := PackedStringArray()
	for p in db:
		names.append(p["name"])
	print("DB_COUNT=%d" % db.size())
	print("DB_NAMES=%s" % ",".join(names))
	var declared := PackedStringArray()
	for p in inst:
		declared.append(p["name"])
	print("INST_COUNT=%d" % inst.size())
	print("INST_HAS_COLLISION_PRIORITY=%s" % str(inst.any(
		func(p: Dictionary) -> bool: return p["name"] == "collision_priority")))
	layer.free()
	quit()
