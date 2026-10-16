extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	await process_frame
	for ei in [-2, -1, 0, 1, 31, 32, 33, 42, 100]:
		var a := StringName("e%d" % (ei + 100))
		InputMap.add_action(a)
		var e := InputEventAction.new()
		e.action = a; e.pressed = true; e.event_index = ei
		Input.parse_input_event(e)
		await process_frame
		print("ei=%d -> pressed=%d" % [ei, int(Input.is_action_pressed(a))])
	quit(0)
