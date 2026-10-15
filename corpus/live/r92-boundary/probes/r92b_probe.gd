extends SceneTree
# r92-boundary probe — scheduler-sensitivity attack on the r92 TileMapLayer scout rows.
# Launch shape:
#   godot --headless [--fixed-fps N] --path proj --script res://r92b_probe.gd -- --arm=<arm>
# Every arm prints `R92B <arm> <key>=<value>` diagnostics and one final
# `PASS r92b_tilemap <arm> ...` line (battery signature convention).
#
# Arms:
#   sched — scheduler introspection: physics frames per `await physics_frame`,
#           process (idle) frames per physics frame, physics frames per
#           `await process_frame`, wall usec per physics frame. This is the receipt
#           of WHAT --fixed-fps actually changes (the idle:physics ratio).
#   phys  — per-physics-frame latency pollers for the five physics levers the scout
#           pinned as "exactly one physics step" (set_cell / erase_cell /
#           collision_enabled / transform / update_internals / notify_*). A `t=N`
#           means the lever became visible after N `await physics_frame`; t=-1 means
#           not within POLL frames. Also the idle-frame discriminator: the same
#           write read after ONE `await process_frame` (mode-dependent by construction).
#   nav   — per-physics-frame latency pollers for NavigationServer2D region
#           registration/removal (the scout's nav row), plus the map iteration-id
#           cadence per physics frame (the r91 fixed-fps stall surface).
#
# No object ids / RIDs / addresses are printed (byte-stability).
# A 20 s watchdog quits FAIL instead of hanging.

const POLL := 24

var arm := ""
var _items: PackedStringArray = []

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")

func _it(key: String, value: String) -> void:
	_items.append("%s=%s" % [key, value])
	print("R92B %s %s=%s" % [arm, key, value])

func _pass() -> void:
	print("PASS r92b_tilemap %s %s" % [arm, " ".join(_items)])
	quit()

func _fail(reason: String) -> void:
	print("FAIL r92b_tilemap %s reason=%s" % [arm, reason])
	quit(1)

func _v2(p: Vector2) -> String:
	return "%.4f,%.4f" % [p.x, p.y]

func _v2i(p: Vector2i) -> String:
	return "%d,%d" % [p.x, p.y]

func _b(v: bool) -> String:
	return "1" if v else "0"

func _ints(arr: Array) -> String:
	var parts: PackedStringArray = []
	for v in arr:
		parts.append(str(v))
	return "[%s]" % ",".join(parts)

# --- shared construction (mirrors the scout probe) -------------------------------

func _mk_texture(w: int, h: int) -> ImageTexture:
	var img := Image.create_empty(w, h, false, Image.FORMAT_RGBA8)
	img.fill(Color(1, 1, 1, 1))
	return ImageTexture.create_from_image(img)

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

func _add_phys_tile(ts: TileSet, src: TileSetAtlasSource) -> void:
	ts.add_physics_layer()
	var td := src.get_tile_data(Vector2i(0, 0), 0)
	td.set_collision_polygons_count(0, 1)
	td.set_collision_polygon_points(0, 0,
		PackedVector2Array([Vector2(-8, -8), Vector2(8, -8), Vector2(8, 8), Vector2(-8, 8)]))

func _add_nav_tile(ts: TileSet, src: TileSetAtlasSource) -> void:
	ts.add_navigation_layer()
	var td := src.get_tile_data(Vector2i(0, 0), 0)
	var poly := NavigationPolygon.new()
	poly.add_outline(PackedVector2Array([Vector2(-8, -8), Vector2(8, -8), Vector2(8, 8), Vector2(-8, 8)]))
	poly.make_polygons_from_outlines()
	td.set_navigation_polygon(0, poly)

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

# Poll a zero-arg witness once per physics frame; returns frames-to-want, or -1.
func _poll(cb: Callable, want: String, maxn: int) -> int:
	for i in maxn:
		await physics_frame
		if cb.call() == want:
			return i + 1
	return -1

func _nreg(map: RID) -> int:
	return NavigationServer2D.map_get_regions(map).size()

func _poll_nreg(map: RID, want: int, maxn: int) -> int:
	for i in maxn:
		await physics_frame
		if _nreg(map) == want:
			return i + 1
	return -1

# --- sched ------------------------------------------------------------------------

func _sched() -> void:
	_it("cmdline", "|".join(OS.get_cmdline_args()))
	_it("user_args", "|".join(OS.get_cmdline_user_args()))
	_it("physics_tps", str(Engine.physics_ticks_per_second))
	_it("max_fps", str(Engine.max_fps))
	_it("time_scale", "%.4f" % Engine.time_scale)
	var phys_deltas: Array = []
	var proc_deltas: Array = []
	var last_p := Engine.get_physics_frames()
	var last_pr := Engine.get_process_frames()
	var t0 := Time.get_ticks_usec()
	for i in 12:
		await physics_frame
		var p := Engine.get_physics_frames()
		var pr := Engine.get_process_frames()
		phys_deltas.append(p - last_p)
		proc_deltas.append(pr - last_pr)
		last_p = p
		last_pr = pr
	var t1 := Time.get_ticks_usec()
	_it("phys_per_await", _ints(phys_deltas))
	_it("proc_per_phys_await", _ints(proc_deltas))
	_it("usec_per_phys_frame", "%.1f" % (float(t1 - t0) / 12.0))
	var proc_await_phys: Array = []
	var last_p2 := Engine.get_physics_frames()
	for i in 12:
		await process_frame
		var p2 := Engine.get_physics_frames()
		proc_await_phys.append(p2 - last_p2)
		last_p2 = p2
	_it("phys_per_proc_await", _ints(proc_await_phys))
	_pass()

# --- phys -------------------------------------------------------------------------

func _phys() -> void:
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
	# set_cell: frames until the collision exists (scout: same-frame stale, f1 hit)
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	_it("set_same", _mc(probe))
	_it("t_set", str(await _poll(_mc.bind(probe), "hit", POLL)))
	# erase_cell: frames until the collision is gone
	layer.erase_cell(Vector2i(0, 0))
	_it("erase_same", _mc(probe))
	_it("t_erase", str(await _poll(_mc.bind(probe), "null", POLL)))
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	_it("t_set2", str(await _poll(_mc.bind(probe), "hit", POLL)))
	# collision_enabled
	layer.collision_enabled = false
	_it("dis_same", _mc(probe))
	_it("t_dis", str(await _poll(_mc.bind(probe), "null", POLL)))
	layer.collision_enabled = true
	_it("en_same", _mc(probe))
	_it("t_en", str(await _poll(_mc.bind(probe), "hit", POLL)))
	# transform
	layer.position = Vector2(200, 200)
	_it("mv_same", _mc(probe))
	_it("t_mv", str(await _poll(_mc.bind(probe), "null", POLL)))
	layer.position = Vector2(0, 0)
	_it("t_mv_back", str(await _poll(_mc.bind(probe), "hit", POLL)))
	# update_internals is synchronous; notify_runtime_tile_data_update is not
	layer.erase_cell(Vector2i(0, 0))
	layer.update_internals()
	_it("upd_erase_same", _mc(probe))
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	layer.update_internals()
	_it("upd_set_same", _mc(probe))
	layer.erase_cell(Vector2i(0, 0))
	layer.notify_runtime_tile_data_update()
	_it("notify_erase_same", _mc(probe))
	_it("t_notify_erase", str(await _poll(_mc.bind(probe), "null", POLL)))
	# idle-frame discriminator: the same write read after ONE await process_frame.
	# A physics-step law makes this mode-dependent by construction (ff120: 0 physics
	# steps per idle frame; ff30: 2).
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	_it("t_set3", str(await _poll(_mc.bind(probe), "hit", POLL)))
	layer.erase_cell(Vector2i(0, 0))
	await process_frame
	_it("proc_await_erase", _mc(probe))
	_it("t_erase2", str(await _poll(_mc.bind(probe), "null", POLL)))
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	await process_frame
	_it("proc_await_set", _mc(probe))
	_it("t_set4", str(await _poll(_mc.bind(probe), "hit", POLL)))
	# control: data side is immediate in every mode
	layer.set_cell(Vector2i(4, 4), sid, Vector2i(0, 0), 0)
	_it("data_immediate", _b(layer.get_cell_tile_data(Vector2i(4, 4)) != null))
	_pass()

# --- nav --------------------------------------------------------------------------

func _nav() -> void:
	var tex := _mk_texture(32, 32)
	var d := _mk_tileset(tex)
	var ts: TileSet = d["ts"]
	var src: TileSetAtlasSource = d["src"]
	var sid: int = d["sid"]
	_add_nav_tile(ts, src)
	var layer := _mk_layer(ts)
	root.add_child(layer)
	var map: RID = layer.get_navigation_map()
	_it("map_valid", _b(map.is_valid()))
	_it("iter_empty", str(NavigationServer2D.map_get_iteration_id(map)))
	_it("regions_empty", str(_nreg(map)))
	# a nav-polygon cell registers a region
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	_it("reg_same", str(_nreg(map)))
	_it("t_reg_add", str(await _poll_nreg(map, 1, POLL)))
	_it("iter_after_add", str(NavigationServer2D.map_get_iteration_id(map)))
	# map iteration-id cadence per physics frame while the map is live
	var iters: Array = []
	var last_it := NavigationServer2D.map_get_iteration_id(map)
	for i in 12:
		await physics_frame
		var it := NavigationServer2D.map_get_iteration_id(map)
		iters.append(it - last_it)
		last_it = it
	_it("iter_deltas", _ints(iters))
	# a cell whose tile has no nav polygon must not add a region
	layer.set_cell(Vector2i(1, 0), sid, Vector2i(1, 0), 0)
	_it("t_reg_plain_to2", str(await _poll_nreg(map, 2, POLL)))
	_it("regions_after_plain", str(_nreg(map)))
	# disable / re-enable / erase
	layer.navigation_enabled = false
	_it("dis_same", str(_nreg(map)))
	_it("t_reg_dis", str(await _poll_nreg(map, 0, POLL)))
	layer.navigation_enabled = true
	_it("t_reg_reen", str(await _poll_nreg(map, 1, POLL)))
	layer.erase_cell(Vector2i(0, 0))
	_it("erase_same", str(_nreg(map)))
	_it("t_reg_erase", str(await _poll_nreg(map, 0, POLL)))
	for i in 6:
		await physics_frame
	_it("iter_settled", str(NavigationServer2D.map_get_iteration_id(map)))
	_it("regions_settled", str(_nreg(map)))
	_pass()

# --- dispatch ---------------------------------------------------------------------

func _run() -> void:
	print("arm=%s" % arm)
	if arm == "":
		_fail("empty_arm")
		return
	var watchdog := create_timer(20.0)
	watchdog.timeout.connect(func() -> void:
		print("FAIL r92b_tilemap %s reason=watchdog" % arm)
		quit(1))
	match arm:
		"sched":
			await _sched()
		"phys":
			await _phys()
		"nav":
			await _nav()
		_:
			_fail("unknown_arm")
