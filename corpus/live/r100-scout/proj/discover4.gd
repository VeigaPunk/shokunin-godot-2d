extends SceneTree
# r100-scout discovery probe 4 — drag threshold bisection + drag-data source.
#   godot --headless --path proj --script res://discover4.gd -- --arm=<name>

var arm := ""
var _nodes: Array = []
var _order: Array = []

class Sink extends Control:
	var tag := ""
	var log: Array = []
	var drag_data: Variant = null
	var drag_calls := 0
	var drop_log: Array = []
	var order: Array = []

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
		order.append("%s:get" % tag)
		return drag_data

	func _can_drop_data(_at_position: Vector2, data: Variant) -> bool:
		order.append("%s:can(%s)" % [tag, _dtag(data)])
		return true

	func _drop_data(_at_position: Vector2, data: Variant) -> void:
		order.append("%s:drop(%s)" % [tag, _dtag(data)])

	func _dtag(data: Variant) -> String:
		if data is Dictionary and data.has("tag"):
			return str(data["tag"])
		return str(data)


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")


func _run() -> void:
	match arm:
		"threshold":
			await _arm_threshold()
		"source":
			await _arm_source()
		_:
			await _arm_threshold()
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


func _arm_threshold() -> void:
	var LM := MOUSE_BUTTON_MASK_LEFT
	var out: Array = []
	# single-motion bisection: rel lengths 5.66 / 8 / 10 / 10.5 / 11 / 12 / 16
	var cases := [
		["r5_66", Vector2(4, 4)], ["r8", Vector2(8, 0)], ["r10", Vector2(10, 0)],
		["r10_5", Vector2(10.5, 0)], ["r11", Vector2(11, 0)], ["r12", Vector2(12, 0)],
		["r16", Vector2(16, 0)],
	]
	for c in cases:
		var a := _mk_sink("A", Vector2.ZERO, Vector2(32, 32), Control.MOUSE_FILTER_STOP)
		a.drag_data = {"tag": "pay"}
		root.add_child(a)
		await process_frame
		root.push_input(_mb(Vector2(8, 8), true, LM))
		root.push_input(_mm(Vector2(8, 8) + (c[1] as Vector2), c[1], LM))
		await process_frame
		out.append("%s=%d/%d" % [c[0], int(root.gui_is_dragging()), a.drag_calls])
		root.push_input(_mb(Vector2(8, 8), false, 0))
		await process_frame
		a.free()
	# accumulation: 3 x (4,4) = 16.97
	var b := _mk_sink("B", Vector2.ZERO, Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	b.drag_data = {"tag": "pay"}
	root.add_child(b)
	await process_frame
	root.push_input(_mb(Vector2(8, 8), true, LM))
	var acc := ""
	for i in range(4):
		root.push_input(_mm(Vector2(10 + i * 4, 10 + i * 4), Vector2(4, 4), LM))
		await process_frame
		acc += "%d:%d/%d " % [i + 1, int(root.gui_is_dragging()), b.drag_calls]
	out.append("acc[%s]" % acc)
	root.push_input(_mb(Vector2(24, 24), false, 0))
	await process_frame
	print("PASS r100_disc4 threshold %s" % " ".join(out))


func _arm_source() -> void:
	var LM := MOUSE_BUTTON_MASK_LEFT
	var a := _mk_sink("A", Vector2.ZERO, Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	a.drag_data = {"tag": "fromA"}
	var b := _mk_sink("B", Vector2(32, 0), Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	b.drag_data = {"tag": "fromB"}
	root.add_child(a)
	root.add_child(b)
	await process_frame
	var out: Array = []
	root.push_input(_mb(Vector2(8, 8), true, LM))
	await process_frame
	root.push_input(_mm(Vector2(40, 8), Vector2(32, 0), LM))
	await process_frame
	out.append("s1 drag=%d data=%s A=%d B=%d" % [
		int(root.gui_is_dragging()), _dtag(root.gui_get_drag_data()), a.drag_calls, b.drag_calls])
	root.push_input(_mm(Vector2(50, 8), Vector2(10, 0), LM))
	await process_frame
	out.append("s2 b.order=%s" % _f(b.order))
	root.push_input(_mb(Vector2(50, 8), false, 0))
	await process_frame
	out.append("s3 b.order=%s drag=%d" % [_f(b.order), int(root.gui_is_dragging())])
	# does mouse_focus (press target) own the drag? press on A, move over A itself far
	a.drag_calls = 0
	b.drag_calls = 0
	root.push_input(_mb(Vector2(8, 8), true, LM))
	await process_frame
	root.push_input(_mm(Vector2(28, 28), Vector2(20, 20), LM))
	await process_frame
	out.append("s4_same drag=%d data=%s A=%d B=%d" % [
		int(root.gui_is_dragging()), _dtag(root.gui_get_drag_data()), a.drag_calls, b.drag_calls])
	root.push_input(_mb(Vector2(28, 28), false, 0))
	await process_frame
	print("PASS r100_disc4 source %s" % " ".join(out))


func _dtag(data: Variant) -> String:
	if data is Dictionary and data.has("tag"):
		return str(data["tag"])
	return str(data)


func _f(arr: Array) -> String:
	return "-" if arr.is_empty() else "[%s]" % "|".join(arr)
