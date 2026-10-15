extends SceneTree
var slider: HSlider
var button: Button
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
    button = Button.new()
    button.text = "Other"
    button.focus_mode = Control.FOCUS_ALL
    label = Label.new()
    label.text = "Value 5"
    ui.add_child(slider)
    ui.add_child(button)
    ui.add_child(label)
    root.add_child(ui)
    slider.value_changed.connect(_on_value_changed)
    await process_frame
    slider.grab_focus()
    await process_frame
    var edges := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]
    var values: Array[float] = [6,6,6,5,5,5,5,4,4]
    var receipts_by_edge := [[6.0],[6.0],[6.0],[6.0],[6.0],[6.0],[6.0],[6.0,4.0],[6.0,4.0]]
    var labels := ["Value 6","Value 6","Value 6","Value 6","Value 6","Value 6","Value 6","Value 4","Value 4"]
    for i in range(edges.size()):
        if i == 1 or i == 5:
            button.grab_focus()
            await process_frame
        elif i == 3 or i == 7:
            slider.grab_focus()
            await process_frame
        var expected_owner: Control = button if i in [1,2,5,6] else slider
        assert(get_root().gui_get_focus_owner() == expected_owner, "owner before %d" % i)
        assert(slider.has_focus() == (expected_owner == slider), "slider focus before %d" % i)
        _action(edges[i][0], edges[i][1])
        await process_frame
        if i == 0:
            assert(slider.value_changed.is_connected(_on_value_changed))
            assert(slider.value == 6.0 and receipts == [6.0] and label.text == "Value 6")
            slider.value_changed.disconnect(_on_value_changed)
            assert(not slider.value_changed.is_connected(_on_value_changed))
        elif i == 3:
            assert(not slider.value_changed.is_connected(_on_value_changed))
            assert(slider.value == 5.0 and receipts == [6.0] and label.text == "Value 6")
            slider.value_changed.connect(_on_value_changed)
            assert(slider.value_changed.is_connected(_on_value_changed))
        assert(slider.value == values[i] and receipts == receipts_by_edge[i] and label.text == labels[i], "state after %d value=%s receipts=%s label=%s" % [i, slider.value, receipts, label.text])
        print("edge=%d owner=%s value=%s receipts=%s label=%s connected=%s" % [i, expected_owner.name, slider.value, receipts, label.text, slider.value_changed.is_connected(_on_value_changed)])
    print("R47_RECONNECT PASS nine checks")
    quit(0)
func _action(action: String, pressed: bool) -> void:
    var event := InputEventAction.new()
    event.action = action
    event.pressed = pressed
    Input.parse_input_event(event)
func _on_value_changed(value: float) -> void:
    receipts.append(value)
    label.text = "Value %d" % int(value)
