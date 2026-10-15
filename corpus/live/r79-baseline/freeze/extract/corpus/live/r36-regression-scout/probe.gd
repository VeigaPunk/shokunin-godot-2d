extends SceneTree
var slider: HSlider
var receipts: Array[float] = []
func _initialize() -> void:
    var root_control := Control.new()
    slider = HSlider.new()
    slider.min_value = 0.0
    slider.max_value = 10.0
    slider.step = 1.0
    slider.value = 5.0
    slider.focus_mode = Control.FOCUS_ALL
    root_control.add_child(slider)
    root.add_child(root_control)
    slider.value_changed.connect(_on_changed)
    await process_frame
    slider.grab_focus()
    await process_frame
    print("SETUP focus=%s value=%s" % [slider.has_focus(), slider.value])
    var er := InputEventAction.new()
    er.action = "ui_right"
    er.pressed = true
    Input.parse_input_event(er)
    await process_frame
    print("RIGHT pressed value=%s receipts=%s" % [slider.value, receipts])
    er.pressed = false
    Input.parse_input_event(er)
    await process_frame
    print("RIGHT released value=%s receipts=%s" % [slider.value, receipts])
    var el := InputEventAction.new()
    el.action = "ui_left"
    el.pressed = true
    Input.parse_input_event(el)
    await process_frame
    print("LEFT pressed value=%s receipts=%s" % [slider.value, receipts])
    el.pressed = false
    Input.parse_input_event(el)
    await process_frame
    print("LEFT released value=%s receipts=%s" % [slider.value, receipts])
    quit(0)
func _on_changed(v: float) -> void:
    receipts.append(v)
