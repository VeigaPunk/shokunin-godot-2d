extends SceneTree

var signal_count := 0

func _initialize() -> void:
	var button := Button.new()
	button.name = "Activate"
	button.text = "Activate"
	var label := Label.new()
	label.name = "Status"
	label.text = "Waiting"
	root.add_child(button)
	root.add_child(label)
	await process_frame
	if not button.is_inside_tree() or not label.is_inside_tree() or label.text != "Waiting":
		_fail("button/label setup is not in tree with initial text")
		return
	button.pressed.connect(_on_button_pressed)
	if OS.get_cmdline_user_args().has("--disconnect"):
		button.pressed.disconnect(_on_button_pressed)
	button._pressed()
	if OS.get_cmdline_user_args().has("--disconnect"):
		if signal_count != 0 or label.text != "Waiting":
			_fail("disconnected pressed signal unexpectedly updated label")
			return
		_fail("expected in-tree Button pressed connection to update Label text=Activated")
		return
	if signal_count != 1 or label.text != "Activated":
		_fail("Button activation did not update in-tree Label exactly once")
		return
	print("PASS button_in_tree=true label_in_tree=true initial=Waiting activation=BaseButton._pressed signal_count=1 label_text=Activated")
	quit(0)

func _on_button_pressed() -> void:
	signal_count += 1
	var label := root.get_node("Status") as Label
	label.text = "Activated"

func _fail(message: String) -> void:
	push_error("button activation assertion failed: " + message)
	quit(2)
