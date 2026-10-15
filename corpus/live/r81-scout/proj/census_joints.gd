extends SceneTree
# r81-scout scratch census — joint + collision-layer API surface (read-only).
# Dynamic (string-keyed) lookups only, so a missing constant cannot break the parse.

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	print("CENSUS godot=%s" % Engine.get_version_info().string)
	print("CENSUS engine2d=%s hint=%s sep_thread=%s tps=%s gravity=%s" % [
		ProjectSettings.get_setting("physics/2d/physics_engine"),
		ProjectSettings.get_setting("physics/2d/physics_engine", "?") ,
		ProjectSettings.get_setting("physics/2d/run_on_separate_thread"),
		ProjectSettings.get_setting("physics/common/physics_ticks_per_second"),
		ProjectSettings.get_setting("physics/2d/default_gravity")])
	print("CENSUS hint2d=%s" % ProjectSettings.get_setting("physics/2d/physics_engine"))
	var info := Engine.get_version_info()
	print("CENSUS 3dhint=%s" % ProjectSettings.get_setting("physics/3d/physics_engine"))

	for cls in ["Joint2D", "PinJoint2D", "GrooveJoint2D", "DampedSpringJoint2D"]:
		var props: Array = []
		for p in ClassDB.class_get_property_list(cls, true):
			props.append(String(p["name"]))
		props.sort()
		print("CLS %s props=%s" % [cls, props])
		var meths: Array = []
		for m in ClassDB.class_get_method_list(cls, true):
			meths.append(String(m["name"]))
		meths.sort()
		print("CLS %s methods=%s" % [cls, meths])

	var jm: Array = []
	for m in ClassDB.class_get_method_list("PhysicsServer2D", true):
		if String(m["name"]).contains("joint"):
			jm.append(String(m["name"]))
	jm.sort()
	print("SRV joint_methods=%s" % [jm])

	var consts: Array = ClassDB.class_get_integer_constant_list("PhysicsServer2D", true)
	consts.sort()
	var want := ["JOINT_PARAM_", "JOINT_TYPE_", "PIN_JOINT_", "DAMPED_SPRING_"]
	for c in consts:
		for w in want:
			if String(c).begins_with(w):
				print("CONST %s=%d" % [c, ClassDB.class_get_integer_constant("PhysicsServer2D", String(c))])

	# live joint: defaults via dynamic int lookup
	var j: RID = PhysicsServer2D.joint_create()
	var has_type: bool = PhysicsServer2D.has_method("joint_get_type")
	print("SRV has_joint_get_type=%s" % has_type)
	if has_type:
		print("DEF joint_type_new=%s" % PhysicsServer2D.call("joint_get_type", j))
	for nm in ["JOINT_PARAM_BIAS", "JOINT_PARAM_MAX_BIAS", "JOINT_PARAM_MAX_FORCE"]:
		var v: float = PhysicsServer2D.joint_get_param(j, ClassDB.class_get_integer_constant("PhysicsServer2D", nm))
		print("DEF %s=%.6f" % [nm, v])
	for nm2 in ["PIN_JOINT_SOFTNESS", "PIN_JOINT_LIMIT_UPPER", "PIN_JOINT_LIMIT_LOWER", "PIN_JOINT_MOTOR_TARGET_VELOCITY"]:
		var v2: float = PhysicsServer2D.pin_joint_get_param(j, ClassDB.class_get_integer_constant("PhysicsServer2D", nm2))
		print("DEF %s=%.6f" % [nm2, v2])
	for nm3 in ["PIN_JOINT_FLAG_ANGULAR_LIMIT_ENABLED", "PIN_JOINT_FLAG_MOTOR_ENABLED"]:
		var v3: bool = PhysicsServer2D.pin_joint_get_flag(j, ClassDB.class_get_integer_constant("PhysicsServer2D", nm3))
		print("DEF %s=%s" % [nm3, v3])
	for nm4 in ["DAMPED_SPRING_REST_LENGTH", "DAMPED_SPRING_STIFFNESS", "DAMPED_SPRING_DAMPING"]:
		var v4: float = PhysicsServer2D.damped_spring_joint_get_param(j, ClassDB.class_get_integer_constant("PhysicsServer2D", nm4))
		print("DEF %s=%.6f" % [nm4, v4])
	print("DEF joint_is_disabled_collisions_between_bodies=%s" % PhysicsServer2D.call("joint_is_disabled_collisions_between_bodies", j))
	PhysicsServer2D.free_rid(j)

	# collision object property names (layer/mask lattice carriers)
	var cprops: Array = []
	for p in ClassDB.class_get_property_list("CollisionObject2D", true):
		var n := String(p["name"])
		if n.begins_with("collision") or n == "input_pickable":
			cprops.append(n)
	cprops.sort()
	print("CLS CollisionObject2D layer_props=%s" % [cprops])
	var aprops: Array = []
	for p in ClassDB.class_get_property_list("Area2D", true):
		var n2 := String(p["name"])
		if n2 in ["monitoring", "monitorable", "priority"]:
			aprops.append(n2)
	aprops.sort()
	print("CLS Area2D monitor_props=%s" % [aprops])
	var signals: Array = []
	for s in ClassDB.class_get_signal_list("Area2D", true):
		signals.append(String(s["name"]))
	signals.sort()
	print("CLS Area2D signals=%s" % [signals])
	quit(0)
