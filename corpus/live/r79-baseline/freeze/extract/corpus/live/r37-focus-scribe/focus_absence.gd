extends SceneTree
var slider: HSlider
var label: Label
var receipts: Array[float] = []
func action(name: String, down: bool) -> void:
    var event := InputEventAction.new()
    event.action = name
    event.pressed = down
    Input.parse_input_event(event)
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
    var owner0 = get_root().gui_get_focus_owner()
    print("SETUP focus_owner=%s slider_has_focus=%s value=%s receipts=%s label=%s" % [str(owner0), slider.has_focus(), slider.value, receipts, label.text])
    for name in ["ui_right", "ui_left"]:
        var owner_before = get_root().gui_get_focus_owner()
        print("BEFORE action=%s focus_owner=%s slider_has_focus=%s value=%s receipts=%s label=%s" % [name, str(owner_before), slider.has_focus(), slider.value, receipts, label.text])
        action(name, true)
        await process_frame
        action(name, false)
        await process_frame
        print("AFTER action=%s focus_owner=%s slider_has_focus=%s value=%s receipts=%s label=%s" % [name, str(get_root().gui_get_focus_owner()), slider.has_focus(), slider.value, receipts, label.text])
    print("FINAL no_grab_focus=true value=%s receipts=%s label=%s" % [slider.value, receipts, label.text])
    if slider.value != 5.0 or not receipts.is_empty() or label.text != "Value 5":
        push_error("focus absence did not preserve value/signals/label")
        quit(3)
        return
    push_error("INTENDED NEGATIVE: unfocused slider did not adjust after ui_right then ui_left")
    quit(2)
func _on_value_changed(value: float) -> void:
    receipts.append(value)
    label.text = "Value %d" % int(value)
