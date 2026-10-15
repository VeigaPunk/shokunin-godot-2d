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
    var other := Button.new()
    other.text = "Other"
    other.focus_mode = Control.FOCUS_ALL
    ui.add_child(slider)
    ui.add_child(label)
    ui.add_child(other)
    root.add_child(ui)
    slider.value_changed.connect(_on_value_changed)
    await process_frame
    slider.grab_focus()
    await process_frame
    assert(slider.is_inside_tree() and slider.value == 5.0 and receipts.is_empty() and label.text == "Value 5")
    assert(slider.value_changed.is_connected(_on_value_changed))
    var edges := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]
    var values: Array[float] = [6,6,6,5,5,5,5,4,4]
    var owners: Array[Control] = [slider,other,other,slider,slider,other,other,slider,slider]
    var connected_states := [true,false,false,false,false,false,false,true,true]
    for i in range(edges.size()):
        if i == 1 or i == 5:
            other.grab_focus()
            await process_frame
        elif i == 3 or i == 7:
            slider.grab_focus()
            await process_frame
        assert(get_root().gui_get_focus_owner() == owners[i] and slider.has_focus() == (owners[i] == slider), "owner before edge %d" % i)
        assert(slider.value_changed.is_connected(_on_value_changed) == connected_states[i], "connection before edge %d" % i)
        var event := InputEventAction.new()
        event.action = edges[i][0]
        event.pressed = edges[i][1]
        Input.parse_input_event(event)
        await process_frame
        assert(slider.value == values[i], "numeric after edge %d: %s" % [i, slider.value])
        assert(receipts == [6.0], "receipts after edge %d: %s" % [i, receipts])
        assert(label.text == "Value 6", "label after edge %d: %s" % [i, label.text])
        if i == 0:
            assert(slider.value_changed.is_connected(_on_value_changed))
            slider.value_changed.disconnect(_on_value_changed)
            assert(not slider.value_changed.is_connected(_on_value_changed))
        elif i == 7:
            assert(not slider.value_changed.is_connected(_on_value_changed))
            slider.value_changed.connect(_on_value_changed)
            assert(slider.value_changed.is_connected(_on_value_changed))
        assert(slider.value_changed.is_connected(_on_value_changed) == connected_states[i+1] if i < 8 else slider.value_changed.is_connected(_on_value_changed), "transition after edge %d" % i)
    print("R48_LATE_RECONNECT_EXPECTED_NEGATIVE values=6,6,6,5,5,5,5,4,4 receipts=[6] Label=Value 6; callback reconnected after edge7; edge8 release unchanged")
    push_error("R48 LATE RECONNECT ASSERTION FAILED: expected terminal negative after nine checks")
    quit(2)
func _on_value_changed(value: float) -> void:
    receipts.append(value)
    label.text = "Value %d" % int(value)
