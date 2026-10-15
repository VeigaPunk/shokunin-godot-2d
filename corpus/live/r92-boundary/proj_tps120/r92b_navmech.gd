extends SceneTree
# r92-boundary mechanism probe (separate file so the r92b_probe.gd receipts stay frozen).
# Launch: godot --headless [--fixed-fps N] --path <proj> --script res://r92b_navmech.gd -- --arm=mech
# Answers: WHERE does the pending navigation region live when the scout's nav row reads
# `regions_f1`, and what is the in-situ idle:physics ratio of this process?
#   n_same   — region count in the frame of the set_cell (scout: 0)
#   n_force  — after NavigationServer2D.map_force_update(map) in the same frame
#   n_upd    — after layer.update_internals() in the same frame
#   n_proc1  — after ONE await process_frame (idle), no physics await
#   n_proc2  — after a second await process_frame
#   n_f1/n_f2— after 1 / 2 await physics_frame
#   proc_per_phys — idle frames elapsed per physics frame, in situ
#   phys_per_proc — physics steps per idle frame, in situ
# Prints `PASS r92b_navmech mech ...` (battery signature convention).

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
	print("R92M %s %s=%s" % [arm, key, value])

func _pass() -> void:
	print("PASS r92b_navmech %s %s" % [arm, " ".join(_items)])
	quit()

func _b(v: bool) -> String:
	return "1" if v else "0"

func _ints(arr: Array) -> String:
	var parts: PackedStringArray = []
	for v in arr:
		parts.append(str(v))
	return "[%s]" % ",".join(parts)

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
	var sid := ts.add_source(src)
	return {"ts": ts, "src": src, "sid": sid}

func _add_nav_tile(ts: TileSet, src: TileSetAtlasSource) -> void:
	ts.add_navigation_layer()
	var td := src.get_tile_data(Vector2i(0, 0), 0)
	var poly := NavigationPolygon.new()
	poly.add_outline(PackedVector2Array([Vector2(-8, -8), Vector2(8, -8), Vector2(8, 8), Vector2(-8, 8)]))
	poly.make_polygons_from_outlines()
	td.set_navigation_polygon(0, poly)

func _nreg(map: RID) -> int:
	return NavigationServer2D.map_get_regions(map).size()

func _mech() -> void:
	var d := _mk_tileset(_mk_texture(32, 32))
	var ts: TileSet = d["ts"]
	var src: TileSetAtlasSource = d["src"]
	var sid: int = d["sid"]
	_add_nav_tile(ts, src)
	var layer := TileMapLayer.new()
	layer.tile_set = ts
	root.add_child(layer)
	var map: RID = layer.get_navigation_map()
	# in-situ scheduler ratio before the write
	var proc_deltas: Array = []
	var phys_deltas: Array = []
	var last_p := Engine.get_physics_frames()
	var last_pr := Engine.get_process_frames()
	for i in 8:
		await physics_frame
		var p := Engine.get_physics_frames()
		var pr := Engine.get_process_frames()
		phys_deltas.append(p - last_p)
		proc_deltas.append(pr - last_pr)
		last_p = p
		last_pr = pr
	_it("phys_per_await", _ints(phys_deltas))
	_it("proc_per_phys", _ints(proc_deltas))
	# the write and the four same-frame levers
	_it("n_empty", str(_nreg(map)))
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	_it("n_same", str(_nreg(map)))
	NavigationServer2D.map_force_update(map)
	_it("n_force", str(_nreg(map)))
	layer.update_internals()
	_it("n_upd", str(_nreg(map)))
	# idle awaits only
	await process_frame
	_it("n_proc1", str(_nreg(map)))
	await process_frame
	_it("n_proc2", str(_nreg(map)))
	# physics awaits
	await physics_frame
	_it("n_f1", str(_nreg(map)))
	await physics_frame
	_it("n_f2", str(_nreg(map)))
	await physics_frame
	_it("n_f3", str(_nreg(map)))
	# the reverse direction: does erase also take 2 steps?
	layer.erase_cell(Vector2i(0, 0))
	_it("n_erase_same", str(_nreg(map)))
	await physics_frame
	_it("n_erase_f1", str(_nreg(map)))
	await physics_frame
	_it("n_erase_f2", str(_nreg(map)))
	_it("iter_final", str(NavigationServer2D.map_get_iteration_id(map)))
	_pass()

func _run() -> void:
	if arm == "":
		print("FAIL r92b_navmech reason=empty_arm")
		quit(1)
		return
	var watchdog := create_timer(20.0)
	watchdog.timeout.connect(func() -> void:
		print("FAIL r92b_navmech %s reason=watchdog" % arm)
		quit(1))
	match arm:
		"mech":
			await _mech()
		"cold":
			await _cold()
		_:
			print("FAIL r92b_navmech %s reason=unknown_arm" % arm)
			quit(1)

# Cold arm: reproduce the scout nav arm's phase exactly — write the first cell with NO
# prior physics step, then poll the server region count per physics frame. This is the
# phase the scout's `regions_f1` key measures.
func _cold() -> void:
	var d := _mk_tileset(_mk_texture(32, 32))
	var ts: TileSet = d["ts"]
	var src: TileSetAtlasSource = d["src"]
	var sid: int = d["sid"]
	_add_nav_tile(ts, src)
	var layer := TileMapLayer.new()
	layer.tile_set = ts
	root.add_child(layer)
	var map: RID = layer.get_navigation_map()
	_it("n_empty", str(_nreg(map)))
	layer.set_cell(Vector2i(0, 0), sid, Vector2i(0, 0), 0)
	_it("n_same", str(_nreg(map)))
	var t := -1
	for i in POLL:
		await physics_frame
		if _nreg(map) == 1:
			t = i + 1
			break
	_it("t_cold_add", str(t))
	layer.erase_cell(Vector2i(0, 0))
	_it("n_erase_same", str(_nreg(map)))
	var te := -1
	for i in POLL:
		await physics_frame
		if _nreg(map) == 0:
			te = i + 1
			break
	_it("t_cold_erase", str(te))
	# in-situ ratio, measured after the poll window
	var proc_deltas: Array = []
	var last_pr := Engine.get_process_frames()
	for i in 8:
		await physics_frame
		var pr := Engine.get_process_frames()
		proc_deltas.append(pr - last_pr)
		last_pr = pr
	_it("proc_per_phys", _ints(proc_deltas))
	_pass()
