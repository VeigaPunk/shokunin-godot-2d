extends SceneTree
# r80 fixture — RigidBody2D CCD + 2D motion-query family (read-only).
# One arm per process, exactly the battery's launch shape:
#   godot --headless --path <scratch> --script res://phys2d_motion.gd -- --arm=<name>
# Prints R80 diagnostic lines and one final `PASS phys2d_motion <arm> ...` line.
# No object ids / addresses / RIDs are printed (byte-stability).
# The `match arm:` dispatch in _run is the sole arm index (28 arms);
# per-arm measured classes live in r80-scout §1.1-1.3.

const WALL_X := 100.0
const WALL_HALF := 2.0
const BULLET_R := 8.0
const CCD := {"d": RigidBody2D.CCD_MODE_DISABLED,
	"r": RigidBody2D.CCD_MODE_CAST_RAY,
	"s": RigidBody2D.CCD_MODE_CAST_SHAPE}

var arm := ""
var _frame_no := 0

# contact-monitor capture state (shared with the _mk_bullet callback)
var _entries: Array = []
var _exits: Array = []

class IntegBody extends RigidBody2D:
	var seen: Dictionary = {}
	var stamp := -1
	func _integrate_forces(state: PhysicsDirectBodyState2D) -> void:
		stamp += 1
		seen["step%d" % stamp] = {
			"count": state.get_contact_count(),
			"lv": state.linear_velocity,
		}

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")

func _run() -> void:
	print("R80 arm=%s godot=%s engine2d=%s separate_thread=%s" % [
		arm, Engine.get_version_info().string,
		ProjectSettings.get_setting("physics/2d/physics_engine"),
		ProjectSettings.get_setting("physics/2d/run_on_separate_thread")])
	match arm:
		"ccd_ladder": await _arm_ccd_ladder()
		"ccd_gap": await _arm_ccd_gap()
		"ccd_spin": await _arm_ccd_spin()
		"ccd_edge": await _arm_ccd_edge()
		"btm_from": await _arm_btm_from()
		"btm_hit": await _arm_btm_hit()
		"btm_embed": await _arm_btm_embed()
		"btm_margin": await _arm_btm_margin()
		"btm_from2": await _arm_btm_from2()
		"btm_recflag": await _arm_btm_recflag()
		"mac_hit": await _arm_mac_hit()
		"mac_miss": await _arm_mac_miss()
		"tm_hit": await _arm_tm_hit()
		"mac_test_only": await _arm_mac_test_only()
		"mac_nodecomp": await _arm_mac_nodecomp()
		"mac_chain": await _arm_mac_chain()
		"mac_maxcol": await _arm_mac_maxcol()
		"mac_rigid": await _arm_mac_rigid()
		"mac_embed": await _arm_mac_embed()
		"dss_motion": await _arm_dss_motion()
		"dss_embed": await _arm_dss_embed()
		"dss_shapes": await _arm_dss_shapes()
		"dss_purity": await _arm_dss_purity()
		"dss_wrongarg": await _arm_dss_wrongarg()
		"cont_windows": await _arm_cont_windows()
		"cont_cap": await _arm_cont_cap()
		"bds_windows": await _arm_bds_windows()
		"cont_persist": await _arm_cont_persist()
		_: _fail("unknown_arm")

func _fail(reason: String) -> void:
	print("FAIL phys2d_motion %s reason=%s" % [arm, reason])
	quit(1)

func _finish(line: String) -> void:
	# nodes/RIDs die with the process on quit(); no teardown bookkeeping.
	print("PASS phys2d_motion " + line)
	quit(0)

func _space() -> RID:
	return root.world_2d.space

func _dss() -> PhysicsDirectSpaceState2D:
	return PhysicsServer2D.space_get_direct_state(_space())

func _frames(n: int) -> void:
	for i in n:
		await physics_frame
		_frame_no += 1

func _fv(v: Variant) -> String:
	if v is Vector2:
		return "(%.4f,%.4f)" % [v.x, v.y]
	return str(v)

func _teleport(b: PhysicsBody2D, to: Vector2) -> void:
	# server-tier write: lands edge-0 (r79 #12); a node write on a RigidBody2D
	# inside signal windows is reverted by the server-driven sync.
	PhysicsServer2D.body_set_state(b.get_rid(), PhysicsServer2D.BODY_STATE_TRANSFORM,
		Transform2D(0, to))

func _mk_wall(pos: Vector2, size: Vector2) -> StaticBody2D:
	var b := StaticBody2D.new()
	var cs := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = size
	cs.shape = rs
	b.add_child(cs)
	b.position = pos
	root.add_child(b)
	return b

func _mk_rigid(pos: Vector2, shape: Shape2D) -> RigidBody2D:
	var b := RigidBody2D.new()
	var cs := CollisionShape2D.new()
	cs.shape = shape
	b.add_child(cs)
	b.position = pos
	b.gravity_scale = 0.0
	root.add_child(b)
	return b

func _mk_bullet(pos: Vector2, vel: Vector2, ccd: int) -> RigidBody2D:
	var sh := CircleShape2D.new()
	sh.radius = BULLET_R
	var b := _mk_rigid(pos, sh)
	b.can_sleep = false
	b.continuous_cd = ccd
	b.contact_monitor = true
	b.max_contacts_reported = 4
	b.body_entered.connect(func(_n: Node) -> void: _entries.append(1))
	b.linear_velocity = vel
	return b

func _mk_char(pos: Vector2) -> CharacterBody2D:
	var b := CharacterBody2D.new()
	var cs := CollisionShape2D.new()
	var sh := CircleShape2D.new()
	sh.radius = 10.0
	cs.shape = sh
	b.add_child(cs)
	b.position = pos
	root.add_child(b)
	return b

# ---------------------------------------------------------------- Q1: CCD

func _arm_ccd_ladder() -> void:
	# All 21 cells fly simultaneously in parallel y-lanes (600px apart): 30
	# physics frames total instead of 630, same determinism.
	var vels := [600.0, 1150.0, 1200.0, 2000.0, 2400.0, 3000.0, 3600.0]
	var bullets: Array = []
	var lane := 0
	for mk in ["d", "r", "s"]:
		for v in vels:
			lane += 1
			var y := float(lane) * 600.0
			_mk_wall(Vector2(WALL_X, y), Vector2(4, 400))
			var b := _mk_bullet(Vector2(0, y), Vector2(v, 0), CCD[mk])
			bullets.append(b)
	await _frames(30)
	var out: Array = []
	var idx := 0
	for mk in ["d", "r", "s"]:
		var crosses: Array = []
		var xs: Array = []
		var vxs: Array = []
		for v in vels:
			var b: RigidBody2D = bullets[idx]
			idx += 1
			crosses.append(1 if b.global_position.x > WALL_X + WALL_HALF else 0)
			xs.append(snappedf(b.global_position.x, 0.001))
			vxs.append(snappedf(b.linear_velocity.x, 0.001))
		out.append("%s_cross=%s %s_x=%s %s_vx=%s %s_ccd=%d" % [mk, crosses, mk, xs, mk, vxs,
			mk, bullets[idx - 1].get_continuous_collision_detection_mode()])
	_finish("ccd_ladder vels=%s entries=%d %s" % [vels, _entries.size(), " ".join(out)])

func _arm_ccd_gap() -> void:
	# wall = two 4x216 segments at y+-114 -> faces at y+-6, gap 12px; bullet is a
	# 16x16 box through the gap: corners overlap each segment by 2px, the center
	# ray threads the slot untouched.
	var out: Array = []
	var lane := 0
	var hits := {}
	var boxes: Array = []
	for mk in ["d", "r", "s"]:
		var mode: int = CCD[mk]
		lane += 1
		var y := float(lane) * 800.0
		_mk_wall(Vector2(WALL_X, y - 114.0), Vector2(4, 216))
		_mk_wall(Vector2(WALL_X, y + 114.0), Vector2(4, 216))
		var rs := RectangleShape2D.new()
		rs.size = Vector2(16, 16)
		var b := _mk_rigid(Vector2(0, y), rs)
		b.can_sleep = false
		b.continuous_cd = mode
		b.contact_monitor = true
		b.max_contacts_reported = 4
		var tag := lane
		b.body_entered.connect(func(_n: Node) -> void: hits[tag] = hits.get(tag, 0) + 1)
		b.linear_velocity = Vector2(2400, 0)
		boxes.append(b)
		hits[tag] = 0
	await _frames(30)
	for i in boxes.size():
		var mk: String = ["d", "r", "s"][i]
		var b: RigidBody2D = boxes[i]
		out.append("%s_cross=%d %s_hit=%d %s_x=%s" % [mk, 1 if b.global_position.x > WALL_X + WALL_HALF else 0,
			mk, hits.get(i + 1, 0), mk, snappedf(b.global_position.x, 0.001)])
	_finish("ccd_gap v=2400 box16x16 gap12 %s" % [" ".join(out)])

func _arm_ccd_spin() -> void:
	# free bar 8x128 spins w=90deg/step about its center; long-axis pose cycles
	# {0,90}deg (vertical/horizontal); the offset 20x4 wall at (40,+40) is never
	# touched by a sampled pose but IS crossed by the swept volume each quarter
	# turn. ray has no linear motion to cast -> only a rotation-sweeping
	# implementation can catch.
	var out: Array = []
	var lane := 0
	var hits := {}
	var bars: Array = []
	for mk in ["d", "r", "s"]:
		var mode: int = CCD[mk]
		lane += 1
		var y := float(lane) * 800.0
		_mk_wall(Vector2(40, y + 40.0), Vector2(20, 4))
		var rs := RectangleShape2D.new()
		rs.size = Vector2(8, 128)
		var b := _mk_rigid(Vector2(0, y), rs)
		b.can_sleep = false
		b.continuous_cd = mode
		b.contact_monitor = true
		b.max_contacts_reported = 4
		var tag := lane
		b.body_entered.connect(func(_n: Node) -> void: hits[tag] = hits.get(tag, 0) + 1)
		b.angular_velocity = TAU * 15.0  # 90 deg per 1/60s step
		bars.append(b)
		hits[tag] = 0
	await _frames(8)
	# self-verifying: at every sampled pose, a motion=0 body_test_motion must be
	# clean -> no discrete contact was available to catch.
	var poses: Array = []
	var pose_hit: Array = []
	for i in bars.size():
		var b: RigidBody2D = bars[i]
		poses.append(snappedf(rad_to_deg(fposmod(b.rotation, TAU)), 0.01))
		var rp := _mk_test_params(Vector2.ZERO, 0.0, b.global_transform)
		var rr := PhysicsTestMotionResult2D.new()
		pose_hit.append(1 if PhysicsServer2D.body_test_motion(b.get_rid(), rp, rr) else 0)
	for i in bars.size():
		var mk: String = ["d", "r", "s"][i]
		var b: RigidBody2D = bars[i]
		out.append("%s_hit=%d %s_rot=%s %s_ccd=%d" % [mk, hits.get(i + 1, 0), mk,
			poses[i], mk,
			b.get_continuous_collision_detection_mode()])
	_finish("ccd_spin w=90deg_per_step bar8x128 wall20x4@(40,+40) %s endposes=%s endpose_overlap=%s" % [
		" ".join(out), poses, pose_hit])

func _arm_ccd_edge() -> void:
	# doc-canonical edge clip: wall 4x10 spanning y in [0,10]; bullet r8 at y=14
	# -> its center ray at y=14 passes above the wall, its lower edge clips 4px.
	# v=2400 -> discrete steps (40px) skip the 20px overlap window entirely.
	var out: Array = []
	var lane := 0
	var hits := {}
	var bodies: Array = []
	for mk in ["d", "r", "s"]:
		lane += 1
		var y := float(lane) * 800.0
		_mk_wall(Vector2(WALL_X, y + 5.0), Vector2(4, 10))
		var b := _mk_bullet(Vector2(0, y + 14.0), Vector2(2400, 0), CCD[mk])
		var tag := lane
		b.body_entered.connect(func(_n: Node) -> void: hits[tag] = hits.get(tag, 0) + 1)
		bodies.append(b)
		hits[tag] = 0
	await _frames(30)
	for i in bodies.size():
		var mk: String = ["d", "r", "s"][i]
		var b: RigidBody2D = bodies[i]
		out.append("%s_cross=%d %s_hit=%d %s_pos=%s" % [mk,
			1 if b.global_position.x > WALL_X + WALL_HALF else 0, mk, hits.get(i + 1, 0), mk,
			_fv(b.global_position)])
	# r80 critic C2 positive witness: a char probe test-motion into lane 1's
	# wall face MUST hit — a dead wall (collision_layer=0 forge) can't pass.
	var probe := _mk_char(Vector2(WALL_X - 14.0, 805.0))
	await _frames(1)
	var wr := PhysicsTestMotionResult2D.new()
	var wp := _mk_test_params(Vector2(20, 0), 0.0, probe.global_transform)
	var wh: bool = PhysicsServer2D.body_test_motion(probe.get_rid(), wp, wr)
	_finish("ccd_edge v=2400 circle8@y14 wall4x10@[0,10] %s w[%s]" % [
		" ".join(out), _res_line(wr, wh)])

# ------------------------------------------------- Q2: motion-test family

func _mk_test_params(motion: Vector2, margin: float, from: Variant = null, recovery := false) -> PhysicsTestMotionParameters2D:
	var p := PhysicsTestMotionParameters2D.new()
	p.motion = motion
	p.margin = margin
	if from != null:
		p.from = from
	p.recovery_as_collision = recovery
	return p

func _res_line(r: PhysicsTestMotionResult2D, hit_flag: bool) -> String:
	if not hit_flag:
		return "hit=false travel=%s rem=%s" % [_fv(r.get_travel()), _fv(r.get_remainder())]
	var coll: Variant = r.get_collider()
	return "hit=true travel=%s rem=%s pt=%s n=%s depth=%s sf=%s uf=%s cv=%s cls=%s" % [
		_fv(r.get_travel()), _fv(r.get_remainder()), _fv(r.get_collision_point()),
		_fv(r.get_collision_normal()), snappedf(r.get_collision_depth(), 0.0001),
		snappedf(r.get_collision_safe_fraction(), 0.0001), snappedf(r.get_collision_unsafe_fraction(), 0.0001),
		_fv(r.get_collider_velocity()), (coll as Object).get_class() if coll != null else "null"]

func _arm_btm_from() -> void:
	_mk_wall(Vector2(200, 0), Vector2(4, 400))
	var b := _mk_char(Vector2(0, 0))
	await _frames(2)
	b.global_position = Vector2(0, 1000)  # kinematic node write: lands next step
	await _frames(1)
	var r1 := PhysicsTestMotionResult2D.new()
	var p1 := _mk_test_params(Vector2(400, 0), 0.0)  # from unset
	var h1: bool = PhysicsServer2D.body_test_motion(b.get_rid(), p1, r1)
	var r2 := PhysicsTestMotionResult2D.new()
	var p2 := _mk_test_params(Vector2(400, 0), 0.0, b.global_transform)
	var h2: bool = PhysicsServer2D.body_test_motion(b.get_rid(), p2, r2)
	_finish("btm_from body@(0,1000) wall@200 no_from[%s] with_from[%s] bodypos=%s" % [
		_res_line(r1, h1), _res_line(r2, h2), _fv(b.global_position)])

func _arm_btm_hit() -> void:
	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
	var b := _mk_char(Vector2(0, 0))
	await _frames(2)
	var r := PhysicsTestMotionResult2D.new()
	var p := _mk_test_params(Vector2(200, 0), 0.0, b.global_transform)
	var h: bool = PhysicsServer2D.body_test_motion(b.get_rid(), p, r)
	_finish("btm_hit %s bodypos=%s" % [_res_line(r, h), _fv(b.global_position)])

func _arm_btm_embed() -> void:
	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
	var b := _mk_char(Vector2(96, 0))  # circle r10: face 98 -> 8px embedded
	await _frames(2)
	# away-motion rows separate the recovery-report flag from the motion-hit flag
	var out: Array = []
	for spec in [["rec_off", 50.0, false, false], ["rec_on", 50.0, true, false],
			["rec_on_sepray", 50.0, true, true],
			["away_off", -50.0, false, false], ["away_on", -50.0, true, false]]:
		var r := PhysicsTestMotionResult2D.new()
		var p := _mk_test_params(Vector2(spec[1], 0), 0.0, b.global_transform, spec[2])
		if spec[3]:
			p.collide_separation_ray = true
		var h: bool = PhysicsServer2D.body_test_motion(b.get_rid(), p, r)
		out.append("%s[%s]" % [spec[0], _res_line(r, h)])
	_finish("btm_embed %s" % [" ".join(out)])

func _arm_btm_margin() -> void:
	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
	var b := _mk_char(Vector2(0, 0))
	await _frames(2)
	var out: Array = []
	for m in [0.0, 0.08, 1.0, 4.0]:
		var r := PhysicsTestMotionResult2D.new()
		var p := _mk_test_params(Vector2(200, 0), m, b.global_transform)
		var h: bool = PhysicsServer2D.body_test_motion(b.get_rid(), p, r)
		out.append("m%s[%s]" % [m, _res_line(r, h)])
	_finish("btm_margin %s" % [" ".join(out)])

func _arm_btm_from2() -> void:
	# Discriminator for the unset-`from` semantics of btm_from. Three candidate
	# referents predict different outcomes: (a) the body server transform, (b) a
	# stale one-flush-behind pose, (c) Transform2D() identity. Walls at y=0 and
	# y=3000; bodies at y=3000 (node init, no write), y=3600 (no wall) and a
	# server-tier teleported body at y=4200 (wall C there).
	_mk_wall(Vector2(200, 0), Vector2(4, 400))    # lane B: y in [-200,200]
	_mk_wall(Vector2(200, 3000), Vector2(4, 400)) # lane A: y in [2800,3200]
	_mk_wall(Vector2(200, 4200), Vector2(4, 400)) # lane C: y in [4000,4400]
	var b1 := _mk_char(Vector2(0, 3000))  # node-init, no writes
	var b2 := _mk_char(Vector2(0, 3600))  # node-init, empty lane
	var b3 := _mk_char(Vector2(0, 0))
	await _frames(2)
	_teleport(b3, Vector2(0, 4200))      # server-tier write, lands edge-0
	await _frames(1)
	var out: Array = []
	for spec in [["n1", b1, null], ["n2", b2, null],
			["srv_tele", b3, null],
			["ident_from", b2, Transform2D()],
			["with_from3600", b2, Transform2D(0, Vector2(0, 3600))]]:
		var r := PhysicsTestMotionResult2D.new()
		var p := _mk_test_params(Vector2(400, 0), 0.0, spec[2])
		var h: bool = PhysicsServer2D.body_test_motion((spec[1] as PhysicsBody2D).get_rid(), p, r)
		out.append("%s[%s]" % [spec[0], _res_line(r, h)])
	_finish("btm_from2 %s b1pos=%s b3pos=%s" % [" ".join(out),
		_fv(b1.global_position), _fv(b3.global_position)])

func _arm_btm_recflag() -> void:
	# recovery_as_collision discriminator that btm_embed could not separate:
	# embedded start + ZERO motion isolates the recovery report from any
	# motion-phase hit. rec_off=hit would mean recovery is always reported;
	# rec_on-only hit means the flag gates the recovery report.
	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
	var b := _mk_char(Vector2(96, 0))  # embedded 8px in wall face 98
	await _frames(2)
	var out: Array = []
	for spec in [["zero_off", Vector2.ZERO, false], ["zero_on", Vector2.ZERO, true],
			["tiny_off", Vector2(0.01, 0), false], ["tiny_on", Vector2(0.01, 0), true]]:
		var r := PhysicsTestMotionResult2D.new()
		var p := _mk_test_params(spec[1], 0.0, b.global_transform, spec[2])
		var h: bool = PhysicsServer2D.body_test_motion(b.get_rid(), p, r)
		out.append("%s[%s]" % [spec[0], _res_line(r, h)])
	_finish("btm_recflag %s" % [" ".join(out)])

func _kc_line(c: KinematicCollision2D) -> String:
	if c == null:
		return "null"
	var coll: Variant = c.get_collider()
	return "travel=%s rem=%s pos=%s n=%s depth=%s angle=%s cv=%s cls=%s" % [
		_fv(c.get_travel()), _fv(c.get_remainder()), _fv(c.get_position()),
		_fv(c.get_normal()), snappedf(c.get_depth(), 0.0001), snappedf(c.get_angle(), 0.0001),
		_fv(c.get_collider_velocity()), (coll as Object).get_class() if coll != null else "null"]

func _arm_mac_hit() -> void:
	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
	var b := _mk_char(Vector2(0, 0))
	await _frames(2)
	var c := b.move_and_collide(Vector2(200, 0))
	_finish("mac_hit %s bodypos=%s" % [_kc_line(c), _fv(b.global_position)])

func _arm_mac_miss() -> void:
	_mk_wall(Vector2(WALL_X, 500), Vector2(4, 400))
	var b := _mk_char(Vector2(0, 0))
	await _frames(2)
	var c := b.move_and_collide(Vector2(60, 0))
	_finish("mac_miss col=%s bodypos=%s" % ["null" if c == null else "nonnull", _fv(b.global_position)])

func _arm_tm_hit() -> void:
	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
	var b := _mk_char(Vector2(0, 0))
	await _frames(2)
	var c := KinematicCollision2D.new()
	var h: bool = b.test_move(b.global_transform, Vector2(200, 0), c)
	_finish("tm_hit ret=%s %s bodypos=%s" % [h, _kc_line(c), _fv(b.global_position)])

func _arm_mac_test_only() -> void:
	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
	var b := _mk_char(Vector2(0, 0))
	await _frames(2)
	var c := b.move_and_collide(Vector2(200, 0), true)
	var pos1 := b.global_position
	var srv1: Transform2D = PhysicsServer2D.body_get_state(b.get_rid(), PhysicsServer2D.BODY_STATE_TRANSFORM)
	var c2 := b.move_and_collide(Vector2(200, 0))
	_finish("mac_test_only col1=%s pos_after_test=%s srv_after_test=%s col2=%s pos_after_real=%s" % [
		_kc_line(c), _fv(pos1), _fv(srv1.origin),
		"null" if c2 == null else "hit", _fv(b.global_position)])

func _arm_mac_nodecomp() -> void:
	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
	_mk_wall(Vector2(50, -110), Vector2(400, 4))
	var b := _mk_char(Vector2(0, 0))
	await _frames(2)
	var c := b.move_and_collide(Vector2(200, -200))
	_finish("mac_nodecomp %s bodypos=%s" % [_kc_line(c), _fv(b.global_position)])

func _arm_mac_chain() -> void:
	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
	_mk_wall(Vector2(50, -110), Vector2(400, 4))
	var b := _mk_char(Vector2(0, 0))
	await _frames(2)
	var motion := Vector2(200, -200)
	var hops: Array = []
	for i in 4:
		var c := b.move_and_collide(motion)
		if c == null:
			hops.append("n%d=null pos=%s" % [i, _fv(b.global_position)])
			break
		hops.append("h%d[t=%s r=%s n=%s pos=%s]" % [i, _fv(c.get_travel()), _fv(c.get_remainder()), _fv(c.get_normal()), _fv(b.global_position)])
		motion = c.get_remainder().slide(c.get_normal())
	_finish("mac_chain %s" % [" ".join(hops)])

func _arm_mac_maxcol() -> void:
	# no wall: the 5-arg callv refuses on arity before any query runs.
	var b := _mk_char(Vector2(0, 0))
	await _frames(2)
	# max_collisions 5th positional arg: absent from this build's ClassDB sig
	# (4 args). .callv captures the typed refusal without a SCRIPT ERROR.
	var res: Variant = b.callv("move_and_collide", [Vector2(200, 0), false, 0.08, false, 4])
	_finish("mac_maxcol callv5=%s bodypos=%s" % ["null" if res == null else "ret", _fv(b.global_position)])

func _arm_mac_rigid() -> void:
	# Pair 1: miss lane (wall at y=500, body at y=0) — does a RigidBody2D accept
	# move_and_collide at all and does the write persist through the sync?
	# Pair 2: hit lane (wall in the body's lane) — does it stop like the
	# CharacterBody2D and does the server keep the stopped pose?
	_mk_wall(Vector2(WALL_X, 500), Vector2(4, 400))
	_mk_wall(Vector2(WALL_X, 900), Vector2(4, 400))
	var sh := CircleShape2D.new()
	sh.radius = 10.0
	var b := _mk_rigid(Vector2(0, 0), sh)
	var h := _mk_rigid(Vector2(0, 900), sh)  # in the y900 wall lane: motion (200,0) reaches it
	await _frames(2)
	var c := b.move_and_collide(Vector2(60, 0))
	var pos_now := b.global_position
	var ch := h.move_and_collide(Vector2(200, 0))
	var hpos_now := h.global_position
	await _frames(3)
	var pos_late := b.global_position
	var hpos_late := h.global_position
	var srv: Transform2D = PhysicsServer2D.body_get_state(b.get_rid(), PhysicsServer2D.BODY_STATE_TRANSFORM)
	var hsrv: Transform2D = PhysicsServer2D.body_get_state(h.get_rid(), PhysicsServer2D.BODY_STATE_TRANSFORM)
	_finish("mac_rigid col=%s pos_now=%s pos_late=%s srv_late=%s hitcol=%s hpos_now=%s hpos_late=%s hsrv_late=%s" % [
		"null" if c == null else _kc_line(c), _fv(pos_now), _fv(pos_late), _fv(srv.origin),
		"null" if ch == null else _kc_line(ch), _fv(hpos_now), _fv(hpos_late), _fv(hsrv.origin)])

func _arm_mac_embed() -> void:
	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
	_mk_wall(Vector2(WALL_X, 600), Vector2(4, 400))
	_mk_wall(Vector2(WALL_X, 1200), Vector2(4, 400))
	var b := _mk_char(Vector2(96, 0))  # embedded 8px
	var b2 := _mk_char(Vector2(96, 600))
	var b3 := _mk_char(Vector2(96, 1200))
	b3.safe_margin = 5.0  # body property vs the 0.08 arg default
	await _frames(2)
	var c1 := b.move_and_collide(Vector2(50, 0), false, 0.08, false)
	var c2 := b2.move_and_collide(Vector2(50, 0), false, 0.08, true)
	var c3 := b3.move_and_collide(Vector2(50, 0))  # arg default margin
	_finish("mac_embed rec_off[%s pos=%s] rec_on[%s pos=%s] prop5_argdefault[%s pos=%s]" % [
		_kc_line(c1), _fv(b.global_position), _kc_line(c2), _fv(b2.global_position),
		_kc_line(c3), _fv(b3.global_position)])

# ------------------------------------------- Q4: direct-space query family

func _mk_shape_params(shape: Shape2D, xform: Transform2D, motion: Vector2) -> PhysicsShapeQueryParameters2D:
	var p := PhysicsShapeQueryParameters2D.new()
	p.shape = shape
	p.transform = xform
	p.motion = motion
	return p

func _sorted_keys(d: Dictionary) -> Array:
	var k := d.keys()
	k.sort()
	return k

func _rest_line(d: Dictionary) -> String:
	if d.is_empty():
		return "{}"
	return "{keys=%s pt=%s n=%s lv=%s cls=%s}" % [
		_sorted_keys(d), _fv(d.get("point")), _fv(d.get("normal")),
		_fv(d.get("linear_velocity")),
		(d.get("collider") as Object).get_class() if d.get("collider") != null else "null"]

func _arm_dss_motion() -> void:
	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
	await _frames(2)
	var dss := _dss()
	var circle := CircleShape2D.new()
	circle.radius = 8.0
	var p := _mk_shape_params(circle, Transform2D(0, Vector2(0, 0)), Vector2(200, 0))
	var cm := dss.cast_motion(p)
	var cs := dss.collide_shape(p)
	var is_ := dss.intersect_shape(p)
	var ri := dss.get_rest_info(p)
	var p2 := _mk_shape_params(circle, Transform2D(0, Vector2(0, 0)), Vector2(-200, 0))
	var cm2 := dss.cast_motion(p2)
	var p3 := _mk_shape_params(circle, Transform2D(0, Vector2(0, 0)), Vector2.ZERO)
	var cm3 := dss.cast_motion(p3)
	var ri3 := dss.get_rest_info(p3)  # zero-motion control: {} proves the hit was swept
	_finish("dss_motion cm=%s cm_away=%s cm_zero=%s cs_n=%d is_n=%d ri=%s ri_zero=%s" % [
		cm, cm2, cm3, cs.size(), is_.size(), _rest_line(ri), _rest_line(ri3)])

func _arm_dss_embed() -> void:
	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
	await _frames(2)
	var dss := _dss()
	var circle := CircleShape2D.new()
	circle.radius = 8.0
	var pt := _mk_shape_params(circle, Transform2D(0, Vector2(96, 0)), Vector2(200, 0))
	var cm_t := dss.cast_motion(pt)
	var pa := _mk_shape_params(circle, Transform2D(0, Vector2(96, 0)), Vector2(-200, 0))
	var cm_a := dss.cast_motion(pa)
	var cs := dss.collide_shape(pt)
	var is_ := dss.intersect_shape(pt)
	var ri := dss.get_rest_info(pt)
	_finish("dss_embed cm_toward=%s cm_away=%s cs_n=%d cs_pts=%s is_n=%d ri=%s" % [
		cm_t, cm_a, cs.size(), cs, is_.size(), _rest_line(ri)])

func _arm_dss_shapes() -> void:
	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
	var mover := _mk_bullet(Vector2(300, 0), Vector2(120, 0), 0)
	mover.contact_monitor = false
	await _frames(2)
	var dss := _dss()
	var rq := PhysicsRayQueryParameters2D.new()
	rq.from = Vector2(0, 0)
	rq.to = Vector2(200, 0)
	var ray_hit := dss.intersect_ray(rq)
	var rq2 := PhysicsRayQueryParameters2D.new()
	rq2.from = Vector2(0, 500)
	rq2.to = Vector2(200, 500)
	var ray_miss := dss.intersect_ray(rq2)
	var circle := CircleShape2D.new()
	circle.radius = 8.0
	var qm := _mk_shape_params(circle, Transform2D(0, mover.global_position), Vector2.ZERO)
	var ri := dss.get_rest_info(qm)
	var is_ := dss.intersect_shape(qm)
	var qz := _mk_shape_params(circle, Transform2D(0, Vector2(96, 0)), Vector2.ZERO)
	var cs_full := dss.collide_shape(qz, 32)
	var cs_cap1 := dss.collide_shape(qz, 1)
	_finish("dss_shapes ray_hit={keys=%s cls=%s pos=%s n=%s} ray_miss=%s ri=%s is_n=%d is0={keys=%s cls=%s} cs_full=%d cs_cap1=%d" % [
		_sorted_keys(ray_hit), (ray_hit["collider"] as Object).get_class(), _fv(ray_hit.get("position")), _fv(ray_hit.get("normal")),
		"{}" if ray_miss.is_empty() else "nonempty", _rest_line(ri), is_.size(),
		_sorted_keys(is_[0]) if is_.size() > 0 else [],
		(is_[0]["collider"] as Object).get_class() if is_.size() > 0 else "null",
		cs_full.size(), cs_cap1.size()])

func _arm_dss_purity() -> void:
	_mk_wall(Vector2(WALL_X, 0), Vector2(4, 400))
	await _frames(2)
	var dss := _dss()
	var circle := CircleShape2D.new()
	circle.radius = 8.0
	var p := _mk_shape_params(circle, Transform2D(0.3, Vector2(5, 7)), Vector2(150, -40))
	p.margin = 0.5
	var before := [p.transform, p.motion, p.margin, p.collision_mask, p.collide_with_bodies, p.collide_with_areas, p.exclude]
	dss.cast_motion(p)
	dss.collide_shape(p)
	dss.intersect_shape(p)
	dss.get_rest_info(p)
	var after := [p.transform, p.motion, p.margin, p.collision_mask, p.collide_with_bodies, p.collide_with_areas, p.exclude]
	_finish("dss_purity equal=%s before=%s after=%s" % [before == after, before, after])

func _arm_dss_wrongarg() -> void:
	# no wall: every call refuses on param class/null before any query runs.
	await _frames(2)
	var dss := _dss()
	var ptq := PhysicsPointQueryParameters2D.new()
	ptq.position = Vector2(WALL_X, 0)
	var is_bad: Variant = dss.call("intersect_shape", ptq)
	var cm_bad: Variant = dss.call("cast_motion", ptq)
	var ri_bad: Variant = dss.call("get_rest_info", ptq)
	var cs_bad: Variant = dss.call("collide_shape", ptq)
	var is_null: Variant = dss.call("intersect_shape", null)
	var ray_null: Variant = dss.call("intersect_ray", null)
	var pt_null: Variant = dss.call("intersect_point", null)
	_finish("dss_wrongarg is=%s cm=%s ri=%s cs=%s is_null=%s ray_null=%s pt_null=%s" % [
		is_bad.size() if is_bad is Array else "null", cm_bad, ri_bad,
		cs_bad.size() if cs_bad is Array else "null",
		is_null.size() if is_null is Array else "null", ray_null,
		pt_null.size() if pt_null is Array else "null"])

# ------------------------------------------------- Q5: contact materialization

func _mk_faller(pos: Vector2, cap := 4) -> RigidBody2D:
	var b := RigidBody2D.new()
	var cs := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = Vector2(10, 10)
	cs.shape = rs
	b.add_child(cs)
	b.position = pos
	b.gravity_scale = 4.0
	root.add_child(b)
	b.contact_monitor = true
	b.max_contacts_reported = cap
	return b

func _arm_cont_windows() -> void:
	_mk_wall(Vector2(0, 20), Vector2(200, 20))
	var b := _mk_faller(Vector2(0, -4))
	var reads := {}
	b.body_entered.connect(func(_n: Node) -> void:
		_entries.append(_frame_no)
		reads["in_cb"] = [b.get_contact_count(), b.get_colliding_bodies().size()])
	b.body_exited.connect(func(_n: Node) -> void:
		_exits.append(_frame_no)
		reads["in_exit_cb"] = [b.get_contact_count(), b.get_colliding_bodies().size()])
	var f0 := _frame_no
	while _entries.is_empty() and _frame_no - f0 < 200:
		await physics_frame
		_frame_no += 1
	reads["pp_after_entry"] = [b.get_contact_count(), b.get_colliding_bodies().size()]
	await process_frame
	reads["process_after_entry"] = [b.get_contact_count(), b.get_colliding_bodies().size()]
	_teleport(b, Vector2(2000, -4000))
	var f1 := _frame_no
	while _exits.is_empty() and _frame_no - f1 < 200:
		await physics_frame
		_frame_no += 1
	reads["pp_after_exit"] = [b.get_contact_count(), b.get_colliding_bodies().size()]
	await process_frame
	reads["process_after_exit"] = [b.get_contact_count(), b.get_colliding_bodies().size()]
	var eframe: int = _entries[0] if _entries.size() > 0 else -1
	var xframe: int = _exits[0] if _exits.size() > 0 else -1
	_finish("cont_windows entry_f=%d exit_f=%d in_cb=%s pp_entry=%s proc_entry=%s in_exit_cb=%s pp_exit=%s proc_exit=%s" % [
		eframe, xframe, reads.get("in_cb"), reads.get("pp_after_entry"), reads.get("process_after_entry"),
		reads.get("in_exit_cb"), reads.get("pp_after_exit"), reads.get("process_after_exit")])

func _arm_cont_cap() -> void:
	# corner wedge, two identical fallers: A capped at 1, B uncapped (4).
	# The delta between them is the truncation witness.
	_mk_wall(Vector2(0, 20), Vector2(200, 20))
	_mk_wall(Vector2(17, 0), Vector2(20, 200))
	_mk_wall(Vector2(400, 20), Vector2(200, 20))
	_mk_wall(Vector2(417, 0), Vector2(20, 200))
	var a := _mk_faller(Vector2(4, -4), 1)
	var b2 := _mk_faller(Vector2(404, -4), 4)
	var entered := {"a": false, "b": false}
	a.body_entered.connect(func(_n: Node) -> void: entered["a"] = true)
	b2.body_entered.connect(func(_n: Node) -> void: entered["b"] = true)
	var f0 := _frame_no
	while not (entered["a"] and entered["b"]) and _frame_no - f0 < 200:
		await physics_frame
		_frame_no += 1
	await _frames(30)
	var arr_a := a.get_colliding_bodies()
	var arr_b := b2.get_colliding_bodies()
	_finish("cont_cap capped=[count=%d arr=%d] uncapped=[count=%d arr=%d cls=%s,%s]" % [
		a.get_contact_count(), arr_a.size(),
		b2.get_contact_count(), arr_b.size(),
		(arr_b[0] as Object).get_class() if arr_b.size() > 0 else "none",
		(arr_b[1] as Object).get_class() if arr_b.size() > 1 else "none"])

func _arm_bds_windows() -> void:
	_mk_wall(Vector2(0, 20), Vector2(200, 20))
	var b := IntegBody.new()
	var cs := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = Vector2(10, 10)
	cs.shape = rs
	b.add_child(cs)
	b.position = Vector2(0, -4)
	b.gravity_scale = 4.0
	b.contact_monitor = true
	b.max_contacts_reported = 4
	root.add_child(b)
	var cb_reads := {}
	b.body_entered.connect(func(_n: Node) -> void:
		_entries.append(_frame_no)
		var st: Variant = PhysicsServer2D.body_get_direct_state(b.get_rid())
		cb_reads["in_cb"] = {"obj": st != null,
			"count": (st as PhysicsDirectBodyState2D).get_contact_count() if st != null else -1})
	var st0: Variant = PhysicsServer2D.body_get_direct_state(b.get_rid())
	var out0 := "null" if st0 == null else "obj"
	var cnt0: int = (st0 as PhysicsDirectBodyState2D).get_contact_count() if st0 != null else -2
	var f0 := _frame_no
	while _entries.is_empty() and _frame_no - f0 < 200:
		await physics_frame
		_frame_no += 1
	var st1: Variant = PhysicsServer2D.body_get_direct_state(b.get_rid())
	var out1 := "null" if st1 == null else "obj"
	var cnt1: int = (st1 as PhysicsDirectBodyState2D).get_contact_count() if st1 != null else -2
	await process_frame
	var st2: Variant = PhysicsServer2D.body_get_direct_state(b.get_rid())
	var out2 := "null" if st2 == null else "obj"
	var cnt2: int = (st2 as PhysicsDirectBodyState2D).get_contact_count() if st2 != null else -2
	var integ: Variant = b.seen.get("step0", {})
	var last_integ: Variant = b.seen.get("step%d" % b.stamp, {})
	_finish("bds_windows oop=%s cnt=%d in_cb=%s in_phase=%s cnt=%d proc=%s cnt=%d integ_first=%s integ_last=%s" % [
		out0, cnt0, cb_reads.get("in_cb"), out1, cnt1, out2, cnt2, integ, last_integ])

func _arm_cont_persist() -> void:
	_mk_wall(Vector2(0, 20), Vector2(200, 20))
	var b := _mk_faller(Vector2(0, -4))
	b.body_entered.connect(func(_n: Node) -> void: _entries.append(_frame_no))
	b.body_exited.connect(func(_n: Node) -> void: _exits.append(_frame_no))
	var f0 := _frame_no
	while _entries.is_empty() and _frame_no - f0 < 200:
		await physics_frame
		_frame_no += 1
	var per_frame: Array = []
	_teleport(b, Vector2(2000, -4000))
	for i in 6:
		per_frame.append([_frame_no, b.get_colliding_bodies().size()])
		await physics_frame
		_frame_no += 1
	per_frame.append([_frame_no, b.get_colliding_bodies().size()])
	var eframe: int = _entries[0] if _entries.size() > 0 else -1
	var xframe: int = _exits[0] if _exits.size() > 0 else -1
	_finish("cont_persist entry_f=%d exit_f=%d seq[frame,size]=%s" % [eframe, xframe, per_frame])
