extends SceneTree
# r100-scout scratch probe — Viewport/Control GUI input-routing + pointer-gesture lattice.
# One cell per process, exactly the battery's launch shape:
#   godot --headless --path <scratch> --script res://r100_gui.gd -- --arm=<cell>
# Prints one final `PASS r100_gui <cell> ...` line. No object ids / RIDs / timestamps.
# Cells: census routing hover motion localpos cursor drag touch subvp warp focus render osmeta

var _nodes: Array = []

class Sink extends Control:
	var tag := ""
	var log: Array = []
	var in_log: Array = []
	var handled := false
	var drag_data: Variant = null
	var drag_calls := 0
	var drag_at: Array = []
	var drop_log: Array = []
	var can_drop := true

	func _gui_input(event: InputEvent) -> void:
		log.append("%s:%s" % [tag, _ev(event)])
		if handled:
			get_viewport().set_input_as_handled()

	func _input(event: InputEvent) -> void:
		if in_log.size() < 24:
			in_log.append("%s:%s" % [tag, _ev(event)])

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

	func _get_drag_data(at_position: Vector2) -> Variant:
		drag_calls += 1
		drag_at.append("(%.1f,%.1f)" % [at_position.x, at_position.y])
		return drag_data

	func _can_drop_data(_at_position: Vector2, data: Variant) -> bool:
		drop_log.append("can(%s)" % _dtag(data))
		return can_drop

	func _drop_data(_at_position: Vector2, data: Variant) -> void:
		drop_log.append("drop(%s)" % _dtag(data))

	func _dtag(data: Variant) -> String:
		if data == null:
			return "null"
		if data is Dictionary and data.has("tag"):
			return str(data["tag"])
		return "<data>"


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var seq_arms := ['census', 'routing', 'hover', 'motion', 'localpos', 'cursor', 'clip', 'drag', 'touch', 'subvp', 'warp', 'focus', 'render', 'osmeta']
	var do_clean := 0
	for a in OS.get_cmdline_user_args():
		if a == "--clean=1":
			do_clean = 1
	for a in seq_arms:
		match a:
			"census":
				await _cell_census()
			"routing":
				await _cell_routing()
			"hover":
				await _cell_hover()
			"motion":
				await _cell_motion()
			"localpos":
				await _cell_localpos()
			"cursor":
				await _cell_cursor()
			"clip":
				await _cell_clip()
			"drag":
				await _cell_drag()
			"touch":
				await _cell_touch()
			"subvp":
				await _cell_subvp()
			"warp":
				await _cell_warp()
			"focus":
				await _cell_focus()
			"render":
				await _cell_render()
			"osmeta":
				await _cell_osmeta()
			_:
				pass
		if do_clean == 1:
			await _cleanup()
	print("SEQ_DONE clean=%d" % do_clean)
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


func _mb(pos: Vector2, pressed: bool, mask := 0, dc := false) -> InputEventMouseButton:
	var e := InputEventMouseButton.new()
	e.button_index = MOUSE_BUTTON_LEFT
	e.pressed = pressed
	e.button_mask = mask
	e.double_click = dc
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


func _click(pos: Vector2) -> void:
	root.push_input(_mb(pos, true))
	root.push_input(_mb(pos, false))


func _fmt(arr: Array) -> String:
	return "-" if arr.is_empty() else "[%s]" % "|".join(arr)


func _clr(sinks: Array) -> void:
	for s in sinks:
		(s as Sink).log.clear()


func _tag_of(c: Control) -> String:
	if c == null:
		return "null"
	if c.name != "":
		return str(c.name)
	return c.get_class()


func _method_map(o: Object, names: Array) -> String:
	var out: Array = []
	for m in names:
		out.append("%s=%d" % [m, int(o.has_method(m))])
	return "|".join(out)


func _own_props(o: Object) -> Array:
	var out: Array = []
	for p in o.get_property_list():
		if int(p.get("usage", 0)) & PROPERTY_USAGE_STORAGE:
			out.append(str(p["name"]))
	out.sort()
	return out


func _xform(x: Transform2D) -> String:
	return "(%.4f,%.4f;%.4f,%.4f;%.4f,%.4f)" % [x.x.x, x.y.x, x.x.y, x.y.y, x.origin.x, x.origin.y]


# ---------------------------------------------------------------- census
func _cell_census() -> void:
	var ctrl := Control.new()
	var label := Label.new()
	var button := Button.new()
	var panel := Panel.new()
	var ccontainer := Container.new()
	_nodes.append_array([ctrl, label, button, panel, ccontainer])
	var facts: Array = []
	facts.append("dv=%s" % DisplayServer.get_name())
	facts.append("vpsize=%s" % str(root.get_visible_rect().size))
	facts.append("final=%s" % _xform(root.get_final_transform()))
	facts.append("mf_ctrl=%d mf_label=%d mf_button=%d mf_panel=%d mf_container=%d" % [
		ctrl.mouse_filter, label.mouse_filter, button.mouse_filter, panel.mouse_filter,
		ccontainer.mouse_filter])
	facts.append("focus_mode_ctrl=%d" % ctrl.focus_mode)
	facts.append("vpmethods=[%s]" % _method_map(root, [
		"push_input", "push_unhandled_input", "gui_get_focus_owner",
		"gui_get_hovered_control", "gui_is_dragging", "gui_get_drag_data",
		"gui_release_focus", "set_input_as_handled", "is_input_handled",
		"get_mouse_position", "warp_mouse", "get_final_transform"]))
	facts.append("ctrlmethods=[%s]" % _method_map(ctrl, [
		"force_drag", "accept_event", "grab_focus", "has_focus",
		"release_focus", "get_local_mouse_position", "set_drag_preview"]))
	facts.append("inputmethods=[%s]" % _method_map(Input, [
		"warp_mouse", "get_mouse_position", "set_emulate_mouse_from_touch",
		"is_emulating_mouse_from_touch", "set_emulate_touch_from_mouse",
		"is_emulating_touch_from_mouse", "get_last_mouse_velocity",
		"get_last_mouse_screen_velocity", "parse_input_event",
		"flush_buffered_events", "is_mouse_button_pressed"]))
	facts.append("emul_mouse=%d emul_touch=%d" % [
		int(Input.is_emulating_mouse_from_touch()), int(Input.is_emulating_touch_from_mouse())])
	var mb := InputEventMouseButton.new()
	facts.append("mbprops=[%s]" % "|".join(_own_props(mb)))
	var mm := InputEventMouseMotion.new()
	facts.append("mmprops=[%s]" % "|".join(_own_props(mm)))
	var st := InputEventScreenTouch.new()
	facts.append("stprops=[%s]" % "|".join(_own_props(st)))
	var sd := InputEventScreenDrag.new()
	facts.append("sdprops=[%s]" % "|".join(_own_props(sd)))
	print("PASS r100_gui census %s" % " ".join(facts))


# ---------------------------------------------------------------- routing
func _cell_routing() -> void:
	var parent := _mk_sink("P", Vector2.ZERO, Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	var child := _mk_sink("C", Vector2.ZERO, Vector2(16, 16), Control.MOUSE_FILTER_STOP)
	parent.add_child(child)
	root.add_child(parent)
	await process_frame
	var out: Array = []
	_clr([parent, child])
	_click(Vector2(8, 8))
	await process_frame
	out.append("s1_cc[%s]%s" % [_fmt(child.log), _fmt(parent.log)])
	child.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_clr([parent, child])
	_click(Vector2(8, 8))
	await process_frame
	out.append("s2_ci[%s]%s" % [_fmt(child.log), _fmt(parent.log)])
	child.mouse_filter = Control.MOUSE_FILTER_PASS
	_clr([parent, child])
	_click(Vector2(8, 8))
	await process_frame
	out.append("s3_cp[%s]%s" % [_fmt(child.log), _fmt(parent.log)])
	child.handled = true
	_clr([parent, child])
	_click(Vector2(8, 8))
	await process_frame
	out.append("s4_ch[%s]%s" % [_fmt(child.log), _fmt(parent.log)])
	child.handled = false
	child.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.mouse_filter = Control.MOUSE_FILTER_PASS
	_clr([parent, child])
	_click(Vector2(8, 8))
	await process_frame
	out.append("s5_ci_pp[%s]%s" % [_fmt(child.log), _fmt(parent.log)])
	parent.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_clr([parent, child])
	_click(Vector2(8, 8))
	await process_frame
	out.append("s6_ii[%s]%s" % [_fmt(child.log), _fmt(parent.log)])
	parent.mouse_filter = Control.MOUSE_FILTER_STOP
	_clr([parent, child])
	_click(Vector2(24, 24))
	await process_frame
	out.append("s7_inparent[%s]%s" % [_fmt(child.log), _fmt(parent.log)])
	_clr([parent, child])
	_click(Vector2(60, 60))
	await process_frame
	out.append("s8_out[%s]%s" % [_fmt(child.log), _fmt(parent.log)])
	var rb := InputEventMouseButton.new()
	rb.button_index = MOUSE_BUTTON_RIGHT
	rb.pressed = true
	rb.position = Vector2(8, 8)
	rb.global_position = Vector2(8, 8)
	_clr([parent, child])
	root.push_input(rb)
	await process_frame
	out.append("s9_rb[%s]%s" % [_fmt(child.log), _fmt(parent.log)])
	_clr([parent, child])
	root.push_input(_mb(Vector2(8, 8), true))
	await process_frame
	var held_push := int(Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT))
	root.push_input(_mb(Vector2(8, 8), false))
	await process_frame
	out.append("s10_input_state held_push=%d cursor=%s" % [
		held_push, str(root.get_mouse_position())])
	print("PASS r100_gui routing %s" % " ".join(out))


# ---------------------------------------------------------------- hover
func _cell_hover() -> void:
	var a := _mk_sink("A", Vector2.ZERO, Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	var b := _mk_sink("B", Vector2(32, 0), Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	var ign := _mk_sink("I", Vector2.ZERO, Vector2(8, 8), Control.MOUSE_FILTER_IGNORE)
	a.add_child(ign)
	var ev: Array = []
	a.mouse_entered.connect(func() -> void: ev.append("A_in"))
	a.mouse_exited.connect(func() -> void: ev.append("A_out"))
	b.mouse_entered.connect(func() -> void: ev.append("B_in"))
	b.mouse_exited.connect(func() -> void: ev.append("B_out"))
	root.add_child(a)
	root.add_child(b)
	await process_frame
	var out: Array = []
	out.append("h0=%s" % _tag_of(root.gui_get_hovered_control()))
	root.push_input(_mm(Vector2(8, 8), Vector2(8, 8)))
	await process_frame
	out.append("h1=%s ev=%s" % [_tag_of(root.gui_get_hovered_control()), _fmt(ev)])
	root.push_input(_mm(Vector2(4, 4), Vector2(-4, -4)))
	await process_frame
	out.append("h2=%s ev=%s" % [_tag_of(root.gui_get_hovered_control()), _fmt(ev)])
	root.push_input(_mm(Vector2(40, 8), Vector2(36, 4)))
	await process_frame
	out.append("h3=%s ev=%s" % [_tag_of(root.gui_get_hovered_control()), _fmt(ev)])
	root.push_input(_mm(Vector2(60, 60), Vector2(20, 52)))
	await process_frame
	out.append("h4=%s ev=%s" % [_tag_of(root.gui_get_hovered_control()), _fmt(ev)])
	var c := _mk_sink("C", Vector2.ZERO, Vector2(8, 8), Control.MOUSE_FILTER_STOP)
	ign.add_child(c)
	await process_frame
	root.push_input(_mm(Vector2(2, 2), Vector2(-58, -58)))
	await process_frame
	out.append("h5=%s ev=%s" % [_tag_of(root.gui_get_hovered_control()), _fmt(ev)])
	root.push_input(_mm(Vector2(60, 60), Vector2(58, 58)))
	await process_frame
	root.push_input(_mb(Vector2(8, 8), true))
	await process_frame
	out.append("h6_press=%s ev=%s" % [_tag_of(root.gui_get_hovered_control()), _fmt(ev)])
	root.push_input(_mb(Vector2(8, 8), false))
	await process_frame
	out.append("h7_after_release=%s" % _tag_of(root.gui_get_hovered_control()))
	print("PASS r100_gui hover %s" % " ".join(out))


# ---------------------------------------------------------------- motion
func _cell_motion() -> void:
	var s := _mk_sink("S", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	root.add_child(s)
	await process_frame
	var out: Array = []
	_clr([s])
	root.push_input(_mm(Vector2(10, 10), Vector2(5, 7)))
	await process_frame
	out.append("m1[%s]" % _fmt(s.log))
	_clr([s])
	root.push_input(_mm(Vector2(20, 30), Vector2(10, 20)))
	await process_frame
	out.append("m2[%s]" % _fmt(s.log))
	_clr([s])
	root.push_input(_mb(Vector2(10, 10), true, 0, true))
	root.push_input(_mb(Vector2(10, 10), false))
	await process_frame
	out.append("m3_dc[%s]" % _fmt(s.log))
	out.append("m4_push_input_state held=%d cursor=%s vel=%s" % [
		int(Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT)), str(root.get_mouse_position()),
		str(Input.get_last_mouse_velocity())])
	print("PASS r100_gui motion %s" % " ".join(out))


# ---------------------------------------------------------------- localpos
func _cell_localpos() -> void:
	var parent := _mk_sink("P", Vector2(20, 10), Vector2(40, 40), Control.MOUSE_FILTER_STOP)
	var child := _mk_sink("C", Vector2(4, 2), Vector2(10, 10), Control.MOUSE_FILTER_STOP)
	parent.add_child(child)
	root.add_child(parent)
	await process_frame
	var out: Array = []
	root.push_input(_mb(Vector2(30, 14), true))
	await process_frame
	out.append("lp_push_p[%s] c[%s] loc_c=%.1f,%.1f" % [
		_fmt(parent.log), _fmt(child.log),
		child.get_local_mouse_position().x, child.get_local_mouse_position().y])
	parent.log.clear()
	child.log.clear()
	root.push_input(_mb(Vector2(30, 14), true), true)
	await process_frame
	out.append("lp_push_local_p[%s] c[%s]" % [_fmt(parent.log), _fmt(child.log)])
	parent.log.clear()
	child.log.clear()
	Input.parse_input_event(_mb(Vector2(30, 14), true))
	await process_frame
	out.append("lp_parse_p[%s] c[%s] loc_c=%.1f,%.1f gloc_c=%.1f,%.1f" % [
		_fmt(parent.log), _fmt(child.log),
		child.get_local_mouse_position().x, child.get_local_mouse_position().y,
		child.get_global_mouse_position().x, child.get_global_mouse_position().y])
	print("PASS r100_gui localpos %s" % " ".join(out))


# ---------------------------------------------------------------- cursor
func _cell_cursor() -> void:
	var s := _mk_sink("S", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	root.add_child(s)
	await process_frame
	var out: Array = []
	out.append("c0=%s" % str(root.get_mouse_position()))
	root.push_input(_mm(Vector2(20, 20), Vector2(20, 20)))
	await process_frame
	out.append("c1_push_mm=%s" % str(root.get_mouse_position()))
	root.push_input(_mb(Vector2(22, 22), true))
	await process_frame
	out.append("c2_push_mb=%s" % str(root.get_mouse_position()))
	Input.parse_input_event(_mb(Vector2(24, 24), false))
	await process_frame
	out.append("c3_parse_mb=%s" % str(root.get_mouse_position()))
	Input.parse_input_event(_mm(Vector2(30, 30), Vector2(6, 6)))
	await process_frame
	out.append("c4_parse_mm=%s" % str(root.get_mouse_position()))
	var mm2 := _mm(Vector2(70, 70), Vector2(10, 10))
	mm2.global_position = Vector2(60, 60)
	Input.parse_input_event(mm2)
	await process_frame
	out.append("c5_gpos_drives=%s" % str(root.get_mouse_position()))
	var st := InputEventScreenTouch.new()
	st.index = 0
	st.pressed = true
	st.position = Vector2(44, 44)
	Input.parse_input_event(st)
	await process_frame
	out.append("c6_parse_st=%s" % str(root.get_mouse_position()))
	root.push_input(_mm(Vector2(50, 50), Vector2(50, 50)))
	await process_frame
	out.append("c7_push_mm2=%s" % str(root.get_mouse_position()))
	out.append("c8 ds=%s" % str(DisplayServer.mouse_get_position()))
	print("PASS r100_gui cursor %s" % " ".join(out))


# ---------------------------------------------------------------- clip (motion picking vs button picking)
func _cell_clip() -> void:
	var inb := _mk_sink("IN", Vector2.ZERO, Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	var ed := _mk_sink("ED", Vector2(60, 0), Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	var fa := _mk_sink("FA", Vector2(80, 0), Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	root.add_child(inb)
	root.add_child(ed)
	root.add_child(fa)
	await process_frame
	var out: Array = []
	out.append("cp0_vis=%s" % str(root.get_visible_rect()))
	for p in [Vector2(62, 4), Vector2(63.9, 4), Vector2(64, 4), Vector2(64.1, 4), Vector2(70, 4), Vector2(90, 4)]:
		root.push_input(_mm(p, p))
		await process_frame
		out.append("cp_hover%s=%s" % [str(p), _tag_of(root.gui_get_hovered_control())])
		_clr([inb, ed, fa])
		root.push_input(_mb(p, true))
		await process_frame
		out.append("cp_press%s in=%s ed=%s fa=%s" % [
			str(p), _fmt(inb.log), _fmt(ed.log), _fmt(fa.log)])
		root.push_input(_mb(p, false))
		await process_frame
	root.push_input(_mm(Vector2(200, 200), Vector2(200, 200)))
	await process_frame
	out.append("cp_hover200=%s" % _tag_of(root.gui_get_hovered_control()))
	print("PASS r100_gui clip %s" % " ".join(out))


# ---------------------------------------------------------------- drag
func _cell_drag() -> void:
	var LM := MOUSE_BUTTON_MASK_LEFT
	var a := _mk_sink("A", Vector2.ZERO, Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	a.drag_data = {"tag": "fromA"}
	var b := _mk_sink("B", Vector2(32, 0), Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	b.drag_data = {"tag": "fromB"}
	root.add_child(a)
	root.add_child(b)
	await process_frame
	var out: Array = []
	# d1: motion relative length exactly 10 -> below threshold
	root.push_input(_mb(Vector2(8, 8), true, LM))
	root.push_input(_mm(Vector2(18, 8), Vector2(10, 0), LM))
	await process_frame
	out.append("d1_at_threshold drag=%d calls=%d" % [int(root.gui_is_dragging()), a.drag_calls])
	root.push_input(_mb(Vector2(18, 8), false))
	await process_frame
	# d2: 10.5 -> drag starts; source = press-focus A, at_position = press-local
	root.push_input(_mb(Vector2(8, 8), true, LM))
	root.push_input(_mm(Vector2(18.5, 8), Vector2(10.5, 0), LM))
	await process_frame
	out.append("d2_over_threshold drag=%d calls=%d data=%s at=%s" % [
		int(root.gui_is_dragging()), a.drag_calls, _dtag(root.gui_get_drag_data()), _fmt(a.drag_at)])
	# d3: motion over B (in-viewport) -> can_drop on B
	root.push_input(_mm(Vector2(40, 8), Vector2(21.5, 0), LM))
	await process_frame
	out.append("d3_over_b drag=%d a_drop=%s b_drop=%s b_get=%d" % [
		int(root.gui_is_dragging()), _fmt(a.drop_log), _fmt(b.drop_log), b.drag_calls])
	# d4: second motion over B -> can_drop again
	root.push_input(_mm(Vector2(44, 4), Vector2(4, -4), LM))
	await process_frame
	out.append("d4_over_b2 b_drop=%s" % _fmt(b.drop_log))
	# d5: release over B -> drop
	root.push_input(_mb(Vector2(44, 4), false))
	await process_frame
	out.append("d5_release drag=%d b_drop=%s" % [int(root.gui_is_dragging()), _fmt(b.drop_log)])
	# d6: masked press + unmasked motion (rel 30) -> no drag
	root.push_input(_mb(Vector2(8, 8), true, LM))
	root.push_input(_mm(Vector2(38, 8), Vector2(30, 0), 0))
	await process_frame
	out.append("d6_unmasked_motion drag=%d calls=%d" % [int(root.gui_is_dragging()), a.drag_calls])
	root.push_input(_mb(Vector2(38, 8), false))
	await process_frame
	# d7: accumulation 3 x (4,4): 5.66 / 11.31 / 16.97
	root.push_input(_mb(Vector2(4, 4), true, LM))
	var acc := ""
	for i in range(3):
		root.push_input(_mm(Vector2(8 + i * 4, 8 + i * 4), Vector2(4, 4), LM))
		await process_frame
		acc += "%d:%d " % [i + 1, int(root.gui_is_dragging())]
	out.append("d7_accum[%s] calls=%d" % [acc, a.drag_calls])
	root.push_input(_mb(Vector2(16, 16), false))
	await process_frame
	# d8: release over the source with no valid target -> cancel, no drop
	root.push_input(_mb(Vector2(8, 8), true, LM))
	root.push_input(_mm(Vector2(8, 28), Vector2(0, 20), LM))
	await process_frame
	root.push_input(_mb(Vector2(8, 28), false))
	await process_frame
	out.append("d8_no_target drag=%d a_drop=%s b_drop=%s" % [
		int(root.gui_is_dragging()), _fmt(a.drop_log), _fmt(b.drop_log)])
	# d9: force_drag (no threshold, no mask needed)
	var c := _mk_sink("C", Vector2.ZERO, Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	var d := _mk_sink("D", Vector2(32, 0), Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	root.add_child(c)
	root.add_child(d)
	await process_frame
	c.force_drag({"tag": "forced"}, null)
	await process_frame
	out.append("d9_force drag=%d data=%s calls=%d" % [
		int(root.gui_is_dragging()), _dtag(root.gui_get_drag_data()), c.drag_calls])
	root.push_input(_mm(Vector2(40, 8), Vector2(40, 8)))
	await process_frame
	out.append("d10_force_over_d d_drop=%s" % _fmt(d.drop_log))
	root.push_input(_mb(Vector2(40, 8), false))
	await process_frame
	out.append("d11_force_drop drag=%d d_drop=%s" % [int(root.gui_is_dragging()), _fmt(d.drop_log)])
	# d12: can_drop=false -> can called, drop not
	d.can_drop = false
	c.force_drag({"tag": "no"}, null)
	root.push_input(_mm(Vector2(41, 9), Vector2(1, 1)))
	await process_frame
	root.push_input(_mb(Vector2(41, 9), false))
	await process_frame
	out.append("d12_nodrop drag=%d d_drop=%s" % [int(root.gui_is_dragging()), _fmt(d.drop_log)])
	print("PASS r100_gui drag %s" % " ".join(out))


func _dtag(data: Variant) -> String:
	if data is Dictionary and data.has("tag"):
		return str(data["tag"])
	return "null" if data == null else "<data>"


# ---------------------------------------------------------------- touch
func _cell_touch() -> void:
	var a := _mk_sink("A", Vector2.ZERO, Vector2(16, 16), Control.MOUSE_FILTER_STOP)
	var b := _mk_sink("B", Vector2(16, 0), Vector2(16, 16), Control.MOUSE_FILTER_STOP)
	root.add_child(a)
	root.add_child(b)
	await process_frame
	var out: Array = []
	var st := InputEventScreenTouch.new()
	st.index = 0
	st.pressed = true
	st.double_tap = true
	st.position = Vector2(20, 4)
	root.push_input(st)
	await process_frame
	out.append("t1_push_a=%s b=%s" % [_fmt(a.log), _fmt(b.log)])
	a.log.clear()
	b.log.clear()
	var sd := InputEventScreenDrag.new()
	sd.index = 0
	sd.position = Vector2(4, 4)
	sd.relative = Vector2(-16, 0)
	root.push_input(sd)
	await process_frame
	out.append("t2_pushdrag_a=%s b=%s" % [_fmt(a.log), _fmt(b.log)])
	var up := InputEventScreenTouch.new()
	up.index = 0
	up.pressed = false
	up.position = Vector2(4, 4)
	root.push_input(up)
	await process_frame
	# emulation: touch -> mouse (Input.parse_input_event)
	a.log.clear()
	b.log.clear()
	var st2 := InputEventScreenTouch.new()
	st2.index = 0
	st2.pressed = true
	st2.position = Vector2(8, 8)
	Input.parse_input_event(st2)
	await process_frame
	out.append("t3_emul_touch held=%d a=%s b=%s emul=%d" % [
		int(Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT)), _fmt(a.log), _fmt(b.log),
		int(Input.is_emulating_mouse_from_touch())])
	var up2 := InputEventScreenTouch.new()
	up2.index = 0
	up2.pressed = false
	up2.position = Vector2(8, 8)
	Input.parse_input_event(up2)
	await process_frame
	# emulation: mouse -> touch
	Input.set_emulate_touch_from_mouse(true)
	a.log.clear()
	b.log.clear()
	a.in_log.clear()
	Input.parse_input_event(_mb(Vector2(20, 4), true))
	await process_frame
	out.append("t4_emul_mouse a_gui=%s a_in=%s emul_t=%d" % [
		_fmt(a.log), _fmt(a.in_log), int(Input.is_emulating_touch_from_mouse())])
	Input.parse_input_event(_mb(Vector2(20, 4), false))
	await process_frame
	Input.set_emulate_touch_from_mouse(false)
	print("PASS r100_gui touch %s" % " ".join(out))


# ---------------------------------------------------------------- subvp
func _cell_subvp() -> void:
	var rnode := _mk_sink("R", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	root.add_child(rnode)
	var sv := SubViewport.new()
	_nodes.append(sv)
	sv.size = Vector2i(64, 64)
	var snode := _mk_sink("S", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	sv.add_child(snode)
	root.add_child(sv)
	await process_frame
	var out: Array = []
	out.append("v0_local=%d size=%s cursor=%s" % [
		int(sv.handle_input_locally), str(sv.size), str(sv.get_mouse_position())])
	sv.push_input(_mb(Vector2(8, 8), true))
	await process_frame
	out.append("v1_sub[%s] root=%s" % [_fmt(snode.log), _fmt(rnode.log)])
	out.append("v2_hovered=%s cursor_sub=%s cursor_root=%s" % [
		_tag_of(sv.gui_get_hovered_control()), str(sv.get_mouse_position()),
		str(root.get_mouse_position())])
	_clr([rnode, snode])
	root.push_input(_mb(Vector2(8, 8), true))
	await process_frame
	out.append("v3_root_push_sub[%s] root=%s" % [_fmt(snode.log), _fmt(rnode.log)])
	out.append("v4_cursors sub=%s root=%s" % [
		str(sv.get_mouse_position()), str(root.get_mouse_position())])
	var sv2 := SubViewport.new()
	_nodes.append(sv2)
	sv2.size = Vector2i(64, 64)
	sv2.handle_input_locally = false
	var s2 := _mk_sink("S2", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	sv2.add_child(s2)
	root.add_child(sv2)
	await process_frame
	sv2.push_input(_mb(Vector2(12, 12), true))
	await process_frame
	out.append("v5_local_false local=%d s2=[%s] cursor=%s" % [
		int(sv2.handle_input_locally), _fmt(s2.log), str(sv2.get_mouse_position())])
	print("PASS r100_gui subvp %s" % " ".join(out))


# ---------------------------------------------------------------- warp
func _cell_warp() -> void:
	var out: Array = []
	out.append("w0 dv=%s cursor=%s ds_mouse=%s" % [
		DisplayServer.get_name(), str(root.get_mouse_position()),
		str(DisplayServer.mouse_get_position())])
	root.push_input(_mm(Vector2(20, 20), Vector2(20, 20)))
	await process_frame
	out.append("w1 after_push cursor=%s ds_mouse=%s" % [
		str(root.get_mouse_position()), str(DisplayServer.mouse_get_position())])
	Input.warp_mouse(Vector2(30, 30))
	await process_frame
	out.append("w2 after_input_warp cursor=%s ds_mouse=%s" % [
		str(root.get_mouse_position()), str(DisplayServer.mouse_get_position())])
	root.warp_mouse(Vector2(40, 40))
	await process_frame
	out.append("w3 after_vp_warp cursor=%s ds_mouse=%s" % [
		str(root.get_mouse_position()), str(DisplayServer.mouse_get_position())])
	out.append("w4 mode=%d" % Input.get_mouse_mode())
	print("PASS r100_gui warp %s" % " ".join(out))


# ---------------------------------------------------------------- focus
func _cell_focus() -> void:
	var f := _mk_sink("F", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	f.focus_mode = Control.FOCUS_ALL
	var g := _mk_sink("G", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	g.focus_mode = Control.FOCUS_ALL
	root.add_child(f)
	root.add_child(g)
	await process_frame
	var out: Array = []
	f.grab_focus()
	await process_frame
	out.append("f0 owner=%s f_focus=%d g_focus=%d" % [
		_tag_of(root.gui_get_focus_owner()), int(f.has_focus()), int(g.has_focus())])
	var k := InputEventKey.new()
	k.keycode = KEY_A
	k.pressed = true
	_clr([f, g])
	root.push_input(k)
	await process_frame
	out.append("f1_key gui_f=%s gui_g=%s in_f=%s" % [_fmt(f.log), _fmt(g.log), _fmt(f.in_log)])
	f.handled = true
	_clr([f, g])
	root.push_input(k)
	await process_frame
	out.append("f2_handled gui_f=%s gui_g=%s" % [_fmt(f.log), _fmt(g.log)])
	f.handled = false
	g.grab_focus()
	await process_frame
	_clr([f, g])
	root.push_input(k)
	await process_frame
	out.append("f3_regrab gui_f=%s gui_g=%s owner=%s" % [
		_fmt(f.log), _fmt(g.log), _tag_of(root.gui_get_focus_owner())])
	root.gui_release_focus()
	await process_frame
	_clr([f, g])
	root.push_input(k)
	await process_frame
	out.append("f4_released gui_f=%s gui_g=%s owner=%s" % [
		_fmt(f.log), _fmt(g.log), _tag_of(root.gui_get_focus_owner())])
	print("PASS r100_gui focus %s" % " ".join(out))


# ---------------------------------------------------------------- render residue (vacuous-surface evidence)
func _cell_render() -> void:
	var out: Array = []
	var tex := root.get_texture()
	out.append("r0 tex_cls=%s size=%s" % [
		"-" if tex == null else tex.get_class(),
		"-" if tex == null else str(tex.get_size())])
	var img: Image = null
	if tex != null:
		img = tex.get_image()
	out.append("r1 img_null=%d" % int(img == null))
	out.append("r2 adapter=%s rd_null=%d" % [
		RenderingServer.get_video_adapter_name(), int(RenderingServer.get_rendering_device() == null)])
	out.append("r3 method=%s screens=%d ssize=%s win_size=%s" % [
		ProjectSettings.get_setting("rendering/renderer/rendering_method"),
		DisplayServer.get_screen_count(), str(DisplayServer.screen_get_size()), str(root.size)])
	var pl := PointLight2D.new()
	_nodes.append(pl)
	out.append("r4 light sh=%d filt=%d smooth=%.1f blend=%d" % [
		int(pl.shadow_enabled), pl.shadow_filter, pl.shadow_filter_smooth, pl.blend_mode])
	var gp := GPUParticles2D.new()
	_nodes.append(gp)
	out.append("r5 gpu_capture=%s" % str(gp.capture_rect()))
	print("PASS r100_gui render %s" % " ".join(out))


# ---------------------------------------------------------------- os/threading meta (deterministic subset)
func _cell_osmeta() -> void:
	var out: Array = []
	for cls in ["Thread", "Mutex", "Semaphore", "WorkerThreadPool", "Time"]:
		var exists := int(ClassDB.class_exists(cls))
		var nm := -1
		if exists == 1:
			nm = ClassDB.class_get_method_list(cls, true).size()
		out.append("%s[e=%d,m=%d]" % [cls, exists, nm])
	out.append("os=%s procs_gt0=%d" % [OS.get_name(), int(OS.get_processor_count() > 0)])
	out.append("wtp_has_thread_count=%d" % int(ClassDB.class_has_method("WorkerThreadPool", "get_thread_count")))
	print("PASS r100_gui osmeta %s" % " ".join(out))
