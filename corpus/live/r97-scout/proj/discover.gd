extends SceneTree
# r97 scout DISCOVERY probe — SceneTree group/signal/call_deferred lattice.
# Launch: godot --headless --path proj --script res://discover.gd -- --arm=<name> [--rev]
# Each arm prints `D97 <arm> <key>=<value>` diagnostics; no final PASS line.
# Identities are node tags only (never RIDs / object ids / instance ids).

var arm := ""
var _rev := false
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
		"probe_boot": await _a_probe_boot()
		"probe_census": await _a_probe_census()
		"probe_group_order": await _a_group_order()
		"probe_group_forms": await _a_group_forms()
		"probe_group_flags": await _a_group_flags()
		"probe_group_lifecycle": await _a_group_lifecycle()
		"probe_group_reorder": await _a_group_reorder()
		"probe_group_dup": await _a_group_dup()
		"probe_sig_forms": await _a_sig_forms()
		"probe_sig_flags": await _a_sig_flags()
		"probe_defer_ladder": await _a_defer_ladder()
		"probe_defer_phys": await _a_defer_phys()
		"probe_defer_nest": await _a_defer_nest()
		"probe_defer_slots": await _a_defer_slots()
		"probe_defer_slots2": await _a_defer_slots2()
		"probe_defer_probe2": await _a_defer_probe2()
		"probe_defer_probe3": await _a_defer_probe3()
		"probe_defer_probe4": await _a_defer_probe4()
		"probe_defer_probe5": await _a_defer_probe5()
		"probe_defer_probe6": await _a_defer_probe6()
		"probe_defer_order": await _a_defer_order()
		"probe_set_group2": await _a_set_group2()
		"probe_scene_forms": await _a_scene_forms()
		"probe_scene_packed": await _a_scene_packed()
		"probe_scene_missing": await _a_scene_missing()
		"probe_scene_node": await _a_scene_node()
		_: _fail("unknown_arm")


func _fail(reason: String) -> void:
	print("FAIL discover %s reason=%s" % [arm, reason])
	quit(1)


func _it(key: String, value: String) -> void:
	print("D97 %s %s=%s" % [arm, key, value])


func _v(v: Variant) -> String:
	if v is bool:
		return "true" if v else "false"
	if v is float:
		return "%.4f" % v
	if v is int:
		return str(v)
	if v is Array:
		return "[%s]" % ",".join(PackedStringArray(v.map(func(x): return str(x))))
	return str(v)


func _frames(n: int) -> void:
	for i in n:
		await process_frame


# ------------------------------------------------------------------ helpers

class DF extends Node:
	var log: Array = []
	func _init(l: Array = []) -> void:
		log = l
	func cb(tag: String) -> void:
		log.push_back(tag)
	var seen: Array = []
	func take(a: Array) -> void:
		seen = a
		a.push_back("mut_in_cb")
		log.push_back("take%dtag" % a.size())
	func outer() -> void:
		log.push_back("outer")
		call_deferred("inner")
	func inner() -> void:
		log.push_back("inner")
	func tree_cb(tag: String) -> void:
		log.push_back(tag)
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
	func _push(k: String) -> void:
		log.push_back(k)
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


class Sig extends RefCounted:
	var tag := ""
	var log: Array = []
	var n := 0
	func _init(t: String, l: Array = []) -> void:
		tag = t
		log = l
	func on_x() -> void:
		n += 1
		log.push_back("%s.x%d" % [tag, n])
	func on_y() -> void:
		n += 1
		log.push_back("%s.y%d" % [tag, n])


func _mk(tag: String, parent: Node = null) -> LNode:
	var n := LNode.new(ORDER)
	n.name = tag
	n.tag = tag
	(parent if parent != null else G).add_child(n)
	return n


func _ord(tags: Array) -> String:
	var parts: PackedStringArray = []
	for t in tags:
		parts.append(str(t))
	return "[%s]" % ",".join(parts)


func _tags(nodes: Array) -> Array:
	var out: Array = []
	for n in nodes:
		out.append(n.tag)
	return out


func _reset() -> void:
	ORDER.clear()


func _snap() -> String:
	var s := _ord(ORDER)
	_reset()
	return s


# ------------------------------------------------------------------ arms

func _a_probe_boot() -> void:
	_it("boot", "true")
	_it("engine", Engine.get_version_info()["string"])
	_it("tree_cls", get_class())
	_it("root_cls", root.get_class())
	_it("root_name", root.name)
	_it("proc_ticks", str(Engine.physics_ticks_per_second))
	_it("max_fps", str(Engine.max_fps))
	await _frames(1)
	_it("frame1", "true")
	quit()


func _a_probe_census() -> void:
	var meths: Array = []
	for m in ClassDB.class_get_method_list("SceneTree", true):
		meths.append(str(m.get("name")))
	meths.sort()
	var gm: Array = []
	for m in meths:
		if str(m).contains("group"):
			gm.append(str(m))
	var sm: Array = []
	for m in meths:
		if str(m).contains("scene"):
			sm.append(str(m))
	var dm: Array = []
	for m in meths:
		if str(m).contains("defer") or str(m).contains("idle") or str(m).contains("process"):
			dm.append(str(m))
	_it("group_meths", _ord(gm))
	_it("scene_meths", _ord(sm))
	_it("defer_meths", _ord(dm))
	_it("group_flags", "DEFAULT=%d REVERSE=%d DEFERRED=%d UNIQUE=%d" % [
		SceneTree.GROUP_CALL_DEFAULT, SceneTree.GROUP_CALL_REVERSE,
		SceneTree.GROUP_CALL_DEFERRED, SceneTree.GROUP_CALL_UNIQUE])
	var props: Array = []
	for p in ClassDB.class_get_property_list("SceneTree", true):
		props.append(str(p.get("name")))
	_it("tree_props", _ord(props))
	var node_meths: Array = []
	for m in ClassDB.class_get_method_list("Node", true):
		var nm := str(m.get("name"))
		if nm.contains("group") or nm.contains("deferred"):
			node_meths.append(nm)
	node_meths.sort()
	_it("node_group_meths", _ord(node_meths))
	var obj_meths: Array = []
	for m in ClassDB.class_get_method_list("Object", true):
		var nm := str(m.get("name"))
		if nm.contains("deferred"):
			obj_meths.append(nm)
	obj_meths.sort()
	_it("object_defer_meths", _ord(obj_meths))
	_it("signal_flags", "Object.CONNECT_DEFERRED=%d ONE_SHOT=%d PERSIST=%d REFERENCE_COUNTED=%d" % [
		Object.CONNECT_DEFERRED, Object.CONNECT_ONE_SHOT, Object.CONNECT_PERSIST,
		Object.CONNECT_REFERENCE_COUNTED])
	var am: Array = []
	for m in ClassDB.class_get_method_list("SceneTreeTimer", true):
		am.append(str(m.get("name")))
	_it("timer_meths", _ord(am))
	_it("timer_cls", "SceneTreeTimer" if ClassDB.class_exists("SceneTreeTimer") else "absent")
	_it("scene_tree_timer_time_left", "present")
	quit()


func _a_group_order() -> void:
	var a := _mk("a")
	var b := _mk("b")
	var c := _mk("c")
	var add_order: Array = ["a", "b", "c"]
	if _rev:
		add_order = ["c", "b", "a"]
	for t in add_order:
		var n: LNode = G.get_node(NodePath(t))
		n.add_to_group("grp")
	_it("add_order", _ord(add_order))
	_it("nodes", _ord(_tags(get_nodes_in_group("grp"))))
	_it("first", str(get_first_node_in_group("grp").tag))
	_it("last", str(get_nodes_in_group("grp")[-1].tag))
	_it("is_in_group_a", _v(a.is_in_group("grp")))
	_it("groups_a", _pub(a.get_groups()))
	_it("count", str(get_nodes_in_group("grp").size()))
	# re-add after a remove: does it go to the end or back to its slot?
	b.remove_from_group("grp")
	_it("after_remove_b", _ord(_tags(get_nodes_in_group("grp"))))
	b.add_to_group("grp")
	_it("after_readd_b", _ord(_tags(get_nodes_in_group("grp"))))
	# a fresh node appends
	var d := _mk("d")
	d.add_to_group("grp")
	_it("after_d", _ord(_tags(get_nodes_in_group("grp"))))
	# get_node_count_in_group / has_group
	_it("count_api", str(get_node_count_in_group("grp")))
	_it("has_group", _v(has_group("grp")) + " " + _v(has_group("nope")))
	# empty / unknown group
	_it("unknown", _ord(_tags(get_nodes_in_group("nope"))))
	_it("first_unknown", "null" if get_first_node_in_group("nope") == null else "node")
	_it("count_unknown", str(get_node_count_in_group("nope")))
	quit()


func _a_group_reorder() -> void:
	# Is the group list a node-order view or an insertion list? Remove two, re-add
	# them in the opposite order, and also reparent a member.
	var a := _mk("a")
	var b := _mk("b")
	var c := _mk("c")
	var d := _mk("d")
	for n in [a, b, c, d]:
		n.add_to_group("grp")
	_it("t0", _ord(_tags(get_nodes_in_group("grp"))))
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
	# move_child (tree-order change only)
	G.move_child(a, G.get_child_count() - 1)
	_it("after_move_child", _ord(_tags(get_nodes_in_group("grp"))))
	_it("tree_order2", _ord(G.get_children().map(func(n): return str(n.name))))
	# repeat reads: is the returned order stable call-to-call?
	_it("rep1", _ord(_tags(get_nodes_in_group("grp"))))
	_it("rep2", _ord(_tags(get_nodes_in_group("grp"))))
	_it("rep3", _ord(_tags(get_nodes_in_group("grp"))))
	quit()


func _pub(groups: PackedStringArray) -> String:
	var out: PackedStringArray = []
	for g in groups:
		if not str(g).begins_with("_"):
			out.append(str(g))
	return _ord(out)


func _sorted_str(a: Array) -> Array:
	var c := a.duplicate()
	c.sort()
	return c


func _a_group_forms() -> void:
	var a := _mk("a")
	var b := _mk("b")
	a.add_to_group("grp")
	b.add_to_group("grp")
	a.set_meta("m", 1)
	b.set_meta("m", 2)
	# call_group direct: order + args + return discarded
	call_group("grp", "_push", "direct")
	_it("call_group_order", _snap())
	call_group("grp", "set_meta", "m2", 9)
	_it("call_args_a", str(a.get_meta("m2")))
	_it("call_args_b", str(b.get_meta("m2")))
	# notify_group: property set on every node
	call_group("grp", "set_meta", "nm", "x")
	call_group("grp", "set_meta", "nm", "y")
	_it("repeat_direct", _v(a.get_meta("nm") == "y" and b.get_meta("nm") == "y"))
	# notify_group(grp, notification) — delivered through Node._notification
	var p := _mk("p")
	p.add_to_group("np")
	notify_group("np", Node.NOTIFICATION_PAUSED)
	_it("notify_group_order", _snap())
	_it("notify_group_seen", str(p.paused_seen))
	notify_group("np", Node.NOTIFICATION_PAUSED)
	_it("notify_group_seen2", str(p.paused_seen))
	# reverse
	call_group_flags(SceneTree.GROUP_CALL_REVERSE, "grp", "_push", "rev")
	_it("reverse_order", _snap())
	# deferred
	call_group_flags(SceneTree.GROUP_CALL_DEFERRED, "grp", "_push", "deferred")
	_it("deferred_immediate", _snap())
	await process_frame
	_it("deferred_after_frame", _snap())
	# unique
	call_group_flags(SceneTree.GROUP_CALL_UNIQUE, "grp", "_push", "uniq")
	_it("unique_1", _snap())
	call_group_flags(SceneTree.GROUP_CALL_UNIQUE, "grp", "_push", "uniq")
	_it("unique_2_same_args", _snap())
	call_group_flags(SceneTree.GROUP_CALL_UNIQUE, "grp", "_push", "uniq2")
	_it("unique_3_new_args", _snap())
	call_group_flags(SceneTree.GROUP_CALL_UNIQUE, "grp", "_push", "uniq")
	_it("unique_4_after_new", _snap())
	# unique + reverse
	call_group_flags(SceneTree.GROUP_CALL_UNIQUE | SceneTree.GROUP_CALL_REVERSE, "grp", "_push", "ur")
	_it("unique_reverse", _snap())
	# unique + deferred
	call_group_flags(SceneTree.GROUP_CALL_UNIQUE | SceneTree.GROUP_CALL_DEFERRED, "grp", "_push", "ud")
	_it("unique_deferred_immediate", _snap())
	call_group_flags(SceneTree.GROUP_CALL_UNIQUE | SceneTree.GROUP_CALL_DEFERRED, "grp", "_push", "ud")
	await process_frame
	_it("unique_deferred_after", _snap())
	# missing method
	call_group("grp", "no_such_method", 1)
	_it("missing_method_noop", "true")
	# set_group / notify_group_flags / set_group_flags forms
	var q := _mk("q")
	q.add_to_group("sq")
	q.position = Vector2(0, 0)
	set_group("sq", "position", Vector2(7, 8))
	_it("set_group_pos", _v(q.position))
	call_group("sq", "set_meta", "sqm", "a")
	_it("sq_meta_pre", str(q.get_meta("sqm")))
	_it("set_group_arity", "probe")
	notify_group_flags(SceneTree.GROUP_CALL_REVERSE, "np", Node.NOTIFICATION_PAUSED)
	_it("notify_group_flags_rev", str(p.paused_seen))
	quit()


func _a_group_flags() -> void:
	var a := _mk("a")
	var b := _mk("b")
	var c := _mk("c")
	for n in [a, b, c]:
		n.add_to_group("grp")
	# deferred+reverse combination
	call_group_flags(SceneTree.GROUP_CALL_DEFERRED | SceneTree.GROUP_CALL_REVERSE, "grp", "_push", "dr")
	_it("def_rev_immediate", _snap())
	await process_frame
	_it("def_rev_after", _snap())
	# deferred: node freed before flush
	call_group_flags(SceneTree.GROUP_CALL_DEFERRED, "grp", "_push", "freed")
	c.queue_free()
	_it("pre_free", _snap())
	await process_frame
	_it("after_free_flush", _snap())
	_it("free_skipped", "true")
	# deferred: node leaves the group before flush
	var d := _mk("d")
	d.add_to_group("grp")
	call_group_flags(SceneTree.GROUP_CALL_DEFERRED, "grp", "_push", "left")
	d.remove_from_group("grp")
	await process_frame
	_it("after_leave_flush", _snap())
	# deferred: node joins after the call is queued
	var e := _mk("e")
	call_group_flags(SceneTree.GROUP_CALL_DEFERRED, "grp", "_push", "join")
	e.add_to_group("grp")
	await process_frame
	_it("after_join_flush", _snap())
	# deferred: order among two queued calls
	call_group_flags(SceneTree.GROUP_CALL_DEFERRED, "grp", "_push", "q1")
	call_group_flags(SceneTree.GROUP_CALL_DEFERRED, "grp", "_push", "q2")
	await process_frame
	_it("two_queued", _snap())
	# call_group from inside a group callback (reentrancy)
	call_group("grp", "_push", "outer")
	call_group("grp", "_push", "inner")
	_it("reentrant_direct", _snap())
	quit()


func _a_group_lifecycle() -> void:
	var a := _mk("a")
	var b := _mk("b")
	a.add_to_group("grp")
	b.add_to_group("grp")
	# duplicate add
	a.add_to_group("grp")
	_it("dup_add_nodes", _ord(_tags(get_nodes_in_group("grp"))))
	_it("dup_add_count", str(get_nodes_in_group("grp").size()))
	# remove twice
	a.remove_from_group("grp")
	a.remove_from_group("grp")
	_it("after_double_remove", _ord(_tags(get_nodes_in_group("grp"))))
	# add while iterating get_nodes_in_group snapshot
	var snapshot := get_nodes_in_group("grp")
	var c := _mk("c")
	c.add_to_group("grp")
	_it("snapshot_before_add", _ord(_tags(snapshot)))
	_it("live_after_add", _ord(_tags(get_nodes_in_group("grp"))))
	# groups on a freed node / parent-child
	var parent := _mk("parent")
	var child := _mk("child", parent)
	parent.add_to_group("grp")
	child.add_to_group("grp")
	_it("parent_child", _ord(_tags(get_nodes_in_group("grp"))))
	parent.remove_from_group("grp")
	_it("child_stays", _ord(_tags(get_nodes_in_group("grp"))))
	# group on the SceneTree root itself
	root.add_to_group("rootgrp")
	_it("root_in_group", _ord(get_nodes_in_group("rootgrp").map(func(n): return str(n.name))))
	root.remove_from_group("rootgrp")
	# call_group on a group with a node that has no such method: skipped silently
	call_group("grp", "_push", "mixed")
	_it("mixed", _snap())
	# group name with dots/slashes
	var s := _mk("s")
	s.add_to_group("a/b.c")
	_it("weird_group", _ord(_tags(get_nodes_in_group("a/b.c"))))
	_it("weird_groups", _pub(s.get_groups()))
	quit()


func _a_group_dup() -> void:
	var a := _mk("a")
	a.add_to_group("g1")
	a.add_to_group("g2")
	a.add_to_group("g3")
	_it("groups", _pub(a.get_groups()))
	_it("groups_sorted", _ord(_sorted_str(Array(a.get_groups()).filter(func(g): return not str(g).begins_with("_")))))
	call_group("g1", "_push", "g1")
	_it("g1", _snap())
	# node in two groups called twice by two calls
	call_group("g2", "_push", "g2")
	call_group("g3", "_push", "g3")
	_it("g2_g3", _snap())
	# get_groups on root
	_it("root_groups", _ord(_sorted_str(Array(root.get_groups()).filter(func(g): return not str(g).begins_with("_")))))
	_it("root_groups_live", _pub(root.get_groups()))
	quit()


func _a_sig_forms() -> void:
	var s := _mk("s")
	s.tag = "s"
	_it("class_has_sig_a", _v(s.has_signal("sig_a")))
	_it("sig_own", _ord(s.get_signal_list().map(func(d): return str(d.get("name"))).filter(func(x): return str(x).begins_with("sig_"))))
	s.sig_a.connect(s.on_a)
	s.sig_a.connect(s.on_b)
	_it("connected_n", str(s.sig_a.get_connections().size()))
	_it("is_connected_a", _v(s.sig_a.is_connected(s.on_a)))
	s.sig_a.emit()
	_it("emit_order", _snap())
	s.sig_a.emit()
	_it("emit2_order", _snap())
	s.sig_a.disconnect(s.on_a)
	s.sig_a.emit()
	_it("after_disconnect", _snap())
	# reconnect in the other order: does connect order or the original slot win?
	s.sig_a.disconnect(s.on_b)
	s.sig_a.connect(s.on_b)
	s.sig_a.connect(s.on_a)
	s.sig_a.emit()
	_it("reconnect_order", _snap())
	# method-name Callable identity
	s.sig_a.disconnect(Callable(s, "on_a"))
	_it("byname_is_connected", _v(s.sig_a.is_connected(Callable(s, "on_a"))))
	s.sig_a.connect(Callable(s, "on_a"))
	s.sig_a.emit()
	_it("byname_order", _snap())
	s.sig_b.emit()
	_it("no_listeners", _snap())
	_it("conn_flags_default", str(s.sig_a.get_connections()[0].get("flags", -1)))
	# await on a signal: emit-time resume or next-frame resume?
	var s2 := _mk("s2")
	s2.tag = "s2"
	await_probe(s2)
	_it("await_before", _ord(AWAITED))
	s2.sig_b.emit()
	_it("await_same_frame", _ord(AWAITED))
	await process_frame
	_it("await_next_frame", _ord(AWAITED))
	# a second waiter added after the first emit still resumes on the next emit
	await_probe2(s2)
	s2.sig_b.emit()
	_it("await2", _ord(AWAITED))
	quit()


func _a_sig_flags() -> void:
	var s := _mk("s")
	s.tag = "s"
	s.sig_a.connect(s.on_a)
	s.sig_a.connect(s.on_b, Object.CONNECT_DEFERRED)
	s.sig_a.emit()
	_it("mixed_immediate", _snap())
	await process_frame
	_it("mixed_after_frame", _snap())
	# deferred-only: emission queues the call; the frame flush runs it
	var s2 := _mk("s2")
	s2.tag = "s2"
	s2.sig_a.connect(s2.on_a, Object.CONNECT_DEFERRED)
	s2.sig_a.emit()
	s2.sig_a.emit()
	_it("defer_two_emits_immediate", _snap())
	await process_frame
	_it("defer_two_emits_after", _snap())
	# emit then disconnect before the flush: does the queued call still run?
	var s3 := _mk("s3")
	s3.tag = "s3"
	s3.sig_a.connect(s3.on_a, Object.CONNECT_DEFERRED)
	s3.sig_a.emit()
	s3.sig_a.disconnect(s3.on_a)
	_it("disc_before_flush_connected", _v(s3.sig_a.is_connected(s3.on_a)))
	await process_frame
	_it("disc_before_flush_after", _snap())
	# one shot immediate: second emit is a no-op
	var s4 := _mk("s4")
	s4.tag = "s4"
	s4.sig_a.connect(s4.on_a, Object.CONNECT_ONE_SHOT)
	_it("os_connected_t0", _v(s4.sig_a.is_connected(s4.on_a)))
	s4.sig_a.emit()
	_it("os_after_emit", _snap())
	_it("os_connected_after_emit", _v(s4.sig_a.is_connected(s4.on_a)))
	s4.sig_a.emit()
	_it("os_second_emit", _snap())
	# one shot + deferred: when is the connection severed?
	var s5 := _mk("s5")
	s5.tag = "s5"
	s5.sig_a.connect(s5.on_a, Object.CONNECT_DEFERRED | Object.CONNECT_ONE_SHOT)
	s5.sig_a.emit()
	_it("osd_connected_after_emit", _v(s5.sig_a.is_connected(s5.on_a)))
	s5.sig_a.emit()
	_it("osd_second_emit", _snap())
	await process_frame
	_it("osd_flush", _snap())
	_it("osd_connected_after_flush", _v(s5.sig_a.is_connected(s5.on_a)))
	# reference counted: the same callable may be connected twice
	var s6 := _mk("s6")
	s6.tag = "s6"
	s6.sig_a.connect(s6.on_a, Object.CONNECT_REFERENCE_COUNTED)
	s6.sig_a.connect(s6.on_a, Object.CONNECT_REFERENCE_COUNTED)
	_it("rc_conn_n", str(s6.sig_a.get_connections().size()))
	s6.sig_a.emit()
	_it("rc_order", _snap())
	s6.sig_a.disconnect(s6.on_a)
	_it("rc_after_one_disconnect_n", str(s6.sig_a.get_connections().size()))
	s6.sig_a.emit()
	_it("rc_after_one_disconnect", _snap())
	# persist: serialization flag, not a delivery modifier
	var s7 := _mk("s7")
	s7.tag = "s7"
	s7.sig_a.connect(s7.on_a, Object.CONNECT_PERSIST)
	s7.sig_a.emit()
	_it("persist_ran", _snap())
	_it("persist_flags", str(s7.sig_a.get_connections()[0].get("flags", -1)))
	# bound callable identity
	var s8 := _mk("s8")
	s8.tag = "s8"
	s8.sig_a.connect(s8.on_a.bind("x"))
	s8.sig_a.connect(s8.on_b.bind("x"))
	s8.sig_a.emit()
	_it("bind_order", _snap())
	_it("bind_conn_n", str(s8.sig_a.get_connections().size()))
	# two distinct signals with deferred connections: one FIFO queue?
	var s9 := _mk("s9")
	s9.tag = "s9"
	s9.sig_a.connect(s9.on_a, Object.CONNECT_DEFERRED)
	s9.sig_b.connect(s9.on_b, Object.CONNECT_DEFERRED)
	s9.sig_b.emit()
	s9.sig_a.emit()
	_it("cross_signal_immediate", _snap())
	await process_frame
	_it("cross_signal_after", _snap())
	quit()


func _a_defer_ladder() -> void:
	var log: Array = []
	log.push_back("t0")
	DFNODE.call_deferred("cb", "cd")
	_ladder_co(log)
	log.push_back("t0_end")
	await process_frame
	log.push_back("after_pf1")
	await process_frame
	log.push_back("after_pf2")
	_it("ladder", _ord(log))
	quit()


func _a_defer_phys() -> void:
	var log: Array = []
	DFNODE.call_deferred("cb", "cd")
	_phys_co(log)
	_it("t0", _ord(log))
	await process_frame
	_it("after_pf", _ord(log))
	await process_frame
	_it("after_pf2", _ord(log))
	quit()


func _phys_co(log: Array) -> void:
	await physics_frame
	log.push_back("co_phys")


func _ladder_co(log: Array) -> void:
	await process_frame
	log.push_back("co_pf")


func _a_defer_nest() -> void:
	var log: Array = []
	DFNODE.call_deferred("cb", "d1")
	_it("t0", _ord(log))
	await process_frame
	_it("after_pf", _ord(log))
	await process_frame
	_it("after_pf2", _ord(log))
	DFNODE.call_deferred("outer")
	await process_frame
	_it("after_nested", _ord(log))
	await process_frame
	_it("after_nested2", _ord(log))
	quit()


func _a_defer_slots() -> void:
	# call_deferred on a node vs on the SceneTree vs on a detached node vs a freed node
	var s := _mk("s")
	s.tag = "s"
	s.call_deferred("_push", "node")
	DFNODE.call_deferred("tree_cb", "tree")
	_it("t0", _snap())
	await process_frame
	_it("after_pf", _snap())
	# set_deferred timing
	var s2 := _mk("s2")
	s2.tag = "s2"
	s2.set_deferred("position", Vector2(5, 5))
	_it("set_deferred_t0", _v(s2.position == Vector2(5, 5)))
	await process_frame
	_it("set_deferred_t1", _v(s2.position == Vector2(5, 5)))
	# detached node: does a deferred call still run?
	var s3 := _mk("s3")
	s3.tag = "s3"
	G.remove_child(s3)
	s3.call_deferred("_push", "detached")
	await process_frame
	_it("detached_defer", _snap())
	# queue_free + deferred: which runs first, and is the call dropped?
	var s4 := _mk("s4")
	s4.tag = "s4"
	s4.call_deferred("_push", "s4")
	s4.queue_free()
	await process_frame
	_it("queue_free_defer", _snap())
	it_valid("s4_valid", is_instance_valid(s4))
	# immediate free + deferred: the call must be dropped (object gone)
	var s5 := _mk("s5")
	s5.tag = "s5"
	s5.call_deferred("_push", "s5")
	s5.free()
	await process_frame
	_it("free_defer", _snap())
	# nested call_deferred: same flush or next frame?
	DFNODE.call_deferred("outer")
	await process_frame
	_it("nest1", _snap())
	await process_frame
	_it("nest2", _snap())
	quit()


var DLOG: Array = []


func _tree_pf_cb() -> void:
	DLOG.push_back("pf_sig")


func _a_defer_order() -> void:
	# exact position of the deferred flush vs the process_frame signal vs an
	# `await process_frame` continuation, all in one frame.
	process_frame.connect(_tree_pf_cb)
	DLOG = []
	DFNODE.log = []
	await process_frame
	DLOG.push_back("resume")
	_it("frame1", "%s | df=%s" % [_ord(DLOG), _ord(DFNODE.log)])
	# second frame: queue a deferred call mid-frame
	DLOG = []
	DFNODE.log = []
	DFNODE.call_deferred("cb", "cd")
	DLOG.push_back("queued")
	await process_frame
	DLOG.push_back("resume2")
	_it("frame2", "%s | df=%s" % [_ord(DLOG), _ord(DFNODE.log)])
	# third frame: emit a deferred SIGNAL mid-frame
	var s := _mk("s")
	s.tag = "s"
	s.sig_a.connect(s.on_a, Object.CONNECT_DEFERRED)
	DLOG = []
	DFNODE.log = []
	ORDER.clear()
	s.sig_a.emit()
	_it("frame3_emit", "%s | df=%s ord=%s" % [_ord(DLOG), _ord(DFNODE.log), _ord(ORDER)])
	await process_frame
	_it("frame3_after", "%s | ord=%s" % [_ord(DLOG), _ord(ORDER)])
	# fourth frame: call_deferred queued from inside the process_frame signal cb
	DLOG = []
	DFNODE.log = []
	DFNODE.call_deferred("cb", "from_sig")
	DLOG.push_back("sig_frame")
	await process_frame
	_it("frame4", "%s | df=%s" % [_ord(DLOG), _ord(DFNODE.log)])
	process_frame.disconnect(_tree_pf_cb)
	quit()


func _a_set_group2() -> void:
	var a := _mk("a")
	var b := _mk("b")
	a.add_to_group("sg")
	b.add_to_group("sg")
	a.position = Vector2(1, 1)
	b.position = Vector2(2, 2)
	a.set_meta("v", "A0")
	b.set_meta("v", "B0")
	set_group("sg", "position", Vector2(9, 9))
	_it("set_group_pos", "%s/%s" % [_v(a.position), _v(b.position)])
	set_group("sg", "v", "Z")
	_it("set_group_meta", "%s/%s" % [str(a.get_meta("v")), str(b.get_meta("v"))])
	set_group_flags(SceneTree.GROUP_CALL_REVERSE, "sg", "position", Vector2(3, 3))
	_it("set_group_flags", "%s/%s" % [_v(a.position), _v(b.position)])
	set_group_flags(SceneTree.GROUP_CALL_DEFERRED, "sg", "position", Vector2(4, 4))
	_it("set_group_deferred_t0", "%s/%s" % [_v(a.position), _v(b.position)])
	await process_frame
	_it("set_group_deferred_t1", "%s/%s" % [_v(a.position), _v(b.position)])
	# missing property: silent or error?
	set_group("sg", "no_such_prop", 1)
	_it("set_group_missing_prop", "survived")
	quit()


func _a_defer_probe6() -> void:
	# is an Array argument copied at queue time, or is the log array itself a copy?
	DFNODE.log = []
	DFNODE.seen = []
	var a: Array = ["one"]
	_it("a_before", "%s size=%d" % [_ord(a), a.size()])
	DFNODE.call_deferred("take", a)
	a.push_back("two")
	_it("a_after_push", "%s size=%d" % [_ord(a), a.size()])
	await process_frame
	_it("a_final", "%s size=%d" % [_ord(a), a.size()])
	_it("seen_final", "%s size=%d" % [_ord(DFNODE.seen), DFNODE.seen.size()])
	_it("log_final", _ord(DFNODE.log))
	_it("same_ref", _v(a == DFNODE.seen))
	quit()


func _a_defer_probe5() -> void:
	# does call_deferred capture the ARGUMENT BY VALUE at queue time?
	DFNODE.log = []
	var local: Array = []
	DFNODE.call_deferred("cb", "x")
	local.push_back("local_only")
	await process_frame
	_it("arg_capture", _ord(DFNODE.log))
	_it("local_after", _ord(local))
	# capture by reference: a Node handed to a deferred call is the same instance
	var n := _mk("cap")
	n.call_deferred("_push", "cap")
	await process_frame
	_it("node_arg", _snap())
	# what does a deferred call do with an Array argument built at queue time?
	DFNODE.log = []
	var arr: Array = ["pre"]
	DFNODE.call_deferred("cb", "y")
	arr.push_back("post")
	await process_frame
	_it("arr_mutation", _ord(DFNODE.log))
	_it("arr_final", _ord(arr))
	quit()


func _a_defer_probe4() -> void:
	# ladder shape with a LOCAL log (the shape that did not show "cd")
	var log: Array = []
	DFNODE.call_deferred("cb", "L")
	_ladder_co(log)
	log.push_back("t0_end")
	await process_frame
	log.push_back("after_pf1")
	await process_frame
	log.push_back("after_pf2")
	_it("ladder_local", _ord(log))
	# and the same shape with the coroutine call AFTER the deferred queue call
	var log2: Array = []
	_ladder_co(log2)
	DFNODE.call_deferred("cb", "L2")
	log2.push_back("e2")
	await process_frame
	log2.push_back("a2")
	_it("ladder_local2", _ord(log2))
	quit()


func _a_defer_probe3() -> void:
	# exact ladder shape, but log into DFNODE.log (a property) instead of a local
	DFNODE.log = []
	DFNODE.call_deferred("cb", "cd")
	_ladder_co(DFNODE.log)
	DFNODE.log.push_back("t0_end")
	await process_frame
	DFNODE.log.push_back("after_pf1")
	await process_frame
	DFNODE.log.push_back("after_pf2")
	_it("ladder_prop", _ord(DFNODE.log))
	# and the same without the coroutine
	DFNODE.log = []
	DFNODE.call_deferred("cb", "cd2")
	DFNODE.log.push_back("end2")
	await process_frame
	DFNODE.log.push_back("after2")
	_it("noco", _ord(DFNODE.log))
	quit()


func _a_defer_probe2() -> void:
	_it("dfnode_valid", _v(is_instance_valid(DFNODE)))
	_it("dfnode_in_tree", _v(DFNODE.is_inside_tree()))
	_it("dfnode_has_cb", _v(DFNODE.has_method("cb")))
	_it("dfnode_name", str(DFNODE.name))
	DFNODE.call_deferred("cb", "p1")
	_it("after_call", _snap())
	await process_frame
	_it("after_pf", _snap())
	DFNODE.call_deferred("cb", "p2")
	await process_frame
	_it("after_pf2", _snap())
	DFNODE.call_deferred("cb", "p3")
	DFNODE.call_deferred("cb", "p4")
	await process_frame
	_it("after_pf3", _snap())
	await process_frame
	_it("after_pf4", _snap())
	quit()


func _a_defer_slots2() -> void:
	# same-object deferred slots: FIFO within one object, and set_deferred on it
	DFNODE.call_deferred("slot_a")
	DFNODE.call_deferred("slot_b")
	DFNODE.call_deferred("slot_meta")
	_it("t0", _snap())
	await process_frame
	_it("after_pf", _snap())
	_it("meta_set", str(DFNODE.get_meta("dfm", "none")))
	# a deferred call queued from a deferred callback on the same node
	DFNODE.call_deferred("outer")
	await process_frame
	_it("after_nest", _snap())
	quit()


func it_valid(key: String, v: bool) -> void:
	_it(key, _v(v))


func await_probe(n: LNode) -> void:
	await n.sig_b
	AWAITED.push_back("w1")


func await_probe2(n: LNode) -> void:
	await n.sig_b
	AWAITED.push_back("w2")


func _a_scene_forms() -> void:
	_it("current_scene_initial", "null" if current_scene == null else current_scene.name)
	_it("scene_file_initial", "null" if current_scene == null else str(current_scene.scene_file_path))
	it_scene_change()
	quit()


func it_scene_change() -> void:
	change_scene_to_file("res://scene_a.tscn")
	_it("after_change_call", _csname())
	_it("root_children", _ord(root.get_children().map(func(n): return str(n.name))))
	await process_frame
	_it("after_pf1", _csname())
	_it("root_children_pf1", _ord(root.get_children().map(func(n): return str(n.name))))
	await process_frame
	_it("after_pf2", _csname())
	_it("root_children_pf2", _ord(root.get_children().map(func(n): return str(n.name))))
	await _frames(4)
	_it("after_pf6", _csname())
	_it("root_children_pf6", _ord(root.get_children().map(func(n): return str(n.name))))
	quit()


func _csname() -> String:
	if current_scene == null:
		return "null"
	return "%s tag=%s" % [str(current_scene.name), str(current_scene.get("tag"))]


func _a_scene_packed() -> void:
	var ps: PackedScene = load("res://scene_b.tscn")
	_it("packed_loaded", _v(ps != null))
	change_scene_to_packed(ps)
	_it("after_call", _csname())
	_it("children", _ord(root.get_children().map(func(n): return str(n.name))))
	await process_frame
	_it("after_pf1", _csname())
	_it("children_pf1", _ord(root.get_children().map(func(n): return str(n.name))))
	await _frames(3)
	_it("after_pf4", _csname())
	_it("children_pf4", _ord(root.get_children().map(func(n): return str(n.name))))
	quit()


func _a_scene_missing() -> void:
	_it("err_seen_t0", "0")
	change_scene_to_file("res://scene_missing.tscn")
	_it("after_call", _csname())
	await process_frame
	_it("after_pf1", _csname())
	await _frames(2)
	_it("after_pf3", _csname())
	quit()


func _a_scene_node() -> void:
	var n := Node2D.new()
	n.name = "AdHoc"
	change_scene_to_node(n)
	_it("after_call", _csname())
	_it("adhoc_parent", "null" if n.get_parent() == null else str(n.get_parent().name))
	await process_frame
	_it("after_pf1", _csname())
	_it("adhoc_parent1", "null" if n.get_parent() == null else str(n.get_parent().name))
	await _frames(2)
	_it("after_pf3", _csname())
	quit()
