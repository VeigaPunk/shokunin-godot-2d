extends SceneTree
# r89 scout probe — Geometry2D authorability lattice (r88-census top-ranked surface).
# Battery launch shape: godot --headless --path <scratch> --script res://geo2d_lattice.gd -- --arm=<name>
# Arm parse is the battery convention (OS.get_cmdline_user_args + "--arm=" prefix scan);
# a silent arm fallback is impossible: every arm prints its own name on the PASS line.
# Prints `R89 <arm> <key>=<value>` diagnostics and one final
# `PASS geo2d_lattice <arm> <key>=<value> ...` line (the authorable signature).
# No object ids / RIDs / addresses are printed (byte-stability).
# `_poly2str` / `_poly2str_area` shapes follow the r88 census helpers verbatim.

var arm := ""
var _items: PackedStringArray = []
var _frames := 60

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
		elif a.begins_with("--frames="):
			_frames = int(a.substr(9))
	_run.call_deferred()

func _it(key: String, value: String) -> void:
	_items.append("%s=%s" % [key, value])
	print("R89 %s %s=%s" % [arm, key, value])

func _pass() -> void:
	print("PASS geo2d_lattice %s %s" % [arm, " ".join(_items)])
	quit()

func _v2(p: Vector2) -> String:
	return "%.4f,%.4f" % [p.x, p.y]

func _area(poly: PackedVector2Array) -> float:
	var a := 0.0
	for i in poly.size():
		var p := poly[i]
		var q := poly[(i + 1) % poly.size()]
		a += p.x * q.y - q.x * p.y
	return a / 2.0

func _poly2str(arr: Array) -> String:
	var parts: PackedStringArray = []
	for poly in arr:
		var verts: PackedStringArray = []
		for v in poly:
			verts.append(_v2(v))
		parts.append("n%d[%s]" % [poly.size(), ";".join(verts)])
	return "k=%d{%s}" % [arr.size(), "|".join(parts)]

func _poly2str_area(arr: Array) -> String:
	var parts: PackedStringArray = []
	for poly in arr:
		var verts: PackedStringArray = []
		for v in poly:
			verts.append(_v2(v))
		parts.append("n%d[%s] a=%.4f" % [poly.size(), ";".join(verts), _area(poly)])
	return "k=%d{%s}" % [arr.size(), "|".join(parts)]

func _atlas2str(d: Dictionary) -> String:
	var pts: PackedStringArray = []
	for p in d["points"]:
		pts.append("(%s)" % _v2(p))
	var s: Vector2 = d["size"]
	return "points=[%s] size=(%s)" % [",".join(pts), _v2(s)]

func _tri_area(poly: PackedVector2Array, idx: PackedInt32Array) -> float:
	var t := 0.0
	var i := 0
	while i + 2 < idx.size():
		t += absf(_area(PackedVector2Array([poly[idx[i]], poly[idx[i + 1]], poly[idx[i + 2]]])))
		i += 3
	return t

func _sq(cx: float, cy: float, r: float) -> PackedVector2Array:
	return PackedVector2Array([Vector2(cx - r, cy - r), Vector2(cx + r, cy - r),
		Vector2(cx + r, cy + r), Vector2(cx - r, cy + r)])

func _body(x: float, y: float) -> RigidBody2D:
	var b := RigidBody2D.new()
	var cs := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = 8.0
	cs.shape = circle
	b.add_child(cs)
	b.position = Vector2(x, y)
	return b

func _run() -> void:
	match arm:
		"census": _arm_census()
		"ops": _arm_ops()
		"contain": _arm_contain()
		"joins": _arm_joins()
		"trig": _arm_trig()
		"pred": _arm_pred()
		"edge": _arm_edge()
		"offempty": _arm_offempty()
		"offdeg": _arm_offdeg()
		"lineempty": _arm_lineempty()
		"atlasempty": _arm_atlasempty()
		"bridge": _arm_bridge()
		"bridge_hole": _arm_bridge_hole()
		"bridge_hole2": _arm_bridge_hole2()
		"ring": _arm_ring()
		"ring2": _arm_ring2()
		"ring4": _arm_ring4()
		"pipedges": _arm_pipedges()
		"ringhits": _arm_ringhits()
		"polyendpoly": _arm_polyendpoly()
		_: _arm_census()

# ---------- API census ----------

func _arm_census() -> void:
	var sig: PackedStringArray = []
	for m in ClassDB.class_get_method_list("Geometry2D"):
		var n := String(m["name"])
		if n in ["offset_polygon", "offset_polyline", "make_atlas", "triangulate_polygon",
				"convex_hull", "decompose_polygon_in_convex", "merge_polygons", "clip_polygons"]:
			var args: PackedStringArray = []
			for a in m["args"]:
				args.append(String(a["name"]))
			sig.append("%s(%s)" % [n, ",".join(args)])
	sig.sort()
	_it("sig", "[%s]" % "|".join(sig))
	_it("join", "SQ=%d,RD=%d,MT=%d" % [Geometry2D.JOIN_SQUARE, Geometry2D.JOIN_ROUND, Geometry2D.JOIN_MITER])
	_it("end", "POLY=%d,JOINED=%d,BUTT=%d,SQUARE=%d,ROUND=%d" % [Geometry2D.END_POLYGON,
		Geometry2D.END_JOINED, Geometry2D.END_BUTT, Geometry2D.END_SQUARE, Geometry2D.END_ROUND])
	_it("op", "UNION=%d,DIFF=%d,INTER=%d,XOR=%d" % [Geometry2D.OPERATION_UNION,
		Geometry2D.OPERATION_DIFFERENCE, Geometry2D.OPERATION_INTERSECTION, Geometry2D.OPERATION_XOR])
	_it("nmethods", "%d" % ClassDB.class_get_method_list("Geometry2D").size())
	var a := _sq(0, 0, 10)
	var d2 := _poly2str(Geometry2D.offset_polygon(a, 2.0))
	var m := ""
	for jn in [["sq", Geometry2D.JOIN_SQUARE], ["rd", Geometry2D.JOIN_ROUND], ["mt", Geometry2D.JOIN_MITER]]:
		if _poly2str(Geometry2D.offset_polygon(a, 2.0, jn[1])) == d2:
			m += String(jn[0]) + ","
	_it("default_join_polygon", "%s match=[%s]" % [d2, m])
	var line := PackedVector2Array([Vector2(0, 0), Vector2(20, 0), Vector2(20, 20)])
	var dl := _poly2str(Geometry2D.offset_polyline(line, 2.0))
	var ml := ""
	for jn in [["sq", Geometry2D.JOIN_SQUARE], ["rd", Geometry2D.JOIN_ROUND], ["mt", Geometry2D.JOIN_MITER]]:
		for en in [["joined", Geometry2D.END_JOINED],
				["butt", Geometry2D.END_BUTT], ["square", Geometry2D.END_SQUARE], ["round", Geometry2D.END_ROUND]]:
			if _poly2str(Geometry2D.offset_polyline(line, 2.0, jn[1], en[1])) == dl:
				ml += "%s/%s," % [jn[0], en[0]]
	_it("default_polyline", "%s match=[%s]" % [dl, ml])
	_pass()

# ---------- boolean ops on two overlapping squares (r88 census reproduction) ----------

func _arm_ops() -> void:
	var a := _sq(0, 0, 10)
	var b := _sq(8, 0, 10)
	_it("clip", _poly2str(Geometry2D.clip_polygons(a, b)))
	_it("merge", _poly2str(Geometry2D.merge_polygons(a, b)))
	_it("inter", _poly2str(Geometry2D.intersect_polygons(a, b)))
	_it("excl", _poly2str_area(Geometry2D.exclude_polygons(a, b)))
	var tri := Geometry2D.triangulate_polygon(a)
	_it("tri_idx", "%s tri_area=%.4f poly_area=%.4f" % [str(tri), _tri_area(a, tri), absf(_area(a))])
	_it("off_p2_sq", _poly2str_area(Geometry2D.offset_polygon(a, 2.0, Geometry2D.JOIN_SQUARE)))
	_it("off_p2_rd", _poly2str_area(Geometry2D.offset_polygon(a, 2.0, Geometry2D.JOIN_ROUND)))
	_it("off_p2_mt", _poly2str_area(Geometry2D.offset_polygon(a, 2.0, Geometry2D.JOIN_MITER)))
	_it("off_m2_sq", _poly2str_area(Geometry2D.offset_polygon(a, -2.0, Geometry2D.JOIN_SQUARE)))
	_it("off_m2_rd", _poly2str_area(Geometry2D.offset_polygon(a, -2.0, Geometry2D.JOIN_ROUND)))
	_it("off_m2_mt", _poly2str_area(Geometry2D.offset_polygon(a, -2.0, Geometry2D.JOIN_MITER)))
	_pass()

# ---------- containment / hole semantics (new this round) ----------

func _arm_contain() -> void:
	var big := _sq(0, 0, 20)
	var small := _sq(0, 0, 5)
	_it("merge_bs", _poly2str_area(Geometry2D.merge_polygons(big, small)))
	_it("merge_sb", _poly2str_area(Geometry2D.merge_polygons(small, big)))
	_it("clip_bs", _poly2str_area(Geometry2D.clip_polygons(big, small)))
	_it("clip_sb", _poly2str_area(Geometry2D.clip_polygons(small, big)))
	_it("inter_bs", _poly2str_area(Geometry2D.intersect_polygons(big, small)))
	_it("inter_sb", _poly2str_area(Geometry2D.intersect_polygons(small, big)))
	_it("excl_bs", _poly2str_area(Geometry2D.exclude_polygons(big, small)))
	_it("excl_sb", _poly2str_area(Geometry2D.exclude_polygons(small, big)))
	var l := _sq(0, 0, 10)
	var r := _sq(20, 0, 10)
	_it("adj_merge", _poly2str_area(Geometry2D.merge_polygons(l, r)))
	_it("adj_clip", _poly2str_area(Geometry2D.clip_polygons(l, r)))
	_it("adj_inter", _poly2str_area(Geometry2D.intersect_polygons(l, r)))
	var o := _sq(6, 6, 10)
	_it("ovl_excl", _poly2str_area(Geometry2D.exclude_polygons(l, o)))
	_it("ovl_clip", _poly2str_area(Geometry2D.clip_polygons(l, o)))
	_it("ovl_inter", _poly2str_area(Geometry2D.intersect_polygons(l, o)))
	_pass()

# ---------- join / end-type lattice (new this round) ----------

func _arm_joins() -> void:
	var a := _sq(0, 0, 10)
	_it("poly_p2_sq", _poly2str_area(Geometry2D.offset_polygon(a, 2.0, Geometry2D.JOIN_SQUARE)))
	_it("poly_p2_rd", _poly2str_area(Geometry2D.offset_polygon(a, 2.0, Geometry2D.JOIN_ROUND)))
	_it("poly_p2_mt", _poly2str_area(Geometry2D.offset_polygon(a, 2.0, Geometry2D.JOIN_MITER)))
	_it("poly_m2_sq", _poly2str_area(Geometry2D.offset_polygon(a, -2.0, Geometry2D.JOIN_SQUARE)))
	_it("poly_m2_rd", _poly2str_area(Geometry2D.offset_polygon(a, -2.0, Geometry2D.JOIN_ROUND)))
	_it("poly_m2_mt", _poly2str_area(Geometry2D.offset_polygon(a, -2.0, Geometry2D.JOIN_MITER)))
	_it("poly_zero", _poly2str_area(Geometry2D.offset_polygon(a, 0.0, Geometry2D.JOIN_ROUND)))
	_it("poly_collapse", _poly2str_area(Geometry2D.offset_polygon(a, -20.0, Geometry2D.JOIN_ROUND)))
	var line := PackedVector2Array([Vector2(0, 0), Vector2(20, 0), Vector2(20, 20)])
	_it("line_rd_joined", _poly2str_area(Geometry2D.offset_polyline(line, 2.0, Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_it("line_sq_joined", _poly2str_area(Geometry2D.offset_polyline(line, 2.0, Geometry2D.JOIN_SQUARE, Geometry2D.END_JOINED)))
	_it("line_mt_joined", _poly2str_area(Geometry2D.offset_polyline(line, 2.0, Geometry2D.JOIN_MITER, Geometry2D.END_JOINED)))
	_it("line_rd_butt", _poly2str_area(Geometry2D.offset_polyline(line, 2.0, Geometry2D.JOIN_ROUND, Geometry2D.END_BUTT)))
	_it("line_rd_square", _poly2str_area(Geometry2D.offset_polyline(line, 2.0, Geometry2D.JOIN_ROUND, Geometry2D.END_SQUARE)))
	_it("line_rd_round", _poly2str_area(Geometry2D.offset_polyline(line, 2.0, Geometry2D.JOIN_ROUND, Geometry2D.END_ROUND)))
	_it("line_m2_joined", _poly2str_area(Geometry2D.offset_polyline(line, -2.0, Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_it("line_default", _poly2str_area(Geometry2D.offset_polyline(line, 2.0)))
	_pass()

# ---------- triangulation / hull / decomposition / atlas ----------

func _arm_trig() -> void:
	var concave := PackedVector2Array([Vector2(0, 0), Vector2(20, 0), Vector2(20, 20),
		Vector2(10, 8), Vector2(0, 20)])
	var hull := Geometry2D.convex_hull(concave)
	_it("hull", _poly2str([hull]))
	var tri := Geometry2D.triangulate_polygon(concave)
	_it("tri_idx", "%s tri_area=%.4f poly_area=%.4f" % [str(tri), _tri_area(concave, tri), absf(_area(concave))])
	var dec := Geometry2D.decompose_polygon_in_convex(concave)
	var dec_area := 0.0
	for p in dec:
		dec_area += absf(_area(p))
	_it("decomp", "%s dec_area=%.4f" % [_poly2str(dec), dec_area])
	var pts := PackedVector2Array([Vector2(0, 0), Vector2(30, 0), Vector2(15, 26),
		Vector2(8, 8), Vector2(22, 8)])
	_it("delaunay", str(Geometry2D.triangulate_delaunay(pts)))
	_it("atlas3", _atlas2str(Geometry2D.make_atlas(PackedVector2Array([Vector2(20, 10), Vector2(5, 5), Vector2(3, 3)]))))
	_it("atlas1", _atlas2str(Geometry2D.make_atlas(PackedVector2Array([Vector2(4, 4)]))))
	_it("atlas_sq", _atlas2str(Geometry2D.make_atlas(PackedVector2Array([Vector2(7, 3), Vector2(7, 3)]))))
	_pass()

# ---------- predicates ----------

func _arm_pred() -> void:
	var sq := _sq(0, 0, 10)
	_it("pip", "in=%s out=%s edge=%s corner=%s outside_corner=%s" % [
		Geometry2D.is_point_in_polygon(Vector2(5, 5), sq),
		Geometry2D.is_point_in_polygon(Vector2(15, 5), sq),
		Geometry2D.is_point_in_polygon(Vector2(10, 5), sq),
		Geometry2D.is_point_in_polygon(Vector2(10, 10), sq),
		Geometry2D.is_point_in_polygon(Vector2(10.0001, 5), sq)])
	_it("pic", "on=%s out=%s center=%s" % [
		Geometry2D.is_point_in_circle(Vector2(3, 4), Vector2(0, 0), 5.0),
		Geometry2D.is_point_in_circle(Vector2(6, 0), Vector2(0, 0), 5.0),
		Geometry2D.is_point_in_circle(Vector2(0, 0), Vector2(0, 0), 5.0)])
	var li = Geometry2D.line_intersects_line(Vector2(0, 0), Vector2(1, 0), Vector2(2, -1), Vector2(0, 1))
	var si = Geometry2D.segment_intersects_segment(Vector2(0, 0), Vector2(4, 0), Vector2(2, -1), Vector2(2, 1))
	var sm = Geometry2D.segment_intersects_segment(Vector2(0, 0), Vector2(1, 0), Vector2(2, -1), Vector2(2, 1))
	_it("isect", "line=%s seg=%s miss=%s" % [str(li), str(si), str(sm)])
	_it("closest", "cap=%s uncap=%s segseg=%s degenerate=%s" % [
		Geometry2D.get_closest_point_to_segment(Vector2(3, 4), Vector2(0, 0), Vector2(10, 0)),
		Geometry2D.get_closest_point_to_segment_uncapped(Vector2(13, 4), Vector2(0, 0), Vector2(10, 0)),
		Geometry2D.get_closest_points_between_segments(Vector2(0, 0), Vector2(10, 0), Vector2(5, -2), Vector2(5, 2)),
		Geometry2D.get_closest_point_to_segment(Vector2(3, 4), Vector2(2, 2), Vector2(2, 2))])
	_it("tri", "in=%s out=%s edge=%s vertex=%s" % [
		Geometry2D.point_is_inside_triangle(Vector2(1, 1), Vector2(0, 0), Vector2(4, 0), Vector2(0, 4)),
		Geometry2D.point_is_inside_triangle(Vector2(4, 4), Vector2(0, 0), Vector2(4, 0), Vector2(0, 4)),
		Geometry2D.point_is_inside_triangle(Vector2(2, 0), Vector2(0, 0), Vector2(4, 0), Vector2(0, 4)),
		Geometry2D.point_is_inside_triangle(Vector2(0, 0), Vector2(0, 0), Vector2(4, 0), Vector2(0, 4))])
	_it("bresenham", "fwd=%s rev=%s diag=%s" % [
		str(Geometry2D.bresenham_line(Vector2(0, 0), Vector2(5, 3))),
		str(Geometry2D.bresenham_line(Vector2(5, 3), Vector2(0, 0))),
		str(Geometry2D.bresenham_line(Vector2(0, 0), Vector2(3, 3)))])
	_it("sic", "fwd=%.4f rev=%.4f miss=%.4f inside=%.4f startinside=%.4f tangent=%.4f" % [
		Geometry2D.segment_intersects_circle(Vector2(-10, 0), Vector2(10, 0), Vector2(0, 0), 5.0),
		Geometry2D.segment_intersects_circle(Vector2(10, 0), Vector2(-10, 0), Vector2(0, 0), 5.0),
		Geometry2D.segment_intersects_circle(Vector2(-10, 10), Vector2(10, 10), Vector2(0, 0), 5.0),
		Geometry2D.segment_intersects_circle(Vector2(-3, 0), Vector2(3, 0), Vector2(0, 0), 5.0),
		Geometry2D.segment_intersects_circle(Vector2(0, 0), Vector2(10, 0), Vector2(0, 0), 5.0),
		Geometry2D.segment_intersects_circle(Vector2(-10, 5), Vector2(10, 5), Vector2(0, 0), 5.0)])
	_pass()

# ---------- degenerate inputs (all known-clean calls) ----------

func _arm_edge() -> void:
	var empty := PackedVector2Array()
	var sq := _sq(0, 0, 10)
	var one := PackedVector2Array([Vector2(1, 1)])
	var two := PackedVector2Array([Vector2(0, 0), Vector2(4, 0)])
	var dup := PackedVector2Array([Vector2(0, 0), Vector2(0, 0), Vector2(4, 0), Vector2(4, 0)])
	var col := PackedVector2Array([Vector2(0, 0), Vector2(1, 0), Vector2(2, 0)])
	var bow := PackedVector2Array([Vector2(0, 0), Vector2(10, 10), Vector2(10, 0), Vector2(0, 10)])
	_it("clip_emptyR", _poly2str(Geometry2D.clip_polygons(sq, empty)))
	_it("merge_emptyR", _poly2str(Geometry2D.merge_polygons(sq, empty)))
	_it("inter_emptyR", _poly2str(Geometry2D.intersect_polygons(sq, empty)))
	_it("excl_emptyR", _poly2str(Geometry2D.exclude_polygons(sq, empty)))
	_it("clip_emptyL", _poly2str(Geometry2D.clip_polygons(empty, sq)))
	_it("merge_emptyL", _poly2str(Geometry2D.merge_polygons(empty, sq)))
	_it("inter_emptyL", _poly2str(Geometry2D.intersect_polygons(empty, sq)))
	_it("clip_self", _poly2str(Geometry2D.clip_polygons(sq, sq)))
	_it("merge_self", _poly2str(Geometry2D.merge_polygons(sq, sq)))
	_it("inter_self", _poly2str(Geometry2D.intersect_polygons(sq, sq)))
	_it("excl_self", _poly2str(Geometry2D.exclude_polygons(sq, sq)))
	_it("clip_one", _poly2str(Geometry2D.clip_polygons(one, sq)))
	_it("clip_two", _poly2str(Geometry2D.clip_polygons(two, sq)))
	_it("tri", "one=%s two=%s dup=%s col=%s bow=%s sq=%s" % [
		str(Geometry2D.triangulate_polygon(one)),
		str(Geometry2D.triangulate_polygon(two)),
		str(Geometry2D.triangulate_polygon(dup)),
		str(Geometry2D.triangulate_polygon(col)),
		str(Geometry2D.triangulate_polygon(bow)),
		str(Geometry2D.triangulate_polygon(sq))])
	_it("cw", "sq=%s rev=%s one=%s two=%s col=%s bow=%s" % [
		Geometry2D.is_polygon_clockwise(sq),
		Geometry2D.is_polygon_clockwise(PackedVector2Array([sq[0], sq[3], sq[2], sq[1]])),
		Geometry2D.is_polygon_clockwise(one),
		Geometry2D.is_polygon_clockwise(two),
		Geometry2D.is_polygon_clockwise(col),
		Geometry2D.is_polygon_clockwise(bow)])
	_it("pip_degen", "bow=%s col=%s one=%s" % [
		Geometry2D.is_point_in_polygon(Vector2(5, 5), bow),
		Geometry2D.is_point_in_polygon(Vector2(1, 0), col),
		Geometry2D.is_point_in_polygon(Vector2(1, 1), one)])
	_it("clip_bow", _poly2str(Geometry2D.clip_polygons(bow, sq)))
	_it("clip_rev", _poly2str(Geometry2D.clip_polygons(PackedVector2Array([sq[0], sq[3], sq[2], sq[1]]), _sq(8, 0, 10))))
	_it("hull_degen", "one=%s col=%s sq=%s" % [
		_poly2str([Geometry2D.convex_hull(one)]),
		_poly2str([Geometry2D.convex_hull(col)]),
		_poly2str([Geometry2D.convex_hull(sq)])])
	_pass()

# ---------- isolated boundary arms (one risky call per process) ----------

func _arm_offempty() -> void:
	_it("call", "offset_polygon(empty,2.0,JOIN_ROUND)")
	var r := Geometry2D.offset_polygon(PackedVector2Array(), 2.0, Geometry2D.JOIN_ROUND)
	_it("result", _poly2str(r))
	_pass()

func _arm_offdeg() -> void:
	var col := PackedVector2Array([Vector2(0, 0), Vector2(1, 0), Vector2(2, 0)])
	_it("col3", _poly2str(Geometry2D.offset_polygon(col, 2.0, Geometry2D.JOIN_ROUND)))
	var two := PackedVector2Array([Vector2(0, 0), Vector2(4, 0)])
	_it("two", _poly2str(Geometry2D.offset_polygon(two, 2.0, Geometry2D.JOIN_ROUND)))
	var one := PackedVector2Array([Vector2(1, 1)])
	_it("one", _poly2str(Geometry2D.offset_polygon(one, 2.0, Geometry2D.JOIN_ROUND)))
	_pass()

func _arm_lineempty() -> void:
	_it("call", "offset_polyline(empty,2.0,JOIN_ROUND,END_JOINED)")
	var r := Geometry2D.offset_polyline(PackedVector2Array(), 2.0, Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)
	_it("result", _poly2str(r))
	_pass()

func _arm_atlasempty() -> void:
	_it("call", "make_atlas(empty)")
	var r := Geometry2D.make_atlas(PackedVector2Array())
	_it("result", _atlas2str(r))
	_pass()

# ---------- geometry -> CollisionPolygon2D -> falling body (lifecycle cells) ----------

func _arm_bridge() -> void:
	var wall := Geometry2D.clip_polygons(_sq(0, 0, 60), _sq(0, -30, 60))
	var st := StaticBody2D.new()
	var pol := CollisionPolygon2D.new()
	if wall.size() > 0:
		pol.polygon = wall[0]
	st.add_child(pol)
	st.position = Vector2(0, 60)
	root.add_child(st)
	var b := _body(0, -100)
	root.add_child(b)
	for i in _frames:
		await physics_frame
	var dss := root.world_2d.direct_space_state
	var q := PhysicsPointQueryParameters2D.new()
	q.position = b.global_position
	var hits := dss.intersect_point(q)
	_it("wall", _poly2str(wall))
	_it("tps", "%d frames=%d" % [Engine.physics_ticks_per_second, _frames])
	_it("rest", "y=%.4f vel=%.4f,%.4f self_hit=%d" % [b.global_position.y,
		b.linear_velocity.x, b.linear_velocity.y, hits.size()])
	_pass()

func _arm_bridge_hole() -> void:
	# merge() of a contained square yields TWO contours: outer + hole (negative winding).
	# CollisionPolygon2D carries ONE contour — measure what the collider does with contour[0].
	var big := _sq(0, 0, 40)
	var small := _sq(0, 0, 10)
	var merged := Geometry2D.merge_polygons(big, small)
	var outer := 0
	var best := -1.0
	for i in merged.size():
		if absf(_area(merged[i])) > best:
			best = absf(_area(merged[i]))
			outer = i
	var st := StaticBody2D.new()
	var pol := CollisionPolygon2D.new()
	pol.polygon = merged[outer]
	st.add_child(pol)
	root.add_child(st)
	var b := _body(0, -60)
	root.add_child(b)
	for i in 90:
		await physics_frame
	_it("merged", _poly2str_area(merged))
	_it("outer_idx", "%d outer_area=%.4f" % [outer, _area(merged[outer])])
	_it("drop", "y=%.4f vel=%.4f,%.4f" % [b.global_position.y, b.linear_velocity.x, b.linear_velocity.y])
	_pass()

func _arm_bridge_hole2() -> void:
	# Same geometry, but BOTH contours are attached as separate CollisionPolygon2Ds:
	# if holes were subtractive the centre body would fall through; measure.
	var big := _sq(0, 0, 40)
	var small := _sq(0, 0, 10)
	var merged := Geometry2D.merge_polygons(big, small)
	var st := StaticBody2D.new()
	for i in merged.size():
		var pol := CollisionPolygon2D.new()
		pol.polygon = merged[i]
		st.add_child(pol)
	root.add_child(st)
	var b := _body(0, -60)
	root.add_child(b)
	for i in 90:
		await physics_frame
	_it("merged", _poly2str_area(merged))
	_it("polys", "%d" % merged.size())
	_it("drop", "y=%.4f vel=%.4f,%.4f" % [b.global_position.y, b.linear_velocity.x, b.linear_velocity.y])
	_pass()

# ---------- round-2: the hole cell (clip-based ring), boundary ladders ----------

func _rect(x0: float, y0: float, x1: float, y1: float) -> PackedVector2Array:
	return PackedVector2Array([Vector2(x0, y0), Vector2(x1, y0), Vector2(x1, y1), Vector2(x0, y1)])

func _drop_for(frames: int) -> Array:
	var b := _body(0, -60)
	root.add_child(b)
	for i in frames:
		await physics_frame
	var dss := root.world_2d.direct_space_state
	var q := PhysicsPointQueryParameters2D.new()
	q.position = b.global_position
	var hits := dss.intersect_point(q)
	return [b.global_position.y, b.linear_velocity.x, b.linear_velocity.y, hits.size()]

func _arm_ring() -> void:
	# clip_polygons IS the hole-producing op (merge collapses it): contour0 = outer, contour1 = hole.
	var ring := Geometry2D.clip_polygons(_sq(0, 0, 40), _sq(0, 0, 10))
	var st := StaticBody2D.new()
	var pol := CollisionPolygon2D.new()
	pol.polygon = ring[0]
	st.add_child(pol)
	root.add_child(st)
	var r := await _drop_for(_frames)
	_it("ring", _poly2str_area(ring))
	_it("colliders", "n=1 contour0_only")
	_it("drop_center", "y=%.4f vel=%.4f,%.4f hits=%d tps=%d frames=%d" % [r[0], r[1], r[2], r[3],
		Engine.physics_ticks_per_second, _frames])
	_pass()

func _arm_ring2() -> void:
	var ring := Geometry2D.clip_polygons(_sq(0, 0, 40), _sq(0, 0, 10))
	var st := StaticBody2D.new()
	var n := 0
	for c in ring:
		if c.size() >= 3:
			var pol := CollisionPolygon2D.new()
			pol.polygon = c
			st.add_child(pol)
			n += 1
	root.add_child(st)
	var r := await _drop_for(_frames)
	_it("ring", _poly2str_area(ring))
	_it("colliders", "n=%d all_contours" % n)
	_it("drop_center", "y=%.4f vel=%.4f,%.4f hits=%d tps=%d frames=%d" % [r[0], r[1], r[2], r[3],
		Engine.physics_ticks_per_second, _frames])
	_pass()

func _arm_ring4() -> void:
	# Positive control: a hole CAN be authored as several solid slabs (no subtractive shape exists).
	var slabs := [_rect(-40, -40, 40, -10), _rect(-40, 10, 40, 40), _rect(-40, -10, -10, 10), _rect(10, -10, 40, 10)]
	var st := StaticBody2D.new()
	for s in slabs:
		var pol := CollisionPolygon2D.new()
		pol.polygon = s
		st.add_child(pol)
	root.add_child(st)
	var r := await _drop_for(_frames)
	_it("slabs", "%d" % slabs.size())
	_it("drop_center", "y=%.4f vel=%.4f,%.4f hits=%d tps=%d frames=%d" % [r[0], r[1], r[2], r[3],
		Engine.physics_ticks_per_second, _frames])
	_pass()

func _arm_pipedges() -> void:
	# Boundary-policy ladders (labels are literal: GDScript % formatting has no %e).
	var sq := _sq(0, 0, 10)
	var cw := PackedVector2Array([sq[0], sq[3], sq[2], sq[1]])
	var ds := [0.0, 0.000001, 0.0001, 0.001, 0.01, 0.1, 1.0]
	var ls := ["0", "1e-6", "1e-4", "1e-3", "1e-2", "0.1", "1.0"]
	var lad: PackedStringArray = []
	for i in ds.size():
		lad.append("%s:%s" % [ls[i], Geometry2D.is_point_in_polygon(Vector2(10.0 + ds[i], 5.0), sq)])
	_it("pip_right", "[%s]" % ",".join(lad))
	var lad2: PackedStringArray = []
	for i in [0, 2, 4, 5]:
		lad2.append("%s:%s" % [ls[i], Geometry2D.is_point_in_polygon(Vector2(10.0 + ds[i], 5.0), cw)])
	_it("pip_right_cw", "[%s]" % ",".join(lad2))
	_it("pip_corner", "on=%s e4=%s e2=%s d1=%s" % [
		Geometry2D.is_point_in_polygon(Vector2(10, 10), sq),
		Geometry2D.is_point_in_polygon(Vector2(10.0001, 10.0001), sq),
		Geometry2D.is_point_in_polygon(Vector2(10.01, 10.01), sq),
		Geometry2D.is_point_in_polygon(Vector2(10.1, 10.1), sq)])
	var lad3: PackedStringArray = []
	for i in [0, 1, 2, 4, 5]:
		lad3.append("%s:%s" % [ls[i], Geometry2D.point_is_inside_triangle(Vector2(2.0 + ds[i], ds[i]), Vector2(0, 0), Vector2(4, 0), Vector2(0, 4))])
	_it("tri_ladder", "[%s]" % ",".join(lad3))
	_it("circle_ladder", "on=%s in=%s out=%s" % [
		Geometry2D.is_point_in_circle(Vector2(5, 0), Vector2(0, 0), 5.0),
		Geometry2D.is_point_in_circle(Vector2(5.0 - 0.0001, 0), Vector2(0, 0), 5.0),
		Geometry2D.is_point_in_circle(Vector2(5.0 + 0.0001, 0), Vector2(0, 0), 5.0)])
	_pass()

func _arm_ringhits() -> void:
	# Hole semantics as a point-query discriminator: three collider builds of the same ring.
	#   A = clip contour0 only (outer)      B = A + the hole contour as a second polygon
	#   C = the ring authored as four solid slabs
	# Sample points (relative): centre (hole), top/right/bottom/left band midpoints.
	var ring := Geometry2D.clip_polygons(_sq(0, 0, 40), _sq(0, 0, 10))
	var builds: Array = []
	var a := StaticBody2D.new()
	var pa := CollisionPolygon2D.new()
	pa.polygon = ring[0]
	a.add_child(pa)
	builds.append(["A_contour0", a, -200.0])
	var b := StaticBody2D.new()
	for c in ring:
		if c.size() >= 3:
			var pb := CollisionPolygon2D.new()
			pb.polygon = c
			b.add_child(pb)
	builds.append(["B_both", b, 0.0])
	var c3 := StaticBody2D.new()
	for s in [_rect(-40, -40, 40, -10), _rect(-40, 10, 40, 40), _rect(-40, -10, -10, 10), _rect(10, -10, 40, 10)]:
		var pc := CollisionPolygon2D.new()
		pc.polygon = s
		c3.add_child(pc)
	builds.append(["C_slabs", c3, 200.0])
	var samples := [["centre", Vector2(0, 0)], ["top", Vector2(0, -25)], ["right", Vector2(25, 0)],
		["bottom", Vector2(0, 25)], ["left", Vector2(-25, 0)]]
	var names: PackedStringArray = []
	for i in builds.size():
		var bd: Array = builds[i]
		bd[1].position = Vector2(bd[2], 0)
		root.add_child(bd[1])
		names.append(String(bd[0]))
	for i in 2:
		await physics_frame
	var dss := root.world_2d.direct_space_state
	var out: PackedStringArray = []
	for i in builds.size():
		var bd: Array = builds[i]
		var cell: PackedStringArray = []
		for s in samples:
			var q := PhysicsPointQueryParameters2D.new()
			q.position = Vector2(bd[2], 0) + s[1]
			cell.append("%s:%d" % [s[0], dss.intersect_point(q).size()])
		out.append("%s[%s]" % [bd[0], ",".join(cell)])
	_it("hits", "[%s]" % "|".join(out))
	_it("ring", _poly2str_area(ring))
	_it("tps", "%d" % Engine.physics_ticks_per_second)
	_pass()

func _arm_polyendpoly() -> void:
	# END_POLYGON on an OPEN polyline is a measured refusal: one engine ERROR + k=0.
	var open := PackedVector2Array([Vector2(0, 0), Vector2(20, 0), Vector2(20, 20)])
	var closed := PackedVector2Array([Vector2(0, 0), Vector2(20, 0), Vector2(20, 20), Vector2(0, 20)])
	_it("open_endpolygon", _poly2str_area(Geometry2D.offset_polyline(open, 2.0, Geometry2D.JOIN_ROUND, Geometry2D.END_POLYGON)))
	_it("closed_endpolygon", _poly2str_area(Geometry2D.offset_polyline(closed, 2.0, Geometry2D.JOIN_ROUND, Geometry2D.END_POLYGON)))
	_it("closed_endjoined", _poly2str_area(Geometry2D.offset_polyline(closed, 2.0, Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_it("closed_endbutt", _poly2str_area(Geometry2D.offset_polyline(closed, 2.0, Geometry2D.JOIN_ROUND, Geometry2D.END_BUTT)))
	_pass()
