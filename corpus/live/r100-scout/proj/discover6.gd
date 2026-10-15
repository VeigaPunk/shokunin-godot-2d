extends SceneTree
# r100-scout discovery probe 6 — viewport pick clipping + drag target freeze.
#   godot --headless --path proj --script res://discover6.gd -- --arm=<name>

var arm := ""
var _nodes: Array = []

class Sink extends Control:
	var tag := ""
	var log: Array = []
	var drag_data: Variant = null
	var drag_calls := 0
	var drop_log: Array = []
	var can_drop := true

	func _gui_input(event: InputEvent) -> void:
		log.append("%s:%s" % [tag, _ev(event)])

	func _ev(event: InputEvent) -> String:
		if event is InputEventMouseButton:
			var e := event as InputEventMouseButton
			return "mb(b=%d,p=%d,pos=%.1f,%.1f)" % [e.button_index, int(e.pressed), e.position.x, e.position.y]
		if event is InputEventMouseMotion:
			var e := event as InputEventMouseMotion
			return "mm(bm=%d,pos=%.1f,%.1f,rel=%.1f,%.1f)" % [
				e.button_mask, e.position.x, e.position.y, e.relative.x, e.relative.y]
		return event.get_class()

	func _get_drag_data(_at_position: Vector2) -> Variant:
		drag_calls += 1
		return drag_data

	func _can_drop_data(_at_position: Vector2, _data: Variant) -> bool:
		drop_log.append("can")
		return can_drop

	func _drop_data(_at_position: Vector2, _data: Variant) -> void:
		drop_log.append("drop")


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")


func _run() -> void:
	match arm:
		"clip":
			await _arm_clip()
		"dragtarget":
			await _arm_dragtarget()
		_:
			await _arm_clip()
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


func _f(arr: Array) -> String:
	return "-" if arr.is_empty() else "[%s]" % "|".join(arr)


func _arm_clip() -> void:
	var inside := _mk_sink("IN", Vector2(0, 0), Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	var edge := _mk_sink("ED", Vector2(60, 0), Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	var far := _mk_sink("FA", Vector2(80, 0), Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	root.add_child(inside)
	root.add_child(edge)
	root.add_child(far)
	await process_frame
	var out: Array = []
	out.append("vis=%s" % str(root.get_visible_rect()))
	root.push_input(_mb(Vector2(62, 4), true))
	await process_frame
	out.append("clip_62[%s]" % _f(edge.log))
	edge.log.clear()
	root.push_input(_mb(Vector2(63.9, 4), true))
	await process_frame
	out.append("clip_63_9[%s]" % _f(edge.log))
	edge.log.clear()
	root.push_input(_mb(Vector2(64.1, 4), true))
	await process_frame
	out.append("clip_64_1[%s]" % _f(edge.log))
	edge.log.clear()
	root.push_input(_mb(Vector2(70, 4), true))
	await process_frame
	out.append("clip_70[%s]" % _f(edge.log))
	far.log.clear()
	root.push_input(_mb(Vector2(90, 4), true))
	await process_frame
	out.append("clip_90[%s]" % _f(far.log))
	inside.log.clear()
	root.push_input(_mb(Vector2(31.9, 31.9), true))
	await process_frame
	out.append("clip_in[%s]" % _f(inside.log))
	print("PASS r100_disc6 clip %s" % " ".join(out))


func _arm_dragtarget() -> void:
	var LM := MOUSE_BUTTON_MASK_LEFT
	var a := _mk_sink("A", Vector2(0, 0), Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	a.drag_data = {"tag": "fromA"}
	var b := _mk_sink("B", Vector2(32, 0), Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	root.add_child(a)
	root.add_child(b)
	await process_frame
	var out: Array = []
	# t1: drag starts INSIDE A (threshold crossed), then move over B
	root.push_input(_mb(Vector2(8, 8), true, LM))
	root.push_input(_mm(Vector2(24, 24), Vector2(16, 16), LM))
	await process_frame
	out.append("t1_start drag=%d calls=%d" % [int(root.gui_is_dragging()), a.drag_calls])
	root.push_input(_mm(Vector2(40, 8), Vector2(16, -16), LM))
	await process_frame
	out.append("t2_over_b drag=%d a_drop=%s b_drop=%s" % [
		int(root.gui_is_dragging()), _f(a.drop_log), _f(b.drop_log)])
	root.push_input(_mb(Vector2(40, 8), false))
	await process_frame
	out.append("t3_release a_drop=%s b_drop=%s" % [_f(a.drop_log), _f(b.drop_log)])
	# t4: force_drag from C then over D (both in-viewport)
	var c := _mk_sink("C", Vector2(0, 0), Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	var d := _mk_sink("D", Vector2(32, 0), Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	root.add_child(c)
	root.add_child(d)
	await process_frame
	c.force_drag({"tag": "forced"}, null)
	root.push_input(_mm(Vector2(40, 8), Vector2(40, 8), LM))
	await process_frame
	out.append("t4_force_over_d drag=%d c_drop=%s d_drop=%s" % [
		int(root.gui_is_dragging()), _f(c.drop_log), _f(d.drop_log)])
	root.push_input(_mb(Vector2(40, 8), false))
	await process_frame
	out.append("t5_force_release c_drop=%s d_drop=%s" % [_f(c.drop_log), _f(d.drop_log)])
	# t6: force_drag then NO motion, release in place (over the source)
	c.force_drag({"tag": "stay"}, null)
	root.push_input(_mb(Vector2(40, 8), false))
	await process_frame
	out.append("t6_force_nomotion drag=%d c_drop=%s d_drop=%s" % [
		int(root.gui_is_dragging()), _f(c.drop_log), _f(d.drop_log)])
	print("PASS r100_disc6 dragtarget %s" % " ".join(out))
