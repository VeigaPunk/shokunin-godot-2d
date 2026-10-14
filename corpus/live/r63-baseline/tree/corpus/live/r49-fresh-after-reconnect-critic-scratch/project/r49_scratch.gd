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
    var edges := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]
    var vals: Array[float] = [6,6,6,5,5,5,5,4,4]
    for i in range(edges.size()):
        if i == 1 or i == 5:
            other.grab_focus()
            await process_frame
        elif i == 3 or i == 7:
            slider.grab_focus()
            await process_frame
        var owner: Control = other if i in [1,2,5,6] else slider
        if get_root().gui_get_focus_owner() != owner:
            push_error("OWNER pre edge %d" % i); quit(2); return
        _action(edges[i][0], edges[i][1]); await process_frame
        if i == 0:
            if slider.value != 6 or receipts != [6.0] or label.text != "Value 6" or not slider.value_changed.is_connected(_on_value_changed):
                push_error("EDGE0 state"); quit(2); return
            slider.value_changed.disconnect(_on_value_changed)
            if slider.value_changed.is_connected(_on_value_changed): push_error("disconnect"); quit(2); return
        elif i == 7:
            if slider.value != 4 or receipts != [6.0] or label.text != "Value 6" or slider.value_changed.is_connected(_on_value_changed):
                push_error("EDGE7 preconnect"); quit(2); return
            slider.value_changed.connect(_on_value_changed)
            if not slider.value_changed.is_connected(_on_value_changed): push_error("reconnect"); quit(2); return
        else:
            if slider.value != vals[i] or receipts != [6.0] or label.text != "Value 6":
                push_error("STATE after edge %d value=%s receipts=%s label=%s" % [i,slider.value,receipts,label.text]); quit(2); return
            if i < 7 and slider.value_changed.is_connected(_on_value_changed): push_error("connected early"); quit(2); return
            if i == 8 and not slider.value_changed.is_connected(_on_value_changed): push_error("not connected edge8"); quit(2); return
    if get_root().gui_get_focus_owner() != slider or slider.value != 4 or receipts != [6.0] or label.text != "Value 6" or not slider.value_changed.is_connected(_on_value_changed):
        push_error("edge8 terminal state"); quit(2); return
    _action("ui_left", true); await process_frame
    if get_root().gui_get_focus_owner() != slider or slider.value != 3 or receipts != [6.0,3.0] or label.text != "Value 3":
        push_error("EDGE9 fresh press expected 3/[6,3]/Value 3 got %s/%s/%s" % [slider.value,receipts,label.text]); quit(2); return
    print("PASS r49 scratch edge9=3 receipts=[6,3] label=Value 3 after ten checks")
    quit(0)
func _action(action: String, pressed: bool) -> void:
    var event := InputEventAction.new(); event.action=action; event.pressed=pressed; Input.parse_input_event(event)
func _on_value_changed(value: float) -> void:
    receipts.append(value); label.text="Value %d" % int(value)
