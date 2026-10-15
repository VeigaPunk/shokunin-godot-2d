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
	# Deliberately omit SceneTree dispatch: this is the negative control.
	await process_frame
	if signal_count != 0:
		push_error("negative control failed: expected absent signal, got one")
		quit(1)
		return
	push_error("negative control: expected collected signal was absent (dispatch deliberately disabled)")
	quit(1)

func _on_collected() -> void:
	signal_count += 1

func _fail(message: String) -> void:
	push_error("negative scene signal test: " + message)
	quit(1)
