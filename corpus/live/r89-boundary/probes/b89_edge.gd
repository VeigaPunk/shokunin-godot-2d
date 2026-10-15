extends SceneTree
# r89-boundary probe — Geometry2D edge-input lattice (attack on the r89-scout pins).
# Isolation rule: exactly ONE risky sub-call per process, selected by --sub=<name>.
# A SIGABRT/hang therefore names the exact call in the driver's rc/receipt.
# Launch shape: godot --headless --path <proj> --script res://b89_edge.gd -- --sub=<name>
# Prints `R89B <sub> <key>=<value>` lines; a final `PASS b89_edge <sub> <items>` line.
# `_poly2str` / `_poly2str_area` follow the r89-scout helpers verbatim (%.4f).

var sub := ""
var _items: PackedStringArray = []

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--sub="):
			sub = a.substr(6)
	_run.call_deferred()

func _it(key: String, value: String) -> void:
	_items.append("%s=%s" % [key, value])
	print("R89B %s %s=%s" % [sub, key, value])

func _pass() -> void:
	print("PASS b89_edge %s %s" % [sub, " ".join(_items)])
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

func _sq(cx: float, cy: float, r: float) -> PackedVector2Array:
	return PackedVector2Array([Vector2(cx - r, cy - r), Vector2(cx + r, cy - r),
		Vector2(cx + r, cy + r), Vector2(cx - r, cy + r)])

func _scaled(poly: PackedVector2Array, s: float) -> PackedVector2Array:
	var out := PackedVector2Array()
	for v in poly:
		out.append(v * s)
	return out

func _nan_poly() -> PackedVector2Array:
	return PackedVector2Array([Vector2(NAN, NAN), Vector2(10, 0), Vector2(10, 10), Vector2(0, 10)])

func _nan_poly2() -> PackedVector2Array:
	return PackedVector2Array([Vector2(0, 0), Vector2(NAN, 10), Vector2(10, 10), Vector2(0, 10)])

func _inf_poly() -> PackedVector2Array:
	return PackedVector2Array([Vector2(INF, 0), Vector2(10, 0), Vector2(10, 10), Vector2(0, 10)])

func _pentagram(cx: float, cy: float, r: float) -> PackedVector2Array:
	var out := PackedVector2Array()
	for i in 5:
		var a := -PI / 2.0 + float(i) * TAU * 2.0 / 5.0
		out.append(Vector2(cx + r * cos(a), cy + r * sin(a)))
	return out

func _col3() -> PackedVector2Array:
	return PackedVector2Array([Vector2(0, 0), Vector2(1, 0), Vector2(2, 0)])

func _bow() -> PackedVector2Array:
	return PackedVector2Array([Vector2(0, 0), Vector2(10, 10), Vector2(10, 0), Vector2(0, 10)])

func _line3() -> PackedVector2Array:
	return PackedVector2Array([Vector2(0, 0), Vector2(20, 0), Vector2(20, 20)])

func _run() -> void:
	match sub:
		"sanity": _s_sanity()
		"bool_empty_empty": _s_bool_empty_empty()
		"bool_empty_left": _s_bool_empty_left()
		"bool_collinear_clip": _s_bool_collinear_clip()
		"bool_collinear_merge": _s_bool_collinear_merge()
		"bool_dup_clip": _s_bool_dup_clip()
		"bool_bow_merge": _s_bool_bow_merge()
		"bool_bow_inter": _s_bool_bow_inter()
		"bool_bow_excl": _s_bool_bow_excl()
		"bool_bow_bow": _s_bool_bow_bow()
		"bool_bow_rev": _s_bool_bow_rev()
		"bool_star5_clip": _s_bool_star5_clip()
		"bool_huge_1e6": _s_bool_huge(1e6)
		"bool_huge_1e9": _s_bool_huge(1e9)
		"bool_huge_1e10": _s_bool_huge(1e10)
		"bool_huge_1e12": _s_bool_huge(1e12)
		"bool_huge_1e15": _s_bool_huge(1e15)
		"bool_huge_1e18": _s_bool_huge(1e18)
		"bool_huge_3e38": _s_bool_huge(1.5e38)
		"bool_scale_ladder": _s_bool_scale_ladder()
		"bool_tiny_1e6": _s_bool_huge(1e-6)
		"bool_tiny_1e20": _s_bool_huge(1e-20)
		"bool_denorm": _s_bool_huge(1e-45)
		"bool_mixed_scale": _s_bool_mixed_scale()
		"bool_nan_clip": _s_bool_nan_clip()
		"bool_nan_merge": _s_bool_nan_merge()
		"bool_nan_inter": _s_bool_nan_inter()
		"bool_nan_excl": _s_bool_nan_excl()
		"bool_nan_both": _s_bool_nan_both()
		"bool_inf_clip": _s_bool_inf_clip()
		"bool_negzero": _s_bool_negzero()
		"tri_empty": _s_tri_empty()
		"tri_star5": _s_tri_star5()
		"tri_nan": _s_tri_nan()
		"tri_inf": _s_tri_inf()
		"tri_huge_1e9": _s_tri_huge()
		"tri_tiny_1e20": _s_tri_tiny()
		"tri_dup_all": _s_tri_dup_all()
		"tri_zero_area_4": _s_tri_zero_area_4()
		"tri_eps_col": _s_tri_eps_col()
		"hull_empty": _s_hull_empty()
		"hull_dup_all": _s_hull_dup_all()
		"hull_nan": _s_hull_nan()
		"hull_inf": _s_hull_inf()
		"hull_huge": _s_hull_huge()
		"hull_tiny": _s_hull_tiny()
		"hull_star5": _s_hull_star5()
		"dec_empty": _s_dec_empty()
		"dec_bow": _s_dec_bow()
		"dec_nan": _s_dec_nan()
		"dec_huge": _s_dec_huge()
		"off_nan_delta": _s_off_nan_delta()
		"off_inf_delta": _s_off_inf_delta()
		"off_neginf_delta": _s_off_neginf_delta()
		"off_huge_delta": _s_off_huge_delta()
		"off_mega_neg": _s_off_mega_neg()
		"off_nan_poly": _s_off_nan_poly()
		"off_inf_poly": _s_off_inf_poly()
		"off_huge_poly": _s_off_huge_poly()
		"off_huge_poly_miter": _s_off_huge_poly_miter()
		"off_tiny_poly": _s_off_tiny_poly()
		"off_negzero_delta": _s_off_negzero_delta()
		"off_denorm_delta": _s_off_denorm_delta()
		"off_exact_boundary": _s_off_exact_boundary()
		"off_just_beyond": _s_off_just_beyond()
		"off_delta_ladder": _s_off_delta_ladder()
		"line_1pt": _s_line_1pt()
		"line_2pt": _s_line_2pt()
		"line_2pt_dup": _s_line_2pt_dup()
		"line_col": _s_line_col()
		"line_col_rev": _s_line_col_rev()
		"line_dup4": _s_line_dup4()
		"line_nan": _s_line_nan()
		"line_inf": _s_line_inf()
		"line_huge": _s_line_huge()
		"line_tiny": _s_line_tiny()
		"line_selfint": _s_line_selfint()
		"line_star5": _s_line_star5()
		"line_delta_nan": _s_line_delta_nan()
		"line_delta_inf": _s_line_delta_inf()
		"line_delta_zero": _s_line_delta_zero()
		"line_delta_huge": _s_line_delta_huge()
		"line_closed2": _s_line_closed2()
		"line_closed3": _s_line_closed3()
		"line_rev": _s_line_rev()
		"line_empty_reverify": _s_line_empty_reverify()
		"atlas_zero": _s_atlas_zero()
		"atlas_neg": _s_atlas_neg()
		"atlas_huge": _s_atlas_huge()
		"atlas_nan": _s_atlas_nan()
		"atlas_inf": _s_atlas_inf()
		"atlas_many": _s_atlas_many()
		"atlas_zero_plus_real": _s_atlas_zero_plus_real()
		"atlas_frac": _s_atlas_frac()
		"pred_nan": _s_pred_nan()
		"pred_inf": _s_pred_inf()
		"pred_huge": _s_pred_huge()
		"pred_tiny": _s_pred_tiny()
		"isect_nan": _s_isect_nan()
		"closest_nan": _s_closest_nan()
		"bresenham_nan": _s_bresenham_nan()
		"sic_nan": _s_sic_nan()
		"sic_huge": _s_sic_huge()
		_:
			_it("unknown", "sub=%s" % sub)
			_pass()

# ---------------- sanity ----------------

func _s_sanity() -> void:
	_it("fmt_nan", "%.4f" % [NAN])
	_it("fmt_inf", "%.4f" % [INF])
	_it("fmt_neginf", "%.4f" % [-INF])
	_it("fmt_1e38", "%.4f" % [1e38])
	_it("fmt_1e-45", "%.4f" % [1e-45])
	_it("str_nan", str(NAN))
	_it("vec_nan", _v2(Vector2(NAN, 0.0)))
	_it("vec_1e38", _v2(Vector2(1e38, 0.0)))
	_it("vec_1e-45", _v2(Vector2(1e-45, 0.0)))
	_it("nan_plus", "%.4f" % [NAN + 1.0])
	_it("inf_minus_inf", "%.4f" % [INF - INF])
	_pass()

# ---------------- boolean ops ----------------

func _s_bool_empty_empty() -> void:
	var e := PackedVector2Array()
	_it("call", "clip|merge|inter|excl(empty,empty)")
	_it("clip", _poly2str(Geometry2D.clip_polygons(e, e)))
	_it("merge", _poly2str(Geometry2D.merge_polygons(e, e)))
	_it("inter", _poly2str(Geometry2D.intersect_polygons(e, e)))
	_it("excl", _poly2str(Geometry2D.exclude_polygons(e, e)))
	_pass()

func _s_bool_empty_left() -> void:
	var e := PackedVector2Array()
	var sq := _sq(0, 0, 10)
	_it("call", "clip|merge|inter|excl(empty,sq)")
	_it("clip", _poly2str(Geometry2D.clip_polygons(e, sq)))
	_it("merge", _poly2str(Geometry2D.merge_polygons(e, sq)))
	_it("inter", _poly2str(Geometry2D.intersect_polygons(e, sq)))
	_it("excl", _poly2str(Geometry2D.exclude_polygons(e, sq)))
	_pass()

func _s_bool_collinear_clip() -> void:
	var col := _col3()
	var sq := _sq(0, 0, 10)
	_it("call", "clip(col3,sq)|clip(sq,col3)")
	_it("col_sq", _poly2str(Geometry2D.clip_polygons(col, sq)))
	_it("sq_col", _poly2str(Geometry2D.clip_polygons(sq, col)))
	_pass()

func _s_bool_collinear_merge() -> void:
	var col := _col3()
	var sq := _sq(0, 0, 10)
	_it("call", "merge(col3,sq)|inter(col3,sq)|excl(col3,sq)")
	_it("merge", _poly2str(Geometry2D.merge_polygons(col, sq)))
	_it("inter", _poly2str(Geometry2D.intersect_polygons(col, sq)))
	_it("excl", _poly2str(Geometry2D.exclude_polygons(col, sq)))
	_pass()

func _s_bool_dup_clip() -> void:
	var dup := PackedVector2Array([Vector2(0, 0), Vector2(0, 0), Vector2(4, 0), Vector2(4, 0)])
	var sq := _sq(0, 0, 10)
	_it("call", "clip(dup4,sq)")
	_it("dup_sq", _poly2str(Geometry2D.clip_polygons(dup, sq)))
	_pass()

func _s_bool_bow_merge() -> void:
	var bow := _bow()
	var sq := _sq(0, 0, 10)
	_it("call", "merge(bow,sq)")
	_it("merge", _poly2str_area(Geometry2D.merge_polygons(bow, sq)))
	_pass()

func _s_bool_bow_inter() -> void:
	var bow := _bow()
	var sq := _sq(0, 0, 10)
	_it("call", "inter(bow,sq)")
	_it("inter", _poly2str_area(Geometry2D.intersect_polygons(bow, sq)))
	_pass()

func _s_bool_bow_excl() -> void:
	var bow := _bow()
	var sq := _sq(0, 0, 10)
	_it("call", "excl(bow,sq)")
	_it("excl", _poly2str_area(Geometry2D.exclude_polygons(bow, sq)))
	_pass()

func _s_bool_bow_bow() -> void:
	var bow := _bow()
	_it("call", "clip|merge|inter(bow,bow)")
	_it("clip", _poly2str(Geometry2D.clip_polygons(bow, bow)))
	_it("merge", _poly2str(Geometry2D.merge_polygons(bow, bow)))
	_it("inter", _poly2str(Geometry2D.intersect_polygons(bow, bow)))
	_pass()

func _s_bool_bow_rev() -> void:
	var bow := _bow()
	var rev := PackedVector2Array([bow[0], bow[3], bow[2], bow[1]])
	var sq := _sq(0, 0, 10)
	_it("call", "clip(reversed-bow,sq)")
	_it("rev_sq", _poly2str(Geometry2D.clip_polygons(rev, sq)))
	_pass()

func _s_bool_star5_clip() -> void:
	var star := _pentagram(5, 5, 6)
	var sq := _sq(5, 5, 3)
	_it("call", "clip(pentagram,sq)")
	_it("star", _poly2str(Geometry2D.clip_polygons(star, sq)))
	_it("star_merge", _poly2str_area(Geometry2D.merge_polygons(star, sq)))
	_pass()

func _s_bool_huge(s: float) -> void:
	var a := _sq(0, 0, s)
	var b := _sq(s * 0.5, 0, s)
	_it("call", "clip(a,b) scale=%.4f" % s)
	_it("clip", _poly2str(Geometry2D.clip_polygons(a, b)))
	_it("merge", _poly2str(Geometry2D.merge_polygons(a, b)))
	_it("inter", _poly2str(Geometry2D.intersect_polygons(a, b)))
	_pass()

func _s_bool_scale_ladder() -> void:
	_it("call", "clip/merge(sq(0,0,s), sq(0.5s,0,s)) scale ladder")
	var scales := [1.0, 0.1, 0.01, 1e-3, 1e-4, 1e-5, 1e-6]
	var labels := ["1.0", "0.1", "0.01", "1e-3", "1e-4", "1e-5", "1e-6"]
	var parts: PackedStringArray = []
	for i in scales.size():
		var s: float = scales[i]
		var a := _sq(0, 0, s)
		var b := _sq(s * 0.5, 0, s)
		parts.append("s=%s:clip=%d,merge=%d" % [labels[i], Geometry2D.clip_polygons(a, b).size(),
			Geometry2D.merge_polygons(a, b).size()])
	_it("ladder", "|".join(parts))
	_pass()

func _s_bool_mixed_scale() -> void:
	var big := _sq(0, 0, 1e9)
	var tiny := _sq(0, 0, 1e-9)
	_it("call", "clip(big1e9,tiny1e-9)")
	_it("clip", _poly2str(Geometry2D.clip_polygons(big, tiny)))
	_it("inter", _poly2str(Geometry2D.intersect_polygons(big, tiny)))
	_pass()

func _s_bool_nan_clip() -> void:
	var sq := _sq(0, 0, 10)
	_it("call", "clip(nanpoly,sq)")
	_it("result", _poly2str(Geometry2D.clip_polygons(_nan_poly(), sq)))
	_pass()

func _s_bool_nan_merge() -> void:
	var sq := _sq(0, 0, 10)
	_it("call", "merge(nanpoly,sq)")
	_it("result", _poly2str(Geometry2D.merge_polygons(_nan_poly(), sq)))
	_pass()

func _s_bool_nan_inter() -> void:
	var sq := _sq(0, 0, 10)
	_it("call", "inter(nanpoly,sq)")
	_it("result", _poly2str(Geometry2D.intersect_polygons(_nan_poly(), sq)))
	_pass()

func _s_bool_nan_excl() -> void:
	var sq := _sq(0, 0, 10)
	_it("call", "excl(nanpoly,sq)")
	_it("result", _poly2str(Geometry2D.exclude_polygons(_nan_poly(), sq)))
	_pass()

func _s_bool_nan_both() -> void:
	_it("call", "clip(nanpoly,nanpoly2)")
	_it("result", _poly2str(Geometry2D.clip_polygons(_nan_poly(), _nan_poly2())))
	_pass()

func _s_bool_inf_clip() -> void:
	var sq := _sq(0, 0, 10)
	_it("call", "clip(infpoly,sq)")
	_it("result", _poly2str(Geometry2D.clip_polygons(_inf_poly(), sq)))
	_pass()

func _s_bool_negzero() -> void:
	var nz := PackedVector2Array([Vector2(-0.0, -0.0), Vector2(10, -0.0), Vector2(10, 10), Vector2(-0.0, 10)])
	var sq := _sq(0, 0, 10)
	_it("call", "clip(negzero,sq)")
	_it("result", _poly2str(Geometry2D.clip_polygons(nz, sq)))
	_pass()

# ---------------- triangulate / hull / decompose ----------------

func _s_tri_empty() -> void:
	_it("call", "triangulate(empty)")
	_it("result", str(Geometry2D.triangulate_polygon(PackedVector2Array())))
	_pass()

func _s_tri_star5() -> void:
	var star := _pentagram(5, 5, 6)
	_it("call", "triangulate(pentagram)")
	_it("result", str(Geometry2D.triangulate_polygon(star)))
	_pass()

func _s_tri_nan() -> void:
	_it("call", "triangulate(nanpoly)")
	_it("result", str(Geometry2D.triangulate_polygon(_nan_poly())))
	_pass()

func _s_tri_inf() -> void:
	_it("call", "triangulate(infpoly)")
	_it("result", str(Geometry2D.triangulate_polygon(_inf_poly())))
	_pass()

func _s_tri_huge() -> void:
	_it("call", "triangulate(sq1e9)")
	_it("result", str(Geometry2D.triangulate_polygon(_sq(0, 0, 1e9))))
	_pass()

func _s_tri_tiny() -> void:
	_it("call", "triangulate(sq1e-20)")
	_it("result", str(Geometry2D.triangulate_polygon(_sq(0, 0, 1e-20))))
	_pass()

func _s_tri_dup_all() -> void:
	var d := PackedVector2Array([Vector2(3, 3), Vector2(3, 3), Vector2(3, 3), Vector2(3, 3)])
	_it("call", "triangulate(all-dup)")
	_it("result", str(Geometry2D.triangulate_polygon(d)))
	_pass()

func _s_tri_zero_area_4() -> void:
	var c := PackedVector2Array([Vector2(0, 0), Vector2(1, 0), Vector2(2, 0), Vector2(3, 0)])
	_it("call", "triangulate(col4)")
	_it("result", str(Geometry2D.triangulate_polygon(c)))
	_pass()

func _s_tri_eps_col() -> void:
	var c := PackedVector2Array([Vector2(0, 0), Vector2(1, 0.0000001), Vector2(2, 0)])
	_it("call", "triangulate(near-col-1e-7)")
	_it("result", str(Geometry2D.triangulate_polygon(c)))
	_pass()

func _s_hull_empty() -> void:
	_it("call", "convex_hull(empty)")
	_it("result", _poly2str([Geometry2D.convex_hull(PackedVector2Array())]))
	_pass()

func _s_hull_dup_all() -> void:
	var d := PackedVector2Array([Vector2(3, 3), Vector2(3, 3), Vector2(3, 3)])
	_it("call", "convex_hull(all-dup)")
	_it("result", _poly2str([Geometry2D.convex_hull(d)]))
	_pass()

func _s_hull_nan() -> void:
	_it("call", "convex_hull(nanpoly)")
	_it("result", _poly2str([Geometry2D.convex_hull(_nan_poly())]))
	_pass()

func _s_hull_inf() -> void:
	_it("call", "convex_hull(infpoly)")
	_it("result", _poly2str([Geometry2D.convex_hull(_inf_poly())]))
	_pass()

func _s_hull_huge() -> void:
	_it("call", "convex_hull(sq1e9)")
	_it("result", _poly2str([Geometry2D.convex_hull(_sq(0, 0, 1e9))]))
	_pass()

func _s_hull_tiny() -> void:
	_it("call", "convex_hull(sq1e-20)")
	_it("result", _poly2str([Geometry2D.convex_hull(_sq(0, 0, 1e-20))]))
	_pass()

func _s_hull_star5() -> void:
	_it("call", "convex_hull(pentagram)")
	_it("result", _poly2str([Geometry2D.convex_hull(_pentagram(5, 5, 6))]))
	_pass()

func _s_dec_empty() -> void:
	_it("call", "decompose(empty)")
	_it("result", _poly2str(Geometry2D.decompose_polygon_in_convex(PackedVector2Array())))
	_pass()

func _s_dec_bow() -> void:
	_it("call", "decompose(bowtie)")
	_it("result", _poly2str(Geometry2D.decompose_polygon_in_convex(_bow())))
	_pass()

func _s_dec_nan() -> void:
	_it("call", "decompose(nanpoly)")
	_it("result", _poly2str(Geometry2D.decompose_polygon_in_convex(_nan_poly())))
	_pass()

func _s_dec_huge() -> void:
	_it("call", "decompose(sq1e9)")
	_it("result", _poly2str(Geometry2D.decompose_polygon_in_convex(_sq(0, 0, 1e9))))
	_pass()

# ---------------- offset_polygon ----------------

func _s_off_nan_delta() -> void:
	_it("call", "offset_polygon(sq,NAN,ROUND)")
	_it("result", _poly2str(Geometry2D.offset_polygon(_sq(0, 0, 10), NAN, Geometry2D.JOIN_ROUND)))
	_pass()

func _s_off_inf_delta() -> void:
	_it("call", "offset_polygon(sq,INF,ROUND)")
	_it("result", _poly2str(Geometry2D.offset_polygon(_sq(0, 0, 10), INF, Geometry2D.JOIN_ROUND)))
	_pass()

func _s_off_neginf_delta() -> void:
	_it("call", "offset_polygon(sq,-INF,ROUND)")
	_it("result", _poly2str(Geometry2D.offset_polygon(_sq(0, 0, 10), -INF, Geometry2D.JOIN_ROUND)))
	_pass()

func _s_off_huge_delta() -> void:
	_it("call", "offset_polygon(sq,1e6,ROUND)")
	_it("result", _poly2str(Geometry2D.offset_polygon(_sq(0, 0, 10), 1e6, Geometry2D.JOIN_ROUND)))
	_pass()

func _s_off_mega_neg() -> void:
	_it("call", "offset_polygon(sq,-1e6,ROUND)")
	_it("result", _poly2str(Geometry2D.offset_polygon(_sq(0, 0, 10), -1e6, Geometry2D.JOIN_ROUND)))
	_pass()

func _s_off_nan_poly() -> void:
	_it("call", "offset_polygon(nanpoly,2,ROUND)")
	_it("result", _poly2str(Geometry2D.offset_polygon(_nan_poly(), 2.0, Geometry2D.JOIN_ROUND)))
	_pass()

func _s_off_inf_poly() -> void:
	_it("call", "offset_polygon(infpoly,2,ROUND)")
	_it("result", _poly2str(Geometry2D.offset_polygon(_inf_poly(), 2.0, Geometry2D.JOIN_ROUND)))
	_pass()

func _s_off_huge_poly() -> void:
	_it("call", "offset_polygon(sq1e6,2,ROUND)")
	_it("result", _poly2str_area(Geometry2D.offset_polygon(_sq(0, 0, 1e6), 2.0, Geometry2D.JOIN_ROUND)))
	_pass()

func _s_off_huge_poly_miter() -> void:
	_it("call", "offset_polygon(sq1e9,2,MITER)")
	_it("result", _poly2str(Geometry2D.offset_polygon(_sq(0, 0, 1e9), 2.0, Geometry2D.JOIN_MITER)))
	_pass()

func _s_off_tiny_poly() -> void:
	_it("call", "offset_polygon(sq1e-6,1e-6,ROUND)")
	_it("result", _poly2str_area(Geometry2D.offset_polygon(_sq(0, 0, 1e-6), 1e-6, Geometry2D.JOIN_ROUND)))
	_pass()

func _s_off_negzero_delta() -> void:
	_it("call", "offset_polygon(sq,-0.0,ROUND)")
	_it("result", _poly2str_area(Geometry2D.offset_polygon(_sq(0, 0, 10), -0.0, Geometry2D.JOIN_ROUND)))
	_pass()

func _s_off_denorm_delta() -> void:
	_it("call", "offset_polygon(sq,1e-45,ROUND)")
	_it("result", _poly2str(Geometry2D.offset_polygon(_sq(0, 0, 10), 1e-45, Geometry2D.JOIN_ROUND)))
	_pass()

func _s_off_exact_boundary() -> void:
	_it("call", "offset_polygon(sq,-10,ROUND)")
	_it("result", _poly2str(Geometry2D.offset_polygon(_sq(0, 0, 10), -10.0, Geometry2D.JOIN_ROUND)))
	_pass()

func _s_off_just_beyond() -> void:
	_it("call", "offset_polygon(sq,-10.0001,ROUND)")
	_it("result", _poly2str(Geometry2D.offset_polygon(_sq(0, 0, 10), -10.0001, Geometry2D.JOIN_ROUND)))
	_pass()

func _s_off_delta_ladder() -> void:
	_it("call", "offset_polygon(r=10 sq, delta, ROUND) delta ladder")
	var deltas := [1.0, 0.1, 0.01, 1e-3, 1e-4, 1e-5, 1e-6, 1e-9]
	var labels := ["1.0", "0.1", "0.01", "1e-3", "1e-4", "1e-5", "1e-6", "1e-9"]
	var parts: PackedStringArray = []
	for i in deltas.size():
		var d: float = deltas[i]
		var r := Geometry2D.offset_polygon(_sq(0, 0, 10), d, Geometry2D.JOIN_ROUND)
		var first := r[0][0] if r.size() > 0 and r[0].size() > 0 else Vector2(0, 0)
		var area := 0.0
		if r.size() > 0:
			area = absf(_area(r[0]))
		parts.append("d=%s:k=%d,first=%s,a=%.4f" % [labels[i], r.size(), _v2(first), area])
	_it("ladder", "|".join(parts))
	_pass()

# ---------------- offset_polyline (isolated; empty already a SIGABRT) ----------------

func _s_line_1pt() -> void:
	_it("call", "offset_polyline(1pt,2,ROUND,JOINED)")
	_it("result", _poly2str(Geometry2D.offset_polyline(PackedVector2Array([Vector2(1, 1)]), 2.0,
		Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_pass()

func _s_line_2pt() -> void:
	_it("call", "offset_polyline(2pt,2,ROUND,JOINED)")
	_it("result", _poly2str(Geometry2D.offset_polyline(PackedVector2Array([Vector2(0, 0), Vector2(4, 0)]), 2.0,
		Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_pass()

func _s_line_2pt_dup() -> void:
	_it("call", "offset_polyline(2dup,2,ROUND,JOINED)")
	_it("result", _poly2str(Geometry2D.offset_polyline(PackedVector2Array([Vector2(0, 0), Vector2(0, 0)]), 2.0,
		Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_pass()

func _s_line_col() -> void:
	_it("call", "offset_polyline(col3,2,ROUND,JOINED)")
	_it("result", _poly2str(Geometry2D.offset_polyline(_col3(), 2.0, Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_pass()

func _s_line_col_rev() -> void:
	var c := _col3()
	var rev := PackedVector2Array([c[2], c[1], c[0]])
	_it("call", "offset_polyline(rev-col3,2,ROUND,JOINED)")
	_it("result", _poly2str(Geometry2D.offset_polyline(rev, 2.0, Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_pass()

func _s_line_dup4() -> void:
	var d := PackedVector2Array([Vector2(0, 0), Vector2(0, 0), Vector2(4, 0), Vector2(4, 0)])
	_it("call", "offset_polyline(dup4,2,ROUND,JOINED)")
	_it("result", _poly2str(Geometry2D.offset_polyline(d, 2.0, Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_pass()

func _s_line_nan() -> void:
	var d := PackedVector2Array([Vector2(0, 0), Vector2(NAN, 0), Vector2(4, 0)])
	_it("call", "offset_polyline(nanline,2,ROUND,JOINED)")
	_it("result", _poly2str(Geometry2D.offset_polyline(d, 2.0, Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_pass()

func _s_line_inf() -> void:
	var d := PackedVector2Array([Vector2(0, 0), Vector2(INF, 0), Vector2(4, 0)])
	_it("call", "offset_polyline(infline,2,ROUND,JOINED)")
	_it("result", _poly2str(Geometry2D.offset_polyline(d, 2.0, Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_pass()

func _s_line_huge() -> void:
	_it("call", "offset_polyline(1e9-line,2,ROUND,JOINED)")
	_it("result", _poly2str(Geometry2D.offset_polyline(_scaled(_line3(), 1e9), 2.0,
		Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_pass()

func _s_line_tiny() -> void:
	_it("call", "offset_polyline(1e-6-line,2,ROUND,JOINED)")
	_it("result", _poly2str(Geometry2D.offset_polyline(_scaled(_line3(), 1e-6), 2.0,
		Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_pass()

func _s_line_selfint() -> void:
	var d := PackedVector2Array([Vector2(0, 0), Vector2(10, 10), Vector2(10, 0), Vector2(0, 10), Vector2(20, 5)])
	_it("call", "offset_polyline(selfint,2,ROUND,JOINED)")
	_it("result", _poly2str(Geometry2D.offset_polyline(d, 2.0, Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_pass()

func _s_line_star5() -> void:
	_it("call", "offset_polyline(pentagram-path,2,ROUND,JOINED)")
	_it("result", _poly2str(Geometry2D.offset_polyline(_pentagram(5, 5, 6), 2.0,
		Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_pass()

func _s_line_delta_nan() -> void:
	_it("call", "offset_polyline(line,NAN,ROUND,JOINED)")
	_it("result", _poly2str(Geometry2D.offset_polyline(_line3(), NAN, Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_pass()

func _s_line_delta_inf() -> void:
	_it("call", "offset_polyline(line,INF,ROUND,JOINED)")
	_it("result", _poly2str(Geometry2D.offset_polyline(_line3(), INF, Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_pass()

func _s_line_delta_zero() -> void:
	_it("call", "offset_polyline(line,0,ROUND,JOINED)")
	_it("result", _poly2str(Geometry2D.offset_polyline(_line3(), 0.0, Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_pass()

func _s_line_delta_huge() -> void:
	_it("call", "offset_polyline(line,1e6,ROUND,JOINED)")
	_it("result", _poly2str(Geometry2D.offset_polyline(_line3(), 1e6, Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_pass()

func _s_line_closed2() -> void:
	var d := PackedVector2Array([Vector2(0, 0), Vector2(4, 0), Vector2(0, 0)])
	_it("call", "offset_polyline(closed-2pt,2,ROUND,JOINED)")
	_it("result", _poly2str(Geometry2D.offset_polyline(d, 2.0, Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_pass()

func _s_line_closed3() -> void:
	var d := PackedVector2Array([Vector2(0, 0), Vector2(4, 0), Vector2(0, 4), Vector2(0, 0)])
	_it("call", "offset_polyline(closed-3pt,2,ROUND,JOINED)")
	_it("result", _poly2str(Geometry2D.offset_polyline(d, 2.0, Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_pass()

func _s_line_rev() -> void:
	var d := PackedVector2Array([Vector2(20, 20), Vector2(20, 0), Vector2(0, 0)])
	_it("call", "offset_polyline(rev-line,2,ROUND,JOINED)")
	_it("result", _poly2str(Geometry2D.offset_polyline(d, 2.0, Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_pass()

func _s_line_empty_reverify() -> void:
	_it("call", "offset_polyline(empty,2,ROUND,JOINED)")
	_it("result", _poly2str(Geometry2D.offset_polyline(PackedVector2Array(), 2.0,
		Geometry2D.JOIN_ROUND, Geometry2D.END_JOINED)))
	_pass()

# ---------------- make_atlas ----------------

func _s_atlas_zero() -> void:
	_it("call", "make_atlas([(0,0)])")
	_it("result", _atlas2str(Geometry2D.make_atlas(PackedVector2Array([Vector2(0, 0)]))))
	_pass()

func _s_atlas_neg() -> void:
	_it("call", "make_atlas([(-1,-1)])")
	_it("result", _atlas2str(Geometry2D.make_atlas(PackedVector2Array([Vector2(-1, -1)]))))
	_pass()

func _s_atlas_huge() -> void:
	_it("call", "make_atlas([(1e6,1e6)])")
	_it("result", _atlas2str(Geometry2D.make_atlas(PackedVector2Array([Vector2(1e6, 1e6)]))))
	_pass()

func _s_atlas_nan() -> void:
	_it("call", "make_atlas([(NAN,NAN)])")
	_it("result", _atlas2str(Geometry2D.make_atlas(PackedVector2Array([Vector2(NAN, NAN)]))))
	_pass()

func _s_atlas_inf() -> void:
	_it("call", "make_atlas([(INF,INF)])")
	_it("result", _atlas2str(Geometry2D.make_atlas(PackedVector2Array([Vector2(INF, INF)]))))
	_pass()

func _s_atlas_many() -> void:
	var v := PackedVector2Array()
	for i in 64:
		v.append(Vector2(3 + (i % 8), 3 + (i / 8)))
	_it("call", "make_atlas(64x 3px)")
	_it("result", _atlas2str(Geometry2D.make_atlas(v)))
	_pass()

func _s_atlas_zero_plus_real() -> void:
	_it("call", "make_atlas([(0,0),(4,4)])")
	_it("result", _atlas2str(Geometry2D.make_atlas(PackedVector2Array([Vector2(0, 0), Vector2(4, 4)]))))
	_pass()

func _s_atlas_frac() -> void:
	_it("call", "make_atlas([(0.5,0.5)])")
	_it("result", _atlas2str(Geometry2D.make_atlas(PackedVector2Array([Vector2(0.5, 0.5)]))))
	_pass()

# ---------------- predicates / misc ----------------

func _s_pred_nan() -> void:
	var sq := _sq(0, 0, 10)
	_it("call", "predicates(NaN)")
	_it("pip_nan_pt", str(Geometry2D.is_point_in_polygon(Vector2(NAN, NAN), sq)))
	_it("pip_nan_poly", str(Geometry2D.is_point_in_polygon(Vector2(1, 1), _nan_poly())))
	_it("pic_nan", str(Geometry2D.is_point_in_circle(Vector2(NAN, 0), Vector2(0, 0), 5.0)))
	_it("tri_nan", str(Geometry2D.point_is_inside_triangle(Vector2(NAN, NAN), Vector2(0, 0), Vector2(4, 0), Vector2(0, 4))))
	_it("cw_nan", str(Geometry2D.is_polygon_clockwise(_nan_poly())))
	_pass()

func _s_pred_inf() -> void:
	var sq := _sq(0, 0, 10)
	_it("call", "predicates(INF)")
	_it("pip_inf_pt", str(Geometry2D.is_point_in_polygon(Vector2(INF, 0), sq)))
	_it("pip_inf_poly", str(Geometry2D.is_point_in_polygon(Vector2(1, 1), _inf_poly())))
	_it("pic_inf", str(Geometry2D.is_point_in_circle(Vector2(INF, 0), Vector2(0, 0), 5.0)))
	_it("cw_inf", str(Geometry2D.is_polygon_clockwise(_inf_poly())))
	_pass()

func _s_pred_huge() -> void:
	var big := _sq(0, 0, 1e9)
	_it("call", "predicates(huge)")
	_it("pip_in", str(Geometry2D.is_point_in_polygon(Vector2(1, 1), big)))
	_it("pip_edge", str(Geometry2D.is_point_in_polygon(Vector2(1e9, 0), big)))
	_it("pic_huge_r", str(Geometry2D.is_point_in_circle(Vector2(1e9, 0), Vector2(0, 0), 1e9)))
	_pass()

func _s_pred_tiny() -> void:
	var small := _sq(0, 0, 1e-20)
	_it("call", "predicates(tiny)")
	_it("pip_in", str(Geometry2D.is_point_in_polygon(Vector2(0, 0), small)))
	_it("pip_edge", str(Geometry2D.is_point_in_polygon(Vector2(1e-20, 0), small)))
	_it("pic_tiny", str(Geometry2D.is_point_in_circle(Vector2(1e-20, 0), Vector2(0, 0), 1e-20)))
	_pass()

func _s_isect_nan() -> void:
	_it("call", "line/segment intersects (NaN)")
	_it("line", str(Geometry2D.line_intersects_line(Vector2(NAN, 0), Vector2(1, 0), Vector2(2, -1), Vector2(0, 1))))
	_it("seg", str(Geometry2D.segment_intersects_segment(Vector2(NAN, 0), Vector2(4, 0), Vector2(2, -1), Vector2(2, 1))))
	_it("seg2", str(Geometry2D.segment_intersects_segment(Vector2(0, 0), Vector2(4, 0), Vector2(NAN, -1), Vector2(2, 1))))
	_pass()

func _s_closest_nan() -> void:
	_it("call", "closest-points (NaN)")
	_it("c1", str(Geometry2D.get_closest_point_to_segment(Vector2(NAN, 0), Vector2(0, 0), Vector2(10, 0))))
	_it("c2", str(Geometry2D.get_closest_point_to_segment_uncapped(Vector2(NAN, 0), Vector2(0, 0), Vector2(10, 0))))
	_it("c3", str(Geometry2D.get_closest_points_between_segments(Vector2(NAN, 0), Vector2(10, 0), Vector2(5, -2), Vector2(5, 2))))
	_pass()

func _s_bresenham_nan() -> void:
	_it("call", "bresenham(NaN)")
	_it("b1", str(Geometry2D.bresenham_line(Vector2(NAN, NAN), Vector2(5, 3))))
	_it("b2", str(Geometry2D.bresenham_line(Vector2(0, 0), Vector2(INF, INF))))
	_pass()

func _s_sic_nan() -> void:
	_it("call", "segment_intersects_circle(NaN)")
	_it("n1", "%.4f" % Geometry2D.segment_intersects_circle(Vector2(NAN, 0), Vector2(10, 0), Vector2(0, 0), 5.0))
	_it("n2", "%.4f" % Geometry2D.segment_intersects_circle(Vector2(-10, 0), Vector2(10, 0), Vector2(NAN, 0), 5.0))
	_it("n3", "%.4f" % Geometry2D.segment_intersects_circle(Vector2(-10, 0), Vector2(10, 0), Vector2(0, 0), NAN))
	_pass()

func _s_sic_huge() -> void:
	_it("call", "segment_intersects_circle(huge)")
	_it("h1", "%.4f" % Geometry2D.segment_intersects_circle(Vector2(-1e9, 0), Vector2(1e9, 0), Vector2(0, 0), 5.0))
	_it("h2", "%.4f" % Geometry2D.segment_intersects_circle(Vector2(-1e9, 0), Vector2(1e9, 0), Vector2(0, 0), 1e9))
	_it("h3", "%.4f" % Geometry2D.segment_intersects_circle(Vector2(-1e-20, 0), Vector2(1e-20, 0), Vector2(0, 0), 1e-20))
	_pass()
