extends SceneTree
# r100b one-off: emulated mouse-button state machine on the parse path — the
# mechanism behind the same-process contamination chain (cursor cell c6 parses a
# ScreenTouch press and never parses a release).
func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var out: Array = []
	out.append("held0=%d emul_mouse=%d" % [
		int(Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT)),
		int(Input.is_emulating_mouse_from_touch())])
	var st := InputEventScreenTouch.new()
	st.index = 0
	st.pressed = true
	st.position = Vector2(44, 44)
	Input.parse_input_event(st)
	Input.flush_buffered_events()
	out.append("touch_press held=%d cursor=%s" % [
		int(Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT)), str(root.get_mouse_position())])
	var st2 := InputEventScreenTouch.new()
	st2.index = 0
	st2.pressed = false
	st2.position = Vector2(44, 44)
	Input.parse_input_event(st2)
	Input.flush_buffered_events()
	out.append("touch_release held=%d" % int(Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT)))
	var st3 := InputEventScreenTouch.new()
	st3.index = 0
	st3.pressed = true
	st3.position = Vector2(10, 10)
	Input.parse_input_event(st3)
	Input.flush_buffered_events()
	out.append("second_press held=%d cursor=%s" % [
		int(Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT)), str(root.get_mouse_position())])
	print("PASS r100b_emul %s" % " ".join(out))
	quit(0)
