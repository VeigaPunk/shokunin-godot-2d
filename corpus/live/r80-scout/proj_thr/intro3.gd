extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	for m in ClassDB.class_get_method_list("PhysicsBody2D", true):
		if m["name"] in ["move_and_collide", "test_move", "move_and_slide"]:
			print("SIG %s args=%s" % [m["name"], m["args"]])
	for m in ClassDB.class_get_method_list("KinematicCollision2D", true):
		print("KC %s(%s) flags=%d" % [m["name"], ", ".join(m["args"].map(func(a): return a["name"])), m["flags"]])
	for m in ClassDB.class_get_method_list("PhysicsTestMotionResult2D", true):
		print("TMR %s(%s) flags=%d" % [m["name"], ", ".join(m["args"].map(func(a): return a["name"])), m["flags"]])
	# global max_collisions census
	var found: Array = []
	for cls in ClassDB.get_class_list():
		for m in ClassDB.class_get_method_list(cls, true):
			for a in m["args"]:
				if "collisions" in a["name"] or "max_col" in a["name"]:
					found.append("%s.%s(%s)" % [cls, m["name"], a["name"]])
		for p in ClassDB.class_get_property_list(cls, true):
			if "collision" in p["name"]:
				if "max" in p["name"] or "count" in p["name"]:
					found.append("%s.prop:%s" % [cls, p["name"]])
	print("CENSUS max_collisions-related: %s" % found)
	print("DONE")
	quit(0)
