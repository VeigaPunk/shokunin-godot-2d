extends SceneTree
var slider: HSlider
var label: Label
var value_receipts: Array[float] = []
var disconnected := OS.get_cmdline_user_args().has("--disconnect-signal")
var no_focus := OS.get_cmdline_user_args().has("--no-focus")

func _initialize() -> void:
    var ui := CanvasLayer.new()
    slider = HSlider.new()
    slider.min_value = 0.0
    slider.max_value = 10.0
    slider.step = 1.0
    slider.value = 5.0
    slider.focus_mode = Control.FOCUS_ALL
    label = Label.new()
    label.text = "Value 5"
    ui.add_child(slider)
    ui.add_child(label)
    root.add_child(ui)
    if not disconnected:
        slider.value_changed.connect(_on_value_changed)
    await process_frame
    if not no_focus:
        slider.grab_focus()
    await process_frame
    if not slider.is_inside_tree() or slider.value != 5.0 or value_receipts != [] or label.text != "Value 5":
        push_error("SLIDER setup assertion failed: expected in-tree value=5 Label=Value 5")
        quit(2)
        return
    if no_focus:
        if slider.has_focus() or get_root().gui_get_focus_owner() == slider:
            push_error("SLIDER no-focus setup assertion failed: slider owns GUI focus")
            quit(2)
            return
    elif not slider.has_focus() or get_root().gui_get_focus_owner() != slider:
        push_error("SLIDER focus assertion failed before ui_right")
        quit(2)
        return
    _edge("ui_right", true)
    await process_frame
    _check_edge("right_press", 6.0, [6.0], "Value 6", not disconnected and not no_focus)
    _edge("ui_right", false)
    await process_frame
    _check_edge("right_release", 6.0, [6.0], "Value 6", not disconnected and not no_focus)
    _edge("ui_left", true)
    await process_frame
    _check_edge("left_press", 5.0, [6.0, 5.0], "Value 5", not disconnected and not no_focus)
    _edge("ui_left", false)
    await process_frame
    _check_edge("left_release", 5.0, [6.0, 5.0], "Value 5", not disconnected and not no_focus)
    if disconnected:
        if slider.value != 5.0 or value_receipts != [] or label.text != "Value 5":
            push_error("DISCONNECTED_FINAL mismatch")
            quit(2)
            return
        push_error("DISCONNECTED expected connected receipts")
        quit(2)
        return
    if no_focus:
        if slider.value != 5.0 or value_receipts != [] or label.text != "Value 5":
            push_error("NO_FOCUS_FINAL mismatch")
            quit(2)
            return
        push_error("NO_FOCUS expected focus adjustment")
        quit(2)
        return
    print("PASS edge four-edge focused connected")
    quit(0)

func _edge(action: String, pressed: bool) -> void:
    var event := InputEventAction.new()
    event.action = action
    event.pressed = pressed
    Input.parse_input_event(event)

func _check_edge(name: String, expected_value: float, expected_receipts: Array, expected_label: String, connected: bool) -> void:
    print("EDGE %s value=%s receipts=%s label=%s focus=%s" % [name, slider.value, value_receipts, label.text, slider.has_focus()])
    if connected:
        if slider.value != expected_value or value_receipts != expected_receipts or label.text != expected_label:
            push_error("EDGE ASSERTION FAILED " + name)
            quit(2)
    elif no_focus:
        if slider.value != 5.0 or value_receipts != [] or label.text != "Value 5":
            push_error("NO_FOCUS EDGE ASSERTION FAILED " + name)
            quit(2)
    else:
        if slider.value != (6.0 if name.begins_with("right") else 5.0) or value_receipts != [] or label.text != "Value 5":
            push_error("DISCONNECTED EDGE ASSERTION FAILED " + name)
            quit(2)

func _action(action: String, pressed: bool) -> void:
    var event := InputEventAction.new()
    event.action = action
    event.pressed = pressed
    Input.parse_input_event(event)

func _on_value_changed(value: float) -> void:
    value_receipts.append(value)
    label.text = "Value %d" % int(value)
