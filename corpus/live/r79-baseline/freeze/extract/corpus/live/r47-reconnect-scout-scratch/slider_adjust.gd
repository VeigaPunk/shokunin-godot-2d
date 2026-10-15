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
    var other := Button.new()
    other.text = "Other"
    other.focus_mode = Control.FOCUS_ALL
    ui.add_child(other)
    var actions := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]
    var values: Array[float] = [6,6,6,5,5,5,5,4,4]
    var receipt_history: Array = [[6.0],[6.0],[6.0],[6.0],[6.0],[6.0],[6.0],[6.0,4.0],[6.0,4.0]]
    for i in range(actions.size()):
        if i == 1 or i == 5:
            other.grab_focus()
            await process_frame
        elif i == 3 or i == 7:
            slider.grab_focus()
            await process_frame
        var owner: Control = other if i in [1,2,5,6] else slider
        if get_root().gui_get_focus_owner() != owner or slider.has_focus() != (owner == slider):
            push_error("OWNER ASSERT before edge %d" % i); quit(2); return
        _action(actions[i][0], actions[i][1])
        await process_frame
        if i == 0:
            if slider.value != 6 or receipts != [6.0] or label.text != "Value 6" or not slider.value_changed.is_connected(_on_value_changed):
                push_error("EDGE0 or connected-state assertion failed"); quit(2); return
            slider.value_changed.disconnect(_on_value_changed)
            if slider.value_changed.is_connected(_on_value_changed):
                push_error("disconnect transition assertion failed"); quit(2); return
        elif i == 3:
            if slider.value != 5 or receipts != [6.0] or label.text != "Value 6" or slider.value_changed.is_connected(_on_value_changed):
                push_error("EDGE3 or disconnected-state assertion failed"); quit(2); return
            slider.value_changed.connect(_on_value_changed)
            if not slider.value_changed.is_connected(_on_value_changed):
                push_error("reconnect transition assertion failed"); quit(2); return
        elif slider.value != values[i] or receipts != receipt_history[i] or label.text != ("Value 6" if i < 7 else "Value 4"):
            push_error("edge assertion failed: %d value=%s receipts=%s label=%s" % [i, slider.value, receipts, label.text]); quit(2); return
    print("PASS R47_RECONNECT values=6,6,6,5,5,5,5,4,4 receipts=[6] edges0-6,[6,4] edges7-8 Label=Value 4")
    quit(0)
func _action(action: String, pressed: bool) -> void:
    var event := InputEventAction.new()
    event.action = action
    event.pressed = pressed
    Input.parse_input_event(event)
func _on_value_changed(value: float) -> void:
    receipts.append(value)
    label.text = "Value %d" % int(value)
