extends SceneTree
var slider: HSlider
var receipts: Array[float] = []
var label: Label
func _initialize() -> void:
    run.call_deferred()
func _value(v: float) -> void:
    receipts.append(v)
func send_action(a: String) -> void:
    var e := InputEventAction.new()
    e.action = a
    e.pressed = true
    Input.parse_input_event(e)
    await process_frame
    e = InputEventAction.new()
    e.action = a
    e.pressed = false
    Input.parse_input_event(e)
    await process_frame
func run() -> void:
    var root_ui := Control.new()
    slider = HSlider.new()
    slider.min_value = 0
    slider.max_value = 10
    slider.step = 1
    slider.value = 5
    slider.focus_mode = Control.FOCUS_ALL
    label = Label.new()
    label.text = "Value %d" % int(slider.value)
    root_ui.add_child(slider)
    root_ui.add_child(label)
    root.add_child(root_ui)
    if not OS.get_cmdline_user_args().has("--disconnect"):
        slider.value_changed.connect(_value)
        slider.value_changed.connect(func(v: float): label.text = "Value %d" % int(v))
    await process_frame
    slider.grab_focus()
    await process_frame
    print("SETUP value=%s focused=%s focus_owner=%s label=%s" % [slider.value, slider.has_focus(), get_root().gui_get_focus_owner(), label.text])
    await send_action("ui_right")
    print("AFTER_RIGHT value=%s receipts=%s label=%s focus=%s" % [slider.value, receipts, label.text, slider.has_focus()])
    await send_action("ui_left")
    print("AFTER_LEFT value=%s receipts=%s label=%s focus=%s" % [slider.value, receipts, label.text, slider.has_focus()])
    quit(0)
