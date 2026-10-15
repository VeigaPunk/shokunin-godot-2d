extends SceneTree
# r97-boundary attack probe (r97b) — SceneTree group / deferred / idle-frame
# lattice, attacked under quiet + hog-load + `--fixed-fps` modes.
#
# Launch shape (same as the frozen r97-scout probe):
#   godot --headless --path proj --script res://r97b_lattice.gd -- --arm=<name>
# bounded by `timeout -s KILL`.  Every arm prints `R97 r97b_lattice <arm>
# <key>=<value>` diagnostics and one final `PASS r97b_lattice <arm> …` line.
# No RID / object id / instance id / address / absolute frame index is ever
# printed (byte-stability): identities are node tags, frame data is a RELATIVE
# frame clock (`@v`, incremented on every `process_frame` signal emission).
#
# Arms (each attacks one r97-scout claim; see reports/round-97/r97-boundary.md):
#   order_ticks          L1 "group order == tree order": is the vector stable
#                        ACROSS frames/ticks (r95 lesson: order can be a
#                        tick-phase cycle), and does it track a tree move?
#   order_priority       L2 "group-call order == tree order": hunt the unstated
#                        priority mode (`process_priority` /
#                        `process_thread_group_order`), with a `_process`
#                        control proving the priorities are live.
#   defer_capture_order  L3 "member list captured at QUEUE time": is the ORDER
#                        captured too, or re-derived at flush?  Plus
#                        remove/join/queue_free/free/detach/reparent edges and
#                        the in-call group mutation the scout left unmeasured.
#   defer_phase          L10 idle-frame order: where do physics ticks, node
#                        `_process`, the `process_frame` signal and the
#                        deferred flush sit relative to each other, per mode?
#   phys_await           scout §9.1: `await physics_frame` frame index is
#                        "bimodal, a --fixed-fps run would make it
#                        deterministic" — measured distribution + frame shape.

var arm := ""
var _items: PackedStringArray = []
var ORDER: Array = []
var PLOG: Array = []
var NODES: Dictionary = {}
var G: Node = null
var CLK: Array = [0]
var PN: PhaseNode = null


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()


func _run() -> void:
	G = Node.new()
	G.name = "G"
	root.add_child(G)
	match arm:
		"order_ticks": await _arm_order_ticks()
		"order_priority": await _arm_order_priority()
		"defer_capture_order": await _arm_defer_capture_order()
		"defer_phase": await _arm_defer_phase()
		"frame_shape": await _arm_frame_shape()
		"phys_await": await _arm_phys_await()
		_: _fail("unknown_arm")


# ------------------------------------------------------------------ plumbing

func _fail(reason: String) -> void:
	print("FAIL r97b_lattice %s reason=%s" % [arm, reason])
	quit(1)


func _it(key: String, value: String) -> void:
	_items.append("%s=%s" % [key, value])
	print("R97 r97b_lattice %s %s=%s" % [arm, key, value])


func _pass() -> void:
	print("PASS r97b_lattice %s %s" % [arm, " ".join(_items)])
	quit()


func _v(b: bool) -> String:
	return "true" if b else "false"


func _ord(a: Array) -> String:
	var parts: PackedStringArray = []
	for x in a:
		parts.append(str(x))
	return "[%s]" % ",".join(parts)


func _take() -> String:
	var s := _ord(ORDER)
	ORDER.clear()
	return s


func _mk(tag: String, parent: Node = null) -> LNode:
	var n := LNode.new(ORDER)
	n.name = tag
	n.tag = tag
	n.tree = self
	n.clk = CLK
	(parent if parent != null else G).add_child(n)
	NODES[tag] = n
	return n


func _vec(grp: String) -> String:
	var out: Array = []
	for n in get_nodes_in_group(grp):
		out.append(str(n.name))
	return ",".join(out)


func _dfs_names(n: Node, out: Array) -> void:
	for c in n.get_children():
		out.append(str(c.name))
		_dfs_names(c, out)


func _tree() -> String:
	var out: Array = []
	_dfs_names(G, out)
	return ",".join(out)


func _dfs_members(n: Node, grp: String, out: Array) -> void:
	for c in n.get_children():
		if c.is_in_group(grp):
			out.append(str(c.name))
		_dfs_members(c, grp, out)


func _dfs_member_str(grp: String) -> String:
	var out: Array = []
	_dfs_members(G, grp, out)
	return ",".join(out)


func _distinct(a: Array) -> int:
	var s: Dictionary = {}
	for x in a:
		s[str(x)] = true
	return s.size()


func _cycle(a: Array) -> int:
	if a.size() < 2:
		return -1
	for i in range(1, a.size()):
		if str(a[i]) == str(a[0]):
			return i
	return -1


func _hist(a: Array) -> String:
	var d: Dictionary = {}
	for x in a:
		var k := str(x)
		d[k] = int(d.get(k, 0)) + 1
	var keys: Array = d.keys()
	keys.sort()
	var parts: PackedStringArray = []
	for k in keys:
		parts.append("%s:%d" % [k, d[k]])
	return "[" + ",".join(parts) + "]"


func _rev_str(csv: String) -> String:
	var parts := csv.split(",")
	parts.reverse()
	return ",".join(parts)


func _tag_of(entry: String) -> String:
	return entry.split("@")[0]


func _stamp_of(entry: String) -> int:
	var parts := entry.split("@")
	return int(parts[1]) if parts.size() > 1 else -1


func _split_frame(seq: Array, v: int) -> Dictionary:
	# frame v = [entries stamped v-1 before `pf_sig@v`] (physics + node _process)
	#         + `pf_sig@v` + [entries stamped v after it] (the deferred flush)
	var pre: Array = []
	var post: Array = []
	var phase := 0
	for e in seq:
		var s := str(e)
		if s == "pf_sig@%d" % v:
			phase = 1
			continue
		if s == "pf_sig@%d" % (v + 1):
			phase = 2
			continue
		if phase == 0 and _stamp_of(s) == v - 1:
			pre.append(_tag_of(s))
		elif phase == 1 and _stamp_of(s) == v:
			post.append(_tag_of(s))
	return {"pre": pre, "post": post}


func _clock_only() -> void:
	process_frame.connect(func() -> void: CLK[0] += 1)


func _clock_with_marker() -> void:
	process_frame.connect(func() -> void:
		CLK[0] += 1
		ORDER.append("pf_sig@%d" % CLK[0]))


func _join(seg: Array) -> String:
	var parts: PackedStringArray = []
	for x in seg:
		parts.append(str(x))
	return ",".join(parts)


func _has(seg: Array, tag: String) -> bool:
	return seg.has(tag)


# ------------------------------------------------------------------ helpers

class LNode extends Node2D:
	var tag := ""
	var log: Array = []
	var tree: SceneTree = null
	var clk: Array = []
	var hook := Callable()
	func _init(l: Array = []) -> void:
		log = l
	func mark(_k: String) -> void:
		log.append(tag)
	func mark_clk(_k: String) -> void:
		log.append("%s@%d" % [tag, clk[0]])
	func mark_mut(_k: String) -> void:
		log.append("%s@%d" % [tag, clk[0]])
		if hook.is_valid():
			hook.call(tag)
	func mark_cq(_k: String, q: int) -> void:
		log.append("%s(q%d)@%d" % [tag, q, clk[0]])
	func defer_mark(_k: String) -> void:
		log.append("%s!@%d" % [tag, clk[0]])
		if tree != null:
			tree.call_group_flags(SceneTree.GROUP_CALL_DEFERRED, "g9", "mark_clk", "n2")


class ProcNode extends Node:
	var tag := ""
	var log: Array = []
	func _init(l: Array = [], t: String = "") -> void:
		log = l
		tag = t
	func _ready() -> void:
		set_process(true)
	func _process(_d: float) -> void:
		log.append(tag)


class Sampler extends Node:
	var tree: SceneTree
	var grp := ""
	var log: Array = []
	var idle: Array = []
	var idle_calls: Array = []
	var phys: Array = []
	var phys_calls: Array = []
	var n_idle := 0
	var n_phys := 0
	func _ready() -> void:
		set_process(true)
		set_physics_process(true)
	func vec() -> String:
		var out: Array = []
		for n in tree.get_nodes_in_group(grp):
			out.append(str(n.name))
		return ",".join(out)
	func _process(_d: float) -> void:
		n_idle += 1
		idle.append(vec())
		log.clear()
		tree.call_group(grp, "mark", "i")
		idle_calls.append(",".join(log))
	func _physics_process(_d: float) -> void:
		n_phys += 1
		phys.append(vec())
		log.clear()
		tree.call_group(grp, "mark", "p")
		phys_calls.append(",".join(log))


class PhaseNode extends Node:
	var log: Array = []
	var tree: SceneTree
	var grp := ""
	var clk: Array = []
	func _init(l: Array, t: SceneTree, g: String, c: Array) -> void:
		log = l
		tree = t
		grp = g
		clk = c
	func _ready() -> void:
		set_process(true)
		set_physics_process(true)
	func _process(_d: float) -> void:
		log.append("nodeproc@%d" % clk[0])
		call_deferred("cb", "D_proc", clk[0])
		log.append("postq@%d" % clk[0])
		tree.call_group_flags(SceneTree.GROUP_CALL_DEFERRED, grp, "mark_cq", "dq", clk[0])
		log.append("postg@%d" % clk[0])
	func _physics_process(_d: float) -> void:
		log.append("phys@%d" % clk[0])
		call_deferred("cb", "D_phys", clk[0])
		log.append("postp@%d" % clk[0])
	func cb(tag: String, q: int) -> void:
		log.append("%s(q%d)@%d" % [tag, q, clk[0]])


class CbNode extends Node:
	var log: Array = []
	var clk: Array = []
	func _init(l: Array = [], c: Array = []) -> void:
		log = l
		clk = c
	func cb(tag: String) -> void:
		log.append("%s@%d" % [tag, clk[0]])


# ------------------------------------------------------------------ arms

func _arm_order_ticks() -> void:
	# The scout's L1 construction, sampled every frame and every tick.
	var a := _mk("a")
	var b := _mk("b")
	var c := _mk("c")
	var d := _mk("d")
	var p := _mk("p")
	var ch := _mk("ch", p)
	var add_order: Array = ["c", "a", "ch", "d", "b", "p"]
	for t in add_order:
		(NODES[t] as Node).add_to_group("g1")
	_it("add_order", _ord(add_order))
	_it("t0_read", _vec("g1"))
	_it("t0_dfs", _dfs_member_str("g1"))
	_it("t0_eq_dfs", _v(_vec("g1") == _dfs_member_str("g1")))
	var s := Sampler.new()
	s.name = "S"
	s.tree = self
	s.grp = "g1"
	s.log = ORDER
	G.add_child(s)
	for i in 24:
		await process_frame
	var p1_idle: Array = s.idle.duplicate()
	var p1_icall: Array = s.idle_calls.duplicate()
	var p1_phys: Array = s.phys.duplicate()
	_it("p1_idle_n", str(p1_idle.size()))
	_it("p1_idle_distinct", str(_distinct(p1_idle)))
	_it("p1_idle_cycle", str(_cycle(p1_idle)))
	_it("p1_idle_vec", str(p1_idle[0]) if p1_idle.size() > 0 else "none")
	_it("p1_icall_distinct", str(_distinct(p1_icall)))
	_it("p1_call_eq_read", _v(p1_icall == p1_idle))
	_it("p1_phys_n", str(p1_phys.size()))
	_it("p1_phys_distinct", str(_distinct(p1_phys)))
	_it("p1_phys_cycle", str(_cycle(p1_phys)))
	_it("p1_phys_vec", str(p1_phys[0]) if p1_phys.size() > 0 else "none")
	# tree move with no group op: does the read track the tree at read time?
	G.move_child(NODES["a"], G.get_child_count() - 1)
	var moved := _vec("g1")
	_it("after_move_read", moved)
	_it("after_move_dfs", _dfs_member_str("g1"))
	_it("after_move_eq_dfs", _v(moved == _dfs_member_str("g1")))
	var n0_i := s.idle.size()
	var n0_p := s.phys.size()
	for i in 24:
		await process_frame
	var p2_idle: Array = s.idle.slice(n0_i)
	var p2_phys: Array = s.phys.slice(n0_p)
	var p2_icall: Array = s.idle_calls.slice(n0_i)
	_it("p2_idle_n", str(p2_idle.size()))
	_it("p2_idle_distinct", str(_distinct(p2_idle)))
	_it("p2_idle_cycle", str(_cycle(p2_idle)))
	_it("p2_idle_vec", str(p2_idle[0]) if p2_idle.size() > 0 else "none")
	_it("p2_idle_eq_moved", _v(str(p2_idle[0]) == moved if p2_idle.size() > 0 else false))
	_it("p2_call_eq_read", _v(p2_icall == p2_idle))
	_it("p2_phys_n", str(p2_phys.size()))
	_it("p2_phys_distinct", str(_distinct(p2_phys)))
	_it("p2_phys_vec", str(p2_phys[0]) if p2_phys.size() > 0 else "none")
	_it("tree", _tree())
	_it("read_eq_dfs", _v(_vec("g1") == _dfs_member_str("g1")))
	_pass()


func _arm_order_priority() -> void:
	# Hunt the priority mode the scout never armed.
	var a := _mk("a")
	var b := _mk("b")
	var c := _mk("c")
	var d := _mk("d")
	for t in ["d", "b", "a", "c"]:
		(NODES[t] as Node).add_to_group("g2")
	_it("base_read", _vec("g2"))
	call_group("g2", "mark", "x")
	_it("base_call", _take())
	call_group_flags(SceneTree.GROUP_CALL_REVERSE, "g2", "mark", "x")
	_it("base_call_rev", _take())
	# control: four nodes whose only job is to log their _process order
	var pa := ProcNode.new(ORDER, "pa")
	pa.name = "PA"
	var pb := ProcNode.new(ORDER, "pb")
	pb.name = "PB"
	var pc := ProcNode.new(ORDER, "pc")
	pc.name = "PC"
	var pd := ProcNode.new(ORDER, "pd")
	pd.name = "PD"
	for n in [pa, pb, pc, pd]:
		G.add_child(n)
	var has_prio: bool = pa.has_method("set_process_priority")
	_it("prio_available", _v(has_prio))
	if has_prio:
		pa.set_process_priority(100)
		pb.set_process_priority(-100)
		pc.set_process_priority(50)
		pd.set_process_priority(0)
		_it("prio_get", "%d/%d/%d/%d" % [pa.get_process_priority(),
			pb.get_process_priority(), pc.get_process_priority(), pd.get_process_priority()])
		await process_frame
		ORDER.clear()
		await process_frame
		var ctrl: Array = []
		for e in ORDER:
			if ["pa", "pb", "pc", "pd"].has(str(e)):
				ctrl.append(str(e))
		_it("prio_proc_order", _ord(ctrl))
		for n in [pa, pb, pc, pd]:
			n.set_process(false)
		# same priorities on the group members
		a.set_process_priority(100)
		b.set_process_priority(-100)
		c.set_process_priority(50)
		d.set_process_priority(0)
		_it("gprio_get", "%d/%d/%d/%d" % [a.get_process_priority(), b.get_process_priority(),
			c.get_process_priority(), d.get_process_priority()])
		_it("prio_read", _vec("g2"))
		ORDER.clear()
		call_group("g2", "mark", "x")
		_it("prio_call", _take())
		call_group_flags(SceneTree.GROUP_CALL_REVERSE, "g2", "mark", "x")
		_it("prio_call_rev", _take())
		for n in [a, b, c, d]:
			n.set_process_priority(0)
	# process_thread_group_order (censused, never armed by the scout)
	var has_tgo: bool = a.has_method("set_process_thread_group_order") \
		and a.has_method("get_process_thread_group_order")
	_it("tgo_available", _v(has_tgo))
	if has_tgo:
		a.set_process_thread_group_order(3)
		b.set_process_thread_group_order(1)
		c.set_process_thread_group_order(2)
		d.set_process_thread_group_order(0)
		_it("tgo_get", "%d/%d/%d/%d" % [a.get_process_thread_group_order(),
			b.get_process_thread_group_order(), c.get_process_thread_group_order(),
			d.get_process_thread_group_order()])
		_it("tgo_read", _vec("g2"))
		call_group("g2", "mark", "x")
		_it("tgo_call", _take())
		call_group_flags(SceneTree.GROUP_CALL_REVERSE, "g2", "mark", "x")
		_it("tgo_call_rev", _take())
		for n in [a, b, c, d]:
			n.set_process_thread_group_order(0)
	# tree move: does a read follow the tree at read time?
	G.move_child(NODES["d"], 0)
	_it("after_move_read", _vec("g2"))
	_it("after_move_dfs", _dfs_member_str("g2"))
	_it("after_move_eq_dfs", _v(_vec("g2") == _dfs_member_str("g2")))
	call_group("g2", "mark", "x")
	_it("after_move_call", _take())
	_it("tree", _tree())
	_pass()


func _arm_defer_capture_order() -> void:
	# L3, sharpened: capture is proven for the SET; is the ORDER captured too?
	_clock_only()
	var a := _mk("a")
	var b := _mk("b")
	var c := _mk("c")
	var d := _mk("d")
	for t in ["a", "b", "c", "d"]:
		(NODES[t] as Node).add_to_group("g3")
	var q_read := _vec("g3")
	call_group_flags(SceneTree.GROUP_CALL_DEFERRED, "g3", "mark_clk", "q")
	G.move_child(d, 0)
	var f_read := _vec("g3")
	await process_frame
	await process_frame
	var fwd_call := _take()
	_it("fwd_queue_read", q_read)
	_it("fwd_flush_read", f_read)
	_it("fwd_call", fwd_call)
	_it("fwd_call_eq_queue", _v(_tags_only(fwd_call) == q_read))
	_it("fwd_call_eq_flush", _v(_tags_only(fwd_call) == f_read))
	_it("fwd_read_after", _vec("g3"))
	# reverse variant
	var e := _mk("e")
	var f := _mk("f")
	var g := _mk("g")
	for t in ["e", "f", "g"]:
		(NODES[t] as Node).add_to_group("g4")
	var rq := _vec("g4")
	call_group_flags(SceneTree.GROUP_CALL_DEFERRED | SceneTree.GROUP_CALL_REVERSE, "g4", "mark_clk", "q")
	G.move_child(g, 0)
	var rf := _vec("g4")
	await process_frame
	await process_frame
	var rev_call := _take()
	_it("rev_queue_read", rq)
	_it("rev_flush_read", rf)
	_it("rev_call", rev_call)
	_it("rev_call_eq_queue_rev", _v(_tags_only(rev_call) == _rev_str(rq)))
	_it("rev_call_eq_flush_rev", _v(_tags_only(rev_call) == _rev_str(rf)))
	# membership / lifecycle edges between queue and flush
	var h := _mk("h")
	var i2 := _mk("i")
	var j := _mk("j")
	var k := _mk("k")
	h.add_to_group("g5")
	j.add_to_group("g5")
	k.add_to_group("g5")
	_it("mut_queue_read", _vec("g5"))
	call_group_flags(SceneTree.GROUP_CALL_DEFERRED, "g5", "mark_clk", "q")
	j.remove_from_group("g5")
	i2.add_to_group("g5")
	k.queue_free()
	h.free()
	await process_frame
	await process_frame
	_it("mut_call", _take())
	_it("mut_read_after", _vec("g5"))
	_it("mut_k_valid", _v(is_instance_valid(k)))
	# detach (out of tree, not freed) and reparent between queue and flush
	var m := _mk("m")
	var n2 := _mk("n")
	var o := _mk("o")
	m.add_to_group("g6")
	n2.add_to_group("g6")
	o.add_to_group("g6")
	_it("det_queue_read", _vec("g6"))
	call_group_flags(SceneTree.GROUP_CALL_DEFERRED, "g6", "mark_clk", "q")
	G.remove_child(m)
	var holder := Node.new()
	holder.name = "H"
	root.add_child(holder)
	n2.reparent(holder)
	_it("det_flush_read", _vec("g6"))
	await process_frame
	await process_frame
	_it("det_call", _take())
	_it("det_read_after", _vec("g6"))
	# set_group_flags(DEFERRED): a node that JOINS after the queue
	var q1 := _mk("q1")
	q1.add_to_group("g8")
	_it("setg_queue_read", _vec("g8"))
	set_group_flags(SceneTree.GROUP_CALL_DEFERRED, "g8", "position", Vector2(5, 5))
	var q2 := _mk("q2")
	q2.add_to_group("g8")
	await process_frame
	await process_frame
	_it("setg_join_pos", "(%.1f,%.1f)" % [q2.position.x, q2.position.y])
	_it("setg_old_pos", "(%.1f,%.1f)" % [q1.position.x, q1.position.y])
	# deferred group call queued from INSIDE the deferred flush
	var r1 := _mk("r1")
	r1.add_to_group("g9")
	call_group_flags(SceneTree.GROUP_CALL_DEFERRED, "g9", "defer_mark", "x")
	await process_frame
	await process_frame
	_it("nested_call", _take())
	# direct call while a member mutates the same group (scout §9.5)
	var s1 := _mk("s1")
	var s2 := _mk("s2")
	var s3 := _mk("s3")
	var s4 := _mk("s4")
	for t in ["s1", "s2", "s3"]:
		(NODES[t] as Node).add_to_group("g10")
	s1.hook = mut_hook
	_it("callmut_before", _vec("g10"))
	call_group("g10", "mark_mut", "x")
	_it("callmut_call", _take())
	_it("callmut_after", _vec("g10"))
	# cleanup: no orphan node / leaked RID at exit
	if is_instance_valid(holder):
		holder.free()
	if is_instance_valid(m):
		m.free()
	_pass()


func _tags_only(vec: String) -> String:
	var s := vec
	if s.begins_with("["):
		s = s.substr(1)
	if s.ends_with("]"):
		s = s.substr(0, s.length() - 1)
	var parts := s.split(",")
	var out: PackedStringArray = []
	for p in parts:
		out.append(str(p).split("@")[0])
	return ",".join(out)


func mut_hook(tag: String) -> void:
	if tag == "s1":
		if NODES.has("s2") and is_instance_valid(NODES["s2"]):
			(NODES["s2"] as Node).remove_from_group("g10")
		if NODES.has("s4") and is_instance_valid(NODES["s4"]):
			(NODES["s4"] as Node).add_to_group("g10")


func _arm_defer_phase() -> void:
	# L10: where do physics ticks / node _process / the process_frame signal /
	# the deferred flush sit relative to each other?
	# Self-owned frame clock `@v`: v increments at every `process_frame`
	# emission, so pre-signal entries of frame k carry v = k-1 and `pf_sig@k`.
	# Every deferred entry also carries its queue clock, so "ran in the same
	# frame, before the signal" is decidable from one interleaved log.
	_clock_with_marker()
	process_frame.connect(func() -> void: PLOG.append("pf_sig@%d" % CLK[0]))
	var a := _mk("a")
	var b := _mk("b")
	a.add_to_group("g7")
	b.add_to_group("g7")
	var pn := PhaseNode.new(PLOG, self, "g7", CLK)
	pn.name = "PH"
	G.add_child(pn)
	PN = pn
	# a deferred call queued from the signal listener itself
	process_frame.connect(func() -> void:
		PN.call_deferred("cb", "D_sig", CLK[0]))
	for i in 2:
		await process_frame
	PLOG.clear()
	for i in 4:
		await process_frame
	# one more frame: where does the `await process_frame` continuation resume?
	await process_frame
	PLOG.append("resume@%d" % CLK[0])
	var seq: Array = PLOG.duplicate()
	_it("seq", _ord(seq))
	var iters: Array = []
	for e in seq:
		var it := _stamp_of(str(e))
		if it >= 0 and not iters.has(it):
			iters.append(it)
	iters.sort()
	_it("iters", _ord(iters))
	# per-stamp split: entries before the `pf_sig@v` emission vs after it
	for k in iters.size():
		var v: int = int(iters[k])
		var pre: Array = []
		var post: Array = []
		var seen := false
		for e in seq:
			var s := str(e)
			if _stamp_of(s) != v:
				continue
			if s.begins_with("pf_sig@"):
				seen = true
				continue
			if seen:
				post.append(s)
			else:
				pre.append(s)
		_it("v%d_pre" % v, _ord(pre))
		_it("v%d_post" % v, _ord(post))
	# queue -> run delay for the deferred call queued from `nodeproc`
	var delays: Array = []
	for e in seq:
		var s := str(e)
		if s.begins_with("D_proc(q"):
			delays.append(_stamp_of(s) - _q_of(s))
	_it("dproc_delay", _hist(delays))
	# queue -> run delay for the deferred call queued from the signal listener
	var dsd: Array = []
	for e in seq:
		var s := str(e)
		if s.begins_with("D_sig(q"):
			dsd.append(_stamp_of(s) - _q_of(s))
	_it("dsig_delay", _hist(dsd))
	# did a `nodeproc`-queued deferred call run BEFORE its own frame signal?
	var before_sig := false
	var after_sig := false
	for e in seq:
		var s := str(e)
		if s.begins_with("D_proc(q"):
			var q := _q_of(s)
			if _pos_before(seq, s, "pf_sig@%d" % (q + 1)):
				before_sig = true
			else:
				after_sig = true
	_it("dproc_before_sig", _v(before_sig))
	_it("dproc_after_sig", _v(after_sig))
	# group deferred call marks (the LNodes log into ORDER, not PLOG)
	var gmarks: Array = ORDER.duplicate()
	_it("gmarks", _ord(gmarks))
	var gd2: Array = []
	var gbefore := false
	var gafter := false
	for e in gmarks:
		var s := str(e)
		if not s.contains("(q"):
			continue
		gd2.append(_stamp_of(s) - _q_of(s))
		if _pos_before(gmarks, s, "pf_sig@%d" % (_q_of(s) + 1)):
			gbefore = true
		else:
			gafter = true
	_it("group_delay", _hist(gd2))
	_it("group_before_sig", _v(gbefore))
	# where does the await continuation sit?
	var resume_entry := ""
	for e in seq:
		if str(e).begins_with("resume@"):
			resume_entry = str(e)
	_it("resume", resume_entry)
	_it("resume_after_sig", _v(_pos_before(seq, "pf_sig@%d" % _stamp_of(resume_entry),
		resume_entry)))
	_it("phys_per_frame", "%.2f" % (float(_count_tag(seq, "phys")) / float(max(iters.size(), 1))))
	_it("iter_n", str(iters.size()))
	_pass()


func _pos_before(seq: Array, entry: String, marker: String) -> bool:
	var i := seq.find(entry)
	var j := seq.find(marker)
	return i >= 0 and j >= 0 and i < j


func _q_of(entry: String) -> int:
	var i := entry.find("(q")
	var j := entry.find(")", i)
	return int(entry.substr(i + 2, j - i - 2)) if i >= 0 and j > i else -1


func _count_tag(seq: Array, tag: String) -> int:
	var n := 0
	for e in seq:
		if _tag_of(str(e)) == tag:
			n += 1
	return n


func _arm_frame_shape() -> void:
	# Clean control: no deferred calls at all.  Where do the node `_process`
	# callback, the node `_physics_process` callback and the `process_frame`
	# signal sit relative to each other inside one frame-epoch?
	_clock_with_marker()
	process_frame.connect(func() -> void: PLOG.append("pf_sig@%d" % CLK[0]))
	var pn := PhaseNode.new(PLOG, self, "g7", CLK)
	pn.name = "PH"
	G.add_child(pn)
	for i in 2:
		await process_frame
	PLOG.clear()
	for i in 4:
		await process_frame
	var seq: Array = PLOG.duplicate()
	_it("seq", _ord(seq))
	var n_proc := 0
	var n_phys := 0
	var n_sig := 0
	for e in seq:
		var s := str(e)
		if s.begins_with("nodeproc@"):
			n_proc += 1
		elif s.begins_with("phys@"):
			n_phys += 1
		elif s.begins_with("pf_sig@"):
			n_sig += 1
	_it("n_nodeproc", str(n_proc))
	_it("n_phys", str(n_phys))
	_it("n_sig", str(n_sig))
	_it("phys_per_frame", "%.2f" % (float(n_phys) / float(max(n_sig, 1))))
	var p0 := _first_of(seq, "nodeproc@")
	var h0 := _first_of(seq, "phys@")
	_it("proc_before_sig", _v(_pos_before(seq, p0, "pf_sig@%d" % (_stamp_of(p0) + 1))))
	_it("phys_before_sig", _v(_pos_before(seq, h0, "pf_sig@%d" % (_stamp_of(h0) + 1))))
	_it("proc_before_phys", _v(_pos_before(seq, p0, h0)))
	_pass()


func _first_of(seq: Array, prefix: String) -> String:
	for e in seq:
		if str(e).begins_with(prefix):
			return str(e)
	return ""


func _arm_phys_await() -> void:
	# scout §9.1: is the `await physics_frame` index deterministic under ff?
	_clock_only()
	var pf0 := Engine.get_process_frames()
	var ph0 := Engine.get_physics_frames()
	for i in 60:
		await process_frame
	var d_pf := Engine.get_process_frames() - pf0
	var d_ph := Engine.get_physics_frames() - ph0
	_it("frame_shape", "pf=%d ph=%d ratio=%.4f" % [d_pf, d_ph, float(d_ph) / float(d_pf)])
	var seq: Array = []
	for i in 24:
		var p0 := Engine.get_physics_frames()
		var f0 := Engine.get_process_frames()
		await physics_frame
		seq.append("%d:%d" % [Engine.get_physics_frames() - p0,
			Engine.get_process_frames() - f0])
	_it("await_n", str(seq.size()))
	_it("await_dph", _hist(seq.map(func(s: String) -> String: return s.split(":")[0])))
	_it("await_dpf", _hist(seq.map(func(s: String) -> String: return s.split(":")[1])))
	_it("await_same_frame", str(seq.filter(func(s: String) -> bool: return s.ends_with(":0")).size()))
	_it("await_two_frames", str(seq.filter(func(s: String) -> bool: return s.ends_with(":2")).size()))
	_it("await_seq", _ord(seq))
	# deferred call queued from a physics_frame continuation: same frame?
	var cb := CbNode.new(ORDER, CLK)
	cb.name = "CB"
	G.add_child(cb)
	await physics_frame
	var q_stamp: int = int(CLK[0])
	cb.call_deferred("cb", "P")
	await process_frame
	await process_frame
	var entries: Array = []
	for e in ORDER.duplicate():
		if _tag_of(str(e)) == "P":
			entries.append(str(e))
	var same := false
	for e in entries:
		if _stamp_of(str(e)) == q_stamp:
			same = true
	_it("phys_defer_same_frame", _v(same))
	_it("phys_defer_log", _ord(entries))
	_it("phys_defer_qstamp", str(q_stamp))
	_pass()
