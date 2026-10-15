extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	for cls in ["PhysicsBody2D", "PhysicsServer2D", "KinematicCollision2D", "PhysicsTestMotionParameters2D", "PhysicsTestMotionResult2D"]:
		print("=== %s ===" % cls)
		for m in ClassDB.class_get_method_list(cls, true):
			var n: String = m["name"]
			var keep: bool = ("move" in n) or ("test" in n) or ("motion" in n) or ("collid" in n) or ("contact" in n) or ("collision" in n) or ("body_" in n and cls == "PhysicsServer2D")
			if keep:
				var args: Array = []
				for a in m["args"]:
					var dv = a.get("default_value")
					args.append("%s%s" % [a["name"], "=%s" % dv if dv != null else ""])
				var ret: String = m["return"].get("class_name", "") if m["return"]["type"] == TYPE_OBJECT else type_string(m["return"]["type"])
				print("  %s(%s) -> %s flags=%d" % [n, ", ".join(args), ret, m["flags"]])
		if cls == "KinematicCollision2D":
			for m in ClassDB.class_get_method_list(cls, true):
				print("  KC2D %s flags=%d" % [m["name"], m["flags"]])
	print("CCD enums: DISABLED=%d RAY=%d SHAPE=%d" % [RigidBody2D.CCD_MODE_DISABLED, RigidBody2D.CCD_MODE_CAST_RAY, RigidBody2D.CCD_MODE_CAST_SHAPE])
	print("DONE")
	quit(0)
