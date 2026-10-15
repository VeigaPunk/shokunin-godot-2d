extends SceneTree
# r100-boundary probe — phase / ordering / startup-mode artifacts around the
# r100 GUI input-routing lattice (frozen scout probe: proj/r100_gui.gd dd826f6e…).
# One arm per process:
#   godot --headless [--fixed-fps N] --path proj --script res://r100b_phase.gd -- --arm=<arm>
# Arms: cursorphase hoverphase dragphase coalesce velphase startup flushpos
# Prints exactly one `PASS r100b_phase <arm> ...` line. No object ids / RIDs / timestamps.

var arm := ""
var _nodes: Array = []
var _init_pf := -1
var _init_ph := -1
var _init_t := -1

class Sink extends Control:
	var tag := ""
	var log: Array = []
	var in_log: Array = []
	var seq_log: Array = []
	var handled := false
	var mm_n := 0
	var mm_rel := Vector2.ZERO
	var drag_data: Variant = null
	var drag_calls := 0

	func _gui_input(event: InputEvent) -> void:
		log.append("%s:%s" % [tag, _ev(event)])
		seq_log.append("g:%s" % _ev(event))
		if handled:
			get_viewport().set_input_as_handled()
		if event is InputEventMouseMotion:
			mm_n += 1
			mm_rel += (event as InputEventMouseMotion).relative

	func _input(event: InputEvent) -> void:
		if in_log.size() < 24:
			in_log.append("%s:%s" % [tag, _ev(event)])
		seq_log.append("i:%s" % _ev(event))

	func _ev(event: InputEvent) -> String:
		if event is InputEventMouseButton:
			var e := event as InputEventMouseButton
			return "mb(b=%d,p=%d,dc=%d,bm=%d,pos=%.1f,%.1f,gpos=%.1f,%.1f)" % [
				e.button_index, int(e.pressed), int(e.double_click), e.button_mask,
				e.position.x, e.position.y, e.global_position.x, e.global_position.y]
		if event is InputEventMouseMotion:
			var e := event as InputEventMouseMotion
			return "mm(bm=%d,pos=%.1f,%.1f,gpos=%.1f,%.1f,rel=%.1f,%.1f,vel=%.1f,%.1f)" % [
				e.button_mask, e.position.x, e.position.y, e.global_position.x, e.global_position.y,
				e.relative.x, e.relative.y, e.velocity.x, e.velocity.y]
		if event is InputEventKey:
			var e := event as InputEventKey
			return "key(k=%d,p=%d)" % [e.keycode, int(e.pressed)]
		if event is InputEventScreenTouch:
			var e := event as InputEventScreenTouch
			return "st(i=%d,p=%d,dt=%d,pos=%.1f,%.1f)" % [
				e.index, int(e.pressed), int(e.double_tap), e.position.x, e.position.y]
		if event is InputEventScreenDrag:
			var e := event as InputEventScreenDrag
			return "sd(i=%d,pos=%.1f,%.1f,rel=%.1f,%.1f)" % [
				e.index, e.position.x, e.position.y, e.relative.x, e.relative.y]
		return event.get_class()

	func _get_drag_data(_at_position: Vector2) -> Variant:
		drag_calls += 1
		return drag_data


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_init_pf = Engine.get_process_frames()
	_init_ph = Engine.get_physics_frames()
	_init_t = Time.get_ticks_msec()
	call_deferred("_run")


func _run() -> void:
	match arm:
		"cursorphase":
			await _a_cursorphase()
		"hoverphase":
			await _a_hoverphase()
		"dragphase":
			await _a_dragphase()
		"coalesce":
			await _a_coalesce()
		"velphase":
			await _a_velphase()
		"startup":
			await _a_startup()
		"flushpos":
			await _a_flushpos()
		"orderin":
			await _a_orderin()
		"dblclick":
			await _a_dblclick()
		_:
			print("PASS r100b_phase unknown arm=%s" % arm)
	await _cleanup()
	quit(0)


func _cleanup() -> void:
	for c in root.get_children():
		c.free()
	for n in _nodes:
		if is_instance_valid(n):
			n.free()
	_nodes.clear()
	await process_frame


func _mk_sink(tag: String, pos: Vector2, size: Vector2, filt: int) -> Sink:
	var s := Sink.new()
	_nodes.append(s)
	s.tag = tag
	s.name = tag
	s.position = pos
	s.size = size
	s.mouse_filter = filt
	return s


func _mb(pos: Vector2, pressed: bool, mask := 0) -> InputEventMouseButton:
	var e := InputEventMouseButton.new()
	e.button_index = MOUSE_BUTTON_LEFT
	e.pressed = pressed
	e.button_mask = mask
	e.position = pos
	e.global_position = pos
	return e


func _mm(pos: Vector2, rel: Vector2, mask := 0) -> InputEventMouseMotion:
	var e := InputEventMouseMotion.new()
	e.position = pos
	e.global_position = pos
	e.relative = rel
	e.button_mask = mask
	return e


func _fmt(arr: Array) -> String:
	return "-" if arr.is_empty() else "[%s]" % "|".join(arr)


func _tag_of(c: Control) -> String:
	if c == null:
		return "null"
	if c.name != "":
		return str(c.name)
	return c.get_class()


# ---------------------------------------------------------------- cursorphase
# Is the cursor write synchronous with parse_input_event, or does it happen at
# an input flush / frame boundary? (the scout sampled once, after one frame)
func _a_cursorphase() -> void:
	var s := _mk_sink("S", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	root.add_child(s)
	await process_frame
	var out: Array = []
	out.append("init=%s" % str(root.get_mouse_position()))
	Input.parse_input_event(_mm(Vector2(20, 20), Vector2(20, 20)))
	out.append("mm_imm=%s" % str(root.get_mouse_position()))
	Input.flush_buffered_events()
	out.append("mm_flush=%s" % str(root.get_mouse_position()))
	await process_frame
	out.append("mm_f1=%s" % str(root.get_mouse_position()))
	await process_frame
	out.append("mm_f2=%s" % str(root.get_mouse_position()))
	Input.parse_input_event(_mb(Vector2(24, 24), true))
	out.append("mb_imm=%s held=%d" % [
		str(root.get_mouse_position()), int(Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT))])
	Input.flush_buffered_events()
	out.append("mb_flush=%s held=%d" % [
		str(root.get_mouse_position()), int(Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT))])
	await process_frame
	out.append("mb_f1=%s held=%d" % [
		str(root.get_mouse_position()), int(Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT))])
	root.push_input(_mm(Vector2(30, 30), Vector2(6, 6)))
	out.append("push_imm=%s" % str(root.get_mouse_position()))
	await process_frame
	out.append("push_f1=%s" % str(root.get_mouse_position()))
	# parse a motion from a non-default global_position: which field drives it?
	var mm2 := _mm(Vector2(70, 70), Vector2(10, 10))
	mm2.global_position = Vector2(52, 52)
	Input.parse_input_event(mm2)
	out.append("gpos_imm=%s" % str(root.get_mouse_position()))
	await process_frame
	out.append("gpos_f1=%s" % str(root.get_mouse_position()))
	# hover after parse motion (does the parse path update hover too?)
	out.append("hovered=%s" % _tag_of(root.gui_get_hovered_control()))
	print("PASS r100b_phase cursorphase %s" % " ".join(out))


# ---------------------------------------------------------------- hoverphase
# Is the hover pick synchronous with push_input, or deferred to a frame phase?
func _a_hoverphase() -> void:
	var a := _mk_sink("A", Vector2.ZERO, Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	root.add_child(a)
	var ev: Array = []
	a.mouse_entered.connect(func() -> void: ev.append("in@%d" % Engine.get_process_frames()))
	a.mouse_exited.connect(func() -> void: ev.append("out@%d" % Engine.get_process_frames()))
	await process_frame
	var out: Array = []
	out.append("h0=%s ev=%s pf=%d" % [
		_tag_of(root.gui_get_hovered_control()), _fmt(ev), Engine.get_process_frames()])
	root.push_input(_mm(Vector2(8, 8), Vector2(8, 8)))
	out.append("h_imm=%s ev=%s" % [_tag_of(root.gui_get_hovered_control()), _fmt(ev)])
	await process_frame
	out.append("h_f1=%s ev=%s" % [_tag_of(root.gui_get_hovered_control()), _fmt(ev)])
	await process_frame
	out.append("h_f2=%s ev=%s" % [_tag_of(root.gui_get_hovered_control()), _fmt(ev)])
	root.push_input(_mm(Vector2(60, 60), Vector2(52, 52)))
	out.append("leave_imm=%s ev=%s" % [_tag_of(root.gui_get_hovered_control()), _fmt(ev)])
	await process_frame
	out.append("leave_f1=%s ev=%s" % [_tag_of(root.gui_get_hovered_control()), _fmt(ev)])
	root.push_input(_mm(Vector2(8, 8), Vector2(-52, -52)))
	await process_frame
	root.push_input(_mb(Vector2(8, 8), true))
	out.append("press_imm=%s" % _tag_of(root.gui_get_hovered_control()))
	await process_frame
	out.append("press_f1=%s" % _tag_of(root.gui_get_hovered_control()))
	root.push_input(_mb(Vector2(8, 8), false))
	await process_frame
	out.append("rel_f1=%s" % _tag_of(root.gui_get_hovered_control()))
	print("PASS r100b_phase hoverphase %s" % " ".join(out))


# ---------------------------------------------------------------- dragphase
# Drag-threshold accumulation: per delivered event or per frame? Is the
# accumulated quantity sum(|relative|) or net displacement from the press?
func _a_dragphase() -> void:
	var LM := MOUSE_BUTTON_MASK_LEFT
	var a := _mk_sink("A", Vector2.ZERO, Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	a.drag_data = {"tag": "fromA"}
	root.add_child(a)
	await process_frame
	var out: Array = []
	# (1) scout d7 shape: 3 x rel(4,4), one motion per frame
	root.push_input(_mb(Vector2(4, 4), true, LM))
	var acc := ""
	for i in range(3):
		root.push_input(_mm(Vector2(8 + i * 4, 8 + i * 4), Vector2(4, 4), LM))
		await process_frame
		acc += "%d:%d " % [i + 1, int(root.gui_is_dragging())]
	out.append("dp_multiframe[%s] calls=%d" % [acc, a.drag_calls])
	root.push_input(_mb(Vector2(16, 16), false))
	await process_frame
	# (2) same three motions, all inside one frame (no await between)
	var seq := ""
	root.push_input(_mb(Vector2(4, 4), true, LM))
	for i in range(3):
		root.push_input(_mm(Vector2(8 + i * 4, 8 + i * 4), Vector2(4, 4), LM))
		seq += "%d:%d " % [i + 1, int(root.gui_is_dragging())]
	out.append("dp_sameframe[%s] calls=%d" % [seq, a.drag_calls])
	root.push_input(_mb(Vector2(16, 16), false))
	await process_frame
	# (3) sign test, same frame: rel(+6,0) then rel(-6,0) -> sum|rel|=12, net=0
	var c0 := a.drag_calls
	root.push_input(_mb(Vector2(8, 8), true, LM))
	root.push_input(_mm(Vector2(14, 8), Vector2(6, 0), LM))
	root.push_input(_mm(Vector2(8, 8), Vector2(-6, 0), LM))
	out.append("dp_sign_same drag=%d calls=%d" % [int(root.gui_is_dragging()), a.drag_calls - c0])
	root.push_input(_mb(Vector2(8, 8), false))
	await process_frame
	# (4) sign test, one motion per frame
	c0 = a.drag_calls
	root.push_input(_mb(Vector2(8, 8), true, LM))
	root.push_input(_mm(Vector2(14, 8), Vector2(6, 0), LM))
	await process_frame
	var mid := int(root.gui_is_dragging())
	root.push_input(_mm(Vector2(8, 8), Vector2(-6, 0), LM))
	await process_frame
	out.append("dp_sign_multi mid=%d after=%d calls=%d" % [
		mid, int(root.gui_is_dragging()), a.drag_calls - c0])
	root.push_input(_mb(Vector2(8, 8), false))
	await process_frame
	# (5) net displacement crosses threshold while sum(|rel|) also crosses:
	#     rel(+8,0) then rel(+8,0): sum 16, net 16, press-dist 16
	c0 = a.drag_calls
	root.push_input(_mb(Vector2(8, 8), true, LM))
	root.push_input(_mm(Vector2(16, 8), Vector2(8, 0), LM))
	root.push_input(_mm(Vector2(24, 8), Vector2(8, 0), LM))
	out.append("dp_net16 drag=%d calls=%d" % [int(root.gui_is_dragging()), a.drag_calls - c0])
	root.push_input(_mb(Vector2(24, 8), false))
	await process_frame
	# (6) single motion rel(10.5,0) -> drag (scout d2 shape, re-measured here)
	c0 = a.drag_calls
	root.push_input(_mb(Vector2(8, 8), true, LM))
	root.push_input(_mm(Vector2(18.5, 8), Vector2(10.5, 0), LM))
	out.append("dp_10p5 drag=%d calls=%d" % [int(root.gui_is_dragging()), a.drag_calls - c0])
	root.push_input(_mb(Vector2(18.5, 8), false))
	await process_frame
	# (7) three motions in one frame, each rel(3,3): sum|rel| = 12.7 -> drag if per-event
	c0 = a.drag_calls
	root.push_input(_mb(Vector2(8, 8), true, LM))
	for i in range(3):
		root.push_input(_mm(Vector2(11 + i * 3, 11 + i * 3), Vector2(3, 3), LM))
	out.append("dp_small3 drag=%d calls=%d" % [int(root.gui_is_dragging()), a.drag_calls - c0])
	root.push_input(_mb(Vector2(20, 20), false))
	await process_frame
	# (8) relative-only: press(8,8), motion at pos(8,8) with rel(30,0)
	c0 = a.drag_calls
	root.push_input(_mb(Vector2(8, 8), true, LM))
	root.push_input(_mm(Vector2(8, 8), Vector2(30, 0), LM))
	out.append("dp_rel_only drag=%d calls=%d" % [int(root.gui_is_dragging()), a.drag_calls - c0])
	root.push_input(_mb(Vector2(8, 8), false))
	await process_frame
	# (9) position-only: press(8,8), motion at pos(40,8) with rel(0,0)
	c0 = a.drag_calls
	root.push_input(_mb(Vector2(8, 8), true, LM))
	root.push_input(_mm(Vector2(40, 8), Vector2(0, 0), LM))
	out.append("dp_pos_only drag=%d calls=%d" % [int(root.gui_is_dragging()), a.drag_calls - c0])
	root.push_input(_mb(Vector2(40, 8), false))
	await process_frame
	# (10) position-driven threshold: pos-only motions at 18 then 19
	c0 = a.drag_calls
	root.push_input(_mb(Vector2(8, 8), true, LM))
	root.push_input(_mm(Vector2(18, 8), Vector2(0, 0), LM))
	var at10 := int(root.gui_is_dragging())
	root.push_input(_mm(Vector2(19, 8), Vector2(0, 0), LM))
	out.append("dp_pos_thresh at10=%d at11=%d calls=%d" % [
		at10, int(root.gui_is_dragging()), a.drag_calls - c0])
	root.push_input(_mb(Vector2(19, 8), false))
	await process_frame
	print("PASS r100b_phase dragphase %s" % " ".join(out))


# ---------------------------------------------------------------- coalesce
# Buffered (parsed) motion events: delivered 1:1 or coalesced? When?
func _a_coalesce() -> void:
	var s := _mk_sink("S", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	root.add_child(s)
	await process_frame
	var out: Array = []
	# two parsed motions back-to-back, no explicit flush
	s.log.clear(); s.mm_n = 0; s.mm_rel = Vector2.ZERO
	Input.parse_input_event(_mm(Vector2(10, 10), Vector2(10, 0)))
	Input.parse_input_event(_mm(Vector2(20, 10), Vector2(10, 0)))
	out.append("p2_imm n=%d rel=%s log=%s" % [s.mm_n, str(s.mm_rel), _fmt(s.log)])
	Input.flush_buffered_events()
	out.append("p2_flush n=%d rel=%s" % [s.mm_n, str(s.mm_rel)])
	await process_frame
	out.append("p2_f1 n=%d rel=%s log=%s" % [s.mm_n, str(s.mm_rel), _fmt(s.log)])
	# two parsed motions with an explicit flush between
	s.log.clear(); s.mm_n = 0; s.mm_rel = Vector2.ZERO
	Input.parse_input_event(_mm(Vector2(30, 10), Vector2(10, 0)))
	Input.flush_buffered_events()
	Input.parse_input_event(_mm(Vector2(40, 10), Vector2(10, 0)))
	out.append("p2_sep imm n=%d" % s.mm_n)
	Input.flush_buffered_events()
	out.append("p2_sep flush n=%d rel=%s log=%s" % [s.mm_n, str(s.mm_rel), _fmt(s.log)])
	await process_frame
	# two pushed motions in one frame
	s.log.clear(); s.mm_n = 0; s.mm_rel = Vector2.ZERO
	root.push_input(_mm(Vector2(50, 10), Vector2(10, 0)))
	root.push_input(_mm(Vector2(60, 10), Vector2(10, 0)))
	out.append("push2 imm n=%d rel=%s log=%s" % [s.mm_n, str(s.mm_rel), _fmt(s.log)])
	await process_frame
	out.append("push2_f1 n=%d rel=%s" % [s.mm_n, str(s.mm_rel)])
	print("PASS r100b_phase coalesce %s" % " ".join(out))


# ---------------------------------------------------------------- velphase
# Input.get_last_mouse_velocity(): push path vs parse path, time dependence.
func _a_velphase() -> void:
	var out: Array = []
	out.append("v0_none=%s screen=%s" % [
		str(Input.get_last_mouse_velocity()), str(Input.get_last_mouse_screen_velocity())])
	root.push_input(_mm(Vector2(10, 10), Vector2(5, 0)))
	out.append("v1_push=%s" % str(Input.get_last_mouse_velocity()))
	Input.parse_input_event(_mm(Vector2(20, 20), Vector2(10, 0)))
	out.append("v2_parse_imm=%s screen=%s" % [
		str(Input.get_last_mouse_velocity()), str(Input.get_last_mouse_screen_velocity())])
	await process_frame
	out.append("v3_f1=%s" % str(Input.get_last_mouse_velocity()))
	await process_frame
	out.append("v4_f2=%s" % str(Input.get_last_mouse_velocity()))
	await process_frame
	await process_frame
	Input.parse_input_event(_mm(Vector2(40, 40), Vector2(20, 0)))
	out.append("v5_parse2_imm=%s" % str(Input.get_last_mouse_velocity()))
	await process_frame
	out.append("v6_f1=%s" % str(Input.get_last_mouse_velocity()))
	print("PASS r100b_phase velphase %s" % " ".join(out))


# ---------------------------------------------------------------- startup
# Startup shape: frame counters at _initialize / _run / first frames, and the
# startup pick state (is anything hovered/focused before any input?).
func _a_startup() -> void:
	var out: Array = []
	out.append("init pf=%d ph=%d t=%d" % [_init_pf, _init_ph, _init_t])
	out.append("run pf=%d ph=%d t=%d" % [
		Engine.get_process_frames(), Engine.get_physics_frames(), Time.get_ticks_msec()])
	var a := _mk_sink("A", Vector2.ZERO, Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	a.focus_mode = Control.FOCUS_ALL
	root.add_child(a)
	out.append("add h=%s owner=%s" % [
		_tag_of(root.gui_get_hovered_control()), _tag_of(root.gui_get_focus_owner())])
	for i in range(4):
		await process_frame
		out.append("f%d pf=%d ph=%d h=%s owner=%s" % [
			i + 1, Engine.get_process_frames(), Engine.get_physics_frames(),
			_tag_of(root.gui_get_hovered_control()), _tag_of(root.gui_get_focus_owner())])
	out.append("shape fps=%d max_fps=%d tps=%d scale=%.2f vis=%s win=%s final=%s" % [
		int(Engine.get_frames_per_second()), Engine.max_fps, Engine.physics_ticks_per_second,
		Engine.time_scale, str(root.get_visible_rect()), str(root.size),
		str(root.get_final_transform())])
	print("PASS r100b_phase startup %s" % " ".join(out))


# ---------------------------------------------------------------- flushpos
# Where in the frame does the implicit input flush that applies parsed events
# run?  A `process_frame` listener (connected before the parse) runs before the
# `await process_frame` continuation; comparing the two localizes the flush.
func _a_flushpos() -> void:
	var s := _mk_sink("S", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	root.add_child(s)
	await process_frame
	var out: Array = []
	var log: Array = []
	process_frame.connect(func() -> void: log.append("sig@%d=%s" % [
		Engine.get_process_frames(), str(root.get_mouse_position())]))
	out.append("pre=%s pf=%d" % [str(root.get_mouse_position()), Engine.get_process_frames()])
	Input.parse_input_event(_mm(Vector2(20, 20), Vector2(20, 20)))
	out.append("post_parse=%s" % str(root.get_mouse_position()))
	await process_frame
	out.append("after_await=%s log=%s" % [str(root.get_mouse_position()), _fmt(log)])
	# second event: does the signal listener of the *next* frame see it flushed?
	Input.parse_input_event(_mm(Vector2(44, 44), Vector2(24, 24)))
	out.append("post_parse2=%s" % str(root.get_mouse_position()))
	await process_frame
	out.append("after_await2=%s log=%s" % [str(root.get_mouse_position()), _fmt(log)])
	# explicit flush inside the frame, then the listener should see it this frame
	Input.parse_input_event(_mm(Vector2(12, 12), Vector2(-32, -32)))
	Input.flush_buffered_events()
	out.append("post_flush=%s" % str(root.get_mouse_position()))
	await process_frame
	out.append("after_await3=%s log=%s" % [str(root.get_mouse_position()), _fmt(log)])
	print("PASS r100b_phase flushpos %s" % " ".join(out))


# ---------------------------------------------------------------- orderin
# Interleaved `_input` / `_gui_input` delivery order (the pinned cells keep the
# two logs separate, so the cross-callback order is unmeasured there).
func _a_orderin() -> void:
	var a := _mk_sink("A", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	a.focus_mode = Control.FOCUS_ALL
	root.add_child(a)
	await process_frame
	var out: Array = []
	a.grab_focus()
	await process_frame
	a.seq_log.clear()
	root.push_input(_mb(Vector2(8, 8), true))
	await process_frame
	out.append("press[%s]" % _fmt(a.seq_log))
	a.seq_log.clear()
	root.push_input(_mm(Vector2(12, 12), Vector2(4, 4)))
	await process_frame
	out.append("motion[%s]" % _fmt(a.seq_log))
	a.seq_log.clear()
	var k := InputEventKey.new()
	k.keycode = KEY_A
	k.pressed = true
	root.push_input(k)
	await process_frame
	out.append("key[%s]" % _fmt(a.seq_log))
	a.seq_log.clear()
	var st := InputEventScreenTouch.new()
	st.index = 0
	st.pressed = true
	st.position = Vector2(8, 8)
	root.push_input(st)
	await process_frame
	out.append("touch[%s]" % _fmt(a.seq_log))
	a.handled = true
	a.seq_log.clear()
	root.push_input(_mb(Vector2(8, 8), true))
	await process_frame
	out.append("handled_press[%s]" % _fmt(a.seq_log))
	a.handled = false
	a.seq_log.clear()
	root.push_input(_mm(Vector2(20, 20), Vector2(8, 8)))
	root.push_input(_mb(Vector2(20, 20), true))
	await process_frame
	out.append("two_in_frame[%s]" % _fmt(a.seq_log))
	print("PASS r100b_phase orderin %s" % " ".join(out))


# ---------------------------------------------------------------- dblclick
# Is `double_click` computed for parsed (synthetic) events, or only carried
# when set by the caller?  (time-based computation would be mode-sensitive)
func _a_dblclick() -> void:
	var a := _mk_sink("A", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	root.add_child(a)
	await process_frame
	var out: Array = []
	for i in range(2):
		Input.parse_input_event(_mb(Vector2(8, 8), true))
		await process_frame
		Input.parse_input_event(_mb(Vector2(8, 8), false))
		await process_frame
	out.append("parsed_pair[%s]" % _fmt(a.log))
	a.log.clear()
	for i in range(2):
		root.push_input(_mb(Vector2(8, 8), true))
		root.push_input(_mb(Vector2(8, 8), false))
		await process_frame
	out.append("pushed_pair[%s]" % _fmt(a.log))
	a.log.clear()
	Input.parse_input_event(_mb(Vector2(8, 8), true))
	await process_frame
	out.append("parsed_third[%s]" % _fmt(a.log))
	print("PASS r100b_phase dblclick %s" % " ".join(out))
