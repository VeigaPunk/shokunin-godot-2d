extends SceneTree

var signal_count := 0

func _initialize() -> void:
	var packed := load("res://pickup.tscn") as PackedScene
	if packed == null:
		_fail("scene did not load")
		return
	var pickup := packed.instantiate()
	root.add_child(pickup)
	pickup.collected.connect(_on_collected)
	var event := InputEventKey.new()
	event.keycode = KEY_E
	event.pressed = true
	Input.parse_input_event(event)
	await process_frame
	if not pickup.consumed or signal_count != 1:
		_fail("SceneTree dispatch of E did not consume and emit once")
		return
	var repeat_event := event.duplicate() as InputEventKey
	Input.parse_input_event(repeat_event)
	await process_frame
	if signal_count != 1:
		_fail("repeat event emitted collected twice")
		return
	print("PASS scene_loaded=true SceneTree_dispatched_event=E consumed=true signal_count=1 repeat_suppressed=true")
	quit(0)

func _on_collected() -> void:
	signal_count += 1

func _fail(message: String) -> void:
	push_error("scene signal test: " + message)
	quit(1)
