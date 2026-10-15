extends SceneTree
# r97-boundary SECONDARY attack probe (r97b_extra) — two side quests that are
# NOT in the frozen r97b_lattice.gd revision used for the 324-receipt matrix
# (keeping that probe's evidence chain intact).
#
#   godot --headless --path proj --script res://r97b_extra.gd -- --arm=<name>
#   arms: order_churn      L1 under add/remove/move churn (is the group list a
#                          tree-order VIEW or a stored insertion list that can
#                          drift, the r95 "order cycle" question?)
#         unique_boundary  L4 sharpened: WHERE does the GROUP_CALL_UNIQUE
#                          frame key expire — at the flush or at the
#                          `process_frame` signal?
# Prints `R97 r97b_lattice <arm> …` + one `PASS r97b_lattice <arm> …` line so
# the same analyzer parses it.

var arm := ""
var _items: PackedStringArray = []
var ORDER: Array = []
var NODES: Dictionary = {}
var G: Node = null
var CLK: Array = [0]


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
		"order_churn": await _arm_order_churn()
		"unique_boundary": await _arm_unique_boundary()
		_: _fail("unknown_arm")


func _fail(reason: String) -> void:
	print("FAIL r97b_extra %s reason=%s" % [arm, reason])
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
	n.clk = CLK
	(parent if parent != null else G).add_child(n)
	NODES[tag] = n
	return n


func _vec(grp: String) -> String:
	var out: Array = []
	for n in get_nodes_in_group(grp):
		out.append(str(n.name))
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


func _clock_only() -> void:
	process_frame.connect(func() -> void: CLK[0] += 1)


class LNode extends Node2D:
	var tag := ""
	var log: Array = []
	var clk: Array = []
	func _init(l: Array = []) -> void:
		log = l
	func mark(_k: String) -> void:
		log.append(tag)
	func mark_clk(_k: String) -> void:
		log.append("%s@%d" % [tag, clk[0]])


class Churner extends Node:
	# one add/remove rotation per frame; a move_child every 5th frame
	var tree: SceneTree
	var grp := ""
	var nodes: Dictionary = {}
	var dfs_fn := Callable()
	var g: Node = null
	var tags: Array = []
	var k := 0
	var vecs: Array = []
	var dfs_ok := 0
	var v1_ok := 0
	var v2_ok := 0
	var mism := "none"
	var n := 0
	func _ready() -> void:
		set_process(true)
	func _process(_d: float) -> void:
		n += 1
		var t: String = str(tags[k % tags.size()])
		k += 1
		var node: Node = nodes[t]
		node.remove_from_group(grp)
		var v1 := _vec()
		var d1 := str(dfs_fn.call(grp))
		node.add_to_group(grp)
		var v2 := _vec()
		var d2 := str(dfs_fn.call(grp))
		vecs.append(v1)
		vecs.append(v2)
		if v1 == d1:
			dfs_ok += 1
			v1_ok += 1
		elif mism == "none":
			mism = "v1|got=%s|dfs=%s" % [v1, d1]
		if v2 == d2:
			dfs_ok += 1
			v2_ok += 1
		elif mism == "none":
			mism = "v2|got=%s|dfs=%s" % [v2, d2]
		if n % 5 == 0:
			var first: Node = nodes[str(tags[0])]
			g.move_child(first, g.get_child_count() - 1)
	func _vec() -> String:
		var out: Array = []
		for x in tree.get_nodes_in_group(grp):
			out.append(str(x.name))
		return ",".join(out)


func _arm_order_churn() -> void:
	_clock_only()
	var a := _mk("a")
	var b := _mk("b")
	var c := _mk("c")
	var d := _mk("d")
	var p := _mk("p")
	var ch := _mk("ch", p)
	for t in ["c", "a", "ch", "d", "b", "p"]:
		(NODES[t] as Node).add_to_group("g1")
	_it("t0", _vec("g1"))
	_it("t0_eq_dfs", _v(_vec("g1") == _dfs_member_str("g1")))
	var churn := Churner.new()
	churn.name = "CH"
	churn.tree = self
	churn.grp = "g1"
	churn.nodes = NODES
	churn.dfs_fn = _dfs_member_str
	churn.g = G
	churn.tags = ["a", "b", "c", "d", "p", "ch"]
	G.add_child(churn)
	for i in 30:
		await process_frame
	_it("churn_samples", str(churn.vecs.size()))
	_it("churn_distinct", str(_distinct(churn.vecs)))
	_it("churn_dfs_ok", str(churn.dfs_ok))
	_it("churn_v1_ok", str(churn.v1_ok))
	_it("churn_v2_ok", str(churn.v2_ok))
	_it("churn_mism", str(churn.mism))
	_it("churn_dfs_n", str(churn.vecs.size()))
	_it("churn_dfs_all", _v(churn.dfs_ok == churn.vecs.size()))
	_it("after_churn", _vec("g1"))
	_it("after_churn_dfs", _dfs_member_str("g1"))
	_it("after_churn_eq_dfs", _v(_vec("g1") == _dfs_member_str("g1")))
	# full remove-all then re-add-all in reverse tree order
	var rev: Array = ["ch", "p", "b", "d", "a", "c"]
	for t in rev:
		(NODES[t] as Node).remove_from_group("g1")
	_it("emptied", _vec("g1"))
	for t in rev:
		(NODES[t] as Node).add_to_group("g1")
	_it("readd_rev", _vec("g1"))
	_it("readd_rev_eq_dfs", _v(_vec("g1") == _dfs_member_str("g1")))
	_pass()


class UNode extends Node:
	var tree: SceneTree
	var grp := ""
	func _init(t: SceneTree, g: String) -> void:
		tree = t
		grp = g
	func _ready() -> void:
		set_process(true)
	func _process(_d: float) -> void:
		tree.call_group_flags(SceneTree.GROUP_CALL_UNIQUE | SceneTree.GROUP_CALL_DEFERRED,
			grp, "mark_clk", "u")
		tree.call_group_flags(SceneTree.GROUP_CALL_UNIQUE | SceneTree.GROUP_CALL_DEFERRED,
			grp, "mark_clk", "u")


func _arm_unique_boundary() -> void:
	process_frame.connect(func() -> void:
		CLK[0] += 1
		ORDER.append("pf_sig@%d" % CLK[0])
		# same UNIQUE|DEFERRED call, queued from the signal listener (i.e.
		# after the flush that served the _process-queued call of this frame)
		call_group_flags(SceneTree.GROUP_CALL_UNIQUE | SceneTree.GROUP_CALL_DEFERRED,
			"g2", "mark_clk", "u"))
	var a := _mk("a")
	a.add_to_group("g2")
	var un := UNode.new(self, "g2")
	un.name = "U"
	G.add_child(un)
	for i in 2:
		await process_frame
	ORDER.clear()
	for i in 3:
		await process_frame
	_it("seq", _ord(ORDER))
	_it("mark_n", str(ORDER.size()))
	_it("distinct_stamps", str(_distinct(ORDER)))
	# per-frame: how many "a" marks landed between consecutive signals?
	var segs: Array = []
	var cur: Array = []
	for e in ORDER:
		var s := str(e)
		if s.begins_with("pf_sig@"):
			segs.append(cur)
			cur = []
		else:
			cur.append(s)
	segs.append(cur)
	_it("segs", _ord(segs.map(func(x: Array) -> String: return ",".join(x))))
	_pass()
