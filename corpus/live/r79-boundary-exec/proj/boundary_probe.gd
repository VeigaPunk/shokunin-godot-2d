extends SceneTree
# r79 boundary-exec scratch probe — LIVE falsification arms for the §1.4 pins.
# Scratch only (corpus/live/r79-boundary-exec/). Control arms stay in the
# byte-identical scout scratch probe (proj/phys2d_events.gd, sha 7329acb2…);
# this file holds ONLY falsification arms and never edits the tracked fixture.
#
# Launch shape (the battery's own):
#   godot --headless --path <scratch> --script res://boundary_probe.gd -- --arm=<name>
# Emits `XPROBE <arm> | k=v ...` lines; measurement-only (no production pin).

const FLOOR_A_Y := 20.0
const FLOOR_B_Y := 220.0
const FALLER_Y := -4.0

class Hook extends Node2D:
	var cb: Callable
	var fired := false

	func _physics_process(_delta: float) -> void:
		if fired:
			return
		fired = true
		cb.call()

class Sampler extends Node2D:
	var getter: Callable
	var samples: Array = []
	var max_frames := 10
	var n := 0

	func _physics_process(_delta: float) -> void:
		if n >= max_frames:
			return
		samples.append(getter.call(n))
		n += 1

var arm := ""
var _faller: RigidBody2D
var _floor_a: StaticBody2D
var _floor_a2: StaticBody2D
var _entries: Array = []
var _entry_frames: Array = []
var _exits: Array = []
var _exit_frames: Array = []
var _x: Dictionary = {}
var _frame_no := 0
var _raw_rids: Array = []
var _foreign_space := RID()
var _foreign_shape := RID()
var _swap_shape: Shape2D
var _cb1_done := false

func _track(rid: RID) -> RID:
	_raw_rids.append(rid)
	return rid

func _free_tracked() -> void:
	for i in range(_raw_rids.size() - 1, -1, -1):
		PhysicsServer2D.free_rid(_raw_rids[i])
	_raw_rids.clear()

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")

func _run() -> void:
	print("R79X arm=%s godot=%s engine2d=%s" % [
		arm, Engine.get_version_info().string,
		ProjectSettings.get_setting("physics/2d/physics_engine")])
	match arm:
		"xcm_two_floors":
			await _arm_x_cm_two_floors()
		"xcm_swap_shrink", "xcm_swap_grow", "xcm_swap_noop":
			await _arm_x_cm_swap(arm)
		"xcm_floor_move":
			await _arm_x_cm_floor_move()
		"xrb_deferred_one", "xrb_deferred_two", "xrb_immediate_one", "xrb_immediate_two":
			await _arm_x_rb_deferred(arm)
		"xrb_free_immediate":
			await _arm_x_rb_free_immediate()
		"xrb_immediate_scout", "xrb_immediate_nosamp", "xrb_immediate_postread", "xrb_immediate_sampler", "xrb_immediate_ordertest", "xrb_immediate_nocolliders", "xrb_immediate_noderead", "xrb_immediate_readonly", "xrb_immediate_posread":
			await _arm_x_rb_scout_replica(arm)
		"xrb_dss_foreign":
			await _arm_x_rb_dss_foreign()
		_:
			print("XPROBE %s | error=unknown_arm" % arm)
			quit(1)

func _finish() -> void:
	print("XPROBE %s | %s" % [arm, _line()])
	print("XPROBE_DONE %s" % arm)
	_free_tracked()
	quit(0)

func _line() -> String:
	var parts: Array = []
	for k in _x.keys():
		parts.append("%s=%s" % [k, _x[k]])
	return " ".join(parts)

func _frames(n: int) -> void:
	for i in n:
		await physics_frame
		_frame_no += 1

func _wait_for(cond: Callable, max_frames: int) -> int:
	for i in max_frames:
		if cond.call():
			return i
		await physics_frame
		_frame_no += 1
	return -1

func _mk_static(pos: Vector2, size: Vector2, nm: String) -> StaticBody2D:
	var b := StaticBody2D.new()
	b.name = nm
	var cs := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = size
	cs.shape = rs
	b.add_child(cs)
	b.position = pos
	root.add_child(b)
	return b

func _mk_faller(pos: Vector2, monitor: bool, max_contacts: int) -> RigidBody2D:
	var b := RigidBody2D.new()
	b.name = "Faller"
	var cs := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = Vector2(10, 10)
	cs.shape = rs
	b.add_child(cs)
	b.position = pos
	b.gravity_scale = 4.0
	root.add_child(b)
	b.contact_monitor = monitor
	b.max_contacts_reported = max_contacts
	return b

func _srv_origin(rid: RID) -> Variant:
	var t: Variant = PhysicsServer2D.body_get_state(rid, PhysicsServer2D.BODY_STATE_TRANSFORM)
	if t == null:
		return "<null>"
	return (t as Transform2D).origin

func _q_count(at: Vector2, areas: bool) -> int:
	var dss: Variant = PhysicsServer2D.space_get_direct_state(root.world_2d.space)
	if dss == null:
		return -1
	var q := PhysicsPointQueryParameters2D.new()
	q.position = at
	q.collide_with_bodies = not areas
	q.collide_with_areas = areas
	return (dss as PhysicsDirectSpaceState2D).intersect_point(q).size()

# ------------------------------------------------- probe 1: cb_count/cb_colliders
func _x_entered(other: Node) -> void:
	_entries.append(String(other.name))
	_entry_frames.append(_frame_no)
	if not _cb1_done:
		_cb1_done = true
		_x["cb1_cls"] = other.get_class()
		_x["cb1_count"] = _faller.get_contact_count()
		_x["cb1_colliders"] = _faller.get_colliding_bodies().size()
		match arm:
			"xcm_swap_shrink", "xcm_swap_grow", "xcm_swap_noop":
				var cs := _faller.get_child(0) as CollisionShape2D
				cs.shape = _swap_shape
				_x["swap_size"] = "%s" % (_swap_shape as RectangleShape2D).size
				_x["post_swap_count"] = _faller.get_contact_count()
				_x["post_swap_colliders"] = _faller.get_colliding_bodies().size()
			"xcm_floor_move":
				_floor_a.position = Vector2(10000, 10000)
				_x["floor_moved_in_cb"] = true
	_x["count_%d" % _entries.size()] = _faller.get_contact_count()
	_x["colliders_%d" % _entries.size()] = _faller.get_colliding_bodies().size()

func _x_exited(_other: Node) -> void:
	_exits.append(String(_other.name))
	_exit_frames.append(_frame_no)

func _x_cm_setup(second_floor: bool, swap: Shape2D) -> void:
	_swap_shape = swap
	_floor_a = _mk_static(Vector2(0, FLOOR_A_Y), Vector2(400, 40), "FloorA")
	if second_floor:
		_floor_a2 = _mk_static(Vector2(0, FLOOR_A_Y), Vector2(400, 40), "FloorA2")
	_mk_static(Vector2(0, FLOOR_B_Y), Vector2(400, 40), "FloorB")
	_faller = _mk_faller(Vector2(0, FALLER_Y), true, 4)
	_faller.body_entered.connect(_x_entered)
	_faller.body_exited.connect(_x_exited)

func _x_cm_report() -> void:
	_x["entered"] = _entries.size()
	_x["exited"] = _exits.size()
	_x["entry_frames"] = ",".join(_entry_frames)
	_x["entry_names"] = ",".join(_entries)
	_x["exit_frames"] = ",".join(_exit_frames)
	_x["valid"] = is_instance_valid(_faller)
	_x["exit1_frame"] = _exit_frames[0] if _exit_frames.size() > 0 else -1
	_finish()

func _arm_x_cm_two_floors() -> void:
	_x_cm_setup(true, null)
	var entry1 := await _wait_for(func() -> bool: return _entries.size() >= 1, 20)
	_x["entry1_wait"] = entry1
	await _frames(6)
	_floor_a.position = Vector2(10000, 10000)
	var entry2 := await _wait_for(func() -> bool: return _entries.size() >= 2, 45)
	_x["entry2_wait"] = entry2
	await _frames(2)
	_x_cm_report()

func _arm_x_cm_swap(kind: String) -> void:
	var sz := Vector2(2, 2) if kind == "xcm_swap_shrink" else (Vector2(10, 10) if kind == "xcm_swap_noop" else Vector2(20, 20))
	var swap := RectangleShape2D.new()
	swap.size = sz
	_x_cm_setup(false, swap)
	var entry1 := await _wait_for(func() -> bool: return _entries.size() >= 1, 20)
	_x["entry1_wait"] = entry1
	await _frames(6)
	_floor_a.position = Vector2(10000, 10000)
	var entry2 := await _wait_for(func() -> bool: return _entries.size() >= 2, 45)
	_x["entry2_wait"] = entry2
	await _frames(2)
	_x_cm_report()

func _arm_x_cm_floor_move() -> void:
	_x_cm_setup(false, null)
	var entry1 := await _wait_for(func() -> bool: return _entries.size() >= 1, 20)
	_x["entry1_wait"] = entry1
	var exit1 := await _wait_for(func() -> bool: return _exits.size() >= 1, 20)
	_x["exit1_wait"] = exit1
	await _frames(6)
	_floor_a.position = Vector2(10000, 10000)
	var entry2 := await _wait_for(func() -> bool: return _entries.size() >= 2, 45)
	_x["entry2_wait"] = entry2
	await _frames(2)
	_x_cm_report()

# ------------------------------------------------- probe 2: deferred-write reorder
func _x_rb_entered(other: Node) -> void:
	_entries.append(String(other.name))
	_entry_frames.append(_frame_no)
	var idx := _entries.size()
	_x["cb%d_frame" % idx] = _frame_no
	_x["cb%d_cls" % idx] = other.get_class()
	_x["cb%d_node" % idx] = _faller.global_position
	_x["cb%d_srv" % idx] = _srv_origin(_faller.get_rid())
	_x["cb%d_count" % idx] = _faller.get_contact_count()
	if idx == 1:
		if arm in ["xrb_immediate_one", "xrb_immediate_two"]:
			_faller.global_position = Vector2(600, 600)
		else:
			_faller.call_deferred("set_global_position", Vector2(600, 600))
		_x["cb1_node_after_call"] = _faller.global_position
		_x["cb1_srv_after_call"] = _srv_origin(_faller.get_rid())

func _x_rb_sample(n: int) -> String:
	var node_v: Variant = "<dead>"
	var srv_v: Variant = "<null>"
	if is_instance_valid(_faller):
		node_v = _faller.global_position
		srv_v = _srv_origin(_faller.get_rid())
	return "f%d node=%s srv=%s" % [n, node_v, srv_v]

func _arm_x_rb_deferred(kind: String) -> void:
	_floor_a = _mk_static(Vector2(0, FLOOR_A_Y), Vector2(400, 40), "FloorA")
	if kind in ["xrb_deferred_two", "xrb_immediate_two"]:
		_floor_a2 = _mk_static(Vector2(0, FLOOR_A_Y), Vector2(400, 40), "FloorA2")
	_faller = _mk_faller(Vector2(0, FALLER_Y), true, 4)
	_faller.body_entered.connect(_x_rb_entered)
	var sampler := Sampler.new()
	sampler.getter = _x_rb_sample
	sampler.max_frames = 8
	root.add_child(sampler)
	var entry1 := await _wait_for(func() -> bool: return _cb1_done, 20)
	_x["entry1_wait"] = entry1
	await _frames(6)
	_x["entered"] = _entries.size()
	_x["entry_frames"] = ",".join(_entry_frames)
	_x["entry_names"] = ",".join(_entries)
	_x["samples"] = " ; ".join(sampler.samples)
	_x["valid_after"] = is_instance_valid(_faller)
	if is_instance_valid(_faller):
		_x["late_node"] = _faller.global_position
		_x["late_srv"] = _srv_origin(_faller.get_rid())
	_finish()

# ------------------------------------------------- probe 2 attribution: scout replica
# `xrb_immediate_scout` replicates the scout's rb_node_position arm exactly
# (same callback order: count/colliders/srv_before, then the immediate write,
# then node_read; same read schedule: 1 frame -> next, 4 frames -> late; no
# sampler). `xrb_immediate_nosamp` is the same but prints the XPROBE keys.
func _x_scout_entered(other: Node) -> void:
	_entries.append(String(other.name))
	if _cb1_done:
		return
	_cb1_done = true
	if arm == "xrb_immediate_ordertest":
		# the sticking callback body verbatim (_x_rb_entered), on the replica's
		# read schedule: node read -> srv read -> contact count -> write -> reads
		_x["cb1_cls"] = other.get_class()
		_x["cb1_node"] = _faller.global_position
		_x["cb1_srv"] = _srv_origin(_faller.get_rid())
		_x["cb1_count"] = _faller.get_contact_count()
		_faller.global_position = Vector2(600, 600)
		_x["cb1_node_after_call"] = _faller.global_position
		_x["cb1_srv_after_call"] = _srv_origin(_faller.get_rid())
		return
	if arm == "xrb_immediate_nocolliders":
		# replica minus the get_colliding_bodies() call
		_x["count_1"] = _faller.get_contact_count()
		_x["srv_before"] = _srv_origin(_faller.get_rid())
		_faller.global_position = Vector2(600, 600)
		_x["node_read"] = _faller.global_position
		return
	if arm == "xrb_immediate_readonly":
		# noderead + a BARE pre-write node read (result not stored)
		_x["cb1_cls"] = other.get_class()
		var _junk: Vector2 = _faller.global_position
		_x["cb1_srv"] = _srv_origin(_faller.get_rid())
		_x["cb1_count"] = _faller.get_contact_count()
		_faller.global_position = Vector2(600, 600)
		_x["cb1_node_after_call"] = _faller.global_position
		_x["cb1_srv_after_call"] = _srv_origin(_faller.get_rid())
		return
	if arm == "xrb_immediate_posread":
		# bare pre-write read of the LOCAL transform instead of global_position
		_x["cb1_cls"] = other.get_class()
		var _junk2: Vector2 = _faller.position
		_x["cb1_srv"] = _srv_origin(_faller.get_rid())
		_x["cb1_count"] = _faller.get_contact_count()
		_faller.global_position = Vector2(600, 600)
		_x["cb1_node_after_call"] = _faller.global_position
		_x["cb1_srv_after_call"] = _srv_origin(_faller.get_rid())
		return
	if arm == "xrb_immediate_noderead":
		# ordertest minus the pre-write node read
		_x["cb1_cls"] = other.get_class()
		_x["cb1_srv"] = _srv_origin(_faller.get_rid())
		_x["cb1_count"] = _faller.get_contact_count()
		_faller.global_position = Vector2(600, 600)
		_x["cb1_node_after_call"] = _faller.global_position
		_x["cb1_srv_after_call"] = _srv_origin(_faller.get_rid())
		return
	_x["count_1"] = _faller.get_contact_count()
	_x["colliders_1"] = _faller.get_colliding_bodies().size()
	_x["srv_before"] = _srv_origin(_faller.get_rid())
	_faller.global_position = Vector2(600, 600)
	_x["node_read"] = _faller.global_position
	if arm == "xrb_immediate_postread":
		_x["srv_after_write"] = _srv_origin(_faller.get_rid())

func _arm_x_rb_scout_replica(kind: String) -> void:
	_floor_a = _mk_static(Vector2(0, FLOOR_A_Y), Vector2(400, 40), "FloorA")
	_faller = _mk_faller(Vector2(0, FALLER_Y), true, 4)
	_faller.body_entered.connect(_x_scout_entered)
	if kind == "xrb_immediate_sampler":
		var sampler := Sampler.new()
		sampler.getter = _x_rb_sample
		sampler.max_frames = 8
		root.add_child(sampler)
	var entry1 := await _wait_for(func() -> bool: return _cb1_done, 20)
	await _frames(1)
	var next_node: Variant = "<dead>"
	var next_srv: Variant = "<dead>"
	if is_instance_valid(_faller):
		next_node = _faller.global_position
		next_srv = _srv_origin(_faller.get_rid())
	await _frames(4)
	var late_node: Variant = "<dead>"
	if is_instance_valid(_faller):
		late_node = _faller.global_position
	var stuck := false
	if is_instance_valid(_faller) and kind == "xrb_immediate_scout":
		var p := _faller.global_position
		stuck = absf(p.x - 600.0) < 0.01 and absf(p.y - 600.0) < 0.01
	_x["entry1_frame"] = entry1
	_x["next_node"] = next_node
	_x["next_srv"] = next_srv
	_x["late_node"] = late_node
	_x["node_write_stuck"] = stuck
	_x["valid_after"] = is_instance_valid(_faller)
	_finish()

# ------------------------------------------------- probe 3: immediate free() in-cb
func _x_free_entered(other: Node) -> void:
	_entries.append(String(other.name))
	_entry_frames.append(_frame_no)
	if not _cb1_done:
		_cb1_done = true
		_x["cb1_frame"] = _frame_no
		_x["cb1_cls"] = other.get_class()
		_x["cb1_node"] = _faller.global_position
		_x["pre_free_valid"] = is_instance_valid(_faller)
		_faller.free()
		_x["post_free_valid"] = is_instance_valid(_faller)

func _arm_x_rb_free_immediate() -> void:
	_floor_a = _mk_static(Vector2(0, FLOOR_A_Y), Vector2(400, 40), "FloorA")
	_faller = _mk_faller(Vector2(0, FALLER_Y), true, 4)
	_faller.body_entered.connect(_x_free_entered)
	var entry1 := await _wait_for(func() -> bool: return _cb1_done, 20)
	_x["entry1_wait"] = entry1
	_x["entered"] = _entries.size()
	_x["valid_after"] = is_instance_valid(_faller)
	await _frames(3)
	_x["valid_late"] = is_instance_valid(_faller)
	_x["late_node"] = _faller.global_position if is_instance_valid(_faller) else "<dead>"
	_finish()

# ------------------------------------------------- probe 4: foreign-space DSS bypass
func _arm_x_rb_dss_foreign() -> void:
	# a second, unlocked PhysicsServer2D space with one static body (server API)
	_foreign_space = _track(PhysicsServer2D.space_create())
	_foreign_shape = _track(PhysicsServer2D.rectangle_shape_create())
	PhysicsServer2D.shape_set_data(_foreign_shape, Vector2(20, 20))
	var fbody := _track(PhysicsServer2D.body_create())
	PhysicsServer2D.body_set_mode(fbody, PhysicsServer2D.BODY_MODE_STATIC)
	PhysicsServer2D.body_add_shape(fbody, _foreign_shape)
	PhysicsServer2D.body_set_space(fbody, _foreign_space)
	PhysicsServer2D.body_set_state(fbody, PhysicsServer2D.BODY_STATE_TRANSFORM,
		Transform2D(0, Vector2(0, 50)))
	_floor_a = _mk_static(Vector2(0, FLOOR_A_Y), Vector2(400, 40), "FloorA")
	_faller = _mk_faller(Vector2(0, FALLER_Y), true, 4)
	_faller.body_entered.connect(_x_dss_entered)
	await _frames(2)
	# exterior control: the same foreign query outside any callback
	var pre := _foreign_query()
	_x["pre_foreign_null"] = pre["null"]
	_x["pre_foreign_pt_hits"] = pre["pt_hits"]
	_x["pre_foreign_shape_hits"] = pre["shape_hits"]
	_x["pre_self_hits"] = _q_count(Vector2(0, FLOOR_A_Y), false)
	var entry1 := await _wait_for(func() -> bool: return _cb1_done, 20)
	_x["entry1_wait"] = entry1
	await _frames(2)
	_x["valid_after"] = is_instance_valid(_faller)
	_finish()

func _foreign_query() -> Dictionary:
	var out := {"null": true, "pt_hits": -1, "shape_hits": -1}
	var dss: Variant = PhysicsServer2D.space_get_direct_state(_foreign_space)
	if dss == null:
		return out
	out["null"] = false
	var d := dss as PhysicsDirectSpaceState2D
	var q := PhysicsPointQueryParameters2D.new()
	q.position = Vector2(0, 50)
	q.collide_with_bodies = true
	q.collide_with_areas = false
	out["pt_hits"] = d.intersect_point(q).size()
	var p := PhysicsShapeQueryParameters2D.new()
	var qs := RectangleShape2D.new()
	qs.size = Vector2(20, 20)
	p.shape = qs
	p.transform = Transform2D(0, Vector2(0, 50))
	p.collide_with_bodies = true
	p.collide_with_areas = false
	out["shape_hits"] = d.intersect_shape(p, 8).size()
	return out

func _x_dss_entered(other: Node) -> void:
	_entries.append(String(other.name))
	if _cb1_done:
		return
	_cb1_done = true
	_x["cb1_frame"] = _frame_no
	_x["cb1_cls"] = other.get_class()
	var self_dss: Variant = PhysicsServer2D.space_get_direct_state(root.world_2d.space)
	_x["self_null"] = self_dss == null
	_x["self_hits"] = _q_count(Vector2(0, FLOOR_A_Y), false)
	if self_dss != null:
		var sp := PhysicsShapeQueryParameters2D.new()
		var ss := RectangleShape2D.new()
		ss.size = Vector2(20, 20)
		sp.shape = ss
		sp.transform = Transform2D(0, Vector2(0, FLOOR_A_Y))
		sp.collide_with_bodies = true
		sp.collide_with_areas = false
		_x["self_shape_hits"] = (self_dss as PhysicsDirectSpaceState2D).intersect_shape(sp, 8).size()
	var f := _foreign_query()
	_x["foreign_null"] = f["null"]
	_x["foreign_pt_hits"] = f["pt_hits"]
	_x["foreign_shape_hits"] = f["shape_hits"]
	# second call in the same callback: the foreign query must be repeatable
	var f2 := _foreign_query()
	_x["foreign_shape_hits2"] = f2["shape_hits"]
