extends SceneTree
var slider: HSlider
var other: Button
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
    other = Button.new()
    other.text = "other"
    other.focus_mode = Control.FOCUS_ALL
    label = Label.new()
    label.text = "Value 5"
    ui.add_child(slider)
    ui.add_child(other)
    ui.add_child(label)
    root.add_child(ui)
    slider.value_changed.connect(_on_value_changed)
    await process_frame
    slider.grab_focus()
    await process_frame
    print("SETUP slider_in_tree=%s focus_owner_slider=%s focus_owner=%s value=%s receipts=%s label=%s" % [slider.is_inside_tree(), get_root().gui_get_focus_owner() == slider, get_root().gui_get_focus_owner(), slider.value, receipts, label.text])
    await edge("ui_right", true)
    other.grab_focus()
    await process_frame
    print("HANDOFF owner_other=%s slider_has_focus=%s owner=%s" % [get_root().gui_get_focus_owner() == other, slider.has_focus(), get_root().gui_get_focus_owner()])
    for event in [["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]:
        await edge(event[0], event[1])
    quit(0)
func edge(action: String, pressed: bool) -> void:
    var event := InputEventAction.new()
    event.action = action
    event.pressed = pressed
    Input.parse_input_event(event)
    await process_frame
    print("EDGE %s %s value=%s receipts=%s label=%s owner_other=%s slider_focus=%s" % [action, "press" if pressed else "release", slider.value, receipts, label.text, get_root().gui_get_focus_owner() == other, slider.has_focus()])
func _on_value_changed(value: float) -> void:
    receipts.append(value)
    label.text = "Value %d" % int(value)
