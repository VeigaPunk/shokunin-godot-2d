extends SceneTree
# r98 scout smoke probe — what is measurable headless for the CanvasItem surface?
# Launch: godot --headless --path proj --script res://smoke.gd -- --arm=<name>

var arm := ""

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"draw": await _arm_draw()
		"census": await _arm_census()
		"xform": await _arm_xform()
		_: print("FAIL smoke unknown_arm=%s" % arm); quit(1)

func _p(k: String, v: Variant) -> void:
	print("SMOKE %s %s=%s" % [arm, k, str(v)])

# ---------------------------------------------------------------- draw timing

class DCounter:
	extends Node2D
	var draws := 0
	var frames: Array = []
	var notif_draw := 0
	var notif_vis := 0
	var draw_sig := 0
	func _draw() -> void:
		draws += 1
		frames.append(Engine.get_process_frames())
	func _notification(what: int) -> void:
		if what == NOTIFICATION_DRAW:
			notif_draw += 1
		elif what == NOTIFICATION_VISIBILITY_CHANGED:
			notif_vis += 1

func _arm_draw() -> void:
	var n := DCounter.new()
	_p("pf0", Engine.get_process_frames())
	root.add_child(n)
	n.draw.connect(func(): n.draw_sig += 1)
	await process_frame
	_p("after1_draws", n.draws)
	_p("after1_frames", n.frames)
	await process_frame
	_p("after2_draws", n.draws)
	# coalescing: three queue_redraw in one frame
	n.queue_redraw(); n.queue_redraw(); n.queue_redraw()
	await process_frame
	_p("coal_draws", n.draws)
	# redraw from inside _draw -> one more next frame
	await process_frame
	_p("idle_draws", n.draws)
	# hidden suppression
	n.visible = false
	await process_frame
	var d0: int = n.draws
	n.queue_redraw()
	await process_frame
	await process_frame
	_p("hidden_delta", n.draws - d0)
	n.visible = true
	await process_frame
	await process_frame
	_p("shown_delta", n.draws - d0)
	_p("notif_draw", n.notif_draw)
	_p("draw_sig", n.draw_sig)
	_p("notif_vis", n.notif_vis)
	print("PASS smoke draw draws=%d" % n.draws)
	quit()

# ---------------------------------------------------------------- census

func _arm_census() -> void:
	_p("ci_consts", ClassDB.class_get_integer_constant_list("CanvasItem", true))
	for c in ["NOTIFICATION_DRAW", "NOTIFICATION_VISIBILITY_CHANGED", "NOTIFICATION_TRANSFORM_CHANGED", "NOTIFICATION_LOCAL_TRANSFORM_CHANGED", "NOTIFICATION_ENTER_CANVAS", "NOTIFICATION_EXIT_CANVAS", "CLIP_CHILDREN_DISABLED", "CLIP_CHILDREN_ONLY", "CLIP_CHILDREN_AND_DRAW"]:
		if ClassDB.class_has_integer_constant("CanvasItem", c):
			_p("const_" + c, ClassDB.class_get_integer_constant("CanvasItem", c))
	var props: Array = []
	for p in ClassDB.class_get_property_list("CanvasItem", true):
		props.append(str(p.get("name")))
	_p("ci_props", props)
	var methods: Array = []
	for m in ClassDB.class_get_method_list("CanvasItem", true):
		methods.append(str(m.get("name")))
	_p("ci_methods", methods)
	var drawm: Array = []
	for m in methods:
		if m.begins_with("draw_"):
			drawm.append(m)
	_p("ci_draw_methods", drawm)
	var rs: Array = []
	for m in ClassDB.class_get_method_list("RenderingServer", true):
		var nm := str(m.get("name"))
		if nm.begins_with("canvas_item_get") or nm.begins_with("canvas_get"):
			rs.append(nm)
	_p("rs_canvas_getters", rs)
	_p("theme_fallback_font", ThemeDB.fallback_font != null)
	var dt_ok := false
	if ThemeDB.has_method("get_default_theme"):
		var dt: Theme = ThemeDB.get_default_theme()
		dt_ok = dt != null and dt.default_font != null
	_p("theme_default_font", dt_ok)
	var n2 := Node2D.new()
	var n2p: Array = []
	for p in ClassDB.class_get_property_list("Node2D", true):
		n2p.append(str(p.get("name")))
	_p("n2_props", n2p)
	var n2m: Array = []
	for m in ClassDB.class_get_method_list("Node2D", true):
		n2m.append(str(m.get("name")))
	_p("n2_methods", n2m)
	_p("has_pivot", ClassDB.class_has_method("CanvasItem", "get_pivot_offset"))
	_p("has_notify_transform", ClassDB.class_has_method("CanvasItem", "notify_transform"))
	n2.free()
	print("PASS smoke census ok=true")
	quit()

# ---------------------------------------------------------------- transform

func _tm(t: Transform2D) -> String:
	return "(%.4f,%.4f;%.4f,%.4f;%.4f,%.4f)" % [t.x.x, t.x.y, t.y.x, t.y.y, t.origin.x, t.origin.y]

func _arm_xform() -> void:
	var n := Node2D.new()
	n.position = Vector2(10, 20)
	n.rotation = 0.5
	n.scale = Vector2(2, 3)
	n.skew = 0.25
	root.add_child(n)
	_p("t", _tm(n.get_transform()))
	var t2 := Transform2D(0.5, Vector2(2, 3), 0.25, Vector2(10, 20))
	_p("t_ctor_eq", n.get_transform() == t2)
	var p := Node2D.new()
	p.position = Vector2(100, 50)
	p.rotation = 0.3
	p.scale = Vector2(2, 2)
	root.add_child(p)
	var c := Node2D.new()
	c.position = Vector2(5, 0)
	c.rotation = 0.4
	c.scale = Vector2(1.5, 1.5)
	p.add_child(c)
	_p("gt", _tm(c.get_global_transform()))
	_p("gt_eq", c.get_global_transform() == p.get_global_transform() * c.get_transform())
	_p("gp", c.global_position)
	_p("to_global", c.to_global(Vector2(5, 0)))
	_p("to_local_rt", c.to_local(c.to_global(Vector2(5, 0))))
	p.scale = Vector2(2, 0.5)
	_p("nonuni_gt", _tm(c.get_global_transform()))
	_p("nonuni_grot", c.global_rotation)
	_p("nonuni_gscale", c.global_scale)
	c.top_level = true
	_p("top_gt", _tm(c.get_global_transform()))
	c.top_level = false
	c.rotation = 4.0
	_p("rot4", c.rotation)
	_p("rot4_g", c.global_rotation)
	c.rotation = -4.0
	_p("rotm4", c.rotation)
	c.scale = Vector2(0, 0)
	_p("zero_gscale", c.global_scale)
	print("PASS smoke xform ok=true")
	quit()
