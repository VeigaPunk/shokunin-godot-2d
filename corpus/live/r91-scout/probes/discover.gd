extends SceneTree
# r91-scout discovery micro-probe: candidate API census + minimal nav feasibility.
# Battery launch shape: godot --headless --path proj --script res://discover.gd -- --arm=<name>

func _arg(name: String, def: String = "") -> String:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--" + name + "="):
			return a.substr(name.length() + 3)
	return def

func _quad_poly(x0: float, y0: float, x1: float, y1: float) -> NavigationPolygon:
	var p := NavigationPolygon.new()
	p.vertices = PackedVector2Array([Vector2(x0, y0), Vector2(x1, y0), Vector2(x1, y1), Vector2(x0, y1)])
	p.add_polygon(PackedInt32Array([0, 1, 2, 3]))
	return p

func _ps(arr: Array) -> String:
	var parts: Array[String] = []
	for s in arr:
		parts.append(str(s))
	return "[" + ",".join(parts) + "]"

func _reach(map: RID, from: Vector2, to: Vector2) -> bool:
	var p := NavigationServer2D.map_get_path(map, from, to, true)
	return p.size() > 0 and p[p.size() - 1].distance_to(to) < 0.5

func _names(cls: String, kind: String) -> String:
	var out: Array[String] = []
	var list: Array = []
	if kind == "m":
		list = ClassDB.class_get_method_list(cls, true)
		for d in list:
			out.append(String(d["name"]))
	elif kind == "p":
		list = ClassDB.class_get_property_list(cls, true)
		for d in list:
			out.append(String(d["name"]))
	elif kind == "e":
		list = ClassDB.class_get_integer_constant_list(cls, true)
		for d in list:
			out.append(String(d))
	out.sort()
	return "[" + ",".join(out) + "]"

func _initialize() -> void:
	var arm := _arg("arm", "census")
	print("PASS discover arm=", arm)
	match arm:
		"census":
			for cls in ["NavigationServer2D", "NavigationPolygon", "NavigationRegion2D",
					"NavigationAgent2D", "NavigationPathQueryParameters2D",
					"NavigationPathQueryResult2D", "Tween", "AnimationPlayer", "TileMapLayer",
					"NavigationObstacle2D"]:
				if not ClassDB.class_exists(cls):
					print("CLS ", cls, " MISSING")
					continue
				print("M ", cls, "=", _names(cls, "m"))
			print("ENUM Tween=", _names("Tween", "e"))
			print("ENUM NavigationAgent2D=", _names("NavigationAgent2D", "e"))
			print("ENUM NavigationPathQueryParameters2D=", _names("NavigationPathQueryParameters2D", "e"))
		"tweenval":
			# static interpolate_value: pure math?
			var v: Variant = Tween.interpolate_value(0.0, 10.0, 0.25, 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN_OUT)
			print("interp_linear_025=", v)
			var w: Variant = Tween.interpolate_value(0.0, 10.0, 0.25, 1.0, Tween.TRANS_QUAD, Tween.EASE_IN_OUT)
			print("interp_quad_025=", w)
			var e: Variant = Tween.interpolate_value(0.0, 10.0, 0.5, 1.0, Tween.TRANS_EXPO, Tween.EASE_OUT)
			print("interp_expo_easeout_05=", e)
		"navmin":
			# minimal: one map + one region with a hand-built quad navpoly; path query + sync timing.
			var map := NavigationServer2D.map_create()
			NavigationServer2D.map_set_active(map, true)
			NavigationServer2D.map_set_cell_size(map, 1.0)
			NavigationServer2D.map_set_edge_connection_margin(map, 5.0)
			var poly := NavigationPolygon.new()
			var verts := PackedVector2Array([Vector2(0, 0), Vector2(100, 0), Vector2(100, 100), Vector2(0, 100)])
			poly.vertices = verts
			poly.add_polygon(PackedInt32Array([0, 1, 2, 3]))
			var region := NavigationServer2D.region_create()
			NavigationServer2D.region_set_map(region, map)
			NavigationServer2D.region_set_navigation_polygon(region, poly)
			print("pre_force iter=", NavigationServer2D.map_get_iteration_id(map),
				" path=", NavigationServer2D.map_get_path(map, Vector2(10, 10), Vector2(90, 90), true))
			NavigationServer2D.map_force_update(map)
			print("post_force iter=", NavigationServer2D.map_get_iteration_id(map),
				" path=", NavigationServer2D.map_get_path(map, Vector2(10, 10), Vector2(90, 90), true))
			print("outside=", NavigationServer2D.map_get_path(map, Vector2(-50, -50), Vector2(90, 90), true))
			print("unmapped=", NavigationServer2D.map_get_path(RID(), Vector2(10, 10), Vector2(90, 90), true))
		"navstep":
			# does the map sync on physics frames? and does force_update work in-frame?
			var map := NavigationServer2D.map_create()
			NavigationServer2D.map_set_active(map, true)
			NavigationServer2D.map_set_cell_size(map, 1.0)
			var poly := NavigationPolygon.new()
			poly.vertices = PackedVector2Array([Vector2(0, 0), Vector2(100, 0), Vector2(100, 100), Vector2(0, 100)])
			poly.add_polygon(PackedInt32Array([0, 1, 2, 3]))
			var region := NavigationServer2D.region_create()
			NavigationServer2D.region_set_map(region, map)
			NavigationServer2D.region_set_navigation_polygon(region, poly)
			print("t0 iter=", NavigationServer2D.map_get_iteration_id(map),
				" rid_iter=", NavigationServer2D.region_get_iteration_id(region),
				" path=", NavigationServer2D.map_get_path(map, Vector2(10, 10), Vector2(90, 90), true))
			await physics_frame
			print("t1 iter=", NavigationServer2D.map_get_iteration_id(map),
				" rid_iter=", NavigationServer2D.region_get_iteration_id(region),
				" path=", NavigationServer2D.map_get_path(map, Vector2(10, 10), Vector2(90, 90), true))
			await physics_frame
			print("t2 iter=", NavigationServer2D.map_get_iteration_id(map),
				" rid_iter=", NavigationServer2D.region_get_iteration_id(region),
				" path=", NavigationServer2D.map_get_path(map, Vector2(10, 10), Vector2(90, 90), true))
			# query_path with a full parameter/result pair
			var qp := NavigationPathQueryParameters2D.new()
			qp.map = map
			qp.start_position = Vector2(10, 10)
			qp.target_position = Vector2(90, 90)
			qp.path_postprocessing = NavigationPathQueryParameters2D.PATH_POSTPROCESSING_NONE
			var qr := NavigationPathQueryResult2D.new()
			NavigationServer2D.query_path(qp, qr)
			print("qpath=", qr.path, " types=", qr.path_types, " rids=", qr.path_rids, " len=", qr.path_length)
			# force update after a live transform move
			NavigationServer2D.region_set_transform(region, Transform2D(0.0, Vector2(200, 0)))
			NavigationServer2D.map_force_update(map)
			print("after_move iter=", NavigationServer2D.map_get_iteration_id(map),
				" path=", NavigationServer2D.map_get_path(map, Vector2(210, 10), Vector2(290, 90), true))
			await physics_frame
			print("after_move_f iter=", NavigationServer2D.map_get_iteration_id(map),
				" path=", NavigationServer2D.map_get_path(map, Vector2(210, 10), Vector2(290, 90), true))
			NavigationServer2D.free_rid(region)
			NavigationServer2D.free_rid(map)
		"navbake":
			# headless bake feasibility: NavigationPolygon from outlines + region node bake
			var poly := NavigationPolygon.new()
			poly.add_outline(PackedVector2Array([Vector2(0, 0), Vector2(200, 0), Vector2(200, 200), Vector2(0, 200)]))
			poly.add_outline(PackedVector2Array([Vector2(60, 60), Vector2(60, 140), Vector2(140, 140), Vector2(140, 60)]))
			print("outlines=", poly.get_outline_count(), " polys_before=", poly.get_polygon_count())
			poly.make_polygons_from_outlines()
			print("polys_after=", poly.get_polygon_count(), " verts=", poly.vertices.size())
			var region := NavigationRegion2D.new()
			region.navigation_polygon = poly
			get_root().add_child(region)
			await physics_frame
			var m: RID = region.get_navigation_map()
			print("node_map=", m, " iter=", NavigationServer2D.map_get_iteration_id(m),
				" path=", NavigationServer2D.map_get_path(m, Vector2(10, 10), Vector2(190, 190), true))
			await physics_frame
			print("node_map2 iter=", NavigationServer2D.map_get_iteration_id(m),
				" path=", NavigationServer2D.map_get_path(m, Vector2(10, 10), Vector2(190, 190), true))
			region.queue_free()
		"navdbg":
			var map := NavigationServer2D.map_create()
			NavigationServer2D.map_set_active(map, true)
			var poly := NavigationPolygon.new()
			poly.vertices = PackedVector2Array([Vector2(0, 0), Vector2(100, 0), Vector2(100, 100), Vector2(0, 100)])
			poly.add_polygon(PackedInt32Array([0, 1, 2, 3]))
			var region := NavigationServer2D.region_create()
			NavigationServer2D.region_set_map(region, map)
			NavigationServer2D.region_set_navigation_polygon(region, poly)
			print("poly_count=", poly.get_polygon_count(), " verts=", poly.vertices.size())
			print("regions_before=", NavigationServer2D.map_get_regions(map))
			for i in range(6):
				await physics_frame
				print("f", i, " iter=", NavigationServer2D.map_get_iteration_id(map),
					" regions=", NavigationServer2D.map_get_regions(map),
					" bounds=", NavigationServer2D.region_get_bounds(region),
					" closest=", NavigationServer2D.map_get_closest_point(map, Vector2(50, 50)))
			print("path=", NavigationServer2D.map_get_path(map, Vector2(10, 10), Vector2(90, 90), true))
			print("path_raw=", NavigationServer2D.map_get_path(map, Vector2(10, 10), Vector2(90, 90), false))
			NavigationServer2D.free_rid(region)
			NavigationServer2D.free_rid(map)
		"navagentdbg":
			var reg := NavigationRegion2D.new()
			var poly := NavigationPolygon.new()
			poly.vertices = PackedVector2Array([Vector2(0, 0), Vector2(200, 0), Vector2(200, 200), Vector2(0, 200)])
			poly.add_polygon(PackedInt32Array([0, 1, 2, 3]))
			reg.navigation_polygon = poly
			get_root().add_child(reg)
			var ag := NavigationAgent2D.new()
			reg.add_child(ag)
			ag.target_position = Vector2(180, 180)
			print("ag_rid=", ag.get_rid(), " path_desired=", ag.path_desired_distance,
				" target_desired=", ag.target_desired_distance, " radius=", ag.radius,
				" maxspeed=", ag.max_speed, " postproc=", ag.path_postprocessing)
			for i in range(6):
				await physics_frame
				print("f", i, " next=", ag.get_next_path_position(),
					" fin=", ag.is_navigation_finished(),
					" dist=", ag.distance_to_target(),
					" reached=", ag.is_target_reached(),
					" reachable=", ag.is_target_reachable(),
					" pathlen=", ag.get_path_length(),
					" idx=", ag.get_current_navigation_path_index())
			reg.queue_free()
		"navbakedbg":
			var root := Node2D.new()
			get_root().add_child(root)
			var reg := NavigationRegion2D.new()
			root.add_child(reg)
			var sb := StaticBody2D.new()
			var cs := CollisionShape2D.new()
			var rect := RectangleShape2D.new()
			rect.size = Vector2(300, 200)
			cs.shape = rect
			sb.add_child(cs)
			reg.add_child(sb)
			var poly := NavigationPolygon.new()
			print("sgm=", poly.source_geometry_mode, " pgt=", poly.parsed_geometry_type,
				" cmask=", poly.get_parsed_collision_mask(), " agent_r=", poly.agent_radius,
				" cell=", poly.cell_size, " border=", poly.border_size,
				" sp=", poly.sample_partition_type)
			reg.navigation_polygon = poly
			reg.bake_navigation_polygon()
			print("baking0=", reg.is_baking())
			var n := 0
			while reg.is_baking() and n < 120:
				await physics_frame
				n += 1
			print("baking_done n=", n, " polys=", poly.get_polygon_count(), " verts=", poly.vertices.size(),
				" rect=", poly.get_baking_rect())
			await physics_frame
			await physics_frame
			await physics_frame
			var m: RID = reg.get_navigation_map()
			print("map_iter=", NavigationServer2D.map_get_iteration_id(m),
				" path=", NavigationServer2D.map_get_path(m, Vector2(10, 10), Vector2(280, 180), true))
			root.queue_free()
		"navlinkdbg":
			var map := NavigationServer2D.map_create()
			NavigationServer2D.map_set_active(map, true)
			var mk := func(x0: float) -> RID:
				var p := NavigationPolygon.new()
				p.vertices = PackedVector2Array([Vector2(x0, 0), Vector2(x0 + 100, 0), Vector2(x0 + 100, 100), Vector2(x0, 100)])
				p.add_polygon(PackedInt32Array([0, 1, 2, 3]))
				var r := NavigationServer2D.region_create()
				NavigationServer2D.region_set_map(r, map)
				NavigationServer2D.region_set_navigation_polygon(r, p)
				return r
			var r1: RID = mk.call(0.0)
			var r2: RID = mk.call(400.0)
			var link := NavigationServer2D.link_create()
			NavigationServer2D.link_set_map(link, map)
			NavigationServer2D.link_set_start_position(link, Vector2(100, 50))
			NavigationServer2D.link_set_end_position(link, Vector2(400, 50))
			for i in range(5):
				await physics_frame
			print("link_iter=", NavigationServer2D.link_get_iteration_id(link),
				" iter=", NavigationServer2D.map_get_iteration_id(map))
			print("path_nolink=", NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(490, 50), true))
			NavigationServer2D.link_set_bidirectional(link, true)
			NavigationServer2D.map_force_update(map)
			print("path_bidir=", NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(490, 50), true),
				" rev=", NavigationServer2D.map_get_path(map, Vector2(490, 50), Vector2(10, 50), true))
			NavigationServer2D.link_set_enabled(link, false)
			NavigationServer2D.map_force_update(map)
			print("path_disabled=", NavigationServer2D.map_get_path(map, Vector2(10, 50), Vector2(490, 50), true))
			for r in [r1, r2, link, map]:
				NavigationServer2D.free_rid(r)
		"navavoiddbg":
			var reg := NavigationRegion2D.new()
			var poly := NavigationPolygon.new()
			poly.vertices = PackedVector2Array([Vector2(0, 0), Vector2(300, 0), Vector2(300, 300), Vector2(0, 300)])
			poly.add_polygon(PackedInt32Array([0, 1, 2, 3]))
			reg.navigation_polygon = poly
			get_root().add_child(reg)
			var a := NavigationAgent2D.new()
			var b := NavigationAgent2D.new()
			for ag in [a, b]:
				reg.add_child(ag)
				ag.avoidance_enabled = true
				ag.radius = 10.0
				ag.max_speed = 50.0
			a.position = Vector2(50, 150)
			b.position = Vector2(250, 150)
			for i in range(5):
				await physics_frame
			print("rid_a=", a.get_rid(), " rid_b=", b.get_rid(), " ae=", a.avoidance_enabled)
			for i in range(10):
				a.velocity = Vector2(50, 0)
				b.velocity = Vector2(-50, 0)
				await physics_frame
				print("f", i, " a=", a.position, " b=", b.position, " av=", a.velocity, " bv=", b.velocity)
			reg.queue_free()
		"navavoid2":
			var reg := NavigationRegion2D.new()
			var poly := NavigationPolygon.new()
			poly.vertices = PackedVector2Array([Vector2(0, 0), Vector2(300, 0), Vector2(300, 300), Vector2(0, 300)])
			poly.add_polygon(PackedInt32Array([0, 1, 2, 3]))
			reg.navigation_polygon = poly
			get_root().add_child(reg)
			var a := NavigationAgent2D.new()
			reg.add_child(a)
			a.avoidance_enabled = true
			a.radius = 10.0
			a.position = Vector2(50, 150)
			for i in range(5):
				await physics_frame
			print("rid_a=", a.get_rid(), " ae=", a.avoidance_enabled)
			for i in range(10):
				a.set_velocity_forced(Vector2(50, 0))
				await physics_frame
				print("f", i, " a=", a.position, " av=", a.velocity)
			reg.queue_free()
		"navavoid3":
			# server-level avoidance: callback + velocity_forced, deterministic?
			var map := NavigationServer2D.map_create()
			NavigationServer2D.map_set_active(map, true)
			var a := NavigationServer2D.agent_create()
			var b := NavigationServer2D.agent_create()
			var hits: Array[String] = []
			var cb := func(safe_v: Vector2) -> void:
				hits.append("%.4f,%.4f" % [safe_v.x, safe_v.y])
			for ag in [a, b]:
				NavigationServer2D.agent_set_map(ag, map)
				NavigationServer2D.agent_set_avoidance_enabled(ag, true)
				NavigationServer2D.agent_set_radius(ag, 10.0)
				NavigationServer2D.agent_set_max_speed(ag, 50.0)
				NavigationServer2D.agent_set_avoidance_callback(ag, cb)
			NavigationServer2D.agent_set_position(a, Vector2(50, 150))
			NavigationServer2D.agent_set_position(b, Vector2(250, 150))
			for i in range(5):
				await physics_frame
			print("has_cb=", NavigationServer2D.agent_has_avoidance_callback(a),
				" a_pos=", NavigationServer2D.agent_get_position(a),
				" b_pos=", NavigationServer2D.agent_get_position(b))
			for i in range(20):
				NavigationServer2D.agent_set_velocity_forced(a, Vector2(50, 0))
				NavigationServer2D.agent_set_velocity_forced(b, Vector2(-50, 0))
				await physics_frame
			print("hits_n=", hits.size(), " hits=", hits)
			print("a_pos=", NavigationServer2D.agent_get_position(a),
				" b_pos=", NavigationServer2D.agent_get_position(b),
				" a_vel=", NavigationServer2D.agent_get_velocity(a),
				" b_vel=", NavigationServer2D.agent_get_velocity(b))
			for r in [a, b, map]:
				NavigationServer2D.free_rid(r)
		"navbake3":
			var root := Node2D.new()
			get_root().add_child(root)
			var reg := NavigationRegion2D.new()
			root.add_child(reg)
			var sb := StaticBody2D.new()
			var cs := CollisionShape2D.new()
			var rect := RectangleShape2D.new()
			rect.size = Vector2(300, 200)
			cs.shape = rect
			sb.add_child(cs)
			reg.add_child(sb)
			var poly := NavigationPolygon.new()
			reg.navigation_polygon = poly
			print("inside=", reg.is_inside_tree(), " parent_inside=", reg.get_parent().is_inside_tree())
			await physics_frame
			await physics_frame
			print("inside2=", reg.is_inside_tree())
			reg.bake_navigation_polygon()
			print("baking0=", reg.is_baking())
			var n := 0
			while reg.is_baking() and n < 60:
				await physics_frame
				n += 1
			print("baking_done n=", n, " polys=", poly.get_polygon_count(),
				" verts=", poly.vertices.size(), " rect=", poly.get_baking_rect(),
				" outl=", poly.get_outline_count())
			for i in range(4):
				await physics_frame
			var m: RID = reg.get_navigation_map()
			print("map_iter=", NavigationServer2D.map_get_iteration_id(m),
				" path=", NavigationServer2D.map_get_path(m, Vector2(10, 10), Vector2(280, 180), true))
			root.queue_free()
		"navclasses":
			for cls in ["NavigationLink2D", "NavigationObstacle2D", "NavigationMeshSourceGeometryData2D",
					"NavigationRegion2D", "NavigationPolygon"]:
				print("CLS ", cls, "=", ClassDB.class_exists(cls))
			for cls in ["NavigationPolygon", "NavigationRegion2D", "NavigationServer2D"]:
				print("E ", cls, "=", _names(cls, "e"))
		"navavoid4":
			# avoidance with a region present; callback payloads; teardown orders
			var map := NavigationServer2D.map_create()
			NavigationServer2D.map_set_active(map, true)
			var poly := NavigationPolygon.new()
			poly.vertices = PackedVector2Array([Vector2(0, 0), Vector2(400, 0), Vector2(400, 300), Vector2(0, 300)])
			poly.add_polygon(PackedInt32Array([0, 1, 2, 3]))
			var reg := NavigationServer2D.region_create()
			NavigationServer2D.region_set_map(reg, map)
			NavigationServer2D.region_set_navigation_polygon(reg, poly)
			var a := NavigationServer2D.agent_create()
			var b := NavigationServer2D.agent_create()
			var hits_a: Array[String] = []
			var hits_b: Array[String] = []
			NavigationServer2D.agent_set_avoidance_callback(a, func(v: Vector2) -> void: hits_a.append("%.3f,%.3f" % [v.x, v.y]))
			NavigationServer2D.agent_set_avoidance_callback(b, func(v: Vector2) -> void: hits_b.append("%.3f,%.3f" % [v.x, v.y]))
			for ag in [a, b]:
				NavigationServer2D.agent_set_map(ag, map)
				NavigationServer2D.agent_set_avoidance_enabled(ag, true)
				NavigationServer2D.agent_set_radius(ag, 10.0)
				NavigationServer2D.agent_set_max_speed(ag, 50.0)
			NavigationServer2D.agent_set_position(a, Vector2(50, 150))
			NavigationServer2D.agent_set_position(b, Vector2(250, 150))
			for i in range(4):
				await physics_frame
			print("iter=", NavigationServer2D.map_get_iteration_id(map))
			for i in range(12):
				NavigationServer2D.agent_set_velocity(a, Vector2(50, 0))
				NavigationServer2D.agent_set_velocity(b, Vector2(-50, 0))
				await physics_frame
			print("hits_a_n=", hits_a.size(), " tail_a=", hits_a.slice(maxi(hits_a.size() - 4, 0)))
			print("hits_b_n=", hits_b.size(), " tail_b=", hits_b.slice(maxi(hits_b.size() - 4, 0)))
			print("pos_a=", NavigationServer2D.agent_get_position(a), " pos_b=", NavigationServer2D.agent_get_position(b),
				" vel_a=", NavigationServer2D.agent_get_velocity(a), " vel_b=", NavigationServer2D.agent_get_velocity(b))
			# teardown order A: clear callbacks, free agents, region, map
			NavigationServer2D.agent_set_avoidance_callback(a, Callable())
			NavigationServer2D.agent_set_avoidance_callback(b, Callable())
			NavigationServer2D.free_rid(a)
			NavigationServer2D.free_rid(b)
			NavigationServer2D.free_rid(reg)
			NavigationServer2D.free_rid(map)
			print("teardown_clean=true")
		"navbake4":
			var root := Node2D.new()
			get_root().add_child(root)
			var reg := NavigationRegion2D.new()
			root.add_child(reg)
			var sb := StaticBody2D.new()
			var cs := CollisionShape2D.new()
			var rect := RectangleShape2D.new()
			rect.size = Vector2(300, 200)
			cs.shape = rect
			sb.add_child(cs)
			reg.add_child(sb)
			var poly := NavigationPolygon.new()
			reg.navigation_polygon = poly
			await physics_frame
			await physics_frame
			print("inside=", reg.is_inside_tree())
			var sgd := NavigationMeshSourceGeometryData2D.new()
			NavigationServer2D.parse_source_geometry_data(poly, sgd, reg, Callable())
			print("sgd_has=", sgd.has_data(), " trav=", sgd.get_traversable_outlines().size(),
				" obs=", sgd.get_obstruction_outlines().size(), " bounds=", sgd.get_bounds())
			NavigationServer2D.bake_from_source_geometry_data(poly, sgd, Callable())
			print("sync_bake polys=", poly.get_polygon_count(), " verts=", poly.vertices.size(),
				" rect=", poly.get_baking_rect())
			var reg2 := NavigationRegion2D.new()
			root.add_child(reg2)
			var sb2 := StaticBody2D.new()
			var cs2 := CollisionShape2D.new()
			var rect2 := RectangleShape2D.new()
			rect2.size = Vector2(100, 100)
			cs2.shape = rect2
			sb2.add_child(cs2)
			reg2.add_child(sb2)
			var poly2 := NavigationPolygon.new()
			reg2.navigation_polygon = poly2
			await physics_frame
			reg2.bake_navigation_polygon(false)
			print("nothread baking=", reg2.is_baking(), " polys=", poly2.get_polygon_count(),
				" verts=", poly2.vertices.size(), " rect=", poly2.get_baking_rect())
			await physics_frame
			await physics_frame
			await physics_frame
			print("iter2=", NavigationServer2D.map_get_iteration_id(reg2.get_navigation_map()),
				" path2=", NavigationServer2D.map_get_path(reg2.get_navigation_map(), Vector2(-40, -40), Vector2(40, 40), true))
			root.queue_free()
		"navfree1":
			# agent only, no callback, no region: free order agent->map
			var map := NavigationServer2D.map_create()
			NavigationServer2D.map_set_active(map, true)
			var a := NavigationServer2D.agent_create()
			NavigationServer2D.agent_set_map(a, map)
			NavigationServer2D.agent_set_avoidance_enabled(a, true)
			for i in range(3):
				await physics_frame
			NavigationServer2D.free_rid(a)
			NavigationServer2D.free_rid(map)
			print("navfree1 ok")
		"navfree2":
			# agent + callback, free callback then agent then map
			var map := NavigationServer2D.map_create()
			NavigationServer2D.map_set_active(map, true)
			var a := NavigationServer2D.agent_create()
			NavigationServer2D.agent_set_map(a, map)
			NavigationServer2D.agent_set_avoidance_enabled(a, true)
			NavigationServer2D.agent_set_avoidance_callback(a, func(v: Vector2) -> void: pass)
			for i in range(3):
				await physics_frame
			NavigationServer2D.agent_set_avoidance_callback(a, Callable())
			NavigationServer2D.free_rid(a)
			NavigationServer2D.free_rid(map)
			print("navfree2 ok")
		"navfree3":
			# map only (no agents): free map
			var map := NavigationServer2D.map_create()
			NavigationServer2D.map_set_active(map, true)
			for i in range(3):
				await physics_frame
			NavigationServer2D.free_rid(map)
			print("navfree3 ok")
		"navfree4":
			# region + map, no agents
			var map := NavigationServer2D.map_create()
			NavigationServer2D.map_set_active(map, true)
			var poly := NavigationPolygon.new()
			poly.vertices = PackedVector2Array([Vector2(0, 0), Vector2(100, 0), Vector2(100, 100), Vector2(0, 100)])
			poly.add_polygon(PackedInt32Array([0, 1, 2, 3]))
			var reg := NavigationServer2D.region_create()
			NavigationServer2D.region_set_map(reg, map)
			NavigationServer2D.region_set_navigation_polygon(reg, poly)
			for i in range(3):
				await physics_frame
			NavigationServer2D.free_rid(reg)
			NavigationServer2D.free_rid(map)
			print("navfree4 ok")
		"navfree5":
			# two agents with callbacks + region: free agents, region, map (navavoid4 order, minimal)
			var map := NavigationServer2D.map_create()
			NavigationServer2D.map_set_active(map, true)
			var a := NavigationServer2D.agent_create()
			var b := NavigationServer2D.agent_create()
			NavigationServer2D.agent_set_avoidance_callback(a, func(v: Vector2) -> void: pass)
			NavigationServer2D.agent_set_avoidance_callback(b, func(v: Vector2) -> void: pass)
			for ag in [a, b]:
				NavigationServer2D.agent_set_map(ag, map)
				NavigationServer2D.agent_set_avoidance_enabled(ag, true)
			NavigationServer2D.agent_set_position(a, Vector2(50, 150))
			NavigationServer2D.agent_set_position(b, Vector2(250, 150))
			for i in range(3):
				await physics_frame
			NavigationServer2D.agent_set_velocity(a, Vector2(50, 0))
			NavigationServer2D.agent_set_velocity(b, Vector2(-50, 0))
			await physics_frame
			NavigationServer2D.free_rid(a)
			NavigationServer2D.free_rid(b)
			NavigationServer2D.free_rid(map)
			print("navfree5 ok")
		"navfree6":
			# clear callback, await a frame, then free
			var map := NavigationServer2D.map_create()
			NavigationServer2D.map_set_active(map, true)
			var a := NavigationServer2D.agent_create()
			NavigationServer2D.agent_set_map(a, map)
			NavigationServer2D.agent_set_avoidance_enabled(a, true)
			NavigationServer2D.agent_set_avoidance_callback(a, func(v: Vector2) -> void: pass)
			for i in range(3):
				await physics_frame
			NavigationServer2D.agent_set_avoidance_callback(a, Callable())
			await physics_frame
			await physics_frame
			NavigationServer2D.free_rid(a)
			NavigationServer2D.free_rid(map)
			print("navfree6 ok")
		"navfree7":
			# node-based agent, server callback on the node's RID, queue_free teardown
			var reg := NavigationRegion2D.new()
			var poly := NavigationPolygon.new()
			poly.vertices = PackedVector2Array([Vector2(0, 0), Vector2(300, 0), Vector2(300, 300), Vector2(0, 300)])
			poly.add_polygon(PackedInt32Array([0, 1, 2, 3]))
			reg.navigation_polygon = poly
			get_root().add_child(reg)
			var holder := Node2D.new()
			holder.position = Vector2(50, 150)
			reg.add_child(holder)
			var ag := NavigationAgent2D.new()
			ag.avoidance_enabled = true
			ag.radius = 10.0
			holder.add_child(ag)
			var hits: Array[String] = []
			NavigationServer2D.agent_set_avoidance_callback(ag.get_rid(), func(v: Vector2) -> void: hits.append("%.3f,%.3f" % [v.x, v.y]))
			for i in range(5):
				await physics_frame
			for i in range(8):
				ag.velocity = Vector2(50, 0)
				await physics_frame
			print("node_agent hits=", hits.size(), " tail=", hits.slice(maxi(hits.size() - 3, 0)),
				" pos=", holder.position, " has_cb=", NavigationServer2D.agent_has_avoidance_callback(ag.get_rid()))
			reg.queue_free()
			await physics_frame
			print("navfree7 ok")
		"navavoid5":
			# close approach with manual position integration; do NOT free agents (callback crash)
			var map := NavigationServer2D.map_create()
			NavigationServer2D.map_set_active(map, true)
			var a := NavigationServer2D.agent_create()
			var b := NavigationServer2D.agent_create()
			var hits_a: Array[String] = []
			NavigationServer2D.agent_set_avoidance_callback(a, func(v: Vector2) -> void: hits_a.append("%.3f,%.3f" % [v.x, v.y]))
			NavigationServer2D.agent_set_avoidance_callback(b, func(v: Vector2) -> void: pass)
			for ag in [a, b]:
				NavigationServer2D.agent_set_map(ag, map)
				NavigationServer2D.agent_set_avoidance_enabled(ag, true)
				NavigationServer2D.agent_set_radius(ag, 10.0)
				NavigationServer2D.agent_set_max_speed(ag, 50.0)
				NavigationServer2D.agent_set_neighbor_distance(ag, 200.0)
				NavigationServer2D.agent_set_max_neighbors(ag, 8)
				NavigationServer2D.agent_set_time_horizon_agents(ag, 1.0)
			var pa := Vector2(150, 150)
			var pb := Vector2(190, 150)
			for i in range(4):
				await physics_frame
			for i in range(10):
				pa += Vector2(50, 0) * 0.016667
				pb += Vector2(-50, 0) * 0.016667
				NavigationServer2D.agent_set_position(a, pa)
				NavigationServer2D.agent_set_position(b, pb)
				NavigationServer2D.agent_set_velocity(a, Vector2(50, 0))
				NavigationServer2D.agent_set_velocity(b, Vector2(-50, 0))
				await physics_frame
			print("pa=", pa, " pb=", pb, " hits_n=", hits_a.size(), " tail=", hits_a.slice(maxi(hits_a.size() - 5, 0)))
			print("leak_on_exit_expected")
		"navbake5":
			# route B: parse collider obstructions + bake with an explicit baking_rect
			var root := Node2D.new()
			get_root().add_child(root)
			var reg := NavigationRegion2D.new()
			root.add_child(reg)
			var sb := StaticBody2D.new()
			var cs := CollisionShape2D.new()
			var rect := RectangleShape2D.new()
			rect.size = Vector2(100, 100)
			cs.shape = rect
			sb.add_child(cs)
			reg.add_child(sb)
			var poly := NavigationPolygon.new()
			poly.baking_rect = Rect2(-150, -150, 300, 300)
			poly.agent_radius = 5.0
			reg.navigation_polygon = poly
			await physics_frame
			await physics_frame
			var sgd := NavigationMeshSourceGeometryData2D.new()
			NavigationServer2D.parse_source_geometry_data(poly, sgd, reg, Callable())
			print("obs=", sgd.get_obstruction_outlines().size(), " trav=", sgd.get_traversable_outlines().size(),
				" bounds=", sgd.get_bounds())
			NavigationServer2D.bake_from_source_geometry_data(poly, sgd, Callable())
			print("bake polys=", poly.get_polygon_count(), " verts=", poly.vertices.size(),
				" rect=", poly.get_baking_rect())
			for i in range(4):
				await physics_frame
			var m: RID = reg.get_navigation_map()
			print("iter=", NavigationServer2D.map_get_iteration_id(m),
				" through=", NavigationServer2D.map_get_path(m, Vector2(-100, 0), Vector2(100, 0), true),
				" around=", NavigationServer2D.map_get_path(m, Vector2(-100, -100), Vector2(100, 100), true))
			root.queue_free()
		"navbake6":
			# route A: outline -> make_polygons_from_outlines (deprecated) then region + path across the hole
			var poly := NavigationPolygon.new()
			poly.add_outline(PackedVector2Array([Vector2(0, 0), Vector2(200, 0), Vector2(200, 200), Vector2(0, 200)]))
			poly.add_outline(PackedVector2Array([Vector2(60, 60), Vector2(60, 140), Vector2(140, 140), Vector2(140, 60)]))
			poly.make_polygons_from_outlines()
			print("outline_polys=", poly.get_polygon_count(), " verts=", poly.vertices.size(),
				" verts_pva=", poly.vertices)
			var map := NavigationServer2D.map_create()
			NavigationServer2D.map_set_active(map, true)
			var reg := NavigationServer2D.region_create()
			NavigationServer2D.region_set_map(reg, map)
			NavigationServer2D.region_set_navigation_polygon(reg, poly)
			for i in range(6):
				await physics_frame
			print("iter=", NavigationServer2D.map_get_iteration_id(map),
				" across_hole=", NavigationServer2D.map_get_path(map, Vector2(100, 20), Vector2(100, 180), true),
				" straight=", NavigationServer2D.map_get_path(map, Vector2(20, 100), Vector2(180, 100), true))
			NavigationServer2D.free_rid(reg)
			NavigationServer2D.free_rid(map)
		"navbake7":
			# modern route with an explicit traversable outline + collider obstruction
			var root := Node2D.new()
			get_root().add_child(root)
			var reg := NavigationRegion2D.new()
			root.add_child(reg)
			var sb := StaticBody2D.new()
			var cs := CollisionShape2D.new()
			var rect := RectangleShape2D.new()
			rect.size = Vector2(100, 100)
			cs.shape = rect
			sb.add_child(cs)
			reg.add_child(sb)
			var poly := NavigationPolygon.new()
			poly.baking_rect = Rect2(-150, -150, 300, 300)
			poly.agent_radius = 5.0
			reg.navigation_polygon = poly
			await physics_frame
			await physics_frame
			var sgd := NavigationMeshSourceGeometryData2D.new()
			NavigationServer2D.parse_source_geometry_data(poly, sgd, reg, Callable())
			sgd.add_traversable_outline(PackedVector2Array([Vector2(-150, -150), Vector2(150, -150), Vector2(150, 150), Vector2(-150, 150)]))
			print("obs=", sgd.get_obstruction_outlines().size(), " trav=", sgd.get_traversable_outlines().size(),
				" has=", sgd.has_data())
			NavigationServer2D.bake_from_source_geometry_data(poly, sgd, Callable())
			print("bake polys=", poly.get_polygon_count(), " verts=", poly.vertices.size())
			reg.navigation_polygon = null
			reg.navigation_polygon = poly
			for i in range(5):
				await physics_frame
			var m: RID = reg.get_navigation_map()
			print("iter=", NavigationServer2D.map_get_iteration_id(m),
				" through=", NavigationServer2D.map_get_path(m, Vector2(-100, 0), Vector2(100, 0), true),
				" around=", NavigationServer2D.map_get_path(m, Vector2(-100, -100), Vector2(100, 100), true),
				" outside=", NavigationServer2D.map_get_path(m, Vector2(-200, -200), Vector2(100, 100), true))
			root.queue_free()
		"navbake8":
			# bake output fed to a fresh server region; print vertices + per-frame diagnostics
			var root := Node2D.new()
			get_root().add_child(root)
			var reg := NavigationRegion2D.new()
			root.add_child(reg)
			var sb := StaticBody2D.new()
			var cs := CollisionShape2D.new()
			var rect := RectangleShape2D.new()
			rect.size = Vector2(100, 100)
			cs.shape = rect
			sb.add_child(cs)
			reg.add_child(sb)
			var poly := NavigationPolygon.new()
			poly.baking_rect = Rect2(-150, -150, 300, 300)
			poly.agent_radius = 5.0
			reg.navigation_polygon = poly
			await physics_frame
			await physics_frame
			var sgd := NavigationMeshSourceGeometryData2D.new()
			NavigationServer2D.parse_source_geometry_data(poly, sgd, reg, Callable())
			sgd.add_traversable_outline(PackedVector2Array([Vector2(-150, -150), Vector2(150, -150), Vector2(150, 150), Vector2(-150, 150)]))
			NavigationServer2D.bake_from_source_geometry_data(poly, sgd, Callable())
			print("baked_polys=", poly.get_polygon_count(), " verts=", poly.vertices)
			for i in range(poly.get_polygon_count()):
				print("poly", i, "=", poly.get_polygon(i))
			var map := NavigationServer2D.map_create()
			NavigationServer2D.map_set_active(map, true)
			var sreg := NavigationServer2D.region_create()
			NavigationServer2D.region_set_map(sreg, map)
			NavigationServer2D.region_set_navigation_polygon(sreg, poly)
			for i in range(5):
				await physics_frame
				print("f", i, " iter=", NavigationServer2D.map_get_iteration_id(map),
					" bounds=", NavigationServer2D.region_get_bounds(sreg))
			print("through=", NavigationServer2D.map_get_path(map, Vector2(-100, 0), Vector2(100, 0), true),
				" around=", NavigationServer2D.map_get_path(map, Vector2(-100, -100), Vector2(100, 100), true))
			NavigationServer2D.free_rid(sreg)
			NavigationServer2D.free_rid(map)
			root.queue_free()
		"navsync3":
			for async_mode in [true, false]:
				var map := NavigationServer2D.map_create()
				NavigationServer2D.map_set_active(map, true)
				NavigationServer2D.map_set_use_async_iterations(map, async_mode)
				var reg := NavigationServer2D.region_create()
				NavigationServer2D.region_set_map(reg, map)
				NavigationServer2D.region_set_navigation_polygon(reg, _quad_poly(0, 0, 100, 100))
				var init_ladder: Array[String] = []
				for i in range(8):
					await physics_frame
					init_ladder.append("f%d:mi=%d,ri=%d,reach=%s" % [i,
						NavigationServer2D.map_get_iteration_id(map),
						NavigationServer2D.region_get_iteration_id(reg),
						str(_reach(map, Vector2(10, 10), Vector2(90, 90)))])
				print("async=", async_mode, " init=", _ps(init_ladder))
				NavigationServer2D.region_set_transform(reg, Transform2D(0.0, Vector2(500, 0)))
				NavigationServer2D.map_force_update(map)
				var chg: Array[String] = []
				for i in range(8):
					chg.append("f%d:mi=%d,ri=%d,reach=%s" % [i,
						NavigationServer2D.map_get_iteration_id(map),
						NavigationServer2D.region_get_iteration_id(reg),
						str(_reach(map, Vector2(510, 10), Vector2(590, 90)))])
					await physics_frame
				print("chg=", _ps(chg))
				NavigationServer2D.region_set_enabled(reg, false)
				NavigationServer2D.map_force_update(map)
				var dis: Array[String] = []
				for i in range(8):
					dis.append("f%d:ri=%d,reach=%s" % [i,
						NavigationServer2D.region_get_iteration_id(reg),
						str(_reach(map, Vector2(510, 10), Vector2(590, 90)))])
					await physics_frame
				print("dis=", _ps(dis))
				NavigationServer2D.free_rid(reg)
				NavigationServer2D.free_rid(map)
		"navpoly2":
			# do two hand-built polygons inside ONE NavigationPolygon connect across a shared edge?
			var map := NavigationServer2D.map_create()
			NavigationServer2D.map_set_active(map, true)
			var p1 := NavigationPolygon.new()
			p1.vertices = PackedVector2Array([Vector2(0, 0), Vector2(40, 0), Vector2(40, 200), Vector2(0, 200),
				Vector2(200, 0), Vector2(200, 40), Vector2(40, 40)])
			p1.add_polygon(PackedInt32Array([0, 1, 2, 3]))
			p1.add_polygon(PackedInt32Array([1, 4, 5, 6]))
			var r1 := NavigationServer2D.region_create()
			NavigationServer2D.region_set_map(r1, map)
			NavigationServer2D.region_set_navigation_polygon(r1, p1)
			for i in range(10):
				await physics_frame
			print("two_poly_one_region: verts=", p1.vertices, " polys=", p1.get_polygon_count())
			print("  across=", _reach(map, Vector2(20, 180), Vector2(180, 20)),
				" path=", NavigationServer2D.map_get_path(map, Vector2(20, 180), Vector2(180, 20), true))
			# same L as two regions
			var rv := NavigationServer2D.region_create()
			NavigationServer2D.region_set_map(rv, map)
			NavigationServer2D.region_set_navigation_polygon(rv, _quad_poly(300, 0, 340, 200))
			var rh := NavigationServer2D.region_create()
			NavigationServer2D.region_set_map(rh, map)
			NavigationServer2D.region_set_navigation_polygon(rh, _quad_poly(340, 0, 500, 40))
			for i in range(10):
				await physics_frame
			print("two_regions_L: across=", _reach(map, Vector2(320, 180), Vector2(480, 20)),
				" path=", NavigationServer2D.map_get_path(map, Vector2(320, 180), Vector2(480, 20), true))
			NavigationServer2D.free_rid(rv)
			NavigationServer2D.free_rid(rh)
			NavigationServer2D.free_rid(r1)
			NavigationServer2D.free_rid(map)
		_:
			print("UNKNOWN_ARM ", arm)
	quit(0)
