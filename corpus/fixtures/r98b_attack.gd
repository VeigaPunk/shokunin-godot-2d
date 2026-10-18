extends SceneTree
# r98b boundary FROZEN attack probe — attacks the r98 scout's CanvasItem claims
# (queue_redraw flush L1, skew decomposition L3/L4/L5, clip refusal L9) under
# quiet / >=12-hog load / --fixed-fps 1|30|120, and hunts UNSTATED tick modes
# (the r95 lesson: check anything claimed "stable" across ticks).
#
# Launch shape (battery convention):
#   godot --headless [--fixed-fps N] --path proj --script res://r98b_attack.gd -- --arm=<name> [--var=..]
# Every arm prints `R98B <arm> <key>=<value>` lines and one final
# `PASS r98b <arm> <key=value> ...` line (arm name on the PASS line).
# No RIDs / object ids / addresses / wall-clock values are printed.
#
# Arms:
#   qflush      queue_redraw from _physics_process: same-PROCESS-frame flush,
#               per-frame coalescing across ticks, self-queue swallow, and the
#               "queue then hide" suppression when the hide lands in a LATER
#               process frame than the queue (tick-separated hide)
#   qorder      draw-callback order sampled per frame: tree-order queue,
#               reverse queue, 3-tick staggered queue (FIFO vs tree order),
#               and a tick-phase-offset stagger
#   latch       the scout's context-dependent redraw latch (redraw_context),
#               replicated + tick-offset / immediate / second-write variants
#   gskew       global_skew / global_rotation / global_scale round-trip under a
#               NON-UNIFORM parent (shear decomposition; L5 unstated mode)
#   skewgrid    exact-equality grid for Node2D transform == Transform2D(r,s,k,p)
#               and == R*K*S, incl. degenerate/negative scales and |skew| > PI
#   epssweep    zero/degenerate-scale global_scale readback vs parent scale
#               (is the ~2e-5 epsilon constant or scale-dependent?)
#   clipmatrix  clip_children refusal matrix: prior value x 99, == MAX, negatives,
#               method vs property path, recovery, repeated refusal
#   notifyphase transform-notification flush timing vs tick/frame waits (L10)
#   visphase    the visibility-chain draw counts with physics-frame waits (L8)
#   env         launch-mode fingerprint (informative; not an authorable row)

var arm := ""
var opt := ""
var _items: PackedStringArray = []

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
		elif a.begins_with("--var="):
			opt = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"qflush": await _arm_qflush()
		"qorder": await _arm_qorder()
		"latch": await _arm_latch()
		"gskew": await _arm_gskew()
		"skewgrid": await _arm_skewgrid()
		"epssweep": await _arm_epssweep()
		"clipmatrix": await _arm_clipmatrix()
		"notifyphase": await _arm_notifyphase()
		"visphase": await _arm_visphase()
		"env": await _arm_env()
		_: _fail("unknown_arm")

# --------------------------------------------------------------- utilities

func _fail(reason: String) -> void:
	print("FAIL r98b %s reason=%s" % [arm, reason])
	quit(1)

func _it(key: String, value: String) -> void:
	_items.append("%s=%s" % [key, value])
	print("R98B %s %s=%s" % [arm, key, value])

func _pass() -> void:
	print("PASS r98b %s %s" % [arm, " ".join(_items)])
	quit()

func _frames(n: int) -> void:
	for i in n:
		await process_frame

func _b(v: bool) -> String:
	return "1" if v else "0"

func _v2(v: Vector2) -> String:
	return "(%.4f,%.4f)" % [v.x, v.y]

func _approx(a: float, b: float) -> bool:
	return absf(a - b) < 1e-4

func _groups(s: String) -> String:
	return ",".join(s.split("|", false))

func _all_same_nonempty(s: String, want: String) -> bool:
	var n := 0
	for g in s.split("|", false):
		if g == "":
			continue
		if g != want:
			return false
		n += 1
	return n > 0

func _tm(t: Transform2D) -> String:
	return "(%.4f,%.4f;%.4f,%.4f;%.4f,%.4f)" % [t.x.x, t.x.y, t.y.x, t.y.y, t.origin.x, t.origin.y]

# Sample one draw-order frame: each `await process_frame` resumes at the next
# frame's process_frame signal; the sink then holds the previous frame's
# separator + draws (the controller appends "|" from _process, before the flush).
func _sample(sink: Array, n: int) -> String:
	var parts: Array = []
	for i in n:
		await process_frame
		parts.append("".join(sink))
		sink.clear()
	return "|".join(parts)

# --------------------------------------------------------------- qflush

class QF:
	extends Node2D
	var q_pending := false
	var q_every := false
	var queue_from_draw := false
	var draws := 0
	var q_pf := -1
	var d_pf := -1
	var draw_pf_counts := {}
	func _physics_process(_dt: float) -> void:
		if q_pending:
			q_pending = false
			q_pf = Engine.get_process_frames()
			queue_redraw()
		if q_every:
			queue_redraw()
	func _draw() -> void:
		draws += 1
		d_pf = Engine.get_process_frames()
		draw_pf_counts[d_pf] = int(draw_pf_counts.get(d_pf, 0)) + 1
		if queue_from_draw:
			queue_redraw()

class QH:
	extends Node2D
	var draws := 0
	func _draw() -> void:
		draws += 1

class QHC:
	extends Node2D
	var target: Node2D
	var armed := false
	var tick := 0
	var t_queue := -1
	var t_hide := -1
	var pf_queue := -1
	var pf_hide := -1
	var done := false
	func _physics_process(_dt: float) -> void:
		if target == null or not armed or done:
			return
		if tick == t_queue:
			pf_queue = Engine.get_process_frames()
			target.queue_redraw()
		elif tick == t_hide:
			pf_hide = Engine.get_process_frames()
			target.visible = false
			done = true
		tick += 1

func _arm_qflush() -> void:
	var t := QF.new()
	t.set_physics_process(true)
	root.add_child(t)
	await _frames(1)
	# (1) a single queue from a physics tick: does the draw land in the same
	# PROCESS frame as the tick that queued it?
	var d0 := t.draws
	t.q_pf = -1
	t.d_pf = -1
	t.q_pending = true
	var guard := 0
	while t.q_pf < 0 and guard < 240:
		await process_frame
		guard += 1
	guard = 0
	while t.d_pf < 0 and guard < 240:
		await process_frame
		guard += 1
	_it("same_pf", _b(t.q_pf == t.d_pf and t.q_pf >= 0))
	_it("d_pf_delta", str(t.d_pf - t.q_pf))
	_it("d_n", str(t.draws - d0))
	# (2) queue every tick for 6 process frames: draws must equal the number of
	# frames that contained >= 1 tick (coalescing is per PROCESS frame)
	d0 = t.draws
	t.draw_pf_counts.clear()
	var frames_with_tick := 0
	var last_ph := Engine.get_physics_frames()
	var ticks_window := 0
	t.q_every = true
	for i in 6:
		await process_frame
		var ph := Engine.get_physics_frames()
		if ph > last_ph:
			frames_with_tick += 1
			ticks_window += ph - last_ph
		last_ph = ph
	t.q_every = false
	await process_frame
	var max_per_pf := 0
	for k in t.draw_pf_counts.keys():
		max_per_pf = max(max_per_pf, int(t.draw_pf_counts[k]))
	_it("coalesce_draws", str(t.draws - d0))
	_it("frames_with_tick", str(frames_with_tick))
	_it("ticks_window", str(ticks_window))
	_it("coalesce_eq", _b(t.draws - d0 == frames_with_tick))
	_it("max_draws_per_pf", str(max_per_pf))
	_it("distinct_draw_pf", str(t.draw_pf_counts.size()))
	# (3) self-queue from inside _draw is swallowed
	d0 = t.draws
	t.queue_from_draw = true
	t.queue_redraw()
	await _frames(4)
	t.queue_from_draw = false
	_it("selfq_draws", str(t.draws - d0))
	# (4) queue on tick A, hide on tick B: suppressed only if B is in the SAME
	# process frame as A (tick-separated hide)
	var h := QH.new()
	var ctl := QHC.new()
	ctl.target = h
	ctl.t_queue = 0
	ctl.t_hide = 1
	ctl.set_physics_process(false)
	root.add_child(h)
	root.add_child(ctl)
	ctl.set_physics_process(false)
	await _frames(3)
	d0 = h.draws
	ctl.tick = 0
	ctl.set_physics_process(true)
	ctl.armed = true
	var g2 := 0
	while not ctl.done and g2 < 240:
		await process_frame
		g2 += 1
	await _frames(2)
	_it("hide_span_pf", str(ctl.pf_hide - ctl.pf_queue))
	_it("hide_same_frame", _b(ctl.pf_hide == ctl.pf_queue))
	_it("hide_ticksep_n", str(h.draws - d0))
	# (5) queue while hidden across >=1 tick: the pending draw must be dropped;
	# showing afterwards draws exactly once
	h.visible = true
	await _frames(1)
	d0 = h.draws
	h.visible = false
	h.queue_redraw()
	await physics_frame
	await process_frame
	_it("hidden_across_tick_n", str(h.draws - d0))
	h.visible = true
	await _frames(2)
	_it("show_after_tick_n", str(h.draws - d0))
	_pass()

# --------------------------------------------------------------- qorder

class OT:
	extends Node2D
	var tag := ""
	var sink: Array = []
	func _draw() -> void:
		sink.append(tag)

class OC:
	extends Node2D
	var targets: Array = []
	var mode := ""
	var tick := 0
	var tick0 := 5
	var separator := false
	func _process(_dt: float) -> void:
		if separator:
			sink.append("|")
		if mode == "tree":
			for t in targets:
				t.queue_redraw()
		elif mode == "rev":
			for i in range(targets.size() - 1, -1, -1):
				(targets[i] as Node2D).queue_redraw()
	func _physics_process(_dt: float) -> void:
		if mode == "stagger":
			if tick == 0:
				(targets[2] as Node2D).queue_redraw()
			elif tick == 1:
				(targets[1] as Node2D).queue_redraw()
			elif tick == 2:
				(targets[0] as Node2D).queue_redraw()
		elif mode == "stagger_off":
			if tick == tick0:
				(targets[2] as Node2D).queue_redraw()
			elif tick == tick0 + 1:
				(targets[1] as Node2D).queue_redraw()
			elif tick == tick0 + 2:
				(targets[0] as Node2D).queue_redraw()
		tick += 1
	var sink: Array = []

func _arm_qorder() -> void:
	var sink: Array = []
	var host := Node2D.new()
	root.add_child(host)
	var a := OT.new(); a.tag = "A"; a.sink = sink
	var b := OT.new(); b.tag = "B"; b.sink = sink
	var c := OT.new(); c.tag = "C"; c.sink = sink
	host.add_child(a); host.add_child(b); host.add_child(c)
	var ctl := OC.new()
	ctl.targets = [a, b, c]
	ctl.sink = sink
	ctl.set_physics_process(true)
	ctl.separator = true
	host.add_child(ctl)
	await _frames(2)
	# tree-order queue every frame
	ctl.mode = "tree"
	var s_tree: String = await _sample(sink, 6)
	_it("tree", s_tree)
	# reverse queue every frame
	ctl.mode = "rev"
	var s_rev: String = await _sample(sink, 6)
	_it("rev", s_rev)
	# 3 consecutive ticks queue C,B,A (FIFO would give CBA, tree order ABC)
	ctl.mode = "stagger"
	ctl.tick = 0
	var s_stag: String = await _sample(sink, 12)
	_it("stagger", s_stag)
	# same, starting at tick offset 5 (tick-phase probe)
	ctl.mode = "stagger_off"
	ctl.tick = 0
	var s_off: String = await _sample(sink, 40)
	_it("stagger_off", s_off)
	# flattened queue order (strip separators)
	var flat := (s_stag + s_off).replace("|", "")
	_it("flat", flat)
	_it("tree_groups", _groups(s_tree))
	_it("rev_groups", _groups(s_rev))
	_it("stag_groups", _groups(s_stag))
	_it("stagoff_groups", _groups(s_off))
	_it("tree_stable", _b(_all_same_nonempty(s_tree, "ABC")))
	_it("rev_stable", _b(_all_same_nonempty(s_rev, "CBA")))
	_pass()

# --------------------------------------------------------------- latch

class LT:
	extends Node2D
	var draws := 0
	func _draw() -> void:
		draws += 1

func _arm_latch() -> void:
	var v := opt if opt != "" else "canon"
	match v:
		"canon":
			# byte-level replication of the scout's redraw_context trio
			var a := LT.new()
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
			var b := LT.new()
			root.add_child(b)
			await _frames(3)
			b.scale = Vector2(2, 2)
			await _frames(3)
			var b0 := b.draws
			b.skew = 0.2
			await _frames(4)
			_it("control_n", str(b.draws - b0))
			var c := LT.new()
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
		"t1", "t3":
			var a := LT.new()
			root.add_child(a)
			await _frames(3)
			a.set_oversampling_with_scale(CanvasItem.OVERSAMPLING_WITH_SCALE_ENABLED)
			await _frames(3)
			a.scale = Vector2(2, 2)
			await _frames(3)
			var a0 := a.draws
			var ticks := 1 if v == "t1" else 3
			for i in ticks:
				await physics_frame
			a.skew = 0.2
			await _frames(4)
			_it("trigger_n", str(a.draws - a0))
			_it("tick_wait", str(ticks))
		"imm":
			var a := LT.new()
			root.add_child(a)
			await _frames(3)
			a.set_oversampling_with_scale(CanvasItem.OVERSAMPLING_WITH_SCALE_ENABLED)
			await _frames(3)
			var a0 := a.draws
			a.scale = Vector2(2, 2)
			a.skew = 0.2
			await _frames(4)
			_it("trigger_n", str(a.draws - a0))
		"second":
			var a := LT.new()
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
			var a1 := a.draws
			a.position = Vector2(3, 4)
			await _frames(4)
			_it("second_n", str(a.draws - a1))
		_:
			_fail("unknown_var")
	_it("var", v)
	_pass()

# --------------------------------------------------------------- gskew

func _arm_gskew() -> void:
	var p := Node2D.new()
	p.rotation = 0.7
	p.scale = Vector2(3, 0.25)
	root.add_child(p)
	var c := Node2D.new()
	p.add_child(c)
	await _frames(1)
	# global_skew round-trip under a non-uniform parent
	c.global_skew = 0.3
	_it("gs_rt", _b(_approx(c.get_global_skew(), 0.3)))
	_it("gs_local", "%.4f" % c.skew)
	_it("gs_local_rot", "%.4f" % c.rotation)
	_it("gs_global", "%.4f" % c.get_global_skew())
	# global_rotation round-trip under the same parent
	c.global_rotation = 0.9
	_it("gr_rt", _b(_approx(c.get_global_rotation(), 0.9)))
	_it("gr_local", "%.4f" % c.rotation)
	_it("gr_local_skew", "%.4f" % c.skew)
	_it("gr_global", "%.4f" % c.get_global_rotation())
	# global_scale round-trip
	c.global_scale = Vector2(2, 2)
	var gsc := c.get_global_scale()
	_it("gsc_rt", _b(_approx(gsc.x, 2.0) and _approx(gsc.y, 2.0)))
	_it("gsc_local", _v2(c.scale))
	_it("gsc_global", _v2(gsc))
	# uniform parent control
	var p2 := Node2D.new()
	p2.rotation = 0.7
	p2.scale = Vector2(2, 2)
	root.add_child(p2)
	var c2 := Node2D.new()
	p2.add_child(c2)
	await _frames(1)
	c2.global_skew = 0.3
	_it("gs_rt_uniform", _b(_approx(c2.get_global_skew(), 0.3)))
	_it("gs_local_uniform", "%.4f" % c2.skew)
	c2.global_rotation = 0.9
	_it("gr_rt_uniform", _b(_approx(c2.get_global_rotation(), 0.9)))
	_it("gr_local_uniform", "%.4f" % c2.rotation)
	_pass()

# --------------------------------------------------------------- skewgrid

func _arm_skewgrid() -> void:
	var n := Node2D.new()
	root.add_child(n)
	await _frames(1)
	var rots: Array = [0.0, 0.3, PI / 2.0, -1.2, 4.0]
	var scales: Array = [Vector2(1, 1), Vector2(2, 3), Vector2(-1, 1), Vector2(1, -1),
			Vector2(-2, -3), Vector2(0, 0), Vector2(0, 1), Vector2(1, 0)]
	var skews: Array = [0.0, 0.5, -0.5, PI / 4.0, 2.5]
	var ctor_fail := 0
	var ctor_fail_z := 0
	var ctor_fail_nz := 0
	var rks_fail := 0
	var rks_fail_z := 0
	var rks_fail_nz := 0
	var first_fail := "-"
	var idx := 0
	for r in rots:
		for s in scales:
			for k in skews:
				n.rotation = r
				n.scale = s
				n.skew = k
				var t := n.get_transform()
				var expect := Transform2D(r, s, k, Vector2.ZERO)
				var rk := Transform2D(r, Vector2.ONE, 0.0, Vector2.ZERO) \
						* Transform2D(0.0, Vector2.ONE, k, Vector2.ZERO) \
						* Transform2D(0.0, s, 0.0, Vector2.ZERO)
				var degenerate: bool = s.x == 0.0 or s.y == 0.0
				if t != expect:
					ctor_fail += 1
					if degenerate:
						ctor_fail_z += 1
					else:
						ctor_fail_nz += 1
					if first_fail == "-":
						first_fail = "ctor@%d(r=%.2f,s=%.2f,%.2f,k=%.2f)" % [idx, r, s.x, s.y, k]
				if expect != rk:
					rks_fail += 1
					if degenerate:
						rks_fail_z += 1
					else:
						rks_fail_nz += 1
					if first_fail == "-":
						first_fail = "rks@%d" % idx
				idx += 1
	_it("combos", str(idx))
	_it("ctor_fail_n", str(ctor_fail))
	_it("ctor_fail_z", str(ctor_fail_z))
	_it("ctor_fail_nz", str(ctor_fail_nz))
	_it("rks_fail_n", str(rks_fail))
	_it("rks_fail_z", str(rks_fail_z))
	_it("rks_fail_nz", str(rks_fail_nz))
	_it("first_fail", first_fail)
	# degenerate-scale detail at 8 decimals: the stored local transform itself
	# is epsilon-clamped (the ~1e-5 that the scout saw only via global_scale)
	var z := Node2D.new()
	root.add_child(z)
	z.scale = Vector2(0, 0)
	var zt := z.get_transform()
	_it("z_tf00", "(%.8f,%.8f;%.8f,%.8f)" % [zt.x.x, zt.x.y, zt.y.x, zt.y.y])
	_it("z_ctor_eq00", _b(zt == Transform2D(0.0, Vector2(0, 0), 0.0, Vector2.ZERO)))
	z.scale = Vector2(0, 1)
	zt = z.get_transform()
	_it("z_tf01", "(%.8f,%.8f;%.8f,%.8f)" % [zt.x.x, zt.x.y, zt.y.x, zt.y.y])
	_it("z_ctor_eq01", _b(zt == Transform2D(0.0, Vector2(0, 1), 0.0, Vector2.ZERO)))
	# y-basis convention for negative skew and skew > PI
	n.rotation = 0.0
	n.scale = Vector2.ONE
	for k in [-0.5, 2.5]:
		n.skew = k
		_it("y_%s" % str(k).replace("-", "m").replace(".", "_"), _tm(n.get_transform()))
	# local rotation raw vs transform: rotation=4.0 must not be normalised
	n.rotation = 4.0
	n.skew = 0.0
	n.scale = Vector2.ONE
	_it("rot4", _tm(n.get_transform()))
	_pass()

# --------------------------------------------------------------- epssweep

func _arm_epssweep() -> void:
	var parts: Array = []
	var eps_exact: Array = []
	for ps in [0.001, 0.5, 1.0, 2.0, 100.0]:
		var p := Node2D.new()
		p.scale = Vector2(ps, ps)
		root.add_child(p)
		var c := Node2D.new()
		p.add_child(c)
		await _frames(1)
		for s in [Vector2(0, 0), Vector2(0, 1), Vector2(1, 0)]:
			c.scale = s
			var gs := c.get_global_scale()
			parts.append("ps=%.3f s=(%.0f,%.0f)->(%.6f,%.6f)" % [ps, s.x, s.y, gs.x, gs.y])
			if s == Vector2(0, 0):
				eps_exact.append("ps=%.3f->%.9f" % [ps, gs.x])
		root.remove_child(p)
		p.free()
	_it("eps", ";".join(parts))
	_it("eps_exact", ",".join(eps_exact))
	# zero scale + rotation + skew: does the epsilon survive, and do the angle
	# readbacks stay the set values?
	var p2 := Node2D.new()
	p2.rotation = 0.7
	p2.scale = Vector2(2, 2)
	root.add_child(p2)
	var c2 := Node2D.new()
	p2.add_child(c2)
	await _frames(1)
	c2.rotation = 0.4
	c2.skew = 0.5
	c2.scale = Vector2(0, 0)
	var gs2 := c2.get_global_scale()
	_it("zero_rot_skew", "(%.6f,%.6f)|grot=%.4f|gskew=%.4f|lscale=(%.4f,%.4f)" % [
		gs2.x, gs2.y, c2.get_global_rotation(), c2.get_global_skew(), c2.scale.x, c2.scale.y])
	# local scale readback for a degenerate set (no parent)
	var n := Node2D.new()
	root.add_child(n)
	n.scale = Vector2(0, 0)
	_it("local_zero", _v2(n.scale) + "|tf=" + _tm(n.get_transform()))
	_pass()

# --------------------------------------------------------------- clipmatrix

func _arm_clipmatrix() -> void:
	var n := Node2D.new()
	root.add_child(n)
	await _frames(1)
	var stays: Array = []
	for prior in [0, 1, 2]:
		n.set_clip_children_mode(prior)
		n.clip_children = 99
		stays.append("p%d->%d" % [prior, n.get_clip_children_mode()])
	_it("stay99", ",".join(stays))
	n.set_clip_children_mode(1)
	n.clip_children = 3
	_it("stay3", str(n.get_clip_children_mode()))
	n.set_clip_children_mode(1)
	n.clip_children = 2
	_it("ok2", str(n.get_clip_children_mode()))
	var negs: Array = []
	for v in [-1, -2, -3, -5, -2147483648]:
		n.set_clip_children_mode(v)
		negs.append("%d->%d" % [v, n.get_clip_children_mode()])
	_it("neg", ",".join(negs))
	n.set_clip_children_mode(0)
	n.clip_children = -2
	_it("neg_prop", str(n.get_clip_children_mode()))
	n.clip_children = 1
	_it("recover", str(n.get_clip_children_mode()))
	n.clip_children = 99
	_it("stay_after_neg", str(n.get_clip_children_mode()))
	n.clip_children = 99
	_it("stay_repeat", str(n.get_clip_children_mode()))
	_it("max_const", str(ClassDB.class_get_integer_constant("CanvasItem", "CLIP_CHILDREN_MAX")))
	_it("err_lines_expected", "6")
	_pass()

# --------------------------------------------------------------- notifyphase

class NTP:
	extends Node2D
	var counts := {}
	func _notification(what: int) -> void:
		counts[what] = int(counts.get(what, 0)) + 1

func _nset(a: Dictionary, b: Dictionary) -> String:
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

func _arm_notifyphase() -> void:
	var p := NTP.new()
	var c := NTP.new()
	root.add_child(p)
	p.add_child(c)
	p.set_notify_transform(true)
	p.set_notify_local_transform(true)
	c.set_notify_transform(true)
	c.set_notify_local_transform(true)
	await _frames(1)
	# move the parent, then wait ONE PHYSICS FRAME and read the child delta;
	# then wait one process frame and read again (flush is frame-scoped?)
	var cb := c.counts.duplicate(true)
	p.position = Vector2(2, 2)
	await physics_frame
	_it("move_tick", _nset(cb, c.counts))
	await process_frame
	_it("move_frame", _nset(cb, c.counts))
	# reparent into a CanvasLayer at a tick offset; same two-stage read
	var cl := CanvasLayer.new()
	root.add_child(cl)
	await _frames(1)
	var t := NTP.new()
	t.set_notify_transform(true)
	t.set_notify_local_transform(true)
	root.add_child(t)
	await _frames(1)
	var tb := t.counts.duplicate(true)
	t.reparent(cl)
	await physics_frame
	_it("rep_tick", _nset(tb, t.counts))
	await process_frame
	_it("rep_frame", _nset(tb, t.counts))
	_it("cl_node", _b(t.get_canvas_layer_node() != null))
	# reparent back
	tb = t.counts.duplicate(true)
	t.reparent(root)
	await physics_frame
	_it("back_tick", _nset(tb, t.counts))
	await process_frame
	_it("back_frame", _nset(tb, t.counts))
	_it("cl_node_back", _b(t.get_canvas_layer_node() != null))
	_pass()

# --------------------------------------------------------------- visphase

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

func _arm_visphase() -> void:
	# exact replication of the scout's vis_chain ladder (process-frame waits)
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
	var n1 := int(c.notif.get(31, 0))
	var s1 := c.vis_sig
	c.hide()
	await _frames(1)
	_it("hide_noop", str(int(c.notif.get(31, 0)) - n1 + c.vis_sig - s1))
	c.show()
	await _frames(1)
	_it("show_notif", str(int(c.notif.get(31, 0)) - n1))
	_it("draws_total", str(p.draws + c.draws))
	# tick-waited variant: the SAME ladder and the SAME measurement points, but
	# every wait is a physics frame + a process frame (does the count change when
	# ticks are forced between steps?)
	var p2 := VC.new()
	var c2 := VC.new()
	root.add_child(p2)
	p2.add_child(c2)
	await physics_frame
	await process_frame
	await physics_frame
	await process_frame
	var td0 := c2.draws
	p2.visible = false
	await physics_frame
	await process_frame
	c2.queue_redraw()
	await physics_frame
	await process_frame
	await physics_frame
	await process_frame
	_it("tick_hidden_queue_n", str(c2.draws - td0))
	p2.visible = true
	await physics_frame
	await process_frame
	_it("tick_restore_n", str(c2.draws - td0))
	c2.hide()
	await physics_frame
	await process_frame
	var tn1 := int(c2.notif.get(31, 0))
	var ts1 := c2.vis_sig
	c2.hide()
	await physics_frame
	await process_frame
	_it("tick_hide_noop", str(int(c2.notif.get(31, 0)) - tn1 + c2.vis_sig - ts1))
	c2.show()
	await physics_frame
	await process_frame
	_it("tick_show_notif", str(int(c2.notif.get(31, 0)) - tn1))
	_it("tick_draws_total", str(p2.draws + c2.draws))
	_pass()

# --------------------------------------------------------------- env

func _arm_env() -> void:
	var p0 := Engine.get_process_frames()
	var ph0 := Engine.get_physics_frames()
	for i in 5:
		await process_frame
	_it("pf5", str(Engine.get_process_frames() - p0))
	_it("ph5", str(Engine.get_physics_frames() - ph0))
	_it("tps", str(Engine.physics_ticks_per_second))
	_it("ver", str(Engine.get_version_info()["string"]))
	_it("headless", DisplayServer.get_name())
	var n := Node2D.new()
	root.add_child(n)
	await _frames(1)
	_it("vp", _v2(n.get_viewport_rect().size))
	_it("iqfr_method", _b(ClassDB.class_has_method("CanvasItem", "is_queued_for_redraw")))
	_pass()
