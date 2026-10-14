extends SceneTree
var slider: HSlider
var label: Label
var receipts: Array[float] = []
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
    slider.value_changed.connect(_on_value_changed)
    await process_frame
    var mode := OS.get_cmdline_user_args().has("--focused")
    if mode:
        slider.grab_focus()
    await process_frame
    print("BEFORE mode=%s owner=%s has_focus=%s value=%s receipts=%s label=%s" % [mode, str(get_root().gui_get_focus_owner()), slider.has_focus(), slider.value, receipts, label.text])
    _action("ui_right", true)
    await process_frame
    _action("ui_right", false)
    await process_frame
    var rv := slider.value
    var rr := receipts.duplicate()
    var rl := label.text
    print("AFTER_RIGHT mode=%s owner=%s value=%s receipts=%s label=%s" % [mode, str(get_root().gui_get_focus_owner()), rv, rr, rl])
    print("BEFORE_LEFT mode=%s owner=%s has_focus=%s value=%s receipts=%s label=%s" % [mode, str(get_root().gui_get_focus_owner()), slider.has_focus(), slider.value, receipts, label.text])
    _action("ui_left", true)
    await process_frame
    _action("ui_left", false)
    await process_frame
    print("AFTER_LEFT mode=%s owner=%s value=%s receipts=%s label=%s" % [mode, str(get_root().gui_get_focus_owner()), slider.value, receipts, label.text])
    quit(0)
func _action(action: String, pressed: bool) -> void:
    var event := InputEventAction.new()
    event.action = action
    event.pressed = pressed
    Input.parse_input_event(event)
func _on_value_changed(value: float) -> void:
    receipts.append(value)
    label.text = "Value %d" % int(value)
