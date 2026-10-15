extends SceneTree
# r91b agent fin/reached split diagnostic.
# The r91-scout probe reports `reached_at=-1` (fin true, reached false in the same
# readback) while the r91b instrumented lane reports split=0. This probe isolates which
# probe-code detail produces the split: pre-walk readbacks (get_current_navigation_path_index),
# the extra is_navigation_finished() call after the await, and read order.
#
# Launch: godot --headless --path proj --script res://r91b_agent_diag.gd -- --arm=<v1..v6>
# v1: scout-exact (full pre-reads incl. s_idx; only is_target_reached() after await)
# v2: v1 + is_navigation_finished() after await, reached read first
# v3: scout-exact minus the s_idx pre-read
# v4: scout-exact minus ALL pre-reads except distance/plen (r91b_nav pre-reads)
# v5: v4 + is_navigation_finished() after await, fin read first (exact r91b_nav semantics)
# v6: full pre-reads + fin after await, fin read first

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

func _await_frames(n: int) -> void:
	for i in range(n):
		await physics_frame

func _initialize() -> void:
	var arm := _arg("arm", "v1")
	match arm:
		"v1": await _run("full", false, "reached_only")
		"v2": await _run("full", true, "reached_first")
		"v3": await _run("no_idx", false, "reached_only")
		"v4": await _run("min", false, "reached_only")
		"v5": await _run("min", true, "fin_first")
		"v6": await _run("full", true, "fin_first")
		"v7": await _run("min", true, "double_reached")
		"v8": await _run("min", true, "double_fin")
		"v9": await _run("min", true, "triple")
		"bent": await _run_bent()
		_:
			print("PASS r91b_agent_diag unknown arm=", arm)
	quit(0)

func _run(pre_reads: String, fin_after: bool, order: String) -> void:
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
	for i in range(60):
		await physics_frame
		if ag.is_target_reachable():
			first_reachable = i + 1
			break
	await _await_frames(2)
	var s_next := ""
	var s_fin := false
	var s_reachable := false
	var s_reached := false
	var s_idx := -1
	if pre_reads == "full":
		s_next = _v(ag.get_next_path_position())
		s_fin = ag.is_navigation_finished()
		s_reachable = ag.is_target_reachable()
		s_reached = ag.is_target_reached()
		var _d := ag.distance_to_target()
		var _p := ag.get_path_length()
		s_idx = ag.get_current_navigation_path_index()
	elif pre_reads == "no_idx":
		s_next = _v(ag.get_next_path_position())
		s_fin = ag.is_navigation_finished()
		s_reachable = ag.is_target_reachable()
		s_reached = ag.is_target_reached()
		var _d2 := ag.distance_to_target()
		var _p2 := ag.get_path_length()
	else:
		var _d3 := ag.distance_to_target()
		var _p3 := ag.get_path_length()
	var steps := 0
	var reached_at := -1
	var fin_at := -1
	var fin_same_frame := false
	var probe_note := ""
	while steps < 80 and not ag.is_navigation_finished():
		var next := ag.get_next_path_position()
		holder.position = holder.position.move_toward(next, 8.0)
		steps += 1
		await physics_frame
		if order == "reached_only":
			if reached_at < 0 and ag.is_target_reached():
				reached_at = steps
		elif order == "reached_first":
			var rch := ag.is_target_reached()
			var fin := ag.is_navigation_finished()
			if reached_at < 0 and rch:
				reached_at = steps
			if fin_at < 0 and fin:
				fin_at = steps
				fin_same_frame = rch
		elif order == "double_reached":
			# is_target_reached() twice in a row (no other call between)
			var r1 := ag.is_target_reached()
			var r2 := ag.is_target_reached()
			var f1 := ag.is_navigation_finished()
			if r1 != r2:
				probe_note = "reached_r1=%s r2=%s at step %d" % [r1, r2, steps]
			if reached_at < 0 and r1:
				reached_at = steps
			if fin_at < 0 and f1:
				fin_at = steps
				fin_same_frame = r1
		elif order == "double_fin":
			# is_navigation_finished() twice in a row, then is_target_reached()
			var f1b := ag.is_navigation_finished()
			var f2b := ag.is_navigation_finished()
			var r2b := ag.is_target_reached()
			if f1b != f2b:
				probe_note = "fin_f1=%s f2=%s at step %d" % [f1b, f2b, steps]
			if fin_at < 0 and f1b:
				fin_at = steps
				fin_same_frame = r2b
			if reached_at < 0 and r2b:
				reached_at = steps
		elif order == "triple":
			# reached -> fin -> reached in one frame: the cleanest staleness proof
			var r1c := ag.is_target_reached()
			var fc := ag.is_navigation_finished()
			var r2c := ag.is_target_reached()
			if r1c != r2c or (fc and r1c != r2c):
				probe_note = "step=%d r1=%s fin=%s r2=%s" % [steps, r1c, fc, r2c]
			if fin_at < 0 and fc:
				fin_at = steps
				fin_same_frame = r1c
			if reached_at < 0 and r1c:
				reached_at = steps
		else:
			var fin2 := ag.is_navigation_finished()
			var rch2 := ag.is_target_reached()
			if fin_at < 0 and fin2:
				fin_at = steps
				fin_same_frame = rch2
			if reached_at < 0 and rch2:
				reached_at = steps
	var post_fin := ag.is_navigation_finished()
	var post_reached := ag.is_target_reached()
	if fin_at < 0 and post_fin:
		fin_at = steps
	print("PASS r91b_agent_diag arm=", _arg("arm"),
		" pre=", pre_reads, " fin_after=", fin_after, " order=", order,
		" first_reachable=", first_reachable,
		" walk_steps=", steps,
		" reached_at=", reached_at, " fin_at=", fin_at,
		" fin_same_frame=", fin_same_frame,
		" post_fin=", post_fin, " post_reached=", post_reached,
		" s_fin=", s_fin, " s_reachable=", s_reachable, " s_reached=", s_reached,
		" s_idx=", s_idx, " final_pos=", _v(holder.position),
		" note=", probe_note)
	root.queue_free()
	await physics_frame

# Discriminating distance_to_target() vs get_path_length() lane: an L-shaped navmesh
# (two node regions) where the straight line (226.27) and the path (282.84) differ.
func _run_bent() -> void:
	var root := Node2D.new()
	get_root().add_child(root)
	var reg1 := NavigationRegion2D.new()
	reg1.navigation_polygon = _quad_poly(0, 0, 40, 200)
	root.add_child(reg1)
	var reg2 := NavigationRegion2D.new()
	reg2.navigation_polygon = _quad_poly(40, 0, 200, 40)
	root.add_child(reg2)
	var holder := Node2D.new()
	holder.position = Vector2(20, 180)
	root.add_child(holder)
	var ag := NavigationAgent2D.new()
	ag.path_desired_distance = 4.0
	ag.target_desired_distance = 8.0
	holder.add_child(ag)
	ag.target_position = Vector2(180, 20)
	var first_reachable := -1
	for i in range(60):
		await physics_frame
		if ag.is_target_reachable():
			first_reachable = i + 1
			break
	await _await_frames(2)
	var dist := ag.distance_to_target()
	var plen := ag.get_path_length()
	var path := ag.get_current_navigation_path()
	print("PASS r91b_agent_diag arm=bent first_reachable=", first_reachable,
		" dist=%.4f" % dist, " plen=%.4f" % plen,
		" delta=%.4f" % (plen - dist),
		" path=", _path(path),
		" dist_eq_straight=", absf(dist - 226.2742) < 0.01,
		" plen_eq_L=", absf(plen - 282.8427) < 0.01)
	root.queue_free()
	await physics_frame
