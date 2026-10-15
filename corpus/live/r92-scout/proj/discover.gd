extends SceneTree
# r92-scout discovery micro-probe — TileMapLayer/TileSet runtime lattice.
# One arm per process:
#   godot --headless --path proj --script res://discover.gd -- --arm=<name> [--frames=N]
# Prints `R92 <arm> <key>=<value>` diagnostics and one final
# `PASS discover <arm> <key>=<value> ...` line. No RIDs/object ids/pointers.

var arm := ""
var _items: PackedStringArray = []

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")

func _it(key: String, value: String) -> void:
	_items.append("%s=%s" % [key, value])
	print("R92 %s %s=%s" % [arm, key, value])

func _pass() -> void:
	print("PASS discover %s %s" % [arm, " ".join(_items)])
	quit()

func _fail(reason: String) -> void:
	print("FAIL discover %s reason=%s" % [arm, reason])
	quit(1)

func _v2(p: Vector2) -> String:
	return "%.4f,%.4f" % [p.x, p.y]

func _v2i(p: Vector2i) -> String:
	return "%d,%d" % [p.x, p.y]

func _coords(arr: Array) -> String:
	var parts: PackedStringArray = []
	for c in arr:
		parts.append(_v2i(c))
	return "n%d[%s]" % [arr.size(), ";".join(parts)]

func _b(v: bool) -> String:
	return "1" if v else "0"

# --- shared construction helpers -------------------------------------------------

func _mk_texture(w: int, h: int) -> ImageTexture:
	var img := Image.create_empty(w, h, false, Image.FORMAT_RGBA8)
	img.fill(Color(1, 1, 1, 1))
	return ImageTexture.create_from_image(img)

# A TileSet with one atlas source (32x32 texture, 16x16 regions => 4 tiles),
# 1 physics layer, 1 custom data layer ("hp":int), 1 navigation layer, 1 terrain set.
func _mk_tileset(tex: ImageTexture) -> Dictionary:
	var ts := TileSet.new()
	ts.tile_size = Vector2i(16, 16)
	var src := TileSetAtlasSource.new()
	src.texture = tex
	src.texture_region_size = Vector2i(16, 16)
	src.create_tile(Vector2i(0, 0))
	src.create_tile(Vector2i(1, 0))
	src.create_tile(Vector2i(0, 1))
	src.create_tile(Vector2i(1, 1))
	var sid := ts.add_source(src)
	return {"ts": ts, "src": src, "sid": sid}

func _mk_layer(ts: TileSet) -> TileMapLayer:
	var layer := TileMapLayer.new()
	layer.tile_set = ts
	return layer

func _run() -> void:
	print("arm=%s" % arm)
	if arm == "":
		_fail("empty_arm")
		return
	match arm:
		"census":
			_census()
		"atlas":
			_atlas()
		"cells":
			_cells()
		"custom":
			_custom()
		"physics":
			await _physics()
		"timing":
			await _timing()
		"terrain":
			_terrain()
		"nav":
			_nav()
		"pattern":
			_pattern()
		"misc":
			_misc()
		"neighbors":
			_neighbors()
		"flip":
			_flip()
		"fixinvalid":
			_fixinvalid()
		"dataarray":
			_dataarray()
		"mappattern":
			_mappattern()
		"quadrant":
			await _quadrant()
		"srcids":
			_srcids()
		"nullts":
			_nullts()
		_:
			_fail("unknown_arm")

# --- arm: census ----------------------------------------------------------------

func _census() -> void:
	for cls in ["TileMapLayer", "TileSet", "TileSetAtlasSource", "TileData",
			"TileSetSource", "TileMapPattern", "TileSetScenesCollectionSource"]:
		var methods: Array = ClassDB.class_get_method_list(cls, true)
		var names: PackedStringArray = []
		for m in methods:
			names.append(m["name"])
		names.sort()
		_it("m_%s" % cls, "n%d[%s]" % [names.size(), ",".join(names)])
		var props: Array = ClassDB.class_get_property_list(cls, true)
		var pnames: PackedStringArray = []
		for p in props:
			pnames.append("%s:%d" % [p["name"], p["type"]])
		pnames.sort()
		_it("p_%s" % cls, "n%d[%s]" % [pnames.size(), ",".join(pnames)])
	var ts := TileSet.new()
	_it("ts_defaults", "tile_size=%s physics_layers=%d nav_layers=%d custom_data_layers=%d terrain_sets=%d sources=%d tile_shape=%d" % [
		_v2i(ts.tile_size), ts.get_physics_layers_count(), ts.get_navigation_layers_count(),
		ts.get_custom_data_layers_count(), ts.get_terrain_sets_count(), ts.get_source_count(),
		ts.tile_shape])
	var layer := TileMapLayer.new()
	_it("layer_defaults", "enabled=%s collision_enabled=%s nav_enabled=%s use_kinematic=%s phys_quad=%d rend_quad=%d col_vis=%d nav_vis=%d y_sort_origin=%d x_draw_rev=%s occl=%s" % [
		_b(layer.enabled), _b(layer.collision_enabled), _b(layer.navigation_enabled),
		_b(layer.use_kinematic_bodies), layer.physics_quadrant_size, layer.rendering_quadrant_size,
		layer.collision_visibility_mode, layer.navigation_visibility_mode,
		layer.y_sort_origin, _b(layer.x_draw_order_reversed),
		_b(layer.occlusion_enabled)])
	var src := TileSetAtlasSource.new()
	_it("atlas_defaults", "region=%s margins=%s separation=%s tiles=%d" % [
		_v2i(src.texture_region_size), _v2i(src.margins), _v2i(src.separation),
		src.get_tiles_count()])
	_it("enum_terrainset", "MATCH_CORNERS_AND_SIDES=%d MATCH_CORNERS=%d MATCH_SIDES=%d" % [
		TileSet.TERRAIN_MODE_MATCH_CORNERS_AND_SIDES, TileSet.TERRAIN_MODE_MATCH_CORNERS,
		TileSet.TERRAIN_MODE_MATCH_SIDES])
	_it("enum_tileshape", "SQUARE=%d ISOMETRIC=%d HALF_OFFSET_SQUARE=%d HEXAGON=%d" % [
		TileSet.TILE_SHAPE_SQUARE, TileSet.TILE_SHAPE_ISOMETRIC,
		TileSet.TILE_SHAPE_HALF_OFFSET_SQUARE, TileSet.TILE_SHAPE_HEXAGON])
	_it("enum_neighbor", "RIGHT_SIDE=%d RIGHT_CORNER=%d BOTTOM_RIGHT_SIDE=%d BOTTOM_RIGHT_CORNER=%d" % [
		TileSet.CELL_NEIGHBOR_RIGHT_SIDE, TileSet.CELL_NEIGHBOR_RIGHT_CORNER,
		TileSet.CELL_NEIGHBOR_BOTTOM_RIGHT_SIDE, TileSet.CELL_NEIGHBOR_BOTTOM_RIGHT_CORNER])
	_it("layer_has_methods", "notify_runtime_tile_data_update=%s update_internals=%s get_coords_for_body_rid=%s get_pattern=%s set_pattern=%s set_cells_terrain_connect=%s set_cells_terrain_path=%s get_surrounding_cells=%s get_used_cells_by_id=%s" % [
		_b(layer.has_method("notify_runtime_tile_data_update")), _b(layer.has_method("update_internals")),
		_b(layer.has_method("get_coords_for_body_rid")), _b(layer.has_method("get_pattern")),
		_b(layer.has_method("set_pattern")), _b(layer.has_method("set_cells_terrain_connect")),
		_b(layer.has_method("set_cells_terrain_path")), _b(layer.has_method("get_surrounding_cells")),
		_b(layer.has_method("get_used_cells_by_id"))])
	_pass()

# --- arm: atlas -----------------------------------------------------------------

func _atlas() -> void:
	var ts := TileSet.new()
	var tex := _mk_texture(32, 32)
	var src := TileSetAtlasSource.new()
	src.texture = tex
	_it("region_default", _v2i(src.texture_region_size))
	var sid := ts.add_source(src)
	_it("sid_first", str(sid))
	_it("source_count", str(ts.get_source_count()))
	_it("has_source_0", _b(ts.has_source(0)))
	_it("src_type", str(ts.get_source(sid).get_class()))
	# create tiles
	src.create_tile(Vector2i(0, 0))
	src.create_tile(Vector2i(1, 0))
	_it("tiles_after_2", str(src.get_tiles_count()))
	_it("has_tile_00", _b(src.has_tile(Vector2i(0, 0))))
	_it("has_tile_10", _b(src.has_tile(Vector2i(1, 0))))
	_it("has_tile_11", _b(src.has_tile(Vector2i(1, 1))))
	var ids: PackedStringArray = []
	for i in src.get_tiles_count():
		ids.append(_v2i(src.get_tile_id(i)))
	_it("tiles_list", "n%d[%s]" % [ids.size(), ";".join(ids)])
	# duplicate create_tile call
	src.create_tile(Vector2i(0, 0))
	_it("tiles_after_dup", str(src.get_tiles_count()))
	# alternative tiles
	var alt := src.create_alternative_tile(Vector2i(0, 0))
	_it("alt_id", str(alt))
	_it("alt_count", str(src.get_alternative_tiles_count(Vector2i(0, 0))))
	var alts: PackedStringArray = []
	for i in src.get_alternative_tiles_count(Vector2i(0, 0)):
		alts.append(str(src.get_alternative_tile_id(Vector2i(0, 0), i)))
	_it("alt_list", "n%d[%s]" % [alts.size(), ";".join(alts)])
	_it("alt_tile_id_of_alt", _v2i(src.get_tile_id(0)))
	_it("alt_has_alt_0", _b(src.has_alternative_tile(Vector2i(0, 0), 0)))
	_it("alt_has_alt_1", _b(src.has_alternative_tile(Vector2i(0, 0), 1)))
	_it("alt_has_alt_7", _b(src.has_alternative_tile(Vector2i(0, 0), 7)))
	# tile data
	var td := src.get_tile_data(Vector2i(0, 0), 0)
	_it("td_class", td.get_class() if td else "null")
	var td_alt := src.get_tile_data(Vector2i(0, 0), alt)
	_it("td_alt_distinct", _b(td != null and td_alt != null and td != td_alt))
	# out-of-texture tile
	src.create_tile(Vector2i(9, 9))
	_it("tile_99_created", _b(src.has_tile(Vector2i(9, 9))))
	# get_tile_data on a non-existent tile
	var td_none := src.get_tile_data(Vector2i(5, 5), 0)
	_it("td_missing", td_none.get_class() if td_none else "null")
	# remove
	src.remove_tile(Vector2i(1, 0))
	_it("tiles_after_remove", str(src.get_tiles_count()))
	_it("has_tile_10_after", _b(src.has_tile(Vector2i(1, 0))))
	# texture swap / null texture
	var src2 := TileSetAtlasSource.new()
	var sid2 := ts.add_source(src2)
	_it("sid2", str(sid2))
	_it("src2_null_texture", _b(src2.texture == null))
	var td2 := src2.get_tile_data(Vector2i(0, 0), 0)
	_it("src2_td", td2.get_class() if td2 else "null")
	# explicit source id
	var src3 := TileSetAtlasSource.new()
	src3.texture = tex
	var sid3 := ts.add_source(src3, 7)
	_it("sid3_explicit", str(sid3))
	_it("source_count_after_explicit", str(ts.get_source_count()))
	_it("sources_list", str(ts.get_source_id_list()))
	_pass()

# --- arm: cells -----------------------------------------------------------------

func _cells() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var ts: TileSet = d["ts"]
	var sid: int = d["sid"]
	var layer := _mk_layer(ts)
	root.add_child(layer)
	_it("empty_used", _coords(layer.get_used_cells()))
	_it("empty_rect", str(layer.get_used_rect()))
	_it("empty_source", str(layer.get_cell_source_id(Vector2i(0, 0))))
	_it("empty_atlas", _v2i(layer.get_cell_atlas_coords(Vector2i(0, 0))))
	_it("empty_alt", str(layer.get_cell_alternative_tile(Vector2i(0, 0))))
	_it("empty_td", "null" if layer.get_cell_tile_data(Vector2i(0, 0)) == null else "obj")
	# set cells
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	layer.set_cell(Vector2i(3, 2), sid, Vector2i(1, 0), 0)
	layer.set_cell(Vector2i(-2, -1), sid, Vector2i(0, 1), 0)
	_it("used_after_3", _coords(layer.get_used_cells()))
	_it("rect_after_3", str(layer.get_used_rect()))
	_it("src_3_2", str(layer.get_cell_source_id(Vector2i(3, 2))))
	_it("atlas_3_2", _v2i(layer.get_cell_atlas_coords(Vector2i(3, 2))))
	_it("td_3_2", "null" if layer.get_cell_tile_data(Vector2i(3, 2)) == null else "obj")
	# same-frame readback of tile data after a write
	layer.set_cell(Vector2i(9, 9), sid, Vector2i(0, 0), 0)
	_it("same_frame_td", "null" if layer.get_cell_tile_data(Vector2i(9, 9)) == null else "obj")
	# erase via source -1
	layer.set_cell(Vector2i(3, 2), -1, Vector2i(-1, -1), -1)
	_it("erase_src", str(layer.get_cell_source_id(Vector2i(3, 2))))
	_it("erase_used_n", str(layer.get_used_cells().size()))
	# erase_cell
	layer.erase_cell(Vector2i(0, 0))
	_it("erase_used_n2", str(layer.get_used_cells().size()))
	_it("erase_absent_ok", _b(layer.get_cell_source_id(Vector2i(0, 0)) == -1))
	# invalid source id
	layer.set_cell(Vector2i(5, 5), 42, Vector2i(0, 0), 0)
	_it("bad_src_readback", str(layer.get_cell_source_id(Vector2i(5, 5))))
	_it("bad_src_used_has", _b(layer.get_used_cells().has(Vector2i(5, 5))))
	# invalid atlas coords on a valid source
	layer.set_cell(Vector2i(6, 6), sid, Vector2i(9, 9), 0)
	_it("bad_atlas_readback", _v2i(layer.get_cell_atlas_coords(Vector2i(6, 6))))
	_it("bad_atlas_td", "null" if layer.get_cell_tile_data(Vector2i(6, 6)) == null else "obj")
	# get_used_cells_by_id
	_it("used_by_id_src", _coords(layer.get_used_cells_by_id(sid)))
	_it("used_by_id_bad", _coords(layer.get_used_cells_by_id(42)))
	# clear
	layer.clear()
	_it("clear_used_n", str(layer.get_used_cells().size()))
	_it("clear_rect", str(layer.get_used_rect()))
	# mapping helpers
	_it("map_to_local_1_1", _v2(layer.map_to_local(Vector2i(1, 1))))
	_it("map_to_local_neg", _v2(layer.map_to_local(Vector2i(-1, -1))))
	_it("local_to_map_16_16", _v2i(layer.local_to_map(Vector2(16, 16))))
	_it("local_to_map_8_8", _v2i(layer.local_to_map(Vector2(8, 8))))
	_it("local_to_map_neg", _v2i(layer.local_to_map(Vector2(-1, -1))))
	_it("surrounding", _coords(layer.get_surrounding_cells(Vector2i(0, 0))))
	_it("surrounding_n", str(layer.get_surrounding_cells(Vector2i(0, 0)).size()))
	_pass()

# --- arm: custom ----------------------------------------------------------------

func _custom() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var ts: TileSet = d["ts"]
	var src: TileSetAtlasSource = d["src"]
	var sid: int = d["sid"]
	var layer := _mk_layer(ts)
	root.add_child(layer)
	_it("cd_layers_0", str(ts.get_custom_data_layers_count()))
	ts.add_custom_data_layer()
	ts.set_custom_data_layer_name(0, "hp")
	ts.set_custom_data_layer_type(0, TYPE_INT)
	_it("cd_layers_1", str(ts.get_custom_data_layers_count()))
	_it("cd_name_0", ts.get_custom_data_layer_name(0))
	_it("cd_type_0", str(ts.get_custom_data_layer_type(0)))
	_it("cd_index_of", str(ts.get_custom_data_layer_by_name("hp")))
	_it("cd_index_of_missing", str(ts.get_custom_data_layer_by_name("nope")))
	ts.add_custom_data_layer()
	ts.set_custom_data_layer_name(1, "tag")
	ts.set_custom_data_layer_type(1, TYPE_STRING)
	_it("cd_layers_2", str(ts.get_custom_data_layers_count()))
	var td := src.get_tile_data(Vector2i(0, 0), 0)
	_it("td_cd_default_hp", str(td.get_custom_data("hp")))
	_it("td_cd_default_tag", str(td.get_custom_data("tag")))
	td.set_custom_data("hp", 7)
	td.set_custom_data("tag", "alpha")
	_it("td_cd_hp", str(td.get_custom_data("hp")))
	_it("td_cd_tag", str(td.get_custom_data("tag")))
	# wrong-typed write (layer declared TYPE_INT)
	td.set_custom_data("hp", "not-an-int")
	_it("td_cd_hp_wrongtype", str(td.get_custom_data("hp")))
	# unregistered name write
	td.set_custom_data("ghost", 1)
	_it("td_cd_ghost", str(td.get_custom_data("ghost")))
	_it("td_cd_missing", str(td.get_custom_data("absent")))
	# readback through the layer
	layer.set_cell(Vector2i(2, 2), sid, Vector2i(0, 0), 0)
	var ctd := layer.get_cell_tile_data(Vector2i(2, 2))
	_it("layer_cd_hp", str(ctd.get_custom_data("hp")))
	_it("layer_cd_tag", str(ctd.get_custom_data("tag")))
	# index-based API
	_it("td_cd_by_index_0", str(td.get_custom_data_by_layer_id(0)))
	_it("td_cd_by_index_1", str(td.get_custom_data_by_layer_id(1)))
	# removal
	ts.remove_custom_data_layer(1)
	_it("cd_layers_after_remove", str(ts.get_custom_data_layers_count()))
	_it("cd_name_0_after", ts.get_custom_data_layer_name(0))
	_it("td_cd_tag_after_remove", str(td.get_custom_data("tag")))
	# duplicate tileset deep/shallow
	var dup: TileSet = ts.duplicate(true)
	_it("dup_cd_layers", str(dup.get_custom_data_layers_count()))
	_it("dup_cd_name", dup.get_custom_data_layer_name(0))
	_pass()

# --- arm: physics ---------------------------------------------------------------

func _physics() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var ts: TileSet = d["ts"]
	var src: TileSetAtlasSource = d["src"]
	var sid: int = d["sid"]
	_it("phys_layers_0", str(ts.get_physics_layers_count()))
	ts.add_physics_layer()
	_it("phys_layers_1", str(ts.get_physics_layers_count()))
	_it("phys_layer_defaults", "cl=%d cm=%d prio=%.4f mat_null=%s" % [
		ts.get_physics_layer_collision_layer(0), ts.get_physics_layer_collision_mask(0),
		ts.get_physics_layer_collision_priority(0),
		_b(ts.get_physics_layer_physics_material(0) == null)])
	ts.set_physics_layer_collision_layer(0, 3)
	ts.set_physics_layer_collision_mask(0, 5)
	_it("phys_layer_set", "cl=%d cm=%d" % [ts.get_physics_layer_collision_layer(0),
		ts.get_physics_layer_collision_mask(0)])
	var td := src.get_tile_data(Vector2i(0, 0), 0)
	_it("td_poly_0", str(td.get_collision_polygons_count(0)))
	td.set_collision_polygons_count(0, 1)
	td.set_collision_polygon_points(0, 0, PackedVector2Array([Vector2(-8, -8), Vector2(8, -8), Vector2(8, 8), Vector2(-8, 8)]))
	_it("td_poly_1", str(td.get_collision_polygons_count(0)))
	_it("td_poly_pts", _v2(td.get_collision_polygon_points(0, 0)[0]))
	_it("td_poly_oneshot", _b(td.is_collision_polygon_one_way(0, 0)))
	td.set_collision_polygon_one_way(0, 0, true)
	td.set_collision_polygon_one_way_margin(0, 0, 4.0)
	_it("td_poly_oneshot_set", "%s m=%.4f" % [_b(td.is_collision_polygon_one_way(0, 0)),
		td.get_collision_polygon_one_way_margin(0, 0)])
	# second layer, polygon only on layer 1
	ts.add_physics_layer()
	_it("td_poly_layer1", str(td.get_collision_polygons_count(1)))
	# layer node
	var layer := _mk_layer(ts)
	root.add_child(layer)
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	layer.set_cell(Vector2i(1, 0), sid, Vector2i(1, 0), 0)
	_it("layer_phys_quad", str(layer.physics_quadrant_size))
	_it("layer_collision_enabled", _b(layer.collision_enabled))
	# body drop: a static-collision test via a CharacterBody2D move_and_collide
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
	var hit := probe.move_and_collide(Vector2(0, 20), true)
	_it("mc_into_tile_same_frame", "null" if hit == null else "hit")
	var hit2 := probe.move_and_collide(Vector2(0, 20), true)
	_it("mc_into_tile_2nd", "null" if hit2 == null else "hit")
	if hit2 != null:
		_it("mc_collider_meta", "class=%s travel=%.4f,%.4f normal=%.4f,%.4f" % [
			hit2.get_collider().get_class(), hit2.get_travel().x, hit2.get_travel().y,
			hit2.get_normal().x, hit2.get_normal().y])
		_it("mc_collider_is_layer", _b(hit2.get_collider() == layer))
		_it("mc_local_shape", str(hit2.get_local_shape() != null))
	# collision_enabled=false
	layer.collision_enabled = false
	await physics_frame
	await physics_frame
	var hit3 := probe.move_and_collide(Vector2(0, 20), true)
	_it("mc_disabled_same_frame", "null" if hit3 == null else "hit")
	var hit4 := probe.move_and_collide(Vector2(0, 20), true)
	_it("mc_disabled_settled", "null" if hit4 == null else "hit")
	# re-enable + erase the tile under the probe
	layer.collision_enabled = true
	layer.erase_cell(Vector2i(0, 0))
	await physics_frame
	await physics_frame
	var hit5 := probe.move_and_collide(Vector2(0, 20), true)
	_it("mc_erased_tile", "null" if hit5 == null else "hit")
	# get_coords_for_body_rid / kinematic bodies
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	layer.use_kinematic_bodies = true
	await physics_frame
	await physics_frame
	var body_rid: RID = probe.get_rid()
	var coords_for := layer.get_coords_for_body_rid(body_rid)
	_it("coords_for_body", _v2i(coords_for))
	# physics space query
	var space: RID = probe.get_world_2d().space
	_it("space_valid", _b(space.is_valid()))
	_pass()

# --- arm: timing ----------------------------------------------------------------

func _timing() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var ts: TileSet = d["ts"]
	var src: TileSetAtlasSource = d["src"]
	var sid: int = d["sid"]
	ts.add_physics_layer()
	var td := src.get_tile_data(Vector2i(0, 0), 0)
	td.set_collision_polygons_count(0, 1)
	td.set_collision_polygon_points(0, 0, PackedVector2Array([Vector2(-8, -8), Vector2(8, -8), Vector2(8, 8), Vector2(-8, 8)]))
	var layer := _mk_layer(ts)
	root.add_child(layer)
	var probe := CharacterBody2D.new()
	var cs := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = Vector2(8, 8)
	cs.shape = shape
	probe.add_child(cs)
	probe.position = Vector2(8, -6)
	root.add_child(probe)
	# wait for the nodes to enter the tree and the space to pick them up
	await physics_frame
	await physics_frame
	var before := probe.move_and_collide(Vector2(0, 20), true)
	_it("pre_set_cell", "null" if before == null else "hit")
	# write the cell, then probe in the SAME frame (no physics step)
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	var same := probe.move_and_collide(Vector2(0, 20), true)
	_it("post_set_same_frame", "null" if same == null else "hit")
	var td_same := layer.get_cell_tile_data(Vector2i(0, 0))
	_it("td_same_frame", "null" if td_same == null else "obj")
	# one physics frame later
	await physics_frame
	var f1 := probe.move_and_collide(Vector2(0, 20), true)
	_it("post_set_f1", "null" if f1 == null else "hit")
	await physics_frame
	var f2 := probe.move_and_collide(Vector2(0, 20), true)
	_it("post_set_f2", "null" if f2 == null else "hit")
	await physics_frame
	var f3 := probe.move_and_collide(Vector2(0, 20), true)
	_it("post_set_f3", "null" if f3 == null else "hit")
	# explicit notify_runtime_tile_data_update
	layer.set_cell(Vector2i(3, 0), sid, Vector2i(0, 0), 0)
	layer.notify_runtime_tile_data_update()
	var n0 := probe.move_and_collide(Vector2(0, 20), true)
	_it("notify_same_frame_at_0_0", "null" if n0 == null else "hit")
	# erase timing
	layer.erase_cell(Vector2i(0, 0))
	var e_same := probe.move_and_collide(Vector2(0, 20), true)
	_it("erase_same_frame", "null" if e_same == null else "hit")
	await physics_frame
	var e_f1 := probe.move_and_collide(Vector2(0, 20), true)
	_it("erase_f1", "null" if e_f1 == null else "hit")
	await physics_frame
	var e_f2 := probe.move_and_collide(Vector2(0, 20), true)
	_it("erase_f2", "null" if e_f2 == null else "hit")
	# move the whole layer (transform) with a cell present
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	await physics_frame
	await physics_frame
	var m0 := probe.move_and_collide(Vector2(0, 20), true)
	_it("move_pre", "null" if m0 == null else "hit")
	layer.position = Vector2(200, 200)
	var m_same := probe.move_and_collide(Vector2(0, 20), true)
	_it("move_same_frame", "null" if m_same == null else "hit")
	await physics_frame
	var m_f1 := probe.move_and_collide(Vector2(0, 20), true)
	_it("move_f1", "null" if m_f1 == null else "hit")
	await physics_frame
	var m_f2 := probe.move_and_collide(Vector2(0, 20), true)
	_it("move_f2", "null" if m_f2 == null else "hit")
	_pass()

# --- arm: terrain ---------------------------------------------------------------

func _terrain() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var ts: TileSet = d["ts"]
	var src: TileSetAtlasSource = d["src"]
	var sid: int = d["sid"]
	var layer := _mk_layer(ts)
	root.add_child(layer)
	_it("terrain_sets_0", str(ts.get_terrain_sets_count()))
	ts.add_terrain_set()
	_it("terrain_sets_1", str(ts.get_terrain_sets_count()))
	_it("tset_mode_default", str(ts.get_terrain_set_mode(0)))
	ts.set_terrain_set_mode(0, TileSet.TERRAIN_MODE_MATCH_CORNERS_AND_SIDES)
	_it("terrain_count_0", str(ts.get_terrains_count(0)))
	ts.add_terrain(0)
	ts.add_terrain(0)
	_it("terrain_count_2", str(ts.get_terrains_count(0)))
	ts.set_terrain_name(0, 0, "grass")
	ts.set_terrain_name(0, 1, "dirt")
	_it("terrain_names", "%s,%s" % [ts.get_terrain_name(0, 0), ts.get_terrain_name(0, 1)])
	ts.set_terrain_color(0, 0, Color(0, 1, 0))
	_it("terrain_color", str(ts.get_terrain_color(0, 0)))
	var td := src.get_tile_data(Vector2i(0, 0), 0)
	_it("td_terrain_set_default", str(td.terrain_set))
	td.terrain_set = 0
	td.terrain = 0
	_it("td_terrain", "set=%d t=%d" % [td.terrain_set, td.terrain])
	# peering bits
	td.set_terrain_peering_bit(TileSet.CELL_NEIGHBOR_RIGHT_SIDE, 1)
	_it("td_peering_right", str(td.get_terrain_peering_bit(TileSet.CELL_NEIGHBOR_RIGHT_SIDE)))
	_it("td_peering_left", str(td.get_terrain_peering_bit(TileSet.CELL_NEIGHBOR_LEFT_SIDE)))
	# second tile gets the same terrain
	var td2 := src.get_tile_data(Vector2i(1, 0), 0)
	td2.terrain_set = 0
	td2.terrain = 1
	# terrain connect over a 1x3 strip
	layer.set_cells_terrain_connect([Vector2i(0, 0), Vector2i(1, 0), Vector2i(2, 0)], 0, 0, true)
	_it("connect_used", _coords(layer.get_used_cells()))
	_it("connect_src_0_0", str(layer.get_cell_source_id(Vector2i(0, 0))))
	_it("connect_atlas_0_0", _v2i(layer.get_cell_atlas_coords(Vector2i(0, 0))))
	_it("connect_atlas_1_0", _v2i(layer.get_cell_atlas_coords(Vector2i(1, 0))))
	_it("connect_atlas_2_0", _v2i(layer.get_cell_atlas_coords(Vector2i(2, 0))))
	# terrain path
	layer.clear()
	layer.set_cells_terrain_path([Vector2i(0, 0), Vector2i(1, 0), Vector2i(2, 0)], 0, 0, true)
	_it("path_used", _coords(layer.get_used_cells()))
	# ignore_empty_terrains=false with no matching terrain
	layer.clear()
	layer.set_cells_terrain_connect([Vector2i(0, 0), Vector2i(1, 0)], 0, 1, false)
	_it("connect_ignore_false_used", _coords(layer.get_used_cells()))
	# bad terrain set index
	layer.clear()
	layer.set_cells_terrain_connect([Vector2i(0, 0)], 5, 0, true)
	_it("connect_bad_set_used", _coords(layer.get_used_cells()))
	_pass()

# --- arm: nav -------------------------------------------------------------------

func _nav() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var ts: TileSet = d["ts"]
	var src: TileSetAtlasSource = d["src"]
	var sid: int = d["sid"]
	_it("nav_layers_0", str(ts.get_navigation_layers_count()))
	ts.add_navigation_layer()
	_it("nav_layers_1", str(ts.get_navigation_layers_count()))
	_it("nav_layer_defaults", "cl=%d cm=%d" % [ts.get_navigation_layer_layers(0),
		ts.get_navigation_layer_layers(0)])
	ts.set_navigation_layer_layers(0, 3)
	_it("nav_layer_set", str(ts.get_navigation_layer_layers(0)))
	var td := src.get_tile_data(Vector2i(0, 0), 0)
	_it("td_nav_poly_default", "null" if td.get_navigation_polygon(0) == null else "obj")
	var poly := NavigationPolygon.new()
	poly.add_outline(PackedVector2Array([Vector2(-8, -8), Vector2(8, -8), Vector2(8, 8), Vector2(-8, 8)]))
	poly.make_polygons_from_outlines()
	td.set_navigation_polygon(0, poly)
	_it("td_nav_poly_set", "null" if td.get_navigation_polygon(0) == null else "obj")
	var layer := _mk_layer(ts)
	root.add_child(layer)
	_it("layer_nav_enabled", _b(layer.navigation_enabled))
	_it("layer_nav_vis", str(layer.navigation_visibility_mode))
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	var map: RID = layer.get_navigation_map()
	_it("layer_nav_map_valid", _b(map.is_valid()))
	it_region_count(layer, "after_set_cell")
	await physics_frame
	await physics_frame
	it_region_count(layer, "after_2f")
	await physics_frame
	await physics_frame
	it_region_count(layer, "after_4f")
	# map iteration id
	if map.is_valid():
		_it("map_iter", str(NavigationServer2D.map_get_iteration_id(map)))
	# collision/nav quadrants
	_it("nav_quadrant_size", str(layer.physics_quadrant_size))
	# region for a single tile
	_it("nav_regions_default_map", str(NavigationServer2D.map_get_regions(map).size() if map.is_valid() else -1))
	_pass()

func it_region_count(layer: TileMapLayer, label: String) -> void:
	var map: RID = layer.get_navigation_map()
	var n := NavigationServer2D.map_get_regions(map).size() if map.is_valid() else -1
	_it("regions_%s" % label, str(n))

# --- arm: pattern ---------------------------------------------------------------

func _pattern() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var ts: TileSet = d["ts"]
	var src: TileSetAtlasSource = d["src"]
	var sid: int = d["sid"]
	var layer := _mk_layer(ts)
	root.add_child(layer)
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	layer.set_cell(Vector2i(1, 0), sid, Vector2i(1, 0), 0)
	layer.set_cell(Vector2i(0, 1), sid, Vector2i(0, 1), 0)
	var pat := layer.get_pattern([Vector2i(0, 0), Vector2i(1, 0), Vector2i(0, 1)])
	_it("pattern_class", pat.get_class())
	_it("pattern_size", _v2i(pat.get_size()))
	_it("pattern_used", _coords(pat.get_used_cells()))
	_it("pattern_src_0_0", str(pat.get_cell_source_id(Vector2i(0, 0))))
	_it("pattern_atlas_1_0", _v2i(pat.get_cell_atlas_coords(Vector2i(1, 0))))
	_it("pattern_empty_at_1_1", str(pat.get_cell_source_id(Vector2i(1, 1))))
	# empty pattern
	var empty_pat := layer.get_pattern([])
	_it("pattern_empty_size", _v2i(empty_pat.get_size()))
	_it("pattern_empty_used", _coords(empty_pat.get_used_cells()))
	# set pattern at an offset
	layer.clear()
	layer.set_pattern(Vector2i(4, 4), pat)
	_it("set_pattern_used", _coords(layer.get_used_cells()))
	_it("set_pattern_rect", str(layer.get_used_rect()))
	_it("set_pattern_atlas_5_4", _v2i(layer.get_cell_atlas_coords(Vector2i(5, 4))))
	# pattern from a region with a hole
	layer.clear()
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	layer.set_cell(Vector2i(2, 0), sid, Vector2i(1, 0), 0)
	var pat2 := layer.get_pattern([Vector2i(0, 0), Vector2i(1, 0), Vector2i(2, 0)])
	_it("pattern2_used", _coords(pat2.get_used_cells()))
	_it("pattern2_size", _v2i(pat2.get_size()))
	_it("pattern2_hole_src", str(pat2.get_cell_source_id(Vector2i(1, 0))))
	_it("pattern2_hole_alt", str(pat2.get_cell_alternative_tile(Vector2i(1, 0))))
	_pass()

# --- arm: misc ------------------------------------------------------------------

func _misc() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var ts: TileSet = d["ts"]
	var src: TileSetAtlasSource = d["src"]
	var sid: int = d["sid"]
	var layer := _mk_layer(ts)
	root.add_child(layer)
	_it("tile_size", _v2i(ts.tile_size))
	_it("map_to_local_0_0", _v2(layer.map_to_local(Vector2i(0, 0))))
	_it("map_to_local_2_3", _v2(layer.map_to_local(Vector2i(2, 3))))
	# tile_set swap after cells exist
	layer.set_cell(Vector2i(1, 1), sid, Vector2i(0, 0), 0)
	_it("cells_before_swap", _coords(layer.get_used_cells()))
	var ts2 := TileSet.new()
	ts2.tile_size = Vector2i(16, 16)
	var src2 := TileSetAtlasSource.new()
	src2.texture = tex
	src2.create_tile(Vector2i(0, 0))
	var sid2 := ts2.add_source(src2)
	layer.tile_set = ts2
	_it("cells_after_swap", _coords(layer.get_used_cells()))
	_it("src_after_swap", str(layer.get_cell_source_id(Vector2i(1, 1))))
	_it("td_after_swap", "null" if layer.get_cell_tile_data(Vector2i(1, 1)) == null else "obj")
	_it("sid2", str(sid2))
	# tile_size change with cells present
	ts2.tile_size = Vector2i(32, 32)
	_it("local_after_tilesize", _v2(layer.map_to_local(Vector2i(1, 1))))
	# layer disabled
	layer.enabled = false
	_it("disabled_readback", _b(layer.enabled))
	_it("disabled_used", _coords(layer.get_used_cells()))
	layer.enabled = true
	# duplicate of the layer node
	layer.set_cell(Vector2i(0, 0), sid2, Vector2i(0, 0), 0)
	var dup: TileMapLayer = layer.duplicate()
	_it("dup_used", _coords(dup.get_used_cells()))
	_it("dup_tileset_same", _b(dup.tile_set == layer.tile_set))
	_it("dup_tileset_eq", _b(dup.tile_set == ts2))
	# tile_map_data round trip
	var data: PackedByteArray = layer.tile_map_data
	_it("tile_map_data_len", str(data.size()))
	var layer2 := _mk_layer(ts2)
	root.add_child(layer2)
	layer2.tile_map_data = data
	_it("data_roundtrip_used", _coords(layer2.get_used_cells()))
	# used rect for negative coords
	layer.set_cell(Vector2i(-3, -2), sid2, Vector2i(0, 0), 0)
	_it("rect_neg", str(layer.get_used_rect()))
	_it("used_neg", _coords(layer.get_used_cells()))
	_pass()

# --- arm: neighbors -------------------------------------------------------------

func _neighbors() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var layer := _mk_layer(d["ts"])
	root.add_child(layer)
	var names := {
		"RIGHT_SIDE": TileSet.CELL_NEIGHBOR_RIGHT_SIDE,
		"RIGHT_CORNER": TileSet.CELL_NEIGHBOR_RIGHT_CORNER,
		"BOTTOM_RIGHT_SIDE": TileSet.CELL_NEIGHBOR_BOTTOM_RIGHT_SIDE,
		"BOTTOM_RIGHT_CORNER": TileSet.CELL_NEIGHBOR_BOTTOM_RIGHT_CORNER,
		"BOTTOM_SIDE": TileSet.CELL_NEIGHBOR_BOTTOM_SIDE,
		"BOTTOM_CORNER": TileSet.CELL_NEIGHBOR_BOTTOM_CORNER,
		"BOTTOM_LEFT_SIDE": TileSet.CELL_NEIGHBOR_BOTTOM_LEFT_SIDE,
		"BOTTOM_LEFT_CORNER": TileSet.CELL_NEIGHBOR_BOTTOM_LEFT_CORNER,
		"LEFT_SIDE": TileSet.CELL_NEIGHBOR_LEFT_SIDE,
		"LEFT_CORNER": TileSet.CELL_NEIGHBOR_LEFT_CORNER,
		"TOP_LEFT_SIDE": TileSet.CELL_NEIGHBOR_TOP_LEFT_SIDE,
		"TOP_LEFT_CORNER": TileSet.CELL_NEIGHBOR_TOP_LEFT_CORNER,
		"TOP_SIDE": TileSet.CELL_NEIGHBOR_TOP_SIDE,
		"TOP_CORNER": TileSet.CELL_NEIGHBOR_TOP_CORNER,
		"TOP_RIGHT_SIDE": TileSet.CELL_NEIGHBOR_TOP_RIGHT_SIDE,
		"TOP_RIGHT_CORNER": TileSet.CELL_NEIGHBOR_TOP_RIGHT_CORNER,
	}
	var keys: Array = names.keys()
	keys.sort()
	for k in keys:
		_it("nb_%s" % k, _v2i(layer.get_neighbor_cell(Vector2i(0, 0), names[k])))
	_it("nb_count", str(keys.size()))
	_pass()

# --- arm: flip ------------------------------------------------------------------

func _flip() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var ts: TileSet = d["ts"]
	var src: TileSetAtlasSource = d["src"]
	var sid: int = d["sid"]
	# an alternative tile with flipped data
	var alt := src.create_alternative_tile(Vector2i(0, 0))
	var td := src.get_tile_data(Vector2i(0, 0), alt)
	td.set_flip_h(true)
	td.set_transpose(true)
	var layer := _mk_layer(ts)
	root.add_child(layer)
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	layer.set_cell(Vector2i(1, 0), sid, Vector2i(0, 0), alt)
	_it("base_flip_h", _b(layer.is_cell_flipped_h(Vector2i(0, 0))))
	_it("base_flip_v", _b(layer.is_cell_flipped_v(Vector2i(0, 0))))
	_it("base_transpose", _b(layer.is_cell_transposed(Vector2i(0, 0))))
	_it("alt_flip_h", _b(layer.is_cell_flipped_h(Vector2i(1, 0))))
	_it("alt_flip_v", _b(layer.is_cell_flipped_v(Vector2i(1, 0))))
	_it("alt_transpose", _b(layer.is_cell_transposed(Vector2i(1, 0))))
	_it("alt_id_readback", str(layer.get_cell_alternative_tile(Vector2i(1, 0))))
	_it("alt_td_flip_h", _b(layer.get_cell_tile_data(Vector2i(1, 0)).get_flip_h()))
	# empty cell flip readback
	_it("empty_flip_h", _b(layer.is_cell_flipped_h(Vector2i(5, 5))))
	_it("empty_transpose", _b(layer.is_cell_transposed(Vector2i(5, 5))))
	_pass()

# --- arm: fixinvalid ------------------------------------------------------------

func _fixinvalid() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var ts: TileSet = d["ts"]
	var sid: int = d["sid"]
	var layer := _mk_layer(ts)
	root.add_child(layer)
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	layer.set_cell(Vector2i(1, 0), 42, Vector2i(0, 0), 0)
	layer.set_cell(Vector2i(2, 0), sid, Vector2i(9, 9), 0)
	_it("before_used", _coords(layer.get_used_cells()))
	layer.fix_invalid_tiles()
	_it("after_used", _coords(layer.get_used_cells()))
	_it("after_src_1_0", str(layer.get_cell_source_id(Vector2i(1, 0))))
	_it("after_src_2_0", str(layer.get_cell_source_id(Vector2i(2, 0))))
	_it("after_atlas_2_0", _v2i(layer.get_cell_atlas_coords(Vector2i(2, 0))))
	# a source removed after cells exist
	ts.remove_source(sid)
	_it("after_remove_used", _coords(layer.get_used_cells()))
	layer.fix_invalid_tiles()
	_it("after_remove_fixed", _coords(layer.get_used_cells()))
	_pass()

# --- arm: dataarray -------------------------------------------------------------

func _dataarray() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var ts: TileSet = d["ts"]
	var src: TileSetAtlasSource = d["src"]
	var sid: int = d["sid"]
	var layer := _mk_layer(ts)
	root.add_child(layer)
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	layer.set_cell(Vector2i(2, 1), sid, Vector2i(1, 0), 0)
	var arr: Array = layer.get_tile_map_data_as_array()
	_it("arr_len", str(arr.size()))
	var parts: PackedStringArray = []
	for i in arr.size():
		parts.append(str(arr[i]))
	_it("arr_vals", "[%s]" % ",".join(parts))
	var layer2 := _mk_layer(ts)
	root.add_child(layer2)
	layer2.set_tile_map_data_from_array(arr)
	_it("roundtrip_used", _coords(layer2.get_used_cells()))
	_it("roundtrip_src", str(layer2.get_cell_source_id(Vector2i(2, 1))))
	# byte form
	var bytes: PackedByteArray = layer.tile_map_data
	_it("bytes_len", str(bytes.size()))
	var layer3 := _mk_layer(ts)
	root.add_child(layer3)
	layer3.tile_map_data = bytes
	_it("bytes_roundtrip_used", _coords(layer3.get_used_cells()))
	# empty array
	var layer4 := _mk_layer(ts)
	root.add_child(layer4)
	layer4.set_tile_map_data_from_array([])
	_it("empty_arr_used", _coords(layer4.get_used_cells()))
	# short/malformed array
	var layer5 := _mk_layer(ts)
	root.add_child(layer5)
	layer5.set_tile_map_data_from_array([1, 2, 3])
	_it("short_arr_used", _coords(layer5.get_used_cells()))
	_pass()

# --- arm: mappattern ------------------------------------------------------------

func _mappattern() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var ts: TileSet = d["ts"]
	var src: TileSetAtlasSource = d["src"]
	var sid: int = d["sid"]
	var layer := _mk_layer(ts)
	root.add_child(layer)
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	layer.set_cell(Vector2i(1, 0), sid, Vector2i(1, 0), 0)
	var pat := layer.get_pattern([Vector2i(0, 0), Vector2i(1, 0)])
	var other := _mk_layer(ts)
	root.add_child(other)
	other.set_cell(Vector2i(10, 10), sid, Vector2i(0, 1), 0)
	# map_pattern(position_in_this: Vector2i, position_in_pattern: Vector2i, pattern: TileMapPattern) -> Vector2i
	var mapped := other.map_pattern(Vector2i(10, 10), Vector2i(0, 0), pat)
	_it("map_pattern_00_to_10_10", _v2i(mapped))
	var mapped2 := other.map_pattern(Vector2i(10, 10), Vector2i(1, 0), pat)
	_it("map_pattern_10_to_10_10", _v2i(mapped2))
	var mapped3 := other.map_pattern(Vector2i(0, 0), Vector2i(0, 0), pat)
	_it("map_pattern_00_to_00", _v2i(mapped3))
	# get_pattern over a non-rectangular region
	layer.clear()
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	var pat2 := layer.get_pattern([Vector2i(0, 0), Vector2i(4, 4)])
	_it("sparse_pattern_size", _v2i(pat2.get_size()))
	_it("sparse_pattern_used", _coords(pat2.get_used_cells()))
	_pass()

# --- arm: quadrant --------------------------------------------------------------

func _quadrant() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var ts: TileSet = d["ts"]
	var src: TileSetAtlasSource = d["src"]
	var sid: int = d["sid"]
	ts.add_physics_layer()
	var td := src.get_tile_data(Vector2i(0, 0), 0)
	td.set_collision_polygons_count(0, 1)
	td.set_collision_polygon_points(0, 0, PackedVector2Array([Vector2(-8, -8), Vector2(8, -8), Vector2(8, 8), Vector2(-8, 8)]))
	var layer := _mk_layer(ts)
	root.add_child(layer)
	_it("default_phys_quad", str(layer.physics_quadrant_size))
	# cells spanning one quadrant boundary (quadrant size 16 => 16x16 cells)
	for x in range(0, 20):
		layer.set_cell(Vector2i(x, 0), sid, Vector2i(0, 0), 0)
	layer.set_physics_quadrant_size(2)
	_it("set_phys_quad", str(layer.physics_quadrant_size))
	await physics_frame
	await physics_frame
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
	var hit := probe.move_and_collide(Vector2(0, 20), true)
	_it("quad2_hit_at_0", "null" if hit == null else "hit")
	probe.position = Vector2(8 + 16 * 19, -6)
	await physics_frame
	var hit_far := probe.move_and_collide(Vector2(0, 20), true)
	_it("quad2_hit_at_19", "null" if hit_far == null else "hit")
	# quadrant size change at runtime
	layer.set_physics_quadrant_size(16)
	await physics_frame
	await physics_frame
	var hit_after := probe.move_and_collide(Vector2(0, 20), true)
	_it("quad16_hit_at_19", "null" if hit_after == null else "hit")
	_pass()

# --- arm: srcids ----------------------------------------------------------------

func _srcids_of(ts: TileSet) -> String:
	var parts: PackedStringArray = []
	for i in ts.get_source_count():
		parts.append(str(ts.get_source_id(i)))
	return "n%d[%s]" % [parts.size(), ";".join(parts)]

func _srcids() -> void:
	var tex := _mk_texture(32, 32)
	var ts := TileSet.new()
	var src := TileSetAtlasSource.new()
	src.texture = tex
	src.create_tile(Vector2i(0, 0))
	var sid := ts.add_source(src)
	_it("sid_auto", str(sid))
	_it("next_source_id", str(ts.get_next_source_id()))
	var src_b := TileSetAtlasSource.new()
	src_b.texture = tex
	var sid_b := ts.add_source(src_b, 5)
	_it("sid_explicit_5", str(sid_b))
	_it("next_after_explicit", str(ts.get_next_source_id()))
	_it("count", str(ts.get_source_count()))
	_it("ids", _srcids_of(ts))
	_it("get_source_id_0", str(ts.get_source_id(0)))
	_it("get_source_id_1", str(ts.get_source_id(1)))
	# set_source_id move
	ts.set_source_id(sid_b, 2)
	_it("after_move_ids", _srcids_of(ts))
	_it("has_source_2", _b(ts.has_source(2)))
	_it("has_source_5", _b(ts.has_source(5)))
	# remove
	ts.remove_source(2)
	_it("after_remove_ids", _srcids_of(ts))
	_it("count_after_remove", str(ts.get_source_count()))
	# add_source(null)
	var null_id := ts.add_source(null)
	_it("add_null_source_id", str(null_id))
	_it("count_after_null", str(ts.get_source_count()))
	_it("get_source_null", "null" if ts.get_source(null_id) == null else "obj")
	# explicit id collision
	var src_c := TileSetAtlasSource.new()
	src_c.texture = tex
	var sid_c := ts.add_source(src_c, sid)
	_it("add_colliding_id", str(sid_c))
	_it("count_after_collide", str(ts.get_source_count()))
	# negative explicit id
	var src_d := TileSetAtlasSource.new()
	src_d.texture = tex
	var sid_d := ts.add_source(src_d, -3)
	_it("add_negative_id", str(sid_d))
	_it("ids_after_neg", _srcids_of(ts))
	_pass()

# --- arm: nullts (crash class) --------------------------------------------------

func _nullts() -> void:
	var layer := TileMapLayer.new()
	root.add_child(layer)
	_it("tileset_null", _b(layer.tile_set == null))
	layer.set_cell(Vector2i(0, 0), 0, Vector2i(0, 0), 0)
	_it("used_after_set", _coords(layer.get_used_cells()))
	_it("src_after_set", str(layer.get_cell_source_id(Vector2i(0, 0))))
	_it("about_to_call_tile_data", "1")
	# expected: engine crash (SIGSEGV) if the null tileset is dereferenced
	var td := layer.get_cell_tile_data(Vector2i(0, 0))
	_it("td_after_set", "null" if td == null else "obj")
	_pass()
