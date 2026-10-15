extends SceneTree
var slider: HSlider
var other: Button
var label: Label
var receipts: Array[float] = []
var values: Array[float] = []
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
    check_owner(slider, "setup")
    check_state(5.0, [], "setup")
    await edge("ui_right", true, slider, 6.0, [6.0], "Value 6")
    other.grab_focus()
    await process_frame
    check_owner(other, "handoff-1")
    await edge("ui_right", true, other, 6.0, [6.0], "Value 6")
    await edge("ui_right", false, other, 6.0, [6.0], "Value 6")
    slider.grab_focus()
    await process_frame
    check_owner(slider, "restore-1")
    await edge("ui_left", true, slider, 5.0, [6.0, 5.0], "Value 5")
    await edge("ui_left", false, slider, 5.0, [6.0, 5.0], "Value 5")
    other.grab_focus()
    await process_frame
    check_owner(other, "handoff-2")
    await edge("ui_left", true, other, 5.0, [6.0, 5.0], "Value 5")
    await edge("ui_left", false, other, 5.0, [6.0, 5.0], "Value 5")
    slider.grab_focus()
    await process_frame
    check_owner(slider, "restore-2")
    await edge("ui_left", true, slider, 4.0, [6.0, 5.0, 4.0], "Value 4")
    await edge("ui_left", false, slider, 4.0, [6.0, 5.0, 4.0], "Value 4")
    print("R44 PASS values=%s receipts=%s label=%s" % [values, receipts, label.text])
    quit(0)
func edge(action: String, pressed: bool, expected_owner: Control, expected_value: float, expected_receipts: Array, expected_label: String) -> void:
    var name := action + (" press" if pressed else " release")
    check_owner(expected_owner, "before " + name)
    var event := InputEventAction.new()
    event.action = action
    event.pressed = pressed
    Input.parse_input_event(event)
    await process_frame
    values.append(slider.value)
    check_owner(expected_owner, "after " + name)
    check_state(expected_value, expected_receipts, "after " + name)
    assert(label.text == expected_label, "label mismatch " + name)
    print("EDGE %s owner=%s value=%s receipts=%s label=%s" % [name, expected_owner.name, slider.value, receipts, label.text])
func check_owner(expected: Control, where: String) -> void:
    var owner := get_root().gui_get_focus_owner()
    assert(owner == expected, "focus owner mismatch at " + where + ": " + str(owner))
    assert(slider.has_focus() == (expected == slider), "slider focus mismatch at " + where)
func check_state(expected_value: float, expected_receipts: Array, where: String) -> void:
    assert(is_equal_approx(slider.value, expected_value), "value mismatch at " + where + ": " + str(slider.value))
    assert(receipts == expected_receipts, "receipt mismatch at " + where + ": " + str(receipts))
    assert(label.text == "Value %d" % int(expected_value), "label mismatch at " + where + ": " + label.text)
func _on_value_changed(value: float) -> void:
    receipts.append(value)
    label.text = "Value %d" % int(value)
