extends SceneTree
# r100-scout discovery probe 3 — drag-start with explicit button_mask.
#   godot --headless --path proj --script res://discover3.gd -- --arm=<name>

var arm := ""
var _nodes: Array = []

class Sink extends Control:
	var tag := ""
	var log: Array = []
	var drag_data: Variant = null
	var drag_calls := 0
	var drop_log: Array = []

	func _gui_input(event: InputEvent) -> void:
		log.append("%s:%s" % [tag, _ev(event)])

	func _ev(event: InputEvent) -> String:
		if event is InputEventMouseButton:
			var e := event as InputEventMouseButton
			return "mb(b=%d,p=%d,bm=%d,pos=%.1f,%.1f)" % [
				e.button_index, int(e.pressed), e.button_mask, e.position.x, e.position.y]
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
		return true

	func _drop_data(_at_position: Vector2, _data: Variant) -> void:
		drop_log.append("drop")


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")


func _run() -> void:
	await _arm_dragmask()
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


func _arm_dragmask() -> void:
	var a := _mk_sink("A", Vector2.ZERO, Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	a.drag_data = {"tag": "pay"}
	var b := _mk_sink("B", Vector2(32, 0), Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	root.add_child(a)
	root.add_child(b)
	await process_frame
	var out: Array = []
	var LM := MOUSE_BUTTON_MASK_LEFT
	# v1: push press with mask, then push motion with mask
	root.push_input(_mb(Vector2(8, 8), true, LM))
	root.push_input(_mm(Vector2(12, 12), Vector2(4, 4), LM))
	await process_frame
	out.append("v1_masked push_push drag=%d calls=%d alog=%s" % [
		int(root.gui_is_dragging()), a.drag_calls, _f(a.log)])
	root.push_input(_mb(Vector2(12, 12), false, 0))
	await process_frame
	# v2: parse press, push motion masked
	Input.parse_input_event(_mb(Vector2(8, 8), true, LM))
	root.push_input(_mm(Vector2(12, 12), Vector2(4, 4), LM))
	await process_frame
	out.append("v2_parse_push drag=%d calls=%d" % [int(root.gui_is_dragging()), a.drag_calls])
	root.push_input(_mb(Vector2(12, 12), false, 0))
	await process_frame
	# v3: parse press, parse motion masked
	Input.parse_input_event(_mb(Vector2(8, 8), true, LM))
	await process_frame
	Input.parse_input_event(_mm(Vector2(12, 12), Vector2(4, 4), LM))
	await process_frame
	out.append("v3_parse_parse drag=%d calls=%d" % [int(root.gui_is_dragging()), a.drag_calls])
	# v4: continue to B and release -> drop?
	Input.parse_input_event(_mm(Vector2(40, 8), Vector2(28, -4), LM))
	await process_frame
	out.append("v4_over_b drag=%d bdrop=%s" % [int(root.gui_is_dragging()), _f(b.drop_log)])
	Input.parse_input_event(_mb(Vector2(40, 8), false, 0))
	await process_frame
	out.append("v5_release drag=%d bdrop=%s" % [int(root.gui_is_dragging()), _f(b.drop_log)])
	# v6: push-only full sequence with masks + frames
	a.drag_calls = 0
	b.drop_log.clear()
	root.push_input(_mb(Vector2(8, 8), true, LM))
	await process_frame
	root.push_input(_mm(Vector2(12, 12), Vector2(4, 4), LM))
	await process_frame
	out.append("v6_push_move drag=%d calls=%d" % [int(root.gui_is_dragging()), a.drag_calls])
	root.push_input(_mm(Vector2(40, 8), Vector2(28, -4), LM))
	await process_frame
	out.append("v7_push_over_b drag=%d bdrop=%s" % [int(root.gui_is_dragging()), _f(b.drop_log)])
	root.push_input(_mb(Vector2(40, 8), false, 0))
	await process_frame
	out.append("v8_push_release drag=%d bdrop=%s" % [int(root.gui_is_dragging()), _f(b.drop_log)])
	print("PASS r100_disc3 dragmask %s" % " ".join(out))


func _f(arr: Array) -> String:
	return "-" if arr.is_empty() else "[%s]" % "|".join(arr)
