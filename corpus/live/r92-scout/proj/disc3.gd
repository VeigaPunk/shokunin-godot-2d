extends SceneTree
var arm := ""
func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")
func _v2i(p: Vector2i) -> String:
	return "%d,%d" % [p.x, p.y]
func _b(v: bool) -> String:
	return "1" if v else "0"
func _run() -> void:
	print("arm=%s" % arm)
	var img := Image.create_empty(32, 32, false, Image.FORMAT_RGBA8)
	img.fill(Color(1, 1, 1, 1))
	var tex := ImageTexture.create_from_image(img)
	var ts := TileSet.new()
	ts.tile_size = Vector2i(16, 16)
	var src := TileSetAtlasSource.new()
	src.texture = tex
	src.texture_region_size = Vector2i(16, 16)
	src.create_tile(Vector2i(0, 0))
	var sid := ts.add_source(src)
	ts.add_physics_layer()
	var td := src.get_tile_data(Vector2i(0, 0), 0)
	td.set_collision_polygons_count(0, 1)
	td.set_collision_polygon_points(0, 0, PackedVector2Array([Vector2(-8, -8), Vector2(8, -8), Vector2(8, 8), Vector2(-8, 8)]))
	var layer := TileMapLayer.new()
	layer.tile_set = ts
	layer.use_kinematic_bodies = true
	root.add_child(layer)
	for x in range(0, 10):
		layer.set_cell(Vector2i(x, 4), sid, Vector2i(0, 0), 0)
	var body := RigidBody2D.new()
	var cs := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = Vector2(8, 8)
	cs.shape = shape
	body.add_child(cs)
	body.position = Vector2(8, -40)
	root.add_child(body)
	for i in range(0, 90):
		await physics_frame
		if i % 20 == 0 or i == 89:
			print("R92 kin i=%d pos=%.4f,%.4f has=%s coords=%s lin=%.4f,%.4f" % [
				i, body.position.x, body.position.y, _b(layer.has_body_rid(body.get_rid())),
				_v2i(layer.get_coords_for_body_rid(body.get_rid())),
				body.linear_velocity.x, body.linear_velocity.y])
	print("PASS disc3 kinematic_fall")
	quit(0)
