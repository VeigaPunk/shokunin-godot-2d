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
    var edges := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]
    var owners: Array[Control] = [slider, other, other, slider, slider, other, other, slider, slider, slider, slider]
    var vals: Array[float] = [6.0,6.0,6.0,5.0,5.0,5.0,5.0,4.0,4.0,3.0,3.0]
    var rs: Array = [[6.0],[6.0],[6.0],[6.0],[6.0],[6.0],[6.0],[6.0],[6.0],[6.0,3.0],[6.0,3.0]]
    for i in range(edges.size()):
        if i == 1 or i == 5:
            other.grab_focus()
            await process_frame
        elif i == 3 or i == 7:
            slider.grab_focus()
            await process_frame
        if get_root().gui_get_focus_owner() != owners[i] or slider.has_focus() != (owners[i] == slider):
            push_error("SCRIBE owner mismatch edge %d" % i); quit(2); return
        if i in [0,8,9,10] and not slider.value_changed.is_connected(_on_value_changed):
            push_error("SCRIBE expected connected before edge %d" % i); quit(2); return
        if i in [1,2,3,4,5,6,7] and slider.value_changed.is_connected(_on_value_changed):
            push_error("SCRIBE expected disconnected before edge %d" % i); quit(2); return
        _action(edges[i][0], edges[i][1])
        await process_frame
        if i == 0:
            if slider.value != 6.0 or receipts != [6.0] or label.text != "Value 6":
                push_error("SCRIBE edge0 state mismatch"); quit(2); return
            slider.value_changed.disconnect(_on_value_changed)
            if slider.value_changed.is_connected(_on_value_changed):
                push_error("SCRIBE disconnect failed"); quit(2); return
        elif i == 7:
            if slider.value != 4.0 or receipts != [6.0] or label.text != "Value 6" or slider.value_changed.is_connected(_on_value_changed):
                push_error("SCRIBE edge7 pre-reconnect mismatch"); quit(2); return
            slider.value_changed.connect(_on_value_changed)
            if not slider.value_changed.is_connected(_on_value_changed):
                push_error("SCRIBE reconnect failed"); quit(2); return
        elif i in [9,10]:
            if slider.value != 3.0 or receipts != [6.0, 3.0] or label.text != "Value 3":
                push_error("SCRIBE edge%d mismatch: val=%s receipts=%s label=%s" % [i, slider.value, receipts, label.text]); quit(2); return
        else:
            if slider.value != vals[i] or receipts != rs[i] or label.text != "Value 6":
                push_error("SCRIBE edge %d mismatch: val=%s receipts=%s label=%s" % [i, slider.value, receipts, label.text]); quit(2); return
        if i in [8,9,10] and not slider.value_changed.is_connected(_on_value_changed):
            push_error("SCRIBE connection lost after edge %d" % i); quit(2); return
        print("EDGE %d value=%s receipts=%s label=%s connected=%s owner=%s" % [i, slider.value, receipts, label.text, slider.value_changed.is_connected(_on_value_changed), get_root().gui_get_focus_owner().name])
    if slider.value != 3.0 or receipts != [6.0,3.0] or label.text != "Value 3":
        push_error("SCRIBE fresh edge10 mismatch"); quit(2); return
    print("R50_SYNTHETIC_RELEASE_AFTER_FRESH_RECONNECT PASS")
    quit(0)
func _action(action: String, pressed: bool) -> void:
    var event := InputEventAction.new()
    event.action = action
    event.pressed = pressed
    Input.parse_input_event(event)
func _on_value_changed(value: float) -> void:
    receipts.append(value)
    label.text = "Value %d" % int(value)
