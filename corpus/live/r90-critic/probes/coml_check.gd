extends SceneTree
func _initialize() -> void:
	var b := RigidBody2D.new()
	root.add_child(b)
	var names: PackedStringArray = []
	for p in b.get_property_list():
		if String(p["name"]).contains("center_of_mass"):
			names.append(String(p["name"]))
	print("PROBE instance_com_props=%s" % "|".join(names))
	print("PROBE get_center_of_mass_local=%s" % str(b.get("center_of_mass_local")))
	print("PROBE has_method_get=%s" % b.has_method("get_center_of_mass_local"))
	print("PROBE classdb_has=%s" % ClassDB.class_get_property_list("RigidBody2D").any(func(p): return String(p["name"]) == "center_of_mass_local"))
	quit()
