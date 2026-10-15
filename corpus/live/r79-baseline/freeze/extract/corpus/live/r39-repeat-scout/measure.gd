extends SceneTree
var slider: HSlider
var label: Label
var receipts: Array[float] = []
var disconnected := OS.get_cmdline_user_args().has("--disconnect-signal")
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
    if not disconnected: slider.value_changed.connect(_on_value_changed)
    await process_frame
    slider.grab_focus()
    await process_frame
    print("START focus=%s owner=%s value=%s receipts=%s label=%s" % [slider.has_focus(), get_root().gui_get_focus_owner(), slider.value, receipts, label.text])
    for pair in [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]:
        var event := InputEventAction.new()
        event.action = pair[0]
        event.pressed = pair[1]
        Input.parse_input_event(event)
        await process_frame
        print("EDGE %s %s focus=%s owner=%s value=%s receipts=%s label=%s" % [pair[0], "press" if pair[1] else "release", slider.has_focus(), get_root().gui_get_focus_owner(), slider.value, receipts, label.text])
    quit(0)
func _on_value_changed(value: float) -> void:
    receipts.append(value)
    label.text = "Value %d" % int(value)
