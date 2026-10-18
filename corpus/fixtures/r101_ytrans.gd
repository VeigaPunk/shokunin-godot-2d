extends SceneTree
# r101 Y-translation probe (E17-YTRANS) — the surface the dead `--offy` flag
# claimed.  r95's `r95b_order_celloff_y1000` row passed `--offy=1000` but
# `_arm_celloff` never read it (`offy` occurs 0 times in r95b_order.gd), so the
# row was a byte-exact duplicate of `celloff_x0` and Y-translation invariance was
# NEVER measured.  This fixture measures it for real:
#   ytrans : single pile at (0, offy), queried at (16, offy).  The flag is
#            consumed (dy_resid proves it), the translated hit count and the
#            origin hit count are BOTH measured (5 vs 0 at offy=1000 — unforgeable
#            by echoing the flag), and t2/t64_absy read the colliders' real y.
#            The ladder + relative order vector are emitted as R101Y DIAGS
#            only: they are phase-bimodal at offy!=0 (settling order depends
#            on how many real frames ran — measured quiet pf=3 vs in-battery
#            pf=64, run 1) while every pinned invariant holds in both phases.
#            The phase-stable y0 row keeps the full order pin as the sentinel.
#   ysep   : the falsification cell — pile at y=offy, query at y=qoffy (gap>0)
#            must return 0 hits; a probe that skipped the translation returns 5.
#   ycop   : Y co-presence — pile A at y=0 + pile B (a2..e2) at y=offy: measured
#            inter-pile distance, per-pile attribution (no cross tags), the
#            between-pile emptiness, and B's perturbation of A's order vector.
#   census : executable retirement census — `offy` token count in the committed
#            r95b_order.gd source (0 = no read is reachable) + its source sha256,
#            a tripwire if that file ever gains support.
#
# Battery launch shape:
#   godot --headless --path proj --script res://r101_ytrans.gd -- --arm=<name> [--offy=F]
#
# Prints one `PASS r101_ytrans <arm> k=v ...` line; `R101Y` diag lines are not
# part of the authorable signature.

const CAP := 32
const TAGS5 := ["a", "b", "c", "d", "e"]
const TAG_X := {"a": 0.0, "b": 8.0, "c": 16.0, "d": 24.0, "e": 32.0}
const CANON_T2_VEC := "[e#0,a#0,c#0,d#0,b#0]"
const CANON_T2_RELPOS := "[32.0000,0.0000|0.0000,0.0000|16.0000,0.0000|24.0000,0.0000|8.0000,0.0000]"

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
		"ytrans": await _arm_ytrans()
		"ysep": await _arm_ysep()
		"ycop": await _arm_ycop()
		"census": _arm_census()
		_: _fail("unknown_arm")

# --------------------------------------------------------------- utilities

func _fail(reason: String) -> void:
	print("FAIL r101_ytrans %s reason=%s" % [arm, reason])
	quit(1)

func _opt_float(k: String, d: float) -> float:
	return float(opt.get(k, d))

func _it(key: String, value: String) -> void:
	_items.append("%s=%s" % [key, value])
	print("R101Y %s %s=%s" % [arm, key, value])

func _diag(key: String, value: String) -> void:
	print("R101Y %s %s=%s" % [arm, key, value])

func _pass() -> void:
	print("PASS r101_ytrans %s %s" % [arm, " ".join(_items)])
	quit()

func _frames(n: int) -> void:
	for i in n:
		await physics_frame

func _dss() -> PhysicsDirectSpaceState2D:
	return PhysicsServer2D.space_get_direct_state(root.world_2d.space)

func _envstr() -> String:
	return "tps=%d pf=%d proc=%d" % [
		Engine.physics_ticks_per_second, Engine.get_physics_frames(),
		Engine.get_process_frames()]

func _tag(d: Dictionary) -> String:
	var c: Object = d.get("collider")
	if c == null and d.has("collider_id"):
		c = instance_from_id(int(d.get("collider_id")))
	if c == null:
		return "?"
	return str(c.get_meta("tag", c.get_class()))

func _vec(arr: Array) -> String:
	var parts: PackedStringArray = []
	for d in arr:
		parts.append("%s#%s" % [_tag(d), str(d.get("shape", "-"))])
	return "[%s]" % ",".join(parts)

func _pidx(arr: Array) -> String:
	var parts: PackedStringArray = []
	for d in arr:
		var t := _tag(d)
		parts.append(str(TAGS5.find(t)) if t in TAGS5 else t)
	return ",".join(parts)

# position list relative to the query offset (ox, oy) — the translation-invariant
# coordinate frame of the ordering laws
func _relpos(arr: Array, ox: float, oy: float) -> String:
	var parts: PackedStringArray = []
	for d in arr:
		var n2 := d.get("collider") as Node2D
		if n2 == null:
			parts.append("?")
			continue
		var p := n2.global_position
		parts.append("%.4f,%.4f" % [p.x - ox, p.y - oy])
	return "[%s]" % "|".join(parts)

# absolute y of every returned collider, read from the node — evidence the
# translation physically happened (an echo of the flag cannot produce this)
func _absy(arr: Array) -> String:
	var parts: PackedStringArray = []
	for d in arr:
		var n2 := d.get("collider") as Node2D
		parts.append("?" if n2 == null else "%.4f" % n2.global_position.y)
	return "[%s]" % "|".join(parts)

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

func _mk_body(tag: String, pos: Vector2) -> CollisionObject2D:
	var b := StaticBody2D.new()
	b.name = tag
	b.set_meta("tag", tag)
	var cs := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = Vector2(40, 40)
	cs.shape = rs
	b.add_child(cs)
	b.position = pos
	root.add_child(b)
	return b

func _tagx(t: String) -> float:
	if TAG_X.has(t):
		return float(TAG_X[t])
	return float(TAG_X.get(t.substr(0, 1), 0.0))

func _pile(order: Array, ox: float, oy: float) -> Array:
	var made: Array = []
	for t in order:
		made.append(_mk_body(str(t), Vector2(_tagx(str(t)) + ox, oy)))
	return made

func _pt(pos: Vector2) -> PhysicsPointQueryParameters2D:
	var q := PhysicsPointQueryParameters2D.new()
	q.position = pos
	return q

func _q() -> Vector2:
	return Vector2(16, 0)

# residual between the pile's measured y and the requested offset: 0.0000 iff
# the fixture actually consumed the flag
func _y_resid(made: Array, offy: float) -> String:
	var n2 := made[TAGS5.find("c")] as Node2D
	return "%.4f" % (n2.global_position.y - offy)

func _ladder(ticks: Array, ox: float, oy: float) -> Dictionary:
	var dss := _dss()
	var q := Vector2(16.0 + ox, oy)
	var seq: Array = []
	var cur := 0
	var first_vec := ""
	var first_relpos := ""
	var first_absy := ""
	for t in ticks:
		while cur < int(t):
			await physics_frame
			cur += 1
		var r := dss.intersect_point(_pt(q), CAP)
		seq.append(_pidx(r))
		if first_vec == "":
			first_vec = _vec(r)
			first_relpos = _relpos(r, ox, oy)
			first_absy = _absy(r)
	var last := dss.intersect_point(_pt(q), CAP)
	return {"seq": seq, "first_vec": first_vec, "first_relpos": first_relpos,
		"first_absy": first_absy, "last_vec": _vec(last),
		"last_relpos": _relpos(last, ox, oy), "last_absy": _absy(last)}

func _no_suffix(arr: Array) -> bool:
	for d in arr:
		var t := _tag(d)
		if t.length() > 1 and t.substr(1, 1).is_valid_int():
			return false
	return true

func _all_suffix(arr: Array) -> bool:
	if arr.is_empty():
		return false
	for d in arr:
		var t := _tag(d)
		if t.length() < 2 or not t.substr(1, 1).is_valid_int():
			return false
	return true

# --------------------------------------------------------------- ytrans

func _arm_ytrans() -> void:
	var offy := _opt_float("offy", 0.0)
	var made := _pile(["a", "b", "c", "d", "e"], 0.0, offy)
	_it("offy", "%.4f" % offy)
	_it("add_order", "[a,b,c,d,e]")
	_it("dy_resid", _y_resid(made, offy))
	var ticks := [2, 3, 4, 6, 8, 16, 32, 64]
	var lad: Dictionary = await _ladder(ticks, 0.0, offy)
	_it("distinct_ticks", str(_uniq_count(lad["seq"])))
	_it("last_change_tick", str(_last_change(ticks, lad["seq"])))
	# r101 fold (orchestrator, post-run-1): the ladder + order vectors are
	# PHASE-BIMODAL — at offy!=0 the arm's settling order depends on how many
	# real frames ran before each ladder tick (quiet: pf=3; in-battery: pf=64),
	# so the permutation differs while every translation invariant holds.
	# The PASS line pins phase-invariant fields only; the order law stays
	# visible as diagnostics and remains pinned on the phase-stable y0 row.
	_diag("ladder", _ladderstr(ticks, lad["seq"]))
	_diag("t2_vec", lad["first_vec"])
	_diag("t2_relpos", lad["first_relpos"])
	_it("t2_absy", lad["first_absy"])
	_diag("t2_vec_eq_canon", str(lad["first_vec"] == CANON_T2_VEC))
	_diag("t2_relpos_eq_canon", str(lad["first_relpos"] == CANON_T2_RELPOS))
	var dss := _dss()
	var n_y := dss.intersect_point(_pt(Vector2(16.0, offy)), CAP).size()
	var n_0 := dss.intersect_point(_pt(Vector2(16.0, 0.0)), CAP).size()
	_it("n_at_y", str(n_y))
	_it("n_at_0", str(n_0))
	_diag("t64_relpos", lad["last_relpos"])
	_it("t64_absy", lad["last_absy"])
	_diag("env", _envstr())
	_pass()

# --------------------------------------------------------------- ysep

func _arm_ysep() -> void:
	var offy := _opt_float("offy", 1000.0)
	var qoffy := _opt_float("qoffy", 0.0)
	var made := _pile(["a", "b", "c", "d", "e"], 0.0, offy)
	_it("offy", "%.4f" % offy)
	_it("qoffy", "%.4f" % qoffy)
	_it("dy_resid", _y_resid(made, offy))
	await _frames(2)
	var dss := _dss()
	_it("n_at_q", str(dss.intersect_point(_pt(Vector2(16.0, qoffy)), CAP).size()))
	_it("n_at_pile", str(dss.intersect_point(_pt(Vector2(16.0, offy)), CAP).size()))
	_diag("env", _envstr())
	_pass()

# --------------------------------------------------------------- ycop

func _arm_ycop() -> void:
	var offy := _opt_float("offy", 1000.0)
	var a := _pile(["a", "b", "c", "d", "e"], 0.0, 0.0)
	await _frames(2)
	var dss := _dss()
	var a2 := dss.intersect_point(_pt(_q()), CAP)
	_it("offy", "%.4f" % offy)
	# Same fold: per-pile absy + cross-clean + counts are phase-invariant;
	# the order vectors are diagnostics (see _arm_ytrans fold note).
	_diag("a_t2_vec", _vec(a2))
	_diag("a_t2_relpos", _relpos(a2, 0.0, 0.0))
	_it("a_t2_absy", _absy(a2))
	_it("a_t2_cross_clean", str(_no_suffix(a2)))
	var b := _pile(["a2", "b2", "c2", "d2", "e2"], 0.0, offy)
	var an := a[2] as Node2D
	var bn := b[2] as Node2D
	_it("dy_meas", "%.4f" % ((bn.global_position.y - an.global_position.y) - offy))
	await _frames(2)
	var a4 := dss.intersect_point(_pt(_q()), CAP)
	var b2 := dss.intersect_point(_pt(Vector2(16.0, offy)), CAP)
	_diag("a_t4_with_b_vec", _vec(a4))
	_diag("a_t4_with_b_relpos", _relpos(a4, 0.0, 0.0))
	_it("a_t4_absy", _absy(a4))
	_it("a_t4_cross_clean", str(_no_suffix(a4)))
	_diag("b_t2_vec", _vec(b2))
	_diag("b_t2_relpos", _relpos(b2, 0.0, offy))
	_it("b_t2_absy", _absy(b2))
	_it("b_t2_cross_clean", str(_all_suffix(b2)))
	_it("n_between", str(dss.intersect_point(_pt(Vector2(16.0, offy / 2.0)), CAP).size()))
	_it("n_origin", str(dss.intersect_point(_pt(_q()), CAP).size()))
	_it("n_at_b", str(dss.intersect_point(_pt(Vector2(16.0, offy)), CAP).size()))
	await _frames(2)
	_diag("a_t6_with_b_vec", _vec(dss.intersect_point(_pt(_q()), CAP)))
	_diag("b_t4_vec", _vec(dss.intersect_point(_pt(Vector2(16.0, offy)), CAP)))
	_diag("env", _envstr())
	_pass()

# --------------------------------------------------------------- census

func _count(hay: String, needle: String) -> int:
	var n := 0
	var i := hay.find(needle)
	while i != -1:
		n += 1
		i = hay.find(needle, i + needle.length())
	return n

# Retirement census for the r95b `--offy` knob: a flag string that occurs 0 times
# in the probe source has no reachable read (given no dynamic flag-name
# construction; the r95 two-seat byte-identity evidence is the runtime leg).
func _arm_census() -> void:
	var src := FileAccess.get_file_as_string("res://r95b_order.gd")
	if src == "":
		_fail("census_source_unreadable")
		return
	_it("r95b_offy_tokens", str(_count(src, "offy")))
	_it("r95b_lines", str(src.split("\n").size()))
	_it("r95b_sha256", src.sha256_text())
	var self_src := FileAccess.get_file_as_string("res://r101_ytrans.gd")
	_diag("self_offy_tokens", str(_count(self_src, "offy")))
	_diag("self_sha256", self_src.sha256_text())
	_it("replacement_arm", "ytrans")
	_pass()
