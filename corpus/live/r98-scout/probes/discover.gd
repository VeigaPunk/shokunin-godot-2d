extends SceneTree
# r98 scout DISCOVERY probe — CanvasItem draw/transform lattice.
# Launch: godot --headless --path proj --script res://discover.gd -- --arm=<name>
# Discovery only: prints raw readbacks, including deliberately-invalid calls whose
# engine ERROR text is recorded (never used in a frozen row).

var arm := ""

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"qtime": await _arm_qtime()
		"surface": await _arm_surface()
		"vis": await _arm_vis()
		"zorder": await _arm_zorder()
		"modulate": await _arm_modulate()
		"xform2": await _arm_xform2()
		"notify2": await _arm_notify2()
		"drawx": await _arm_drawx()
		"qtime2": await _arm_qtime2()
		"contexts": await _arm_contexts()
		"triggers": await _arm_triggers()
		"vis2": await _arm_vis2()
		"notify3": await _arm_notify3()
		"qtime3": await _arm_qtime3()
		"triggers2": await _arm_triggers2()
		_: print("FAIL discover unknown_arm=%s" % arm); quit(1)

func _p(k: String, v: Variant) -> void:
	print("D %s %s=%s" % [arm, k, str(v)])

func _tm(t: Transform2D) -> String:
	return "(%.6f,%.6f;%.6f,%.6f;%.6f,%.6f)" % [t.x.x, t.x.y, t.y.x, t.y.y, t.origin.x, t.origin.y]

func _v2(v: Vector2) -> String:
	return "(%.6f,%.6f)" % [v.x, v.y]

func _frames(n: int) -> void:
	for i in n:
		await process_frame

# --------------------------------------------------------------- qtime

class Tracer:
	extends Node2D
	var draws := 0
	var draw_at: Array = []
	var proc_at: Array = []
	var notif := {}
	var draw_sig := 0
	var do_queue_in_process := false
	var do_queue_in_draw := false
	func _draw() -> void:
		draws += 1
		draw_at.append("%d/%d" % [Engine.get_process_frames(), Engine.get_physics_frames()])
		if do_queue_in_draw and draws < 4:
			queue_redraw()
	func _process(_d: float) -> void:
		proc_at.append(Engine.get_process_frames())
		if do_queue_in_process:
			queue_redraw()
	func _notification(what: int) -> void:
		notif[what] = int(notif.get(what, 0)) + 1

func _mk_tracer() -> Tracer:
	var t := Tracer.new()
	t.draw.connect(func(): t.draw_sig += 1)
	return t

func _arm_qtime() -> void:
	var t := _mk_tracer()
	_p("pf_at_init", Engine.get_process_frames())
	root.add_child(t)
	_p("pf_after_add", Engine.get_process_frames())
	_p("draws_after_add", t.draws)
	await process_frame
	_p("f1", Engine.get_process_frames())
	_p("draws_f1", t.draws)
	_p("draw_at_f1", t.draw_at)
	await process_frame
	_p("draws_f2", t.draws)
	# queue in _process (frame N) -> draw when?
	t.do_queue_in_process = true
	await process_frame
	_p("f3", Engine.get_process_frames())
	_p("draws_f3", t.draws)
	_p("proc_at", t.proc_at)
	t.do_queue_in_process = false
	await process_frame
	_p("draws_f4", t.draws)
	# queue from inside _draw
	t.do_queue_in_draw = true
	t.queue_redraw()
	await process_frame
	_p("draws_f5", t.draws)
	await process_frame
	_p("draws_f6", t.draws)
	t.do_queue_in_draw = false
	await process_frame
	_p("draws_f7", t.draws)
	# hidden before the queued flush
	var d0 := t.draws
	t.queue_redraw()
	t.visible = false
	await process_frame
	_p("hide_before_flush_delta", t.draws - d0)
	_p("hide_vis", t.visible)
	await process_frame
	_p("hidden_idle_delta", t.draws - d0)
	t.visible = true
	await process_frame
	_p("show_delta", t.draws - d0)
	# out of tree
	t.get_parent().remove_child(t)
	t.queue_redraw()
	_p("out_of_tree_inside", t.is_inside_tree())
	await process_frame
	var d1 := t.draws
	root.add_child(t)
	await process_frame
	_p("readd_delta", t.draws - d1)
	# queue while not in tree then add
	root.remove_child(t)
	t.queue_redraw()
	await process_frame
	var d2 := t.draws
	root.add_child(t)
	await process_frame
	_p("queue_outside_then_add_delta", t.draws - d2)
	_p("notif", t.notif)
	_p("draw_sig", t.draw_sig)
	print("PASS discover qtime draws=%d" % t.draws)
	quit()

# --------------------------------------------------------------- surface

class Surface:
	extends Node2D
	var ok := 0
	var fail := 0
	var calls: Array = []
	var canvas_rid_valid := false
	var tex: Texture2D
	var font: Font
	func _call(name: String, f: Callable) -> void:
		calls.append(name)
		f.call()
		ok += 1
	func _draw() -> void:
		canvas_rid_valid = get_canvas_item().is_valid()
		_call("line", func(): draw_line(Vector2.ZERO, Vector2(10, 10), Color.RED))
		_call("dashed", func(): draw_dashed_line(Vector2.ZERO, Vector2(10, 0), Color.RED))
		_call("polyline", func(): draw_polyline(PackedVector2Array([Vector2.ZERO, Vector2(5, 5)]), Color.RED))
		_call("polyline_colors", func(): draw_polyline_colors(PackedVector2Array([Vector2.ZERO, Vector2(5, 5)]), PackedColorArray([Color.RED, Color.BLUE])))
		_call("ellipse_arc", func(): draw_ellipse_arc(Vector2.ZERO, 5.0, 3.0, 0.0, TAU, 8, Color.RED))
		_call("arc", func(): draw_arc(Vector2.ZERO, 5.0, 0.0, TAU, 8, Color.RED))
		_call("multiline", func(): draw_multiline(PackedVector2Array([Vector2.ZERO, Vector2(5, 5), Vector2(10, 0), Vector2(15, 5)]), Color.RED))
		_call("multiline_colors", func(): draw_multiline_colors(PackedVector2Array([Vector2.ZERO, Vector2(5, 5), Vector2(10, 0), Vector2(15, 5)]), PackedColorArray([Color.RED, Color.BLUE])))
		_call("rect", func(): draw_rect(Rect2(0, 0, 10, 10), Color.RED))
		_call("rect_filled", func(): draw_rect(Rect2(0, 0, 10, 10), Color.RED, true))
		_call("circle", func(): draw_circle(Vector2.ZERO, 5, Color.RED))
		_call("ellipse", func(): draw_ellipse(Vector2.ZERO, 5.0, 3.0, Color.RED))
		if tex != null:
			_call("texture", func(): draw_texture(tex, Vector2.ZERO))
			_call("texture_rect", func(): draw_texture_rect(tex, Rect2(0, 0, 8, 8), false))
			_call("texture_rect_region", func(): draw_texture_rect_region(tex, Rect2(0, 0, 8, 8), Rect2(0, 0, 4, 4)))
			_call("msdf", func(): draw_msdf_texture_rect_region(tex, Rect2(0, 0, 8, 8), Rect2(0, 0, 4, 4)))
			_call("lcd", func(): draw_lcd_texture_rect_region(tex, Rect2(0, 0, 8, 8), Rect2(0, 0, 4, 4)))
		_call("primitive", func(): draw_primitive(PackedVector2Array([Vector2.ZERO, Vector2(5, 0), Vector2(0, 5)]), PackedColorArray([Color.RED, Color.RED, Color.RED]), PackedVector2Array()))
		_call("polygon", func(): draw_polygon(PackedVector2Array([Vector2.ZERO, Vector2(5, 0), Vector2(0, 5)]), PackedColorArray([Color.RED])))
		_call("colored_polygon", func(): draw_colored_polygon(PackedVector2Array([Vector2.ZERO, Vector2(5, 0), Vector2(0, 5)]), Color.RED))
		if font != null:
			_call("string", func(): draw_string(font, Vector2.ZERO, "hi", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color.RED))
			_call("multiline_string", func(): draw_multiline_string(font, Vector2.ZERO, "hi\nthere", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, -1, Color.RED))
			_call("string_outline", func(): draw_string_outline(font, Vector2.ZERO, "hi", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, 1, Color.RED))
			_call("multiline_string_outline", func(): draw_multiline_string_outline(font, Vector2.ZERO, "hi\nthere", HORIZONTAL_ALIGNMENT_LEFT, -1, 8, -1, 1, Color.RED))
			_call("char", func(): draw_char(font, Vector2.ZERO, "h", 8, Color.RED))
			_call("char_outline", func(): draw_char_outline(font, Vector2.ZERO, "h", 8, 1, Color.RED))
		_call("mesh", func(): draw_mesh(QuadMesh.new(), tex))
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_2D
		mm.mesh = QuadMesh.new()
		mm.instance_count = 1
		_call("multimesh", func(): draw_multimesh(mm, tex))
		_call("set_transform", func(): draw_set_transform(Vector2(3, 4), 0.5, Vector2(2, 2)))
		_call("set_transform_matrix", func(): draw_set_transform_matrix(Transform2D(0.5, Vector2(10, 20))))
		_call("anim_slice", func(): draw_animation_slice(0.0, 1.0, 0.0))
		_call("anim_end", func(): draw_end_animation())

func _arm_surface() -> void:
	var s := Surface.new()
	var img := Image.create(4, 4, false, Image.FORMAT_RGBA8)
	img.fill(Color.RED)
	s.tex = ImageTexture.create_from_image(img)
	s.font = ThemeDB.fallback_font
	root.add_child(s)
	await process_frame
	_p("ok", s.ok)
	_p("calls", s.calls)
	_p("canvas_rid_valid", s.canvas_rid_valid)
	# outside _draw -> expected error text
	s.draw_rect(Rect2(0, 0, 1, 1), Color.RED)
	# invalid args inside a second draw
	var bad := Surface.new()
	bad.font = null
	root.add_child(bad)
	await process_frame
	_p("bad_ok", bad.ok)
	# invalid arg probes (each is an engine-side refusal; discovery only)
	var inv := Inv.new()
	root.add_child(inv)
	await process_frame
	_p("inv", inv.log)
	print("PASS discover surface ok=%d" % s.ok)
	quit()

class Inv:
	extends Node2D
	var log: Array = []
	func _draw() -> void:
		draw_arc(Vector2.ZERO, 5.0, 0.0, TAU, 0, Color.RED)
		log.append("arc0_done")
		draw_polygon(PackedVector2Array([Vector2.ZERO, Vector2(1, 1)]), PackedColorArray([Color.RED]))
		log.append("poly2_done")
		draw_line(Vector2.ZERO, Vector2.ZERO, Color.RED)
		log.append("line0_done")
		draw_rect(Rect2(0, 0, 1, 1), Color.RED, false, -1.0)
		log.append("rect_negwidth_done")

# --------------------------------------------------------------- vis

class Vis:
	extends Node2D
	var notif := {}
	var vis_sig := 0
	var hidden_sig := 0
	var draws := 0
	func _draw() -> void:
		draws += 1
	func _notification(what: int) -> void:
		notif[what] = int(notif.get(what, 0)) + 1

func _arm_vis() -> void:
	var p := Vis.new()
	var c := Vis.new()
	root.add_child(p)
	p.add_child(c)
	c.visibility_changed.connect(func(): c.vis_sig += 1)
	c.hidden.connect(func(): c.hidden_sig += 1)
	await _frames(2)
	_p("initial_p_vis_in_tree", p.is_visible_in_tree())
	_p("initial_c_vis_in_tree", c.is_visible_in_tree())
	var dc0 := c.draws
	p.visible = false
	await _frames(2)
	_p("parent_hidden_c_in_tree", c.is_visible_in_tree())
	_p("parent_hidden_c_visible_prop", c.visible)
	_p("c_notif_vis", c.notif.get(31, 0))
	_p("c_vis_sig", c.vis_sig)
	_p("c_hidden_sig", c.hidden_sig)
	c.queue_redraw()
	await _frames(2)
	_p("hidden_ancestor_draw_delta", c.draws - dc0)
	p.visible = true
	await _frames(2)
	_p("restored_c_in_tree", c.is_visible_in_tree())
	_p("restored_draw_delta", c.draws - dc0)
	c.hide()
	await _frames(1)
	_p("c_hidden_in_tree", c.is_visible_in_tree())
	_p("c_vis_sig2", c.vis_sig)
	_p("c_hidden_sig2", c.hidden_sig)
	c.show()
	await _frames(1)
	_p("c_show_in_tree", c.is_visible_in_tree())
	# clip / layers readbacks
	_p("clip_default", c.get_clip_children_mode())
	c.set_clip_children_mode(CanvasItem.CLIP_CHILDREN_ONLY)
	_p("clip_only", c.get_clip_children_mode())
	c.set_clip_children_mode(CanvasItem.CLIP_CHILDREN_AND_DRAW)
	_p("clip_and_draw", c.get_clip_children_mode())
	c.clip_children = 99
	_p("clip_invalid99", c.get_clip_children_mode())
	c.set_visibility_layer(3)
	_p("vis_layer3", c.get_visibility_layer())
	_p("vis_layer_bit0", c.get_visibility_layer_bit(0))
	_p("vis_layer_bit1", c.get_visibility_layer_bit(1))
	_p("light_mask_default", c.get_light_mask())
	_p("oversampling_default", c.get_oversampling_with_scale())
	# visibility layer on the CanvasItem vs Viewport
	_p("vp_canvas_layers", root.canvas_cull_mask)
	_p("notif_p", p.notif)
	_p("notif_c", c.notif)
	print("PASS discover vis ok=true")
	quit()

# --------------------------------------------------------------- zorder

class ZTag:
	extends Node2D
	var tag := ""
	var sink: Array = []
	var draws := 0
	func _draw() -> void:
		draws += 1
		sink.append("%s@pf%d" % [tag, Engine.get_process_frames()])

func _arm_zorder() -> void:
	var sink: Array = []
	var host := Node2D.new()
	host.name = "host"
	root.add_child(host)
	var tags: Array = []
	for spec in [["A", -5, false], ["B", 0, false], ["C", 5, false]]:
		var z := ZTag.new()
		z.tag = str(spec[0])
		z.sink = sink
		z.z_index = int(spec[1])
		z.show_behind_parent = bool(spec[2])
		host.add_child(z)
		tags.append(z)
	await _frames(2)
	_p("zorder_first", sink.duplicate())
	_p("host_z", host.z_index)
	_p("childA_z", (tags[0] as ZTag).z_index)
	_p("childA_z_relative", (tags[0] as ZTag).is_z_relative())
	host.z_index = 10
	_p("childA_z_after_parent10", (tags[0] as ZTag).z_index)
	host.z_as_relative = false
	_p("childA_z_after_parent_nonrel", (tags[0] as ZTag).z_index)
	_p("childA_zrel_after", (tags[0] as ZTag).is_z_relative())
	# y_sort
	host.y_sort_enabled = true
	_p("y_sort_host", host.is_y_sort_enabled())
	_p("y_sort_child", (tags[0] as ZTag).is_y_sort_enabled())
	# move_to_front
	sink.clear()
	(tags[0] as ZTag).move_to_front()
	(tags[0] as ZTag).queue_redraw()
	await _frames(2)
	_p("after_move_to_front", sink.duplicate())
	_p("child_index_A", (tags[0] as ZTag).get_index())
	# re-queue all in reverse order
	sink.clear()
	for i in range(tags.size() - 1, -1, -1):
		(tags[i] as ZTag).queue_redraw()
	await _frames(2)
	_p("requeue_reverse", sink.duplicate())
	print("PASS discover zorder ok=true")
	quit()

# --------------------------------------------------------------- modulate

func _arm_modulate() -> void:
	var p := Node2D.new()
	var c := Node2D.new()
	root.add_child(p)
	p.add_child(c)
	_p("p_modulate_default", p.get_modulate())
	_p("p_self_modulate_default", p.get_self_modulate())
	p.modulate = Color(0.5, 1, 2, 0.25)
	_p("p_modulate", p.get_modulate())
	_p("c_modulate_after_parent", c.get_modulate())
	p.self_modulate = Color(2, 0, 0, 1)
	_p("p_self_modulate", p.get_self_modulate())
	_p("c_self_modulate_after_parent", c.get_self_modulate())
	c.self_modulate = Color(0, 0, 3, 1)
	_p("c_self_modulate", c.get_self_modulate())
	c.modulate = Color(4, -1, 0.5, 4)
	_p("c_modulate_negative", c.get_modulate())
	p.visible = false
	_p("c_modulate_parent_hidden", c.get_modulate())
	var ci: CanvasItem = c
	_p("has_global_modulate", ci.has_method("get_global_modulate"))
	_p("use_parent_material_default", c.get_use_parent_material())
	p.material = null
	_p("p_material", p.get_material())
	print("PASS discover modulate ok=true")
	quit()

# --------------------------------------------------------------- xform2

func _arm_xform2() -> void:
	var n := Node2D.new()
	root.add_child(n)
	# skew convention
	n.position = Vector2.ZERO
	n.rotation = 0.0
	n.scale = Vector2(1, 1)
	n.skew = 0.0
	n.skew = PI / 4.0
	_p("skew_pi4", _tm(n.get_transform()))
	_p("skew_prop", n.get_skew())
	n.rotation = PI / 2.0
	_p("rot90_skew", _tm(n.get_transform()))
	n.rotation = 0.0
	n.skew = 0.5
	n.scale = Vector2(2, 3)
	_p("skew_scale", _tm(n.get_transform()))
	_p("skew_ctor_eq", n.get_transform() == Transform2D(0.0, Vector2(2, 3), 0.5, Vector2.ZERO))
	# skew with rotation order check: r * k * s vs k * r * s
	var a := Transform2D(0.3, Vector2(2, 3), 0.5, Vector2.ZERO)
	var rk := Transform2D(0.3, Vector2.ONE, 0.0, Vector2.ZERO) * Transform2D(0.0, Vector2.ONE, 0.5, Vector2.ZERO) * Transform2D(0.0, Vector2(2, 3), 0.0, Vector2.ZERO)
	_p("ctor_a", _tm(a))
	_p("rks", _tm(rk))
	_p("ctor_eq_rks", a == rk)
	# negative scale
	var p := Node2D.new()
	p.rotation = 0.7
	p.scale = Vector2(2, 2)
	root.add_child(p)
	var c := Node2D.new()
	c.rotation = 0.4
	c.scale = Vector2(-1, 1)
	p.add_child(c)
	_p("mirror_g", _tm(c.get_global_transform()))
	_p("mirror_grot", c.get_global_rotation())
	_p("mirror_gskew", c.get_global_skew())
	_p("mirror_gscale", c.get_global_scale())
	c.scale = Vector2(1, -1)
	_p("mirror_y_grot", c.get_global_rotation())
	_p("mirror_y_gscale", c.get_global_scale())
	c.scale = Vector2(1, 1)
	# non-uniform parent
	p.scale = Vector2(3, 0.25)
	_p("nonuni_gskew", c.get_global_skew())
	_p("nonuni_grot_deg", c.get_global_rotation_degrees())
	p.scale = Vector2(2, 2)
	# zero scale
	c.scale = Vector2(0, 0)
	_p("zero_gscale", c.get_global_scale())
	_p("zero_grot", c.get_global_rotation())
	_p("zero_gskew", c.get_global_skew())
	c.scale = Vector2(1, 1)
	# relative transform
	_p("rel", _tm(c.get_relative_transform_to_parent(p)))
	# translate / apply_scale semantics
	c.position = Vector2.ZERO
	c.rotation = PI / 2.0
	c.scale = Vector2(1, 1)
	c.translate(Vector2(1, 0))
	_p("translate_after", _v2(c.position))
	c.position = Vector2.ZERO
	c.apply_scale(Vector2(2, 2))
	_p("apply_scale_after", _v2(c.scale))
	# global setters under rotated parent
	c.position = Vector2.ZERO
	c.rotation = 0.0
	c.scale = Vector2(1, 1)
	c.global_position = Vector2(10, 10)
	_p("set_gp_local", _v2(c.position))
	c.global_rotation = 0.9
	_p("set_grot_local_deg", c.rotation_degrees)
	c.global_scale = Vector2(2, 2)
	_p("set_gscale_local", _v2(c.scale))
	# rotation normalization
	c.rotation = 4.0
	_p("local_rot_raw", c.rotation)
	_p("global_rot_norm", c.global_rotation)
	_p("global_rot_deg_norm", c.global_rotation_degrees)
	# rotation_degrees setter
	c.rotation_degrees = 45.0
	_p("rot_deg45_rad", c.rotation)
	# top level
	c.top_level = true
	_p("top_gt", _tm(c.get_global_transform()))
	_p("top_is", c.is_set_as_top_level())
	c.top_level = false
	# pivot probes (CanvasItem)
	_p("edit_pivot", c._edit_get_pivot())
	_p("edit_rect", c._edit_get_rect())
	print("PASS discover xform2 ok=true")
	quit()

# --------------------------------------------------------------- notify2

class NTag:
	extends Node2D
	var tag := ""
	var counts := {}
	var local_counts := {}
	var set_notify := false
	func _notification(what: int) -> void:
		counts[what] = int(counts.get(what, 0)) + 1
	func _ready() -> void:
		if set_notify:
			set_notify_transform(true)

func _arm_notify2() -> void:
	var p := NTag.new()
	p.tag = "p"
	var c := NTag.new()
	c.tag = "c"
	root.add_child(p)
	p.add_child(c)
	await _frames(2)
	p.set_notify_transform(true)
	p.set_notify_local_transform(true)
	c.set_notify_transform(true)
	c.set_notify_local_transform(true)
	_p("p_notify_enabled", p.is_transform_notification_enabled())
	_p("p_local_enabled", p.is_local_transform_notification_enabled())
	var base := p.counts.duplicate(true)
	var cbase := c.counts.duplicate(true)
	p.position = Vector2(1, 2)
	_p("p_counts_delta", _delta(base, p.counts))
	_p("c_counts_delta", _delta(cbase, c.counts))
	base = p.counts.duplicate(true)
	cbase = c.counts.duplicate(true)
	c.position = Vector2(1, 1)
	_p("c_move_p_delta", _delta(base, p.counts))
	_p("c_move_c_delta", _delta(cbase, c.counts))
	# force_update_transform
	base = p.counts.duplicate(true)
	p.force_update_transform()
	_p("force_p_delta", _delta(base, p.counts))
	# enter/exit canvas via CanvasLayer reparent
	var cl := CanvasLayer.new()
	root.add_child(cl)
	var t := NTag.new()
	t.tag = "t"
	root.add_child(t)
	await _frames(1)
	var tb := t.counts.duplicate(true)
	root.remove_child(t)
	cl.add_child(t)
	await _frames(1)
	_p("enter_canvas_delta", _delta(tb, t.counts))
	tb = t.counts.duplicate(true)
	cl.remove_child(t)
	root.add_child(t)
	await _frames(1)
	_p("exit_canvas_delta", _delta(tb, t.counts))
	_p("canvas_layer_node_default", t.get_canvas_layer_node())
	cl.add_child(t)
	await _frames(1)
	_p("canvas_layer_node_cl", t.get_canvas_layer_node() != null)
	_p("canvas_rid_valid", t.get_canvas().is_valid())
	print("PASS discover notify2 ok=true")
	quit()

func _delta(a: Dictionary, b: Dictionary) -> String:
	var keys := {}
	for k in a.keys():
		keys[k] = true
	for k in b.keys():
		keys[k] = true
	var parts: Array = []
	for k in keys.keys():
		var d := int(b.get(k, 0)) - int(a.get(k, 0))
		if d != 0:
			parts.append("%d:%+d" % [int(k), d])
	parts.sort()
	return "[%s]" % ",".join(parts)

# --------------------------------------------------------------- drawx

class DrawX:
	extends Node2D
	var out: Array = []
	func _draw() -> void:
		var t0 := get_transform()
		draw_set_transform(Vector2(5, 5), 0.5, Vector2(2, 2))
		out.append("after_set_transform_same=%d" % int(get_transform() == t0))
		draw_set_transform_matrix(Transform2D(0.5, Vector2(1, 2)))
		out.append("after_set_matrix_same=%d" % int(get_transform() == t0))
		out.append("canvas_valid=%d" % int(get_canvas_item().is_valid()))

func _arm_drawx() -> void:
	var d := DrawX.new()
	d.position = Vector2(7, 8)
	d.rotation = 0.25
	root.add_child(d)
	await _frames(2)
	_p("out", d.out)
	_p("get_canvas_transform", _tm(d.get_canvas_transform()))
	_p("get_viewport_transform", _tm(d.get_viewport_transform()))
	_p("get_global_transform_with_canvas", _tm(d.get_global_transform_with_canvas()))
	_p("get_screen_transform", _tm(d.get_screen_transform()))
	_p("get_viewport_rect", d.get_viewport_rect())
	_p("make_canvas_position_local", _v2(d.make_canvas_position_local(Vector2(10, 10))))
	_p("local_mouse", _v2(d.get_local_mouse_position()))
	print("PASS discover drawx ok=true")
	quit()

# --------------------------------------------------------------- qtime2

class Tracer2:
	extends Node2D
	var events: Array = []
	var draws := 0
	var do_queue_in_process := false
	func _draw() -> void:
		draws += 1
		events.append("d@pf%d/ph%d" % [Engine.get_process_frames(), Engine.get_physics_frames()])
	func _process(_dt: float) -> void:
		if do_queue_in_process:
			events.append("q@pf%d" % Engine.get_process_frames())
			queue_redraw()

func _arm_qtime2() -> void:
	var t := Tracer2.new()
	root.add_child(t)
	await _frames(1)
	_p("e1", t.events)
	t.events.clear()
	# queue from _process in the frame where _process runs
	t.do_queue_in_process = true
	await _frames(1)
	t.do_queue_in_process = false
	_p("e2", t.events)
	await _frames(1)
	_p("e3", t.events)
	# same-frame double queue via _process twice? one process per frame; use two nodes
	t.events.clear()
	var t2 := Tracer2.new()
	root.add_child(t2)
	await _frames(1)
	_p("e4_add", t2.events)
	t2.events.clear()
	t2.do_queue_in_process = true
	await _frames(1)
	t2.do_queue_in_process = false
	_p("e5", t2.events)
	# hidden at add -> no draw; show -> draw
	var t3 := Tracer2.new()
	t3.visible = false
	root.add_child(t3)
	await _frames(2)
	_p("hidden_at_add", t3.events)
	t3.visible = true
	await _frames(1)
	_p("hidden_at_add_show", t3.events)
	# visible=false on a queued-but-not-flushed item within same frame: queue in _process then hide in the same _process?
	# use _process to queue and immediately hide
	t3.events.clear()
	t3.visible = true
	t3.do_queue_in_process = true
	await _frames(1)
	t3.do_queue_in_process = false
	_p("queue_then_next", t3.events)
	print("PASS discover qtime2 ok=true")
	quit()

# --------------------------------------------------------------- contexts

class Ctx:
	extends Node2D
	var log: Array = []
	var do_sig := false
	var do_notif := false
	func _draw() -> void:
		draw_rect(Rect2(0, 0, 1, 1), Color.RED)
		log.append("draw_ok")
	func _notification(what: int) -> void:
		if what == NOTIFICATION_DRAW:
			draw_rect(Rect2(0, 0, 2, 2), Color.RED)
			log.append("notif_draw_ok")
			log.append("notif_then_draw")
	func _ready() -> void:
		if do_sig:
			draw.connect(func(): draw_rect(Rect2(0, 0, 3, 3), Color.RED); log.append("sig_draw_ok"))

func _arm_contexts() -> void:
	var c := Ctx.new()
	c.do_sig = true
	root.add_child(c)
	await _frames(2)
	_p("log", c.log)
	# outside: _process
	c.process_mode = Node.PROCESS_MODE_ALWAYS
	var outside := Ctx.new()
	root.add_child(outside)
	await _frames(1)
	outside.draw_rect(Rect2(0, 0, 1, 1), Color.RED)
	_p("outside_done", true)
	print("PASS discover contexts ok=true")
	quit()

# --------------------------------------------------------------- triggers

class Trig:
	extends Node2D
	var draws := 0
	func _draw() -> void:
		draws += 1

func _arm_triggers() -> void:
	var t := Trig.new()
	root.add_child(t)
	await _frames(2)
	var base := t.draws
	await _frames(2)
	_p("idle", t.draws - base)
	base = t.draws
	t.position = Vector2(5, 5)
	await _frames(2)
	_p("pos", t.draws - base)
	base = t.draws
	t.modulate = Color(0.5, 0.5, 0.5, 1)
	await _frames(2)
	_p("modulate", t.draws - base)
	base = t.draws
	t.material = null
	await _frames(2)
	_p("material_null", t.draws - base)
	base = t.draws
	t.show_behind_parent = true
	await _frames(2)
	_p("behind", t.draws - base)
	base = t.draws
	t.z_index = 3
	await _frames(2)
	_p("z", t.draws - base)
	base = t.draws
	t.set_visibility_layer(2)
	await _frames(2)
	_p("vislayer", t.draws - base)
	base = t.draws
	t.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	await _frames(2)
	_p("texfilter", t.draws - base)
	base = t.draws
	t.set_instance_shader_parameter("x", 1.0)
	await _frames(2)
	_p("shader_param", t.draws - base)
	base = t.draws
	t.rotation = 0.5
	await _frames(2)
	_p("rotation", t.draws - base)
	base = t.draws
	t.top_level = true
	await _frames(2)
	_p("top_level", t.draws - base)
	print("PASS discover triggers ok=true")
	quit()

# --------------------------------------------------------------- vis2

class Vis2:
	extends Node2D
	var notif := {}
	var vis_sig := 0
	var hidden_sig := 0
	func _notification(what: int) -> void:
		notif[what] = int(notif.get(what, 0)) + 1

func _arm_vis2() -> void:
	var c := Vis2.new()
	root.add_child(c)
	c.visibility_changed.connect(func(): c.vis_sig += 1)
	c.hidden.connect(func(): c.hidden_sig += 1)
	await _frames(1)
	_p("base_notif31", c.notif.get(31, 0))
	_p("base_sig", c.vis_sig)
	c.hide()
	await _frames(1)
	_p("hide_notif31", c.notif.get(31, 0))
	_p("hide_sig", c.vis_sig)
	_p("hide_hidden", c.hidden_sig)
	c.show()
	await _frames(1)
	_p("show_notif31", c.notif.get(31, 0))
	_p("show_sig", c.vis_sig)
	c.show()
	await _frames(1)
	_p("show2_notif31", c.notif.get(31, 0))
	_p("show2_sig", c.vis_sig)
	c.hide()
	await _frames(1)
	_p("hide2_notif31", c.notif.get(31, 0))
	_p("hide2_sig", c.vis_sig)
	# clip invalid: start from ONLY then set 99
	c.set_clip_children_mode(CanvasItem.CLIP_CHILDREN_ONLY)
	c.clip_children = 99
	_p("clip_after99", c.get_clip_children_mode())
	c.set_clip_children_mode(CanvasItem.CLIP_CHILDREN_DISABLED)
	c.clip_children = -3
	_p("clip_after_neg3", c.get_clip_children_mode())
	print("PASS discover vis2 ok=true")
	quit()

# --------------------------------------------------------------- notify3

class N3:
	extends Node2D
	var counts := {}
	var tag := ""
	func _notification(what: int) -> void:
		counts[what] = int(counts.get(what, 0)) + 1

func _arm_notify3() -> void:
	var p := N3.new()
	p.tag = "p"
	var c := N3.new()
	c.tag = "c"
	root.add_child(p)
	p.add_child(c)
	await _frames(2)
	# default: notifications enabled?
	_p("p_default_notify", p.is_transform_notification_enabled())
	_p("p_default_local", p.is_local_transform_notification_enabled())
	var b := p.counts.duplicate(true)
	p.position = Vector2(1, 1)
	_p("move_default", _delta(b, p.counts))
	# enable on both
	p.set_notify_transform(true)
	p.set_notify_local_transform(true)
	c.set_notify_transform(true)
	c.set_notify_local_transform(true)
	b = p.counts.duplicate(true)
	var cb := c.counts.duplicate(true)
	p.position = Vector2(2, 2)
	await _frames(1)
	_p("move_enabled_p", _delta(b, p.counts))
	_p("move_enabled_c", _delta(cb, c.counts))
	b = p.counts.duplicate(true)
	cb = c.counts.duplicate(true)
	c.position = Vector2(3, 3)
	await _frames(1)
	_p("cmove_enabled_p", _delta(b, p.counts))
	_p("cmove_enabled_c", _delta(cb, c.counts))
	b = p.counts.duplicate(true)
	p.force_update_transform()
	_p("force_p", _delta(b, p.counts))
	# reparent via reparent()
	var cl := CanvasLayer.new()
	root.add_child(cl)
	await _frames(1)
	var t := N3.new()
	t.tag = "t"
	root.add_child(t)
	await _frames(1)
	var tb := t.counts.duplicate(true)
	t.reparent(cl)
	await _frames(1)
	_p("reparent_delta", _delta(tb, t.counts))
	_p("cl_node", t.get_canvas_layer_node() != null)
	tb = t.counts.duplicate(true)
	t.reparent(root)
	await _frames(1)
	_p("reparent_back_delta", _delta(tb, t.counts))
	_p("cl_node_back", t.get_canvas_layer_node() != null)
	print("PASS discover notify3 ok=true")
	quit()

# --------------------------------------------------------------- qtime3

class T3:
	extends Node2D
	var events: Array = []
	var mode := ""
	func _draw() -> void:
		events.append("d@pf%d/ph%d" % [Engine.get_process_frames(), Engine.get_physics_frames()])
		if mode == "from_draw" and events.size() < 3:
			queue_redraw()
	func _process(_dt: float) -> void:
		if mode == "process":
			events.append("q@pf%d" % Engine.get_process_frames())
			queue_redraw()
			mode = ""
	func _physics_process(_dt: float) -> void:
		if mode == "physics":
			events.append("q@pf%d" % Engine.get_process_frames())
			queue_redraw()
			mode = ""

func _arm_qtime3() -> void:
	var t := T3.new()
	root.add_child(t)
	await _frames(1)
	_p("add", t.events)
	t.events.clear()
	# queue from _process
	t.mode = "process"
	await _frames(1)
	_p("process", t.events)
	# queue from _physics_process
	t.events.clear()
	t.mode = "physics"
	await _frames(1)
	_p("physics", t.events)
	# queue from the await resume point
	t.events.clear()
	t.queue_redraw()
	var pf_now := Engine.get_process_frames()
	await _frames(1)
	_p("await_queue_pf", pf_now)
	_p("await_queue", t.events)
	# queue from _draw -> next frame?
	t.events.clear()
	t.mode = "from_draw"
	t.queue_redraw()
	await _frames(3)
	_p("from_draw", t.events)
	print("PASS discover qtime3 ok=true")
	quit()

# --------------------------------------------------------------- triggers2

func _arm_triggers2() -> void:
	var t := Trig.new()
	root.add_child(t)
	await _frames(2)
	var base := t.draws
	await _frames(2)
	_p("idle", t.draws - base)
	base = t.draws
	t.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
	await _frames(2)
	_p("texture_repeat", t.draws - base)
	base = t.draws
	t.set_oversampling_with_scale(CanvasItem.OVERSAMPLING_WITH_SCALE_ENABLED)
	await _frames(2)
	_p("oversampling", t.draws - base)
	base = t.draws
	t.clip_children = CanvasItem.CLIP_CHILDREN_ONLY
	await _frames(2)
	_p("clip_children", t.draws - base)
	base = t.draws
	t.y_sort_enabled = true
	await _frames(2)
	_p("y_sort", t.draws - base)
	base = t.draws
	t.z_as_relative = false
	await _frames(2)
	_p("z_as_relative", t.draws - base)
	base = t.draws
	t.light_mask = 2
	await _frames(2)
	_p("light_mask", t.draws - base)
	base = t.draws
	t.self_modulate = Color(0.5, 0.5, 0.5, 1)
	await _frames(2)
	_p("self_modulate", t.draws - base)
	base = t.draws
	t.use_parent_material = true
	await _frames(2)
	_p("use_parent_material", t.draws - base)
	base = t.draws
	t.hide()
	await _frames(2)
	_p("hide", t.draws - base)
	t.show()
	await _frames(2)
	base = t.draws
	t.scale = Vector2(2, 2)
	await _frames(2)
	_p("scale", t.draws - base)
	base = t.draws
	t.skew = 0.2
	await _frames(2)
	_p("skew", t.draws - base)
	base = t.draws
	t.name = "renamed"
	await _frames(2)
	_p("rename", t.draws - base)
	base = t.draws
	t.set_visibility_layer_bit(3, false)
	await _frames(2)
	_p("vis_bit", t.draws - base)
	print("PASS discover triggers2 ok=true")
	quit()
