extends SceneTree
# r97 scout FROZEN probe — SceneTree groups / signal connect flags / call_deferred
# timing lattice.
# Battery launch shape:
#   godot --headless --path proj --script res://stree_lattice.gd -- --arm=<name> [--rev]
# Arm parse is the battery convention (OS.get_cmdline_user_args + "--arm=" prefix
# scan); every arm prints its own name on the PASS line, so a silent `_:` fallback
# is impossible to miss.  Prints `R97 <arm> <key>=<value>` diagnostics and one
# final `PASS stree_lattice <arm> <key>=<value> ...` line (the authorable signature).
# No RIDs / object ids / instance ids / addresses are ever printed (byte-stability):
# identities are node tags only.  Internal engine groups (`_root_canvas<id>`, …)
# are filtered out of every group listing.
#
# Measured laws this probe encodes (all [M], see reports/round-97/r97-scout.md):
#   L1 `get_nodes_in_group` returns a TREE-ORDER view (depth-first pre-order over
#      the SceneTree), NOT an insertion list: remove+re-add restores tree position,
#      reparent and move_child reorder the group, and the add_to_group call order is
#      irrelevant.  `get_first_node_in_group` is the first entry, `[-1]` the last.
#   L2 group-call order == that tree order; GROUP_CALL_REVERSE is its exact reverse;
#      `call_group` forwards args and silently skips nodes without the method.
#   L3 GROUP_CALL_DEFERRED runs the whole call at the deferred flush of the SAME
#      frame.  Its MEMBER LIST IS CAPTURED AT QUEUE TIME: a member that leaves the
#      group before the flush is still called; a node that joins after the queue call
#      is NOT called; a freed target is skipped.  `set_group_flags(DEFERRED, …)` uses
#      the same capture-time rule.
#   L4 GROUP_CALL_UNIQUE does NOT dedup two separate DIRECT identical calls.  With
#      GROUP_CALL_DEFERRED it DOES collapse identical queued calls within one frame;
#      the key expires at the frame end.
#   L5 signal emission is synchronous in CONNECT ORDER; disconnect+reconnect moves the
#      callable to the END of the connection list; `bind()` args are one entry.
#   L6 CONNECT_DEFERRED queues the callback at emit time into ONE global FIFO queue
#      (FIFO across signals and across objects) and it still runs if the connection is
#      disconnected before the flush.
#   L7 CONNECT_ONE_SHOT severs the connection AT EMIT TIME (a second emit in the same
#      frame is a no-op, deferred or not; the already-queued deferred call still runs).
#   L8 CONNECT_PERSIST is a serialization flag only — delivery is immediate.
#   L9 CONNECT_REFERENCE_COUNTED tolerates a duplicate connect of the same callable
#      (get_connections() still reports one entry) and needs N disconnects.
#  L10 `await <signal>` resumes AT EMIT TIME (same frame, before the deferred flush).
#      `await process_frame` resumes BEFORE the deferred flush, which runs after the
#      `process_frame` signal; `call_deferred` from inside a deferred callback runs in
#      the SAME flush.  `await physics_frame` is phase-coupled (its frame index is 1 or
#      2, bimodal) but a deferred call queued from its continuation always lands in the
#      same frame as that continuation.
#  L11 a deferred call is dropped if the target object is freed; it still runs for a
#      node that is merely out of the tree; `queue_free` in the same frame leaves the
#      deferred call running and the node gone by the next frame; `set_deferred` lands
#      at the same flush point.
#  L12 [A] FALSIFIED IN-SESSION: a SceneTree SCRIPT's own methods ARE resolvable by
#      `call_deferred` (measured: `call_deferred("_cb", log, "cd")` from inside a
#      deferred `_run()` lands at the same flush).  An earlier "Method not found"
#      observation was an edit artifact (the target method did not exist in that
#      revision), not an engine law.  This probe still routes its deferred calls
#      through a helper Node, which is the ordinary author shape.
#  L13 `set_group`/`set_group_flags` write real properties (deferred variant flushes at
#      the same point); a non-property name is silently skipped, as is an unknown group.
#  L14 `change_scene_to_file` completes asynchronously (not at the next
#      `process_frame`; measured by the 5th frame), `change_scene_to_packed` completes
#      at the next frame, `change_scene_to_node` within two frames; `current_scene` is
#      null until the frame the change completes and the new scene is added to root.

var arm := ""
var _rev := false
var _items: PackedStringArray = []
var ORDER: Array = []
var AWAITED: Array = []
var G: Node = null
var DFNODE: DF = null


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
		elif a == "--rev":
			_rev = true
	_run.call_deferred()


func _run() -> void:
	G = Node.new()
	G.name = "G"
	root.add_child(G)
	DFNODE = DF.new(ORDER)
	DFNODE.name = "DF"
	G.add_child(DFNODE)
	match arm:
		"census": await _arm_census()
		"group_order": await _arm_group_order()
		"group_flags": await _arm_group_flags()
		"group_lifecycle": await _arm_group_lifecycle()
		"group_setters": await _arm_group_setters()
		"signal_order": await _arm_signal_order()
		"signal_flags": await _arm_signal_flags()
		"defer_ladder": await _arm_defer_ladder()
		"defer_slots": await _arm_defer_slots()
		"defer_order": await _arm_defer_order()
		"scene_probe": await _arm_scene_probe()
		_: _fail("unknown_arm")


func _fail(reason: String) -> void:
	print("FAIL stree_lattice %s reason=%s" % [arm, reason])
	quit(1)


func _it(key: String, value: String) -> void:
	_items.append("%s=%s" % [key, value])
	print("R97 %s %s=%s" % [arm, key, value])


func _pass() -> void:
	print("PASS stree_lattice %s %s" % [arm, " ".join(_items)])
	quit()


func _frames(n: int) -> void:
	for i in n:
		await process_frame


func _v(v: Variant) -> String:
	if v is bool:
		return "true" if v else "false"
	if v is float:
		return "%.4f" % v
	if v is int:
		return str(v)
	if v is Vector2:
		return "(%.4f,%.4f)" % [v.x, v.y]
	if v is Array:
		return _ord(v)
	return str(v)


func _ord(a: Array) -> String:
	var parts: PackedStringArray = []
	for x in a:
		parts.append(str(x))
	return "[%s]" % ",".join(parts)


func _snap() -> String:
	var s := _ord(ORDER)
	ORDER.clear()
	return s


# ------------------------------------------------------------------ helpers

class DF extends Node:
	var log: Array = []
	func _init(l: Array = []) -> void:
		log = l
	func cb(tag: String) -> void:
		log.push_back(tag)
	func outer() -> void:
		log.push_back("outer")
		call_deferred("inner")
	func inner() -> void:
		log.push_back("inner")
	func slot_a() -> void:
		log.push_back("A")
	func slot_b() -> void:
		log.push_back("B")
	func slot_meta() -> void:
		set_meta("dfm", "z")


class LNode extends Node2D:
	var tag := ""
	var log: Array = []
	var paused_seen := 0
	func _init(l: Array = []) -> void:
		log = l
	var seq := 0
	func _push(k: String) -> void:
		seq += 1
		log.push_back("%s%d" % [k, seq])
	func _notification(what: int) -> void:
		if what == NOTIFICATION_PAUSED:
			paused_seen += 1
			log.push_back("%s.paused" % tag)
	signal sig_a
	signal sig_b
	var n := 0
	func on_a(_x: Variant = null) -> void:
		n += 1
		log.push_back("a%d" % n)
	func on_b(_x: Variant = null) -> void:
		n += 1
		log.push_back("b%d" % n)


func _mk(tag: String, parent: Node = null) -> LNode:
	var n := LNode.new(ORDER)
	n.name = tag
	n.tag = tag
	n.seq = 0
	(parent if parent != null else G).add_child(n)
	return n


func _tags(nodes: Array) -> Array:
	var out: Array = []
	for n in nodes:
		out.append(n.tag)
	return out


func _pub(groups: PackedStringArray) -> String:
	var out: Array = []
	for g in groups:
		if not str(g).begins_with("_"):
			out.append(str(g))
	out.sort()
	return _ord(out)


func it_valid(key: String, value: String) -> void:
	_it(key, value)


func _csname() -> String:
	if current_scene == null:
		return "null"
	return "%s tag=%s" % [str(current_scene.name), str(current_scene.get("tag"))]


func _tree_names() -> String:
	return _ord(root.get_children().map(func(n): return str(n.name)))


# ------------------------------------------------------------------ arms

func _arm_census() -> void:
	var gm: Array = []
	for m in ClassDB.class_get_method_list("SceneTree", true):
		var nm := str(m.get("name"))
		if nm.contains("group"):
			gm.append(nm)
	gm.sort()
	_it("group_meths", _ord(gm))
	var sg: Array = []
	for m in ClassDB.class_get_method_list("SceneTree", true):
		var nm := str(m.get("name"))
		if nm == "call_group" or nm == "call_group_flags" or nm == "notify_group" \
				or nm == "notify_group_flags" or nm == "set_group" or nm == "set_group_flags":
			var args: Array = []
			for a in m.get("args", []):
				args.append("%s:%s" % [str(a.get("name")), str(a.get("type"))])
			sg.append("%s(%s)" % [nm, ",".join(args)])
	sg.sort()
	_it("group_sigs", _ord(sg))
	_it("group_flags", "DEFAULT=%d REVERSE=%d DEFERRED=%d UNIQUE=%d" % [
		SceneTree.GROUP_CALL_DEFAULT, SceneTree.GROUP_CALL_REVERSE,
		SceneTree.GROUP_CALL_DEFERRED, SceneTree.GROUP_CALL_UNIQUE])
	_it("connect_flags", "DEFERRED=%d PERSIST=%d ONE_SHOT=%d REFERENCE_COUNTED=%d" % [
		Object.CONNECT_DEFERRED, Object.CONNECT_PERSIST, Object.CONNECT_ONE_SHOT,
		Object.CONNECT_REFERENCE_COUNTED])
	var nm2: Array = []
	for m in ClassDB.class_get_method_list("Node", true):
		var nm := str(m.get("name"))
		if nm.contains("group"):
			nm2.append(nm)
	nm2.sort()
	_it("node_group_meths", _ord(nm2))
	var om: Array = []
	for m in ClassDB.class_get_method_list("Object", true):
		var nm := str(m.get("name"))
		if nm.contains("deferred"):
			om.append(nm)
	om.sort()
	_it("object_defer_meths", _ord(om))
	var sm: Array = []
	for m in ClassDB.class_get_method_list("SceneTree", true):
		var nm := str(m.get("name"))
		if nm.begins_with("change_scene") or nm.begins_with("reload") or nm.begins_with("unload"):
			sm.append(nm)
	sm.sort()
	_it("scene_meths", _ord(sm))
	_it("tree_cls", get_class())
	_it("root_cls", root.get_class())
	_it("ticks", str(Engine.physics_ticks_per_second))
	_it("group_signal", "process_frame=%s physics_frame=%s" % [
		_v(has_signal("process_frame")), _v(has_signal("physics_frame"))])
	_pass()


func _arm_group_order() -> void:
	# L1 — the tree-order law, with a remove/re-add permutation and a reparent
	var a := _mk("a")
	var b := _mk("b")
	var c := _mk("c")
	var d := _mk("d")
	var add_order: Array = ["a", "b", "c", "d"]
	if _rev:
		add_order = ["d", "c", "b", "a"]
	for t in add_order:
		var n: LNode = G.get_node(NodePath(t))
		n.add_to_group("grp")
	_it("add_order", _ord(add_order))
	_it("t0", _ord(_tags(get_nodes_in_group("grp"))))
	_it("first", str(get_first_node_in_group("grp").tag))
	_it("last", str(get_nodes_in_group("grp")[-1].tag))
	_it("count", str(get_node_count_in_group("grp")))
	# remove two, re-add them in the OPPOSITE order
	b.remove_from_group("grp")
	d.remove_from_group("grp")
	_it("removed", _ord(_tags(get_nodes_in_group("grp"))))
	d.add_to_group("grp")
	b.add_to_group("grp")
	_it("readd_d_then_b", _ord(_tags(get_nodes_in_group("grp"))))
	_it("tree_order", _ord(G.get_children().map(func(n): return str(n.name))))
	# reparent c to the end of the tree
	G.remove_child(c)
	G.add_child(c)
	_it("after_reparent", _ord(_tags(get_nodes_in_group("grp"))))
	# move_child a to the end (tree order only, no group op)
	G.move_child(a, G.get_child_count() - 1)
	_it("after_move_child", _ord(_tags(get_nodes_in_group("grp"))))
	_it("tree_order2", _ord(G.get_children().map(func(n): return str(n.name))))
	# repeat reads are call-to-call stable
	_it("rep1", _ord(_tags(get_nodes_in_group("grp"))))
	_it("rep2", _ord(_tags(get_nodes_in_group("grp"))))
	# nested subtree: parent before its child (depth-first pre-order)
	var p := _mk("p")
	var ch := _mk("ch", p)
	p.add_to_group("grp")
	ch.add_to_group("grp")
	_it("nested", _ord(_tags(get_nodes_in_group("grp"))))
	_it("nested_tree", _ord(G.get_children().map(func(n): return str(n.name))))
	# duplicate add is idempotent
	b.add_to_group("grp")
	_it("dup_add", _ord(_tags(get_nodes_in_group("grp"))))
	_it("dup_count", str(get_node_count_in_group("grp")))
	# double remove is idempotent
	b.remove_from_group("grp")
	b.remove_from_group("grp")
	_it("double_remove", _ord(_tags(get_nodes_in_group("grp"))))
	# membership helpers
	_it("membership", "has=%s nothas=%s in=%s" % [_v(has_group("grp")), _v(has_group("nope")),
		_v(a.is_in_group("grp"))])
	_it("groups_a", _pub(a.get_groups()))
	_it("unknown", "%s first=%s" % [_ord(_tags(get_nodes_in_group("nope"))),
		"null" if get_first_node_in_group("nope") == null else "node"])
	_it("rev", _v(_rev))
	_pass()


func _arm_group_flags() -> void:
	# L2/L3/L4 — call order, reverse, deferred capture-time, unique dedup.
	# Each experiment runs on its OWN group so the member set is unambiguous.
	ORDER.clear()
	var a := _mk("a")
	var b := _mk("b")
	var c := _mk("c")
	for n in [a, b, c]:
		n.add_to_group("g1")
	call_group("g1", "_push", "direct")
	_it("direct", _snap())
	call_group_flags(SceneTree.GROUP_CALL_REVERSE, "g1", "_push", "rev")
	_it("reverse", _snap())
	# args are forwarded
	call_group("g1", "set_meta", "m2", 9)
	_it("args", "%s/%s" % [str(a.get_meta("m2")), str(b.get_meta("m2"))])
	# deferred: nothing now, the snapshot at the flush
	call_group_flags(SceneTree.GROUP_CALL_DEFERRED, "g1", "_push", "def")
	_it("deferred_t0", _snap())
	await process_frame
	_it("deferred_t1", _snap())
	call_group_flags(SceneTree.GROUP_CALL_DEFERRED | SceneTree.GROUP_CALL_REVERSE, "g1", "_push", "dr")
	await process_frame
	_it("def_rev_t1", _snap())
	# --- capture-time law: the member list is captured AT QUEUE TIME.
	#   d is a member when the call is queued and leaves before the flush  => still called
	#   e joins after the call is queued                                    => NOT called
	var d := _mk("d")
	var e := _mk("e")
	d.add_to_group("g2")
	call_group_flags(SceneTree.GROUP_CALL_DEFERRED, "g2", "_push", "cap")
	d.remove_from_group("g2")
	e.add_to_group("g2")
	it_valid("cap_members_t0", _ord(_tags(get_nodes_in_group("g2"))))
	await process_frame
	_it("cap_t1", _snap())
	it_connected("cap_d_membership", d.is_in_group("g2"))
	it_connected("cap_e_membership", e.is_in_group("g2"))
	# --- deferred reverse on a two-member group
	var f := _mk("f")
	var h := _mk("h")
	f.add_to_group("g3")
	h.add_to_group("g3")
	call_group_flags(SceneTree.GROUP_CALL_DEFERRED | SceneTree.GROUP_CALL_REVERSE, "g3", "_push", "drev")
	await process_frame
	it_valid("drev_members", _ord(_tags(get_nodes_in_group("g3"))))
	_it("drev_t1", _snap())
	# --- two queued calls flush FIFO
	var i1 := _mk("i")
	var j1 := _mk("j")
	i1.add_to_group("g4")
	j1.add_to_group("g4")
	call_group_flags(SceneTree.GROUP_CALL_DEFERRED, "g4", "_push", "q1")
	call_group_flags(SceneTree.GROUP_CALL_DEFERRED, "g4", "_push", "q2")
	await process_frame
	_it("fifo", _snap())
	# --- UNIQUE (direct) does NOT dedup two separate identical calls
	var k1 := _mk("k")
	k1.add_to_group("g5")
	call_group_flags(SceneTree.GROUP_CALL_UNIQUE, "g5", "_push", "u")
	it_valid("uniq_direct_1", _snap())
	call_group_flags(SceneTree.GROUP_CALL_UNIQUE, "g5", "_push", "u")
	it_valid("uniq_direct_2_same_args", _snap())
	call_group_flags(SceneTree.GROUP_CALL_UNIQUE, "g5", "_push", "u2")
	it_valid("uniq_direct_3_new_args", _snap())
	# --- UNIQUE + DEFERRED DOES dedup inside the frame; the key expires at the frame end
	var l1 := _mk("l")
	l1.add_to_group("g6")
	call_group_flags(SceneTree.GROUP_CALL_UNIQUE | SceneTree.GROUP_CALL_DEFERRED, "g6", "_push", "ud")
	call_group_flags(SceneTree.GROUP_CALL_UNIQUE | SceneTree.GROUP_CALL_DEFERRED, "g6", "_push", "ud")
	call_group_flags(SceneTree.GROUP_CALL_UNIQUE | SceneTree.GROUP_CALL_DEFERRED, "g6", "_push", "ud")
	it_valid("uniq_def_t0", _snap())
	await process_frame
	it_valid("uniq_def_t1", _snap())
	call_group_flags(SceneTree.GROUP_CALL_UNIQUE | SceneTree.GROUP_CALL_DEFERRED, "g6", "_push", "ud")
	await process_frame
	it_valid("uniq_def_next_frame", _snap())
	# --- plain DEFERRED does NOT dedup the same call twice
	var m1 := _mk("m")
	m1.add_to_group("g7")
	call_group_flags(SceneTree.GROUP_CALL_DEFERRED, "g7", "_push", "p")
	call_group_flags(SceneTree.GROUP_CALL_DEFERRED, "g7", "_push", "p")
	await process_frame
	it_valid("plain_deferred_twice", _snap())
	# --- set_group_flags DEFERRED uses the same capture-time law
	var n1 := _mk("n")
	var n2 := _mk("n2")
	n1.add_to_group("g8")
	n2.add_to_group("g8")
	n1.position = Vector2(1, 1)
	n2.position = Vector2(2, 2)
	set_group_flags(SceneTree.GROUP_CALL_DEFERRED, "g8", "position", Vector2(7, 7))
	n2.remove_from_group("g8")
	await process_frame
	it_valid("set_def_capture", "%s/%s" % [_v(n1.position), _v(n2.position)])
	# --- notify_group: Node._notification on every member
	var p := _mk("p")
	p.add_to_group("np")
	notify_group("np", Node.NOTIFICATION_PAUSED)
	it_valid("notify", _snap())
	it_paused(p.paused_seen)
	notify_group_flags(SceneTree.GROUP_CALL_REVERSE, "np", Node.NOTIFICATION_PAUSED)
	it_paused(p.paused_seen)
	# --- missing method on a group call is a silent skip
	call_group("g1", "no_such_method", 1)
	it_valid("missing_method", "silent")
	_it("rev", _v(_rev))
	_pass()


func it_paused(n: int) -> void:
	_it("paused_seen", str(n))


func _arm_group_lifecycle() -> void:
	var a := _mk("a")
	var b := _mk("b")
	a.add_to_group("grp")
	b.add_to_group("grp")
	# snapshot vs live view
	var snap := get_nodes_in_group("grp")
	var c := _mk("c")
	c.add_to_group("grp")
	_it("snapshot", _ord(_tags(snap)))
	_it("live", _ord(_tags(get_nodes_in_group("grp"))))
	# the root Window can carry groups too
	root.add_to_group("rootgrp")
	_it("root_in_group", _ord(get_nodes_in_group("rootgrp").map(func(n): return str(n.name))))
	_it("root_groups", _pub(root.get_groups()))
	root.remove_from_group("rootgrp")
	# parent removal does not cascade to children
	var p := _mk("p")
	var ch := _mk("ch", p)
	p.add_to_group("grp")
	ch.add_to_group("grp")
	_it("parent_child", _ord(_tags(get_nodes_in_group("grp"))))
	p.remove_from_group("grp")
	_it("child_stays", _ord(_tags(get_nodes_in_group("grp"))))
	# free() removes the member immediately; queue_free does too by the next frame
	a.free()
	_it("after_free", _ord(_tags(get_nodes_in_group("grp"))))
	b.queue_free()
	_it("after_queue_free_t0", _ord(_tags(get_nodes_in_group("grp"))))
	await process_frame
	_it("after_queue_free_t1", _ord(_tags(get_nodes_in_group("grp"))))
	# odd group names are accepted verbatim
	var s := _mk("s")
	s.add_to_group("a/b.c")
	_it("weird_group", _ord(_tags(get_nodes_in_group("a/b.c"))))
	_it("weird_groups", _pub(s.get_groups()))
	_it("multi_groups", "%s/%s" % [_pub(s.get_groups()), str(s.is_in_group("a/b.c"))])
	_pass()


func _arm_group_setters() -> void:
	# L13 — set_group / set_group_flags
	var a := _mk("a")
	var b := _mk("b")
	a.add_to_group("sg")
	b.add_to_group("sg")
	a.position = Vector2(1, 1)
	b.position = Vector2(2, 2)
	set_group("sg", "position", Vector2(9, 9))
	_it("set_group", "%s/%s" % [_v(a.position), _v(b.position)])
	set_group_flags(SceneTree.GROUP_CALL_REVERSE, "sg", "position", Vector2(3, 3))
	_it("set_group_flags", "%s/%s" % [_v(a.position), _v(b.position)])
	set_group_flags(SceneTree.GROUP_CALL_DEFERRED, "sg", "position", Vector2(4, 4))
	_it("set_group_deferred_t0", "%s/%s" % [_v(a.position), _v(b.position)])
	await process_frame
	_it("set_group_deferred_t1", "%s/%s" % [_v(a.position), _v(b.position)])
	set_group("sg", "no_such_prop", 1)
	_it("missing_prop", "silent")
	it_paused(a.paused_seen)
	# set_group with an out-of-group name is a no-op
	set_group("nope", "position", Vector2(0, 0))
	_it("unknown_group", "%s" % _v(a.position))
	_it("rev", _v(_rev))
	_pass()


func _arm_signal_order() -> void:
	# L5/L9 — synchronous emission in connect order; await resumes at emit time
	var s := _mk("s")
	s.sig_a.connect(s.on_a)
	s.sig_a.connect(s.on_b)
	s.sig_a.emit()
	_it("connect_order", _snap())
	_it("conn_n", str(s.sig_a.get_connections().size()))
	_it("flags_default", str(s.sig_a.get_connections()[0].get("flags", -1)))
	s.sig_a.disconnect(s.on_a)
	s.sig_a.emit()
	_it("after_disconnect", _snap())
	# reconnect moves the callable to the end of the connection list
	s.sig_a.disconnect(s.on_b)
	s.sig_a.connect(s.on_b)
	s.sig_a.connect(s.on_a)
	s.sig_a.emit()
	_it("reconnect_order", _snap())
	# method-name Callable identity
	s.sig_a.disconnect(Callable(s, "on_a"))
	_it("byname_connected", _v(s.sig_a.is_connected(Callable(s, "on_a"))))
	s.sig_a.connect(Callable(s, "on_a"))
	s.sig_a.emit()
	_it("byname_order", _snap())
	# bound callables keep connect order and are distinct entries
	var s2 := _mk("s2")
	s2.tag = "s2"
	s2.sig_a.connect(s2.on_a.bind("x"))
	s2.sig_a.connect(s2.on_b.bind("x"))
	s2.sig_a.emit()
	_it("bind_order", _snap())
	_it("bind_conn_n", str(s2.sig_a.get_connections().size()))
	# emit with no listeners is a no-op
	s2.sig_b.emit()
	_it("no_listeners", _snap())
	# await <signal> resumes at emit time
	var s3 := _mk("s3")
	s3.tag = "s3"
	await_probe(s3)
	_it("await_before", _ord(AWAITED))
	s3.sig_b.emit()
	_it("await_same_frame", _ord(AWAITED))
	await process_frame
	_it("await_next_frame", _ord(AWAITED))
	# two waiters on the same signal both resume in connect order
	await_probe2(s3)
	s3.sig_b.emit()
	_it("await_two", _ord(AWAITED))
	_it("rev", _v(_rev))
	_pass()


func await_probe(n: LNode) -> void:
	await n.sig_b
	AWAITED.push_back("w1")


func await_probe2(n: LNode) -> void:
	await n.sig_b
	AWAITED.push_back("w2")


func _arm_signal_flags() -> void:
	# L6/L7/L8 — DEFERRED / ONE_SHOT / PERSIST / REFERENCE_COUNTED
	var s := _mk("s")
	s.sig_a.connect(s.on_a)
	s.sig_a.connect(s.on_b, Object.CONNECT_DEFERRED)
	s.sig_a.emit()
	_it("mixed_t0", _snap())
	await process_frame
	_it("mixed_t1", _snap())
	# deferred: two emits in one frame queue two calls, FIFO
	var s2 := _mk("s2")
	s2.tag = "s2"
	s2.sig_a.connect(s2.on_a, Object.CONNECT_DEFERRED)
	s2.sig_a.emit()
	s2.sig_a.emit()
	_it("defer_two_t0", _snap())
	await process_frame
	_it("defer_two_t1", _snap())
	# queued deferred callback survives a disconnect before the flush
	var s3 := _mk("s3")
	s3.tag = "s3"
	s3.sig_a.connect(s3.on_a, Object.CONNECT_DEFERRED)
	s3.sig_a.emit()
	s3.sig_a.disconnect(s3.on_a)
	_it("disc_t0_connected", _v(s3.sig_a.is_connected(s3.on_a)))
	await process_frame
	_it("disc_t1_ran", _snap())
	# ONE_SHOT severs at emit time (immediate)
	var s4 := _mk("s4")
	s4.tag = "s4"
	s4.sig_a.connect(s4.on_a, Object.CONNECT_ONE_SHOT)
	s4.sig_a.emit()
	s4.sig_a.emit()
	_it("oneshot", _snap())
	_it("oneshot_connected", _v(s4.sig_a.is_connected(s4.on_a)))
	# ONE_SHOT + DEFERRED also severs at emit time; the queued call still runs
	var s5 := _mk("s5")
	s5.tag = "s5"
	s5.sig_a.connect(s5.on_a, Object.CONNECT_DEFERRED | Object.CONNECT_ONE_SHOT)
	s5.sig_a.emit()
	it_connected("osd_connected_t0", s5.sig_a.is_connected(s5.on_a))
	s5.sig_a.emit()
	_it("osd_second_emit", _snap())
	await process_frame
	_it("osd_flush", _snap())
	it_connected("osd_connected_t1", s5.sig_a.is_connected(s5.on_a))
	# REFERENCE_COUNTED tolerates a duplicate connect and needs N disconnects
	var s6 := _mk("s6")
	s6.tag = "s6"
	s6.sig_a.connect(s6.on_a, Object.CONNECT_REFERENCE_COUNTED)
	s6.sig_a.connect(s6.on_a, Object.CONNECT_REFERENCE_COUNTED)
	_it("rc_conn_n", str(s6.sig_a.get_connections().size()))
	s6.sig_a.emit()
	_it("rc_emit", _snap())
	s6.sig_a.disconnect(s6.on_a)
	it_connected("rc_after_one_disconnect", s6.sig_a.is_connected(s6.on_a))
	s6.sig_a.emit()
	_it("rc_emit2", _snap())
	# PERSIST is serialization-only
	var s7 := _mk("s7")
	s7.tag = "s7"
	s7.sig_a.connect(s7.on_a, Object.CONNECT_PERSIST)
	s7.sig_a.emit()
	_it("persist", _snap())
	_it("persist_flags", str(s7.sig_a.get_connections()[0].get("flags", -1)))
	# one global deferred queue, FIFO across signals and objects
	var s8 := _mk("s8")
	s8.tag = "s8"
	s8.sig_a.connect(s8.on_a, Object.CONNECT_DEFERRED)
	s8.sig_b.connect(s8.on_b, Object.CONNECT_DEFERRED)
	s8.sig_a.emit()
	s8.sig_b.emit()
	it_connected("cross_t0", s8.sig_a.is_connected(s8.on_a))
	await process_frame
	_it("cross_t1", _snap())
	# reversed emit order is visible in the flush order
	s8.sig_b.emit()
	s8.sig_a.emit()
	await process_frame
	_it("cross_rev_t1", _snap())
	_it("rev", _v(_rev))
	_pass()


func it_connected(key: String, v: bool) -> void:
	_it(key, _v(v))


func _arm_defer_ladder() -> void:
	# L10 — the timing ladder. `await process_frame` resumes BEFORE the deferred
	# flush; a deferred call queued anywhere in the frame runs after the
	# `process_frame` signal, in the same idle frame.
	var log: Array = []
	log.push_back("t0")
	DFNODE.call_deferred("cb", "cd")
	_ladder_co(log)
	log.push_back("t0_end")
	await process_frame
	log.push_back("after_pf1")
	await process_frame
	log.push_back("after_pf2")
	it_valid("ladder", _ord(log))
	it_valid("df_log", _ord(DFNODE.log))
	# control: with no process_frame await at all, the deferred call still lands
	DFNODE.log.clear()
	DFNODE.call_deferred("cb", "no_wait")
	await process_frame
	it_valid("no_wait", _ord(DFNODE.log))
	# physics_frame: its position in the frame is phase-dependent, but the
	# deferred call queued from its continuation always lands in the SAME frame
	# as that continuation, before the next `process_frame` signal.
	await _phys_probe()
	# The physics-continuation's frame INDEX is phase-coupled and bimodal (1 or 2
	# frames), so only the in-frame ordering is pinned: the deferred call queued
	# from the physics continuation lands in the SAME frame as that continuation.
	it_valid("phys_defer_same_frame", _v(PHYSR["defer_in_same_frame"]))
	it_valid("phys_co_in_log", _v(PHYSR["co_in_log"]))
	# a deferred call queued from inside a deferred callback runs in the SAME flush
	DFNODE.log.clear()
	DFNODE.call_deferred("outer")
	await process_frame
	it_valid("nested", _ord(DFNODE.log))
	await process_frame
	it_valid("nested_t1", _ord(DFNODE.log))
	_it("rev", _v(_rev))
	_pass()


var PHYSL: Array = []


func _ladder_co(log: Array) -> void:
	await process_frame
	log.push_back("co_pf")


func _phys_co() -> void:
	await physics_frame
	PHYSL.push_back("co_phys")
	DFNODE.call_deferred("cb", "after_phys")


var PHYSR: Dictionary = {}


func _phys_probe() -> void:
	PHYSL.clear()
	DFNODE.log.clear()
	PHYSR = {"co_in_log": false, "defer_in_same_frame": false}
	_phys_co()
	# sample the log from the process_frame signal, which fires AFTER the deferred
	# flush of the same frame (L10) — so if the deferred call landed at all, it is
	# already visible here in the frame that first shows the physics continuation.
	process_frame.connect(_phys_sample)
	for i in 4:
		await process_frame
		if PHYSR["co_in_log"] and PHYSR["defer_in_same_frame"]:
			break
	process_frame.disconnect(_phys_sample)


func _phys_sample() -> void:
	if "co_phys" in PHYSL:
		PHYSR["co_in_log"] = true
		if "after_phys" in DFNODE.log:
			PHYSR["defer_in_same_frame"] = true


func _arm_defer_slots() -> void:
	# L11/L12 — which targets survive, and what set_deferred does
	var s := _mk("s")
	s.tag = "s"
	s.call_deferred("_push", "node")
	DFNODE.call_deferred("cb", "tree")
	it_valid("t0", _snap())
	await process_frame
	it_valid("after_pf", _snap())
	# set_deferred lands at the same flush point
	var s2 := _mk("s2")
	s2.tag = "s2"
	s2.set_deferred("position", Vector2(5, 5))
	it_valid("set_deferred_t0", _v(s2.position == Vector2(5, 5)))
	await process_frame
	it_valid("set_deferred_t1", _v(s2.position == Vector2(5, 5)))
	# a node out of the tree still gets its deferred call
	var s3 := _mk("s3")
	s3.tag = "s3"
	G.remove_child(s3)
	s3.call_deferred("_push", "detached")
	await process_frame
	it_valid("detached", _snap())
	# queue_free: the deferred call still runs, the node is gone next frame
	var s4 := _mk("s4")
	s4.tag = "s4"
	s4.call_deferred("_push", "s4")
	s4.queue_free()
	await process_frame
	it_valid("queue_free", _snap())
	it_valid("queue_free_valid", _v(is_instance_valid(s4)))
	# immediate free: the deferred call is dropped
	var s5 := _mk("s5")
	s5.tag = "s5"
	s5.call_deferred("_push", "s5")
	s5.free()
	await process_frame
	it_valid("free_dropped", _snap())
	# FIFO within one object, and set_deferred on the same object
	DFNODE.log.clear()
	DFNODE.call_deferred("slot_a")
	DFNODE.call_deferred("slot_b")
	DFNODE.call_deferred("slot_meta")
	it_valid("slots_t0", _ord(DFNODE.log))
	await process_frame
	it_valid("slots_t1", _ord(DFNODE.log))
	it_valid("slot_meta", str(DFNODE.get_meta("dfm", "none")))
	# cleanup: the detached and queue-freed nodes are not under G any more
	if is_instance_valid(s3):
		s3.free()
	_it("rev", _v(_rev))
	_pass()


var DLOG: Array = []


func _tree_pf_cb() -> void:
	DLOG.push_back("pf_sig")


func _arm_defer_order() -> void:
	# L10 exact position: process_frame signal -> deferred flush -> next await
	process_frame.connect(_tree_pf_cb)
	DLOG.clear()
	DFNODE.log.clear()
	await process_frame
	DLOG.push_back("resume")
	it_valid("frame1", "%s | df=%s" % [_ord(DLOG), _ord(DFNODE.log)])
	DLOG.clear()
	DFNODE.log.clear()
	DFNODE.call_deferred("cb", "cd")
	DLOG.push_back("queued")
	await process_frame
	DLOG.push_back("resume2")
	it_valid("frame2", "%s | df=%s" % [_ord(DLOG), _ord(DFNODE.log)])
	# a deferred SIGNAL emitted mid-frame lands in the same flush
	var s := _mk("s")
	s.tag = "s"
	s.sig_a.connect(s.on_a, Object.CONNECT_DEFERRED)
	DLOG.clear()
	ORDER.clear()
	s.sig_a.emit()
	it_valid("emit_t0", "%s | ord=%s" % [_ord(DLOG), _ord(ORDER)])
	await process_frame
	it_valid("emit_t1", "%s | ord=%s" % [_ord(DLOG), _ord(ORDER)])
	# a deferred call queued from inside the process_frame signal still flushes
	DLOG.clear()
	DFNODE.log.clear()
	DFNODE.call_deferred("cb", "from_sig")
	DLOG.push_back("sig_frame")
	await process_frame
	it_valid("frame4", "%s | df=%s" % [_ord(DLOG), _ord(DFNODE.log)])
	# a deferred call queued at t0 of a frame and awaited twice
	DFNODE.log.clear()
	DFNODE.call_deferred("cb", "early")
	await process_frame
	it_valid("early_t1", _ord(DFNODE.log))
	process_frame.disconnect(_tree_pf_cb)
	_it("rev", _v(_rev))
	_pass()


func _arm_scene_probe() -> void:
	# SceneTree.change_scene_to_* under `--script` (the battery launch shape).
	# The loaded scene node is created by the tree at the END of the frame that
	# completes the change; no instance ids are printed (byte-stability).
	it_valid("current_scene_t0", "null" if current_scene == null else "set")
	change_scene_to_file("res://scene_a.tscn")
	it_valid("file_t0", _csname())
	it_valid("file_children_t0", str(root.get_child_count()))
	await process_frame
	it_valid("file_t1", _csname())
	await _frames(4)
	it_valid("file_t5", _csname())
	it_valid("file_children_t5", str(root.get_child_count()))
	var ps: PackedScene = load("res://scene_b.tscn")
	it_valid("packed_loaded", _v(ps != null))
	change_scene_to_packed(ps)
	it_valid("packed_t0", _csname())
	await process_frame
	it_valid("packed_t1", _csname())
	await _frames(2)
	it_valid("packed_t3", _csname())
	it_valid("packed_children_t3", str(root.get_child_count()))
	# a free-standing node change (no resource load)
	var ad := Node2D.new()
	ad.name = "AdHoc"
	change_scene_to_node(ad)
	it_valid("node_t0", _csname())
	await _frames(2)
	it_valid("node_t2", "AdHoc" if current_scene == ad else _csname())
	it_valid("node_children_t2", str(root.get_child_count()))
	it_valid("reload_exists", _v(has_method("reload_current_scene")))
	_it("rev", _v(_rev))
	_pass()
