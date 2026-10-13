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
    await process_frame
    print("BEFORE focus_owner=%s has_focus=%s value=%s receipts=%s label=%s" % [get_root().gui_get_focus_owner(), slider.has_focus(), slider.value, receipts, label.text])
    if get_root().gui_get_focus_owner() == slider:
        push_error("SETUP INVALID: no grab_focus but slider acquired focus")
        quit(3)
        return
    _action("ui_right", true)
    await process_frame
    _action("ui_right", false)
    await process_frame
    print("AFTER ui_right focus_owner=%s has_focus=%s value=%s receipts=%s label=%s" % [get_root().gui_get_focus_owner(), slider.has_focus(), slider.value, receipts, label.text])
    _action("ui_left", true)
    await process_frame
    _action("ui_left", false)
    await process_frame
    print("AFTER ui_left focus_owner=%s has_focus=%s value=%s receipts=%s label=%s" % [get_root().gui_get_focus_owner(), slider.has_focus(), slider.value, receipts, label.text])
    print("OBS no_focus values_after_both=%s receipts=%s label=%s" % [slider.value, receipts, label.text])
    if slider.value != 5.0 or receipts != [] or label.text != "Value 5":
        push_error("COUNTERFACTUAL CONTRARY: expected no-focus to preserve value 5 and consumer unchanged")
        quit(4)
        return
    push_error("EXPECTED NEGATIVE: no-focus preserved value=5 after both actions; missing numeric adjustment")
    quit(2)
func _action(action: String, pressed: bool) -> void:
    var event := InputEventAction.new()
    event.action = action
    event.pressed = pressed
    Input.parse_input_event(event)
func _on_value_changed(value: float) -> void:
    receipts.append(value)
    label.text = "Value %d" % int(value)
