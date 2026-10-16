extends SceneTree
# r95b BOUNDARY attack probe — the r95 scout's multi-hit ordering claims under
# quiet / >=12-hog load / --fixed-fps / unstated modes.
#
# Battery launch shape:
#   godot --headless [--fixed-fps N] --path proj --script res://r95b_order.gd -- --arm=<name> [--k=..]
#
# Each arm isolates ONE confound in the scout's ordering evidence:
#   canon   : canonical 5-body pile; dense physics-tick ladder t0..t64 (is the
#             order a stable read across ticks? the scout only ever sampled t2);
#             interleaved point/shape/point queries (does a query mutate state?).
#   perm    : FIXED tag->position map, permuted CREATION order.  The scout's
#             `--rev` variants only RELABEL bodies (positions are index-based),
#             so their "insertion-order dependent" evidence is confounded.
#   warm    : K bodies created far away BEFORE the pile; --keep=0 frees them
#             first (RID/object-id allocation history), --keep=1 keeps them.
#   free    : free one body (--which=a) or two in a given order (--order=ab) ->
#             free-order permutations for the SAME final set.
#   readd   : free a body, re-add a fresh body at its position (id reuse).
#   cap40   : 40-body pile, permuted creation order -> is the sorted SET of the
#             32 returned hits invariant above the default cap, and is it stable
#             across ticks?
#   layers  : pile + one CanvasLayer body at the same spot -> do point and shape
#             queries still share the order?  Does an invisible-to-the-query
#             collider perturb the default-layer vector / its drift path?
#   celloff : pile translated by --off -> order translation-invariance.
#   rigid   : rigid pile -> solver determinism fingerprint (positions per tick).
#   procwait: await PROCESS frames (not physics ticks) -> scheduler-sensitivity
#             of the vector under --fixed-fps.
#   env     : mode facts (tps, separate-thread setting, frame accounting).
#
# Prints one `PASS r95b_order <arm> k=v ...` line (ordering keys only) plus
# `R95B <arm> k=v` diagnostics (instance ids, engine counters) that are NOT part
# of the authorable signature.
#
# `ladder` keys are POSITION permutations ("t2:4,0,2,3,1") so they are
# comparable across label permutations (the scout's confound).

const CAP := 32
const TAGS5 := ["a", "b", "c", "d", "e"]
const TAG_X := {"a": 0.0, "b": 8.0, "c": 16.0, "d": 24.0, "e": 32.0}

var arm := ""
var opt := {}
var _items: PackedStringArray = []

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
		elif a.begins_with("--"):
			var kv := a.substr(2).split("=", true, 1)
			opt[kv[0]] = kv[1] if kv.size() > 1 else "1"
	_run.call_deferred()

func _run() -> void:
	match arm:
		"canon": await _arm_canon()
		"perm": await _arm_perm()
		"warm": await _arm_warm()
		"free": await _arm_free()
		"readd": await _arm_readd()
		"cap40": await _arm_cap40()
		"layers": await _arm_layers()
		"celloff": await _arm_celloff()
		"rigid": await _arm_rigid()
		"procwait": await _arm_procwait()
		"period": await _arm_period()
		"periodx": await _arm_periodx()
		"twopiles": await _arm_twopiles()
		"scoutrev": await _arm_scoutrev()
		"env": await _arm_env()
		_: _fail("unknown_arm")

# --------------------------------------------------------------- utilities

func _fail(reason: String) -> void:
	print("FAIL r95b_order %s reason=%s" % [arm, reason])
	quit(1)

func _opt_str(k: String, d: String) -> String:
	return str(opt.get(k, d))

func _opt_int(k: String, d: int) -> int:
	return int(opt.get(k, d))

func _opt_float(k: String, d: float) -> float:
	return float(opt.get(k, d))

func _it(key: String, value: String) -> void:
	_items.append("%s=%s" % [key, value])
	print("R95B %s %s=%s" % [arm, key, value])

func _diag(key: String, value: String) -> void:
	print("R95B %s %s=%s" % [arm, key, value])

func _pass() -> void:
	print("PASS r95b_order %s %s" % [arm, " ".join(_items)])
	quit()

func _frames(n: int) -> void:
	for i in n:
		await physics_frame

func _dss() -> PhysicsDirectSpaceState2D:
	return PhysicsServer2D.space_get_direct_state(root.world_2d.space)

func _envstr() -> String:
	return "tps=%d pf=%d proc=%d sep2d_has=%s sep2d=%s maxsteps=%s" % [
		Engine.physics_ticks_per_second, Engine.get_physics_frames(),
		Engine.get_process_frames(),
		str(ProjectSettings.has_setting("physics/2d/run_on_separate_thread")),
		str(ProjectSettings.get_setting("physics/2d/run_on_separate_thread", "absent")),
		str(ProjectSettings.get_setting("physics/common/max_physics_steps_per_frame", "absent"))]

func _tag(d: Dictionary) -> String:
	var c: Object = d.get("collider")
	if c == null:
		if d.has("collider_id"):
			c = instance_from_id(int(d.get("collider_id")))
		if c == null:
			return "?"
	return str(c.get_meta("tag", c.get_class()))

func _vec(arr: Array) -> String:
	var parts: PackedStringArray = []
	for d in arr:
		parts.append("%s#%s" % [_tag(d), str(d.get("shape", "-"))])
	return "[%s]" % ",".join(parts)

# position permutation: comparable across label permutations
func _pidx(arr: Array) -> String:
	var parts: PackedStringArray = []
	for d in arr:
		var t := _tag(d)
		parts.append(str(TAGS5.find(t)) if t in TAGS5 else t)
	return ",".join(parts)

func _relpos(arr: Array, ox: float) -> String:
	var parts: PackedStringArray = []
	for d in arr:
		var c = d.get("collider")
		var n2 := c as Node2D
		if n2 == null:
			parts.append("?")
			continue
		var p := n2.global_position
		parts.append("%.4f,%.4f" % [p.x - ox, p.y])
	return "[%s]" % "|".join(parts)

func _sorted(a: Array) -> Array:
	var c := a.duplicate()
	c.sort()
	return c

func _setstr(arr: Array) -> String:
	var keys: Array = []
	for d in arr:
		var k := "%s#%s" % [_tag(d), str(d.get("shape", "-"))]
		if k not in keys:
			keys.append(k)
	return "[%s]" % ",".join(_sorted(keys))

func _uniq_count(a: Array) -> int:
	var u: Array = []
	for v in a:
		if v not in u:
			u.append(v)
	return u.size()

func _last_change(ticks: Array, seq: Array) -> int:
	var lc := -1
	for i in seq.size():
		if i > 0 and seq[i] != seq[i - 1]:
			lc = int(ticks[i])
	return lc

func _ladderstr(ticks: Array, seq: Array) -> String:
	var parts: PackedStringArray = []
	for i in seq.size():
		parts.append("t%d:%s" % [int(ticks[i]), str(seq[i])])
	return "[%s]" % ";".join(parts)

# Query the pile point across a tick ladder; returns the pidx sequence plus the
# full first/last samples (captured in-frame, so no mislabeling).
func _ladder(ticks: Array, ox: float) -> Dictionary:
	var dss := _dss()
	var q := Vector2(16.0 + ox, 0.0)
	var seq: Array = []
	var cur := 0
	var first_vec := ""
	var first_relpos := ""
	var first_set := ""
	var first_sh := ""
	for t in ticks:
		while cur < int(t):
			await physics_frame
			cur += 1
		var r := dss.intersect_point(_pt(q), CAP)
		seq.append(_pidx(r))
		if first_vec == "":
			first_vec = _vec(r)
			first_relpos = _relpos(r, ox)
			first_set = _setstr(r)
			first_sh = _vec(dss.intersect_shape(_sh(_rect(Vector2(60, 60)), Transform2D(0, q)), CAP))
	var last := dss.intersect_point(_pt(q), CAP)
	return {"seq": seq, "first_vec": first_vec, "first_relpos": first_relpos,
		"first_set": first_set, "first_sh": first_sh, "last_vec": _vec(last),
		"last_relpos": _relpos(last, ox), "last_set": _setstr(last)}

# smallest p>0 with seq[i]==seq[i-p] over the dense prefix (ticks<=30); -1 if none
func _cycle_len(ticks: Array, seq: Array) -> int:
	var dense := 0
	while dense < ticks.size() and int(ticks[dense]) <= 30:
		dense += 1
	for p in range(1, 41):
		var ok := true
		for i in range(p, dense):
			if seq[i] != seq[i - p]:
				ok = false
				break
		if ok:
			return p
	return -1

func _mk_body_node(tag: String, pos: Vector2, size: Vector2, cls: String = "static") -> CollisionObject2D:
	var b: CollisionObject2D
	match cls:
		"rigid": b = RigidBody2D.new()
		"char": b = CharacterBody2D.new()
		"area": b = Area2D.new()
		_: b = StaticBody2D.new()
	b.name = tag
	b.set_meta("tag", tag)
	var cs := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = size
	cs.shape = rs
	b.add_child(cs)
	b.position = pos
	return b

func _mk_body(tag: String, pos: Vector2, size: Vector2, cls: String = "static") -> CollisionObject2D:
	var b := _mk_body_node(tag, pos, size, cls)
	root.add_child(b)
	return b

# tag -> fixed x (tags a..e; suffixed variants like a2 fall back to their base)
func _tagx(t: String) -> float:
	if TAG_X.has(t):
		return float(TAG_X[t])
	return float(TAG_X.get(t.substr(0, 1), 0.0))

# The pile: FIXED tag->position map; `order` is the CREATION order.
func _pile(order: Array, ox: float, oy: float, cls: String = "static") -> Array:
	var made: Array = []
	for t in order:
		made.append(_mk_body(str(t), Vector2(_tagx(str(t)) + ox, oy), Vector2(40, 40), cls))
	return made

func _pt(pos: Vector2, canvas_id := 0) -> PhysicsPointQueryParameters2D:
	var q := PhysicsPointQueryParameters2D.new()
	q.position = pos
	if canvas_id != 0:
		q.canvas_instance_id = canvas_id
	return q

func _sh(shape: Shape2D, xform: Transform2D) -> PhysicsShapeQueryParameters2D:
	var q := PhysicsShapeQueryParameters2D.new()
	q.shape = shape
	q.transform = xform
	return q

func _rect(size: Vector2) -> RectangleShape2D:
	var r := RectangleShape2D.new()
	r.size = size
	return r

func _q() -> Vector2:
	return Vector2(16, 0)

# --------------------------------------------------------------- canon

func _arm_canon() -> void:
	var made := _pile(["a", "b", "c", "d", "e"], 0.0, 0.0)
	_it("add_order", "[a,b,c,d,e]")
	_it("map", "[a@0,b@8,c@16,d@24,e@32]")
	var dss := _dss()
	var ticks := [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 32, 36, 40, 48, 56, 64]
	var seq: Array = []
	var cur := 0
	var vec2 := ""
	var relpos2 := ""
	var sh2 := ""
	var vec_end := ""
	for t in ticks:
		while cur < int(t):
			await physics_frame
			cur += 1
		var r := dss.intersect_point(_pt(_q()), CAP)
		seq.append(_pidx(r))
		if int(t) == 2:
			vec2 = _vec(r)
			relpos2 = _relpos(r, 0.0)
			sh2 = _vec(dss.intersect_shape(_sh(_rect(Vector2(60, 60)), Transform2D(0, _q())), CAP))
		if int(t) == 64:
			vec_end = _vec(r)
	_it("ladder", _ladderstr(ticks, seq))
	_it("distinct_ticks", str(_uniq_count(seq)))
	_it("last_change_tick", str(_last_change(ticks, seq)))
	_it("cycle_len_dense", str(_cycle_len(ticks, seq)))
	_it("t0_pidx", str(seq[0]))
	_it("t2_vec", vec2)
	_it("t2_relpos", relpos2)
	_it("t2_sh_vec", sh2)
	_it("t2_pt_eq_sh", str(vec2 == sh2))
	_it("t64_vec", vec_end)
	# interleaved queries at the final tick: does a shape/point query mutate state?
	var p1 := _vec(dss.intersect_point(_pt(_q()), CAP))
	var shq := _sh(_rect(Vector2(60, 60)), Transform2D(0, _q()))
	var sh := _vec(dss.intersect_shape(shq, CAP))
	var p2 := _vec(dss.intersect_point(_pt(_q()), CAP))
	var p3 := _vec(dss.intersect_point(_pt(_q()), CAP))
	_it("end_sh_vec", sh)
	_it("end_pt_eq_sh", str(p1 == sh))
	_it("pt_stable_interleaved", str(p1 == p2 and p2 == p3))
	var ids: PackedStringArray = []
	for b in made:
		ids.append(str(b.get_instance_id()))
	_diag("ids", "[%s]" % ",".join(ids))
	_diag("env", _envstr())
	_pass()

# --------------------------------------------------------------- perm

func _arm_perm() -> void:
	var perms := [
		[0, 1, 2, 3, 4], [4, 3, 2, 1, 0], [1, 2, 0, 4, 3], [2, 0, 4, 3, 1],
		[0, 2, 1, 4, 3], [3, 0, 1, 4, 2], [4, 0, 2, 3, 1], [1, 0, 3, 2, 4],
	]
	var p := _opt_int("perm", 0)
	var idx: Array = perms[p % perms.size()]
	var order: Array = []
	for i in idx:
		order.append(TAGS5[i])
	var made := _pile(order, 0.0, 0.0)
	_it("perm", str(p))
	_it("add_order", "[%s]" % ",".join(order))
	_it("map", "[a@0,b@8,c@16,d@24,e@32]")
	var ticks := [0, 1, 2, 3, 4, 5, 8, 16, 32]
	var seq: Array = []
	var cur := 0
	var dss := _dss()
	var vec2 := ""
	var relpos2 := ""
	for t in ticks:
		while cur < int(t):
			await physics_frame
			cur += 1
		var r := dss.intersect_point(_pt(_q()), CAP)
		seq.append(_pidx(r))
		if int(t) == 2:
			vec2 = _vec(r)
			relpos2 = _relpos(r, 0.0)
	_it("ladder", _ladderstr(ticks, seq))
	_it("distinct_ticks", str(_uniq_count(seq)))
	_it("last_change_tick", str(_last_change(ticks, seq)))
	_it("t2_vec", vec2)
	_it("t2_relpos", relpos2)
	var ids: PackedStringArray = []
	for b in made:
		ids.append(str(b.get_instance_id()))
	_diag("ids", "[%s]" % ",".join(ids))
	_diag("env", _envstr())
	_pass()

# --------------------------------------------------------------- warm

func _arm_warm() -> void:
	var k := _opt_int("k", 0)
	var keep := _opt_int("keep", 0)
	var warm: Array = []
	for i in k:
		var x := 10000.0 + float(i % 16) * 64.0
		var y := 10000.0 + float(i / 16) * 64.0
		warm.append(_mk_body("w%d" % i, Vector2(x, y), Vector2(16, 16)))
	await physics_frame
	if keep == 0:
		for w in warm:
			w.queue_free()
		await _frames(2)
	var made := _pile(["a", "b", "c", "d", "e"], 0.0, 0.0)
	_it("k", str(k))
	_it("keep", str(keep))
	_it("add_order", "[a,b,c,d,e]")
	var ticks := [2, 3, 4, 6, 8, 16, 32]
	var lad := await _ladder(ticks, 0.0)
	_it("ladder", _ladderstr(ticks, lad["seq"]))
	_it("distinct_ticks", str(_uniq_count(lad["seq"])))
	_it("t2_vec", lad["first_vec"])
	_it("t2_relpos", lad["first_relpos"])
	_it("t32_vec", lad["last_vec"])
	var ids: PackedStringArray = []
	for b in made:
		ids.append(str(b.get_instance_id()))
	_diag("ids", "[%s]" % ",".join(ids))
	_diag("env", _envstr())
	_pass()

# --------------------------------------------------------------- free

func _arm_free() -> void:
	var made := _pile(["a", "b", "c", "d", "e"], 0.0, 0.0)
	await _frames(2)
	var dss := _dss()
	var by_tag := {}
	for b in made:
		by_tag[str(b.get_meta("tag"))] = b
	var which := _opt_str("which", "")
	var order := _opt_str("order", "")
	var freed: Array = []
	if which != "":
		by_tag[which].queue_free()
		freed.append(which)
		await _frames(2)
	elif order != "":
		for i in order.length():
			var t := order.substr(i, 1)
			by_tag[t].queue_free()
			freed.append(t)
			await physics_frame
		await physics_frame
	else:
		_fail("free_needs_which_or_order")
		return
	_it("freed", "[%s]" % ",".join(freed))
	_it("add_order", "[a,b,c,d,e]")
	var ticks := [1, 2, 3, 4, 6, 8, 16]
	var lad := await _ladder(ticks, 0.0)
	_it("ladder", _ladderstr(ticks, lad["seq"]))
	_it("distinct_ticks", str(_uniq_count(lad["seq"])))
	_it("last_change_tick", str(_last_change(ticks, lad["seq"])))
	_it("t1_vec", lad["first_vec"])
	_it("t1_relpos", lad["first_relpos"])
	_it("t16_vec", lad["last_vec"])
	_it("set", lad["last_set"])
	_diag("env", _envstr())
	_pass()

# --------------------------------------------------------------- readd

func _arm_readd() -> void:
	var made := _pile(["a", "b", "c", "d", "e"], 0.0, 0.0)
	await _frames(2)
	var dss := _dss()
	var by_tag := {}
	for b in made:
		by_tag[str(b.get_meta("tag"))] = b
	var which := _opt_str("which", "a")
	by_tag[which].queue_free()
	await _frames(2)
	var fresh := _mk_body("f", Vector2(float(TAG_X[which]), 0.0), Vector2(40, 40))
	_it("which", which)
	_it("add_order", "[a,b,c,d,e]")
	var ticks := [1, 2, 3, 4, 6, 8, 16]
	var lad := await _ladder(ticks, 0.0)
	_it("ladder", _ladderstr(ticks, lad["seq"]))
	_it("distinct_ticks", str(_uniq_count(lad["seq"])))
	_it("t1_vec", lad["first_vec"])
	_it("t1_relpos", lad["first_relpos"])
	_it("t16_vec", lad["last_vec"])
	_it("set", lad["last_set"])
	_diag("fresh_id", str(fresh.get_instance_id()))
	_diag("env", _envstr())
	_pass()

# --------------------------------------------------------------- cap40

func _arm_cap40() -> void:
	var p := _opt_int("perm", 0)
	var idx: Array = []
	if p == 0:
		for i in 40:
			idx.append(i)
	elif p == 1:
		for i in 40:
			idx.append(39 - i)
	else:
		for i in 40:
			idx.append((i * 7 + 3) % 40)
	var order: PackedStringArray = []
	for i in idx:
		order.append("t%d" % i)
	for i in idx:
		_mk_body("t%d" % i, Vector2(1000.0 + float(i) * 2.0, 0.0), Vector2(200, 40))
	_it("perm", str(p))
	_it("add_order_head", "[%s]" % ",".join(order.slice(0, 8)))
	var dss := _dss()
	var q := Vector2(1000, 0)
	var ticks := [2, 4, 8, 16, 32]
	var sets: Array = []
	var cur := 0
	var r32_end: Array = []
	for t in ticks:
		while cur < int(t):
			await physics_frame
			cur += 1
		var r := dss.intersect_point(_pt(q), CAP)
		sets.append(_setstr(r))
		if int(t) == 32:
			r32_end = r
	var r64 := dss.intersect_point(_pt(q), 64)
	_it("set32_ladder", _ladderstr(ticks, sets))
	_it("set32_distinct", str(_uniq_count(sets)))
	_it("set32_t2", str(sets[0]))
	_it("n32", str(r32_end.size()))
	_it("n64", str(r64.size()))
	_it("n0", str(dss.intersect_point(_pt(q), 0).size()))
	_it("set32_t32", _setstr(r32_end))
	_it("relpos32_t32", _relpos(r32_end, 1000.0))
	_it("set64", _setstr(r64))
	_it("relpos64_head", _relpos(r64.slice(0, 8), 1000.0))
	_diag("env", _envstr())
	_pass()

# --------------------------------------------------------------- layers

func _arm_layers() -> void:
	var k := _opt_int("k", 0)
	var made := _pile(["a", "b", "c", "d", "e"], 0.0, 0.0)
	var cl_id := 0
	if k == 1:
		var cl := CanvasLayer.new()
		cl.name = "cl"
		root.add_child(cl)
		var clb := _mk_body_node("clb", Vector2(16, 0), Vector2(40, 40))
		cl.add_child(clb)
		cl_id = cl.get_instance_id()
	_it("k", str(k))
	_it("add_order", "[a,b,c,d,e]")
	var ticks := [2, 3, 4, 6, 8, 16, 32]
	var lad := await _ladder(ticks, 0.0)
	_it("pt0_ladder", _ladderstr(ticks, lad["seq"]))
	_it("pt0_distinct", str(_uniq_count(lad["seq"])))
	var dss := _dss()
	var pt0 := dss.intersect_point(_pt(_q()), CAP)
	var ptL := dss.intersect_point(_pt(_q(), cl_id), CAP)
	var shq := _sh(_rect(Vector2(60, 60)), Transform2D(0, _q()))
	var sh := dss.intersect_shape(shq, CAP)
	_it("pt0_vec", _vec(pt0))
	_it("pt0_relpos", _relpos(pt0, 0.0))
	_it("pt0_t2_vec", lad["first_vec"])
	_it("pt0_t2_relpos", lad["first_relpos"])
	_it("pt0_t2_eq_sh", str(lad["first_vec"] == lad["first_sh"]))
	_it("ptL_vec", _vec(ptL))
	_it("sh_vec", _vec(sh))
	_it("sh_relpos", _relpos(sh, 0.0))
	_it("pt_eq_sh", str(_vec(pt0) == _vec(sh)))
	_it("sh_len", str(sh.size()))
	_diag("env", _envstr())
	_pass()

# --------------------------------------------------------------- celloff

func _arm_celloff() -> void:
	var off := _opt_float("off", 0.0)
	var made := _pile(["a", "b", "c", "d", "e"], off, 0.0)
	_it("off", "%.4f" % off)
	_it("add_order", "[a,b,c,d,e]")
	var ticks := [2, 3, 4, 6, 8, 16, 32, 64]
	var lad := await _ladder(ticks, off)
	_it("ladder", _ladderstr(ticks, lad["seq"]))
	_it("distinct_ticks", str(_uniq_count(lad["seq"])))
	_it("last_change_tick", str(_last_change(ticks, lad["seq"])))
	_it("t2_vec", lad["first_vec"])
	_it("t2_relpos", lad["first_relpos"])
	_it("t64_relpos", lad["last_relpos"])
	_diag("env", _envstr())
	_pass()

# --------------------------------------------------------------- rigid

func _arm_rigid() -> void:
	var made := _pile(["a", "b", "c", "d", "e"], 0.0, 0.0, "rigid")
	_it("add_order", "[a,b,c,d,e]")
	var dss := _dss()
	var ticks := [1, 2, 3, 5, 10]
	var seq: Array = []
	var cur := 0
	for t in ticks:
		while cur < int(t):
			await physics_frame
			cur += 1
		seq.append(_pidx(dss.intersect_point(_pt(_q()), CAP)))
		var bp: PackedStringArray = []
		for b in made:
			var n2 := b as Node2D
			bp.append("%.4f,%.4f" % [n2.global_position.x, n2.global_position.y])
		_diag("t%d_bodypos" % int(t), "[%s]" % "|".join(bp))
	_it("ladder", _ladderstr(ticks, seq))
	_it("distinct_ticks", str(_uniq_count(seq)))
	_it("t10_relpos", _relpos(dss.intersect_point(_pt(_q()), CAP), 0.0))
	_diag("env", _envstr())
	_pass()

# --------------------------------------------------------------- procwait

func _arm_procwait() -> void:
	var made := _pile(["a", "b", "c", "d", "e"], 0.0, 0.0)
	_it("add_order", "[a,b,c,d,e]")
	var dss := _dss()
	var pf0 := Engine.get_physics_frames()
	var pr0 := Engine.get_process_frames()
	var pf_deltas: PackedStringArray = []
	var seq: Array = []
	for i in 4:
		await process_frame
		pf_deltas.append(str(Engine.get_physics_frames() - pf0))
		seq.append(_pidx(dss.intersect_point(_pt(_q()), CAP)))
	_it("pf_per_procawait", "[%s]" % ",".join(pf_deltas))
	_it("proc_delta", str(Engine.get_process_frames() - pr0))
	_it("ladder_procawait", _ladderstr([1, 2, 3, 4], seq))
	_it("distinct", str(_uniq_count(seq)))
	_it("t2_vec", _vec(dss.intersect_point(_pt(_q()), CAP)))
	_diag("env", _envstr())
	_pass()

# --------------------------------------------------------------- periodx

# Extended period scan: N ticks = k(k-1)+3, p search up to k(k-1).
func _arm_periodx() -> void:
	var k := _opt_int("k", 5)
	var sp := _opt_float("spacing", 4.0)
	for i in k:
		var x := 16.0 + (float(i) - float(k - 1) / 2.0) * sp
		_mk_body("p%d" % i, Vector2(x, 0.0), Vector2(40, 40))
	_it("k", str(k))
	_it("spacing", "%.1f" % sp)
	var dss := _dss()
	var nticks := k * (k - 1) + 3
	var seq: Array = []
	for t in nticks:
		if t > 0:
			await physics_frame
		seq.append(_vec(dss.intersect_point(_pt(_q()), CAP)))
	var p_found := -1
	for p in range(1, k * (k - 1) + 1):
		var ok := true
		for i in range(p, seq.size()):
			if seq[i] != seq[i - p]:
				ok = false
				break
		if ok:
			p_found = p
			break
	_it("cycle_len", str(p_found))
	_it("expected_kk1", str(k * (k - 1)))
	_it("distinct_ticks", str(_uniq_count(seq)))
	_it("n_ticks", str(nticks))
	_it("t0_vec", str(seq[0]))
	_it("t2_vec", str(seq[2]))
	_it("t3_vec", str(seq[3]))
	_diag("env", _envstr())
	_pass()

# --------------------------------------------------------------- period

func _arm_period() -> void:
	var k := _opt_int("k", 5)
	for i in k:
		var x := 16.0 + (float(i) - float(k - 1) / 2.0) * 4.0
		_mk_body("p%d" % i, Vector2(x, 0.0), Vector2(40, 40))
	_it("k", str(k))
	var dss := _dss()
	var seq: Array = []
	var cur := 0
	var ticks: Array = []
	for i in (4 * k + 8):
		ticks.append(i)
	for t in ticks:
		while cur < int(t):
			await physics_frame
			cur += 1
		seq.append(_vec(dss.intersect_point(_pt(_q()), CAP)))
	var p_found := -1
	for p in range(1, 4 * k + 4):
		var ok := true
		for i in range(p, seq.size()):
			if seq[i] != seq[i - p]:
				ok = false
				break
		if ok:
			p_found = p
			break
	_it("cycle_len", str(p_found))
	_it("distinct_ticks", str(_uniq_count(seq)))
	_it("t0_vec", str(seq[0]))
	_it("t2_vec", str(seq[2]))
	_it("t_last_vec", str(seq[seq.size() - 1]))
	_diag("env", _envstr())
	_pass()

# --------------------------------------------------------------- scoutrev

# Byte-level replication of the scout's `--rev` construction: positions are
# INDEX-based (0,8,16,24,32 in creation order), tags are reversed (e,d,c,b,a).
# The physical construction is therefore IDENTICAL to perm0/scout-canon; only the
# labels differ.  If the position vector equals canon's, the scout's
# "reversed add order -> different vector" row is a label permutation, not an
# add-order test.
func _arm_scoutrev() -> void:
	var tags := ["e", "d", "c", "b", "a"]
	for i in tags.size():
		_mk_body(str(tags[i]), Vector2(float(i) * 8.0, 0.0), Vector2(40, 40))
	_it("add_order", "[%s]" % ",".join(tags))
	_it("map", "[e@0,d@8,c@16,b@24,a@32]")
	var ticks := [0, 1, 2, 3, 4, 5, 8, 16, 32]
	var seq: Array = []
	var cur := 0
	var dss := _dss()
	var vec2 := ""
	var relpos2 := ""
	for t in ticks:
		while cur < int(t):
			await physics_frame
			cur += 1
		var r := dss.intersect_point(_pt(_q()), CAP)
		seq.append(_pidx(r))
		if int(t) == 2:
			vec2 = _vec(r)
			relpos2 = _relpos(r, 0.0)
	_it("ladder", _ladderstr(ticks, seq))
	_it("distinct_ticks", str(_uniq_count(seq)))
	_it("t2_vec", vec2)
	_it("t2_relpos", relpos2)
	_it("scout_row_rev_t2_vec", "[a#0,e#0,c#0,b#0,d#0]")
	_it("t2_vec_matches_scout_row", str(vec2 == "[a#0,e#0,c#0,b#0,d#0]"))
	_it("t2_relpos_equals_canon", str(relpos2 == "[32.0000,0.0000|0.0000,0.0000|16.0000,0.0000|24.0000,0.0000|8.0000,0.0000]"))
	_diag("env", _envstr())
	_pass()

# --------------------------------------------------------------- twopiles

func _arm_twopiles() -> void:
	var a := _pile(["a", "b", "c", "d", "e"], 0.0, 0.0)
	var dss := _dss()
	await _frames(2)
	_it("a_t2_vec", _vec(dss.intersect_point(_pt(_q()), CAP)))
	_it("a_t2_relpos", _relpos(dss.intersect_point(_pt(_q()), CAP), 0.0))
	var b := _pile(["a2", "b2", "c2", "d2", "e2"], 0.0, 1000.0)
	await _frames(2)
	_it("a_t4_with_b_vec", _vec(dss.intersect_point(_pt(_q()), CAP)))
	_it("a_t4_with_b_relpos", _relpos(dss.intersect_point(_pt(_q()), CAP), 0.0))
	_it("b_t2_vec", _vec(dss.intersect_point(_pt(Vector2(16, 1000)), CAP)))
	_it("b_t2_relpos", _relpos(dss.intersect_point(_pt(Vector2(16, 1000)), CAP), 0.0))
	await _frames(2)
	_it("a_t6_with_b_vec", _vec(dss.intersect_point(_pt(_q()), CAP)))
	_it("b_t4_vec", _vec(dss.intersect_point(_pt(Vector2(16, 1000)), CAP)))
	_diag("env", _envstr())
	_pass()

# --------------------------------------------------------------- env

func _arm_env() -> void:
	var pf0 := Engine.get_physics_frames()
	var pr0 := Engine.get_process_frames()
	_it("sep2d_has", str(ProjectSettings.has_setting("physics/2d/run_on_separate_thread")))
	_it("sep2d", str(ProjectSettings.get_setting("physics/2d/run_on_separate_thread", "absent")))
	_it("tps", str(Engine.physics_ticks_per_second))
	_it("maxsteps", str(ProjectSettings.get_setting("physics/common/max_physics_steps_per_frame", "absent")))
	await _frames(2)
	_it("pf_delta", str(Engine.get_physics_frames() - pf0))
	_it("proc_delta", str(Engine.get_process_frames() - pr0))
	_it("pf_per_await", "%.3f" % (float(Engine.get_physics_frames() - pf0) / 2.0))
	_it("proc_per_await", "%.3f" % (float(Engine.get_process_frames() - pr0) / 2.0))
	_diag("env", _envstr())
	_pass()
