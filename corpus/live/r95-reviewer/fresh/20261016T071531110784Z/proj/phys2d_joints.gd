extends SceneTree
# r81 fixture — Godot-4 2D joint lattice + collision layer/mask lattice (read-only).
# One arm per process, exactly the battery's launch shape:
#   godot --headless --path <scratch> --script res://phys2d_joints.gd -- --arm=<name>
# Prints R81 diagnostic lines and one final `PASS phys2d_joints <arm> ...` line.
# No object ids / addresses / RIDs are printed (byte-stability).
# The `match arm:` dispatch in _run is the sole arm index (20 arms);
# per-arm measured classes live in r81-scout §1.1-1.3.

const WALL_X := 100.0
const LANE := 2000.0

var arm := ""
var _frame_no := 0
var _raw_rids: Array = []
var _tracked_nodes: Array = []

class Track extends RefCounted:
	var ent: Array = []
	var ext: Array = []
	var cnt: Dictionary = {}
	var seq: Array = []

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")

func _run() -> void:
	print("R81 arm=%s godot=%s engine2d=%s sep_thread=%s tps=%s" % [
		arm, Engine.get_version_info().string,
		ProjectSettings.get_setting("physics/2d/physics_engine"),
		ProjectSettings.get_setting("physics/2d/run_on_separate_thread"),
		ProjectSettings.get_setting("physics/common/physics_ticks_per_second")])
	match arm:
		"joint_census": await _arm_joint_census()
		"joint_unset_refusal": await _arm_joint_unset_refusal()
		"joint_pin_tiers": await _arm_joint_pin_tiers()
		"joint_pin_clear": await _arm_joint_pin_clear()
		"joint_node_clear": await _arm_joint_node_clear()
		"joint_freed_rid": await _arm_joint_freed_rid()
		"joint_node_freed_rid": await _arm_joint_node_freed_rid()
		"joint_spring_env": await _arm_joint_spring_env()
		"joint_pin_params": await _arm_joint_pin_params()
		"joint_node_anchor": await _arm_joint_node_anchor()
		"joint_groove": await _arm_joint_groove()
		"joint_disable_coll": await _arm_joint_disable_coll()
		"layer_or_table": await _arm_layer_or_table()
		"layer_zero_table": await _arm_layer_zero_table()
		"layer_dyn_pair": await _arm_layer_dyn_pair()
		"layer_flip_mid": await _arm_layer_flip_mid()
		"layer_flip_cb": await _arm_layer_flip_cb()
		"area_lattice": await _arm_area_lattice()
		"area_body_gate": await _arm_area_body_gate()
		"area_entry_order": await _arm_area_entry_order()
		_: _fail("unknown_arm")

func _fail(reason: String) -> void:
	print("FAIL phys2d_joints %s reason=%s" % [arm, reason])
	quit(1)

func _finish(line: String) -> void:
	# The queue_free loop is load-bearing, not hygiene: it runs node-joint
	# destructors in the pre-quit deferred window, and joint_node_freed_rid
	# pins that destructor's double-free diagnostic stream byte-exact.
	for n in _tracked_nodes:
		if is_instance_valid(n):
			n.queue_free()
	_tracked_nodes.clear()
	# Raw joint RIDs are caller-owned and MUST be freed here — a leaked joint
	# RID prints `ERROR: N RID allocations of type 'P12GodotJoint2D' were
	# leaked at exit.` and fails classification.
	_free_tracked()
	print("PASS phys2d_joints " + line)
	quit(0)

func _track(rid: RID) -> RID:
	_raw_rids.append(rid)
	return rid

func _untrack(rid: RID) -> void:
	_raw_rids.erase(rid)

func _free_tracked() -> void:
	for i in range(_raw_rids.size() - 1, -1, -1):
		PhysicsServer2D.free_rid(_raw_rids[i])
	_raw_rids.clear()

func _frames(n: int) -> void:
	for i in n:
		await physics_frame
		_frame_no += 1

func _fv(v: Vector2) -> String:
	return "(%.4f,%.4f)" % [v.x, v.y]

func _v2(v: Vector2) -> String:
	return "(%.2f,%.2f)" % [v.x, v.y]

# ------------------------------------------------------------------ factories

func _mk_static_lm(pos: Vector2, size: Vector2, layer: int, mask: int) -> StaticBody2D:
	var b := StaticBody2D.new()
	var cs := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = size
	cs.shape = rs
	b.add_child(cs)
	b.position = pos
	b.collision_layer = layer
	b.collision_mask = mask
	root.add_child(b)
	_tracked_nodes.append(b)
	return b

func _mk_static(pos: Vector2, size: Vector2) -> StaticBody2D:
	return _mk_static_lm(pos, size, 1, 1)

func _mk_dyn_lm(pos: Vector2, size: Vector2, vel: Vector2,
		layer: int, mask: int, cm: bool, lock_rot: bool = false) -> RigidBody2D:
	var b := RigidBody2D.new()
	var cs := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = size
	cs.shape = rs
	b.add_child(cs)
	b.position = pos
	b.gravity_scale = 0.0
	b.can_sleep = false
	b.contact_monitor = cm
	if cm:
		b.max_contacts_reported = 4
	b.collision_layer = layer
	b.collision_mask = mask
	b.lock_rotation = lock_rot
	root.add_child(b)
	b.linear_velocity = vel
	_tracked_nodes.append(b)
	return b

func _mk_dyn(pos: Vector2, size: Vector2, vel: Vector2) -> RigidBody2D:
	return _mk_dyn_lm(pos, size, vel, 1, 1, false)

func _mk_area(pos: Vector2, size: Vector2, mon: bool, mable: bool,
		layer: int, mask: int) -> Area2D:
	var a := Area2D.new()
	var cs := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = size
	cs.shape = rs
	a.add_child(cs)
	a.position = pos
	a.monitoring = mon
	a.monitorable = mable
	a.collision_layer = layer
	a.collision_mask = mask
	root.add_child(a)
	_tracked_nodes.append(a)
	return a

# ------------------------------------------------------------------ joints

func _arm_joint_census() -> void:
	var jm: Array = []
	for m in ClassDB.class_get_method_list("PhysicsServer2D", true):
		var n := String(m["name"])
		if n.contains("joint"):
			var args: Array = []
			for a in m["args"]:
				args.append(String(a["name"]))
			jm.append("%s(%s)" % [n, ",".join(args)])
	jm.sort()
	var cls_out: Array = []
	for cls in ["Joint2D", "PinJoint2D", "GrooveJoint2D", "DampedSpringJoint2D"]:
		var props: Array = []
		for p in ClassDB.class_get_property_list(cls, true):
			props.append(String(p["name"]))
		props.sort()
		cls_out.append("%s%s" % [cls, props])
	var cs: Array = ClassDB.class_get_integer_constant_list("PhysicsServer2D", true)
	cs.sort()
	var want := ["JOINT_PARAM_", "JOINT_TYPE_", "PIN_JOINT_", "DAMPED_SPRING_"]
	var consts: Array = []
	for c in cs:
		for w in want:
			if String(c).begins_with(w):
				consts.append("%s=%d" % [c, ClassDB.class_get_integer_constant("PhysicsServer2D", String(c))])
	var a := _mk_static(Vector2(0, 0), Vector2(20, 20))
	var b := _mk_static(Vector2(200, 0), Vector2(20, 20))
	var j: RID = _track(PhysicsServer2D.joint_create())
	var out: Array = []
	out.append("unset_type=%d" % PhysicsServer2D.joint_get_type(j))
	out.append("unset_dis=%s" % PhysicsServer2D.joint_is_disabled_collisions_between_bodies(j))
	out.append("unset_bias=%.4f" % PhysicsServer2D.joint_get_param(j, PhysicsServer2D.JOINT_PARAM_BIAS))
	out.append("max_bias=%s" % str(snappedf(PhysicsServer2D.joint_get_param(j, PhysicsServer2D.JOINT_PARAM_MAX_BIAS), 1.0)))
	out.append("max_force=%s" % str(snappedf(PhysicsServer2D.joint_get_param(j, PhysicsServer2D.JOINT_PARAM_MAX_FORCE), 1.0)))
	PhysicsServer2D.joint_make_pin(j, Vector2.ZERO, a.get_rid(), b.get_rid())
	out.append("pin_type=%d" % PhysicsServer2D.joint_get_type(j))
	out.append("pin_soft=%.4f" % PhysicsServer2D.pin_joint_get_param(j, PhysicsServer2D.PIN_JOINT_SOFTNESS))
	out.append("pin_lu=%.4f" % PhysicsServer2D.pin_joint_get_param(j, PhysicsServer2D.PIN_JOINT_LIMIT_UPPER))
	out.append("pin_ll=%.4f" % PhysicsServer2D.pin_joint_get_param(j, PhysicsServer2D.PIN_JOINT_LIMIT_LOWER))
	out.append("pin_mtv=%.4f" % PhysicsServer2D.pin_joint_get_param(j, PhysicsServer2D.PIN_JOINT_MOTOR_TARGET_VELOCITY))
	out.append("pin_flag_ang=%s" % PhysicsServer2D.pin_joint_get_flag(j, PhysicsServer2D.PIN_JOINT_FLAG_ANGULAR_LIMIT_ENABLED))
	out.append("pin_flag_motor=%s" % PhysicsServer2D.pin_joint_get_flag(j, PhysicsServer2D.PIN_JOINT_FLAG_MOTOR_ENABLED))
	out.append("pin_bias=%.4f" % PhysicsServer2D.joint_get_param(j, PhysicsServer2D.JOINT_PARAM_BIAS))
	out.append("pin_dis=%s" % PhysicsServer2D.joint_is_disabled_collisions_between_bodies(j))
	PhysicsServer2D.joint_make_groove(j, Vector2.ZERO, Vector2(0, 100), Vector2(200, 0), a.get_rid(), b.get_rid())
	out.append("groove_type=%d" % PhysicsServer2D.joint_get_type(j))
	out.append("groove_bias=%.4f" % PhysicsServer2D.joint_get_param(j, PhysicsServer2D.JOINT_PARAM_BIAS))
	PhysicsServer2D.joint_make_damped_spring(j, Vector2.ZERO, Vector2(200, 0), a.get_rid(), b.get_rid())
	out.append("spring_type=%d" % PhysicsServer2D.joint_get_type(j))
	out.append("spring_rest=%.4f" % PhysicsServer2D.damped_spring_joint_get_param(j, PhysicsServer2D.DAMPED_SPRING_REST_LENGTH))
	out.append("spring_stiff=%.4f" % PhysicsServer2D.damped_spring_joint_get_param(j, PhysicsServer2D.DAMPED_SPRING_STIFFNESS))
	out.append("spring_damp=%.4f" % PhysicsServer2D.damped_spring_joint_get_param(j, PhysicsServer2D.DAMPED_SPRING_DAMPING))
	out.append("spring_dis=%s" % PhysicsServer2D.joint_is_disabled_collisions_between_bodies(j))
	_finish("joint_census cls=%s srv=%s consts=%s live=%s" % [cls_out, jm, consts, out])

func _probe_joint_getters(j: RID) -> Array:
	# The refusal lattice read order: pin params, pin flags, spring params.
	return [
		PhysicsServer2D.pin_joint_get_param(j, PhysicsServer2D.PIN_JOINT_SOFTNESS),
		PhysicsServer2D.pin_joint_get_param(j, PhysicsServer2D.PIN_JOINT_LIMIT_UPPER),
		PhysicsServer2D.pin_joint_get_param(j, PhysicsServer2D.PIN_JOINT_LIMIT_LOWER),
		PhysicsServer2D.pin_joint_get_param(j, PhysicsServer2D.PIN_JOINT_MOTOR_TARGET_VELOCITY),
		PhysicsServer2D.pin_joint_get_flag(j, PhysicsServer2D.PIN_JOINT_FLAG_ANGULAR_LIMIT_ENABLED),
		PhysicsServer2D.pin_joint_get_flag(j, PhysicsServer2D.PIN_JOINT_FLAG_MOTOR_ENABLED),
		PhysicsServer2D.damped_spring_joint_get_param(j, PhysicsServer2D.DAMPED_SPRING_REST_LENGTH),
		PhysicsServer2D.damped_spring_joint_get_param(j, PhysicsServer2D.DAMPED_SPRING_STIFFNESS),
		PhysicsServer2D.damped_spring_joint_get_param(j, PhysicsServer2D.DAMPED_SPRING_DAMPING),
	]

func _arm_joint_unset_refusal() -> void:
	var j: RID = _track(PhysicsServer2D.joint_create())
	var before: Array = _probe_joint_getters(j)
	var a := _mk_static(Vector2(0, 0), Vector2(20, 20))
	var b := _mk_static(Vector2(200, 0), Vector2(20, 20))
	PhysicsServer2D.joint_make_pin(j, Vector2.ZERO, a.get_rid(), b.get_rid())
	var after: Array = _probe_joint_getters(j)
	var type_pin: int = PhysicsServer2D.joint_get_type(j)
	PhysicsServer2D.joint_clear(j)
	var cleared_type: int = PhysicsServer2D.joint_get_type(j)
	PhysicsServer2D.joint_make_damped_spring(j, Vector2.ZERO, Vector2(200, 0), a.get_rid(), b.get_rid())
	var spring_after: Array = [
		PhysicsServer2D.damped_spring_joint_get_param(j, PhysicsServer2D.DAMPED_SPRING_REST_LENGTH),
		PhysicsServer2D.damped_spring_joint_get_param(j, PhysicsServer2D.DAMPED_SPRING_STIFFNESS),
		PhysicsServer2D.damped_spring_joint_get_param(j, PhysicsServer2D.DAMPED_SPRING_DAMPING),
	]
	_finish("joint_unset_refusal before=%s type_pin=%d after=%s cleared_type=%d spring_after=%s" % [
		before, type_pin, after, cleared_type, spring_after])

func _arm_joint_pin_tiers() -> void:
	var a1 := _mk_static(Vector2(0, 0), Vector2(20, 20))
	a1.name = "PA"  # printed: n_np resolves node_a's stored path
	var b1 := _mk_dyn(Vector2(200, 0), Vector2(20, 20), Vector2(0, 300))
	var pin := PinJoint2D.new()
	pin.node_a = a1.get_path()
	pin.node_b = b1.get_path()
	pin.position = Vector2(0, 0)
	root.add_child(pin)
	_tracked_nodes.append(pin)
	var a2 := _mk_static(Vector2(0, LANE), Vector2(20, 20))
	var b2 := _mk_dyn(Vector2(200, LANE), Vector2(20, 20), Vector2(0, 300))
	var j: RID = _track(PhysicsServer2D.joint_create())
	PhysicsServer2D.joint_make_pin(j, Vector2(0, LANE), a2.get_rid(), b2.get_rid())
	# r81-fold C1: same-position control — a NODE pin in the server lane's y
	# band (x-offset so its bodies cannot interact with the server lane's).
	# The n/s divergence is the 2000 px translation, not the node/server
	# path: n2 must read like s_dist, not n_dist.
	var a3 := _mk_static(Vector2(2000, LANE), Vector2(20, 20))
	var b3 := _mk_dyn(Vector2(2200, LANE), Vector2(20, 20), Vector2(0, 300))
	var pin2 := PinJoint2D.new()
	pin2.node_a = a3.get_path()
	pin2.node_b = b3.get_path()
	pin2.position = Vector2(2000, LANE)
	root.add_child(pin2)
	_tracked_nodes.append(pin2)
	await _frames(40)
	var n_rel := b1.global_position
	var s_rel := b2.global_position - Vector2(0, LANE)
	var n2_rel := b3.global_position - Vector2(2000, LANE)
	var n_rid: RID = pin.get_rid()
	_finish("joint_pin_tiers n_rel=%s s_rel=%s n_dist=%.4f s_dist=%.4f n2_dist=%.4f n_type=%d s_type=%d n_np=%s n_bias_prop=%.4f n_bias_srv=%.4f s_bias_srv=%.4f n_soft_prop=%.4f n_soft_srv=%.4f s_soft_srv=%.4f n_dis=%s s_dis=%s n_flag_ang=%s n_flag_motor=%s" % [
		_fv(n_rel), _fv(s_rel), n_rel.length(), s_rel.length(), n2_rel.length(),
		PhysicsServer2D.joint_get_type(n_rid), PhysicsServer2D.joint_get_type(j),
		str(pin.node_a), pin.bias,
		PhysicsServer2D.joint_get_param(n_rid, PhysicsServer2D.JOINT_PARAM_BIAS),
		PhysicsServer2D.joint_get_param(j, PhysicsServer2D.JOINT_PARAM_BIAS),
		pin.softness,
		PhysicsServer2D.pin_joint_get_param(n_rid, PhysicsServer2D.PIN_JOINT_SOFTNESS),
		PhysicsServer2D.pin_joint_get_param(j, PhysicsServer2D.PIN_JOINT_SOFTNESS),
		PhysicsServer2D.joint_is_disabled_collisions_between_bodies(n_rid),
		PhysicsServer2D.joint_is_disabled_collisions_between_bodies(j),
		PhysicsServer2D.pin_joint_get_flag(n_rid, PhysicsServer2D.PIN_JOINT_FLAG_ANGULAR_LIMIT_ENABLED),
		PhysicsServer2D.pin_joint_get_flag(n_rid, PhysicsServer2D.PIN_JOINT_FLAG_MOTOR_ENABLED)])

func _arm_joint_pin_clear() -> void:
	var a := _mk_static(Vector2(0, 0), Vector2(20, 20))
	var b := _mk_dyn(Vector2(200, 0), Vector2(20, 20), Vector2(0, 300))
	var j: RID = _track(PhysicsServer2D.joint_create())
	PhysicsServer2D.joint_make_pin(j, Vector2.ZERO, a.get_rid(), b.get_rid())
	await _frames(20)
	var pre := _fv(b.global_position)
	var pre_dist: float = b.global_position.length()
	var pre_vel := _fv(b.linear_velocity)
	var type_pre: int = PhysicsServer2D.joint_get_type(j)
	PhysicsServer2D.joint_clear(j)
	var type_post: int = PhysicsServer2D.joint_get_type(j)
	var bias_post: float = PhysicsServer2D.joint_get_param(j, PhysicsServer2D.JOINT_PARAM_BIAS)
	var soft_post: float = PhysicsServer2D.pin_joint_get_param(j, PhysicsServer2D.PIN_JOINT_SOFTNESS)
	await _frames(30)
	var post := _fv(b.global_position)
	var post_dist: float = b.global_position.length()
	var post_vel := _fv(b.linear_velocity)
	PhysicsServer2D.joint_make_pin(j, Vector2.ZERO, a.get_rid(), b.get_rid())
	var type_rearm: int = PhysicsServer2D.joint_get_type(j)
	await _frames(30)
	var end_pos := _fv(b.global_position)
	var end_dist: float = b.global_position.length()
	_finish("joint_pin_clear pre=%s pre_dist=%.4f pre_vel=%s type_pre=%d type_post=%d bias_post=%.4f soft_post=%.4f post=%s post_dist=%.4f post_vel=%s type_rearm=%d end=%s end_dist=%.4f" % [
		pre, pre_dist, pre_vel, type_pre, type_post, bias_post, soft_post,
		post, post_dist, post_vel, type_rearm, end_pos, end_dist])

func _arm_joint_node_clear() -> void:
	var a := _mk_static(Vector2(0, 0), Vector2(20, 20))
	var b := _mk_dyn(Vector2(200, 0), Vector2(20, 20), Vector2(0, 300))
	var pin := PinJoint2D.new()
	pin.node_a = a.get_path()
	pin.node_b = b.get_path()
	pin.position = Vector2(0, 0)
	root.add_child(pin)
	_tracked_nodes.append(pin)
	await _frames(20)
	var rid: RID = pin.get_rid()
	var pre := _fv(b.global_position)
	var type_pre: int = PhysicsServer2D.joint_get_type(rid)
	pin.global_position = Vector2(0, 100)
	var nudge_pos := _fv(pin.global_position)
	await _frames(1)
	var type_live_nudge: int = PhysicsServer2D.joint_get_type(rid)
	await _frames(19)
	var dn_old: float = b.global_position.length()
	var dn_new: float = (b.global_position - Vector2(0, 100)).length()
	await _frames(1)
	var dn_old2: float = b.global_position.length()
	var dn_new2: float = (b.global_position - Vector2(0, 100)).length()
	var after_nudge := _fv(b.global_position)
	PhysicsServer2D.joint_clear(rid)
	var type_post: int = PhysicsServer2D.joint_get_type(rid)
	await _frames(20)
	var post := _fv(b.global_position)
	pin.global_position = Vector2(0, 100.5)
	await _frames(1)
	var type_nudge2: int = PhysicsServer2D.joint_get_type(rid)
	await _frames(19)
	var end_pos := _fv(b.global_position)
	_finish("joint_node_clear pre=%s type_pre=%d nudge_type=%d nudge_pos=%s after_nudge=%s dn_old=%.4f dn_new=%.4f dn_old2=%.4f dn_new2=%.4f type_post=%d post=%s nudge2_type=%d end=%s end_d_old=%.4f end_d_new=%.4f valid=%s na=%s nb=%s" % [
		pre, type_pre, type_live_nudge, nudge_pos, after_nudge, dn_old, dn_new, dn_old2, dn_new2,
		type_post, post, type_nudge2, end_pos,
		b.global_position.length(), (b.global_position - Vector2(0, 100)).length(),
		str(is_instance_valid(pin)), str(pin.node_a != NodePath()), str(pin.node_b != NodePath())])

func _arm_joint_freed_rid() -> void:
	var a := _mk_static(Vector2(0, 0), Vector2(20, 20))
	var b := _mk_dyn(Vector2(200, 0), Vector2(20, 20), Vector2(0, 300))
	var j: RID = _track(PhysicsServer2D.joint_create())
	PhysicsServer2D.joint_make_pin(j, Vector2.ZERO, a.get_rid(), b.get_rid())
	await _frames(20)
	var pre := _fv(b.global_position)
	_untrack(j)
	PhysicsServer2D.free_rid(j)
	var type_freed: int = PhysicsServer2D.joint_get_type(j)
	var bias_freed: float = PhysicsServer2D.joint_get_param(j, PhysicsServer2D.JOINT_PARAM_BIAS)
	PhysicsServer2D.joint_clear(j)
	var soft_freed: float = PhysicsServer2D.pin_joint_get_param(j, PhysicsServer2D.PIN_JOINT_SOFTNESS)
	PhysicsServer2D.joint_make_pin(j, Vector2.ZERO, a.get_rid(), b.get_rid())
	var type_remade: int = PhysicsServer2D.joint_get_type(j)
	# r81-fold C8: the remade joint must honor a param read — a dead RID would
	# still return the -1.0 sentinel, so type=0 alone does not pin the re-make.
	var bias_remade: float = PhysicsServer2D.joint_get_param(j, PhysicsServer2D.JOINT_PARAM_BIAS)
	await _frames(30)
	var post := _fv(b.global_position)
	await _frames(10)
	var late := _fv(b.global_position)
	_finish("joint_freed_rid pre=%s type_freed=%d bias_freed=%.4f soft_freed=%.4f type_remade=%d bias_remade=%.4f post=%s late=%s b_frozen=%s b_valid=%s" % [
		pre, type_freed, bias_freed, soft_freed, type_remade, bias_remade, post, late,
		str(post == late), str(is_instance_valid(b))])

func _arm_joint_node_freed_rid() -> void:
	var a := _mk_static(Vector2(0, 0), Vector2(20, 20))
	var b := _mk_dyn(Vector2(200, 0), Vector2(20, 20), Vector2(0, 300))
	var pin := PinJoint2D.new()
	pin.node_a = a.get_path()
	pin.node_b = b.get_path()
	pin.position = Vector2(0, 0)
	root.add_child(pin)
	_tracked_nodes.append(pin)
	await _frames(20)
	var rid: RID = pin.get_rid()
	var pre := _fv(b.global_position)
	PhysicsServer2D.free_rid(rid)
	var type_freed: int = PhysicsServer2D.joint_get_type(rid)
	var rid_again: RID = pin.get_rid()
	var type_again: int = PhysicsServer2D.joint_get_type(rid_again)
	await _frames(30)
	var post := _fv(b.global_position)
	pin.global_position = Vector2(0, 0.5)
	await _frames(1)
	var type_nudge: int = PhysicsServer2D.joint_get_type(rid_again)
	await _frames(29)
	var end_pos := _fv(b.global_position)
	_finish("joint_node_freed_rid pre=%s type_freed=%d rid_same=%s type_again=%d valid=%s post=%s type_nudge=%d end=%s end_dist=%.4f b_frozen=%s" % [
		pre, type_freed, str(rid == rid_again), type_again, str(is_instance_valid(pin)), post, type_nudge,
		end_pos, b.global_position.length(), str(post == end_pos)])

func _arm_joint_spring_env() -> void:
	var stiffs := [0.0, 4.0, 16.0, 64.0]
	var damps := [0.0, 1.0, 4.0]
	var lanes: Array = []
	var i := 0
	for s in stiffs:
		for d in damps:
			var y := float(i) * LANE
			i += 1
			var a := _mk_static(Vector2(0, y), Vector2(20, 20))
			var b := _mk_dyn(Vector2(100, y), Vector2(20, 20), Vector2(0, -120))
			var j: RID = _track(PhysicsServer2D.joint_create())
			PhysicsServer2D.joint_make_damped_spring(j, Vector2(0, y), Vector2(100, y), a.get_rid(), b.get_rid())
			PhysicsServer2D.damped_spring_joint_set_param(j, PhysicsServer2D.DAMPED_SPRING_REST_LENGTH, 50.0)
			PhysicsServer2D.damped_spring_joint_set_param(j, PhysicsServer2D.DAMPED_SPRING_STIFFNESS, s)
			PhysicsServer2D.damped_spring_joint_set_param(j, PhysicsServer2D.DAMPED_SPRING_DAMPING, d)
			lanes.append({"s": s, "d": d, "b": b, "y": y, "j": j})
	var yc := float(i) * LANE
	i += 1
	var bc := _mk_dyn(Vector2(100, yc), Vector2(20, 20), Vector2(0, -120))
	var yn := float(i) * LANE
	var an := _mk_static(Vector2(0, yn), Vector2(20, 20))
	var bn := _mk_dyn(Vector2(0, yn + 100), Vector2(20, 20), Vector2.ZERO)
	var sp := DampedSpringJoint2D.new()
	sp.length = 100.0
	sp.rest_length = 50.0
	sp.stiffness = 64.0
	sp.damping = 1.0
	sp.node_a = an.get_path()
	sp.node_b = bn.get_path()
	sp.position = Vector2(0, yn)
	root.add_child(sp)
	_tracked_nodes.append(sp)
	await _frames(30)
	var out: Array = []
	for L in lanes:
		var b: RigidBody2D = L["b"]
		out.append("s%.0fd%.0f=%s" % [L["s"], L["d"], _v2(b.global_position - Vector2(0, L["y"]))])
	out.append("nojoint=%s" % _v2(bc.global_position - Vector2(0, yc)))
	var j0: RID = lanes[0]["j"]
	out.append("rb_s0d0=[%.4f,%.4f,%.4f]" % [
		PhysicsServer2D.damped_spring_joint_get_param(j0, PhysicsServer2D.DAMPED_SPRING_REST_LENGTH),
		PhysicsServer2D.damped_spring_joint_get_param(j0, PhysicsServer2D.DAMPED_SPRING_STIFFNESS),
		PhysicsServer2D.damped_spring_joint_get_param(j0, PhysicsServer2D.DAMPED_SPRING_DAMPING)])
	out.append("rb_s64d4=[%.4f,%.4f,%.4f]" % [
		PhysicsServer2D.damped_spring_joint_get_param(lanes[11]["j"], PhysicsServer2D.DAMPED_SPRING_REST_LENGTH),
		PhysicsServer2D.damped_spring_joint_get_param(lanes[11]["j"], PhysicsServer2D.DAMPED_SPRING_STIFFNESS),
		PhysicsServer2D.damped_spring_joint_get_param(lanes[11]["j"], PhysicsServer2D.DAMPED_SPRING_DAMPING)])
	var srid: RID = sp.get_rid()
	out.append("node_props=[l=%.1f,r=%.1f,s=%.1f,d=%.1f]" % [sp.length, sp.rest_length, sp.stiffness, sp.damping])
	out.append("node_srv=[%.4f,%.4f,%.4f]" % [
		PhysicsServer2D.damped_spring_joint_get_param(srid, PhysicsServer2D.DAMPED_SPRING_REST_LENGTH),
		PhysicsServer2D.damped_spring_joint_get_param(srid, PhysicsServer2D.DAMPED_SPRING_STIFFNESS),
		PhysicsServer2D.damped_spring_joint_get_param(srid, PhysicsServer2D.DAMPED_SPRING_DAMPING)])
	out.append("node_type=%d node_pos=%s" % [PhysicsServer2D.joint_get_type(srid), _v2(bn.global_position - Vector2(0, yn))])
	_finish("joint_spring_env " + " ".join(out))

func _arm_joint_pin_params() -> void:
	# tag, kind, value: softness envelope, motor, angular limit, bias
	var specs := [
		["soft0", "soft", 0.0],
		["soft1", "soft", 1.0],
		["soft4", "soft", 4.0],
		["motor", "motor", 3.0],
		["limit", "limit", 0.5],
		["bias1", "bias", 1.0],
		["motor_spin", "motor_spin", 3.0],
		["limit_spin", "limit_spin", 0.5],
	]
	var lanes: Array = []
	var i := 0
	for s in specs:
		var y := float(i) * LANE
		i += 1
		var a := _mk_static(Vector2(0, y), Vector2(20, 20))
		var b := _mk_dyn(Vector2(200, y), Vector2(20, 20), Vector2(0, 300))
		var j: RID = _track(PhysicsServer2D.joint_create())
		var kind := String(s[1])
		var anchor := Vector2(0, y)
		if kind.ends_with("spin"):
			anchor = Vector2(200, y)
			b.linear_velocity = Vector2.ZERO
		PhysicsServer2D.joint_make_pin(j, anchor, a.get_rid(), b.get_rid())
		match kind:
			"soft":
				PhysicsServer2D.pin_joint_set_param(j, PhysicsServer2D.PIN_JOINT_SOFTNESS, s[2])
			"motor", "motor_spin":
				PhysicsServer2D.pin_joint_set_flag(j, PhysicsServer2D.PIN_JOINT_FLAG_MOTOR_ENABLED, true)
				PhysicsServer2D.pin_joint_set_param(j, PhysicsServer2D.PIN_JOINT_MOTOR_TARGET_VELOCITY, s[2])
			"limit", "limit_spin":
				PhysicsServer2D.pin_joint_set_flag(j, PhysicsServer2D.PIN_JOINT_FLAG_ANGULAR_LIMIT_ENABLED, true)
				PhysicsServer2D.pin_joint_set_param(j, PhysicsServer2D.PIN_JOINT_LIMIT_LOWER, -s[2])
				PhysicsServer2D.pin_joint_set_param(j, PhysicsServer2D.PIN_JOINT_LIMIT_UPPER, s[2])
			"bias":
				PhysicsServer2D.joint_set_param(j, PhysicsServer2D.JOINT_PARAM_BIAS, s[2])
		if kind == "limit_spin":
			b.angular_velocity = 3.0
		lanes.append({"tag": s[0], "b": b, "y": y, "j": j})
	await _frames(40)
	var out: Array = []
	for L in lanes:
		var b: RigidBody2D = L["b"]
		var j: RID = L["j"]
		out.append("%s[pos=%s dist=%.4f rot=%.4f rb=[%.4f,%.4f,%s,%.4f,%.4f,%s,%.4f]]" % [
			L["tag"], _v2(b.global_position - Vector2(0, L["y"])),
			(b.global_position - Vector2(0, L["y"])).length(), b.global_rotation,
			PhysicsServer2D.pin_joint_get_param(j, PhysicsServer2D.PIN_JOINT_SOFTNESS),
			PhysicsServer2D.pin_joint_get_param(j, PhysicsServer2D.PIN_JOINT_MOTOR_TARGET_VELOCITY),
			PhysicsServer2D.pin_joint_get_flag(j, PhysicsServer2D.PIN_JOINT_FLAG_MOTOR_ENABLED),
			PhysicsServer2D.pin_joint_get_param(j, PhysicsServer2D.PIN_JOINT_LIMIT_LOWER),
			PhysicsServer2D.pin_joint_get_param(j, PhysicsServer2D.PIN_JOINT_LIMIT_UPPER),
			PhysicsServer2D.pin_joint_get_flag(j, PhysicsServer2D.PIN_JOINT_FLAG_ANGULAR_LIMIT_ENABLED),
			PhysicsServer2D.joint_get_param(j, PhysicsServer2D.JOINT_PARAM_BIAS)])
	_finish("joint_pin_params " + " ".join(out))

func _arm_joint_node_anchor() -> void:
	# lane A: node created at (0,100) while A sits at (0,0) -> which point anchors the pin?
	var a1 := _mk_static(Vector2(0, 0), Vector2(20, 20))
	var b1 := _mk_dyn(Vector2(200, 0), Vector2(20, 20), Vector2(0, 300))
	var p1 := PinJoint2D.new()
	p1.node_a = a1.get_path()
	p1.node_b = b1.get_path()
	p1.position = Vector2(0, 100)
	root.add_child(p1)
	_tracked_nodes.append(p1)
	# lane B: node created at (0,LANE) then moved to (0,LANE+100) before the first physics frame
	var a2 := _mk_static(Vector2(0, LANE), Vector2(20, 20))
	var b2 := _mk_dyn(Vector2(200, LANE), Vector2(20, 20), Vector2(0, 300))
	var p2 := PinJoint2D.new()
	p2.node_a = a2.get_path()
	p2.node_b = b2.get_path()
	p2.position = Vector2(0, LANE)
	root.add_child(p2)
	_tracked_nodes.append(p2)
	p2.global_position = Vector2(0, LANE + 100)
	var p2_pos := _fv(p2.global_position)
	await _frames(40)
	var a_d0: float = b1.global_position.length()
	var a_d100: float = (b1.global_position - Vector2(0, 100)).length()
	var b_d0: float = (b2.global_position - Vector2(0, LANE)).length()
	var b_d100: float = (b2.global_position - Vector2(0, LANE + 100)).length()
	await _frames(1)
	_finish("joint_node_anchor created_at_100[d0=%.4f d0b=%.4f d100=%.4f d100b=%.4f] moved_before_step[d0=%.4f d0b=%.4f d100=%.4f d100b=%.4f] p2_pos=%s" % [
		a_d0, b1.global_position.length(), a_d100, (b1.global_position - Vector2(0, 100)).length(),
		b_d0, (b2.global_position - Vector2(0, LANE)).length(),
		b_d100, (b2.global_position - Vector2(0, LANE + 100)).length(), p2_pos])

func _arm_joint_groove() -> void:
	# 3 static (zero-velocity) convention lanes + dynamic behaviour lanes.
	# All static anchor bodies sit 2000px away unless the lane says otherwise.
	# gst_node: node groove at (0,0), B at (50,50) zero velocity
	var a1 := _mk_static(Vector2(2000, 0), Vector2(20, 20))
	var b1 := _mk_dyn(Vector2(50, 50), Vector2(20, 20), Vector2.ZERO)
	var gr := GrooveJoint2D.new()
	gr.length = 100.0
	gr.initial_offset = 0.0
	gr.node_a = a1.get_path()
	gr.node_b = b1.get_path()
	gr.position = Vector2(0, 0)
	root.add_child(gr)
	_tracked_nodes.append(gr)
	# gst_srv_center: server, anchor_b = body center
	var a2 := _mk_static(Vector2(2000, LANE), Vector2(20, 20))
	var b2 := _mk_dyn(Vector2(50, LANE + 50), Vector2(20, 20), Vector2.ZERO)
	var j2: RID = _track(PhysicsServer2D.joint_create())
	PhysicsServer2D.joint_make_groove(j2, Vector2(0, LANE), Vector2(0, LANE + 100), Vector2(50, LANE + 50), a2.get_rid(), b2.get_rid())
	# gst_srv_jpos: server, anchor_b = the joint node's position
	var a3 := _mk_static(Vector2(2000, LANE * 2), Vector2(20, 20))
	var b3 := _mk_dyn(Vector2(50, LANE * 2 + 50), Vector2(20, 20), Vector2.ZERO)
	var j3: RID = _track(PhysicsServer2D.joint_create())
	PhysicsServer2D.joint_make_groove(j3, Vector2(0, LANE * 2), Vector2(0, LANE * 2 + 100), Vector2(0, LANE * 2), a3.get_rid(), b3.get_rid())
	# gnode: node groove, B moves down along +Y
	var a4 := _mk_static(Vector2(2000, LANE * 3), Vector2(20, 20))
	var b4 := _mk_dyn(Vector2(50, LANE * 3 + 50), Vector2(20, 20), Vector2(0, 60))
	var gr2 := GrooveJoint2D.new()
	gr2.length = 100.0
	gr2.initial_offset = 0.0
	gr2.node_a = a4.get_path()
	gr2.node_b = b4.get_path()
	gr2.position = Vector2(0, LANE * 3)
	root.add_child(gr2)
	_tracked_nodes.append(gr2)
	# gsrv_smallA / gsrv_smallB: two exact translates of the gnode geometry (x +300 / +600)
	var a5 := _mk_static(Vector2(2300, LANE * 4), Vector2(20, 20))
	var b5 := _mk_dyn(Vector2(350, LANE * 4 + 50), Vector2(20, 20), Vector2(0, 60))
	var j5: RID = _track(PhysicsServer2D.joint_create())
	PhysicsServer2D.joint_make_groove(j5, Vector2(300, LANE * 4), Vector2(300, LANE * 4 + 100), Vector2(300, LANE * 4), a5.get_rid(), b5.get_rid())
	var a6 := _mk_static(Vector2(2600, LANE * 5), Vector2(20, 20))
	var b6 := _mk_dyn(Vector2(650, LANE * 5 + 50), Vector2(20, 20), Vector2(0, 60))
	var j6: RID = _track(PhysicsServer2D.joint_create())
	PhysicsServer2D.joint_make_groove(j6, Vector2(600, LANE * 5), Vector2(600, LANE * 5 + 100), Vector2(600, LANE * 5), a6.get_rid(), b6.get_rid())
	# gend_far: body runs up past groove1, A far
	var a7 := _mk_static(Vector2(2000, LANE * 6), Vector2(20, 20))
	var b7 := _mk_dyn(Vector2(0, LANE * 6 + 50), Vector2(20, 20), Vector2(0, -240))
	var j7: RID = _track(PhysicsServer2D.joint_create())
	PhysicsServer2D.joint_make_groove(j7, Vector2(0, LANE * 6), Vector2(0, LANE * 6 + 100), Vector2(0, LANE * 6 + 50), a7.get_rid(), b7.get_rid())
	# gend_near: same but A sits at the groove start (static-dynamic collision confound)
	var a8 := _mk_static(Vector2(0, LANE * 7), Vector2(20, 20))
	var b8 := _mk_dyn(Vector2(0, LANE * 7 + 50), Vector2(20, 20), Vector2(0, -240))
	var j8: RID = _track(PhysicsServer2D.joint_create())
	PhysicsServer2D.joint_make_groove(j8, Vector2(0, LANE * 7), Vector2(0, LANE * 7 + 100), Vector2(0, LANE * 7 + 50), a8.get_rid(), b8.get_rid())
	await _frames(40)
	_finish("joint_groove gst_node=%s gst_srv_center=%s gst_srv_jpos=%s gnode=%s gsmallA=%s gsmallB=%s gend_far=%s gend_far_vel=%s gend_near=%s gend_near_vel=%s gnode_props=[l=%.1f,off=%.1f] gnode_type=%d j3_type=%d gnode_a_dis=%s gsrv_a_dis=%s" % [
		_v2(b1.global_position), _v2(b2.global_position - Vector2(0, LANE)),
		_v2(b3.global_position - Vector2(0, LANE * 2)), _v2(b4.global_position - Vector2(0, LANE * 3)),
		_v2(b5.global_position - Vector2(300, LANE * 4)), _v2(b6.global_position - Vector2(600, LANE * 5)),
		_v2(b7.global_position - Vector2(0, LANE * 6)), _v2(b7.linear_velocity),
		_v2(b8.global_position - Vector2(0, LANE * 7)), _v2(b8.linear_velocity),
		gr.length, gr.initial_offset, PhysicsServer2D.joint_get_type(gr.get_rid()),
		PhysicsServer2D.joint_get_type(j3),
		str(PhysicsServer2D.joint_is_disabled_collisions_between_bodies(gr.get_rid())),
		str(PhysicsServer2D.joint_is_disabled_collisions_between_bodies(j2))])

func _arm_joint_disable_coll() -> void:
	var out: Array = []
	var i := 0
	for mode in [true, false]:
		var y := float(i) * LANE
		i += 1
		var a := _mk_dyn_lm(Vector2(0, y), Vector2(20, 20), Vector2.ZERO, 1, 1, true)
		var b := _mk_dyn_lm(Vector2(10, y), Vector2(20, 20), Vector2.ZERO, 1, 1, true)
		var j: RID = _track(PhysicsServer2D.joint_create())
		PhysicsServer2D.joint_make_pin(j, Vector2(5, y), a.get_rid(), b.get_rid())
		PhysicsServer2D.joint_disable_collisions_between_bodies(j, mode)
		await _frames(30)
		var d := (b.global_position - a.global_position).length()
		out.append("dis_%s[acnt=%d bcnt=%d d=%.4f a_pos=%s b_pos=%s rb=%s]" % [
			str(mode), a.get_contact_count(), b.get_contact_count(), d,
			_v2(a.global_position - Vector2(0, y)), _v2(b.global_position - Vector2(0, y)),
			str(PhysicsServer2D.joint_is_disabled_collisions_between_bodies(j))])
	# lane 3: node groove joint between the same overlapping pair (default flag)
	var a3 := _mk_dyn(Vector2(0, LANE * 2), Vector2(20, 20), Vector2.ZERO)
	var b3 := _mk_dyn(Vector2(10, LANE * 2), Vector2(20, 20), Vector2.ZERO)
	var gr := GrooveJoint2D.new()
	gr.length = 100.0
	gr.initial_offset = 0.0
	gr.node_a = a3.get_path()
	gr.node_b = b3.get_path()
	gr.position = Vector2(5, LANE * 2)
	root.add_child(gr)
	_tracked_nodes.append(gr)
	var gr_rb: Array = [gr.disable_collision, gr.get_exclude_nodes_from_collision(),
		PhysicsServer2D.joint_is_disabled_collisions_between_bodies(gr.get_rid())]
	# lane 4: node pin joint, property vs getter inversion readback
	var a4 := _mk_dyn(Vector2(0, LANE * 3), Vector2(20, 20), Vector2.ZERO)
	var b4 := _mk_dyn(Vector2(10, LANE * 3), Vector2(20, 20), Vector2.ZERO)
	var pin := PinJoint2D.new()
	pin.node_a = a4.get_path()
	pin.node_b = b4.get_path()
	pin.position = Vector2(5, LANE * 3)
	root.add_child(pin)
	_tracked_nodes.append(pin)
	var r1: Array = [pin.disable_collision, pin.get_exclude_nodes_from_collision(),
		PhysicsServer2D.joint_is_disabled_collisions_between_bodies(pin.get_rid())]
	pin.disable_collision = false
	var r2: Array = [pin.disable_collision, pin.get_exclude_nodes_from_collision(),
		PhysicsServer2D.joint_is_disabled_collisions_between_bodies(pin.get_rid())]
	# lane 5/6: static A + dynamic B overlapping, pin joint, flag default vs explicit false
	var s1 := _mk_static(Vector2(0, LANE * 4), Vector2(20, 20))
	var d1 := _mk_dyn_lm(Vector2(10, LANE * 4), Vector2(20, 20), Vector2.ZERO, 1, 1, true)
	var js1: RID = _track(PhysicsServer2D.joint_create())
	PhysicsServer2D.joint_make_pin(js1, Vector2(5, LANE * 4), s1.get_rid(), d1.get_rid())
	var s2 := _mk_static(Vector2(0, LANE * 5), Vector2(20, 20))
	var d2 := _mk_dyn_lm(Vector2(10, LANE * 5), Vector2(20, 20), Vector2.ZERO, 1, 1, true)
	var js2: RID = _track(PhysicsServer2D.joint_create())
	PhysicsServer2D.joint_make_pin(js2, Vector2(5, LANE * 5), s2.get_rid(), d2.get_rid())
	PhysicsServer2D.joint_disable_collisions_between_bodies(js2, false)
	await _frames(30)
	out.append("groove_default[rb=%s acnt=%d bcnt=%d d=%.4f a_pos=%s b_pos=%s]" % [
		gr_rb, a3.get_contact_count(), b3.get_contact_count(),
		(b3.global_position - a3.global_position).length(),
		_v2(a3.global_position - Vector2(0, LANE * 2)), _v2(b3.global_position - Vector2(0, LANE * 2))])
	out.append("node_prop_default=%s node_prop_false=%s node_pos=[%s,%s]" % [
		r1, r2, _v2(a4.global_position - Vector2(0, LANE * 3)), _v2(b4.global_position - Vector2(0, LANE * 3))])
	out.append("static_default[rb=%s dcnt=%d d_pos=%s] static_enabled[rb=%s dcnt=%d d_pos=%s]" % [
		str(PhysicsServer2D.joint_is_disabled_collisions_between_bodies(js1)), d1.get_contact_count(),
		_v2(d1.global_position - Vector2(0, LANE * 4)),
		str(PhysicsServer2D.joint_is_disabled_collisions_between_bodies(js2)), d2.get_contact_count(),
		_v2(d2.global_position - Vector2(0, LANE * 5))])
	_finish("joint_disable_coll " + " ".join(out))

# ------------------------------------------------------------------ layers

func _run_wall_table(cells: Array, tag: String) -> void:
	var lanes: Array = []
	var i := 0
	for c in cells:
		var y := float(i) * LANE
		i += 1
		var wall := _mk_static_lm(Vector2(WALL_X, y), Vector2(4, 400), c[1], c[2])
		var t := Track.new()
		var b := _mk_dyn_lm(Vector2(0, y), Vector2(20, 20), Vector2(120, 0), c[3], c[4], true)
		b.body_entered.connect(func(_n: Node) -> void: t.ent.append(_frame_no))
		b.body_exited.connect(func(_n: Node) -> void: t.ext.append(_frame_no))
		lanes.append({"tag": c[0], "wl": c[1], "wm": c[2], "bl": c[3], "bm": c[4], "w": wall, "b": b, "t": t})
	await _frames(60)
	var out: Array = []
	for L in lanes:
		var b: RigidBody2D = L["b"]
		var w: StaticBody2D = L["w"]
		var t: Track = L["t"]
		var x: float = b.global_position.x
		out.append("%s[wl=%d wm=%d bl=%d bm=%d]ent=%s ext=%s x=%.4f cross=%d cnt=%d" % [
			L["tag"], w.collision_layer, w.collision_mask, b.collision_layer, b.collision_mask,
			(t.ent[0] if t.ent.size() > 0 else -1), (t.ext[0] if t.ext.size() > 0 else -1),
			x, (1 if x > 110.0 else 0), b.get_contact_count()])
	_finish(tag + " " + " ".join(out))

func _arm_layer_or_table() -> void:
	await _run_wall_table([
		["ctl_both", 1, 2, 2, 1],
		["body_only", 1, 0, 2, 1],
		["wall_only", 1, 2, 2, 0],
		["neither", 1, 0, 2, 0],
	], "layer_or_table")

func _arm_layer_zero_table() -> void:
	await _run_wall_table([
		["z_body_l0", 1, 1, 0, 1],
		["z_body_m0", 1, 1, 1, 0],
		["z_wall_l0m0", 0, 0, 1, 1],
		["z_wall_l0m1", 0, 1, 1, 1],
	], "layer_zero_table")

func _arm_layer_dyn_pair() -> void:
	# A left moving +x, B right moving -x, both dynamic, lock_rotation
	var cells := [
		["a_scans_only", 1, 2, 2, 0],
		["b_scans_only", 1, 0, 2, 1],
		["both_scan", 1, 2, 2, 1],
		["neither", 1, 0, 2, 0],
	]
	var lanes: Array = []
	var i := 0
	for c in cells:
		var y := float(i) * LANE
		i += 1
		var ta := Track.new()
		var tb := Track.new()
		var a := _mk_dyn_lm(Vector2(0, y), Vector2(20, 20), Vector2(120, 0), c[1], c[2], true, true)
		var b := _mk_dyn_lm(Vector2(60, y), Vector2(20, 20), Vector2(-120, 0), c[3], c[4], true, true)
		a.body_entered.connect(func(_n: Node) -> void: ta.ent.append(_frame_no))
		b.body_entered.connect(func(_n: Node) -> void: tb.ent.append(_frame_no))
		lanes.append({"tag": c[0], "a": a, "b": b, "ta": ta, "tb": tb})
	await _frames(40)
	var out: Array = []
	for L in lanes:
		var a: RigidBody2D = L["a"]
		var b: RigidBody2D = L["b"]
		var ta: Track = L["ta"]
		var tb: Track = L["tb"]
		out.append("%s[va=%s vb=%s xa=%.2f xb=%.2f crossed=%d acnt=%d bcnt=%d ent_a=%s ent_b=%s]" % [
			L["tag"], _fv(a.linear_velocity), _fv(b.linear_velocity),
			a.global_position.x, b.global_position.x, (1 if b.global_position.x < a.global_position.x else 0),
			a.get_contact_count(), b.get_contact_count(),
			(ta.ent[0] if ta.ent.size() > 0 else -1), (tb.ent[0] if tb.ent.size() > 0 else -1)])
	_finish("layer_dyn_pair " + " ".join(out))

func _arm_layer_flip_mid() -> void:
	# tag, wall_l, wall_m, body_l, body_m, flip_frame, kind
	var specs := [
		["body_mask_off", 1, 2, 2, 1, 40, "body_mask0"],
		["wall_layer_off", 1, 2, 2, 1, 40, "wall_layer0"],
		["mask_off_move", 1, 2, 2, 1, 40, "body_mask0_vel"],
		["body_mask_on", 1, 2, 2, 0, 10, "body_mask1"],
		["wall_layer_on", 0, 2, 2, 1, 10, "wall_layer1"],
	]
	var lanes: Array = []
	var i := 0
	for s in specs:
		var y := float(i) * LANE
		i += 1
		var wall := _mk_static_lm(Vector2(WALL_X, y), Vector2(4, 400), s[1], s[2])
		var t := Track.new()
		var b := _mk_dyn_lm(Vector2(0, y), Vector2(20, 20), Vector2(240, 0), s[3], s[4], true)
		b.body_entered.connect(func(_n: Node) -> void: t.ent.append(_frame_no))
		b.body_exited.connect(func(_n: Node) -> void: t.ext.append(_frame_no))
		lanes.append({"tag": s[0], "wall": wall, "b": b, "t": t, "flip_f": s[5], "kind": s[6]})
	var total := 80
	for f in range(1, total + 1):
		await physics_frame
		_frame_no += 1
		for L in lanes:
			var b: RigidBody2D = L["b"]
			var wall: StaticBody2D = L["wall"]
			var t: Track = L["t"]
			if _frame_no == int(L["flip_f"]):
				t.cnt["at"] = b.get_contact_count()
				t.cnt["x_at"] = snappedf(b.global_position.x, 0.0001)
				t.cnt["m_pre"] = b.collision_mask
				t.cnt["wl_pre"] = wall.collision_layer
				match String(L["kind"]):
					"body_mask0":
						b.collision_mask = 0
					"wall_layer0":
						wall.collision_layer = 0
					"body_mask0_vel":
						b.collision_mask = 0
						b.linear_velocity = Vector2(240, 0)
					"body_mask1":
						b.collision_mask = 1
					"wall_layer1":
						wall.collision_layer = 1
			if _frame_no == int(L["flip_f"]) + 1:
				t.cnt["n1"] = b.get_contact_count()
			if _frame_no == int(L["flip_f"]) + 2:
				t.cnt["n2"] = b.get_contact_count()
	var out: Array = []
	for L in lanes:
		var b: RigidBody2D = L["b"]
		var t: Track = L["t"]
		out.append("%s flip_f=%d x_at=%.4f m_pre=%s wl_pre=%s cnt=[%s,%s,%s] ent=%s ext=%s x_end=%.4f vx_end=%.2f mask=%d wl=%d" % [
			L["tag"], L["flip_f"], t.cnt.get("x_at", -1.0), t.cnt.get("m_pre", -1), t.cnt.get("wl_pre", -1),
			t.cnt.get("at", -1), t.cnt.get("n1", -1), t.cnt.get("n2", -1),
			(t.ent[0] if t.ent.size() > 0 else -1), (t.ext[0] if t.ext.size() > 0 else -1),
			b.global_position.x, b.linear_velocity.x, b.collision_mask, (L["wall"] as StaticBody2D).collision_layer])
	_finish("layer_flip_mid " + " | ".join(out))

func _arm_layer_flip_cb() -> void:
	var lanes: Array = []
	var i := 0
	for kind in ["direct", "deferred"]:
		var y := float(i) * LANE
		i += 1
		_mk_static_lm(Vector2(WALL_X, y), Vector2(4, 400), 1, 2)
		var t := Track.new()
		var b := _mk_dyn_lm(Vector2(0, y), Vector2(20, 20), Vector2(240, 0), 2, 1, true)
		var k: String = kind
		b.body_entered.connect(func(_n: Node) -> void:
			t.ent.append(_frame_no)
			t.cnt["cb"] = b.get_contact_count()
			if k == "direct":
				b.collision_mask = 0
			else:
				b.set_deferred("collision_mask", 0)
			t.cnt["after_write"] = b.collision_mask)
		b.body_exited.connect(func(_n: Node) -> void: t.ext.append(_frame_no))
		lanes.append({"tag": k, "b": b, "t": t})
	await _frames(80)
	var out: Array = []
	for L in lanes:
		var b: RigidBody2D = L["b"]
		var t: Track = L["t"]
		out.append("%s ent=%s ext=%s cb_cnt=%s after_write=%s x_end=%.4f mask=%d" % [
			L["tag"], (t.ent[0] if t.ent.size() > 0 else -1), (t.ext[0] if t.ext.size() > 0 else -1),
			t.cnt.get("cb", -1), t.cnt.get("after_write", -1), b.global_position.x, b.collision_mask])
	_finish("layer_flip_cb " + " | ".join(out))

# ------------------------------------------------------------------ areas

func _arm_area_lattice() -> void:
	# tag, a_mon, a_mable, a_l, a_m, b_mon, b_mable, b_l, b_m
	var specs := [
		["mon_a_only", true, false, 1, 1, false, true, 1, 1],
		["mon_b_only", true, true, 1, 1, true, false, 1, 1],
		["neither_mon", false, true, 1, 1, false, true, 1, 1],
		["neither_mable", true, false, 1, 1, true, false, 1, 1],
		["both_mutual", true, true, 1, 2, true, true, 2, 1],
		["layer_off", true, true, 1, 0, true, true, 2, 0],
		["a_scans_b", true, true, 1, 2, true, true, 2, 0],
		["b_scans_a", true, true, 1, 0, true, true, 2, 1],
	]
	var lanes: Array = []
	var i := 0
	for s in specs:
		var y := float(i) * LANE
		i += 1
		var ta := Track.new()
		var tb := Track.new()
		var a := _mk_area(Vector2(0, y), Vector2(40, 40), s[1], s[2], s[3], s[4])
		var b := _mk_area(Vector2(0, y), Vector2(40, 40), s[5], s[6], s[7], s[8])
		a.area_entered.connect(func(_n: Area2D) -> void: ta.ent.append(_frame_no))
		b.area_entered.connect(func(_n: Area2D) -> void: tb.ent.append(_frame_no))
		lanes.append({"tag": s[0], "a": a, "b": b, "ta": ta, "tb": tb})
	await _frames(5)
	var out: Array = []
	for L in lanes:
		var a: Area2D = L["a"]
		var b: Area2D = L["b"]
		var ta: Track = L["ta"]
		var tb: Track = L["tb"]
		out.append("%s[am=%s amab=%s bm=%s bmab=%s a_ent=%d b_ent=%d]" % [
			L["tag"], str(a.monitoring), str(a.monitorable), str(b.monitoring), str(b.monitorable),
			ta.ent.size(), tb.ent.size()])
	_finish("area_lattice " + " ".join(out))

func _arm_area_body_gate() -> void:
	# area mask decides whether the area sees the body; the body's own mask is irrelevant
	# tag, area_l, area_m, body_l, body_m
	var specs := [
		["area_scans", 1, 2, 2, 0],
		["area_blind", 1, 1, 2, 0],
		["area_scans_bmask", 1, 2, 2, 1],
		["area_blind_bmask", 1, 1, 2, 1],
	]
	var lanes: Array = []
	var i := 0
	for s in specs:
		var y := float(i) * LANE
		i += 1
		var t := Track.new()
		var ar := _mk_area(Vector2(0, y), Vector2(40, 40), true, true, s[1], s[2])
		var b := _mk_dyn_lm(Vector2(0, y), Vector2(20, 20), Vector2.ZERO, s[3], s[4], true)
		ar.body_entered.connect(func(_n: Node) -> void: t.ent.append(_frame_no))
		lanes.append({"tag": s[0], "ar": ar, "b": b, "t": t})
	await _frames(5)
	var out: Array = []
	for L in lanes:
		var ar: Area2D = L["ar"]
		var b: RigidBody2D = L["b"]
		var t: Track = L["t"]
		out.append("%s[am=%s al=%d amask=%d bl=%d bm=%d ent=%s]" % [
			L["tag"], str(ar.monitoring), ar.collision_layer, ar.collision_mask,
			b.collision_layer, b.collision_mask,
			(t.ent[0] if t.ent.size() > 0 else -1)])
	_finish("area_body_gate " + " ".join(out))

func _arm_area_entry_order() -> void:
	# lane 1: areas created before the body; lane 2: body created before the areas
	var t1 := Track.new()
	var created1: Array = []
	var outer1 := _mk_area(Vector2(0, 0), Vector2(200, 200), true, true, 1, 3)
	created1.append("o")
	var inner1 := _mk_area(Vector2(0, 0), Vector2(40, 40), true, true, 1, 3)
	created1.append("i")
	_mk_dyn_lm(Vector2(0, 0), Vector2(20, 20), Vector2.ZERO, 2, 1, false)
	created1.append("b")
	outer1.body_entered.connect(func(_n: Node) -> void: t1.seq.append("ob@%d" % _frame_no))
	inner1.body_entered.connect(func(_n: Node) -> void: t1.seq.append("ib@%d" % _frame_no))
	outer1.area_entered.connect(func(_n: Area2D) -> void: t1.seq.append("oa@%d" % _frame_no))
	inner1.area_entered.connect(func(_n: Area2D) -> void: t1.seq.append("ia@%d" % _frame_no))
	var t2 := Track.new()
	var created2: Array = []
	_mk_dyn_lm(Vector2(0, LANE), Vector2(20, 20), Vector2.ZERO, 2, 1, false)
	created2.append("b")
	var outer2 := _mk_area(Vector2(0, LANE), Vector2(200, 200), true, true, 1, 3)
	created2.append("o")
	var inner2 := _mk_area(Vector2(0, LANE), Vector2(40, 40), true, true, 1, 3)
	created2.append("i")
	outer2.body_entered.connect(func(_n: Node) -> void: t2.seq.append("ob@%d" % _frame_no))
	inner2.body_entered.connect(func(_n: Node) -> void: t2.seq.append("ib@%d" % _frame_no))
	outer2.area_entered.connect(func(_n: Area2D) -> void: t2.seq.append("oa@%d" % _frame_no))
	inner2.area_entered.connect(func(_n: Area2D) -> void: t2.seq.append("ia@%d" % _frame_no))
	await _frames(3)
	_finish("area_entry_order created1=%s areas_first=%s created2=%s body_first=%s" % [created1, t1.seq, created2, t2.seq])
