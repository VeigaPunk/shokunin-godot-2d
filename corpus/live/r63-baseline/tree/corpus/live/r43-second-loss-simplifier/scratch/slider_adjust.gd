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
    slider.grab_focus()
    await process_frame
    if slider.value != 5.0 or receipts != [] or label.text != "Value 5" or get_root().gui_get_focus_owner() != slider:
        push_error("setup failed")
        quit(2)
        return
    var other := Button.new()
    other.text = "Other"
    other.focus_mode = Control.FOCUS_ALL
    ui.add_child(other)
    var edges := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]
    var owners: Array[Control] = [slider, other, other, slider, slider, other, other]
    var values: Array[float] = [6.0, 6.0, 6.0, 5.0, 5.0, 5.0, 5.0]
    var receipt_history: Array[float] = [6.0, 5.0]
    var receipt_counts: Array[int] = [1, 1, 1, 2, 2, 2, 2]
    for i in range(edges.size()):
        if i == 1 or i == 5:
            other.grab_focus()
            await process_frame
        elif i == 3:
            slider.grab_focus()
            await process_frame
        if get_root().gui_get_focus_owner() != owners[i] or slider.has_focus() != (owners[i] == slider):
            push_error("owner mismatch before edge %d" % i)
            quit(2)
            return
        var event := InputEventAction.new()
        event.action = edges[i][0]
        event.pressed = edges[i][1]
        Input.parse_input_event(event)
        await process_frame
        var expected_receipts := receipt_history.slice(0, receipt_counts[i])
        if slider.value != values[i] or receipts != expected_receipts or label.text != "Value %d" % int(values[i]):
            push_error("state mismatch edge=%d value=%s receipts=%s label=%s" % [i, slider.value, receipts, label.text])
            quit(2)
            return
        print("EDGE %d owner=%s value=%s receipts=%s label=%s" % [i, owners[i].name, slider.value, receipts, label.text])
    print("PASS R43 values=6,6,6,5,5,5,5 receipts=6,5")
    push_error("EXPECTED NEGATIVE R43 terminal after all seven checks")
    quit(2)
func _on_value_changed(value: float) -> void:
    receipts.append(value)
    label.text = "Value %d" % int(value)
func _action(action_name: String, pressed: bool) -> void:
    var event := InputEventAction.new()
    event.action = action_name
    event.pressed = pressed
    Input.parse_input_event(event)
