extends SceneTree
# r85 fixture — CanvasLayer / Viewport / Camera2D transform lattice
# (headless 2D, read-only). One arm per process, exactly the battery's
# launch shape:
#   godot --headless --path <scratch> --script res://camera_proc.gd -- --arm=<name>
# Prints an audit header, R85 diagnostic lines, and one final
# `PASS camera_proc <arm> ...` line. No object ids / addresses / RIDs are
# printed (byte-stability).
# The `match arm:` dispatch in _run is the sole arm index (15 pinned arms
# plus 5 non-pinned diag_* diagnostics that no CASES row references);
# per-arm measured classes live in r85-scout §1.1-1.4.
#
# Arms
#   cam_comp         camera position/zoom/offset/anchor -> canvas_transform composition
#   cam_zoom_center  which world point sits at the screen center under fractional zoom
#   cam_phase        physics-phase camera write: same-frame vs next-frame canvas_transform
#   cam_subpixel     1/60 fixed-tps moves: sub-pixel origins vs the closed form
#   cam_space        global vs with_canvas vs screen vs viewport_transform spaces
#   cl_stack         CanvasLayer stacking: per-layer transforms, camera independence
#   cl_follow        follow_viewport_enabled x follow_viewport_scale lattice
#   cl_phase         CanvasLayer write timing (same frame / next frame)
#   cl_draworder     headless redraw order across layers (ordering witness)
#   vp_worlds        SubViewport world_2d sharing vs separate worlds, physics scope
#   vp_render_indep  physics byte-independence from canvas/camera state
#   vp_subcam        per-viewport Camera2D isolation
#   par_layer        ParallaxLayer motion_scale/motion_offset/motion_mirroring
#   par_2d           Parallax2D scroll_scale/repeat/follow/ignore_camera_scroll
#   par_phase        parallax update timing vs a physics-phase camera move
#   diag_*           non-pinned diagnostics (never referenced by a CASES row)

const PFX := "PASS camera_proc "

var arm := ""
var _nodes: Array = []
var _diag: Array = []

# ------------------------------------------------------------------ classes

class Lane extends Node:
	var tag := ""
	var phys := 0
	var idle := 0
	var phys_hook := Callable()
	var idle_hook := Callable()
	var deltas: Array = []
	func _ready() -> void:
		set_process(true)
		set_physics_process(true)
	func _physics_process(d: float) -> void:
		phys += 1
		deltas.append(d)
		if phys_hook.is_valid():
			phys_hook.call(self, d)
	func _process(d: float) -> void:
		idle += 1
		if idle_hook.is_valid():
			idle_hook.call(self, d)

class DrawTag extends Node2D:
	var tag := ""
	var sink: Array = []
	var draws := 0
	var queued := 0
	func _ready() -> void:
		queue_redraw()
	func queue_tag() -> void:
		queued += 1
		queue_redraw()
	func _draw() -> void:
		draws += 1
		draw_rect(Rect2(0, 0, 1, 1), Color.WHITE)
		sink.append("%s@pf%d" % [tag, Engine.get_physics_frames()])

# ------------------------------------------------------------------ helpers

func _v(v: Vector2) -> String:
	return "%.4f,%.4f" % [v.x, v.y]

func _t(t: Transform2D) -> String:
	return "(%.4f,%.4f;%.4f,%.4f;%.4f,%.4f)" % [t.x.x, t.x.y, t.y.x, t.y.y,
		t.origin.x, t.origin.y]

func _near(a: Vector2, b: Vector2) -> bool:
	return a.distance_to(b) < 0.0001

func _mk_lane(tag: String, parent: Node = null) -> Lane:
	var l := Lane.new()
	l.name = tag
	l.tag = tag
	if parent == null:
		parent = root
	parent.add_child(l)
	_nodes.append(l)
	return l

func _mk_node2d(parent: Node, pos: Vector2, name := "N") -> Node2D:
	var n := Node2D.new()
	n.name = name
	n.position = pos
	parent.add_child(n)
	_nodes.append(n)
	return n

func _mk_floor(parent: Node, pos: Vector2, size: Vector2) -> StaticBody2D:
	var f := StaticBody2D.new()
	f.name = "Floor"
	f.position = pos
	var cs := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = size
	cs.shape = rect
	f.add_child(cs)
	parent.add_child(f)
	_nodes.append(f)
	return f

func _mk_body(parent: Node, pos: Vector2, name := "Body") -> RigidBody2D:
	var b := RigidBody2D.new()
	b.name = name
	b.position = pos
	var cs := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(8, 8)
	cs.shape = rect
	b.add_child(cs)
	parent.add_child(b)
	_nodes.append(b)
	return b

func _mk_cam(parent: Node, pos: Vector2, zoom := Vector2.ONE) -> Camera2D:
	var c := Camera2D.new()
	c.name = "Cam"
	c.position = pos
	c.zoom = zoom
	parent.add_child(c)
	_nodes.append(c)
	return c

func _settle() -> void:
	await process_frame
	await process_frame

func _finish(line: String) -> void:
	for n in _nodes:
		if is_instance_valid(n):
			n.free()
	_nodes.clear()
	print(PFX + arm + " " + line)
	quit(0)

func _fail(reason: String) -> void:
	print("FAIL camera_proc %s %s" % [arm, reason])
	quit(1)

func _stamp() -> String:
	return "pf%d#%d%s" % [Engine.get_physics_frames(), Engine.get_process_frames(),
		"P" if Engine.is_in_physics_frame() else "I"]

# Write/observe probe, frame-aligned: the write happens in the lane's
# _physics_process callback for physics frame k; observations are
#   w{k}[before>after]  -- in the writing callback, around the write
#   i{k}[v]             -- the *first* idle observation after that callback
#   next[v]             -- the next physics callback, before its own write
# The number of idle iterations per physics frame is host-timing shaped and is
# never recorded; exactly one idle observation per physics frame is.
func _phase_probe(label: String, write: Callable, read: Callable, frames: int,
		out: Array) -> void:
	var lane := _mk_lane(label)
	var st := {"k": 0, "armed": false}
	lane.phys_hook = func(l: Lane, _d: float):
		if l.phys >= 1 and l.phys <= frames:
			var before: String = str(read.call())
			write.call(l.phys)
			var after: String = str(read.call())
			st["k"] = l.phys
			st["armed"] = true
			out.append("%s.w%d[%s>%s]" % [label, l.phys, before, after])
		elif l.phys == frames + 1:
			out.append("%s.next[%s]" % [label, str(read.call())])
	lane.idle_hook = func(_l: Lane, _d: float):
		if bool(st["armed"]):
			st["armed"] = false
			out.append("%s.i%d[%s]" % [label, int(st["k"]), str(read.call())])
	var guard := 0
	while lane.phys <= frames and guard < 400:
		await process_frame
		guard += 1
	await process_frame

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")

func _run() -> void:
	print("R85 arm=%s godot=%s vp=%s tps=%d tscale=%.3f" % [arm,
		Engine.get_version_info().string, str(root.get_visible_rect().size),
		Engine.physics_ticks_per_second, Engine.time_scale])
	match arm:
		"cam_comp": await _arm_cam_comp()
		"cam_zoom_center": await _arm_cam_zoom_center()
		"cam_phase": await _arm_cam_phase()
		"cam_subpixel": await _arm_cam_subpixel()
		"cam_space": await _arm_cam_space()
		"cl_stack": await _arm_cl_stack()
		"cl_follow": await _arm_cl_follow()
		"cl_phase": await _arm_cl_phase()
		"cl_draworder": await _arm_cl_draworder()
		"vp_worlds": await _arm_vp_worlds()
		"vp_render_indep": await _arm_vp_render_indep()
		"vp_subcam": await _arm_vp_subcam()
		"par_layer": await _arm_par_layer()
		"par_2d": await _arm_par_2d()
		"par_phase": await _arm_par_phase()
		"diag_delta": await _arm_diag_delta()
		"diag_world_step": await _arm_diag_world_step()
		"diag_draw": await _arm_diag_draw()
		"diag_cam_internal": await _arm_diag_cam_internal()
		"diag_stretch": await _arm_diag_stretch()
		_: _fail("unknown_arm")

# ------------------------------------------------------- cam_comp

func _arm_cam_comp() -> void:
	var n := _mk_node2d(root, Vector2(300, 200), "N")
	await _settle()
	var nocam := root.canvas_transform
	var cam := _mk_cam(root, Vector2.ZERO)
	cam.make_current()
	await _settle()
	var s0 := root.canvas_transform
	var t0 := cam.get_target_position()
	var c0 := cam.get_screen_center_position()
	cam.position = Vector2(100, 50)
	await _settle()
	var s1 := root.canvas_transform
	cam.zoom = Vector2(2, 2)
	await _settle()
	var s2 := root.canvas_transform
	cam.offset = Vector2(10, 20)
	await _settle()
	var s3 := root.canvas_transform
	var n3 := n.get_global_transform_with_canvas()
	var t3 := cam.get_target_position()
	var c3 := cam.get_screen_center_position()
	cam.anchor_mode = Camera2D.ANCHOR_MODE_FIXED_TOP_LEFT
	await _settle()
	var s4 := root.canvas_transform
	var t4 := cam.get_target_position()
	var c4 := cam.get_screen_center_position()
	# C6 (r85 critic): a second-config composition witness — comp under
	# s3 alone is an engine identity a constant could fake; s4 forces the
	# same law to hold under a different live transform.
	var n4 := n.get_global_transform_with_canvas()
	var comp4 := s4 * n.global_transform
	var comp4_ok := comp4 == n4
	cam.anchor_mode = Camera2D.ANCHOR_MODE_DRAG_CENTER
	cam.offset = Vector2.ZERO
	cam.zoom = Vector2.ONE
	cam.position = Vector2.ZERO
	await _settle()
	var s5 := root.canvas_transform
	var eq_cam_vp := cam.get_canvas_transform() == root.canvas_transform
	var eq_screen := n.get_screen_transform() == n.get_global_transform_with_canvas()
	var comp := s3 * n.global_transform
	var comp_ok := comp == n3
	var inv := s3.affine_inverse() * (s3 * Vector2(300, 200))
	var inv_ok := _near(inv, Vector2(300, 200))
	var s3_cf := _v(s3.origin + Vector2(32, 32) - s3.origin)
	_finish("vp2=%s nocam=%s s0=%s s1=%s s2=%s s3=%s s4=%s s5=%s n3=%s comp=%s n4=%s comp4=%s t0=%s c0=%s t3=%s c3=%s t4=%s c4=%s eq[cam_vp=%d screen=%d comp=%d comp4=%d inv=%d] probe=%s" % [
		str(root.get_visible_rect().size), _t(nocam), _t(s0), _t(s1), _t(s2), _t(s3), _t(s4), _t(s5),
		_t(n3), _t(comp), _t(n4), _t(comp4), _v(t0), _v(c0), _v(t3), _v(c3), _v(t4), _v(c4),
		int(eq_cam_vp), int(eq_screen), int(comp_ok), int(comp4_ok), int(inv_ok), s3_cf])

# ------------------------------------------------------- cam_zoom_center

func _arm_cam_zoom_center() -> void:
	var cam := _mk_cam(root, Vector2(10.5, -3.25), Vector2(1.5, 1.5))
	cam.make_current()
	await _settle()
	var ct := root.canvas_transform
	var pts: Array = [Vector2.ZERO, Vector2(10.5, -3.25), Vector2(100, 100), Vector2(-7.25, 3.75)]
	var screens: Array = []
	for i in range(pts.size()):
		var p: Vector2 = pts[i]
		screens.append(_v(ct * p))
	var center_world := ct.affine_inverse() * (root.get_visible_rect().size * 0.5)
	var anchor_ok := _near(center_world, Vector2(10.5, -3.25))
	var base := ct * Vector2(10.5, -3.25)
	var dx := (ct * (Vector2(10.5, -3.25) + Vector2(1, 0))) - base
	var dy := (ct * (Vector2(10.5, -3.25) + Vector2(0, 1))) - base
	cam.position = Vector2(10.5 + 1.0 / 60.0, -3.25)
	await _settle()
	var ct2 := root.canvas_transform
	var dsub := (ct2 * Vector2(10.5, -3.25)) - base
	var sub_dev := absf(dsub.x + 1.5 / 60.0)
	var sub_ok := sub_dev < 0.0001
	# C7 (r85 critic): the deviation is emitted at 9 decimals — "exactly
	# -0.025" at 4dp laundered a 0.1% step error.
	_finish("zoom=1.5 pos=10.5,-3.25 ct=%s screens=[%s] center_world=%s anchor_ok=%d dx=%s dy=%s sub60=%s sub_dev=%.9f sub_ok=%d ct2=%s" % [
		_t(ct), "|".join(screens), _v(center_world), int(anchor_ok), _v(dx), _v(dy),
		_v(dsub), sub_dev, int(sub_ok), _t(ct2)])

# ------------------------------------------------------- cam_phase

func _arm_cam_phase() -> void:
	var cam := _mk_cam(root, Vector2.ZERO)
	cam.make_current()
	await _settle()
	var out: Array = []
	var camref := cam
	# A: default process_callback (IDLE), plain write
	await _phase_probe("A", func(k: int): camref.position = Vector2(10.0 * k, 0.0),
		func() -> String: return _v(root.canvas_transform.origin), 3, out)
	# B: same + force_update_scroll() right after the write
	camref.position = Vector2.ZERO
	await _settle()
	await _phase_probe("B", func(k: int):
			camref.position = Vector2(20.0 * k, 0.0)
			camref.force_update_scroll(),
		func() -> String: return _v(root.canvas_transform.origin), 3, out)
	# C: process_callback = PHYSICS, plain write
	camref.position = Vector2.ZERO
	camref.process_callback = Camera2D.CAMERA2D_PROCESS_PHYSICS
	await _settle()
	await _phase_probe("C", func(k: int): camref.position = Vector2(30.0 * k, 0.0),
		func() -> String: return _v(root.canvas_transform.origin), 3, out)
	# D: IDLE again but write from the idle callback (armed once per physics frame,
	# so the write/observe sequence is 1:1 with physics frames and never depends on
	# how many idle iterations the host runs per physics frame)
	camref.process_callback = Camera2D.CAMERA2D_PROCESS_IDLE
	camref.position = Vector2.ZERO
	await _settle()
	var lane := _mk_lane("D")
	var st2 := {"k": 0, "armed": false, "pending": 0}
	lane.phys_hook = func(l: Lane, _d: float):
		if l.phys >= 1 and l.phys <= 3:
			out.append("D.p%d[%s]" % [l.phys, _v(root.canvas_transform.origin)])
			st2["armed"] = true
	lane.idle_hook = func(_l: Lane, _d: float):
		if int(st2["pending"]) > 0:
			out.append("D.i%d[%s]" % [int(st2["pending"]), _v(root.canvas_transform.origin)])
			st2["pending"] = 0
		if bool(st2["armed"]):
			st2["armed"] = false
			st2["k"] = int(st2["k"]) + 1
			st2["pending"] = int(st2["k"])
			camref.position = Vector2(40.0 * float(st2["k"]), 0.0)
			out.append("D.w%d[after=%s]" % [int(st2["k"]), _v(root.canvas_transform.origin)])
	while lane.phys <= 3:
		await process_frame
	await process_frame
	# E: a later-priority physics observer in the same frame still sees the old value
	camref.position = Vector2.ZERO
	await _settle()
	var wl := _mk_lane("Ew")
	var ol := _mk_lane("Eo")
	ol.process_priority = 100
	var st3 := {"k": 0, "armed": false}
	wl.phys_hook = func(l: Lane, _d: float):
		if l.phys >= 1 and l.phys <= 2:
			camref.position = Vector2(50.0 * l.phys, 0.0)
			st3["k"] = l.phys
			st3["armed"] = true
			out.append("E.w%d[after=%s]" % [l.phys, _v(root.canvas_transform.origin)])
		elif l.phys == 3:
			out.append("E.next[%s]" % _v(root.canvas_transform.origin))
	ol.phys_hook = func(l: Lane, _d: float):
		if l.phys >= 1 and l.phys <= 2:
			out.append("E.o%d[sees=%s]" % [l.phys, _v(root.canvas_transform.origin)])
	ol.idle_hook = func(_l: Lane, _d: float):
		if bool(st3["armed"]):
			st3["armed"] = false
			out.append("E.i%d[%s]" % [int(st3["k"]), _v(root.canvas_transform.origin)])
	while wl.phys <= 3:
		await process_frame
	await process_frame
	_finish("pc_idle=%d prio[o=%d] " % [camref.process_callback, ol.process_priority] + " ".join(out))

# ------------------------------------------------------- cam_subpixel

func _arm_cam_subpixel() -> void:
	var cam := _mk_cam(root, Vector2.ZERO)
	cam.make_current()
	await _settle()
	var lane := _mk_lane("subpx")
	var origins: Array = []
	var exact: Array = []
	var close: Array = []
	lane.phys_hook = func(l: Lane, _d: float):
		if l.phys >= 1 and l.phys <= 12:
			var k := l.phys - 1
			var o := root.canvas_transform.origin
			origins.append(_v(o))
			var want := Vector2(32.0 - float(k) / 60.0, 32.0 - float(k) / 120.0)
			exact.append(int(o == want))
			close.append(int(_near(o, want)))
			cam.position = Vector2(float(l.phys) / 60.0, float(l.phys) / 120.0)
	while lane.phys <= 12:
		await process_frame
	var distinct := {}
	for o in origins:
		distinct[o] = 1
	# fractional zoom phase: zoom 1.5 after 12 frames
	cam.zoom = Vector2(1.5, 1.5)
	await _settle()
	var o15 := root.canvas_transform.origin
	var want15 := Vector2(32.0 - 12.0 / 60.0 * 1.5, 32.0 - 12.0 / 120.0 * 1.5)
	cam.zoom = Vector2(0.5, 0.5)
	await _settle()
	var o05 := root.canvas_transform.origin
	var want05 := Vector2(32.0 - 12.0 / 60.0 * 0.5, 32.0 - 12.0 / 120.0 * 0.5)
	_finish("n=%d distinct=%d samples=[%s] eq_exact=%s eq_close=%s zoom15=%s want15=%s z15_ok=%d zoom05=%s want05=%s z05_ok=%d" % [
		origins.size(), distinct.size(), "|".join(origins),
		"".join(exact), "".join(close), _v(o15), _v(want15), int(_near(o15, want15)),
		_v(o05), _v(want05), int(_near(o05, want05))])

# ------------------------------------------------------- cam_space

func _arm_cam_space() -> void:
	var n := _mk_node2d(root, Vector2(300, 200), "N")
	var cam := _mk_cam(root, Vector2.ZERO)
	cam.make_current()
	await _settle()
	var g0 := n.global_transform
	var ct0 := root.canvas_transform
	var wc0 := n.get_global_transform_with_canvas()
	var sc0 := n.get_screen_transform()
	var vx0 := n.get_viewport_transform()
	var vpr := n.get_viewport_rect()
	cam.position = Vector2(100, 50)
	cam.zoom = Vector2(2, 2)
	await _settle()
	var g1 := n.global_transform
	var ct1 := root.canvas_transform
	var wc1 := n.get_global_transform_with_canvas()
	var sc1 := n.get_screen_transform()
	var vx1 := n.get_viewport_transform()
	# CanvasLayer child in the same arm
	var cl := CanvasLayer.new()
	cl.name = "CL"
	cl.layer = 3
	root.add_child(cl)
	_nodes.append(cl)
	var lc := _mk_node2d(cl, Vector2(300, 200), "LC")
	await _settle()
	var lwc := lc.get_global_transform_with_canvas()
	var lsc := lc.get_screen_transform()
	var lvx := lc.get_viewport_transform()
	var lct := cl.get_final_transform() if cl.has_method("get_final_transform") else Transform2D.IDENTITY
	var has_final := cl.has_method("get_final_transform")
	var wc_eq := (wc0 == ct0 * g0) and (wc1 == ct1 * g1)
	var screen_eq := (sc0 == wc0) and (sc1 == wc1)
	var vp_eq := (vx0 == ct0) and (vx1 == ct1)
	var g_indep := g0 == g1
	var l_indep := _near(lwc.origin, Vector2(300, 200))
	# stretch phase: the viewport's content-scale transform vs the transform spaces
	var before_factor := root.content_scale_factor
	var before_mode := root.content_scale_mode
	root.content_scale_factor = 2.0
	await _settle()
	var f2_final := root.get_final_transform()
	var f2_ct := root.canvas_transform
	var f2_wc := n.get_global_transform_with_canvas()
	var f2_sc := n.get_screen_transform()
	var f2_vx := n.get_viewport_transform()
	var f2_lwc := lc.get_global_transform_with_canvas()
	var vx_final_ct := f2_vx == f2_final * f2_ct
	var sc_wc := f2_sc == f2_wc
	var layer_unscaled := _near(f2_lwc.origin, Vector2(300, 200))
	var half_term := f2_ct.origin + Vector2(200, 100)
	root.content_scale_factor = before_factor
	root.content_scale_mode = before_mode
	await _settle()
	var restored := root.canvas_transform == ct1
	_finish("vpr=%s g0=%s g1=%s g_indep=%d ct0=%s ct1=%s wc0=%s wc1=%s sc0=%s sc1=%s vx0=%s vx1=%s wc_eq=%d screen_eq=%d vp_eq=%d cl[has_final=%d final=%s lwc=%s lsc=%s lvx=%s l_indep=%d] stretch[f2_final=%s f2_ct=%s f2_wc=%s f2_sc=%s f2_vx=%s vx_final_ct=%d sc_wc=%d layer_unscaled=%d half=%s restored=%d]" % [
		str(vpr), _t(g0), _t(g1), int(g_indep), _t(ct0), _t(ct1), _t(wc0), _t(wc1),
		_t(sc0), _t(sc1), _t(vx0), _t(vx1), int(wc_eq), int(screen_eq), int(vp_eq),
		int(has_final), _t(lct), _t(lwc), _t(lsc), _t(lvx), int(l_indep),
		_t(f2_final), _t(f2_ct), _t(f2_wc), _t(f2_sc), _t(f2_vx), int(vx_final_ct),
		int(sc_wc), int(layer_unscaled), _v(half_term), int(restored)])

# ------------------------------------------------------- cl_stack

func _arm_cl_stack() -> void:
	var cam := _mk_cam(root, Vector2(50, 0))
	cam.make_current()
	var rn := _mk_node2d(root, Vector2(100, 0), "RN")
	var layers: Array = []
	for lv in [-1, 0, 7]:
		var cl := CanvasLayer.new()
		cl.name = "CL%d" % int(lv)
		cl.layer = int(lv)
		root.add_child(cl)
		_nodes.append(cl)
		var child := _mk_node2d(cl, Vector2(100, 0), "C%d" % int(lv))
		layers.append([cl, child])
	await _settle()
	var rwc := rn.get_global_transform_with_canvas()
	var rows: Array = []
	for i in range(layers.size()):
		var cl: CanvasLayer = layers[i][0]
		var ch: Node2D = layers[i][1]
		rows.append("L%d[in=%d wc=%s vx=%s fin=%s]" % [cl.layer,
			int(cl.is_inside_tree()),
			_v(ch.get_global_transform_with_canvas().origin),
			_v(ch.get_viewport_transform().origin),
			_v(cl.get_final_transform().origin) if cl.has_method("get_final_transform") else "n/a"])
	# transform decomposition readbacks on layer 7
	var cl7: CanvasLayer = layers[2][0]
	cl7.transform = Transform2D(0.5, Vector2(10, 20))
	await _settle()
	var d1 := "t1[off=%s rot=%.4f scale=%s xf=%s]" % [_v(cl7.offset), cl7.rotation, _v(cl7.scale), _t(cl7.transform)]
	cl7.offset = Vector2(5, 5)
	await _settle()
	var d2 := "t2[off=%s rot=%.4f scale=%s xf=%s]" % [_v(cl7.offset), cl7.rotation, _v(cl7.scale), _t(cl7.transform)]
	cl7.scale = Vector2(2, 2)
	await _settle()
	var d3 := "t3[off=%s rot=%.4f scale=%s xf=%s]" % [_v(cl7.offset), cl7.rotation, _v(cl7.scale), _t(cl7.transform)]
	var ch7: Node2D = layers[2][1]
	var wc7 := ch7.get_global_transform_with_canvas()
	var expect7 := cl7.get_final_transform() * ch7.global_transform
	var comp7 := wc7 == expect7
	# nested CanvasLayer inside a layer child
	var inner := CanvasLayer.new()
	inner.name = "Inner"
	inner.layer = 9
	ch7.add_child(inner)
	_nodes.append(inner)
	var ic := _mk_node2d(inner, Vector2(100, 0), "IC")
	await _settle()
	var iwc := ic.get_global_transform_with_canvas()
	var nested_ok := _near(iwc.origin, Vector2(100, 0))
	_finish("cam=%s root_wc=%s layers=[%s] %s %s %s wc7=%s expect7=%s comp7=%d nested[wc=%s isolated=%d]" % [
		_v(cam.position), _v(rwc.origin), "|".join(rows), d1, d2, d3,
		_t(wc7), _t(expect7), int(comp7), _v(iwc.origin), int(nested_ok)])

# ------------------------------------------------------- cl_follow

func _arm_cl_follow() -> void:
	var cam := _mk_cam(root, Vector2(100, 50), Vector2(2, 2))
	cam.make_current()
	await _settle()
	var ct := root.canvas_transform
	var rows: Array = []
	var cfgs: Array = [[false, 1.0], [true, 1.0], [true, 0.5], [true, 2.0]]
	for i in range(cfgs.size()):
		var cl := CanvasLayer.new()
		cl.name = "F%d" % i
		cl.layer = i + 1
		cl.follow_viewport_enabled = bool(cfgs[i][0])
		cl.follow_viewport_scale = float(cfgs[i][1])
		root.add_child(cl)
		_nodes.append(cl)
		var ch := _mk_node2d(cl, Vector2(100, 0), "FC%d" % i)
		await _settle()
		var wc := ch.get_global_transform_with_canvas()
		var fin := cl.get_final_transform() if cl.has_method("get_final_transform") else Transform2D.IDENTITY
		# C3 (r85 critic): `in` pins tree membership — an orphaned layer can
		# otherwise emit an identical row.
		rows.append("F%d[en=%d in=%d sc=%.1f wc=%s fin=%s]" % [i,
			int(cl.follow_viewport_enabled), int(cl.is_inside_tree()),
			cl.follow_viewport_scale, _v(wc.origin), _t(fin)])
	# composition with a non-identity layer transform on a following layer
	var cl2 := CanvasLayer.new()
	cl2.name = "F2b"
	cl2.layer = 20
	cl2.follow_viewport_enabled = true
	cl2.follow_viewport_scale = 1.0
	cl2.offset = Vector2(10, 20)
	root.add_child(cl2)
	_nodes.append(cl2)
	var ch2 := _mk_node2d(cl2, Vector2(100, 0), "FC2b")
	await _settle()
	var wc2 := ch2.get_global_transform_with_canvas()
	var fin2 := cl2.get_final_transform() if cl2.has_method("get_final_transform") else Transform2D.IDENTITY
	# camera move: does a following layer track?
	cam.position = Vector2(300, 0)
	await _settle()
	var wc2b := ch2.get_global_transform_with_canvas()
	var fin2b := cl2.get_final_transform() if cl2.has_method("get_final_transform") else Transform2D.IDENTITY
	_finish("ct=%s rows=[%s] f2b[wc=%s fin=%s] moved[ct=%s wc=%s fin=%s]" % [
		_t(ct), "|".join(rows), _v(wc2.origin), _t(fin2), _t(root.canvas_transform),
		_v(wc2b.origin), _t(fin2b)])

# ------------------------------------------------------- cl_phase

func _arm_cl_phase() -> void:
	var cam := _mk_cam(root, Vector2.ZERO)
	cam.make_current()
	var cl := CanvasLayer.new()
	cl.name = "CL"
	cl.layer = 4
	root.add_child(cl)
	_nodes.append(cl)
	var ch := _mk_node2d(cl, Vector2(100, 0), "C")
	await _settle()
	var out: Array = []
	var clref := cl
	await _phase_probe("A", func(k: int): clref.offset = Vector2(10.0 * k, 0.0),
		func() -> String: return "cl=%s vp=%s" % [_v(ch.get_global_transform_with_canvas().origin),
			_v(root.canvas_transform.origin)], 3, out)
	# B: write the whole transform instead of the offset
	clref.offset = Vector2.ZERO
	await _settle()
	await _phase_probe("B", func(k: int): clref.transform = Transform2D(0.0, Vector2(5.0 * k, 0.0)),
		func() -> String: return "cl=%s" % _v(ch.get_global_transform_with_canvas().origin), 3, out)
	# C: visibility flips do not touch transforms
	clref.transform = Transform2D.IDENTITY
	await _settle()
	clref.visible = false
	await _settle()
	var inv := "inv[wc=%s vp=%s]" % [_v(ch.get_global_transform_with_canvas().origin),
		_v(root.canvas_transform.origin)]
	clref.visible = true
	await _settle()
	_finish("".join(out) + " " + inv)

# ------------------------------------------------------- cl_draworder

func _arm_cl_draworder() -> void:
	var sink: Array = []
	var layers: Array = []
	for lv in [7, -1, 0]:
		var cl := CanvasLayer.new()
		cl.name = "D%d" % int(lv)
		cl.layer = int(lv)
		root.add_child(cl)
		_nodes.append(cl)
		var dt := DrawTag.new()
		dt.name = "T%d" % int(lv)
		dt.tag = "L%d" % int(lv)
		dt.sink = sink
		cl.add_child(dt)
		_nodes.append(dt)
		layers.append(cl)
	var rtag := DrawTag.new()
	rtag.name = "TR"
	rtag.tag = "LR"
	rtag.sink = sink
	root.add_child(rtag)
	_nodes.append(rtag)
	var hidden := CanvasLayer.new()
	hidden.name = "DH"
	hidden.layer = 3
	hidden.visible = false
	root.add_child(hidden)
	_nodes.append(hidden)
	var htag := DrawTag.new()
	htag.name = "TH"
	htag.tag = "LH"
	htag.sink = sink
	hidden.add_child(htag)
	_nodes.append(htag)
	var lane := _mk_lane("drawer")
	var tags_list: Array = [rtag, htag]
	for cl in layers:
		for c in cl.get_children():
			tags_list.append(c)
	lane.phys_hook = func(l: Lane, _d: float):
		if l.phys <= 3:
			for dt in tags_list:
				var d := dt as DrawTag
				if d != null:
					d.queue_tag()
	while lane.phys <= 4:
		await process_frame
	var per := {}
	for s in sink:
		var k: String = str(s).split("@")[0]
		per[k] = int(per.get(k, 0)) + 1
	var later := []
	var first_frame := []
	var frames := []
	for s in sink:
		var tok := str(s)
		var pf := int(tok.split("@pf")[1])
		if pf == 1:
			first_frame.append(tok.split("@")[0])
		else:
			if not later.has(tok.split("@")[0]):
				later.append(tok.split("@")[0])
		frames.append(tok)
	var creation_order := true
	var layer_sorted := true
	var creation_names := ["L7", "L-1", "L0"]
	var sorted_names := ["L-1", "L0", "L7"]
	for i in range(creation_names.size()):
		if first_frame[i] != creation_names[i]:
			creation_order = false
		if first_frame[i] != sorted_names[i]:
			layer_sorted = false
	_finish("seq=%s n=%d counts=%s first=[%s] later=[%s] hidden_draws=%d hidden[in=%d vis=%d queued=%d] creation_order=%d layer_sorted=%d" % [
		"|".join(frames), sink.size(), str(per), ",".join(first_frame), ",".join(later),
		htag.draws, int(hidden.is_inside_tree()), int(hidden.visible),
		htag.queued, int(creation_order), int(layer_sorted)])

# ------------------------------------------------------- vp_worlds

func _arm_vp_worlds() -> void:
	var root_world := root.find_world_2d()
	var sv_default := SubViewport.new()
	sv_default.name = "SVD"
	sv_default.size = Vector2i(64, 64)
	root.add_child(sv_default)
	_nodes.append(sv_default)
	await process_frame
	var d_own := sv_default.world_2d != null
	var d_shares := sv_default.find_world_2d() == root_world
	var sv_share := SubViewport.new()
	sv_share.name = "SVS"
	sv_share.size = Vector2i(64, 64)
	sv_share.world_2d = root_world
	root.add_child(sv_share)
	_nodes.append(sv_share)
	await process_frame
	var s_shares := sv_share.find_world_2d() == root_world
	var sv_own := SubViewport.new()
	sv_own.name = "SVO"
	sv_own.size = Vector2i(64, 64)
	sv_own.world_2d = World2D.new()
	root.add_child(sv_own)
	_nodes.append(sv_own)
	await process_frame
	var o_shares := sv_own.find_world_2d() == root_world
	# physics scope: one body per world, no body-body interaction
	var floor_root := _mk_floor(root, Vector2(0, 90), Vector2(200, 20))
	var b_root := _mk_body(root, Vector2(0, 0), "BR")
	var b_share := _mk_body(sv_share, Vector2(40, 0), "BS")
	var b_own := _mk_body(sv_own, Vector2(0, 0), "BO")
	# a floor inside the default subviewport's own world
	var floor_sub := _mk_floor(sv_default, Vector2(0, 90), Vector2(200, 20))
	var b_default := _mk_body(sv_default, Vector2(0, 0), "BD")
	for i in range(40):
		await physics_frame
	var cr := b_root.get_contact_count()
	var cs := b_share.get_contact_count()
	var co := b_own.get_contact_count()
	var cd := b_default.get_contact_count()
	var rest_root := _v(b_root.position)
	var rest_sub := _v(b_default.position)
	_finish("share[d_own=%d d_shares=%d s_shares=%d o_shares=%d] pos[br=%s bs=%s bo=%s bd=%s] contacts[br=%d bs=%d bo=%d bd=%d] same_rest=%d shared_floor=%d own_fall=%d" % [
		int(d_own), int(d_shares), int(s_shares), int(o_shares),
		rest_root, _v(b_share.position), _v(b_own.position), rest_sub,
		cr, cs, co, cd, int(rest_root == rest_sub), int(b_share.position.y < 100.0),
		int(b_own.position.y > 200.0)])

# ------------------------------------------------------- vp_render_indep

func _arm_vp_render_indep() -> void:
	var bodies: Array = []
	var tags: Array = []
	# L0: own world, no camera
	# L1: own world, static camera (100,50) zoom 2
	# L2: own world, camera moving + zooming every physics frame
	# L3: root world, camera moving + a CanvasLayer offset written every frame
	var v2cam: Camera2D = null
	for i in range(3):
		var sv := SubViewport.new()
		sv.name = "V%d" % i
		sv.size = Vector2i(64, 64)
		sv.world_2d = World2D.new()
		root.add_child(sv)
		_nodes.append(sv)
		_mk_floor(sv, Vector2(0, 90), Vector2(200, 20))
		var b := _mk_body(sv, Vector2(0, 0), "B%d" % i)
		bodies.append(b)
		tags.append("V%d" % i)
		if i == 1:
			var c := _mk_cam(sv, Vector2(100, 50), Vector2(2, 2))
			c.make_current()
		if i == 2:
			var c2 := _mk_cam(sv, Vector2.ZERO)
			c2.make_current()
			v2cam = c2
			var lane := _mk_lane("mv")
			lane.phys_hook = func(l: Lane, _d: float):
				c2.position = Vector2(float(l.phys) / 60.0, float(l.phys) / 120.0)
				c2.zoom = Vector2(1.0 + 0.05 * float(l.phys), 1.0 + 0.05 * float(l.phys))
	var cam_root := _mk_cam(root, Vector2.ZERO)
	cam_root.make_current()
	var cl := CanvasLayer.new()
	cl.name = "CL"
	cl.layer = 2
	root.add_child(cl)
	_nodes.append(cl)
	_mk_floor(root, Vector2(0, 90), Vector2(200, 20))
	var b_root := _mk_body(root, Vector2(0, 0), "B3")
	bodies.append(b_root)
	tags.append("ROOT")
	var lane2 := _mk_lane("mvroot")
	lane2.phys_hook = func(l: Lane, _d: float):
		cam_root.position = Vector2(float(l.phys) / 60.0, 0.0)
		cam_root.zoom = Vector2(1.0 + 0.05 * float(l.phys), 1.0)
		cl.offset = Vector2(float(l.phys), 0.0)
	for i in range(30):
		await physics_frame
	var vals: Array = []
	for b in bodies:
		vals.append(_v(b.position))
	var eq_exact := true
	var eq4 := true
	for i in range(1, bodies.size()):
		if bodies[i].position != bodies[0].position:
			eq_exact = false
		if _v(bodies[i].position) != _v(bodies[0].position):
			eq4 = false
	var names := "|".join(tags)
	# C2 (r85 critic): read back the V2 camera and the ROOT CanvasLayer
	# writes — unwitnessed, both could be dropped and the row still passes.
	_finish("names=%s pos=[%s] eq_exact=%d eq_4dp=%d root_ct=%s v2cam[pos=%s zoom=%s] cloff=%s" % [
		names, "|".join(vals), int(eq_exact), int(eq4), _v(root.canvas_transform.origin),
		_v(v2cam.position), _v(v2cam.zoom), _v(cl.offset)])

# ------------------------------------------------------- vp_subcam

func _arm_vp_subcam() -> void:
	var sv := SubViewport.new()
	sv.name = "SV"
	sv.size = Vector2i(320, 180)
	root.add_child(sv)
	_nodes.append(sv)
	var root_cam := _mk_cam(root, Vector2.ZERO)
	root_cam.make_current()
	var sub_cam := _mk_cam(sv, Vector2(40, 0))
	sub_cam.make_current()
	await _settle()
	var r0 := root.canvas_transform
	var s0 := sv.canvas_transform
	var sv_cam_is := sv.get_camera_2d() == sub_cam
	var root_cam_is := root.get_camera_2d() == root_cam
	root_cam.position = Vector2(100, 0)
	await _settle()
	var r1 := root.canvas_transform
	var s1 := sv.canvas_transform
	sub_cam.position = Vector2(80, 20)
	await _settle()
	var r2 := root.canvas_transform
	var s2 := sv.canvas_transform
	var sub_only := (s1 == s0) and (s2 != s1)
	var root_only := (r1 != r0) and (r2 == r1)
	_finish("root_vpr=%s sub_vpr=%s r0=%s s0=%s r1=%s s1=%s r2=%s s2=%s cams[sv=%d root=%d] iso[sub_only=%d root_only=%d]" % [
		str(root.get_visible_rect().size), str(sv.get_visible_rect().size),
		_t(r0), _t(s0), _t(r1), _t(s1), _t(r2), _t(s2),
		int(sv_cam_is), int(root_cam_is), int(sub_only), int(root_only)])

# ------------------------------------------------------- par_layer

func _arm_par_layer() -> void:
	var cam := _mk_cam(root, Vector2.ZERO)
	cam.make_current()
	var pl := ParallaxLayer.new()
	pl.name = "PL"
	root.add_child(pl)
	_nodes.append(pl)
	var ch := _mk_node2d(pl, Vector2.ZERO, "PC")
	await _settle()
	var rows: Array = []
	rows.append("p0[wc=%s]" % _v(ch.get_global_transform_with_canvas().origin))
	pl.motion_scale = Vector2(0.5, 0.5)
	await _settle()
	rows.append("ms05[cam0 wc=%s lp=%s]" % [_v(ch.get_global_transform_with_canvas().origin), _v(pl.position)])
	cam.position = Vector2(64, 0)
	await _settle()
	rows.append("cam64[wc=%s lp=%s]" % [_v(ch.get_global_transform_with_canvas().origin), _v(pl.position)])
	cam.position = Vector2(128, 0)
	await _settle()
	rows.append("cam128[wc=%s lp=%s]" % [_v(ch.get_global_transform_with_canvas().origin), _v(pl.position)])
	pl.motion_mirroring = Vector2(100, 0)
	await _settle()
	rows.append("mirror100[mm=%s cam128 wc=%s lp=%s]" % [_v(pl.motion_mirroring),
		_v(ch.get_global_transform_with_canvas().origin), _v(pl.position)])
	cam.position = Vector2(150, 0)
	await _settle()
	rows.append("cam150mirror[wc=%s lp=%s]" % [_v(ch.get_global_transform_with_canvas().origin), _v(pl.position)])
	pl.motion_offset = Vector2(10, 0)
	await _settle()
	rows.append("moff10[mo=%s wc=%s lp=%s]" % [_v(pl.motion_offset),
		_v(ch.get_global_transform_with_canvas().origin), _v(pl.position)])
	pl.motion_mirroring = Vector2.ZERO
	pl.motion_offset = Vector2.ZERO
	await _settle()
	# the intended setup: ParallaxBackground (CanvasLayer) parent
	rows.append("has_pbg=%d" % int(ClassDB.class_exists("ParallaxBackground")))
	if ClassDB.class_exists("ParallaxBackground"):
		var pbg: Node = ClassDB.instantiate("ParallaxBackground")
		pbg.name = "PBG"
		root.add_child(pbg)
		_nodes.append(pbg)
		var pl2 := ParallaxLayer.new()
		pl2.name = "PL2"
		pbg.add_child(pl2)
		_nodes.append(pl2)
		var ch2 := _mk_node2d(pl2, Vector2.ZERO, "PC2")
		pl2.motion_scale = Vector2(0.5, 0.5)
		cam.position = Vector2.ZERO
		await _settle()
		rows.append("pbg0[follow=%d wc=%s lp=%s]" % [int(pbg.follow_viewport_enabled),
			_v(ch2.get_global_transform_with_canvas().origin), _v(pl2.position)])
		cam.position = Vector2(64, 0)
		await _settle()
		rows.append("pbg64[wc=%s lp=%s fin=%s]" % [_v(ch2.get_global_transform_with_canvas().origin),
			_v(pl2.position), _t(pbg.get_final_transform())])
		cam.position = Vector2(128, 0)
		await _settle()
		rows.append("pbg128[wc=%s lp=%s]" % [_v(ch2.get_global_transform_with_canvas().origin),
			_v(pl2.position)])
		pl2.motion_mirroring = Vector2(100, 0)
		await _settle()
		rows.append("pbgmirror[mm=%s wc=%s lp=%s]" % [_v(pl2.motion_mirroring),
			_v(ch2.get_global_transform_with_canvas().origin),
			_v(pl2.position)])
		pl2.motion_offset = Vector2(10, 0)
		await _settle()
		rows.append("pbgmoff[mo=%s wc=%s lp=%s]" % [_v(pl2.motion_offset),
			_v(ch2.get_global_transform_with_canvas().origin),
			_v(pl2.position)])
		pl2.motion_offset = Vector2.ZERO
		pl2.motion_mirroring = Vector2.ZERO
		pl2.motion_scale = Vector2(1.0, 1.0)
		await _settle()
		rows.append("pbgms1[wc=%s lp=%s]" % [_v(ch2.get_global_transform_with_canvas().origin),
			_v(pl2.position)])
		pl2.motion_scale = Vector2(0.0, 0.0)
		await _settle()
		rows.append("pbgms0[wc=%s lp=%s]" % [_v(ch2.get_global_transform_with_canvas().origin),
			_v(pl2.position)])
		pl2.motion_scale = Vector2(0.5, 0.5)
		cam.zoom = Vector2(2, 2)
		await _settle()
		rows.append("pbgz2[ct=%s wc=%s lp=%s ign=%d]" % [_v(root.canvas_transform.origin),
			_v(ch2.get_global_transform_with_canvas().origin), _v(pl2.position),
			int(pbg.scroll_ignore_camera_zoom)])
		cam.zoom = Vector2.ONE
		await _settle()
	# under a CanvasLayer with follow_viewport_enabled=true (no ParallaxBackground)
	var cl := CanvasLayer.new()
	cl.name = "CL"
	cl.layer = 5
	cl.follow_viewport_enabled = true
	root.add_child(cl)
	_nodes.append(cl)
	var pl3 := ParallaxLayer.new()
	pl3.name = "PL3"
	cl.add_child(pl3)
	_nodes.append(pl3)
	var ch3 := _mk_node2d(pl3, Vector2.ZERO, "PC3")
	pl3.motion_scale = Vector2(0.5, 0.5)
	await _settle()
	rows.append("cl_follow[wc=%s lp=%s]" % [_v(ch3.get_global_transform_with_canvas().origin), _v(pl3.position)])
	var cl_nofollow := CanvasLayer.new()
	cl_nofollow.name = "CL2"
	cl_nofollow.layer = 6
	root.add_child(cl_nofollow)
	_nodes.append(cl_nofollow)
	var pl4 := ParallaxLayer.new()
	pl4.name = "PL4"
	cl_nofollow.add_child(pl4)
	_nodes.append(pl4)
	var ch4 := _mk_node2d(pl4, Vector2.ZERO, "PC4")
	pl4.motion_scale = Vector2(0.5, 0.5)
	await _settle()
	rows.append("cl_nofollow[wc=%s lp=%s]" % [_v(ch4.get_global_transform_with_canvas().origin), _v(pl4.position)])
	_finish("cam=%s ms=%s mm=%s mo=%s rows=[%s]" % [_v(cam.position), _v(pl.motion_scale),
		_v(pl.motion_mirroring), _v(pl.motion_offset), "|".join(rows)])

# ------------------------------------------------------- par_2d

func _arm_par_2d() -> void:
	var cam := _mk_cam(root, Vector2.ZERO)
	cam.make_current()
	var p2 := Parallax2D.new()
	p2.name = "P2"
	p2.scroll_scale = Vector2(0.5, 0.5)
	root.add_child(p2)
	_nodes.append(p2)
	await _settle()
	var rows: Array = []
	rows.append("d0[off=%s wc=%s]" % [_v(p2.scroll_offset), _v(p2.get_global_transform_with_canvas().origin)])
	cam.position = Vector2(64, 0)
	await _settle()
	rows.append("cam64[off=%s wc=%s]" % [_v(p2.scroll_offset), _v(p2.get_global_transform_with_canvas().origin)])
	p2.ignore_camera_scroll = true
	await _settle()
	rows.append("ignore[off=%s wc=%s]" % [_v(p2.scroll_offset), _v(p2.get_global_transform_with_canvas().origin)])
	p2.ignore_camera_scroll = false
	p2.repeat_size = Vector2(100, 0)
	p2.repeat_times = 3
	await _settle()
	rows.append("rep100x3[off=%s wc=%s]" % [_v(p2.scroll_offset), _v(p2.get_global_transform_with_canvas().origin)])
	cam.position = Vector2(150, 0)
	await _settle()
	rows.append("cam150rep[off=%s wc=%s]" % [_v(p2.scroll_offset), _v(p2.get_global_transform_with_canvas().origin)])
	p2.follow_viewport = true
	await _settle()
	rows.append("follow[off=%s wc=%s]" % [_v(p2.scroll_offset), _v(p2.get_global_transform_with_canvas().origin)])
	p2.screen_offset = Vector2(7, 3)
	await _settle()
	rows.append("screen_off[off=%s wc=%s]" % [_v(p2.scroll_offset), _v(p2.get_global_transform_with_canvas().origin)])
	# C4 (r85 critic): pin the writes themselves — rep/fv/so could be
	# dropped without changing any emitted wc.
	_finish("cam=%s rep=%sx%d fv=%d so=%s ign=%d rows=[%s]" % [_v(cam.position),
		_v(p2.repeat_size), p2.repeat_times, int(p2.follow_viewport),
		_v(p2.screen_offset), int(p2.ignore_camera_scroll), "|".join(rows)])

# ------------------------------------------------------- par_phase

func _arm_par_phase() -> void:
	var cam := _mk_cam(root, Vector2.ZERO)
	cam.make_current()
	var pl := ParallaxLayer.new()
	pl.name = "PL"
	root.add_child(pl)
	_nodes.append(pl)
	var ch := _mk_node2d(pl, Vector2.ZERO, "PC")
	pl.motion_scale = Vector2(0.5, 0.5)
	var p2 := Parallax2D.new()
	p2.name = "P2"
	p2.scroll_scale = Vector2(0.5, 0.5)
	root.add_child(p2)
	_nodes.append(p2)
	var pbg: Node = ClassDB.instantiate("ParallaxBackground")
	pbg.name = "PBG"
	root.add_child(pbg)
	_nodes.append(pbg)
	var pbl := ParallaxLayer.new()
	pbl.name = "PBL"
	pbg.add_child(pbl)
	_nodes.append(pbl)
	var pbc := _mk_node2d(pbl, Vector2.ZERO, "PBC")
	pbl.motion_scale = Vector2(0.5, 0.5)
	await _settle()
	var out: Array = []
	var camref := cam
	var chref := ch
	var p2ref := p2
	var pblref := pbl
	await _phase_probe("PL", func(k: int): camref.position = Vector2(64.0 * k, 0.0),
		func() -> String: return "cam=%s pl=%s p2=%s pbl=%s pbc=%s" % [
			_v(root.canvas_transform.origin),
			_v(chref.get_global_transform_with_canvas().origin),
			_v(p2ref.get_global_transform_with_canvas().origin),
			_v(pblref.position),
			_v(pbc.get_global_transform_with_canvas().origin)], 2, out)
	_finish("".join(out))

# ------------------------------------------------------- diagnostics

func _arm_diag_delta() -> void:
	var lane := _mk_lane("delta")
	var pf_d: Array = []
	var proc_d: Array = []
	lane.phys_hook = func(l: Lane, d: float):
		if l.phys <= 5:
			pf_d.append("%.9f" % d)
	lane.idle_hook = func(l: Lane, d: float):
		if l.idle <= 5:
			proc_d.append("%.9f" % d)
	while lane.phys <= 5:
		await process_frame
	var same := true
	for i in range(1, pf_d.size()):
		if pf_d[i] != pf_d[0]:
			same = false
	_finish("pf_deltas=[%s] same=%d idle_deltas=[%s] pf=%d proc=%d" % [
		"|".join(pf_d), int(same), "|".join(proc_d), Engine.get_physics_frames(),
		Engine.get_process_frames()])

func _arm_diag_world_step() -> void:
	var sv := SubViewport.new()
	sv.name = "SVD"
	sv.size = Vector2i(64, 64)
	root.add_child(sv)
	_nodes.append(sv)
	await process_frame
	var b := _mk_body(sv, Vector2(0, 0), "BD")
	var start := b.position
	for i in range(10):
		await physics_frame
	_finish("world_own=%d start=%s after10=%s moved=%d contacts=%d" % [
		int(sv.world_2d != null), _v(start), _v(b.position),
		int(b.position != start), b.get_contact_count()])

func _arm_diag_draw() -> void:
	var sink: Array = []
	var dt := DrawTag.new()
	dt.name = "TD"
	dt.tag = "TD"
	dt.sink = sink
	root.add_child(dt)
	_nodes.append(dt)
	var lane := _mk_lane("drawer")
	lane.phys_hook = func(l: Lane, _d: float):
		if l.phys <= 3:
			dt.queue_redraw()
	while lane.phys <= 4:
		await process_frame
	_finish("draws=%d seq=%s" % [dt.draws, "|".join(sink)])

func _arm_diag_cam_internal() -> void:
	var cam := _mk_cam(root, Vector2.ZERO)
	cam.make_current()
	await _settle()
	var out: Array = []
	var camref := cam
	var w := _mk_lane("W")
	var o := _mk_lane("O")
	o.process_priority = 100
	w.phys_hook = func(l: Lane, _d: float):
		if l.phys >= 1 and l.phys <= 2:
			camref.position = Vector2(10.0 * l.phys, 0.0)
			out.append("W.w%d[%s after=%s]" % [l.phys, _stamp(), _v(root.canvas_transform.origin)])
	o.phys_hook = func(l: Lane, _d: float):
		if l.phys >= 1 and l.phys <= 2:
			out.append("O.w%d[%s sees=%s]" % [l.phys, _stamp(), _v(root.canvas_transform.origin)])
	o.idle_hook = func(l: Lane, _d: float):
		if l.idle >= 1 and l.idle <= 2:
			out.append("O.i%d[%s sees=%s]" % [l.idle, _stamp(), _v(root.canvas_transform.origin)])
	while w.phys <= 3:
		await process_frame
	await process_frame
	out.append("PRIO2")
	# second phase: process_callback = PHYSICS
	camref.process_callback = Camera2D.CAMERA2D_PROCESS_PHYSICS
	camref.position = Vector2.ZERO
	await _settle()
	var w2 := _mk_lane("W2")
	var o2 := _mk_lane("O2")
	o2.process_priority = 100
	w2.phys_hook = func(l: Lane, _d: float):
		if l.phys >= 1 and l.phys <= 2:
			camref.position = Vector2(20.0 * l.phys, 0.0)
			out.append("W2.w%d[%s after=%s]" % [l.phys, _stamp(), _v(root.canvas_transform.origin)])
	o2.phys_hook = func(l: Lane, _d: float):
		if l.phys >= 1 and l.phys <= 2:
			out.append("O2.w%d[%s sees=%s]" % [l.phys, _stamp(), _v(root.canvas_transform.origin)])
	o2.idle_hook = func(l: Lane, _d: float):
		if l.idle >= 1 and l.idle <= 2:
			out.append("O2.i%d[%s sees=%s]" % [l.idle, _stamp(), _v(root.canvas_transform.origin)])
	while w2.phys <= 3:
		await process_frame
	await process_frame
	_finish("prio[w=%d o=%d] %s" % [w.process_priority, o.process_priority, " ".join(out)])

func _arm_diag_stretch() -> void:
	var n := _mk_node2d(root, Vector2(300, 200), "N")
	var cl := CanvasLayer.new()
	cl.name = "CL"
	cl.layer = 2
	root.add_child(cl)
	_nodes.append(cl)
	var lc := _mk_node2d(cl, Vector2(300, 200), "LC")
	var cam := _mk_cam(root, Vector2(100, 50), Vector2(2, 2))
	cam.make_current()
	await _settle()
	var rows: Array = []
	rows.append("mode=%d factor=%.1f" % [root.content_scale_mode, root.content_scale_factor])
	rows.append("base[final=%s ct=%s wc=%s sc=%s vx=%s lwc=%s]" % [
		_t(root.get_final_transform()), _t(root.canvas_transform),
		_t(n.get_global_transform_with_canvas()), _t(n.get_screen_transform()),
		_t(n.get_viewport_transform()), _t(lc.get_global_transform_with_canvas())])
	root.content_scale_factor = 2.0
	await _settle()
	rows.append("f2[final=%s ct=%s wc=%s sc=%s vx=%s lwc=%s]" % [
		_t(root.get_final_transform()), _t(root.canvas_transform),
		_t(n.get_global_transform_with_canvas()), _t(n.get_screen_transform()),
		_t(n.get_viewport_transform()), _t(lc.get_global_transform_with_canvas())])
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	await _settle()
	rows.append("ci[final=%s ct=%s wc=%s sc=%s vx=%s lwc=%s]" % [
		_t(root.get_final_transform()), _t(root.canvas_transform),
		_t(n.get_global_transform_with_canvas()), _t(n.get_screen_transform()),
		_t(n.get_viewport_transform()), _t(lc.get_global_transform_with_canvas())])
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_VIEWPORT
	await _settle()
	rows.append("vp[final=%s ct=%s wc=%s sc=%s vx=%s lwc=%s]" % [
		_t(root.get_final_transform()), _t(root.canvas_transform),
		_t(n.get_global_transform_with_canvas()), _t(n.get_screen_transform()),
		_t(n.get_viewport_transform()), _t(lc.get_global_transform_with_canvas())])
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	root.content_scale_factor = 1.0
	await _settle()
	rows.append("restored[final=%s ct=%s wc=%s]" % [
		_t(root.get_final_transform()), _t(root.canvas_transform),
		_t(n.get_global_transform_with_canvas())])
	_finish("stretch=[%s]" % "|".join(rows))
