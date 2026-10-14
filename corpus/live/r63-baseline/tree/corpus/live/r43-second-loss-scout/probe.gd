extends SceneTree
var slider: HSlider
var label: Label
var button: Button
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
    button = Button.new()
    button.text = "Other"
    ui.add_child(slider)
    ui.add_child(label)
    ui.add_child(button)
    root.add_child(ui)
    slider.value_changed.connect(_receipt)
    await process_frame
    slider.grab_focus()
    await process_frame
    if get_root().gui_get_focus_owner() != slider: quit(3); return
    await edge("ui_right", true, slider, 6.0, [6.0], "Value 6")
    button.grab_focus()
    await process_frame
    await edge("ui_right", true, button, 6.0, [6.0], "Value 6")
    await edge("ui_right", false, button, 6.0, [6.0], "Value 6")
    slider.grab_focus()
    await process_frame
    await edge("ui_left", true, slider, 5.0, [6.0,5.0], "Value 5")
    await edge("ui_left", false, slider, 5.0, [6.0,5.0], "Value 5")
    button.grab_focus()
    await process_frame
    await edge("ui_left", true, button, 5.0, [6.0,5.0], "Value 5")
    await edge("ui_left", false, button, 5.0, [6.0,5.0], "Value 5")
    print("R43_EXPECTED_NEGATIVE_CONFIRMED")
    quit(2)
func edge(action: String, pressed: bool, owner: Control, value: float, history: Array[float], text: String) -> void:
    if get_root().gui_get_focus_owner() != owner or slider.has_focus() != (owner == slider):
        push_error("FOCUS PRE EVENT FAILED "+action+" "+str(pressed)); quit(4); return
    var event := InputEventAction.new()
    event.action = action
    event.pressed = pressed
    Input.parse_input_event(event)
    await process_frame
    print("EDGE "+action+" "+str(pressed)+" owner="+str(get_root().gui_get_focus_owner())+" value="+str(slider.value)+" receipts="+str(receipts)+" label="+label.text)
    if slider.value != value or receipts != history or label.text != text:
        push_error("STATE HYPOTHESIS FALSE after "+action+" "+str(pressed)); quit(5); return
func _receipt(v: float) -> void:
    receipts.append(v)
    label.text = "Value %d" % int(v)
