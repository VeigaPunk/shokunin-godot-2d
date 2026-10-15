extends SceneTree
# r100-scout discovery probe 5 — drag mask dependency, at_position, touch picking, hover-on-press, subvp local flag.
#   godot --headless --path proj --script res://discover5.gd -- --arm=<name>

var arm := ""
var _nodes: Array = []

class Sink extends Control:
	var tag := ""
	var log: Array = []
	var in_log: Array = []
	var drag_data: Variant = null
	var drag_calls := 0
	var drag_at: Array = []

	func _gui_input(event: InputEvent) -> void:
		log.append("%s:%s" % [tag, _ev(event)])

	func _input(event: InputEvent) -> void:
		if in_log.size() < 12:
			in_log.append("%s:%s" % [tag, _ev(event)])

	func _ev(event: InputEvent) -> String:
		if event is InputEventMouseButton:
			var e := event as InputEventMouseButton
			return "mb(b=%d,p=%d,bm=%d,pos=%.1f,%.1f)" % [
				e.button_index, int(e.pressed), e.button_mask, e.position.x, e.position.y]
		if event is InputEventMouseMotion:
			var e := event as InputEventMouseMotion
			return "mm(bm=%d,pos=%.1f,%.1f,rel=%.1f,%.1f)" % [
				e.button_mask, e.position.x, e.position.y, e.relative.x, e.relative.y]
		if event is InputEventScreenTouch:
			var e := event as InputEventScreenTouch
			return "st(i=%d,p=%d,dt=%d,pos=%.1f,%.1f)" % [
				e.index, int(e.pressed), int(e.double_tap), e.position.x, e.position.y]
		if event is InputEventScreenDrag:
			var e := event as InputEventScreenDrag
			return "sd(i=%d,pos=%.1f,%.1f,rel=%.1f,%.1f)" % [
				e.index, e.position.x, e.position.y, e.relative.x, e.relative.y]
		if event is InputEventKey:
			var e := event as InputEventKey
			return "key(k=%d,p=%d)" % [e.keycode, int(e.pressed)]
		return event.get_class()

	func _get_drag_data(at_position: Vector2) -> Variant:
		drag_calls += 1
		drag_at.append("(%.1f,%.1f)" % [at_position.x, at_position.y])
		return drag_data


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	call_deferred("_run")


func _run() -> void:
	match arm:
		"maskdep":
			await _arm_maskdep()
		"dragat":
			await _arm_dragat()
		"touchpick":
			await _arm_touchpick()
		"hoverpress":
			await _arm_hoverpress()
		"subflag":
			await _arm_subflag()
		"keydual":
			await _arm_keydual()
		_:
			await _arm_maskdep()
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


func _arm_maskdep() -> void:
	var LM := MOUSE_BUTTON_MASK_LEFT
	var out: Array = []
	# m1: press masked, motion unmasked, rel 20
	var a := _mk_sink("A", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	a.drag_data = {"tag": "pay"}
	root.add_child(a)
	await process_frame
	root.push_input(_mb(Vector2(8, 8), true, LM))
	root.push_input(_mm(Vector2(28, 28), Vector2(20, 20), 0))
	await process_frame
	out.append("m1_pressmask_motion0=%d/%d" % [int(root.gui_is_dragging()), a.drag_calls])
	root.push_input(_mb(Vector2(28, 28), false, 0))
	await process_frame
	# m2: press unmasked, motion masked, rel 20
	root.push_input(_mb(Vector2(8, 8), true, 0))
	root.push_input(_mm(Vector2(28, 28), Vector2(20, 20), LM))
	await process_frame
	out.append("m2_press0_motionmask=%d/%d" % [int(root.gui_is_dragging()), a.drag_calls])
	root.push_input(_mb(Vector2(28, 28), false, 0))
	await process_frame
	# m3: both unmasked, rel 20
	root.push_input(_mb(Vector2(8, 8), true, 0))
	root.push_input(_mm(Vector2(28, 28), Vector2(20, 20), 0))
	await process_frame
	out.append("m3_both0=%d/%d" % [int(root.gui_is_dragging()), a.drag_calls])
	root.push_input(_mb(Vector2(28, 28), false, 0))
	await process_frame
	print("PASS r100_disc5 maskdep %s" % " ".join(out))


func _arm_dragat() -> void:
	var LM := MOUSE_BUTTON_MASK_LEFT
	var a := _mk_sink("A", Vector2(20, 10), Vector2(40, 40), Control.MOUSE_FILTER_STOP)
	a.drag_data = {"tag": "pay"}
	root.add_child(a)
	await process_frame
	root.push_input(_mb(Vector2(30, 14), true, LM))
	root.push_input(_mm(Vector2(50, 34), Vector2(20, 20), LM))
	await process_frame
	var out: Array = []
	out.append("da drag=%d calls=%d at=%s" % [
		int(root.gui_is_dragging()), a.drag_calls, _f(a.drag_at)])
	root.push_input(_mb(Vector2(50, 34), false, 0))
	await process_frame
	print("PASS r100_disc5 dragat %s" % " ".join(out))


func _arm_touchpick() -> void:
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
	out.append("tp1_a=%s b=%s" % [_f(a.log), _f(b.log)])
	a.log.clear()
	b.log.clear()
	var sd := InputEventScreenDrag.new()
	sd.index = 0
	sd.position = Vector2(4, 4)
	sd.relative = Vector2(-16, 0)
	root.push_input(sd)
	await process_frame
	out.append("tp2_a=%s b=%s" % [_f(a.log), _f(b.log)])
	out.append("tp3 hovered=%s" % ("null" if root.gui_get_hovered_control() == null else str(root.gui_get_hovered_control().name)))
	print("PASS r100_disc5 touchpick %s" % " ".join(out))


func _arm_hoverpress() -> void:
	var a := _mk_sink("A", Vector2.ZERO, Vector2(32, 32), Control.MOUSE_FILTER_STOP)
	root.add_child(a)
	await process_frame
	var out: Array = []
	out.append("hp0=%s" % ("null" if root.gui_get_hovered_control() == null else str(root.gui_get_hovered_control().name)))
	root.push_input(_mb(Vector2(8, 8), true))
	await process_frame
	out.append("hp1=%s" % ("null" if root.gui_get_hovered_control() == null else str(root.gui_get_hovered_control().name)))
	root.push_input(_mm(Vector2(9, 9), Vector2(1, 1)))
	await process_frame
	out.append("hp2=%s" % ("null" if root.gui_get_hovered_control() == null else str(root.gui_get_hovered_control().name)))
	root.push_input(_mm(Vector2(60, 60), Vector2(51, 51)))
	await process_frame
	out.append("hp3=%s" % ("null" if root.gui_get_hovered_control() == null else str(root.gui_get_hovered_control().name)))
	print("PASS r100_disc5 hoverpress %s" % " ".join(out))


func _arm_subflag() -> void:
	var sv := SubViewport.new()
	_nodes.append(sv)
	sv.size = Vector2i(64, 64)
	sv.handle_input_locally = false
	var s := _mk_sink("S", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	sv.add_child(s)
	root.add_child(sv)
	await process_frame
	var out: Array = []
	out.append("sf local=%d" % int(sv.handle_input_locally))
	sv.push_input(_mb(Vector2(8, 8), true))
	await process_frame
	out.append("sf_push=[%s] cursor=%s" % [_f(s.log), str(sv.get_mouse_position())])
	print("PASS r100_disc5 subflag %s" % " ".join(out))


func _arm_keydual() -> void:
	var f := _mk_sink("F", Vector2.ZERO, Vector2(64, 64), Control.MOUSE_FILTER_STOP)
	f.focus_mode = Control.FOCUS_ALL
	root.add_child(f)
	await process_frame
	var out: Array = []
	f.grab_focus()
	await process_frame
	var k := InputEventKey.new()
	k.keycode = KEY_A
	k.pressed = true
	root.push_input(k)
	await process_frame
	out.append("kd gui=%s in=%s" % [_f(f.log), _f(f.in_log)])
	print("PASS r100_disc5 keydual %s" % " ".join(out))
