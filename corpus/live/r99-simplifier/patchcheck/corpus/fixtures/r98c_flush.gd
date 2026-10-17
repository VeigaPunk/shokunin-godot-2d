extends SceneTree
# r98c author probe — the r98-boundary corrected `queue_redraw` flush
# granularity, measured in the battery's OWN launch shape.
#
# Launch (battery convention):
#   godot --headless --path <proj> --script res://r98c_flush.gd -- --arm=flush
#
# Every CASES row is launched as
#   godot --headless --path <scratch> --script res://<fixture> -- <flags>
# so the engine-level pacing flags r98-boundary used to reach a multi-tick
# process frame (--fixed-fps 1|30, --frame-delay 100) are NOT available to a
# row. This probe reaches that regime in-process: a node blocks the process
# step with OS.delay_msec(D) — what --frame-delay does at the engine level.
# At D=80 ms and 60 physics ticks/s about 5 physics steps run per process
# frame, the regime in which the two flush hypotheses separate:
#
#   per-process-frame flush (r98-scout L1 as first written): draws == frames
#   per-physics-step flush (r98-boundary):                    draws == ticks
#
# Every key is a boolean or a small integer; no wall-clock value, RID, object
# id or frame number is printed, so the row is byte-stable while the regime is
# only required to be multi-tick (>=2 ticks in a frame), which an 80 ms
# process-step block guarantees with a >4x margin at 60 tps.

var arm := ""
var _items: PackedStringArray = []

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"flush": await _arm_flush()
		_: _fail("unknown_arm")

func _fail(reason: String) -> void:
	print("FAIL r98c %s reason=%s" % [arm, reason])
	quit(1)

func _it(key: String, value: String) -> void:
	_items.append("%s=%s" % [key, value])
	print("R98C %s %s=%s" % [arm, key, value])

func _pass() -> void:
	print("PASS r98c %s %s" % [arm, " ".join(_items)])
	quit()

func _b(v: bool) -> String:
	return "1" if v else "0"

func _frames(n: int) -> void:
	for i in n:
		await process_frame

# Process-step pacer: blocks the process step so the next physics loop has
# several ticks of accumulated wall time (the in-process --frame-delay).
class PACE:
	extends Node2D
	var delay_ms := 0
	var active := false
	func _process(_dt: float) -> void:
		if active and delay_ms > 0:
			OS.delay_msec(delay_ms)

# Subject: queues from a physics tick and counts draws per process frame and
# per physics frame.
class SUBJ:
	extends Node2D
	var q_pending := false
	var q_every := false
	var queue_from_draw := false
	var draws := 0
	var q_pf := -1
	var q_ph := -1
	var d_pf := -1
	var d_ph := -1
	var draw_pf_counts := {}
	func _physics_process(_dt: float) -> void:
		if q_pending:
			q_pending = false
			q_pf = Engine.get_process_frames()
			q_ph = Engine.get_physics_frames()
			queue_redraw()
		if q_every:
			queue_redraw()
	func _draw() -> void:
		draws += 1
		d_pf = Engine.get_process_frames()
		d_ph = Engine.get_physics_frames()
		draw_pf_counts[d_pf] = int(draw_pf_counts.get(d_pf, 0)) + 1
		if queue_from_draw:
			queue_redraw()

# Plain draw counter (hide-timing phases).
class HID:
	extends Node2D
	var draws := 0
	func _draw() -> void:
		draws += 1

# Tick controller: queue the target on tick A, hide it on tick B.
class HC:
	extends Node2D
	var target: Node2D
	var armed := false
	var tick := 0
	var t_queue := 0
	var t_hide := 1
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

# --------------------------------------------------------------- flush arm

func _arm_flush() -> void:
	var pace := PACE.new()
	pace.delay_ms = 80
	pace.active = true
	root.add_child(pace)

	var bounded := true

	# (1) one queue from a physics tick: same PROCESS frame, same PHYSICS
	# frame. The physics-frame equality is the per-tick witness — a flush that
	# waited for the end of the process frame would read a later tick counter.
	var t := SUBJ.new()
	root.add_child(t)
	await _frames(2)
	t.q_pending = true
	var g := 0
	while t.q_pf < 0 and g < 240:
		await process_frame
		g += 1
	if g >= 240:
		bounded = false
	g = 0
	while t.d_pf < 0 and g < 240:
		await process_frame
		g += 1
	if g >= 240:
		bounded = false
	var same_pf: bool = t.q_pf >= 0 and t.q_pf == t.d_pf
	var d_pf_delta: int = t.d_pf - t.q_pf
	var d_phf_delta: int = t.d_ph - t.q_ph

	# (2) queue every physics tick for 6 process frames. In the paced regime
	# several ticks share one process frame, so the per-tick flush shows up as
	# draws == ticks (not draws == frames).
	var d0: int = t.draws
	t.draw_pf_counts.clear()
	var frames_with_tick := 0
	var multitick_frames := 0
	var last_ph: int = Engine.get_physics_frames()
	var ticks_window := 0
	t.q_every = true
	for i in 6:
		await process_frame
		var ph: int = Engine.get_physics_frames()
		if ph > last_ph:
			frames_with_tick += 1
			ticks_window += ph - last_ph
			if ph - last_ph >= 2:
				multitick_frames += 1
		last_ph = ph
	t.q_every = false
	await process_frame
	var draws_window: int = t.draws - d0
	var max_per_pf := 0
	for k in t.draw_pf_counts.keys():
		max_per_pf = max(max_per_pf, int(t.draw_pf_counts[k]))

	# (3) self-queue from inside _draw is swallowed
	d0 = t.draws
	t.queue_from_draw = true
	t.queue_redraw()
	await _frames(3)
	t.queue_from_draw = false
	var selfq_draws: int = t.draws - d0

	# (4) three synchronous queues in one process step coalesce to one draw
	# even when that frame carries several ticks.
	var s := SUBJ.new()
	root.add_child(s)
	await _frames(1)
	d0 = s.draws
	s.queue_redraw()
	s.queue_redraw()
	s.queue_redraw()
	await _frames(1)
	var sync_coalesce_n: int = s.draws - d0

	# (5) synchronous queue + hide in one process step: the pending draw is
	# dropped (same-flush condition).
	var a := HID.new()
	root.add_child(a)
	await _frames(1)
	d0 = a.draws
	a.queue_redraw()
	a.visible = false
	await _frames(1)
	var hide_sync_n: int = a.draws - d0
	a.visible = true
	await _frames(1)

	# (6) queue on tick A, hide on tick B, A and B inside ONE process frame:
	# the draw still happens, because tick A's flush precedes tick B's hide.
	var h := HID.new()
	var ctl := HC.new()
	ctl.target = h
	ctl.t_queue = 0
	ctl.t_hide = 1
	root.add_child(h)
	root.add_child(ctl)
	await _frames(2)
	d0 = h.draws
	ctl.tick = 0
	ctl.armed = true
	g = 0
	while not ctl.done and g < 240:
		await process_frame
		g += 1
	if g >= 240:
		bounded = false
	await _frames(2)
	var hide_ticksep_n: int = h.draws - d0
	var hide_ticksep_same_frame: bool = ctl.pf_queue >= 0 and ctl.pf_queue == ctl.pf_hide

	# (7) queue while hidden across >=1 tick: dropped; showing draws once
	h.visible = true
	await _frames(1)
	d0 = h.draws
	h.visible = false
	h.queue_redraw()
	await physics_frame
	await process_frame
	var hidden_across_tick_n: int = h.draws - d0
	h.visible = true
	await _frames(2)
	var show_after_tick_n: int = h.draws - d0

	pace.active = false

	_it("multitick_frames_ge2", _b(multitick_frames >= 1))
	_it("draws_eq_ticks", _b(draws_window == ticks_window and ticks_window > 0))
	_it("draws_gt_frames", _b(draws_window > frames_with_tick))
	_it("max_draws_per_pf_ge2", _b(max_per_pf >= 2))
	_it("same_pf", _b(same_pf))
	_it("d_pf_delta", str(d_pf_delta))
	_it("d_phf_delta", str(d_phf_delta))
	_it("selfq_draws", str(selfq_draws))
	_it("sync_coalesce_n", str(sync_coalesce_n))
	_it("hide_sync_n", str(hide_sync_n))
	_it("hide_ticksep_n", str(hide_ticksep_n))
	_it("hide_ticksep_same_frame", _b(hide_ticksep_same_frame))
	_it("hidden_across_tick_n", str(hidden_across_tick_n))
	_it("show_after_tick_n", str(show_after_tick_n))
	_it("bounded", _b(bounded))
	_pass()
