extends SceneTree
# r100-scout discovery probe 2 — cursor laws, event.position semantics, drag-start variants.
#   godot --headless --path proj --script res://discover2.gd -- --arm=<name>

var arm := ""
var _nodes: Array = []

class Sink extends Control:
	var tag := ""
	var log: Array = []
	var in_log: Array = []
	var drag_data: Variant = null
	var drag_calls := 0
	var drop_log: Array = []

	func _gui_input(event: InputEvent) -> void:
		log.append("%s:%s" % [tag, _ev(event)])

	func _input(event: InputEvent) -> void:
		if in_log.size() < 24:
			in_log.append("%s:%s" % [tag, _ev(event)])

	func _ev(event: InputEvent) -> String:
		if event is InputEventMouseButton:
			var e := event as InputEventMouseButton
			return "mb(b=%d,p=%d,pos=%.1f,%.1f,gpos=%.1f,%.1f,loc=%.1f,%.1f,gloc=%.1f,%.1f)" % [
				e.button_index, int(e.pressed), e.position.x, e.position.y,
				e.global_position.x, e.global_position.y,
				get_local_mouse_position().x, get_local_mouse_position().y,
				get_global_mouse_position().x, get_global_mouse_position().y]
		if event is InputEventMouseMotion:
			var e := event as InputEventMouseMotion
			return "mm(pos=%.1f,%.1f,gpos=%.1f,%.1f,rel=%.1f,%.1f,loc=%.1f,%.1f)" % [
				e.position.x, e.position.y, e.global_position.x, e.global_position.y,
				e.relative.x, e.relative.y,
				get_local_mouse_position().x, get_local_mouse_position().y]
		if event is InputEventScreenTouch:
			var e := event as InputEventScreenTouch
			return "st(i=%d,p=%d,pos=%.1f,%.1f)" % [e.index, int(e.pressed), e.position.x, e.position.y]
		if event is InputEventScreenDrag:
			var e := event as InputEventScreenDrag
			return "sd(i=%d,pos=%.1f,%.1f,rel=%.1f,%.1f)" % [
				e.index, e.position.x, e.position.y, e.relative.x, e.relative.y]
		return event.get_class()

	func _get_drag_data(_at_position: Vector2) -> Variant:
		drag_calls += 1
		return drag_data

	func _can_drop_data(_at_position: Vector2, _data: Variant) -> bool:
		drop_log.append("can")
		return true

	func _drop_data(_at_position: Vector2, _data: Variant) -> void:
		drop_log.append("drop")


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")


func _run() -> void:
	match arm:
		"cursor":
			await _arm_cursor()
		"localpos":
			await _arm_localpos()
		"dragstart":
			await _arm_dragstart()
		"hover2":
			await _arm_hover2()
		"velocity":
			await _arm_velocity()
		_:
			await _arm_cursor()
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


func _mb(pos: Vector2, pressed: bool, dc := false) -> InputEventMouseButton:
	var e := InputEventMouseButton.new()
	e.button_index = MOUSE_BUTTON_LEFT
	e.pressed = pressed
	e.double_click = dc
	e.position = pos
	e.global_position = pos
	return e


func _mm(pos: Vector2, rel: Vector2) -> InputEventMouseMotion:
	var e := InputEventMouseMotion.new()
	e.position = pos
	e.global_position = pos
	e.relative = rel
	return e


func _tag_of(c: Control) -> String:
	if c == null:
		return "null"
	if c.name != "":
		return str(c.name)
	return c.get_class()


# ---------------------------------------------------------------- cursor laws
func _arm_cursor() -> void:
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
	Input.parse_input_event(_mm(Vector2(40, 40), Vector2(10, 10)))
	await process_frame
	out.append("c5_parse_mm2=%s" % str(root.get_mouse_position()))
	var st := InputEventScreenTouch.new()
	st.index = 0
	st.pressed = true
	st.position = Vector2(44, 44)
	Input.parse_input_event(st)
	await process_frame
	out.append("c6_parse_st=%s" % str(root.get_mouse_position()))
	var st2 := InputEventScreenTouch.new()
	st2.index = 0
	st2.pressed = false
	st2.position = Vector2(48, 48)
	Input.parse_input_event(st2)
	await process_frame
	out.append("c7_parse_st_up=%s" % str(root.get_mouse_position()))
	root.push_input(_mm(Vector2(50, 50), Vector2(50, 50)))
	await process_frame
	out.append("c8_push_mm2=%s" % str(root.get_mouse_position()))
	out.append("c9 ds=%s input_warp=%s" % [
		str(DisplayServer.mouse_get_position()), str(Input.get_last_mouse_velocity())])
	print("PASS r100_disc2 cursor %s" % " ".join(out))


# ---------------------------------------------------------------- event.position semantics
func _arm_localpos() -> void:
	var parent := _mk_sink("P", Vector2(20, 10), Vector2(40, 40), Control.MOUSE_FILTER_STOP)
	var child := _mk_sink("C", Vector2(4, 2), Vector2(10, 10), Control.MOUSE_FILTER_STOP)
	parent.add_child(child)
	root.add_child(parent)
	await process_frame
	var out: Array = []
	root.push_input(_mb(Vector2(30, 14), true))
	await process_frame
	out.append("lp_push_p[%s] c[%s]" % [_f(parent.log), _f(child.log)])
	parent.log.clear()
	child.log.clear()
	root.push_input(_mb(Vector2(30, 14), true), true)
	await process_frame
	out.append("lp_push_local_p[%s] c[%s]" % [_f(parent.log), _f(child.log)])
	parent.log.clear()
	child.log.clear()
	var mb := _mb(Vector2(30, 14), true)
	Input.parse_input_event(mb)
	await process_frame
	out.append("lp_parse_p[%s] c[%s]" % [_f(parent.log), _f(child.log)])
	print("PASS r100_disc2 localpos %s" % " ".join(out))


func _f(arr: Array) -> String:
	return "-" if arr.is_empty() else "[%s]" % "|".join(arr)


# ---------------------------------------------------------------- drag start variants
func _arm_dragstart() -> void:
	var a := _mk_sink("A", Vector2.ZERO, Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	a.drag_data = {"tag": "pay"}
	root.add_child(a)
	await process_frame
	var out: Array = []
	# v1: push press, then push motion with big relative
	root.push_input(_mb(Vector2(8, 8), true))
	root.push_input(_mm(Vector2(24, 24), Vector2(16, 16)))
	await process_frame
	out.append("v1_push_push drag=%d calls=%d" % [int(root.gui_is_dragging()), a.drag_calls])
	root.push_input(_mb(Vector2(24, 24), false))
	await process_frame
	# v2: parse press, then push motion
	root.push_input(_mb(Vector2(8, 8), true))
	Input.parse_input_event(_mm(Vector2(24, 24), Vector2(16, 16)))
	await process_frame
	out.append("v2_push_parse drag=%d calls=%d" % [int(root.gui_is_dragging()), a.drag_calls])
	root.push_input(_mb(Vector2(24, 24), false))
	await process_frame
	# v3: parse press, then parse motion
	Input.parse_input_event(_mb(Vector2(8, 8), true))
	await process_frame
	Input.parse_input_event(_mm(Vector2(24, 24), Vector2(16, 16)))
	await process_frame
	out.append("v3_parse_parse drag=%d calls=%d" % [int(root.gui_is_dragging()), a.drag_calls])
	Input.parse_input_event(_mb(Vector2(24, 24), false))
	await process_frame
	# v4: push press, many push motions
	root.push_input(_mb(Vector2(8, 8), true))
	for i in range(6):
		root.push_input(_mm(Vector2(10 + i * 4, 10 + i * 4), Vector2(4, 4)))
		await process_frame
	out.append("v4_many drag=%d calls=%d" % [int(root.gui_is_dragging()), a.drag_calls])
	root.push_input(_mb(Vector2(30, 30), false))
	await process_frame
	# v5: parse press, then push motions with frames
	Input.parse_input_event(_mb(Vector2(8, 8), true))
	await process_frame
	for i in range(4):
		root.push_input(_mm(Vector2(12 + i * 4, 12 + i * 4), Vector2(4, 4)))
		await process_frame
	out.append("v5_parsepush drag=%d calls=%d" % [int(root.gui_is_dragging()), a.drag_calls])
	root.push_input(_mb(Vector2(30, 30), false))
	await process_frame
	# v6: push press, motion via parse_input_event, frames
	root.push_input(_mb(Vector2(8, 8), true))
	await process_frame
	Input.parse_input_event(_mm(Vector2(30, 30), Vector2(22, 22)))
	await process_frame
	out.append("v6_pushparse2 drag=%d calls=%d" % [int(root.gui_is_dragging()), a.drag_calls])
	root.push_input(_mb(Vector2(30, 30), false))
	await process_frame
	print("PASS r100_disc2 dragstart %s" % " ".join(out))


# ---------------------------------------------------------------- hover with names
func _arm_hover2() -> void:
	var a := _mk_sink("A", Vector2.ZERO, Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	var b := _mk_sink("B", Vector2(32, 0), Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	root.add_child(a)
	root.add_child(b)
	await process_frame
	var out: Array = []
	out.append("hv0=%s" % _tag_of(root.gui_get_hovered_control()))
	root.push_input(_mm(Vector2(8, 8), Vector2(8, 8)))
	await process_frame
	out.append("hv1=%s" % _tag_of(root.gui_get_hovered_control()))
	root.push_input(_mm(Vector2(40, 8), Vector2(32, 0)))
	await process_frame
	out.append("hv2=%s" % _tag_of(root.gui_get_hovered_control()))
	root.push_input(_mm(Vector2(60, 60), Vector2(20, 52)))
	await process_frame
	out.append("hv3=%s" % _tag_of(root.gui_get_hovered_control()))
	a.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.push_input(_mm(Vector2(8, 8), Vector2(-52, -52)))
	await process_frame
	out.append("hv4_ign=%s" % _tag_of(root.gui_get_hovered_control()))
	print("PASS r100_disc2 hover2 %s" % " ".join(out))


# ---------------------------------------------------------------- velocity
func _arm_velocity() -> void:
	var s := _mk_sink("S", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	root.add_child(s)
	await process_frame
	var out: Array = []
	root.push_input(_mm(Vector2(10, 10), Vector2(10, 10)))
	await process_frame
	out.append("ve1_push last=%s svel=%s ev=%s" % [
		str(Input.get_last_mouse_velocity()), str(Input.get_last_mouse_screen_velocity()),
		_f(s.log)])
	s.log.clear()
	Input.parse_input_event(_mm(Vector2(30, 30), Vector2(20, 20)))
	await process_frame
	out.append("ve2_parse1 last=%s svel=%s ev=%s" % [
		str(Input.get_last_mouse_velocity()), str(Input.get_last_mouse_screen_velocity()),
		_f(s.log)])
	s.log.clear()
	Input.parse_input_event(_mm(Vector2(50, 50), Vector2(20, 20)))
	await process_frame
	out.append("ve3_parse2 last=%s svel=%s ev=%s" % [
		str(Input.get_last_mouse_velocity()), str(Input.get_last_mouse_screen_velocity()),
		_f(s.log)])
	s.log.clear()
	Input.parse_input_event(_mm(Vector2(60, 60), Vector2(10, 10)))
	await process_frame
	out.append("ve4_parse3 last=%s svel=%s ev=%s" % [
		str(Input.get_last_mouse_velocity()), str(Input.get_last_mouse_screen_velocity()),
		_f(s.log)])
	print("PASS r100_disc2 velocity %s" % " ".join(out))
