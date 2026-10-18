extends SceneTree
# r98 scout FROZEN probe — CanvasItem draw/transform lattice.
# Battery launch shape:
#   godot --headless --path proj --script res://canvas_lattice.gd -- --arm=<name>
# Arm parse is the battery convention (OS.get_cmdline_user_args + "--arm=" prefix
# scan); every arm prints its own name on the PASS line, so a silent `_:` fallback
# is impossible to miss.  Prints `R98 <arm> <key>=<value>` diagnostics and one
# final `PASS canvas_lattice <arm> <key=value> ...` line (the authorable signature).
# No RIDs / object ids / addresses / instance ids are printed (byte-stability).
#
# Measured laws this probe encodes (all [M], see reports/round-98/r98-scout.md):
#   L1  queue_redraw() coalesces to ONE _draw in the same process frame (end-of-frame
#       flush); a queue_redraw() from inside _draw() is swallowed (pending_update is
#       still set during the callback); hidden items queue nothing; show()/re-add redraw
#   L2  the legal draw contexts are _draw(), NOTIFICATION_DRAW handlers and `draw`
#       signal handlers (order: notif -> signal -> _draw); anywhere else the engine
#       refuses with a fixed ERROR line
#   L3  Node2D local transform = R(rotation) * K(skew) * S(scale) * T(position);
#       skew maps the y basis to (-sin k, cos k); the 4-arg Transform2D ctor matches
#   L4  global_rotation/global_skew are decomposition readbacks: under a non-uniform
#       parent scale a shear appears (global_skew != local skew); mirroring one axis
#       flips global_rotation; a zero scale reads back as a ~2e-5 epsilon, not 0
#   L5  global setters inverse-compose through the parent; `translate()` adds to
#       `position` in PARENT space (not the rotated local basis); local `rotation`
#       is stored raw while `global_rotation` is normalised to [-PI, PI]
#   L6  z_index/z_as_relative/y_sort_enabled/show_behind_parent are local readbacks;
#       the headless draw-callback order is the QUEUE/creation order, never a
#       z/y-sorted order (the sort lives in the renderer, unreadable headless)
#   L7  modulate/self_modulate are local readbacks (no effective-modulate getter);
#       parent writes do not change child readbacks; values are not clamped
#   L8  visibility is inherited: a hidden ancestor makes is_visible_in_tree() false
#       while the child's own `visible` stays true; each effective toggle emits one
#       NOTIFICATION_VISIBILITY_CHANGED + one visibility_changed (+ one `hidden`)
#   L9  clip_children is refused (ERROR, value unchanged) for >= CLIP_CHILDREN_MAX;
#       a negative value is stored as its uint32 cast (no error)
#  L10  transform notifications are opt-in (set_notify_transform /
#       set_notify_local_transform); reparenting into a CanvasLayer emits the full
#       re-entry set incl. ENTER_CANVAS+EXIT_CANVAS and TRANSFORM_CHANGED
#  L11  transform writes do NOT redraw; texture_filter/texture_repeat/oversampling/
#       skew/top_level writes DO queue a redraw

var arm := ""
var _items: PackedStringArray = []

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"census": await _arm_census()
		"queue": await _arm_queue()
		"draw_surface": await _arm_draw_surface()
		"draw_refusal": await _arm_draw_refusal()
		"vis_chain": await _arm_vis_chain()
		"clip": await _arm_clip()
		"zorder": await _arm_zorder()
		"modulate": await _arm_modulate()
		"xform_skew": await _arm_xform_skew()
		"xform_mirror": await _arm_xform_mirror()
		"xform_global": await _arm_xform_global()
		"notify": await _arm_notify()
		"draw_state": await _arm_draw_state()
		"redraw_triggers": await _arm_redraw_triggers()
		"redraw_context": await _arm_redraw_context()
		_: _fail("unknown_arm")

# --------------------------------------------------------------- utilities

func _fail(reason: String) -> void:
	print("FAIL canvas_lattice %s reason=%s" % [arm, reason])
	quit(1)

func _it(key: String, value: String) -> void:
	_items.append("%s=%s" % [key, value])
	print("R98 %s %s=%s" % [arm, key, value])

func _pass() -> void:
	print("PASS canvas_lattice %s %s" % [arm, " ".join(_items)])
	quit()

func _frames(n: int) -> void:
	for i in n:
		await process_frame

func _pf() -> int:
	return Engine.get_process_frames()

func _b(v: bool) -> String:
	return "1" if v else "0"

func _v2(v: Vector2) -> String:
	return "(%.4f,%.4f)" % [v.x, v.y]

func _tm(t: Transform2D) -> String:
	return "(%.4f,%.4f;%.4f,%.4f;%.4f,%.4f)" % [t.x.x, t.x.y, t.y.x, t.y.y, t.origin.x, t.origin.y]

func _col(c: Color) -> String:
	return "%.4f,%.4f,%.4f,%.4f" % [c.r, c.g, c.b, c.a]

# --------------------------------------------------------------- census

func _arm_census() -> void:
	var consts: Array = []
	for c in ["NOTIFICATION_DRAW", "NOTIFICATION_VISIBILITY_CHANGED", "NOTIFICATION_ENTER_CANVAS",
			"NOTIFICATION_EXIT_CANVAS", "NOTIFICATION_TRANSFORM_CHANGED",
			"NOTIFICATION_LOCAL_TRANSFORM_CHANGED", "CLIP_CHILDREN_DISABLED", "CLIP_CHILDREN_ONLY",
			"CLIP_CHILDREN_AND_DRAW", "CLIP_CHILDREN_MAX", "TEXTURE_FILTER_PARENT_NODE",
			"TEXTURE_REPEAT_PARENT_NODE", "OVERSAMPLING_WITH_SCALE_PARENT_NODE"]:
		consts.append("%s=%d" % [c, ClassDB.class_get_integer_constant("CanvasItem", c)])
	_it("consts", ",".join(consts))
	var props: Array = []
	for p in ClassDB.class_get_property_list("CanvasItem", true):
		props.append(str(p.get("name")))
	_it("props", ",".join(props))
	var drawm: Array = []
	for m in ClassDB.class_get_method_list("CanvasItem", true):
		var nm := str(m.get("name"))
		if nm.begins_with("draw_"):
			drawm.append(nm)
	_it("draw_n", str(drawm.size()))
	var sigs: Array = []
	for m in ClassDB.class_get_method_list("CanvasItem", true):
		var nm := str(m.get("name"))
		if nm in ["draw_set_transform", "draw_set_transform_matrix", "draw_rect", "draw_ellipse_arc",
				"draw_mesh", "draw_string", "draw_animation_slice"]:
			var parts: Array = []
			for a in m.get("args", []):
				parts.append("%s:%d" % [str(a.get("name")), int(a.get("type"))])
			sigs.append("%s(%s)" % [nm, ",".join(parts)])
	_it("sigs", "|".join(sigs))
	var n2 := Node2D.new()
	_it("defaults", "z=%d,zrel=%s,ysort=%s,behind=%s,light=%d,vislayer=%d,clip=%d,oversample=%d,texfilter=%d,texrepeat=%d" % [
		n2.z_index, _b(n2.is_z_relative()), _b(n2.is_y_sort_enabled()), _b(n2.is_draw_behind_parent_enabled()),
		n2.get_light_mask(), n2.get_visibility_layer(), n2.get_clip_children_mode(),
		n2.get_oversampling_with_scale(), n2.get_texture_filter(), n2.get_texture_repeat()])
	_it("has_pivot", _b(ClassDB.class_has_method("CanvasItem", "get_pivot_offset")))
	_it("has_global_modulate", _b(ClassDB.class_has_method("CanvasItem", "get_global_modulate")))
	_it("has_global_z", _b(ClassDB.class_has_method("CanvasItem", "get_global_z_index")))
	var rs: Array = []
	for m in ClassDB.class_get_method_list("RenderingServer", true):
		var nm := str(m.get("name"))
		if nm.begins_with("canvas_item_get"):
			rs.append(nm)
	_it("rs_getters", str(rs.size()))
	_it("notify_default", _b(n2.is_transform_notification_enabled()))
	_it("local_notify_default", _b(n2.is_local_transform_notification_enabled()))
	n2.free()
	_pass()

# --------------------------------------------------------------- queue

class QT:
	extends Node2D
	var draws := 0
	var events: Array = []
	var mode := ""
	var queue_from_draw := false
	func _draw() -> void:
		draws += 1
		events.append("d@pf%d" % Engine.get_process_frames())
		if queue_from_draw:
			queue_redraw()
	func _process(_dt: float) -> void:
		if mode == "proc":
			events.append("q@pf%d" % Engine.get_process_frames())
			queue_redraw()
			mode = ""

func _arm_queue() -> void:
	var t := QT.new()
	var pf_add := _pf()
	root.add_child(t)
	await _frames(1)
	_it("add_same", _b(t.events.size() == 1 and str(t.events[0]) == "d@pf%d" % pf_add))
	_it("add_n", str(t.draws))
	# queue from _process -> same frame, one draw
	t.events.clear()
	var d0 := t.draws
	t.mode = "proc"
	await _frames(1)
	var qpf := "?"
	if t.events.size() >= 1:
		qpf = str(str(t.events[0]).split("@")[1])
	_it("proc_same", _b(t.draws - d0 == 1 and t.events.size() >= 2 and str(t.events[0]).begins_with("q@") and str(t.events[1]) == "d@" + qpf))
	_it("proc_n", str(t.draws - d0))
	# coalescing: three queue_redraw in one frame -> one draw
	d0 = t.draws
	t.queue_redraw(); t.queue_redraw(); t.queue_redraw()
	await _frames(1)
	_it("coalesce_n", str(t.draws - d0))
	# queue from inside _draw is swallowed
	d0 = t.draws
	t.queue_from_draw = true
	t.queue_redraw()
	await _frames(2)
	_it("from_draw_n", str(t.draws - d0))
	t.queue_from_draw = false
	# hidden queue is suppressed; show redraws
	d0 = t.draws
	t.visible = false
	t.queue_redraw()
	await _frames(2)
	_it("hidden_n", str(t.draws - d0))
	t.visible = true
	await _frames(1)
	_it("show_n", str(t.draws - d0))
	# queue then hide before the flush -> suppressed
	d0 = t.draws
	t.queue_redraw()
	t.visible = false
	await _frames(1)
	_it("hide_before_flush_n", str(t.draws - d0))
	t.visible = true
	await _frames(1)
	# remove / re-add
	d0 = t.draws
	root.remove_child(t)
	t.queue_redraw()
	await _frames(1)
	_it("out_n", str(t.draws - d0))
	root.add_child(t)
	await _frames(1)
	_it("readd_n", str(t.draws - d0))
	# queue while out of tree then add
	d0 = t.draws
	root.remove_child(t)
	t.queue_redraw()
	await _frames(1)
	root.add_child(t)
	await _frames(1)
	_it("outadd_n", str(t.draws - d0))
	_it("events_tail", "|".join(t.events.slice(max(0, t.events.size() - 8))))
	_pass()

# --------------------------------------------------------------- draw_surface

class DS:
	extends Node2D
	var ok := 0
	var order: Array = []
	var rid_ok := false
	var xform_same := false
	var matrix_same := false
	var tex: Texture2D
	var font: Font
	func _call(f: Callable) -> void:
		f.call()
		ok += 1
	func _notification(what: int) -> void:
		if what == NOTIFICATION_DRAW:
			order.append("n")
			draw_rect(Rect2(0, 0, 2, 2), Color.RED)
	func _draw() -> void:
		order.append("d")
		var t0 := get_transform()
		rid_ok = get_canvas_item().is_valid()
		_call(func(): draw_line(Vector2.ZERO, Vector2(10, 10), Color.RED))
		_call(func(): draw_dashed_line(Vector2.ZERO, Vector2(10, 0), Color.RED))
		_call(func(): draw_polyline(PackedVector2Array([Vector2.ZERO, Vector2(5, 5)]), Color.RED))
		_call(func(): draw_polyline_colors(PackedVector2Array([Vector2.ZERO, Vector2(5, 5)]), PackedColorArray([Color.RED, Color.BLUE])))
		_call(func(): draw_ellipse_arc(Vector2.ZERO, 5.0, 3.0, 0.0, TAU, 8, Color.RED))
		_call(func(): draw_arc(Vector2.ZERO, 5.0, 0.0, TAU, 8, Color.RED))
		_call(func(): draw_multiline(PackedVector2Array([Vector2.ZERO, Vector2(5, 5), Vector2(10, 0), Vector2(15, 5)]), Color.RED))
		_call(func(): draw_multiline_colors(PackedVector2Array([Vector2.ZERO, Vector2(5, 5), Vector2(10, 0), Vector2(15, 5)]), PackedColorArray([Color.RED, Color.BLUE])))
		_call(func(): draw_rect(Rect2(0, 0, 10, 10), Color.RED))
		_call(func(): draw_rect(Rect2(0, 0, 10, 10), Color.RED, true))
		_call(func(): draw_circle(Vector2.ZERO, 5.0, Color.RED))
		_call(func(): draw_ellipse(Vector2.ZERO, 5.0, 3.0, Color.RED))
		if tex != null:
			_call(func(): draw_texture(tex, Vector2.ZERO))
			_call(func(): draw_texture_rect(tex, Rect2(0, 0, 8, 8), false))
			_call(func(): draw_texture_rect_region(tex, Rect2(0, 0, 8, 8), Rect2(0, 0, 4, 4)))
			_call(func(): draw_msdf_texture_rect_region(tex, Rect2(0, 0, 8, 8), Rect2(0, 0, 4, 4)))
			_call(func(): draw_lcd_texture_rect_region(tex, Rect2(0, 0, 8, 8), Rect2(0, 0, 4, 4)))
		_call(func(): draw_style_box(StyleBoxFlat.new(), Rect2(0, 0, 4, 4)))
		_call(func(): draw_primitive(PackedVector2Array([Vector2.ZERO, Vector2(5, 0), Vector2(0, 5)]), PackedColorArray([Color.RED, Color.RED, Color.RED]), PackedVector2Array()))
		_call(func(): draw_polygon(PackedVector2Array([Vector2.ZERO, Vector2(5, 0), Vector2(0, 5)]), PackedColorArray([Color.RED])))
		_call(func(): draw_colored_polygon(PackedVector2Array([Vector2.ZERO, Vector2(5, 0), Vector2(0, 5)]), Color.RED))
		if font != null:
			_call(func(): draw_string(font, Vector2.ZERO, "hi", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color.RED))
			_call(func(): draw_multiline_string(font, Vector2.ZERO, "hi\nthere", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, -1, Color.RED))
			_call(func(): draw_string_outline(font, Vector2.ZERO, "hi", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, 1, Color.RED))
			_call(func(): draw_multiline_string_outline(font, Vector2.ZERO, "hi\nthere", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, -1, 1, Color.RED))
			_call(func(): draw_char(font, Vector2.ZERO, "h", 8, Color.RED))
			_call(func(): draw_char_outline(font, Vector2.ZERO, "h", 8, 1, Color.RED))
		_call(func(): draw_mesh(QuadMesh.new(), tex))
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_2D
		mm.mesh = QuadMesh.new()
		mm.instance_count = 1
		_call(func(): draw_multimesh(mm, tex))
		_call(func(): draw_set_transform(Vector2(3, 4), 0.5, Vector2(2, 2)))
		_call(func(): draw_set_transform_matrix(Transform2D(0.5, Vector2(10, 20))))
		_call(func(): draw_animation_slice(0.0, 1.0, 0.0))
		_call(func(): draw_end_animation())
		xform_same = get_transform() == t0
		draw_set_transform_matrix(Transform2D(0.5, Vector2(1, 2)))
		matrix_same = get_transform() == t0

func _arm_draw_surface() -> void:
	var s := DS.new()
	var img := Image.create(4, 4, false, Image.FORMAT_RGBA8)
	img.fill(Color.RED)
	s.tex = ImageTexture.create_from_image(img)
	s.font = ThemeDB.fallback_font
	s.draw.connect(func(): s.order.append("s"); s.draw_rect(Rect2(0, 0, 3, 3), Color.RED))
	root.add_child(s)
	await _frames(2)
	_it("ok_n", str(s.ok))
	_it("rid", _b(s.rid_ok))
	_it("xform_same", _b(s.xform_same))
	_it("matrix_same", _b(s.matrix_same))
	_it("order", "".join(s.order.slice(0, 3)))
	_pass()

# --------------------------------------------------------------- draw_refusal

class DR:
	extends Node2D
	var refused := false
	var proc_refused := false
	var sig_ok := false
	var notif_ok := false
	var mode := ""
	var draws := 0
	func _notification(what: int) -> void:
		if what == NOTIFICATION_DRAW:
			draw_rect(Rect2(0, 0, 2, 2), Color.RED)
			notif_ok = true
	func _draw() -> void:
		draws += 1
		draw_rect(Rect2(0, 0, 1, 1), Color.RED)
	func _process(_dt: float) -> void:
		if mode == "proc":
			mode = ""
			draw_rect(Rect2(0, 0, 1, 1), Color.RED)
			proc_refused = true

func _arm_draw_refusal() -> void:
	var d := DR.new()
	d.draw.connect(func(): d.sig_ok = true; d.draw_rect(Rect2(0, 0, 3, 3), Color.RED))
	root.add_child(d)
	await _frames(2)
	# outside every legal context (this arm body runs deferred): must be refused
	d.draw_rect(Rect2(0, 0, 1, 1), Color.RED)
	d.refused = true
	_it("outside_refused", _b(d.refused))
	d.mode = "proc"
	await _frames(2)
	_it("proc_refused", _b(d.proc_refused))
	_it("sig_ok", _b(d.sig_ok))
	_it("notif_ok", _b(d.notif_ok))
	_it("draws", str(d.draws))
	_pass()

# --------------------------------------------------------------- vis_chain

class VC:
	extends Node2D
	var notif := {}
	var vis_sig := 0
	var hidden_sig := 0
	var draws := 0
	func _draw() -> void:
		draws += 1
	func _notification(what: int) -> void:
		notif[what] = int(notif.get(what, 0)) + 1

func _arm_vis_chain() -> void:
	var p := VC.new()
	var c := VC.new()
	root.add_child(p)
	p.add_child(c)
	c.visibility_changed.connect(func(): c.vis_sig += 1)
	c.hidden.connect(func(): c.hidden_sig += 1)
	await _frames(2)
	var n0 := int(c.notif.get(31, 0))
	var s0 := c.vis_sig
	var h0 := c.hidden_sig
	p.visible = false
	await _frames(1)
	_it("hide_in_tree", _b(c.is_visible_in_tree()))
	_it("hide_prop", _b(c.visible))
	_it("hide_notif", str(int(c.notif.get(31, 0)) - n0))
	_it("hide_sig", str(c.vis_sig - s0))
	_it("hide_hidden_sig", str(c.hidden_sig - h0))
	var d0 := c.draws
	c.queue_redraw()
	await _frames(2)
	_it("hidden_queue_n", str(c.draws - d0))
	p.visible = true
	await _frames(1)
	_it("restore_in_tree", _b(c.is_visible_in_tree()))
	_it("restore_n", str(c.draws - d0))
	c.hide()
	await _frames(1)
	_it("child_hide_in_tree", _b(c.is_visible_in_tree()))
	var n1 := int(c.notif.get(31, 0))
	var s1 := c.vis_sig
	c.hide()
	await _frames(1)
	_it("hide_noop", str(int(c.notif.get(31, 0)) - n1 + c.vis_sig - s1))
	c.show()
	await _frames(1)
	_it("show_in_tree", _b(c.is_visible_in_tree()))
	_it("show_notif", str(int(c.notif.get(31, 0)) - n1))
	_it("show_sig", str(c.vis_sig - s1))
	_it("draws_total", str(p.draws + c.draws))
	_pass()

# --------------------------------------------------------------- clip

func _arm_clip() -> void:
	var n := Node2D.new()
	root.add_child(n)
	await _frames(1)
	_it("default", str(n.get_clip_children_mode()))
	n.set_clip_children_mode(CanvasItem.CLIP_CHILDREN_ONLY)
	_it("only", str(n.get_clip_children_mode()))
	n.set_clip_children_mode(CanvasItem.CLIP_CHILDREN_AND_DRAW)
	_it("and_draw", str(n.get_clip_children_mode()))
	n.set_clip_children_mode(CanvasItem.CLIP_CHILDREN_ONLY)
	n.clip_children = 99
	_it("refused_stays", str(n.get_clip_children_mode()))
	n.set_clip_children_mode(CanvasItem.CLIP_CHILDREN_DISABLED)
	n.clip_children = -3
	_it("neg_cast", str(n.get_clip_children_mode()))
	n.set_visibility_layer(3)
	_it("vis_layer", str(n.get_visibility_layer()))
	_it("bit0", _b(n.get_visibility_layer_bit(0)))
	_it("bit1", _b(n.get_visibility_layer_bit(1)))
	_it("bit2", _b(n.get_visibility_layer_bit(2)))
	_it("light", str(n.get_light_mask()))
	_it("oversample", str(n.get_oversampling_with_scale()))
	_pass()

# --------------------------------------------------------------- zorder

class ZT:
	extends Node2D
	var tag := ""
	var sink: Array = []
	func _draw() -> void:
		sink.append(tag)

func _arm_zorder() -> void:
	var sink: Array = []
	var host := Node2D.new()
	root.add_child(host)
	var tags: Array = []
	for spec in [["A", -5], ["B", 0], ["C", 5]]:
		var z := ZT.new()
		z.tag = str(spec[0])
		z.sink = sink
		z.z_index = int(spec[1])
		host.add_child(z)
		tags.append(z)
	await _frames(2)
	_it("first", "".join(sink))
	_it("z_read", "%d,%d,%d" % [(tags[0] as ZT).z_index, (tags[1] as ZT).z_index, (tags[2] as ZT).z_index])
	_it("zrel", _b((tags[0] as ZT).is_z_relative()))
	host.z_index = 10
	_it("parent_isolated", _b((tags[0] as ZT).z_index == -5))
	host.z_as_relative = false
	_it("parent_flag_isolated", _b((tags[0] as ZT).is_z_relative()))
	host.y_sort_enabled = true
	_it("ysort", "%s,%s" % [_b(host.is_y_sort_enabled()), _b((tags[0] as ZT).is_y_sort_enabled())])
	_it("behind", _b((tags[0] as ZT).is_draw_behind_parent_enabled()))
	sink.clear()
	(tags[0] as ZT).move_to_front()
	_it("front_index", str((tags[0] as ZT).get_index()))
	sink.clear()
	for i in range(tags.size() - 1, -1, -1):
		(tags[i] as ZT).queue_redraw()
	await _frames(1)
	_it("requeue", "".join(sink))
	_pass()

# --------------------------------------------------------------- modulate

func _arm_modulate() -> void:
	var p := Node2D.new()
	var c := Node2D.new()
	root.add_child(p)
	p.add_child(c)
	await _frames(1)
	_it("defaults", "%s|%s" % [_col(p.get_modulate()), _col(p.get_self_modulate())])
	p.modulate = Color(0.5, 1, 2, 0.25)
	_it("p_modulate", _col(p.get_modulate()))
	_it("c_after_parent", _col(c.get_modulate()))
	p.self_modulate = Color(2, 0, 0, 1)
	_it("c_self_after_parent", _col(c.get_self_modulate()))
	c.self_modulate = Color(0, 0, 3, 1)
	_it("c_self", _col(c.get_self_modulate()))
	c.modulate = Color(4, -1, 0.5, 4)
	_it("raw_neg", _col(c.get_modulate()))
	p.visible = false
	_it("hidden_same", _col(c.get_modulate()))
	_it("getter", _b(ClassDB.class_has_method("CanvasItem", "get_global_modulate")))
	_it("upm", _b(c.get_use_parent_material()))
	_it("material_null", _b(p.get_material() == null))
	_pass()

# --------------------------------------------------------------- xform_skew

func _arm_xform_skew() -> void:
	var n := Node2D.new()
	root.add_child(n)
	await _frames(1)
	n.skew = PI / 4.0
	_it("m45", _tm(n.get_transform()))
	n.rotation = PI / 2.0
	_it("m90", _tm(n.get_transform()))
	n.rotation = 0.0
	n.skew = 0.5
	n.scale = Vector2(2, 3)
	_it("ms", _tm(n.get_transform()))
	_it("prop", "%.4f" % n.get_skew())
	_it("ctor", _b(n.get_transform() == Transform2D(0.0, Vector2(2, 3), 0.5, Vector2.ZERO)))
	var a := Transform2D(0.3, Vector2(2, 3), 0.5, Vector2.ZERO)
	var rk := Transform2D(0.3, Vector2.ONE, 0.0, Vector2.ZERO) * Transform2D(0.0, Vector2.ONE, 0.5, Vector2.ZERO) * Transform2D(0.0, Vector2(2, 3), 0.0, Vector2.ZERO)
	_it("rks", _b(a == rk))
	_pass()

# --------------------------------------------------------------- xform_mirror

func _arm_xform_mirror() -> void:
	var p := Node2D.new()
	p.rotation = 0.7
	p.scale = Vector2(2, 2)
	root.add_child(p)
	var c := Node2D.new()
	c.rotation = 0.4
	c.scale = Vector2(-1, 1)
	p.add_child(c)
	await _frames(1)
	_it("mx_grot", "%.4f" % c.get_global_rotation())
	_it("mx_gscale", _v2(c.get_global_scale()))
	_it("mx_gskew", "%.4f" % c.get_global_skew())
	c.scale = Vector2(1, -1)
	_it("my_grot", "%.4f" % c.get_global_rotation())
	_it("my_gscale", _v2(c.get_global_scale()))
	c.scale = Vector2(1, 1)
	p.scale = Vector2(3, 0.25)
	_it("nu_gskew", "%.4f" % c.get_global_skew())
	_it("nu_grot_deg", "%.4f" % c.get_global_rotation_degrees())
	p.scale = Vector2(2, 2)
	c.scale = Vector2(0, 0)
	_it("zero_gscale", "(%.6f,%.6f)" % [c.get_global_scale().x, c.get_global_scale().y])
	_it("zero_grot", "%.4f" % c.get_global_rotation())
	_it("zero_gskew", "%.4f" % c.get_global_skew())
	_pass()

# --------------------------------------------------------------- xform_global

func _arm_xform_global() -> void:
	var p := Node2D.new()
	p.rotation = 0.7
	p.scale = Vector2(2, 2)
	root.add_child(p)
	var c := Node2D.new()
	p.add_child(c)
	await _frames(1)
	c.global_position = Vector2(10, 10)
	_it("gp_local", _v2(c.position))
	c.global_rotation = 0.9
	_it("grot_local_deg", "%.4f" % c.rotation_degrees)
	c.global_scale = Vector2(2, 2)
	_it("gscale_local", _v2(c.scale))
	c.rotation = PI / 2.0
	c.position = Vector2.ZERO
	c.translate(Vector2(1, 0))
	_it("translate", _v2(c.position))
	c.position = Vector2.ZERO
	c.apply_scale(Vector2(2, 2))
	_it("apply_scale", _v2(c.scale))
	c.rotation = 4.0
	_it("norm", "%.4f" % c.global_rotation)
	c.rotation_degrees = 45.0
	_it("deg45", "%.4f" % c.rotation)
	c.top_level = true
	_it("top", _tm(c.get_global_transform()))
	_it("top_is", _b(c.is_set_as_top_level()))
	c.top_level = false
	c.rotation = 0.4
	c.scale = Vector2(1, 1)
	_it("rel", _tm(c.get_relative_transform_to_parent(p)))
	_it("edit_pivot", _v2(c._edit_get_pivot()))
	_pass()

# --------------------------------------------------------------- notify

class NT:
	extends Node2D
	var counts := {}
	func _notification(what: int) -> void:
		counts[what] = int(counts.get(what, 0)) + 1

func _delta_keys(a: Dictionary, b: Dictionary) -> String:
	var keys := {}
	for k in a.keys():
		keys[k] = true
	for k in b.keys():
		keys[k] = true
	var parts: Array = []
	for k in keys.keys():
		if int(b.get(k, 0)) - int(a.get(k, 0)) != 0:
			parts.append(int(k))
	parts.sort()
	return "[%s]" % ",".join(parts)

func _arm_notify() -> void:
	var p := NT.new()
	var c := NT.new()
	root.add_child(p)
	p.add_child(c)
	await _frames(1)
	_it("defaults", "%s,%s" % [_b(p.is_transform_notification_enabled()), _b(p.is_local_transform_notification_enabled())])
	var b := p.counts.duplicate(true)
	var cb := c.counts.duplicate(true)
	p.position = Vector2(1, 1)
	await _frames(1)
	_it("move_default", _delta_keys(b, p.counts))
	_it("move_default_c", _delta_keys(cb, c.counts))
	p.set_notify_transform(true)
	p.set_notify_local_transform(true)
	c.set_notify_transform(true)
	c.set_notify_local_transform(true)
	b = p.counts.duplicate(true)
	cb = c.counts.duplicate(true)
	p.position = Vector2(2, 2)
	await _frames(1)
	_it("move_p", _delta_keys(b, p.counts))
	_it("move_c", _delta_keys(cb, c.counts))
	b = p.counts.duplicate(true)
	cb = c.counts.duplicate(true)
	c.position = Vector2(3, 3)
	await _frames(1)
	_it("cmove_p", _delta_keys(b, p.counts))
	_it("cmove_c", _delta_keys(cb, c.counts))
	var cl := CanvasLayer.new()
	root.add_child(cl)
	await _frames(1)
	var t := NT.new()
	root.add_child(t)
	await _frames(1)
	var tb := t.counts.duplicate(true)
	t.reparent(cl)
	await _frames(1)
	_it("reparent", _delta_keys(tb, t.counts))
	_it("cl_node", _b(t.get_canvas_layer_node() != null))
	tb = t.counts.duplicate(true)
	t.reparent(root)
	await _frames(1)
	_it("reparent_back", _delta_keys(tb, t.counts))
	_it("cl_node_back", _b(t.get_canvas_layer_node() != null))
	_pass()

# --------------------------------------------------------------- draw_state

class DX:
	extends Node2D
	var same := false
	var matrix_same := false
	func _draw() -> void:
		var t0 := get_transform()
		draw_set_transform(Vector2(5, 5), 0.5, Vector2(2, 2))
		same = get_transform() == t0
		draw_set_transform_matrix(Transform2D(0.5, Vector2(1, 2)))
		matrix_same = get_transform() == t0

func _arm_draw_state() -> void:
	var d := DX.new()
	d.position = Vector2(7, 8)
	d.rotation = 0.25
	root.add_child(d)
	await _frames(2)
	_it("same", _b(d.same))
	_it("matrix_same", _b(d.matrix_same))
	_it("canvas", _tm(d.get_canvas_transform()))
	_it("wc", _tm(d.get_global_transform_with_canvas()))
	_it("screen_eq", _b(d.get_screen_transform() == d.get_global_transform_with_canvas()))
	_it("vp", _v2(d.get_viewport_rect().size))
	_it("mcl", _v2(d.make_canvas_position_local(Vector2(10, 10))))
	_it("mouse", _v2(d.get_local_mouse_position()))
	_pass()

# --------------------------------------------------------------- redraw_triggers

class RT:
	extends Node2D
	var draws := 0
	func _draw() -> void:
		draws += 1

func _arm_redraw_triggers() -> void:
	var t := RT.new()
	root.add_child(t)
	await _frames(2)
	var out: Array = []
	var probe := func(label: String, f: Callable) -> void:
		var d0 := t.draws
		f.call()
		await _frames(2)
		out.append("%s=%d" % [label, t.draws - d0])
	await probe.call("idle", func(): pass)
	await probe.call("pos", func(): t.position = Vector2(5, 5))
	await probe.call("rot", func(): t.rotation = 0.5)
	await probe.call("scale", func(): t.scale = Vector2(2, 2))
	await probe.call("skew", func(): t.skew = 0.2)
	await probe.call("modulate", func(): t.modulate = Color(0.5, 0.5, 0.5, 1))
	await probe.call("self_modulate", func(): t.self_modulate = Color(0.5, 0.5, 0.5, 1))
	await probe.call("material", func(): t.material = null)
	await probe.call("z", func(): t.z_index = 3)
	await probe.call("zrel", func(): t.z_as_relative = false)
	await probe.call("ysort", func(): t.y_sort_enabled = true)
	await probe.call("behind", func(): t.show_behind_parent = true)
	await probe.call("vislayer", func(): t.set_visibility_layer(2))
	await probe.call("lightmask", func(): t.light_mask = 2)
	await probe.call("clip", func(): t.clip_children = CanvasItem.CLIP_CHILDREN_ONLY)
	await probe.call("upm", func(): t.use_parent_material = true)
	await probe.call("shader", func(): t.set_instance_shader_parameter("x", 1.0))
	await probe.call("texfilter", func(): t.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST)
	await probe.call("texrepeat", func(): t.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED)
	await probe.call("oversample", func(): t.set_oversampling_with_scale(CanvasItem.OVERSAMPLING_WITH_SCALE_ENABLED))
	await probe.call("toplevel", func(): t.top_level = true)
	await probe.call("rename", func(): t.name = "renamed")
	await probe.call("visbit", func(): t.set_visibility_layer_bit(3, false))
	await probe.call("hide", func(): t.hide())
	await probe.call("show", func(): t.show())
	_it("table", ",".join(out))
	_pass()

# --------------------------------------------------------------- redraw_context

class RC:
	extends Node2D
	var draws := 0
	func _draw() -> void:
		draws += 1

func _arm_redraw_context() -> void:
	# Context-dependent redraw: after an oversampling change + a scale write, the
	# NEXT transform write DOES queue a redraw (the clean-context table above says
	# it does not).  Sequence and control both frozen.
	var a := RC.new()
	root.add_child(a)
	await _frames(3)
	a.set_oversampling_with_scale(CanvasItem.OVERSAMPLING_WITH_SCALE_ENABLED)
	await _frames(3)
	a.scale = Vector2(2, 2)
	await _frames(3)
	var a0 := a.draws
	a.skew = 0.2
	await _frames(4)
	_it("trigger_n", str(a.draws - a0))
	var b := RC.new()
	root.add_child(b)
	await _frames(3)
	b.scale = Vector2(2, 2)
	await _frames(3)
	var b0 := b.draws
	b.skew = 0.2
	await _frames(4)
	_it("control_n", str(b.draws - b0))
	# and a non-transform write in the same context does not
	var c := RC.new()
	root.add_child(c)
	await _frames(3)
	c.set_oversampling_with_scale(CanvasItem.OVERSAMPLING_WITH_SCALE_ENABLED)
	await _frames(3)
	c.scale = Vector2(2, 2)
	await _frames(3)
	var c0 := c.draws
	c.z_index = 5
	await _frames(4)
	_it("nontransform_n", str(c.draws - c0))
	_pass()
