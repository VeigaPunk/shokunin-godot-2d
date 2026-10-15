extends SceneTree
# r88 BOUNDARY seat — Sprite2D frame OOB ERROR budget + sprite metadata / sprite-vs-physics replay.
# Launch: godot --headless --path proj --script res://b88_sprite.gd -- --arm=<arm>
# Arms: oob0 oob1 oob2 oob3 oobneg (one frame set each, ERROR count measured from stderr),
#       phys (scout's sprite_phys mirror), meta (scout's sprite_meta mirror).

var arm := ""
var startup_delay_ms := 0

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
		elif a.begins_with("--delay="):
			startup_delay_ms = int(a.substr(8))
	if arm.is_empty():
		print("R88B ARM_MISSING")
		quit(1)
		return
	print("R88B arm=%s startup_delay_ms=%d" % [arm, startup_delay_ms])
	if startup_delay_ms > 0:
		OS.delay_msec(startup_delay_ms)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"oob0": _arm_oob(0)
		"oob1": _arm_oob(1)
		"oob2": _arm_oob(2)
		"oob3": _arm_oob(3)
		"oobneg": _arm_oob(-1)
		"phys": _arm_phys()
		"fall": _arm_fall()
		"fall_anchor": _arm_fall_anchor()
		"fall_sync": _arm_fall_sync()
		"meta": _arm_meta()
		_:
			print("R88B unknown_arm=%s" % arm)
			quit(2)

func _v2(p: Vector2) -> String:
	return "%.4f,%.4f" % [p.x, p.y]

func _body(x: float, y: float) -> RigidBody2D:
	var b := RigidBody2D.new()
	var cs := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = 8.0
	cs.shape = circle
	b.add_child(cs)
	b.position = Vector2(x, y)
	return b

func _tex() -> ImageTexture:
	var img := Image.create(16, 16, false, Image.FORMAT_RGBA8)
	return ImageTexture.create_from_image(img)

# One sprite, one frame set; mirrors the "regioned" variant of the scout's sprite_phys.
func _arm_oob(v: int) -> void:
	var spr := Sprite2D.new()
	spr.texture = _tex()
	spr.region_enabled = true
	spr.region_rect = Rect2(2, 2, 4, 4)
	spr.hframes = 2
	root.add_child(spr)
	spr.frame = v
	print("R88B sprite set=%d readback_frame=%d coords=%s rect=%s hf=%d vf=%d" % [
		v, spr.frame, spr.frame_coords, spr.get_rect(), spr.hframes, spr.vframes])
	quit()

# Exact mirror of the scout's _arm_sprite_phys.
func _arm_phys() -> void:
	var results: PackedStringArray = []
	for variant in ["plain", "flipped", "regioned", "scaled_neg"]:
		var b := _body(variant.length() * 50, -50)
		var spr := Sprite2D.new()
		spr.texture = _tex()
		b.add_child(spr)
		match variant:
			"flipped":
				spr.flip_h = true
				spr.flip_v = true
			"regioned":
				spr.region_enabled = true
				spr.region_rect = Rect2(2, 2, 4, 4)
				spr.hframes = 2
				spr.frame = 3
			"scaled_neg":
				spr.scale = Vector2(-1, -1)
		root.add_child(b)
	for i in 30:
		await physics_frame
	for b in root.get_children():
		if b is RigidBody2D:
			var spr: Sprite2D = null
			for c in b.get_children():
				if c is Sprite2D:
					spr = c
			results.append("pos=%.4f,%.4f spr_gt=%s spr_rel=%s" % [
				b.global_position.x, b.global_position.y, spr.global_transform, spr.transform])
	print("R88B sprite_phys [%s]" % "|".join(results))
	quit()

# Per-step fall law + engine settings — resolves any step-count / damp ambiguity in the
# sprite_phys / rb_gravity y pins.
func _arm_fall() -> void:
	print("R88B fall tps=%d time_scale=%.3f max_fps=%d grav=%s ldamp=%s adamp=%s" % [
		Engine.physics_ticks_per_second, Engine.time_scale, Engine.max_fps,
		ProjectSettings.get_setting("physics/2d/default_gravity", "<unset>"),
		ProjectSettings.get_setting("physics/2d/default_linear_damp", "<unset>"),
		ProjectSettings.get_setting("physics/2d/default_angular_damp", "<unset>")])
	var b := _body(0, 0)
	root.add_child(b)
	var ys: Array = []
	for i in 60:
		await physics_frame
		ys.append("%d:%.4f/%.4f" % [i, b.global_position.y, b.linear_velocity.y])
	print("R88B fall ys=%s" % ",".join(ys))
	quit()

# Anchored recipe test: baseline at the first physics_frame after creation, then count N more.
# The delta should be immune to the startup step-count race.
func _arm_fall_anchor() -> void:
	var b := _body(0, 0)
	root.add_child(b)
	await physics_frame
	var y0 := b.global_position.y
	var v0 := b.linear_velocity.y
	var ys: Array = []
	for i in 30:
		await physics_frame
		ys.append("%.4f" % b.global_position.y)
	print("R88B fall_anchor y0=%.4f v0=%.4f d30=%.4f y30=%.4f" % [
		y0, v0, b.global_position.y - y0, b.global_position.y])
	quit()

# Deterministic recipe: skip emissions until the body's first integration is visible
# (v != 0), then count N-1 more — the resulting y should be the "N integrations from
# rest" value in both startup modes.
func _arm_fall_sync() -> void:
	var b := _body(0, 0)
	root.add_child(b)
	var guard := 0
	while b.linear_velocity.y == 0.0 and guard < 5:
		await physics_frame
		guard += 1
	var v1 := b.linear_velocity.y
	for i in 29:
		await physics_frame
	print("R88B fall_sync guard=%d v1=%.4f y30=%.4f" % [guard, v1, b.global_position.y])
	quit()

# Exact mirror of the scout's _arm_sprite_meta.
func _arm_meta() -> void:
	var img := Image.create(32, 16, false, Image.FORMAT_RGBA8)
	var tex := ImageTexture.create_from_image(img)
	var s := Sprite2D.new()
	s.texture = tex
	root.add_child(s)
	var fired: Array = []
	s.frame_changed.connect(func(): fired.append("fc"))
	s.texture_changed.connect(func(): fired.append("tc"))
	s.region_enabled = true
	s.region_rect = Rect2(4, 4, 8, 8)
	s.hframes = 4
	s.vframes = 2
	s.frame = 5
	s.flip_h = true
	s.flip_v = true
	s.offset = Vector2(3, -2)
	s.centered = false
	print("R88B sprite_meta readback=[re=%s rr=%s hf=%d vf=%d f=%d fc=%s fh=%s fv=%s off=%s cen=%s]" % [
		s.region_enabled, s.region_rect, s.hframes, s.vframes, s.frame, s.frame_coords,
		s.flip_h, s.flip_v, s.offset, s.centered],
		" xf=", s.global_transform,
		" signals=", fired)
	var s2 := Sprite2D.new()
	s2.texture = tex
	root.add_child(s2)
	s2.scale = Vector2(-1, 1)
	print("R88B sprite_meta scale_neg1_xf=", s2.global_transform,
		" get_rect=", s.get_rect(), " s2_rect=", s2.get_rect())
	quit()
