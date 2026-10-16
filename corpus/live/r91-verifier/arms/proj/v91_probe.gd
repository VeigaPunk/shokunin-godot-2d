extends SceneTree
# r91 verifier-owned independent probe — NOT the author's fixture.
# Arms re-derive the four boundary folds and two laws on verifier-built rigs:
#   agent_order / agent_reached_only : fin-before-reached query-order artifact
#   maxrad                           : path_return_max_radius semantics ladder
#   gate                             : iteration_id>=2 AND reach gate law
#   avoid_bound                      : ORCA bound on a different radii pair
#   teardown_*                       : live-vs-cleared callback crash qualifier

const SYNC_BOUND := 48
var _exit_code := 0

func _arg(name: String, def: String = "") -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--" + name + "="):
			return a.substr(name.length() + 3)
	return def

func _v(v: Vector2) -> String:
	return "(%.4f,%.4f)" % [v.x, v.y]

func _path(p: PackedVector2Array) -> String:
	var parts: Array[String] = []
	for v in p:
		parts.append(_v(v))
	return "[" + ",".join(parts) + "]"

func _quad_poly(x0: float, y0: float, x1: float, y1: float) -> NavigationPolygon:
	var p := NavigationPolygon.new()
	p.vertices = PackedVector2Array([Vector2(x0, y0), Vector2(x1, y0), Vector2(x1, y1), Vector2(x0, y1)])
	p.add_polygon(PackedInt32Array([0, 1, 2, 3]))
	return p

func _server_region(map: RID, poly: NavigationPolygon) -> RID:
	var r := NavigationServer2D.region_create()
	NavigationServer2D.region_set_map(r, map)
	NavigationServer2D.region_set_navigation_polygon(r, poly)
	return r

func _new_map() -> RID:
	var m := NavigationServer2D.map_create()
	NavigationServer2D.map_set_active(m, true)
	return m

func _await_frames(n: int) -> void:
	for i in range(n):
		await physics_frame

func _reach(map: RID, from: Vector2, to: Vector2) -> bool:
	var p := NavigationServer2D.map_get_path(map, from, to, true)
	return p.size() > 0 and p[p.size() - 1].distance_to(to) < 0.5

func _await_sync(map: RID, from: Vector2, to: Vector2, max_frames: int = SYNC_BOUND) -> int:
	var frames := 0
	while frames < max_frames:
		if NavigationServer2D.map_get_iteration_id(map) >= 2 and _reach(map, from, to):
			return frames
		await physics_frame
		frames += 1
	return -1

func _qresult(map: RID, from: Vector2, to: Vector2, pp: int, maxlen: float = 0.0,
		maxrad: float = 0.0, maxdist: float = 0.0, maxpolys: int = 0,
		simpl: bool = false, eps: float = 0.0, layers: int = 1) -> NavigationPathQueryResult2D:
	var qp := NavigationPathQueryParameters2D.new()
	qp.map = map
	qp.start_position = from
	qp.target_position = to
	qp.path_postprocessing = pp
	qp.metadata_flags = NavigationPathQueryParameters2D.PATH_METADATA_INCLUDE_NONE
	qp.navigation_layers = layers
	qp.path_return_max_length = maxlen
	qp.path_return_max_radius = maxrad
	qp.path_search_max_distance = maxdist
	qp.path_search_max_polygons = maxpolys
	qp.simplify_path = simpl
	qp.simplify_epsilon = eps
	var qr := NavigationPathQueryResult2D.new()
	NavigationServer2D.query_path(qp, qr)
	return qr

func _poly_len(p: PackedVector2Array) -> float:
	var total := 0.0
	for i in range(1, p.size()):
		total += p[i - 1].distance_to(p[i])
	return total

func _initialize() -> void:
	var arm := _arg("arm", "")
	match arm:
		"agent_order": await _arm_agent_order(false)
		"agent_reached_only": await _arm_agent_order(true)
		"maxrad": await _arm_maxrad()
		"gate": await _arm_gate()
		"avoid_bound": await _arm_avoid_bound(10.0, Vector2(150, 150), Vector2(190, 150), 1.0)
		"avoid_bound_gap30": await _arm_avoid_bound(5.0, Vector2(150, 150), Vector2(190, 150), 1.0)
		"avoid_bound_gap50": await _arm_avoid_bound(5.0, Vector2(140, 150), Vector2(200, 150), 1.0)
		"avoid_bound_gap40_r10": await _arm_avoid_bound(10.0, Vector2(140, 150), Vector2(200, 150), 1.0)
		"avoid_bound_tau2": await _arm_avoid_bound(5.0, Vector2(150, 150), Vector2(190, 150), 2.0)
		"teardown_live": await _arm_teardown(true, true)
		"teardown_cleared": await _arm_teardown(false, true)
		"teardown_leak_live": await _arm_teardown(true, false)
		"teardown_leak_cleared": await _arm_teardown(false, false)
		_:
			print("V91 unknown arm=", arm)
	quit(_exit_code)

# ------------------------------------------------- agent query-order artifact
func _arm_agent_order(reached_only: bool) -> void:
	var root := Node2D.new()
	get_root().add_child(root)
	var reg := NavigationRegion2D.new()
	reg.navigation_polygon = _quad_poly(0, 0, 200, 200)
	root.add_child(reg)
	var holder := Node2D.new()
	holder.position = Vector2(20, 20)
	reg.add_child(holder)
	var ag := NavigationAgent2D.new()
	ag.path_desired_distance = 4.0
	ag.target_desired_distance = 8.0
	holder.add_child(ag)
	ag.target_position = Vector2(180, 180)
	var waited := 0
	while waited < SYNC_BOUND:
		await physics_frame
		waited += 1
		if ag.is_target_reachable():
			break
	# walk on position only (no agent-state reads until the triple read)
	var steps := 0
	while steps < 80 and holder.position.distance_to(Vector2(180, 180)) > ag.target_desired_distance:
		var next := ag.get_next_path_position()
		holder.position = holder.position.move_toward(next, 8.0)
		steps += 1
		await physics_frame
	if reached_only:
		var ro := ag.is_target_reached()
		print("V91 agent_reached_only waited=", waited, " steps=", steps, " reached_only=", ro)
	else:
		var r1 := ag.is_target_reached()
		var f := ag.is_navigation_finished()
		var r2 := ag.is_target_reached()
		print("V91 agent_order waited=", waited, " steps=", steps,
			" r1=", r1, " fin=", f, " r2=", r2,
			" dist=%.4f" % holder.position.distance_to(Vector2(180, 180)))
	root.queue_free()
	await physics_frame

# ------------------------------------------------- maxrad semantics ladder
func _arm_maxrad() -> void:
	var map := _new_map()
	var rv := _server_region(map, _quad_poly(0, 0, 40, 200))
	var rh := _server_region(map, _quad_poly(40, 0, 200, 40))
	var settle := await _await_sync(map, Vector2(20, 180), Vector2(180, 20))
	if settle < 0:
		print("V91 maxrad STALE")
		_exit_code = 2
		return
	for radius in [0.0, 1.0, 5.0, 10.0, 20.0, 30.0, 60.0, 120.0, 226.0, 300.0]:
		var r := _qresult(map, Vector2(20, 180), Vector2(180, 20),
			NavigationPathQueryParameters2D.PATH_POSTPROCESSING_NONE, 0.0, radius)
		var p := r.get_path()
		var end_dist := p[0].distance_to(p[p.size() - 1]) if p.size() > 0 else -1.0
		print("V91 maxrad R=%.1f n=%d end_dist=%.4f poly_len=%.4f path_len=%.4f path=%s"
			% [radius, p.size(), end_dist, _poly_len(p), r.get_path_length(), _path(p)])
	for pp in [NavigationPathQueryParameters2D.PATH_POSTPROCESSING_NONE,
			NavigationPathQueryParameters2D.PATH_POSTPROCESSING_CORRIDORFUNNEL,
			NavigationPathQueryParameters2D.PATH_POSTPROCESSING_EDGECENTERED]:
		var r := _qresult(map, Vector2(20, 180), Vector2(180, 20), pp)
		print("V91 pp=%d n=%d poly_len=%.4f path_len=%.4f path=%s"
			% [pp, r.get_path().size(), _poly_len(r.get_path()), r.get_path_length(), _path(r.get_path())])
	NavigationServer2D.free_rid(rv)
	NavigationServer2D.free_rid(rh)
	NavigationServer2D.free_rid(map)

# ------------------------------------------------- gate law
func _arm_gate() -> void:
	for rep in range(3):
		var map := _new_map()
		var reg := _server_region(map, _quad_poly(0, 0, 100, 100))
		var first_reach := -1
		var iter_at_reach := -1
		var reach_before_iter2 := false
		for i in range(60):
			await physics_frame
			var it := NavigationServer2D.map_get_iteration_id(map)
			var r := _reach(map, Vector2(10, 10), Vector2(90, 90))
			if r and first_reach < 0:
				first_reach = i
				iter_at_reach = it
			if r and it < 2:
				reach_before_iter2 = true
		print("V91 gate rep=", rep, " first_reach=", first_reach,
			" iter_at_reach=", iter_at_reach, " reach_before_iter2=", reach_before_iter2)
		NavigationServer2D.free_rid(reg)
		NavigationServer2D.free_rid(map)

# ------------------------------------------------- ORCA bound on own rig
func _arm_avoid_bound(radius: float, pa: Vector2, pb: Vector2, tau: float) -> void:
	var map := _new_map()
	var reg := _server_region(map, _quad_poly(0, 0, 400, 300))
	var settle := await _await_sync(map, pa, pb)
	if settle < 0:
		print("V91 avoid_bound STALE")
		_exit_code = 2
		return
	var a := NavigationServer2D.agent_create()
	var b := NavigationServer2D.agent_create()
	var hits_a: Array[Vector2] = []
	var hits_b: Array[Vector2] = []
	NavigationServer2D.agent_set_avoidance_callback(a, func(v: Vector2) -> void:
		hits_a.append(v))
	NavigationServer2D.agent_set_avoidance_callback(b, func(v: Vector2) -> void:
		hits_b.append(v))
	for ag in [a, b]:
		NavigationServer2D.agent_set_map(ag, map)
		NavigationServer2D.agent_set_avoidance_enabled(ag, true)
		NavigationServer2D.agent_set_radius(ag, radius)
		NavigationServer2D.agent_set_max_speed(ag, 50.0)
		NavigationServer2D.agent_set_neighbor_distance(ag, 200.0)
		NavigationServer2D.agent_set_max_neighbors(ag, 8)
		NavigationServer2D.agent_set_time_horizon_agents(ag, tau)
		NavigationServer2D.agent_set_time_horizon_obstacles(ag, tau)
	for i in range(16):
		NavigationServer2D.agent_set_position(a, pa)
		NavigationServer2D.agent_set_position(b, pb)
		NavigationServer2D.agent_set_velocity(a, Vector2(50, 0))
		NavigationServer2D.agent_set_velocity(b, Vector2(-50, 0))
		await physics_frame
	var sums: Array[float] = []
	var last_ia := hits_a.size()
	var last_ib := hits_b.size()
	var dir_ok := true
	for i in range(5):
		NavigationServer2D.agent_set_position(a, pa)
		NavigationServer2D.agent_set_position(b, pb)
		NavigationServer2D.agent_set_velocity(a, Vector2(50, 0))
		NavigationServer2D.agent_set_velocity(b, Vector2(-50, 0))
		await physics_frame
		if hits_a.size() > last_ia and hits_b.size() > last_ib:
			var va: Vector2 = hits_a[hits_a.size() - 1]
			var vb: Vector2 = hits_b[hits_b.size() - 1]
			sums.append(absf(va.x) + absf(vb.x))
			if not (va.x > 0.0 and vb.x < 0.0):
				dir_ok = false
		last_ia = hits_a.size()
		last_ib = hits_b.size()
	var smax := 0.0
	for s in sums:
		if s > smax:
			smax = s
	var gap := pa.distance_to(pb) - 2.0 * radius
	print("V91 avoid_bound r=", radius, " d=", pa.distance_to(pb), " gap=%.4f" % gap,
		" tau=%.1f" % tau, " gap_over_tau=%.4f" % (gap / tau),
		" radii_sum=%.4f" % (2.0 * radius),
		" n_a=", hits_a.size(), " n_b=", hits_b.size(),
		" n_sums=", sums.size(), " sum_max=%.4f" % smax, " dir_ok=", dir_ok,
		" sums=", sums)
	NavigationServer2D.agent_set_avoidance_callback(a, Callable())
	NavigationServer2D.agent_set_avoidance_callback(b, Callable())
	await _await_frames(2)
	NavigationServer2D.free_rid(a)
	NavigationServer2D.free_rid(b)
	NavigationServer2D.free_rid(reg)
	NavigationServer2D.free_rid(map)

# ------------------------------------------------- teardown qualifier
func _arm_teardown(live_cb: bool, do_free: bool) -> void:
	var map := _new_map()
	var a := NavigationServer2D.agent_create()
	var hits: Array[Vector2] = []
	NavigationServer2D.agent_set_map(a, map)
	NavigationServer2D.agent_set_avoidance_enabled(a, true)
	NavigationServer2D.agent_set_avoidance_callback(a, func(v: Vector2) -> void:
		hits.append(v))
	await _await_frames(3)
	print("V91_TEARDOWN live_cb=", live_cb, " free=", do_free,
		" has_cb=", NavigationServer2D.agent_has_avoidance_callback(a))
	if not live_cb:
		NavigationServer2D.agent_set_avoidance_callback(a, Callable())
		await _await_frames(1)
	if do_free:
		NavigationServer2D.free_rid(a)
		NavigationServer2D.free_rid(map)
