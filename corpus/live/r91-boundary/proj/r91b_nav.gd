extends SceneTree
# r91b boundary probe — attack the r91 Navigation2D scout claims.
# Launch shape: godot --headless [--fixed-fps N] --path proj --script res://r91b_nav.gd -- --arm=<arm>
# Every arm prints exactly one `PASS r91b_nav <arm> ...` line (battery signature convention).
# Crash-discipline arms additionally print SURVIVED only if the documented crash did NOT happen.
#
# Arms and the claim each attacks (r91-scout report §3/§4/§5):
#   gate    — sync-gate ladder: `map_get_iteration_id >= 2` necessity/sufficiency,
#             physics-frame accounting (pf_per_await), async=false lane, and the
#             async=false live-change timing the scout left unmeasured (§8).
#   change  — per-frame application timing for 7 live levers (scout law: "2-4 physics
#             frames later", §4.2). Polls each lever to settle and records stale same-frame
#             reads; t=-1 = not applied within 12 frames (unstated-mode hunt).
#   agent   — NavigationAgent2D fin/reached flip split instrumented per frame (scout §3.6:
#             "reached_at=-1 while fin=true"); lane B varies target_desired_distance.
#   avoid   — avoidance callback cadence (once per agent per frame), closing-speed
#             invariant |a|+|b| (~19.85), per-frame hit counts (scout §3.7/§4.5).
#   bake    — both bake routes + collider-only control + orphan refusal (scout §3.8).
#   crash_noclear  — free an agent with a live callback (no clear): expect rc=134.
#   crash_clear0   — clear callback, free same frame: expect rc=134 (navfree2 class).
#   clean_clear1   — clear callback, await 1 frame, free: expect rc=0 (scout discipline).
#   clean_clear2   — clear callback, await 2 frames, free: expect rc=0.
#   leak_cb        — live callback, no free, exit: expect rc=134 (leak-at-exit class).
#   leak_clean     — cleared callback, no free, exit: mode hunt (unknown).
#
# All nav geometry mirrors the scout's frozen probe (nav_lattice.gd, sha256 efb496e5…) so
# every measurement is directly comparable to its rows.

const POLL := 24

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

func _ps(arr: Array) -> String:
	var parts: Array[String] = []
	for s in arr:
		parts.append(str(s))
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

func _await_sync(map: RID, from: Vector2, to: Vector2, max_frames: int = 24) -> int:
	var frames := 0
	while frames < max_frames:
		await physics_frame
		frames += 1
		if NavigationServer2D.map_get_iteration_id(map) >= 2 and _reach(map, from, to):
			break
	return frames

# Poll up to n physics frames for pred; return the 1-based frame the predicate first held,
# or -1 if it never held within n (an unstated-mode signal).
func _poll_frames(n: int, pred: Callable) -> int:
	for i in range(n):
		await physics_frame
		if pred.call():
			return i + 1
	return -1

func _has_waypoint(p: PackedVector2Array, wp: Vector2, eps: float = 0.6) -> bool:
	for v in p:
		if v.distance_to(wp) < eps:
			return true
	return false

func _routes_top(map: RID) -> bool:
	return _has_waypoint(NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(90, 50), true), Vector2(80, 60))

func _routes_bottom(map: RID) -> bool:
	return _has_waypoint(NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(90, 50), true), Vector2(80, 40))

func _initialize() -> void:
	var arm := _arg("arm", "gate")
	match arm:
		"gate": await _arm_gate()
		"change": await _arm_change()
		"agent": await _arm_agent()
		"avoid": await _arm_avoid()
		"bake": await _arm_bake()
		"crash_noclear": await _arm_crash_noclear()
		"crash_clear0": await _arm_crash_clear0()
		"clean_clear1": await _arm_clean_clear1()
		"clean_clear2": await _arm_clean_clear2()
		"leak_cb": await _arm_leak_cb()
		"leak_clean": await _arm_leak_clean()
		_:
			print("PASS r91b_nav unknown arm=", arm)
	quit(0)

# ---------------------------------------------------------------- gate
func _arm_gate() -> void:
	var map := _new_map()
	var reg := _server_region(map, _quad_poly(0, 0, 100, 100))
	var pre_iter := NavigationServer2D.map_get_iteration_id(map)
	var pre_regions := NavigationServer2D.map_get_regions(map).size()
	var pre_path := _path(NavigationServer2D.map_get_path(map, Vector2(10, 10), Vector2(90, 90), true))
	var pre_closest := _v(NavigationServer2D.map_get_closest_point(map, Vector2(50, 50)))
	var pf_start := Engine.get_physics_frames()
	var proc_start := Engine.get_process_frames()
	var trace: Array[String] = []
	var first_iter1 := -1
	var first_iter2 := -1
	var first_reach := -1
	var reach_before_iter2 := false
	var gate_first := -1
	var pf_at_reach := -1
	var cfg_at_iter1 := "unset"
	var cfg_at_iter2 := "unset"
	for i in range(60):
		await physics_frame
		var it := NavigationServer2D.map_get_iteration_id(map)
		var ri := NavigationServer2D.region_get_iteration_id(reg)
		var rc := _reach(map, Vector2(10, 10), Vector2(90, 90))
		if i < 12 or first_reach < 0:
			trace.append("f%d:%d/%d/%s" % [i + 1, it, ri, "1" if rc else "0"])
		if first_iter1 < 0 and it >= 1:
			first_iter1 = i + 1
			cfg_at_iter1 = "cell=%.1f,edge=%.1f,useedge=%s,async=%s,active=%s" % [
				NavigationServer2D.map_get_cell_size(map),
				NavigationServer2D.map_get_edge_connection_margin(map),
				NavigationServer2D.map_get_use_edge_connections(map),
				NavigationServer2D.map_get_use_async_iterations(map),
				NavigationServer2D.map_is_active(map)]
		if first_iter2 < 0 and it >= 2:
			first_iter2 = i + 1
			cfg_at_iter2 = "cell=%.1f,edge=%.1f,link=%.1f,merge=%.2f,useedge=%s,async=%s,active=%s" % [
				NavigationServer2D.map_get_cell_size(map),
				NavigationServer2D.map_get_edge_connection_margin(map),
				NavigationServer2D.map_get_link_connection_radius(map),
				NavigationServer2D.map_get_merge_rasterizer_cell_scale(map),
				NavigationServer2D.map_get_use_edge_connections(map),
				NavigationServer2D.map_get_use_async_iterations(map),
				NavigationServer2D.map_is_active(map)]
		if first_reach < 0 and rc:
			first_reach = i + 1
			pf_at_reach = Engine.get_physics_frames()
		if rc and it < 2:
			reach_before_iter2 = true
		if gate_first < 0 and it >= 2 and rc:
			gate_first = i + 1
		if first_reach >= 0 and i + 1 >= first_reach + 1:
			break
	var pf_per_await := 0.0
	var proc_per_await := 0.0
	if first_reach > 0 and pf_at_reach > 0:
		pf_per_await = float(pf_at_reach - pf_start) / float(first_reach)
		proc_per_await = float(Engine.get_process_frames() - proc_start) / float(first_reach)
	var frames_iter2_to_reach := -1
	if first_reach > 0 and first_iter2 > 0:
		frames_iter2_to_reach = first_reach - first_iter2
	# async=false lane A (scout §3.3: first reachable frame f1) + live-change timing (§8 unknown)
	var map2 := _new_map()
	NavigationServer2D.map_set_use_async_iterations(map2, false)
	var reg2 := _server_region(map2, _quad_poly(0, 0, 100, 100))
	var trace2: Array[String] = []
	var first_reach_sync := -1
	var pf2_start := Engine.get_physics_frames()
	var proc2_start := Engine.get_process_frames()
	var pf2_at_reach := -1
	for i in range(40):
		await physics_frame
		var it2 := NavigationServer2D.map_get_iteration_id(map2)
		var ri2 := NavigationServer2D.region_get_iteration_id(reg2)
		var rc2 := _reach(map2, Vector2(10, 10), Vector2(90, 90))
		trace2.append("f%d:%d/%d/%s" % [i + 1, it2, ri2, "1" if rc2 else "0"])
		if first_reach_sync < 0 and rc2:
			first_reach_sync = i + 1
			pf2_at_reach = Engine.get_physics_frames()
		if first_reach_sync >= 0 and i + 1 >= first_reach_sync + 1:
			break
	var async_pf_per_await := 0.0
	var async_proc_per_await := 0.0
	if first_reach_sync > 0 and pf2_at_reach > 0:
		async_pf_per_await = float(pf2_at_reach - pf2_start) / float(first_reach_sync)
		async_proc_per_await = float(Engine.get_process_frames() - proc2_start) / float(first_reach_sync)
	var async_chg_same := false
	var async_chg_t := -1
	var async_old_gone_t := -1
	if first_reach_sync > 0:
		NavigationServer2D.region_set_transform(reg2, Transform2D(0.0, Vector2(500, 0)))
		NavigationServer2D.map_force_update(map2)
		async_chg_same = _reach(map2, Vector2(510, 10), Vector2(590, 90))
		async_chg_t = await _poll_frames(30, func() -> bool: return _reach(map2, Vector2(510, 10), Vector2(590, 90)))
		async_old_gone_t = await _poll_frames(30, func() -> bool: return not _reach(map2, Vector2(10, 10), Vector2(90, 90)))
	NavigationServer2D.free_rid(reg2)
	NavigationServer2D.free_rid(map2)
	# async=false lane B: disable timing on a freshly synced map (unconfounded by lane A)
	var map3 := _new_map()
	NavigationServer2D.map_set_use_async_iterations(map3, false)
	var reg3 := _server_region(map3, _quad_poly(0, 0, 100, 100))
	var sync3 := -1
	for i in range(40):
		await physics_frame
		if _reach(map3, Vector2(10, 10), Vector2(90, 90)):
			sync3 = i + 1
			break
	var async_dis_same := false
	var async_dis_t := -1
	if sync3 > 0:
		NavigationServer2D.region_set_enabled(reg3, false)
		NavigationServer2D.map_force_update(map3)
		async_dis_same = _reach(map3, Vector2(10, 10), Vector2(90, 90))
		async_dis_t = await _poll_frames(30, func() -> bool: return not _reach(map3, Vector2(10, 10), Vector2(90, 90)))
	NavigationServer2D.free_rid(reg3)
	NavigationServer2D.free_rid(map3)
	print("PASS r91b_nav gate ",
		"pre_iter=", pre_iter, " pre_regions=", pre_regions, " pre_path=", pre_path,
		" pre_closest=", pre_closest,
		" first_iter1=", first_iter1, " first_iter2=", first_iter2,
		" first_reach=", first_reach, " gate_first=", gate_first,
		" reach_before_iter2=", reach_before_iter2,
		" frames_iter2_to_reach=", frames_iter2_to_reach,
		" pf_per_await=%.3f" % pf_per_await, " proc_per_await=%.3f" % proc_per_await,
		" cfg_at_iter1=", cfg_at_iter1, " cfg_at_iter2=", cfg_at_iter2,
		" trace=", _ps(trace),
		" async_first_reach=", first_reach_sync,
		" async_pf_per_await=%.3f" % async_pf_per_await,
		" async_proc_per_await=%.3f" % async_proc_per_await,
		" async_trace=", _ps(trace2),
		" async_chg_same=", async_chg_same, " async_chg_t=", async_chg_t,
		" async_old_gone_t=", async_old_gone_t,
		" async_sync3=", sync3, " async_dis_same=", async_dis_same, " async_dis_t=", async_dis_t)
	NavigationServer2D.free_rid(reg)
	NavigationServer2D.free_rid(map)

# ---------------------------------------------------------------- change application
func _arm_change() -> void:
	# lane 1: single region transform + disable (scout sync-arm geometry)
	var map := _new_map()
	var reg := _server_region(map, _quad_poly(0, 0, 100, 100))
	var settle1 := await _await_sync(map, Vector2(10, 10), Vector2(90, 90))
	NavigationServer2D.region_set_transform(reg, Transform2D(0.0, Vector2(500, 0)))
	NavigationServer2D.map_force_update(map)
	var tr_same_new := _reach(map, Vector2(510, 10), Vector2(590, 90))
	var tr_same_old := _reach(map, Vector2(10, 10), Vector2(90, 90))
	var tr_t := await _poll_frames(POLL, func() -> bool: return _reach(map, Vector2(510, 10), Vector2(590, 90)))
	NavigationServer2D.region_set_enabled(reg, false)
	NavigationServer2D.map_force_update(map)
	var dis_same_reach := _reach(map, Vector2(510, 10), Vector2(590, 90))
	var dis_t := await _poll_frames(POLL, func() -> bool: return not _reach(map, Vector2(510, 10), Vector2(590, 90)))
	NavigationServer2D.free_rid(reg)
	NavigationServer2D.free_rid(map)
	# lane 2: two-corridor route steering (cost / layers / polygon)
	var map2 := _new_map()
	var c := _server_region(map2, _quad_poly(0, 0, 20, 100))
	var a := _server_region(map2, _quad_poly(20, 60, 80, 80))
	var b := _server_region(map2, _quad_poly(20, 20, 80, 40))
	var d := _server_region(map2, _quad_poly(80, 0, 100, 100))
	var settle2 := await _await_sync(map2, Vector2(10, 50), Vector2(90, 50))
	var base_top := _routes_top(map2)
	NavigationServer2D.region_set_travel_cost(a, 10.0)
	NavigationServer2D.region_set_travel_cost(b, 1.0)
	var cost_same := _routes_bottom(map2)
	var cost_t := await _poll_frames(POLL, func() -> bool: return _routes_bottom(map2))
	NavigationServer2D.region_set_travel_cost(a, 1.0)
	NavigationServer2D.region_set_travel_cost(b, 1.0)
	await _await_frames(6)
	NavigationServer2D.region_set_navigation_layers(a, 2)
	var lay_same_top := _routes_top(map2)
	var lay_t := await _poll_frames(POLL, func() -> bool: return _routes_bottom(map2))
	NavigationServer2D.region_set_navigation_layers(a, 1)
	await _await_frames(6)
	NavigationServer2D.region_set_navigation_polygon(a, _quad_poly(20, 90, 30, 92))
	var poly_same_top := _routes_top(map2)
	var poly_t := await _poll_frames(POLL, func() -> bool: return _routes_bottom(map2))
	for r in [c, a, b, d]:
		NavigationServer2D.free_rid(r)
	NavigationServer2D.free_rid(map2)
	# lane 3: link disable
	var map3 := _new_map()
	var r1 := _server_region(map3, _quad_poly(0, 0, 100, 100))
	var r2 := _server_region(map3, _quad_poly(400, 0, 500, 100))
	var link := NavigationServer2D.link_create()
	NavigationServer2D.link_set_map(link, map3)
	NavigationServer2D.link_set_start_position(link, Vector2(100, 50))
	NavigationServer2D.link_set_end_position(link, Vector2(400, 50))
	var settle3 := await _await_sync(map3, Vector2(10, 50), Vector2(490, 50))
	NavigationServer2D.link_set_enabled(link, false)
	var link_same := _reach(map3, Vector2(10, 50), Vector2(490, 50))
	var link_t := await _poll_frames(POLL, func() -> bool: return not _reach(map3, Vector2(10, 50), Vector2(490, 50)))
	NavigationServer2D.free_rid(link)
	NavigationServer2D.free_rid(r1)
	NavigationServer2D.free_rid(r2)
	NavigationServer2D.free_rid(map3)
	# lane 4: edge-connection margin bridging (scout path-arm geometry)
	var map4 := _new_map()
	var rv := _server_region(map4, _quad_poly(0, 0, 40, 200))
	var rh := _server_region(map4, _quad_poly(40, 0, 200, 40))
	var rg := _server_region(map4, _quad_poly(210, 0, 310, 100))
	var settle4 := await _await_sync(map4, Vector2(20, 180), Vector2(180, 20))
	NavigationServer2D.map_set_edge_connection_margin(map4, 20.0)
	NavigationServer2D.map_force_update(map4)
	var gap_same := _reach(map4, Vector2(20, 20), Vector2(250, 20))
	var gap_t := await _poll_frames(POLL, func() -> bool: return _reach(map4, Vector2(20, 20), Vector2(250, 20)))
	for r in [rv, rh, rg]:
		NavigationServer2D.free_rid(r)
	NavigationServer2D.free_rid(map4)
	print("PASS r91b_nav change ",
		"tr_same_new=", tr_same_new, " tr_same_old=", tr_same_old, " tr_t=", tr_t,
		" dis_same_reach=", dis_same_reach, " dis_t=", dis_t,
		" base_top=", base_top, " cost_same=", cost_same, " cost_t=", cost_t,
		" lay_same_top=", lay_same_top, " lay_t=", lay_t,
		" poly_same_top=", poly_same_top, " poly_t=", poly_t,
		" link_same=", link_same, " link_t=", link_t,
		" gap_same=", gap_same, " gap_t=", gap_t,
		" settle1=", settle1, " settle2=", settle2, " settle3=", settle3, " settle4=", settle4)

# ---------------------------------------------------------------- agent fin/reached split
func _agent_lane(parent: Node2D, path_d: float, tgt_d: float) -> Dictionary:
	var holder := Node2D.new()
	holder.position = Vector2(20, 20)
	parent.add_child(holder)
	var ag := NavigationAgent2D.new()
	ag.path_desired_distance = path_d
	ag.target_desired_distance = tgt_d
	holder.add_child(ag)
	ag.target_position = Vector2(180, 180)
	var first_reachable := -1
	for i in range(60):
		await physics_frame
		if ag.is_target_reachable():
			first_reachable = i + 1
			break
	await _await_frames(2)
	var s_dist := ag.distance_to_target()
	var s_plen := ag.get_path_length()
	var steps := 0
	var fin_at := -1
	var reached_at := -1
	var fin_same_frame := false
	while steps < 80 and not ag.is_navigation_finished():
		var next := ag.get_next_path_position()
		holder.position = holder.position.move_toward(next, 8.0)
		steps += 1
		await physics_frame
		var fin_now := ag.is_navigation_finished()
		var rch_now := ag.is_target_reached()
		if fin_now and fin_at < 0:
			fin_at = steps
			fin_same_frame = rch_now
		if rch_now and reached_at < 0:
			reached_at = steps
	for i in range(4):
		await physics_frame
		if fin_at < 0 and ag.is_navigation_finished():
			fin_at = steps + i + 1
		if reached_at < 0 and ag.is_target_reached():
			reached_at = steps + i + 1
	var out := {
		"first_reachable": first_reachable,
		"walk_steps": steps,
		"fin_at": fin_at,
		"reached_at": reached_at,
		"split": (reached_at - fin_at) if (fin_at > 0 and reached_at > 0) else -1,
		"fin_same_frame": fin_same_frame,
		"dist": s_dist,
		"plen": s_plen,
		"final_dist": ag.distance_to_target(),
		"final_pos": _v(holder.position),
		"path": _path(ag.get_current_navigation_path()),
	}
	holder.queue_free()
	await physics_frame
	return out

func _arm_agent() -> void:
	var root := Node2D.new()
	get_root().add_child(root)
	var reg := NavigationRegion2D.new()
	reg.navigation_polygon = _quad_poly(0, 0, 200, 200)
	root.add_child(reg)
	var la := await _agent_lane(root, 4.0, 8.0)
	var lb := await _agent_lane(root, 4.0, 20.0)
	print("PASS r91b_nav agent ",
		"first_reachable=", la["first_reachable"],
		" walk_steps=", la["walk_steps"],
		" fin_at=", la["fin_at"], " reached_at=", la["reached_at"], " split=", la["split"],
		" fin_same_frame=", la["fin_same_frame"],
		" dist=%.4f" % la["dist"], " plen=%.4f" % la["plen"],
		" final_dist=%.4f" % la["final_dist"], " final_pos=", la["final_pos"], " path=", la["path"],
		" b_first_reachable=", lb["first_reachable"],
		" b_walk_steps=", lb["walk_steps"],
		" b_fin_at=", lb["fin_at"], " b_reached_at=", lb["reached_at"], " b_split=", lb["split"],
		" b_fin_same_frame=", lb["fin_same_frame"],
		" b_dist=%.4f" % lb["dist"], " b_final_dist=%.4f" % lb["final_dist"])
	root.queue_free()
	await physics_frame

# ---------------------------------------------------------------- avoidance
func _arm_avoid() -> void:
	var map := _new_map()
	var reg := _server_region(map, _quad_poly(0, 0, 400, 300))
	var settle := await _await_sync(map, Vector2(150, 150), Vector2(190, 150))
	var a := NavigationServer2D.agent_create()
	var b := NavigationServer2D.agent_create()
	var obs := NavigationServer2D.obstacle_create()
	var hits_a: Array[String] = []
	var hits_b: Array[String] = []
	NavigationServer2D.agent_set_avoidance_callback(a, func(v: Vector2) -> void:
		hits_a.append("%.3f,%.3f" % [v.x, v.y]))
	NavigationServer2D.agent_set_avoidance_callback(b, func(v: Vector2) -> void:
		hits_b.append("%.3f,%.3f" % [v.x, v.y]))
	for ag in [a, b]:
		NavigationServer2D.agent_set_map(ag, map)
		NavigationServer2D.agent_set_avoidance_enabled(ag, true)
		NavigationServer2D.agent_set_radius(ag, 10.0)
		NavigationServer2D.agent_set_max_speed(ag, 50.0)
		NavigationServer2D.agent_set_neighbor_distance(ag, 200.0)
		NavigationServer2D.agent_set_max_neighbors(ag, 8)
		NavigationServer2D.agent_set_time_horizon_agents(ag, 1.0)
		NavigationServer2D.agent_set_time_horizon_obstacles(ag, 1.0)
	NavigationServer2D.obstacle_set_map(obs, map)
	NavigationServer2D.obstacle_set_avoidance_enabled(obs, false)
	NavigationServer2D.obstacle_set_position(obs, Vector2(170, 150))
	NavigationServer2D.obstacle_set_radius(obs, 12.0)
	var pa := Vector2(150, 150)
	var pb := Vector2(190, 150)
	for i in range(16):
		NavigationServer2D.agent_set_position(a, pa)
		NavigationServer2D.agent_set_position(b, pb)
		NavigationServer2D.agent_set_velocity(a, Vector2(50, 0))
		NavigationServer2D.agent_set_velocity(b, Vector2(-50, 0))
		await physics_frame
	var hits_before := hits_a.size()
	var seq_a: Array[String] = []
	var seq_b: Array[String] = []
	var sums: Array[String] = []
	var per_a: Array[int] = []
	var per_b: Array[int] = []
	var last_a := hits_a.size()
	var last_b := hits_b.size()
	for i in range(5):
		NavigationServer2D.agent_set_position(a, pa)
		NavigationServer2D.agent_set_position(b, pb)
		NavigationServer2D.agent_set_velocity(a, Vector2(50, 0))
		NavigationServer2D.agent_set_velocity(b, Vector2(-50, 0))
		await physics_frame
		per_a.append(hits_a.size() - last_a)
		per_b.append(hits_b.size() - last_b)
		if hits_a.size() > last_a and hits_b.size() > last_b:
			var sa: PackedStringArray = hits_a[hits_a.size() - 1].split(",")
			var sb: PackedStringArray = hits_b[hits_b.size() - 1].split(",")
			sums.append("%.4f" % (absf(sa[0].to_float()) + absf(sb[0].to_float())))
		last_a = hits_a.size()
		last_b = hits_b.size()
		if hits_a.size() > seq_a.size():
			seq_a.append(hits_a[hits_a.size() - 1])
		if hits_b.size() > seq_b.size():
			seq_b.append(hits_b[hits_b.size() - 1])
	var va := NavigationServer2D.agent_get_velocity(a)
	var vb := NavigationServer2D.agent_get_velocity(b)
	var inv := absf(va.x) + absf(vb.x)
	print("PASS r91b_nav avoid ",
		"pa=", _v(pa), " pb=", _v(pb),
		" warm_n_a=", hits_before,
		" seq_a=", _ps(seq_a), " seq_b=", _ps(seq_b),
		" sums=", _ps(sums),
		" per_a=", str(per_a), " per_b=", str(per_b),
		" n_a=", hits_a.size(), " n_b=", hits_b.size(),
		" vel_a=", _v(va), " vel_b=", _v(vb),
		" sum=%.4f" % inv,
		" has_cb_a=", NavigationServer2D.agent_has_avoidance_callback(a),
		" radius_a=%.1f" % NavigationServer2D.agent_get_radius(a),
		" maxspeed_a=%.1f" % NavigationServer2D.agent_get_max_speed(a),
		" obs_pos=", _v(NavigationServer2D.obstacle_get_position(obs)),
		" obs_en=", NavigationServer2D.obstacle_get_avoidance_enabled(obs),
		" settle=", settle)
	NavigationServer2D.agent_set_avoidance_callback(a, Callable())
	NavigationServer2D.agent_set_avoidance_callback(b, Callable())
	await _await_frames(2)
	NavigationServer2D.free_rid(a)
	NavigationServer2D.free_rid(b)
	NavigationServer2D.free_rid(obs)
	NavigationServer2D.free_rid(reg)
	NavigationServer2D.free_rid(map)

# ---------------------------------------------------------------- bake
func _arm_bake() -> void:
	var poly_a := NavigationPolygon.new()
	poly_a.add_outline(PackedVector2Array([Vector2(0, 0), Vector2(200, 0), Vector2(200, 200), Vector2(0, 200)]))
	poly_a.add_outline(PackedVector2Array([Vector2(60, 60), Vector2(60, 140), Vector2(140, 140), Vector2(140, 60)]))
	poly_a.make_polygons_from_outlines()
	var map_a := _new_map()
	var reg_a := _server_region(map_a, poly_a)
	var root := Node2D.new()
	get_root().add_child(root)
	var reg_node := NavigationRegion2D.new()
	root.add_child(reg_node)
	var sb := StaticBody2D.new()
	var cs := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(100, 100)
	cs.shape = rect
	sb.add_child(cs)
	reg_node.add_child(sb)
	var poly_b := NavigationPolygon.new()
	poly_b.baking_rect = Rect2(-150, -150, 300, 300)
	poly_b.agent_radius = 5.0
	reg_node.navigation_polygon = poly_b
	var orphan := NavigationRegion2D.new()
	orphan.navigation_polygon = NavigationPolygon.new()
	orphan.bake_navigation_polygon(false)
	await _await_frames(2)
	var sgd := NavigationMeshSourceGeometryData2D.new()
	NavigationServer2D.parse_source_geometry_data(poly_b, sgd, reg_node, Callable())
	var obs_n := sgd.get_obstruction_outlines().size()
	var trav_n := sgd.get_traversable_outlines().size()
	var has_before := sgd.has_data()
	sgd.add_traversable_outline(PackedVector2Array([Vector2(-150, -150), Vector2(150, -150),
		Vector2(150, 150), Vector2(-150, 150)]))
	NavigationServer2D.bake_from_source_geometry_data(poly_b, sgd, Callable())
	var polys_b := poly_b.get_polygon_count()
	var verts_b := poly_b.vertices.size()
	var poly_c := NavigationPolygon.new()
	poly_c.baking_rect = Rect2(-150, -150, 300, 300)
	var sgd_c := NavigationMeshSourceGeometryData2D.new()
	NavigationServer2D.parse_source_geometry_data(poly_c, sgd_c, reg_node, Callable())
	NavigationServer2D.bake_from_source_geometry_data(poly_c, sgd_c, Callable())
	var polys_c := poly_c.get_polygon_count()
	var map_b := _new_map()
	var reg_b := _server_region(map_b, poly_b)
	var settle_a := await _await_sync(map_a, Vector2(100, 20), Vector2(100, 180))
	var settle_b := await _await_sync(map_b, Vector2(-100, 0), Vector2(100, 0))
	print("PASS r91b_nav bake ",
		"outline_polys=", poly_a.get_polygon_count(),
		" outline_verts=", poly_a.vertices.size(),
		" hole_across=", _path(NavigationServer2D.map_get_path(map_a, Vector2(100, 20), Vector2(100, 180), true)),
		" hole_straight=", _path(NavigationServer2D.map_get_path(map_a, Vector2(20, 100), Vector2(180, 100), true)),
		" parse_obs=", obs_n, " parse_trav=", trav_n, " parse_has=", has_before,
		" baked_polys=", polys_b, " baked_verts=", verts_b,
		" collider_only_polys=", polys_c,
		" iter_b=", NavigationServer2D.map_get_iteration_id(map_b),
		" through=", _path(NavigationServer2D.map_get_path(map_b, Vector2(-100, 0), Vector2(100, 0), true)),
		" around=", _path(NavigationServer2D.map_get_path(map_b, Vector2(-100, -100), Vector2(100, 100), true)),
		" outside=", _path(NavigationServer2D.map_get_path(map_b, Vector2(-200, -200), Vector2(100, 100), true)),
		" settle_a=", settle_a, " settle_b=", settle_b)
	NavigationServer2D.free_rid(reg_a)
	NavigationServer2D.free_rid(map_a)
	NavigationServer2D.free_rid(reg_b)
	NavigationServer2D.free_rid(map_b)
	orphan.free()
	root.queue_free()
	await physics_frame

# ---------------------------------------------------------------- teardown discipline
func _arm_crash_noclear() -> void:
	var map := _new_map()
	var a := NavigationServer2D.agent_create()
	var hits: Array[Vector2] = []
	NavigationServer2D.agent_set_map(a, map)
	NavigationServer2D.agent_set_avoidance_enabled(a, true)
	NavigationServer2D.agent_set_avoidance_callback(a, func(v: Vector2) -> void:
		hits.append(v))
	await _await_frames(3)
	print("PASS r91b_nav crash_noclear pre_free=1 has_cb=", NavigationServer2D.agent_has_avoidance_callback(a))
	NavigationServer2D.free_rid(a)
	NavigationServer2D.free_rid(map)
	print("SURVIVED r91b_nav crash_noclear")

func _arm_crash_clear0() -> void:
	var map := _new_map()
	var a := NavigationServer2D.agent_create()
	var hits: Array[Vector2] = []
	NavigationServer2D.agent_set_map(a, map)
	NavigationServer2D.agent_set_avoidance_enabled(a, true)
	NavigationServer2D.agent_set_avoidance_callback(a, func(v: Vector2) -> void:
		hits.append(v))
	await _await_frames(3)
	NavigationServer2D.agent_set_avoidance_callback(a, Callable())
	print("PASS r91b_nav crash_clear0 pre_free=1 has_cb=", NavigationServer2D.agent_has_avoidance_callback(a))
	NavigationServer2D.free_rid(a)
	NavigationServer2D.free_rid(map)
	print("SURVIVED r91b_nav crash_clear0")

func _arm_clean_clear1() -> void:
	var map := _new_map()
	var a := NavigationServer2D.agent_create()
	var hits: Array[Vector2] = []
	NavigationServer2D.agent_set_map(a, map)
	NavigationServer2D.agent_set_avoidance_enabled(a, true)
	NavigationServer2D.agent_set_avoidance_callback(a, func(v: Vector2) -> void:
		hits.append(v))
	await _await_frames(3)
	NavigationServer2D.agent_set_avoidance_callback(a, Callable())
	await _await_frames(1)
	NavigationServer2D.free_rid(a)
	NavigationServer2D.free_rid(map)
	print("PASS r91b_nav clean_clear1 survived=1 has_cb=", NavigationServer2D.agent_has_avoidance_callback(a))

func _arm_clean_clear2() -> void:
	var map := _new_map()
	var a := NavigationServer2D.agent_create()
	var hits: Array[Vector2] = []
	NavigationServer2D.agent_set_map(a, map)
	NavigationServer2D.agent_set_avoidance_enabled(a, true)
	NavigationServer2D.agent_set_avoidance_callback(a, func(v: Vector2) -> void:
		hits.append(v))
	await _await_frames(3)
	NavigationServer2D.agent_set_avoidance_callback(a, Callable())
	await _await_frames(2)
	NavigationServer2D.free_rid(a)
	NavigationServer2D.free_rid(map)
	print("PASS r91b_nav clean_clear2 survived=1 has_cb=", NavigationServer2D.agent_has_avoidance_callback(a))

func _arm_leak_cb() -> void:
	var map := _new_map()
	var a := NavigationServer2D.agent_create()
	var hits: Array[Vector2] = []
	NavigationServer2D.agent_set_map(a, map)
	NavigationServer2D.agent_set_avoidance_enabled(a, true)
	NavigationServer2D.agent_set_avoidance_callback(a, func(v: Vector2) -> void:
		hits.append(v))
	await _await_frames(3)
	print("PASS r91b_nav leak_cb pre_exit=1 has_cb=", NavigationServer2D.agent_has_avoidance_callback(a))

func _arm_leak_clean() -> void:
	var map := _new_map()
	var a := NavigationServer2D.agent_create()
	var hits: Array[Vector2] = []
	NavigationServer2D.agent_set_map(a, map)
	NavigationServer2D.agent_set_avoidance_enabled(a, true)
	NavigationServer2D.agent_set_avoidance_callback(a, func(v: Vector2) -> void:
		hits.append(v))
	await _await_frames(3)
	NavigationServer2D.agent_set_avoidance_callback(a, Callable())
	await _await_frames(1)
	print("PASS r91b_nav leak_clean pre_exit=1 has_cb=", NavigationServer2D.agent_has_avoidance_callback(a))
