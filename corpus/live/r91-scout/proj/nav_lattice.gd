extends SceneTree
# r91-scout primary probe — Navigation2D authorability lattice.
# Battery launch shape: godot --headless --path <proj> --script res://nav_lattice.gd -- --arm=<arm>
# Every arm prints exactly one `PASS nav_lattice <arm> ...` line (the battery signature).
#
# Discipline learned in discovery (receipts under runs/disc-*):
#  - NavigationAgent2D extends Node (NOT Node2D): no `position` property.
#  - Server RIDs are usable immediately; *node* tree state is not live until a frame passes.
#  - A map is not queryable until its first synchronization (loud ERROR from
#    map_get_closest_point pre-sync; empty paths from map_get_path).
#  - Live region changes take 2-3 physics frames; map_force_update is NOT synchronous.
#    Initial sync: async iterations (default) ~5-8 frames, async=false ~2 frames.
#  - An avoidance callback must be cleared and >=1 physics frame awaited before free_rid,
#    else "double free or corruption" (rc=134).  Agents leaked at exit crash too.
#  - Hand-built polygon lists inside one NavigationPolygon do NOT connect across a shared
#    edge; two separate regions sharing that edge DO connect.
#  - NavigationPolygon bake requires the region node inside the tree AND a traversable
#    outline; collider-only source geometry bakes to an empty navmesh silently.
#  - map_get_random_point() is random per call (not pinnable).

const SETTLE := 10

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

func _pia(arr: PackedInt32Array) -> String:
	var parts: Array[String] = []
	for i in arr:
		parts.append(str(i))
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

# Poll until the map has finished its initial synchronization for this probe pair.
# The initial async sync is a MODE (observed 3..6 frames typical, >10 in the tail):
# a fixed frame-count wait is not safe; returns the frames actually waited.
func _await_sync(map: RID, from: Vector2, to: Vector2, max_frames: int = 24) -> int:
	var frames := 0
	while frames < max_frames:
		await physics_frame
		frames += 1
		if NavigationServer2D.map_get_iteration_id(map) >= 2 and _reach(map, from, to):
			break
	return frames

func _initialize() -> void:
	var arm := _arg("arm", "census")
	match arm:
		"census": _arm_census()
		"sync": await _arm_sync()
		"path": await _arm_path()
		"query": await _arm_query()
		"region": await _arm_region()
		"agent": await _arm_agent()
		"avoid": await _arm_avoid()
		"bake": await _arm_bake()
		"link": await _arm_link()
		_:
			print("PASS nav_lattice unknown arm=", arm)
	quit(0)

# ---------------------------------------------------------------- census (pure)
func _arm_census() -> void:
	var poly := NavigationPolygon.new()
	var reg := NavigationRegion2D.new()
	var ag := NavigationAgent2D.new()
	var qp := NavigationPathQueryParameters2D.new()
	print("PASS nav_lattice census ",
		"srv_methods=", NavigationServer2D.get_method_list().size(),
		" poly_methods=", NavigationPolygon.new().get_method_list().size(),
		" srv_info=", _ps([NavigationServer2D.INFO_ACTIVE_MAPS, NavigationServer2D.INFO_REGION_COUNT,
			NavigationServer2D.INFO_AGENT_COUNT, NavigationServer2D.INFO_LINK_COUNT,
			NavigationServer2D.INFO_OBSTACLE_COUNT, NavigationServer2D.INFO_POLYGON_COUNT,
			NavigationServer2D.INFO_EDGE_COUNT, NavigationServer2D.INFO_EDGE_CONNECTION_COUNT,
			NavigationServer2D.INFO_EDGE_MERGE_COUNT, NavigationServer2D.INFO_EDGE_FREE_COUNT]),
		" pgt=", _ps([NavigationPolygon.PARSED_GEOMETRY_MESH_INSTANCES,
			NavigationPolygon.PARSED_GEOMETRY_STATIC_COLLIDERS, NavigationPolygon.PARSED_GEOMETRY_BOTH,
			NavigationPolygon.PARSED_GEOMETRY_MAX]),
		" sgm=", _ps([NavigationPolygon.SOURCE_GEOMETRY_ROOT_NODE_CHILDREN,
			NavigationPolygon.SOURCE_GEOMETRY_GROUPS_WITH_CHILDREN,
			NavigationPolygon.SOURCE_GEOMETRY_GROUPS_EXPLICIT, NavigationPolygon.SOURCE_GEOMETRY_MAX]),
		" sp=", _ps([NavigationPolygon.SAMPLE_PARTITION_CONVEX_PARTITION,
			NavigationPolygon.SAMPLE_PARTITION_TRIANGULATE, NavigationPolygon.SAMPLE_PARTITION_MAX]),
		" pp=", _ps([NavigationPathQueryParameters2D.PATH_POSTPROCESSING_NONE,
			NavigationPathQueryParameters2D.PATH_POSTPROCESSING_CORRIDORFUNNEL,
			NavigationPathQueryParameters2D.PATH_POSTPROCESSING_EDGECENTERED]),
		" md=", _ps([NavigationPathQueryParameters2D.PATH_METADATA_INCLUDE_NONE,
			NavigationPathQueryParameters2D.PATH_METADATA_INCLUDE_RIDS,
			NavigationPathQueryParameters2D.PATH_METADATA_INCLUDE_TYPES,
			NavigationPathQueryParameters2D.PATH_METADATA_INCLUDE_OWNERS,
			NavigationPathQueryParameters2D.PATH_METADATA_INCLUDE_ALL]),
		" alg=", NavigationPathQueryParameters2D.PATHFINDING_ALGORITHM_ASTAR,
		" poly_defaults=", "agent_r=%.4f" % poly.agent_radius,
		",cell=%.4f" % poly.cell_size,
		",border=%.4f" % poly.border_size,
		",pgt=", poly.parsed_geometry_type,
		",sgm=", poly.source_geometry_mode,
		",sp=", poly.sample_partition_type,
		",cmask=", poly.get_parsed_collision_mask(),
		",brect=", poly.baking_rect,
		",boff=", poly.baking_rect_offset,
		",polys=", poly.get_polygon_count(),
		" reg_defaults=", "cost=%.4f" % reg.travel_cost,
		",enter=%.4f" % reg.enter_cost,
		",en=", reg.enabled,
		",edge=", reg.use_edge_connections,
		" agent_defaults=", "r=%.4f" % ag.radius,
		",path_d=%.4f" % ag.path_desired_distance,
		",tgt_d=%.4f" % ag.target_desired_distance,
		",maxspeed=%.4f" % ag.max_speed,
		",nd=%.4f" % ag.neighbor_distance,
		",mn=", ag.max_neighbors,
		",tha=%.4f" % ag.time_horizon_agents,
		",tho=%.4f" % ag.time_horizon_obstacles,
		",avoid=", ag.avoidance_enabled,
		",prio=%.4f" % ag.avoidance_priority,
		",layers=", ag.navigation_layers,
		",pp=", ag.path_postprocessing,
		",simpl=", ag.simplify_path,
		",eps=%.4f" % ag.simplify_epsilon,
		" qp_defaults=", "pp=", qp.path_postprocessing,
		",md=", qp.metadata_flags,
		",layers=", qp.navigation_layers,
		",maxlen=%.4f" % qp.path_return_max_length,
		",maxrad=%.4f" % qp.path_return_max_radius,
		",maxdist=%.4f" % qp.path_search_max_distance,
		",maxpolys=", qp.path_search_max_polygons,
		",simpl=", qp.simplify_path,
		",eps=%.4f" % qp.simplify_epsilon)
	ag.free()
	reg.free()

# ---------------------------------------------------------------- sync ladder
func _arm_sync() -> void:
	var map := _new_map()
	var reg := _server_region(map, _quad_poly(0, 0, 100, 100))
	var pre_iter := NavigationServer2D.map_get_iteration_id(map)
	var pre_regions := NavigationServer2D.map_get_regions(map).size()
	var pre_path := _path(NavigationServer2D.map_get_path(map, Vector2(10, 10), Vector2(90, 90), true))
	var pre_closest := _v(NavigationServer2D.map_get_closest_point(map, Vector2(50, 50)))
	var ladder: Array[String] = []
	var first_reach := -1
	for i in range(10):
		await physics_frame
		ladder.append("f%d:%d/%d/%s" % [i, NavigationServer2D.map_get_iteration_id(map),
			NavigationServer2D.region_get_iteration_id(reg),
			"1" if _reach(map, Vector2(10, 10), Vector2(90, 90)) else "0"])
		if first_reach < 0 and _reach(map, Vector2(10, 10), Vector2(90, 90)):
			first_reach = i
	var act_after := NavigationServer2D.map_is_active(map)
	var cellsize := NavigationServer2D.map_get_cell_size(map)
	var edgemargin := NavigationServer2D.map_get_edge_connection_margin(map)
	var linkradius := NavigationServer2D.map_get_link_connection_radius(map)
	var merge_scale := NavigationServer2D.map_get_merge_rasterizer_cell_scale(map)
	var useedge := NavigationServer2D.map_get_use_edge_connections(map)
	var useasync := NavigationServer2D.map_get_use_async_iterations(map)
	# live transform change: is it visible in the same frame? after force_update? after settle?
	NavigationServer2D.region_set_transform(reg, Transform2D(0.0, Vector2(500, 0)))
	NavigationServer2D.map_force_update(map)
	var chg_same := _reach(map, Vector2(510, 10), Vector2(590, 90))
	var chg_iter_same := NavigationServer2D.map_get_iteration_id(map)
	await _await_frames(4)
	var chg_settled := _reach(map, Vector2(510, 10), Vector2(590, 90))
	var chg_iter_settled := NavigationServer2D.map_get_iteration_id(map)
	# live disable: same-frame vs settled
	NavigationServer2D.region_set_enabled(reg, false)
	NavigationServer2D.map_force_update(map)
	var dis_same := _reach(map, Vector2(510, 10), Vector2(590, 90))
	await _await_frames(4)
	var dis_settled := _reach(map, Vector2(510, 10), Vector2(590, 90))
	NavigationServer2D.free_rid(reg)
	NavigationServer2D.free_rid(map)
	# async=false: initial sync should be short
	var map2 := _new_map()
	NavigationServer2D.map_set_use_async_iterations(map2, false)
	var reg2 := _server_region(map2, _quad_poly(0, 0, 100, 100))
	var first_reach_sync := -1
	for i in range(6):
		await physics_frame
		if first_reach_sync < 0 and _reach(map2, Vector2(10, 10), Vector2(90, 90)):
			first_reach_sync = i
	print("PASS nav_lattice sync ",
		"pre_iter=", pre_iter,
		" pre_regions=", pre_regions,
		" pre_path=", pre_path,
		" pre_closest=", pre_closest,
		" cellsize=%.4f" % cellsize,
		" edgemargin=%.4f" % edgemargin,
		" linkradius=%.4f" % linkradius,
		" merge_scale=%.4f" % merge_scale,
		" useedge=", useedge,
		" async=", useasync,
		" active_after=", act_after,
		" chg_same=", chg_same, " chg_iter_same=", chg_iter_same,
		" chg_settled=", chg_settled, " chg_iter_settled=", chg_iter_settled,
		" dis_same=", dis_same, " dis_settled=", dis_settled,
		" ladder=", _ps(ladder),
		" first_reach=", first_reach,
		" first_reach_sync=", first_reach_sync)
	NavigationServer2D.free_rid(reg2)
	NavigationServer2D.free_rid(map2)

# ---------------------------------------------------------------- path shapes (two-region L)
func _arm_path() -> void:
	var map := _new_map()
	# L: vertical bar x 0..40 y 0..200 + horizontal bar x 40..200 y 0..40, as two regions
	var rv := _server_region(map, _quad_poly(0, 0, 40, 200))
	var rh := _server_region(map, _quad_poly(40, 0, 200, 40))
	# separate region 10 px to the right of the L (gap y 0..40, x 200..210)
	var rg := _server_region(map, _quad_poly(210, 0, 310, 100))
	var settle := await _await_sync(map, Vector2(20, 180), Vector2(180, 20))
	print("PASS nav_lattice path ",
		"diag=", _path(NavigationServer2D.map_get_path(map, Vector2(20, 180), Vector2(180, 20), true)),
		" diag_raw=", _path(NavigationServer2D.map_get_path(map, Vector2(20, 180), Vector2(180, 20), false)),
		" same=", _path(NavigationServer2D.map_get_path(map, Vector2(20, 20), Vector2(20, 20), true)),
		" out_start=", _path(NavigationServer2D.map_get_path(map, Vector2(-50, -50), Vector2(90, 20), true)),
		" out_target=", _path(NavigationServer2D.map_get_path(map, Vector2(20, 20), Vector2(400, 400), true)),
		" gap=", _path(NavigationServer2D.map_get_path(map, Vector2(20, 20), Vector2(250, 20), true)),
		" closest_in=", _v(NavigationServer2D.map_get_closest_point(map, Vector2(20, 20))),
		" closest_out=", _v(NavigationServer2D.map_get_closest_point(map, Vector2(-80, -80))),
		" owner_in_is_rv=", str(NavigationServer2D.map_get_closest_point_owner(map, Vector2(20, 20))) == str(rv),
		" owner_out_is_rv=", str(NavigationServer2D.map_get_closest_point_owner(map, Vector2(-80, -80))) == str(rv),
		" settle=", settle,
		" iter=", NavigationServer2D.map_get_iteration_id(map))
	# edge-connection margin 20 should bridge the 10 px gap at y in [0,40]
	NavigationServer2D.map_set_edge_connection_margin(map, 20.0)
	NavigationServer2D.map_force_update(map)
	await _await_frames(4)
	print("gap_margin20=", _path(NavigationServer2D.map_get_path(map, Vector2(20, 20), Vector2(250, 20), true)),
		" reach=", _reach(map, Vector2(20, 20), Vector2(250, 20)),
		" margin=%.4f" % NavigationServer2D.map_get_edge_connection_margin(map))
	for r in [rv, rh, rg]:
		NavigationServer2D.free_rid(r)
	NavigationServer2D.free_rid(map)

# ---------------------------------------------------------------- query_path lattice
func _arm_query() -> void:
	var map := _new_map()
	var rv := _server_region(map, _quad_poly(0, 0, 40, 200))
	var rh := _server_region(map, _quad_poly(40, 0, 200, 40))
	var settle := await _await_sync(map, Vector2(20, 180), Vector2(180, 20))
	var out: Array[String] = []
	for pp in [NavigationPathQueryParameters2D.PATH_POSTPROCESSING_NONE,
			NavigationPathQueryParameters2D.PATH_POSTPROCESSING_CORRIDORFUNNEL,
			NavigationPathQueryParameters2D.PATH_POSTPROCESSING_EDGECENTERED]:
		out.append("pp%d=%s" % [pp, _qpath(map, Vector2(20, 180), Vector2(180, 20), pp,
			NavigationPathQueryParameters2D.PATH_METADATA_INCLUDE_NONE, 1, 0.0, 0.0, 0.0, 0, false, 0.0)])
	var md: Array[String] = []
	for flags in [NavigationPathQueryParameters2D.PATH_METADATA_INCLUDE_NONE,
			NavigationPathQueryParameters2D.PATH_METADATA_INCLUDE_RIDS,
			NavigationPathQueryParameters2D.PATH_METADATA_INCLUDE_TYPES,
			NavigationPathQueryParameters2D.PATH_METADATA_INCLUDE_OWNERS,
			NavigationPathQueryParameters2D.PATH_METADATA_INCLUDE_ALL]:
		var r := _qresult(map, Vector2(20, 180), Vector2(180, 20),
			NavigationPathQueryParameters2D.PATH_POSTPROCESSING_CORRIDORFUNNEL, flags)
		md.append("md%d:%s|%s|%s" % [flags, _pia(r.get_path_types()),
			"n%d" % r.get_path_rids().size(), "n%d" % r.get_path_owner_ids().size()])
	print("PASS nav_lattice query ",
		"postproc=", _ps(out),
		" metadata=", _ps(md),
		" maxlen=", _qpath(map, Vector2(20, 180), Vector2(180, 20),
			NavigationPathQueryParameters2D.PATH_POSTPROCESSING_NONE,
			NavigationPathQueryParameters2D.PATH_METADATA_INCLUDE_NONE, 1, 30.0, 0.0, 0.0, 0, false, 0.0),
		" maxrad=", _qpath(map, Vector2(20, 180), Vector2(180, 20),
			NavigationPathQueryParameters2D.PATH_POSTPROCESSING_NONE,
			NavigationPathQueryParameters2D.PATH_METADATA_INCLUDE_NONE, 1, 0.0, 60.0, 0.0, 0, false, 0.0),
		" maxdist=", _qpath(map, Vector2(20, 180), Vector2(180, 20),
			NavigationPathQueryParameters2D.PATH_POSTPROCESSING_NONE,
			NavigationPathQueryParameters2D.PATH_METADATA_INCLUDE_NONE, 1, 0.0, 0.0, 40.0, 0, false, 0.0),
		" maxpolys=", _qpath(map, Vector2(20, 180), Vector2(180, 20),
			NavigationPathQueryParameters2D.PATH_POSTPROCESSING_NONE,
			NavigationPathQueryParameters2D.PATH_METADATA_INCLUDE_NONE, 1, 0.0, 0.0, 0.0, 1, false, 0.0),
		" simplify=", _qpath(map, Vector2(20, 180), Vector2(180, 20),
			NavigationPathQueryParameters2D.PATH_POSTPROCESSING_NONE,
			NavigationPathQueryParameters2D.PATH_METADATA_INCLUDE_NONE, 1, 0.0, 0.0, 0.0, 0, true, 5.0),
		" layers0=", _qpath(map, Vector2(20, 180), Vector2(180, 20),
			NavigationPathQueryParameters2D.PATH_POSTPROCESSING_NONE,
			NavigationPathQueryParameters2D.PATH_METADATA_INCLUDE_NONE, 0, 0.0, 0.0, 0.0, 0, false, 0.0),
		" length=", "%.4f" % _qresult(map, Vector2(20, 180), Vector2(180, 20),
			NavigationPathQueryParameters2D.PATH_POSTPROCESSING_CORRIDORFUNNEL,
			NavigationPathQueryParameters2D.PATH_METADATA_INCLUDE_NONE).get_path_length(),
		" settle=", settle,
		" iter=", NavigationServer2D.map_get_iteration_id(map))
	NavigationServer2D.free_rid(rv)
	NavigationServer2D.free_rid(rh)
	NavigationServer2D.free_rid(map)

func _qpath(map: RID, from: Vector2, to: Vector2, pp: int, flags: int, layers: int,
		maxlen: float, maxrad: float, maxdist: float, maxpolys: int, simpl: bool, eps: float) -> String:
	var r := _qresult(map, from, to, pp, flags, layers, maxlen, maxrad, maxdist, maxpolys, simpl, eps)
	return _path(r.get_path())

func _qresult(map: RID, from: Vector2, to: Vector2, pp: int, flags: int, layers: int = 1,
		maxlen: float = 0.0, maxrad: float = 0.0, maxdist: float = 0.0, maxpolys: int = 0,
		simpl: bool = false, eps: float = 0.0) -> NavigationPathQueryResult2D:
	var qp := NavigationPathQueryParameters2D.new()
	qp.map = map
	qp.start_position = from
	qp.target_position = to
	qp.path_postprocessing = pp
	qp.metadata_flags = flags
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

# ---------------------------------------------------------------- region lattice
func _arm_region() -> void:
	var map := _new_map()
	# C junction -> A top corridor / B bottom corridor -> D junction
	var c := _server_region(map, _quad_poly(0, 0, 20, 100))
	var a := _server_region(map, _quad_poly(20, 60, 80, 80))
	var b := _server_region(map, _quad_poly(20, 20, 80, 40))
	var d := _server_region(map, _quad_poly(80, 0, 100, 100))
	var settle := await _await_sync(map, Vector2(10, 50), Vector2(90, 50))
	var base := _path(NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(90, 50), true))
	# travel cost steers the route (settle after each change)
	NavigationServer2D.region_set_travel_cost(a, 1.0)
	NavigationServer2D.region_set_travel_cost(b, 10.0)
	await _await_frames(4)
	var top := _path(NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(90, 50), true))
	NavigationServer2D.region_set_travel_cost(a, 10.0)
	NavigationServer2D.region_set_travel_cost(b, 1.0)
	await _await_frames(4)
	var bot := _path(NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(90, 50), true))
	# enter cost alone (A expensive to enter)
	NavigationServer2D.region_set_travel_cost(a, 1.0)
	NavigationServer2D.region_set_travel_cost(b, 1.0)
	NavigationServer2D.region_set_enter_cost(a, 500.0)
	await _await_frames(4)
	var enter := _path(NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(90, 50), true))
	NavigationServer2D.region_set_enter_cost(a, 0.0)
	# navigation layers filter (A=1, B=2)
	NavigationServer2D.region_set_navigation_layers(a, 1)
	NavigationServer2D.region_set_navigation_layers(b, 2)
	await _await_frames(4)
	var l1 := _path(NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(90, 50), true, 1))
	var l2 := _path(NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(90, 50), true, 2))
	var l3 := _path(NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(90, 50), true, 3))
	NavigationServer2D.region_set_navigation_layers(b, 1)
	await _await_frames(4)
	# disable the preferred route A: same-frame vs settled
	NavigationServer2D.region_set_enabled(a, false)
	var dis_same := _path(NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(90, 50), true))
	await _await_frames(4)
	var dis_settled := _path(NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(90, 50), true))
	NavigationServer2D.region_set_enabled(a, true)
	await _await_frames(4)
	var reenabled := _path(NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(90, 50), true))
	# live polygon swap: A's corridor moves out of reach (route must fall back to B)
	NavigationServer2D.region_set_navigation_polygon(a, _quad_poly(20, 90, 30, 92))
	await _await_frames(4)
	var swapped := _path(NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(90, 50), true))
	NavigationServer2D.region_set_navigation_polygon(a, _quad_poly(20, 60, 80, 80))
	await _await_frames(4)
	var restored := _path(NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(90, 50), true))
	print("PASS nav_lattice region ",
		"base=", base, " top_cost1=", top, " bot_cost1=", bot, " enter500=", enter,
		" l1=", l1, " l2=", l2, " l3=", l3,
		" dis_same=", dis_same, " dis_settled=", dis_settled, " reenabled=", reenabled,
		" swapped=", swapped, " restored=", restored,
		" counts=", "regs=", NavigationServer2D.map_get_regions(map).size(),
		",cost_a=%.1f" % NavigationServer2D.region_get_travel_cost(a),
		",cost_b=%.1f" % NavigationServer2D.region_get_travel_cost(b),
		",en_a=", NavigationServer2D.region_get_enabled(a),
		",en_b=", NavigationServer2D.region_get_enabled(b),
		" settle=", settle,
		" iter=", NavigationServer2D.map_get_iteration_id(map))
	for r in [c, a, b, d]:
		NavigationServer2D.free_rid(r)
	NavigationServer2D.free_rid(map)

# ---------------------------------------------------------------- agent node
func _arm_agent() -> void:
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
	var first_reachable := -1
	for i in range(24):
		await physics_frame
		if first_reachable < 0 and ag.is_target_reachable():
			first_reachable = i
			break
	await _await_frames(2)
	var s_next := _v(ag.get_next_path_position())
	var s_fin := ag.is_navigation_finished()
	var s_reachable := ag.is_target_reachable()
	var s_reached := ag.is_target_reached()
	var s_dist := ag.distance_to_target()
	var s_plen := ag.get_path_length()
	var s_idx := ag.get_current_navigation_path_index()
	# walk the holder along the path to the target
	var steps := 0
	var reached_at := -1
	while steps < 60 and not ag.is_navigation_finished():
		var next := ag.get_next_path_position()
		holder.position = holder.position.move_toward(next, 8.0)
		steps += 1
		await physics_frame
		if reached_at < 0 and ag.is_target_reached():
			reached_at = steps
	print("PASS nav_lattice agent ",
		"settled=", s_next, "/", s_fin, "/", s_reachable, "/", s_reached,
		"/%.2f/%.2f/%d" % [s_dist, s_plen, s_idx],
		" walk_steps=", steps,
		" reached_at=", reached_at,
		" fin=", ag.is_navigation_finished(),
		" reached=", ag.is_target_reached(),
		" reachable=", ag.is_target_reachable(),
		" dist=%.4f" % ag.distance_to_target(),
		" final_pos=", _v(holder.position),
		" final_target=", _v(ag.get_final_position()),
		" path=", _path(ag.get_current_navigation_path()),
		" desired=%.1f" % ag.path_desired_distance,
		" target_desired=%.1f" % ag.target_desired_distance,
		" first_reachable=", first_reachable)
	root.queue_free()
	await physics_frame

# ---------------------------------------------------------------- avoidance
func _arm_avoid() -> void:
	var map := _new_map()
	var reg := _server_region(map, _quad_poly(0, 0, 400, 300))
	# agents are created AFTER the map sync so the avoidance sim has no pre-sync history
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
	# steady-state warmup: fixed positions + fixed velocities until the RVO state settles
	for i in range(16):
		NavigationServer2D.agent_set_position(a, pa)
		NavigationServer2D.agent_set_position(b, pb)
		NavigationServer2D.agent_set_velocity(a, Vector2(50, 0))
		NavigationServer2D.agent_set_velocity(b, Vector2(-50, 0))
		await physics_frame
	var hits_before := hits_a.size()
	var seq_a: Array[String] = []
	var seq_b: Array[String] = []
	for i in range(5):
		NavigationServer2D.agent_set_position(a, pa)
		NavigationServer2D.agent_set_position(b, pb)
		NavigationServer2D.agent_set_velocity(a, Vector2(50, 0))
		NavigationServer2D.agent_set_velocity(b, Vector2(-50, 0))
		await physics_frame
		if hits_a.size() > seq_a.size():
			seq_a.append(hits_a[hits_a.size() - 1])
		if hits_b.size() > seq_b.size():
			seq_b.append(hits_b[hits_b.size() - 1])
	print("PASS nav_lattice avoid ",
		"pa=", _v(pa), " pb=", _v(pb),
		" warm_n_a=", hits_before,
		" seq_a=", _ps(seq_a), " seq_b=", _ps(seq_b),
		" n_a=", hits_a.size(), " n_b=", hits_b.size(),
		" vel_a=", _v(NavigationServer2D.agent_get_velocity(a)),
		" vel_b=", _v(NavigationServer2D.agent_get_velocity(b)),
		" has_cb_a=", NavigationServer2D.agent_has_avoidance_callback(a),
		" radius_a=%.1f" % NavigationServer2D.agent_get_radius(a),
		" maxspeed_a=%.1f" % NavigationServer2D.agent_get_max_speed(a),
		" obs_pos=", _v(NavigationServer2D.obstacle_get_position(obs)),
		" obs_en=", NavigationServer2D.obstacle_get_avoidance_enabled(obs),
		" settle=", settle)
	# crash discipline: clear callbacks, >=1 frame, then free
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
	# route A: outlines -> make_polygons_from_outlines -> server region -> path around the hole
	var poly_a := NavigationPolygon.new()
	poly_a.add_outline(PackedVector2Array([Vector2(0, 0), Vector2(200, 0), Vector2(200, 200), Vector2(0, 200)]))
	poly_a.add_outline(PackedVector2Array([Vector2(60, 60), Vector2(60, 140), Vector2(140, 140), Vector2(140, 60)]))
	poly_a.make_polygons_from_outlines()
	var map_a := _new_map()
	var reg_a := _server_region(map_a, poly_a)
	# route B: collider obstruction + explicit traversable outline, modern bake API
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
	# orphan bake refusal: node not inside the tree
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
	# collider-only control: no traversable outline -> silent empty bake
	var poly_c := NavigationPolygon.new()
	poly_c.baking_rect = Rect2(-150, -150, 300, 300)
	var sgd_c := NavigationMeshSourceGeometryData2D.new()
	NavigationServer2D.parse_source_geometry_data(poly_c, sgd_c, reg_node, Callable())
	NavigationServer2D.bake_from_source_geometry_data(poly_c, sgd_c, Callable())
	var polys_c := poly_c.get_polygon_count()
	# feed the route-B bake to a fresh server region
	var map_b := _new_map()
	var reg_b := _server_region(map_b, poly_b)
	var settle_a := await _await_sync(map_a, Vector2(100, 20), Vector2(100, 180))
	var settle_b := await _await_sync(map_b, Vector2(-100, 0), Vector2(100, 0))
	print("PASS nav_lattice bake ",
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

# ---------------------------------------------------------------- link
func _arm_link() -> void:
	var map := _new_map()
	var r1 := _server_region(map, _quad_poly(0, 0, 100, 100))
	var r2 := _server_region(map, _quad_poly(400, 0, 500, 100))
	var link := NavigationServer2D.link_create()
	NavigationServer2D.link_set_map(link, map)
	NavigationServer2D.link_set_start_position(link, Vector2(100, 50))
	NavigationServer2D.link_set_end_position(link, Vector2(400, 50))
	var settle := await _await_sync(map, Vector2(10, 50), Vector2(490, 50))
	var bidir_default := NavigationServer2D.link_is_bidirectional(link)
	var en_default := NavigationServer2D.link_get_enabled(link)
	var fwd_default := _path(NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(490, 50), true))
	var rev_default := _path(NavigationServer2D.map_get_path(map, Vector2(490, 50), Vector2(10, 50), true))
	NavigationServer2D.link_set_bidirectional(link, true)
	await _await_frames(4)
	var rev_bidir := _path(NavigationServer2D.map_get_path(map, Vector2(490, 50), Vector2(10, 50), true))
	NavigationServer2D.link_set_enabled(link, false)
	var fwd_disabled_same := _path(NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(490, 50), true))
	await _await_frames(4)
	var fwd_disabled_settled := _path(NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(490, 50), true))
	NavigationServer2D.link_set_enabled(link, true)
	NavigationServer2D.link_set_bidirectional(link, false)
	NavigationServer2D.link_set_travel_cost(link, 300.0)
	await _await_frames(4)
	var cost300 := _path(NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(490, 50), true))
	NavigationServer2D.link_set_travel_cost(link, 1.0)
	NavigationServer2D.link_set_navigation_layers(link, 2)
	await _await_frames(4)
	var layer1 := _path(NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(490, 50), true, 1))
	var layer2 := _path(NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(490, 50), true, 2))
	print("PASS nav_lattice link ",
		"bidir_default=", bidir_default, " en_default=", en_default,
		" fwd_default=", fwd_default,
		" rev_default=", rev_default,
		" rev_bidir=", rev_bidir,
		" fwd_disabled_same=", fwd_disabled_same,
		" fwd_disabled_settled=", fwd_disabled_settled,
		" cost300=", cost300,
		" layer1=", layer1, " layer2=", layer2,
		" start=", _v(NavigationServer2D.link_get_start_position(link)),
		" end=", _v(NavigationServer2D.link_get_end_position(link)),
		" bidir=", NavigationServer2D.link_is_bidirectional(link),
		" en=", NavigationServer2D.link_get_enabled(link),
		" cost=%.1f" % NavigationServer2D.link_get_travel_cost(link),
		" enter=%.1f" % NavigationServer2D.link_get_enter_cost(link),
		" layers=", NavigationServer2D.link_get_navigation_layers(link),
		" settle=", settle,
		" iter=", NavigationServer2D.map_get_iteration_id(map),
		" link_iter=", NavigationServer2D.link_get_iteration_id(link))
	NavigationServer2D.free_rid(link)
	NavigationServer2D.free_rid(r1)
	NavigationServer2D.free_rid(r2)
	NavigationServer2D.free_rid(map)
