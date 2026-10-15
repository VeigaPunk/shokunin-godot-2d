extends SceneTree
# r100-scout discovery probe 7 — drag drop-target geometry grid.
#   godot --headless --path proj --script res://discover7.gd

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
		return true

	func _drop_data(_at_position: Vector2, _data: Variant) -> void:
		drop_log.append("drop")


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var out: Array = []
	# G1: discover6 t2 geometry (works)
	out.append(await _case("G1", Vector2(0, 0), Vector2(32, 0), Vector2(8, 8),
		[Vector2(24, 24), Vector2(40, 8)]))
	# G2: drag-cell geometry (failed)
	out.append(await _case("G2", Vector2(20, 10), Vector2(60, 10), Vector2(30, 14),
		[Vector2(40.5, 14), Vector2(70, 14)]))
	# G3: G1 geometry, second motion outside the 64x64 viewport
	out.append(await _case("G3", Vector2(0, 0), Vector2(32, 0), Vector2(8, 8),
		[Vector2(24, 24), Vector2(70, 14)]))
	# G4: G2 geometry, second motion still inside A
	out.append(await _case("G4", Vector2(20, 10), Vector2(60, 10), Vector2(30, 14),
		[Vector2(40.5, 14), Vector2(44, 14)]))
	# G5: G2 geometry, single threshold-crossing motion straight over B
	out.append(await _case("G5", Vector2(20, 10), Vector2(60, 10), Vector2(30, 14),
		[Vector2(70, 14)]))
	# G6: G1 geometry, third motion after entering B
	out.append(await _case("G6", Vector2(0, 0), Vector2(32, 0), Vector2(8, 8),
		[Vector2(24, 24), Vector2(40, 8), Vector2(44, 4)]))
	await _cleanup()
	print("PASS r100_disc7 grid %s" % " ".join(out))
	quit(0)


func _cleanup() -> void:
	for c in root.get_children():
		c.free()
	for n in _nodes:
		if is_instance_valid(n):
			n.free()
	_nodes.clear()
	await process_frame


func _case(tag: String, apos: Vector2, bpos: Vector2, press: Vector2, motions: Array) -> String:
	var LM := MOUSE_BUTTON_MASK_LEFT
	var a := Sink.new()
	_nodes.append(a)
	a.tag = "A"
	a.name = "A"
	a.position = apos
	a.size = Vector2(32, 32) if tag == "G1" or tag == "G3" or tag == "G6" else Vector2(40, 40)
	a.mouse_filter = Control.MOUSE_FILTER_STOP
	a.drag_data = {"tag": "fromA"}
	var b := Sink.new()
	_nodes.append(b)
	b.tag = "B"
	b.name = "B"
	b.position = bpos
	b.size = a.size
	b.mouse_filter = Control.MOUSE_FILTER_STOP
	root.add_child(a)
	root.add_child(b)
	await process_frame
	var prev := press
	root.push_input(_mb(press, true, LM))
	for m in motions:
		var rel: Vector2 = (m as Vector2) - prev
		root.push_input(_mm(m, rel, LM))
		prev = m
		await process_frame
	var res := "%s drag=%d a=%s b=%s" % [
		tag, int(root.gui_is_dragging()), _f(a.drop_log), _f(b.drop_log)]
	root.push_input(_mb(prev, false))
	await process_frame
	res += " rel=%s/%s" % [_f(a.drop_log), _f(b.drop_log)]
	a.free()
	b.free()
	await process_frame
	return res


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
