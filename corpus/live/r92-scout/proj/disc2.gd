extends SceneTree
# r92 discovery round 2 — kinematic body tracking, erased-marker encoding,
# update_internals symmetry, quadrant re-partition.

var arm := ""

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")

func _v2(p: Vector2) -> String:
	return "%.4f,%.4f" % [p.x, p.y]

func _v2i(p: Vector2i) -> String:
	return "%d,%d" % [p.x, p.y]

func _ints(arr) -> String:
	var parts: PackedStringArray = []
	for v in arr:
		parts.append(str(v))
	return "[%s]" % ",".join(parts)

func _coords(arr: Array) -> String:
	var parts: PackedStringArray = []
	for c in arr:
		parts.append(_v2i(c))
	return "n%d[%s]" % [arr.size(), ";".join(parts)]

func _b(v: bool) -> String:
	return "1" if v else "0"

func _mk(tex: ImageTexture) -> Dictionary:
	var ts := TileSet.new()
	ts.tile_size = Vector2i(16, 16)
	var src := TileSetAtlasSource.new()
	src.texture = tex
	src.texture_region_size = Vector2i(16, 16)
	src.create_tile(Vector2i(0, 0))
	src.create_tile(Vector2i(1, 0))
	var sid := ts.add_source(src)
	return {"ts": ts, "src": src, "sid": sid}

func _run() -> void:
	print("arm=%s" % arm)
	var img := Image.create_empty(32, 32, false, Image.FORMAT_RGBA8)
	img.fill(Color(1, 1, 1, 1))
	var tex := ImageTexture.create_from_image(img)
	match arm:
		"kinematic":
			await _kinematic(tex)
		"erased":
			_erased(tex)
		"internals":
			await _internals(tex)
		"quadpart":
			await _quadpart(tex)
		_:
			print("FAIL disc2 unknown_arm %s" % arm)
			quit(1)

func _kinematic(tex: ImageTexture) -> void:
	var d := _mk(tex)
	var ts: TileSet = d["ts"]
	var sid: int = d["sid"]
	ts.add_physics_layer()
	var td := (d["src"] as TileSetAtlasSource).get_tile_data(Vector2i(0, 0), 0)
	td.set_collision_polygons_count(0, 1)
	td.set_collision_polygon_points(0, 0, PackedVector2Array([Vector2(-8, -8), Vector2(8, -8), Vector2(8, 8), Vector2(-8, 8)]))
	var layer := TileMapLayer.new()
	layer.tile_set = ts
	root.add_child(layer)
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	layer.set_cell(Vector2i(1, 0), sid, Vector2i(0, 0), 0)
	var body := CharacterBody2D.new()
	var cs := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = Vector2(8, 8)
	cs.shape = shape
	body.add_child(cs)
	body.position = Vector2(8, 8)
	root.add_child(body)
	await physics_frame
	await physics_frame
	print("R92 kinematic use_kinematic=%s" % _b(layer.use_kinematic_bodies))
	print("R92 kinematic has_body_default=%s coords_default=%s" % [_b(layer.has_body_rid(body.get_rid())), _v2i(layer.get_coords_for_body_rid(body.get_rid()))])
	layer.use_kinematic_bodies = true
	await physics_frame
	print("R92 kinematic has_body_kin_on_same=%s" % _b(layer.has_body_rid(body.get_rid())))
	await physics_frame
	print("R92 kinematic has_body_kin_on_f1=%s" % _b(layer.has_body_rid(body.get_rid())))
	await physics_frame
	print("R92 kinematic has_body_kin_on_f2=%s coords=%s" % [_b(layer.has_body_rid(body.get_rid())), _v2i(layer.get_coords_for_body_rid(body.get_rid()))])
	# move the body onto the second cell
	body.position = Vector2(24, 8)
	await physics_frame
	await physics_frame
	print("R92 kinematic after_move_coords=%s" % _v2i(layer.get_coords_for_body_rid(body.get_rid())))
	# leave the tilemap entirely
	body.position = Vector2(400, 400)
	await physics_frame
	await physics_frame
	print("R92 kinematic off_map_coords=%s has=%s" % [_v2i(layer.get_coords_for_body_rid(body.get_rid())), _b(layer.has_body_rid(body.get_rid()))])
	quit(0)

func _erased(tex: ImageTexture) -> void:
	var d := _mk(tex)
	var ts: TileSet = d["ts"]
	var sid: int = d["sid"]
	var layer := TileMapLayer.new()
	layer.tile_set = ts
	root.add_child(layer)
	print("R92 erased empty_len=%d" % layer.tile_map_data.size())
	layer.set_cell(Vector2i(1, 1), sid, Vector2i(0, 0), 0)
	print("R92 erased after_set len=%d bytes=%s" % [layer.tile_map_data.size(), _ints(Array(layer.tile_map_data))])
	layer.erase_cell(Vector2i(1, 1))
	print("R92 erased after_erase len=%d bytes=%s used=%s" % [layer.tile_map_data.size(), _ints(Array(layer.tile_map_data)), _coords(layer.get_used_cells())])
	layer.set_cell(Vector2i(1, 1), sid, Vector2i(0, 0), 0)
	print("R92 erased re_set len=%d bytes=%s used=%s" % [layer.tile_map_data.size(), _ints(Array(layer.tile_map_data)), _coords(layer.get_used_cells())])
	layer.clear()
	print("R92 erased after_clear len=%d bytes=%s used=%s" % [layer.tile_map_data.size(), _ints(Array(layer.tile_map_data)), _coords(layer.get_used_cells())])
	layer.set_cell(Vector2i(5, 5), sid, Vector2i(0, 0), 0)
	print("R92 erased after_clear_set len=%d bytes=%s used=%s" % [layer.tile_map_data.size(), _ints(Array(layer.tile_map_data)), _coords(layer.get_used_cells())])
	print("PASS disc2 erased")
	quit(0)

func _internals(tex: ImageTexture) -> void:
	var d := _mk(tex)
	var ts: TileSet = d["ts"]
	var sid: int = d["sid"]
	ts.add_physics_layer()
	var td := (d["src"] as TileSetAtlasSource).get_tile_data(Vector2i(0, 0), 0)
	td.set_collision_polygons_count(0, 1)
	td.set_collision_polygon_points(0, 0, PackedVector2Array([Vector2(-8, -8), Vector2(8, -8), Vector2(8, 8), Vector2(-8, 8)]))
	var layer := TileMapLayer.new()
	layer.tile_set = ts
	root.add_child(layer)
	var probe := CharacterBody2D.new()
	var cs := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = Vector2(8, 8)
	cs.shape = shape
	probe.add_child(cs)
	probe.position = Vector2(8, -6)
	root.add_child(probe)
	await physics_frame
	await physics_frame
	print("R92 internals empty=%s" % _mc(probe))
	# set + update_internals, same frame
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	layer.update_internals()
	print("R92 internals set_update_same=%s" % _mc(probe))
	await physics_frame
	print("R92 internals set_update_f1=%s" % _mc(probe))
	# erase + update_internals, same frame
	layer.erase_cell(Vector2i(0, 0))
	layer.update_internals()
	print("R92 internals erase_update_same=%s" % _mc(probe))
	await physics_frame
	print("R92 internals erase_update_f1=%s" % _mc(probe))
	# set without update, same frame (control)
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	print("R92 internals set_plain_same=%s" % _mc(probe))
	await physics_frame
	print("R92 internals set_plain_f1=%s" % _mc(probe))
	# set_cell then update_internals on the NEXT frame
	layer.erase_cell(Vector2i(0, 0))
	await physics_frame
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	await physics_frame
	print("R92 internals set_then_update_next=%s" % _mc(probe))
	# notify + update together
	layer.erase_cell(Vector2i(0, 0))
	layer.notify_runtime_tile_data_update()
	layer.update_internals()
	print("R92 internals erase_notify_update_same=%s" % _mc(probe))
	await physics_frame
	print("R92 internals erase_notify_update_f1=%s" % _mc(probe))
	quit(0)

func _mc(probe: CharacterBody2D) -> String:
	var hit := probe.move_and_collide(Vector2(0, 20), true)
	return "null" if hit == null else "hit"

func _quadpart(tex: ImageTexture) -> void:
	var d := _mk(tex)
	var ts: TileSet = d["ts"]
	var sid: int = d["sid"]
	ts.add_physics_layer()
	var td := (d["src"] as TileSetAtlasSource).get_tile_data(Vector2i(0, 0), 0)
	td.set_collision_polygons_count(0, 1)
	td.set_collision_polygon_points(0, 0, PackedVector2Array([Vector2(-8, -8), Vector2(8, -8), Vector2(8, 8), Vector2(-8, 8)]))
	var layer := TileMapLayer.new()
	layer.tile_set = ts
	root.add_child(layer)
	# two cells in the SAME quadrant (0..15) and two in another
	for c in [Vector2i(0, 0), Vector2i(15, 0), Vector2i(16, 0), Vector2i(40, 0)]:
		layer.set_cell(c, sid, Vector2i(0, 0), 0)
	var probe := CharacterBody2D.new()
	var cs := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = Vector2(8, 8)
	cs.shape = shape
	probe.add_child(cs)
	root.add_child(probe)
	await physics_frame
	await physics_frame
	for c in [Vector2i(0, 0), Vector2i(15, 0), Vector2i(16, 0), Vector2i(40, 0)]:
		probe.position = Vector2(c.x * 16 + 8, -6)
		await physics_frame
		print("R92 quadpart quad16 cell=%s %s" % [_v2i(c), _mc(probe)])
	layer.set_physics_quadrant_size(1)
	await physics_frame
	await physics_frame
	for c in [Vector2i(0, 0), Vector2i(15, 0), Vector2i(16, 0), Vector2i(40, 0)]:
		probe.position = Vector2(c.x * 16 + 8, -6)
		await physics_frame
		print("R92 quadpart quad1 cell=%s %s" % [_v2i(c), _mc(probe)])
	quit(0)
