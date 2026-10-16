extends SceneTree
# r92 scout probe — TileMapLayer/TileSet authorability lattice.
# Battery launch shape:
#   godot --headless --path <scratch> --script res://tilemap_lattice.gd -- --arm=<name>
# Arm parse is the battery convention (OS.get_cmdline_user_args + "--arm=" prefix
# scan); every arm prints its own name on the PASS line, so a silent fallback is
# impossible. Prints `R92 <arm> <key>=<value>` diagnostics and one final
# `PASS tilemap_lattice <arm> <key>=<value> ...` line (the authorable signature).
# No object ids / RIDs / addresses are printed (byte-stability).
# A 20 s watchdog quits FAIL instead of hanging if an arm dies mid-way.

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
	print("PASS tilemap_lattice %s %s" % [arm, " ".join(_items)])
	quit()

func _fail(reason: String) -> void:
	print("FAIL tilemap_lattice %s reason=%s" % [arm, reason])
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

func _ints(arr: Array) -> String:
	var parts: PackedStringArray = []
	for v in arr:
		parts.append(str(v))
	return "[%s]" % ",".join(parts)

# --- shared construction --------------------------------------------------------

func _mk_texture(w: int, h: int) -> ImageTexture:
	var img := Image.create_empty(w, h, false, Image.FORMAT_RGBA8)
	img.fill(Color(1, 1, 1, 1))
	return ImageTexture.create_from_image(img)

# TileSet with one atlas source (32x32 texture, 16x16 regions => 4 tiles).
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

func _src_ids(ts: TileSet) -> String:
	var parts: PackedStringArray = []
	for i in ts.get_source_count():
		parts.append(str(ts.get_source_id(i)))
	return "n%d[%s]" % [parts.size(), ";".join(parts)]

# A 4x4 collision polygon on physics layer 0 of tile (0,0) of the atlas.
func _add_phys_tile(ts: TileSet, src: TileSetAtlasSource) -> void:
	ts.add_physics_layer()
	var td := src.get_tile_data(Vector2i(0, 0), 0)
	td.set_collision_polygons_count(0, 1)
	td.set_collision_polygon_points(0, 0,
		PackedVector2Array([Vector2(-8, -8), Vector2(8, -8), Vector2(8, 8), Vector2(-8, 8)]))

func _mk_probe() -> CharacterBody2D:
	var probe := CharacterBody2D.new()
	var cs := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = Vector2(8, 8)
	cs.shape = shape
	probe.add_child(cs)
	probe.position = Vector2(8, -6)
	return probe

func _mc(probe: CharacterBody2D) -> String:
	var hit := probe.move_and_collide(Vector2(0, 20), true)
	return "null" if hit == null else "hit"

func _run() -> void:
	print("arm=%s" % arm)
	if arm == "":
		_fail("empty_arm")
		return
	var watchdog := create_timer(20.0)
	watchdog.timeout.connect(func() -> void:
		print("FAIL tilemap_lattice %s reason=watchdog" % arm)
		quit(1))
	match arm:
		"census":
			_census()
		"atlas":
			_atlas()
		"cells":
			_cells()
		"custom":
			_custom()
		"terrain":
			_terrain()
		"pattern":
			_pattern()
		"encoding":
			_encoding()
		"fixinvalid":
			_fixinvalid()
		"srcids":
			_srcids()
		"physics":
			await _physics()
		"timing":
			await _timing()
		"quadrant":
			await _quadrant()
		"nav":
			await _nav()
		"nullts":
			_nullts()
		_:
			_fail("unknown_arm")

# --- census ---------------------------------------------------------------------

func _census() -> void:
	var layer := TileMapLayer.new()
	_it("layer_defaults", "enabled=%s collision_enabled=%s nav_enabled=%s use_kinematic=%s phys_quad=%d rend_quad=%d col_vis=%d nav_vis=%d y_sort_origin=%d x_draw_rev=%s occl=%s" % [
		_b(layer.enabled), _b(layer.collision_enabled), _b(layer.navigation_enabled),
		_b(layer.use_kinematic_bodies), layer.physics_quadrant_size, layer.rendering_quadrant_size,
		layer.collision_visibility_mode, layer.navigation_visibility_mode,
		layer.y_sort_origin, _b(layer.x_draw_order_reversed), _b(layer.occlusion_enabled)])
	_it("layer_props", "n%d[%s]" % [ClassDB.class_get_property_list("TileMapLayer", true).size(),
		"collision_enabled,collision_visibility_mode,enabled,navigation_enabled,navigation_visibility_mode,occlusion_enabled,physics_quadrant_size,rendering_quadrant_size,tile_map_data,tile_set,use_kinematic_bodies,x_draw_order_reversed,y_sort_origin"])
	_it("layer_no_collision_priority", _b(not layer.get_property_list().any(
		func(p: Dictionary) -> bool: return p["name"] == "collision_priority")))
	var ts := TileSet.new()
	_it("ts_defaults", "tile_size=%s physics_layers=%d nav_layers=%d custom_data_layers=%d terrain_sets=%d occlusion_layers=%d sources=%d tile_shape=%d tile_layout=%d tile_offset_axis=%d uv_clipping=%s" % [
		_v2i(ts.tile_size), ts.get_physics_layers_count(), ts.get_navigation_layers_count(),
		ts.get_custom_data_layers_count(), ts.get_terrain_sets_count(), ts.get_occlusion_layers_count(),
		ts.get_source_count(), ts.tile_shape, ts.tile_layout, ts.tile_offset_axis,
		_b(ts.uv_clipping)])
	var src := TileSetAtlasSource.new()
	_it("atlas_defaults", "region=%s margins=%s separation=%s tiles=%d padding=%s" % [
		_v2i(src.texture_region_size), _v2i(src.margins), _v2i(src.separation),
		src.get_tiles_count(), _b(src.use_texture_padding)])
	_it("enum_terrainset", "MATCH_CORNERS_AND_SIDES=%d MATCH_CORNERS=%d MATCH_SIDES=%d" % [
		TileSet.TERRAIN_MODE_MATCH_CORNERS_AND_SIDES, TileSet.TERRAIN_MODE_MATCH_CORNERS,
		TileSet.TERRAIN_MODE_MATCH_SIDES])
	_it("enum_tileshape", "SQUARE=%d ISOMETRIC=%d HALF_OFFSET_SQUARE=%d HEXAGON=%d" % [
		TileSet.TILE_SHAPE_SQUARE, TileSet.TILE_SHAPE_ISOMETRIC,
		TileSet.TILE_SHAPE_HALF_OFFSET_SQUARE, TileSet.TILE_SHAPE_HEXAGON])
	_it("enum_neighbor", "RIGHT_SIDE=%d RIGHT_CORNER=%d BOTTOM_RIGHT_SIDE=%d BOTTOM_RIGHT_CORNER=%d BOTTOM_SIDE=%d TOP_RIGHT_CORNER=%d" % [
		TileSet.CELL_NEIGHBOR_RIGHT_SIDE, TileSet.CELL_NEIGHBOR_RIGHT_CORNER,
		TileSet.CELL_NEIGHBOR_BOTTOM_RIGHT_SIDE, TileSet.CELL_NEIGHBOR_BOTTOM_RIGHT_CORNER,
		TileSet.CELL_NEIGHBOR_BOTTOM_SIDE, TileSet.CELL_NEIGHBOR_TOP_RIGHT_CORNER])
	_it("invalid_source", str(-1))
	_it("class_method_counts", "TileMapLayer=%d TileSet=%d TileSetAtlasSource=%d TileData=%d TileMapPattern=%d" % [
		ClassDB.class_get_method_list("TileMapLayer", true).size(),
		ClassDB.class_get_method_list("TileSet", true).size(),
		ClassDB.class_get_method_list("TileSetAtlasSource", true).size(),
		ClassDB.class_get_method_list("TileData", true).size(),
		ClassDB.class_get_method_list("TileMapPattern", true).size()])
	layer.free()
	_pass()

# --- atlas ----------------------------------------------------------------------

func _atlas() -> void:
	var ts := TileSet.new()
	var tex := _mk_texture(32, 32)
	var src := TileSetAtlasSource.new()
	src.texture = tex
	var sid := ts.add_source(src)
	_it("sid_first", str(sid))
	_it("count_1", str(ts.get_source_count()))
	_it("has_source_0", _b(ts.has_source(0)))
	_it("src_class", ts.get_source(sid).get_class())
	src.create_tile(Vector2i(0, 0))
	src.create_tile(Vector2i(1, 0))
	_it("tiles_after_2", str(src.get_tiles_count()))
	_it("has_tile_00", _b(src.has_tile(Vector2i(0, 0))))
	_it("has_tile_11", _b(src.has_tile(Vector2i(1, 1))))
	var ids: PackedStringArray = []
	for i in src.get_tiles_count():
		ids.append(_v2i(src.get_tile_id(i)))
	_it("tiles_list", "n%d[%s]" % [ids.size(), ";".join(ids)])
	src.create_tile(Vector2i(0, 0))
	_it("tiles_after_dup", str(src.get_tiles_count()))
	var alt := src.create_alternative_tile(Vector2i(0, 0))
	_it("alt_id", str(alt))
	_it("alt_count", str(src.get_alternative_tiles_count(Vector2i(0, 0))))
	var alts: PackedStringArray = []
	for i in src.get_alternative_tiles_count(Vector2i(0, 0)):
		alts.append(str(src.get_alternative_tile_id(Vector2i(0, 0), i)))
	_it("alt_list", "n%d[%s]" % [alts.size(), ";".join(alts)])
	_it("has_alt_0", _b(src.has_alternative_tile(Vector2i(0, 0), 0)))
	_it("has_alt_1", _b(src.has_alternative_tile(Vector2i(0, 0), 1)))
	_it("has_alt_7", _b(src.has_alternative_tile(Vector2i(0, 0), 7)))
	var td := src.get_tile_data(Vector2i(0, 0), 0)
	var td_alt := src.get_tile_data(Vector2i(0, 0), alt)
	_it("td_class", td.get_class() if td else "null")
	_it("td_alt_distinct", _b(td != null and td_alt != null and td != td_alt))
	var td_none := src.get_tile_data(Vector2i(5, 5), 0)
	_it("td_missing", "null" if td_none == null else "obj")
	src.remove_tile(Vector2i(1, 0))
	_it("tiles_after_remove", str(src.get_tiles_count()))
	_it("has_tile_10_after", _b(src.has_tile(Vector2i(1, 0))))
	var src3 := TileSetAtlasSource.new()
	src3.texture = tex
	var sid3 := ts.add_source(src3, 7)
	_it("sid_explicit_7", str(sid3))
	_it("ids", _src_ids(ts))
	_it("next_source_id", str(ts.get_next_source_id()))
	_it("grid_size", _v2i(src.get_atlas_grid_size()))
	_it("tile_size_in_atlas", _v2i(src.get_tile_size_in_atlas(Vector2i(0, 0))))
	_it("tex_region", str(src.get_tile_texture_region(Vector2i(0, 0))))
	_pass()

# --- cells ----------------------------------------------------------------------

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
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	layer.set_cell(Vector2i(3, 2), sid, Vector2i(1, 0), 0)
	layer.set_cell(Vector2i(-2, -1), sid, Vector2i(0, 1), 0)
	_it("used_after_3", _coords(layer.get_used_cells()))
	_it("rect_after_3", str(layer.get_used_rect()))
	_it("src_3_2", str(layer.get_cell_source_id(Vector2i(3, 2))))
	_it("atlas_3_2", _v2i(layer.get_cell_atlas_coords(Vector2i(3, 2))))
	_it("td_3_2", "null" if layer.get_cell_tile_data(Vector2i(3, 2)) == null else "obj")
	# same-frame data visibility after a write
	layer.set_cell(Vector2i(9, 9), sid, Vector2i(0, 0), 0)
	_it("same_frame_td", "null" if layer.get_cell_tile_data(Vector2i(9, 9)) == null else "obj")
	_it("same_frame_used_has", _b(layer.get_used_cells().has(Vector2i(9, 9))))
	# erase via the -1 sentinel
	layer.set_cell(Vector2i(3, 2), -1, Vector2i(-1, -1), -1)
	_it("erase_src", str(layer.get_cell_source_id(Vector2i(3, 2))))
	_it("erase_used_n", str(layer.get_used_cells().size()))
	layer.erase_cell(Vector2i(0, 0))
	_it("erase_used_n2", str(layer.get_used_cells().size()))
	_it("erase_absent_ok", _b(layer.get_cell_source_id(Vector2i(0, 0)) == -1))
	# poison cells: source id / atlas coords that do not exist are stored verbatim
	layer.set_cell(Vector2i(5, 5), 42, Vector2i(0, 0), 0)
	_it("bad_src_readback", str(layer.get_cell_source_id(Vector2i(5, 5))))
	_it("bad_src_in_used", _b(layer.get_used_cells().has(Vector2i(5, 5))))
	layer.set_cell(Vector2i(6, 6), sid, Vector2i(9, 9), 0)
	_it("bad_atlas_readback", _v2i(layer.get_cell_atlas_coords(Vector2i(6, 6))))
	_it("bad_atlas_td", "null" if layer.get_cell_tile_data(Vector2i(6, 6)) == null else "obj")
	_it("used_by_id_src", _coords(layer.get_used_cells_by_id(sid)))
	_it("used_by_id_bad", _coords(layer.get_used_cells_by_id(42)))
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
	# neighbors: square shape has 8 valid peering bits, 8 refusals
	var valid := {
		"RIGHT_SIDE": TileSet.CELL_NEIGHBOR_RIGHT_SIDE,
		"BOTTOM_RIGHT_CORNER": TileSet.CELL_NEIGHBOR_BOTTOM_RIGHT_CORNER,
		"BOTTOM_SIDE": TileSet.CELL_NEIGHBOR_BOTTOM_SIDE,
		"BOTTOM_LEFT_CORNER": TileSet.CELL_NEIGHBOR_BOTTOM_LEFT_CORNER,
		"LEFT_SIDE": TileSet.CELL_NEIGHBOR_LEFT_SIDE,
		"TOP_LEFT_CORNER": TileSet.CELL_NEIGHBOR_TOP_LEFT_CORNER,
		"TOP_SIDE": TileSet.CELL_NEIGHBOR_TOP_SIDE,
		"TOP_RIGHT_CORNER": TileSet.CELL_NEIGHBOR_TOP_RIGHT_CORNER,
	}
	var vkeys: Array = valid.keys()
	vkeys.sort()
	var vparts: PackedStringArray = []
	for k in vkeys:
		vparts.append("%s:%s" % [k, _v2i(layer.get_neighbor_cell(Vector2i(0, 0), valid[k]))])
	_it("neighbors_valid8", "|".join(vparts))
	var invalid := {
		"RIGHT_CORNER": TileSet.CELL_NEIGHBOR_RIGHT_CORNER,
		"BOTTOM_RIGHT_SIDE": TileSet.CELL_NEIGHBOR_BOTTOM_RIGHT_SIDE,
		"BOTTOM_CORNER": TileSet.CELL_NEIGHBOR_BOTTOM_CORNER,
		"TOP_RIGHT_SIDE": TileSet.CELL_NEIGHBOR_TOP_RIGHT_SIDE,
	}
	var ikeys: Array = invalid.keys()
	ikeys.sort()
	var iparts: PackedStringArray = []
	for k in ikeys:
		iparts.append("%s:%s" % [k, _v2i(layer.get_neighbor_cell(Vector2i(0, 0), invalid[k]))])
	_it("neighbors_invalid4", "|".join(iparts))
	# flip/transpose readback: empty cells read as flipped+transposed
	_it("empty_flip_h", _b(layer.is_cell_flipped_h(Vector2i(7, 7))))
	_it("empty_flip_v", _b(layer.is_cell_flipped_v(Vector2i(7, 7))))
	_it("empty_transpose", _b(layer.is_cell_transposed(Vector2i(7, 7))))
	layer.set_cell(Vector2i(7, 7), sid, Vector2i(0, 0), 0)
	_it("set_flip_h", _b(layer.is_cell_flipped_h(Vector2i(7, 7))))
	_it("set_flip_v", _b(layer.is_cell_flipped_v(Vector2i(7, 7))))
	_it("set_transpose", _b(layer.is_cell_transposed(Vector2i(7, 7))))
	_pass()

# --- custom data ------------------------------------------------------------------

func _custom() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var ts: TileSet = d["ts"]
	var src: TileSetAtlasSource = d["src"]
	var sid: int = d["sid"]
	var layer := _mk_layer(ts)
	root.add_child(layer)
	_it("layers_0", str(ts.get_custom_data_layers_count()))
	ts.add_custom_data_layer()
	ts.set_custom_data_layer_name(0, "hp")
	ts.set_custom_data_layer_type(0, TYPE_INT)
	ts.add_custom_data_layer()
	ts.set_custom_data_layer_name(1, "tag")
	ts.set_custom_data_layer_type(1, TYPE_STRING)
	_it("layers_2", str(ts.get_custom_data_layers_count()))
	_it("name_0", ts.get_custom_data_layer_name(0))
	_it("type_0", str(ts.get_custom_data_layer_type(0)))
	_it("index_of_hp", str(ts.get_custom_data_layer_by_name("hp")))
	_it("index_of_missing", str(ts.get_custom_data_layer_by_name("nope")))
	_it("has_layer_hp", _b(ts.has_custom_data_layer_by_name("hp")))
	var td := src.get_tile_data(Vector2i(0, 0), 0)
	_it("default_hp", str(td.get_custom_data("hp")))
	_it("default_tag", str(td.get_custom_data("tag")))
	_it("has_hp", _b(td.has_custom_data("hp")))
	td.set_custom_data("hp", 7)
	td.set_custom_data("tag", "alpha")
	_it("hp_7", str(td.get_custom_data("hp")))
	_it("tag_alpha", str(td.get_custom_data("tag")))
	_it("by_index_0", str(td.get_custom_data_by_layer_id(0)))
	_it("by_index_1", str(td.get_custom_data_by_layer_id(1)))
	# the declared type is advisory: a wrong-typed write stores verbatim
	td.set_custom_data("hp", "not-an-int")
	_it("hp_wrongtype", str(td.get_custom_data("hp")))
	_it("hp_wrongtype_still", str(td.get_custom_data_by_layer_id(0)))
	# readback through the layer
	layer.set_cell(Vector2i(2, 2), sid, Vector2i(0, 0), 0)
	var ctd := layer.get_cell_tile_data(Vector2i(2, 2))
	_it("layer_hp", str(ctd.get_custom_data("hp")))
	_it("layer_tag", str(ctd.get_custom_data("tag")))
	# unregistered names refuse loudly and return null
	td.set_custom_data("ghost", 1)
	_it("ghost", str(td.get_custom_data("ghost")))
	_it("missing", str(td.get_custom_data("absent")))
	# layer removal invalidates the name
	ts.remove_custom_data_layer(1)
	_it("layers_after_remove", str(ts.get_custom_data_layers_count()))
	_it("tag_after_remove", str(td.get_custom_data("tag")))
	_it("hp_after_remove", str(td.get_custom_data("hp")))
	# deep duplicate keeps the layers and the data
	var dup: TileSet = ts.duplicate(true)
	var dup_src: TileSetAtlasSource = dup.get_source(dup.get_source_id(0))
	var dup_td := dup_src.get_tile_data(Vector2i(0, 0), 0)
	_it("dup_layers", str(dup.get_custom_data_layers_count()))
	_it("dup_hp", str(dup_td.get_custom_data("hp")))
	_it("dup_is_distinct", _b(dup_td != td))
	_pass()

# --- terrain ----------------------------------------------------------------------

func _terrain() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var ts: TileSet = d["ts"]
	var src: TileSetAtlasSource = d["src"]
	var layer := _mk_layer(ts)
	root.add_child(layer)
	_it("sets_0", str(ts.get_terrain_sets_count()))
	ts.add_terrain_set()
	_it("sets_1", str(ts.get_terrain_sets_count()))
	_it("mode_default", str(ts.get_terrain_set_mode(0)))
	ts.set_terrain_set_mode(0, TileSet.TERRAIN_MODE_MATCH_CORNERS_AND_SIDES)
	_it("mode_set", str(ts.get_terrain_set_mode(0)))
	_it("terrains_0", str(ts.get_terrains_count(0)))
	ts.add_terrain(0)
	ts.add_terrain(0)
	_it("terrains_2", str(ts.get_terrains_count(0)))
	ts.set_terrain_name(0, 0, "grass")
	ts.set_terrain_name(0, 1, "dirt")
	_it("names", "%s,%s" % [ts.get_terrain_name(0, 0), ts.get_terrain_name(0, 1)])
	ts.set_terrain_color(0, 0, Color(0, 1, 0))
	_it("color_0", str(ts.get_terrain_color(0, 0)))
	# terrain assignment is per TileData
	var td := src.get_tile_data(Vector2i(0, 0), 0)
	_it("td_terrain_set_default", str(td.terrain_set))
	_it("td_terrain_default", str(td.terrain))
	td.terrain_set = 0
	td.terrain = 0
	_it("td_terrain_set", str(td.terrain_set))
	_it("td_terrain", str(td.terrain))
	td.set_terrain_peering_bit(TileSet.CELL_NEIGHBOR_RIGHT_SIDE, 1)
	_it("peering_right", str(td.get_terrain_peering_bit(TileSet.CELL_NEIGHBOR_RIGHT_SIDE)))
	_it("peering_left", str(td.get_terrain_peering_bit(TileSet.CELL_NEIGHBOR_LEFT_SIDE)))
	_it("peering_right_valid", _b(td.is_valid_terrain_peering_bit(TileSet.CELL_NEIGHBOR_RIGHT_SIDE)))
	_it("peering_right_corner_valid", _b(td.is_valid_terrain_peering_bit(TileSet.CELL_NEIGHBOR_RIGHT_CORNER)))
	# a second tile carrying the other terrain
	var td2 := src.get_tile_data(Vector2i(1, 0), 0)
	td2.terrain_set = 0
	td2.terrain = 1
	# only tiles that carry the requested terrain are placed
	layer.set_cells_terrain_connect([Vector2i(0, 0), Vector2i(1, 0), Vector2i(2, 0)], 0, 0, true)
	_it("connect_used", _coords(layer.get_used_cells()))
	_it("connect_src_0_0", str(layer.get_cell_source_id(Vector2i(0, 0))))
	_it("connect_atlas_0_0", _v2i(layer.get_cell_atlas_coords(Vector2i(0, 0))))
	_it("connect_atlas_1_0", _v2i(layer.get_cell_atlas_coords(Vector2i(1, 0))))
	_it("connect_atlas_2_0", _v2i(layer.get_cell_atlas_coords(Vector2i(2, 0))))
	# the same cells with the second terrain place the other tile
	layer.clear()
	layer.set_cells_terrain_connect([Vector2i(0, 0), Vector2i(1, 0), Vector2i(2, 0)], 0, 1, true)
	_it("connect_dirt_used", _coords(layer.get_used_cells()))
	_it("connect_dirt_atlas_0_0", _v2i(layer.get_cell_atlas_coords(Vector2i(0, 0))))
	# terrain path is the same placement on this single-terrain layout
	layer.clear()
	layer.set_cells_terrain_path([Vector2i(0, 0), Vector2i(1, 0), Vector2i(2, 0)], 0, 0, true)
	_it("path_used", _coords(layer.get_used_cells()))
	# a terrain set index outside the tileset refuses and places nothing
	layer.clear()
	layer.set_cells_terrain_connect([Vector2i(0, 0)], 5, 0, true)
	_it("bad_set_used", _coords(layer.get_used_cells()))
	# a terrain index outside the set refuses and places nothing
	layer.clear()
	layer.set_cells_terrain_connect([Vector2i(0, 0)], 0, 9, true)
	_it("bad_terrain_used", _coords(layer.get_used_cells()))
	# no terrain at all in the tileset
	layer.clear()
	ts.clear_terrains(0)
	layer.set_cells_terrain_connect([Vector2i(0, 0)], 0, 0, true)
	_it("no_terrain_used", _coords(layer.get_used_cells()))
	_pass()

# --- pattern ----------------------------------------------------------------------

func _pattern() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var ts: TileSet = d["ts"]
	var sid: int = d["sid"]
	var layer := _mk_layer(ts)
	root.add_child(layer)
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	layer.set_cell(Vector2i(1, 0), sid, Vector2i(1, 0), 0)
	layer.set_cell(Vector2i(0, 1), sid, Vector2i(0, 1), 0)
	var pat := layer.get_pattern([Vector2i(0, 0), Vector2i(1, 0), Vector2i(0, 1)])
	_it("class", pat.get_class())
	_it("size", _v2i(pat.get_size()))
	_it("used", _coords(pat.get_used_cells()))
	_it("src_0_0", str(pat.get_cell_source_id(Vector2i(0, 0))))
	_it("atlas_1_0", _v2i(pat.get_cell_atlas_coords(Vector2i(1, 0))))
	_it("has_cell_0_0", _b(pat.has_cell(Vector2i(0, 0))))
	_it("empty_at_1_1", str(pat.get_cell_source_id(Vector2i(1, 1))))
	_it("is_empty", _b(pat.is_empty()))
	var empty_pat := layer.get_pattern([])
	_it("empty_size", _v2i(empty_pat.get_size()))
	_it("empty_used", _coords(empty_pat.get_used_cells()))
	_it("empty_is_empty", _b(empty_pat.is_empty()))
	layer.clear()
	layer.set_pattern(Vector2i(4, 4), pat)
	_it("set_used", _coords(layer.get_used_cells()))
	_it("set_rect", str(layer.get_used_rect()))
	_it("set_atlas_5_4", _v2i(layer.get_cell_atlas_coords(Vector2i(5, 4))))
	# a pattern over a sparse region keeps the bounding box and its holes
	layer.clear()
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	layer.set_cell(Vector2i(4, 4), sid, Vector2i(1, 0), 0)
	var pat2 := layer.get_pattern([Vector2i(0, 0), Vector2i(4, 4)])
	_it("sparse_size", _v2i(pat2.get_size()))
	_it("sparse_used", _coords(pat2.get_used_cells()))
	_it("sparse_hole_src", str(pat2.get_cell_source_id(Vector2i(2, 2))))
	# map_pattern translates a pattern coordinate into a layer coordinate
	var other := _mk_layer(ts)
	root.add_child(other)
	var mapped := other.map_pattern(Vector2i(10, 10), Vector2i(1, 0), pat)
	_it("map_pattern_10_10_1_0", _v2i(mapped))
	var mapped2 := other.map_pattern(Vector2i(0, 0), Vector2i(0, 0), pat)
	_it("map_pattern_0_0_0_0", _v2i(mapped2))
	# a pattern set from another layer keeps source/atlas/alternative
	var pat3 := layer.get_pattern([Vector2i(0, 0)])
	other.set_pattern(Vector2i(-2, -2), pat3)
	_it("cross_layer_used", _coords(other.get_used_cells()))
	_it("cross_layer_atlas", _v2i(other.get_cell_atlas_coords(Vector2i(-2, -2))))
	_pass()

# --- encoding ---------------------------------------------------------------------

func _encoding() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var ts: TileSet = d["ts"]
	var sid: int = d["sid"]
	var layer := _mk_layer(ts)
	root.add_child(layer)
	var empty_bytes: PackedByteArray = layer.tile_map_data
	_it("empty_bytes_len", str(empty_bytes.size()))
	_it("empty_arr_len", str(layer.get_tile_map_data_as_array().size()))
	# one cell: (3,4) source 0 atlas (1,0) alt 0
	layer.set_cell(Vector2i(3, 4), sid, Vector2i(1, 0), 0)
	var one: PackedByteArray = layer.tile_map_data
	_it("one_bytes_len", str(one.size()))
	_it("one_bytes", _ints(Array(one)))
	# add a second cell: (7,-2) source 0 atlas (0,1) alt 0
	layer.set_cell(Vector2i(7, -2), sid, Vector2i(0, 1), 0)
	var two: PackedByteArray = layer.tile_map_data
	_it("two_bytes_len", str(two.size()))
	_it("two_bytes", _ints(Array(two)))
	_it("two_arr_len", str(layer.get_tile_map_data_as_array().size()))
	var arr_form: Variant = layer.get_tile_map_data_as_array()
	_it("two_arr_equals_bytes", _b(_ints(arr_form) == _ints(Array(two))))
	# per-cell stride
	_it("stride", str(two.size() - one.size()))
	# an alternative tile changes only the alternative field
	var alt := (ts.get_source(sid) as TileSetAtlasSource).create_alternative_tile(Vector2i(1, 0))
	layer.clear()
	layer.set_cell(Vector2i(3, 4), sid, Vector2i(1, 0), 0)
	var alt_bytes: PackedByteArray = layer.tile_map_data
	_it("alt_bytes", _ints(Array(alt_bytes)))
	_it("alt_id_created", str(alt))
	# erasure is an in-place tombstone, not a removal
	var layer5 := _mk_layer(ts)
	root.add_child(layer5)
	layer5.set_cell(Vector2i(1, 1), sid, Vector2i(0, 0), 0)
	_it("tomb_set_bytes", _ints(Array(layer5.tile_map_data)))
	layer5.erase_cell(Vector2i(1, 1))
	_it("tomb_erase_len", str(layer5.tile_map_data.size()))
	_it("tomb_erase_bytes", _ints(Array(layer5.tile_map_data)))
	_it("tomb_erase_used", _coords(layer5.get_used_cells()))
	layer5.set_cell(Vector2i(1, 1), sid, Vector2i(0, 0), 0)
	_it("tomb_reset_len", str(layer5.tile_map_data.size()))
	_it("tomb_reset_bytes", _ints(Array(layer5.tile_map_data)))
	layer5.clear()
	_it("tomb_clear_len", str(layer5.tile_map_data.size()))
	_it("tomb_clear_bytes", _ints(Array(layer5.tile_map_data)))
	layer5.set_cell(Vector2i(5, 5), sid, Vector2i(0, 0), 0)
	_it("tomb_clear_set_len", str(layer5.tile_map_data.size()))
	_it("tomb_clear_set_bytes", _ints(Array(layer5.tile_map_data)))
	# round trip through the array form
	var layer2 := _mk_layer(ts)
	root.add_child(layer2)
	layer2.set_tile_map_data_from_array(Array(two))
	_it("arr_roundtrip_used", _coords(layer2.get_used_cells()))
	_it("arr_roundtrip_src", str(layer2.get_cell_source_id(Vector2i(7, -2))))
	_it("arr_roundtrip_atlas", _v2i(layer2.get_cell_atlas_coords(Vector2i(7, -2))))
	# malformed arrays are refused by format id
	var layer3 := _mk_layer(ts)
	root.add_child(layer3)
	layer3.set_tile_map_data_from_array([1, 2, 3])
	_it("short_arr_used", _coords(layer3.get_used_cells()))
	_it("short_arr_len", str(layer3.tile_map_data.size()))
	# truncated real data is refused the same way
	var layer4 := _mk_layer(ts)
	root.add_child(layer4)
	var truncated: Array = Array(two)
	truncated.resize(20)
	layer4.set_tile_map_data_from_array(truncated)
	_it("truncated_used", _coords(layer4.get_used_cells()))
	_it("truncated_len", str(layer4.tile_map_data.size()))
	_pass()

# --- fixinvalid -------------------------------------------------------------------

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
	# removing the source invalidates every cell that used it
	ts.remove_source(sid)
	_it("removed_used", _coords(layer.get_used_cells()))
	layer.fix_invalid_tiles()
	_it("removed_fixed_used", _coords(layer.get_used_cells()))
	_pass()

# --- srcids -----------------------------------------------------------------------

func _srcids() -> void:
	var tex := _mk_texture(32, 32)
	var ts := TileSet.new()
	var src := TileSetAtlasSource.new()
	src.texture = tex
	src.create_tile(Vector2i(0, 0))
	var sid := ts.add_source(src)
	_it("auto_id", str(sid))
	_it("next_after_auto", str(ts.get_next_source_id()))
	var src_b := TileSetAtlasSource.new()
	src_b.texture = tex
	var sid_b := ts.add_source(src_b, 5)
	_it("explicit_5", str(sid_b))
	_it("next_after_explicit", str(ts.get_next_source_id()))
	_it("ids", _src_ids(ts))
	_it("id_index_0", str(ts.get_source_id(0)))
	_it("id_index_1", str(ts.get_source_id(1)))
	ts.set_source_id(sid_b, 2)
	_it("moved_ids", _src_ids(ts))
	_it("has_2", _b(ts.has_source(2)))
	_it("has_5", _b(ts.has_source(5)))
	ts.remove_source(2)
	_it("removed_ids", _src_ids(ts))
	_it("count", str(ts.get_source_count()))
	# refusals: null source, colliding id, negative id
	_it("add_null", str(ts.add_source(null)))
	_it("count_after_null", str(ts.get_source_count()))
	var src_c := TileSetAtlasSource.new()
	src_c.texture = tex
	_it("add_colliding", str(ts.add_source(src_c, sid)))
	_it("count_after_colliding", str(ts.get_source_count()))
	var src_d := TileSetAtlasSource.new()
	src_d.texture = tex
	_it("add_negative", str(ts.add_source(src_d, -3)))
	_it("ids_after_refusals", _src_ids(ts))
	_pass()

# --- physics ----------------------------------------------------------------------

func _physics() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var ts: TileSet = d["ts"]
	var src: TileSetAtlasSource = d["src"]
	var sid: int = d["sid"]
	ts.add_physics_layer()
	_it("phys_layers", str(ts.get_physics_layers_count()))
	_it("layer_defaults", "cl=%d cm=%d prio=%.4f mat_null=%s" % [
		ts.get_physics_layer_collision_layer(0), ts.get_physics_layer_collision_mask(0),
		ts.get_physics_layer_collision_priority(0),
		_b(ts.get_physics_layer_physics_material(0) == null)])
	var td := src.get_tile_data(Vector2i(0, 0), 0)
	_it("polys_0", str(td.get_collision_polygons_count(0)))
	td.set_collision_polygons_count(0, 1)
	td.set_collision_polygon_points(0, 0,
		PackedVector2Array([Vector2(-8, -8), Vector2(8, -8), Vector2(8, 8), Vector2(-8, 8)]))
	_it("polys_1", str(td.get_collision_polygons_count(0)))
	_it("poly_pt0", _v2(td.get_collision_polygon_points(0, 0)[0]))
	_it("poly_oneway", _b(td.is_collision_polygon_one_way(0, 0)))
	td.set_collision_polygon_one_way(0, 0, true)
	td.set_collision_polygon_one_way_margin(0, 0, 4.0)
	_it("poly_oneway_set", "%s m=%.4f" % [_b(td.is_collision_polygon_one_way(0, 0)),
		td.get_collision_polygon_one_way_margin(0, 0)])
	td.set_collision_polygon_one_way(0, 0, false)
	# only tile (0,0) carries the polygon
	var layer := _mk_layer(ts)
	root.add_child(layer)
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	layer.set_cell(Vector2i(1, 0), sid, Vector2i(1, 0), 0)
	var probe := _mk_probe()
	root.add_child(probe)
	await physics_frame
	await physics_frame
	_it("tile0", _mc(probe))
	probe.position = Vector2(24, -6)
	await physics_frame
	_it("tile1_no_polygon", _mc(probe))
	probe.position = Vector2(8, -6)
	await physics_frame
	_it("tile0_again", _mc(probe))
	# collision_enabled is a live switch: measure the same-frame readback
	layer.collision_enabled = false
	_it("disabled_same_frame", _mc(probe))
	await physics_frame
	_it("disabled_f1", _mc(probe))
	layer.collision_enabled = true
	_it("enabled_same_frame", _mc(probe))
	await physics_frame
	_it("enabled_f1", _mc(probe))
	# erasing the cell defers to the next physics step
	layer.erase_cell(Vector2i(0, 0))
	_it("erase_same_frame", _mc(probe))
	await physics_frame
	_it("erase_f1", _mc(probe))
	# the collision body is the layer node itself
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	await physics_frame
	await physics_frame
	var hit := probe.move_and_collide(Vector2(0, 20), true)
	if hit == null:
		_it("collider", "null")
	else:
		_it("collider", "class=%s travel=%s normal=%s is_layer=%s shape=%s" % [
			hit.get_collider().get_class(), _v2(hit.get_travel()), _v2(hit.get_normal()),
			_b(hit.get_collider() == layer), str(hit.get_local_shape() != null)])
	# a body RID that the layer does not track refuses and returns the origin cell
	var body_rid: RID = probe.get_rid()
	_it("coords_for_untracked_body", _v2i(layer.get_coords_for_body_rid(body_rid)))
	_it("has_body_rid", _b(layer.has_body_rid(body_rid)))
	# body tracking stays unreachable even with kinematic bodies and a body
	# resting on the tiles: has_body_rid never turns true from script
	layer.use_kinematic_bodies = true
	probe.position = Vector2(8, 8)
	await physics_frame
	await physics_frame
	await physics_frame
	_it("kinematic_use", _b(layer.use_kinematic_bodies))
	_it("kinematic_body_tracked", _b(layer.has_body_rid(body_rid)))
	_it("kinematic_coords", _v2i(layer.get_coords_for_body_rid(body_rid)))
	_pass()

# --- timing -----------------------------------------------------------------------

func _timing() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var ts: TileSet = d["ts"]
	var src: TileSetAtlasSource = d["src"]
	var sid: int = d["sid"]
	_add_phys_tile(ts, src)
	var layer := _mk_layer(ts)
	root.add_child(layer)
	var probe := _mk_probe()
	root.add_child(probe)
	await physics_frame
	await physics_frame
	_it("empty", _mc(probe))
	# the data side of a runtime write is immediate; the physics side is not
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	_it("set_same_frame_physics", _mc(probe))
	_it("set_same_frame_td", "null" if layer.get_cell_tile_data(Vector2i(0, 0)) == null else "obj")
	_it("set_same_frame_used", _b(layer.get_used_cells().has(Vector2i(0, 0))))
	await physics_frame
	_it("set_f1", _mc(probe))
	await physics_frame
	_it("set_f2", _mc(probe))
	# the layer transform defers the same way
	layer.position = Vector2(200, 200)
	_it("move_same_frame", _mc(probe))
	await physics_frame
	_it("move_f1", _mc(probe))
	await physics_frame
	_it("move_f2", _mc(probe))
	layer.position = Vector2(0, 0)
	await physics_frame
	await physics_frame
	_it("moved_back", _mc(probe))
	# erase defers too
	layer.erase_cell(Vector2i(0, 0))
	_it("erase_same_frame", _mc(probe))
	await physics_frame
	_it("erase_f1", _mc(probe))
	# notify_runtime_tile_data_update does not make the physics side synchronous
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	layer.notify_runtime_tile_data_update()
	_it("notify_same_frame", _mc(probe))
	await physics_frame
	_it("notify_f1", _mc(probe))
	# update_internals IS the synchronous apply lever
	layer.erase_cell(Vector2i(0, 0))
	layer.update_internals()
	_it("update_erase_same_frame", _mc(probe))
	await physics_frame
	_it("update_erase_f1", _mc(probe))
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	layer.update_internals()
	_it("update_set_same_frame", _mc(probe))
	# a cell written at frame N is readable as data at frame N (control)
	layer.set_cell(Vector2i(4, 4), sid, Vector2i(0, 0), 0)
	_it("data_immediate_control", _b(layer.get_cell_tile_data(Vector2i(4, 4)) != null))
	_pass()

# --- quadrant ---------------------------------------------------------------------

func _quadrant() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var ts: TileSet = d["ts"]
	var src: TileSetAtlasSource = d["src"]
	var sid: int = d["sid"]
	_add_phys_tile(ts, src)
	var layer := _mk_layer(ts)
	root.add_child(layer)
	_it("default_quad", str(layer.physics_quadrant_size))
	for x in range(0, 20):
		layer.set_cell(Vector2i(x, 0), sid, Vector2i(0, 0), 0)
	var probe := _mk_probe()
	root.add_child(probe)
	await physics_frame
	await physics_frame
	_it("quad16_near", _mc(probe))
	probe.position = Vector2(8 + 16 * 19, -6)
	await physics_frame
	_it("quad16_far", _mc(probe))
	# shrinking the quadrant re-partitions the collision bodies
	layer.set_physics_quadrant_size(2)
	_it("quad_set", str(layer.physics_quadrant_size))
	_it("quad2_same_frame_far", _mc(probe))
	await physics_frame
	_it("quad2_f1_far", _mc(probe))
	probe.position = Vector2(8, -6)
	await physics_frame
	_it("quad2_near", _mc(probe))
	# the quadrant size is a partitioning knob, not a correctness knob: four cells
	# spread across quadrant boundaries all stay collidable under both sizes
	var parts: PackedStringArray = []
	for c in [Vector2i(0, 0), Vector2i(15, 0), Vector2i(16, 0), Vector2i(40, 0)]:
		layer.set_cell(c, sid, Vector2i(0, 0), 0)
	await physics_frame
	await physics_frame
	for c in [Vector2i(0, 0), Vector2i(15, 0), Vector2i(16, 0), Vector2i(40, 0)]:
		probe.position = Vector2(c.x * 16 + 8, -6)
		await physics_frame
		parts.append("%s:%s" % [_v2i(c), _mc(probe)])
	_it("quad2_spread", "|".join(parts))
	layer.set_physics_quadrant_size(16)
	await physics_frame
	await physics_frame
	var parts16: PackedStringArray = []
	for c in [Vector2i(0, 0), Vector2i(15, 0), Vector2i(16, 0), Vector2i(40, 0)]:
		probe.position = Vector2(c.x * 16 + 8, -6)
		await physics_frame
		parts16.append("%s:%s" % [_v2i(c), _mc(probe)])
	_it("quad16_spread", "|".join(parts16))
	# the readback is a plain property
	_it("quad_restored", str(layer.physics_quadrant_size))
	_it("rendering_quad_untouched", str(layer.rendering_quadrant_size))
	_pass()

# --- nav --------------------------------------------------------------------------

func _nav() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var ts: TileSet = d["ts"]
	var src: TileSetAtlasSource = d["src"]
	var sid: int = d["sid"]
	ts.add_navigation_layer()
	_it("nav_layers", str(ts.get_navigation_layers_count()))
	_it("nav_layer_defaults", "layers=%d value1=%s" % [ts.get_navigation_layer_layers(0),
		_b(ts.get_navigation_layer_layer_value(0, 1))])
	ts.set_navigation_layer_layers(0, 3)
	_it("nav_layer_set", str(ts.get_navigation_layer_layers(0)))
	var td := src.get_tile_data(Vector2i(0, 0), 0)
	_it("nav_poly_default", "null" if td.get_navigation_polygon(0) == null else "obj")
	var poly := NavigationPolygon.new()
	poly.add_outline(PackedVector2Array([Vector2(-8, -8), Vector2(8, -8), Vector2(8, 8), Vector2(-8, 8)]))
	poly.make_polygons_from_outlines()
	td.set_navigation_polygon(0, poly)
	_it("nav_poly_set", "null" if td.get_navigation_polygon(0) == null else "obj")
	var layer := _mk_layer(ts)
	root.add_child(layer)
	_it("layer_nav_enabled", _b(layer.navigation_enabled))
	_it("layer_nav_vis", str(layer.navigation_visibility_mode))
	var map: RID = layer.get_navigation_map()
	_it("nav_map_valid", _b(map.is_valid()))
	_it("regions_empty", str(NavigationServer2D.map_get_regions(map).size()))
	# a cell with a navigation polygon registers a region, but not in the same frame
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	_it("regions_same_frame", str(NavigationServer2D.map_get_regions(map).size()))
	await physics_frame
	_it("regions_f1", str(NavigationServer2D.map_get_regions(map).size()))
	await physics_frame
	_it("regions_f2", str(NavigationServer2D.map_get_regions(map).size()))
	# a cell whose tile has no navigation polygon does not register
	layer.set_cell(Vector2i(1, 0), sid, Vector2i(1, 0), 0)
	await physics_frame
	await physics_frame
	_it("regions_after_plain_cell", str(NavigationServer2D.map_get_regions(map).size()))
	# disabling navigation removes the region
	layer.navigation_enabled = false
	_it("regions_disabled_same_frame", str(NavigationServer2D.map_get_regions(map).size()))
	await physics_frame
	_it("regions_disabled_f1", str(NavigationServer2D.map_get_regions(map).size()))
	layer.navigation_enabled = true
	await physics_frame
	await physics_frame
	_it("regions_reenabled", str(NavigationServer2D.map_get_regions(map).size()))
	# erasing the cell removes the region
	layer.erase_cell(Vector2i(0, 0))
	_it("regions_erased_same_frame", str(NavigationServer2D.map_get_regions(map).size()))
	await physics_frame
	_it("regions_erased_f1", str(NavigationServer2D.map_get_regions(map).size()))
	_pass()

# --- nullts (hazard, not a row) ----------------------------------------------------

func _nullts() -> void:
	var layer := TileMapLayer.new()
	root.add_child(layer)
	_it("tileset_null", _b(layer.tile_set == null))
	layer.set_cell(Vector2i(0, 0), 0, Vector2i(0, 0), 0)
	_it("used_after_set", _coords(layer.get_used_cells()))
	_it("src_after_set", str(layer.get_cell_source_id(Vector2i(0, 0))))
	_it("about_to_call_tile_data", "1")
	var td := layer.get_cell_tile_data(Vector2i(0, 0))
	_it("td_after_set", "null" if td == null else "obj")
	_pass()
