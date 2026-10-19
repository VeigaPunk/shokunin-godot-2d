extends SceneTree
# r105 physics-replay boundary probe — what repeated simulation of an identical
# 2D scene actually guarantees on this host (Godot 4.7.2.stable headless).
#
# The docs disavow determinism (physics introduction Warning); this fixture
# measures instead of assuming. Scenario: 8 RigidBody2D boxes with a shared
# friction/bounce material dropped onto a StaticBody2D floor between two walls,
# plus one CharacterBody2D driven by a fixed scripted velocity stream applied
# from the physics_frame handler. Each run simulates TICKS physics ticks.
#
# Arms:
#   inproc  — build+simulate the scenario twice in one process (fresh nodes);
#             print both digests, equality, and gameplay invariants.
#   digest  — build+simulate once; print the sha256 state digest on a REPLAY
#             diagnostic line (cross-process comparison material) plus a
#             PASS line carrying only invariants.
#   perturb — negative control: identical run, then a second run with body 0
#             nudged +1e-4 px in x; the digest MUST differ, proving the digest
#             discriminates (a constant or insensitive digest would PASS
#             everything vacuously).
#
# Battery launch shape:
#   godot --headless --path <scratch> --script res://r105_phys_replay.gd -- --arm=<arm>
# One `PASS r105_phys_replay <arm> <keys>` line per arm; digests live on
# REPLAY diagnostic lines so the pinned PASS line stays host-stable.
# Never echoes nested engine output containing `ERROR:`.

const N_BOXES := 8
const TICKS := 240
const TPS := 120  # sim runs at 120 Hz so one 240-tick run costs ~2 s wall
const FLOOR_TOP := 480.0
const MAX_SPEED := 1200.0
const CHAR_X_LO := 170.0  # lower bound fails if the scripted input never moved it
const CHAR_X_HI := 600.0
const PERTURB_DX := 1e-4

var arm := ""
var _tick := 0
var _boxes: Array = []
var _char: CharacterBody2D
var _world: Node2D

func _arg(name: String, def: String = "") -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--" + name + "="):
			return a.substr(name.length() + 3)
	return def

func _initialize() -> void:
	arm = _arg("arm")
	Engine.physics_ticks_per_second = TPS
	call_deferred("_run")

func _fail(reason: String) -> void:
	print("FAIL r105_phys_replay %s reason=%s" % [arm, reason])
	quit(1)

func _box_material() -> PhysicsMaterial:
	var m := PhysicsMaterial.new()
	m.friction = 0.5
	m.bounce = 0.3
	return m

func _rect_body(pos: Vector2, size: Vector2, mat: PhysicsMaterial) -> StaticBody2D:
	var b := StaticBody2D.new()
	var cs := CollisionShape2D.new()
	var sh := RectangleShape2D.new()
	sh.size = size
	cs.shape = sh
	b.add_child(cs)
	b.physics_material_override = mat
	b.position = pos
	return b

func _build(perturb_dx: float = 0.0) -> void:
	var mat := _box_material()
	_world = Node2D.new()
	root.add_child(_world)
	# floor: top face at FLOOR_TOP
	_world.add_child(_rect_body(Vector2(400, FLOOR_TOP + 10), Vector2(720, 20), mat))
	# walls keep all bodies inside the measured arena
	_world.add_child(_rect_body(Vector2(60, 280), Vector2(20, 440), mat))
	_world.add_child(_rect_body(Vector2(740, 280), Vector2(20, 440), mat))
	_boxes.clear()
	for i in N_BOXES:
		var rb := RigidBody2D.new()
		var cs := CollisionShape2D.new()
		var sh := RectangleShape2D.new()
		sh.size = Vector2(16, 16)
		cs.shape = sh
		rb.add_child(cs)
		rb.physics_material_override = mat
		rb.position = Vector2(180 + i * 50 + (perturb_dx if i == 0 else 0.0),
				40 + (i % 3) * 45)
		rb.rotation = i * 0.11
		_world.add_child(rb)
		_boxes.append(rb)
	# scripted CharacterBody2D — velocity is set from the physics loop below
	_char = CharacterBody2D.new()
	var ccs := CollisionShape2D.new()
	var csh := RectangleShape2D.new()
	csh.size = Vector2(20, 30)
	ccs.shape = csh
	_char.add_child(ccs)
	_char.position = Vector2(150, 440)
	_world.add_child(_char)

func _char_velocity(tick: int) -> Vector2:
	# fixed input stream: sweep right 1.0 s, sweep left ~0.67 s, then stop
	var vx := 0.0
	if tick < 120:
		vx = 160.0
	elif tick < 200:
		vx = -120.0
	return Vector2(vx, 600.0)  # constant fall speed until the floor stops it

func _simulate() -> void:
	for t in TICKS:
		await physics_frame
		_tick = t
		if is_instance_valid(_char):
			_char.velocity = _char_velocity(t)
			_char.move_and_slide()

func _teardown() -> void:
	if is_instance_valid(_world):
		_world.queue_free()
	_world = null
	_boxes.clear()
	_char = null
	await process_frame
	await physics_frame

func _state_digest() -> String:
	var vals := PackedFloat64Array()
	for rb in _boxes:
		vals.append(rb.position.x)
		vals.append(rb.position.y)
		vals.append(rb.rotation)
		vals.append(rb.linear_velocity.x)
		vals.append(rb.linear_velocity.y)
		vals.append(rb.angular_velocity)
		vals.append(1.0 if rb.sleeping else 0.0)
	vals.append(_char.position.x)
	vals.append(_char.position.y)
	vals.append(_char.velocity.x)
	vals.append(_char.velocity.y)
	vals.append(1.0 if _char.is_on_floor() else 0.0)
	var h := HashingContext.new()
	h.start(HashingContext.HASH_SHA256)
	h.update(vals.to_byte_array())
	return h.finish().hex_encode()

func _invariants() -> Dictionary:
	var above := true
	var max_speed := 0.0
	for rb in _boxes:
		if not is_instance_valid(rb) or rb.position.y >= FLOOR_TOP:
			above = false
		var sp: float = rb.linear_velocity.length()
		if sp > max_speed:
			max_speed = sp
	var char_ok := is_instance_valid(_char) \
		and _char.position.x > CHAR_X_LO and _char.position.x < CHAR_X_HI \
		and _char.position.y < FLOOR_TOP
	return {
		"bodies": _boxes.size(),
		"above": above,
		"max_speed_ok": max_speed < MAX_SPEED,
		"char_inrange": char_ok,
	}

func _invars_ok(inv: Dictionary) -> bool:
	return inv["bodies"] == N_BOXES and inv["above"] \
		and inv["max_speed_ok"] and inv["char_inrange"]

func _invars_str(inv: Dictionary) -> String:
	return "bodies=%d above=%s max_speed_ok=%s char_inrange=%s" % [
		inv["bodies"], str(inv["above"]), str(inv["max_speed_ok"]),
		str(inv["char_inrange"])]

func _run() -> void:
	match arm:
		"digest":
			_build()
			await _simulate()
			var inv := _invariants()
			print("REPLAY arm=digest digest=%s %s" % [_state_digest(), _invars_str(inv)])
			if _invars_ok(inv):
				print("PASS r105_phys_replay digest " + _invars_str(inv))
				quit(0)
			else:
				_fail("invariant")
		"inproc":
			_build()
			await _simulate()
			var inv_a := _invariants()
			var d_a := _state_digest()
			await _teardown()
			_build()
			await _simulate()
			var inv_b := _invariants()
			var d_b := _state_digest()
			var equal := d_a == d_b
			print("REPLAY arm=inproc run=1 digest=%s" % d_a)
			print("REPLAY arm=inproc run=2 digest=%s" % d_b)
			print("REPLAY arm=inproc equal=%s" % str(equal))
			if not equal:
				_fail("inproc_diverged equal=false")
			elif not (_invars_ok(inv_a) and _invars_ok(inv_b)):
				_fail("invariant")
			else:
				print("PASS r105_phys_replay inproc equal=true " + _invars_str(inv_b))
				quit(0)
		"perturb":
			_build()
			await _simulate()
			var inv_a := _invariants()
			var d_a := _state_digest()
			await _teardown()
			_build(PERTURB_DX)
			await _simulate()
			var d_b := _state_digest()
			var differs := d_a != d_b
			print("REPLAY arm=perturb base=%s pert=%s differs=%s" % [d_a, d_b, str(differs)])
			if not differs:
				_fail("perturb_invisible digest does not discriminate at dx=1e-4")
			elif not _invars_ok(inv_a):
				_fail("invariant")
			else:
				print("PASS r105_phys_replay perturb differs=true " + _invars_str(inv_a))
				quit(0)
		_:
			_fail("unknown_arm")
