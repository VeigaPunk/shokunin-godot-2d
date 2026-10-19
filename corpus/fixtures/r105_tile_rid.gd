extends SceneTree
# r105 — TileMapLayer body-RID attribution lattice.
# Measures has_body_rid() / get_coords_for_body_rid() against the RID the docs
# prescribe: KinematicCollision2D.get_collider_rid() from a real tile
# collision. The r92 `physics` arm probed the same methods with the MOVING
# body's own RID (probe.get_rid()); arm `wrongrid` reproduces that argument
# error as a paired negative control inside one collision session.
# Arms:
#   exact     physics_quadrant_size=1 — attribution is exact-cell
#   chunked   default quadrant 16 — attribution is quadrant-level
#   kinematic use_kinematic_bodies=1 — RID still resolves through a collision
#   wrongrid  collider RID (positive) vs probe.get_rid() (negative) paired
# PASS conditions are hard-checked where the docs pin behavior (exact-cell
# equality at quadrant 1, has_body_rid truth table); chunked coords are
# measured and pinned by the PASS line.

var arm := ""
var _items: PackedStringArray = []

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")

func _it(key: String, value: String) -> void:
	_items.append("%s=%s" % [key, value])
	print("R105 %s %s=%s" % [arm, key, value])

func _pass() -> void:
	print("PASS r105_tile_rid %s %s" % [arm, " ".join(_items)])
	quit()

func _fail(reason: String) -> void:
	print("FAIL r105_tile_rid %s reason=%s" % [arm, reason])
	quit(1)

func _v2i(p: Vector2i) -> String:
	return "%d,%d" % [p.x, p.y]

func _b(v: bool) -> String:
	return "1" if v else "0"

# TileSet with one 16x16 atlas tile carrying a full-cell collision square on
# physics layer 0; a TileMapLayer at the given physics_quadrant_size; and a
# 8x8 CharacterBody2D probe. Returns the parts the arms need.
func _mk_scene(quad: int, kinematic: bool = false) -> Dictionary:
	var img := Image.create_empty(16, 16, false, Image.FORMAT_RGBA8)
	img.fill(Color(1, 1, 1, 1))
	var tex := ImageTexture.create_from_image(img)
	var ts := TileSet.new()
	ts.tile_size = Vector2i(16, 16)
	ts.add_physics_layer()
	var src := TileSetAtlasSource.new()
	src.texture = tex
	src.texture_region_size = Vector2i(16, 16)
	src.create_tile(Vector2i(0, 0))
	var sid := ts.add_source(src)
	# TileData.physics is sized when the source is attached to the TileSet;
	# writing the polygon before add_source errors on p_layer_id bounds.
	var td := src.get_tile_data(Vector2i(0, 0), 0)
	td.set_collision_polygons_count(0, 1)
	td.set_collision_polygon_points(0, 0,
		PackedVector2Array([Vector2(-8, -8), Vector2(8, -8), Vector2(8, 8), Vector2(-8, 8)]))
	var layer := TileMapLayer.new()
	layer.tile_set = ts
	layer.physics_quadrant_size = quad
	layer.use_kinematic_bodies = kinematic
	root.add_child(layer)
	var probe := CharacterBody2D.new()
	var cs := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = Vector2(8, 8)
	cs.shape = shape
	probe.add_child(cs)
	root.add_child(probe)
	return {"layer": layer, "sid": sid, "probe": probe}

# Drops the probe above `cell` and performs a REAL (non-test) downward move so
# the returned KinematicCollision2D is a delivered collision whose
# get_collider_rid() is the tile body's RID.
func _hit_at(probe: CharacterBody2D, cell: Vector2i) -> KinematicCollision2D:
	probe.position = Vector2(cell.x * 16 + 8, -6)
	await physics_frame
	return probe.move_and_collide(Vector2(0, 20))

# Collision -> RID -> has_body_rid / get_coords_for_body_rid readback.
# Hard-fails on a missed drop or an invalid/untracked collider RID; the coords
# value itself is only recorded (per-arm callers pin or check it).
func _rid_read(layer: TileMapLayer, hit: KinematicCollision2D, key: String) -> Vector2i:
	if hit == null:
		_fail("%s_no_hit" % key)
		return Vector2i.ZERO
	_it("%s_is_layer" % key, _b(hit.get_collider() == layer))
	_it("%s_collider_class" % key, hit.get_collider().get_class())
	var rid: RID = hit.get_collider_rid()
	if not rid.is_valid():
		_fail("%s_invalid_rid" % key)
		return Vector2i.ZERO
	if not layer.has_body_rid(rid):
		_fail("%s_untracked" % key)
		return Vector2i.ZERO
	_it("%s_has" % key, "1")
	var coords := layer.get_coords_for_body_rid(rid)
	_it("%s_coords" % key, _v2i(coords))
	return coords

# --- arms -------------------------------------------------------------------

func _exact() -> void:
	var d := _mk_scene(1)
	var layer: TileMapLayer = d["layer"]
	var sid: int = d["sid"]
	var probe: CharacterBody2D = d["probe"]
	_it("quad", str(layer.physics_quadrant_size))
	for c in [Vector2i(5, 0), Vector2i(21, 0)]:
		layer.set_cell(c, sid, Vector2i(0, 0), 0)
	await physics_frame
	await physics_frame
	var c5 := _rid_read(layer, await _hit_at(probe, Vector2i(5, 0)), "c5")
	if c5 != Vector2i(5, 0):
		_fail("c5_coords_%s" % _v2i(c5))
		return
	var c21 := _rid_read(layer, await _hit_at(probe, Vector2i(21, 0)), "c21")
	if c21 != Vector2i(21, 0):
		_fail("c21_coords_%s" % _v2i(c21))
		return
	_pass()

func _chunked() -> void:
	var d := _mk_scene(16)
	var layer: TileMapLayer = d["layer"]
	var sid: int = d["sid"]
	var probe: CharacterBody2D = d["probe"]
	_it("quad", str(layer.physics_quadrant_size))
	# (5,0) and (15,0) share physics quadrant (0,0); (21,0) is in quadrant
	# (1,0). Same-quadrant attribution must agree, cross-quadrant must not.
	for c in [Vector2i(5, 0), Vector2i(15, 0), Vector2i(21, 0)]:
		layer.set_cell(c, sid, Vector2i(0, 0), 0)
	await physics_frame
	await physics_frame
	var c5 := _rid_read(layer, await _hit_at(probe, Vector2i(5, 0)), "c5")
	var c15 := _rid_read(layer, await _hit_at(probe, Vector2i(15, 0)), "c15")
	var c21 := _rid_read(layer, await _hit_at(probe, Vector2i(21, 0)), "c21")
	if c5 != c15:
		_fail("same_quadrant_diverged_%s_%s" % [_v2i(c5), _v2i(c15)])
		return
	if c5 == c21:
		_fail("cross_quadrant_collapsed")
		return
	_it("same_quad_agree", "1")
	_it("cross_quad_diverge", "1")
	_pass()

func _kinematic() -> void:
	var d := _mk_scene(1, true)
	var layer: TileMapLayer = d["layer"]
	var sid: int = d["sid"]
	var probe: CharacterBody2D = d["probe"]
	_it("quad", str(layer.physics_quadrant_size))
	_it("kinematic_use", _b(layer.use_kinematic_bodies))
	layer.set_cell(Vector2i(5, 0), sid, Vector2i(0, 0), 0)
	await physics_frame
	await physics_frame
	var c5 := _rid_read(layer, await _hit_at(probe, Vector2i(5, 0)), "c5")
	if c5 != Vector2i(5, 0):
		_fail("c5_coords_%s" % _v2i(c5))
		return
	_pass()

func _wrongrid() -> void:
	var d := _mk_scene(1)
	var layer: TileMapLayer = d["layer"]
	var sid: int = d["sid"]
	var probe: CharacterBody2D = d["probe"]
	layer.set_cell(Vector2i(5, 0), sid, Vector2i(0, 0), 0)
	await physics_frame
	await physics_frame
	# positive control first: the doc-prescribed collider RID resolves.
	var hit := await _hit_at(probe, Vector2i(5, 0))
	var c5 := _rid_read(layer, hit, "c5")
	if c5 != Vector2i(5, 0):
		_fail("c5_coords_%s" % _v2i(c5))
		return
	# negative control: the moving body's own RID (what the r92 physics arm
	# measured) is not a tile body RID — has=false, coords falls back to 0,0.
	var own: RID = probe.get_rid()
	if layer.has_body_rid(own):
		_fail("own_rid_tracked")
		return
	_it("own_has", "0")
	var own_coords := layer.get_coords_for_body_rid(own)
	_it("own_coords", _v2i(own_coords))
	if own_coords != Vector2i(0, 0):
		_fail("own_coords_%s" % _v2i(own_coords))
		return
	_pass()

func _run() -> void:
	print("arm=%s" % arm)
	if arm == "":
		_fail("empty_arm")
		return
	var watchdog := create_timer(20.0)
	watchdog.timeout.connect(func() -> void:
		print("FAIL r105_tile_rid %s reason=watchdog" % arm)
		quit(1))
	match arm:
		"exact":
			_exact()
		"chunked":
			_chunked()
		"kinematic":
			_kinematic()
		"wrongrid":
			_wrongrid()
		_:
			_fail("unknown_arm")
