extends SceneTree
# r100-scout discovery probe 8 — motion/hover vs button picking at the viewport edge.
#   godot --headless --path proj --script res://discover8.gd

var _nodes: Array = []

class Sink extends Control:
	var tag := ""
	var log: Array = []

	func _gui_input(event: InputEvent) -> void:
		log.append("%s:%s" % [tag, _ev(event)])

	func _ev(event: InputEvent) -> String:
		if event is InputEventMouseButton:
			var e := event as InputEventMouseButton
			return "mb(p=%d,pos=%.1f,%.1f)" % [int(e.pressed), e.position.x, e.position.y]
		if event is InputEventMouseMotion:
			var e := event as InputEventMouseMotion
			return "mm(pos=%.1f,%.1f)" % [e.position.x, e.position.y]
		return event.get_class()


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var out: Array = []
	var inb := Sink.new()
	_nodes.append(inb)
	inb.tag = "IN"
	inb.name = "IN"
	inb.position = Vector2(0, 0)
	inb.size = Vector2(32, 32)
	inb.mouse_filter = Control.MOUSE_FILTER_STOP
	var ed := Sink.new()
	_nodes.append(ed)
	ed.tag = "ED"
	ed.name = "ED"
	ed.position = Vector2(60, 0)
	ed.size = Vector2(32, 32)
	ed.mouse_filter = Control.MOUSE_FILTER_STOP
	root.add_child(inb)
	root.add_child(ed)
	await process_frame
	out.append("vis=%s" % str(root.get_visible_rect()))
	for p in [Vector2(62, 4), Vector2(63.9, 4), Vector2(64.1, 4), Vector2(70, 4), Vector2(90, 4)]:
		root.push_input(_mm(p, p))
		await process_frame
		var h := root.gui_get_hovered_control()
		out.append("hover%s=%s" % [str(p), "null" if h == null else str(h.name)])
		ed.log.clear()
		inb.log.clear()
		root.push_input(_mb(p, true))
		await process_frame
		out.append("press%s ed=%s in=%s" % [
			str(p), "-" if ed.log.is_empty() else "hit", "-" if inb.log.is_empty() else "hit"])
		ed.log.clear()
		inb.log.clear()
	# motion far outside any control
	root.push_input(_mm(Vector2(200, 200), Vector2(200, 200)))
	await process_frame
	var h2 := root.gui_get_hovered_control()
	out.append("hover200=%s" % ("null" if h2 == null else str(h2.name)))
	# a control fully outside the viewport
	var fa := Sink.new()
	_nodes.append(fa)
	fa.tag = "FA"
	fa.name = "FA"
	fa.position = Vector2(80, 0)
	fa.size = Vector2(32, 32)
	fa.mouse_filter = Control.MOUSE_FILTER_STOP
	root.add_child(fa)
	await process_frame
	root.push_input(_mm(Vector2(90, 4), Vector2(-110, -196)))
	await process_frame
	var h3 := root.gui_get_hovered_control()
	out.append("hover90=%s fa_log=%s" % [
		"null" if h3 == null else str(h3.name), "-" if fa.log.is_empty() else "hit"])
	root.push_input(_mb(Vector2(90, 4), true))
	await process_frame
	out.append("press90_fa=%s" % ("-" if fa.log.is_empty() else "hit"))
	await _cleanup()
	print("PASS r100_disc8 edge %s" % " ".join(out))
	quit(0)


func _cleanup() -> void:
	for c in root.get_children():
		c.free()
	for n in _nodes:
		if is_instance_valid(n):
			n.free()
	_nodes.clear()
	await process_frame


func _mb(pos: Vector2, pressed: bool) -> InputEventMouseButton:
	var e := InputEventMouseButton.new()
	e.button_index = MOUSE_BUTTON_LEFT
	e.pressed = pressed
	e.position = pos
	e.global_position = pos
	return e


func _mm(pos: Vector2, rel: Vector2) -> InputEventMouseMotion:
	var e := InputEventMouseMotion.new()
	e.position = pos
	e.global_position = pos
	e.relative = rel
	return e
