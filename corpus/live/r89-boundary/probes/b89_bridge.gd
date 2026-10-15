extends SceneTree
# r89-boundary probe — geometry -> CollisionPolygon2D -> falling body bridge, attacked
# on the r88 startup step-count race (Case A: first emission has no step; Case B: one step).
# Launch shape: godot --headless --path <proj> --script res://b89_bridge.gd -- --arm=<name> [--frames=N]
# Arms:
#   verbatim  : the r89-scout _arm_bridge sequence, plus a `first=` class diagnostic
#   traj      : same build, one sample per physics frame (1..N), then rest@N
#   sync      : r88 v!=0 sync recipe (guard), then N-1 awaits
#   delay200  : verbatim after OS.delay_msec(200) in _initialize (r88 Case-B forcing)
#   delay500  : verbatim after OS.delay_msec(500)
#   ringtraj  : the ring contour0 build (_drop_for), one sample per frame 1..N
#   ringsync  : ring build with the sync recipe
#   hold      : verbatim N awaits, then a second read N awaits later
# Prints `R89B <arm> <key>=<value>` lines and one `PASS b89_bridge <arm> <items>` line.

var arm := ""
var _frames := 60
var _items: PackedStringArray = []
var _delay := 0

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
		elif a.begins_with("--frames="):
			_frames = int(a.substr(9))
		elif a.begins_with("--delay="):
			_delay = int(a.substr(8))
	if _delay > 0:
		OS.delay_msec(_delay)
	_run.call_deferred()

func _it(key: String, value: String) -> void:
	_items.append("%s=%s" % [key, value])
	print("R89B %s %s=%s" % [arm, key, value])

func _pass() -> void:
	print("PASS b89_bridge %s %s" % [arm, " ".join(_items)])
	quit()

func _v2(p: Vector2) -> String:
	return "%.4f,%.4f" % [p.x, p.y]

func _area(poly: PackedVector2Array) -> float:
	var a := 0.0
	for i in poly.size():
		var p := poly[i]
		var q := poly[(i + 1) % poly.size()]
		a += p.x * q.y - q.x * p.y
	return a / 2.0

func _poly2str(arr: Array) -> String:
	var parts: PackedStringArray = []
	for poly in arr:
		var verts: PackedStringArray = []
		for v in poly:
			verts.append(_v2(v))
		parts.append("n%d[%s]" % [poly.size(), ";".join(verts)])
	return "k=%d{%s}" % [arr.size(), "|".join(parts)]

func _sq(cx: float, cy: float, r: float) -> PackedVector2Array:
	return PackedVector2Array([Vector2(cx - r, cy - r), Vector2(cx + r, cy - r),
		Vector2(cx + r, cy + r), Vector2(cx - r, cy + r)])

func _body(x: float, y: float) -> RigidBody2D:
	var b := RigidBody2D.new()
	var cs := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = 8.0
	cs.shape = circle
	b.add_child(cs)
	b.position = Vector2(x, y)
	return b

func _hits(b: RigidBody2D) -> int:
	var dss := root.world_2d.direct_space_state
	var q := PhysicsPointQueryParameters2D.new()
	q.position = b.global_position
	return dss.intersect_point(q).size()

func _build_wall() -> Array:
	var wall := Geometry2D.clip_polygons(_sq(0, 0, 60), _sq(0, -30, 60))
	var st := StaticBody2D.new()
	var pol := CollisionPolygon2D.new()
	if wall.size() > 0:
		pol.polygon = wall[0]
	st.add_child(pol)
	st.position = Vector2(0, 60)
	root.add_child(st)
	return wall

func _run() -> void:
	match arm:
		"verbatim": _a_verbatim()
		"traj": _a_traj()
		"sync": _a_sync()
		"delay200": _a_verbatim()
		"delay500": _a_verbatim()
		"ringtraj": _a_ringtraj()
		"ringsync": _a_ringsync()
		"hold": _a_hold()
		_: _a_verbatim()

func _a_verbatim() -> void:
	var wall := _build_wall()
	var b := _body(0, -100)
	root.add_child(b)
	await physics_frame
	_it("first", "y=%.6f v=%.6f" % [b.global_position.y, b.linear_velocity.y])
	for i in _frames - 1:
		await physics_frame
	_it("wall", _poly2str(wall))
	_it("tps", "%d frames=%d delay=%d" % [Engine.physics_ticks_per_second, _frames, _delay])
	_it("rest", "y=%.4f y6=%.6f vel=%.4f,%.4f self_hit=%d" % [b.global_position.y,
		b.global_position.y, b.linear_velocity.x, b.linear_velocity.y, _hits(b)])
	_pass()

func _a_traj() -> void:
	var wall := _build_wall()
	var b := _body(0, -100)
	root.add_child(b)
	var ys: PackedFloat32Array = []
	var vs: PackedFloat32Array = []
	var hs: PackedInt32Array = []
	for i in _frames:
		await physics_frame
		ys.append(b.global_position.y)
		vs.append(b.linear_velocity.y)
		hs.append(_hits(b))
	for i in _frames:
		print("R89B %s t=%d y=%.6f v=%.6f hits=%d" % [arm, i + 1, ys[i], vs[i], hs[i]])
	_it("wall", _poly2str(wall))
	_it("tps", "%d frames=%d" % [Engine.physics_ticks_per_second, _frames])
	_it("rest", "y=%.4f y6=%.6f vel=%.4f,%.4f self_hit=%d" % [ys[_frames - 1], ys[_frames - 1],
		b.linear_velocity.x, vs[_frames - 1], hs[_frames - 1]])
	_it("hits_set", "uniq=%s" % str(_uniq(hs)))
	_pass()

func _uniq(arr: PackedInt32Array) -> Array:
	var out: Array = []
	for v in arr:
		if not out.has(v):
			out.append(v)
	return out

func _a_sync() -> void:
	var wall := _build_wall()
	var b := _body(0, -100)
	root.add_child(b)
	await physics_frame
	var guard := 0
	while b.linear_velocity == Vector2.ZERO and guard < 10:
		guard += 1
		await physics_frame
	for i in _frames - 1:
		await physics_frame
	_it("guard", "%d" % guard)
	_it("wall", _poly2str(wall))
	_it("tps", "%d frames=%d" % [Engine.physics_ticks_per_second, _frames])
	_it("rest", "y=%.4f y6=%.6f vel=%.4f,%.4f self_hit=%d" % [b.global_position.y,
		b.global_position.y, b.linear_velocity.x, b.linear_velocity.y, _hits(b)])
	_pass()

func _a_hold() -> void:
	var wall := _build_wall()
	var b := _body(0, -100)
	root.add_child(b)
	for i in _frames:
		await physics_frame
	var y60 := b.global_position.y
	var h60 := _hits(b)
	for i in _frames:
		await physics_frame
	_it("wall", _poly2str(wall))
	_it("tps", "%d frames=%d" % [Engine.physics_ticks_per_second, _frames])
	_it("rest60", "y=%.4f y6=%.6f hits=%d" % [y60, y60, h60])
	_it("rest120", "y=%.4f y6=%.6f vel=%.4f,%.4f self_hit=%d" % [b.global_position.y,
		b.global_position.y, b.linear_velocity.x, b.linear_velocity.y, _hits(b)])
	_pass()

func _a_ringtraj() -> void:
	var ring := Geometry2D.clip_polygons(_sq(0, 0, 40), _sq(0, 0, 10))
	var st := StaticBody2D.new()
	var pol := CollisionPolygon2D.new()
	pol.polygon = ring[0]
	st.add_child(pol)
	root.add_child(st)
	var b := _body(0, -60)
	root.add_child(b)
	var ys: PackedFloat32Array = []
	var hs: PackedInt32Array = []
	for i in _frames:
		await physics_frame
		ys.append(b.global_position.y)
		hs.append(_hits(b))
	for i in _frames:
		print("R89B %s t=%d y=%.6f hits=%d" % [arm, i + 1, ys[i], hs[i]])
	_it("ring", _poly2str(ring))
	_it("tps", "%d frames=%d" % [Engine.physics_ticks_per_second, _frames])
	_it("drop_center", "y=%.4f y6=%.6f vel=%.4f,%.4f hits=%d" % [ys[_frames - 1], ys[_frames - 1],
		b.linear_velocity.x, b.linear_velocity.y, hs[_frames - 1]])
	_pass()

func _a_ringsync() -> void:
	var ring := Geometry2D.clip_polygons(_sq(0, 0, 40), _sq(0, 0, 10))
	var st := StaticBody2D.new()
	var pol := CollisionPolygon2D.new()
	pol.polygon = ring[0]
	st.add_child(pol)
	root.add_child(st)
	var b := _body(0, -60)
	root.add_child(b)
	await physics_frame
	var guard := 0
	while b.linear_velocity == Vector2.ZERO and guard < 10:
		guard += 1
		await physics_frame
	for i in _frames - 1:
		await physics_frame
	_it("guard", "%d" % guard)
	_it("ring", _poly2str(ring))
	_it("tps", "%d frames=%d" % [Engine.physics_ticks_per_second, _frames])
	_it("drop_center", "y=%.4f y6=%.6f vel=%.4f,%.4f hits=%d" % [b.global_position.y,
		b.global_position.y, b.linear_velocity.x, b.linear_velocity.y, _hits(b)])
	_pass()
