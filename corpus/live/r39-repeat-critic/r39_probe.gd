extends SceneTree
var slider: HSlider
var label: Label
var receipts: Array[float] = []
var disconnected := OS.get_cmdline_user_args().has("--disconnect-signal")

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
    slider.grab_focus()
    await process_frame
    print("SETUP focus=%s value=%s receipts=%s label=%s" % [get_root().gui_get_focus_owner() == slider, slider.value, receipts, label.text])
    await edge("ui_right", true, "right1_press")
    await edge("ui_right", true, "right2_press")
    await edge("ui_right", false, "right_release")
    await edge("ui_left", true, "left1_press")
    await edge("ui_left", false, "left1_release")
    await edge("ui_left", true, "left2_press")
    await edge("ui_left", false, "left2_release")
    print("FINAL disconnected=%s value=%s receipts=%s label=%s" % [disconnected, slider.value, receipts, label.text])
    quit(0)

func edge(action: String, pressed: bool, name: String) -> void:
    var event := InputEventAction.new()
    event.action = action
    event.pressed = pressed
    print("SYNC %s event_id=%s action=%s pressed=%s value=%s receipts=%s label=%s" % [name, event.get_instance_id(), action, pressed, slider.value, receipts, label.text])
    Input.parse_input_event(event)
    print("POST_PARSE %s value=%s receipts=%s label=%s" % [name, slider.value, receipts, label.text])
    await process_frame
    print("FRAME %s value=%s receipts=%s label=%s" % [name, slider.value, receipts, label.text])

func _on_value_changed(value: float) -> void:
    receipts.append(value)
    label.text = "Value %d" % int(value)
    print("SIGNAL value_changed=%s receipts=%s label=%s" % [value, receipts, label.text])
