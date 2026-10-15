extends SceneTree
var slider: HSlider
var label: Label
var value_receipts: Array[float] = []
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
    if not disconnected:
        slider.value_changed.connect(_on_value_changed)
    await process_frame
    await process_frame
    if not slider.is_inside_tree() or get_root().gui_get_focus_owner() == slider or slider.value != 5.0 or value_receipts != [] or label.text != "Value 5":
        push_error("SLIDER setup assertion failed: expected no focus owner, in-tree value=5 Label=Value 5")
        quit(2)
        return
    if get_root().gui_get_focus_owner() == slider:
        push_error("SLIDER no-focus assertion failed before ui_right")
        quit(2)
        return
    _action("ui_right", true)
    await process_frame
    _action("ui_right", false)
    await process_frame
    print("OBS right owner_is_slider=%s focus_owner=%s value=%s" % [get_root().gui_get_focus_owner() == slider, str(get_root().gui_get_focus_owner()), slider.value])
    var right_value := slider.value
    var right_receipts := value_receipts.duplicate()
    var right_label := label.text
    if disconnected and (right_value != 6.0 or right_receipts != [] or right_label != "Value 5"):
        push_error("SLIDER DISCONNECTED CONTROL ASSERTION FAILED after ui_right: expected value=6 receipts=[] Label=Value 5")
        quit(2)
        return
    if get_root().gui_get_focus_owner() == slider:
        push_error("SLIDER no-focus assertion failed before ui_left")
        quit(2)
        return
    _action("ui_left", true)
    await process_frame
    _action("ui_left", false)
    await process_frame
    print("OBS left owner_is_slider=%s focus_owner=%s value=%s" % [get_root().gui_get_focus_owner() == slider, str(get_root().gui_get_focus_owner()), slider.value])
    var left_value := slider.value
    if disconnected:
        print("SLIDER_DISCONNECTED values=%s,%s receipts=%s label=%s" % [right_value, left_value, value_receipts, label.text])
        if right_value != 6.0 or left_value != 5.0 or value_receipts != [] or label.text != "Value 5":
            push_error("SLIDER DISCONNECTED CONTROL ASSERTION FAILED: expected numeric transitions 6,5 receipts=[] Label=Value 5")
            quit(2)
            return
        push_error("SLIDER SIGNAL ASSERTION FAILED: expected value_changed receipts [6,5] and Labels [Value 6,Value 5]")
        quit(2)
        return
    print("OBS no_focus values=%s,%s receipts=%s label=%s" % [right_value, left_value, value_receipts, label.text])
    if right_value != 5.0 or left_value != 5.0 or value_receipts != [] or label.text != "Value 5":
        push_error("SLIDER NO-FOCUS CONTROL ASSERTION FAILED: expected values=5,5 receipts=[] Label=Value 5")
        quit(2)
        return
    push_error("SLIDER NO-FOCUS CONTROL ASSERTION FAILED after both actions: expected no value change without focus")
    quit(2)

func _action(action: String, pressed: bool) -> void:
    var event := InputEventAction.new()
    event.action = action
    event.pressed = pressed
    Input.parse_input_event(event)

func _on_value_changed(value: float) -> void:
    value_receipts.append(value)
    label.text = "Value %d" % int(value)
