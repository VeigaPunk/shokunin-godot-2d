extends SceneTree
var slider: HSlider
var label: Label
var value_receipts: Array[float] = []
var disconnected := OS.get_cmdline_user_args().has("--disconnect-signal")
var no_focus := OS.get_cmdline_user_args().has("--no-focus")

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
    if not no_focus:
        slider.grab_focus()
    await process_frame
    if not slider.is_inside_tree() or slider.value != 5.0 or value_receipts != [] or label.text != "Value 5":
        push_error("SLIDER setup assertion failed: expected in-tree value=5 Label=Value 5")
        quit(2)
        return
    if no_focus:
        if slider.has_focus() or get_root().gui_get_focus_owner() == slider:
            push_error("SLIDER no-focus setup assertion failed: slider owns GUI focus")
            quit(2)
            return
    elif not slider.has_focus() or get_root().gui_get_focus_owner() != slider:
        push_error("SLIDER focus assertion failed before ui_right")
        quit(2)
        return
    _action("ui_right", true)
    await process_frame
    print("EDGE right press value=%s receipts=%s label=%s" % [slider.value, value_receipts, label.text])
    _action("ui_right", false)
    await process_frame
    print("EDGE right release value=%s receipts=%s label=%s" % [slider.value, value_receipts, label.text])
    var right_value := slider.value
    var right_receipts := value_receipts.duplicate()
    var right_label := label.text
    if disconnected and not no_focus and (right_value != 6.0 or right_receipts != [] or right_label != "Value 5"):
        push_error("SLIDER DISCONNECTED CONTROL ASSERTION FAILED after ui_right: expected value=6 receipts=[] Label=Value 5")
        quit(2)
        return
    if no_focus:
        if slider.has_focus() or get_root().gui_get_focus_owner() == slider:
            push_error("SLIDER no-focus assertion failed before ui_left: slider owns GUI focus")
            quit(2)
            return
    elif get_root().gui_get_focus_owner() != slider:
        push_error("SLIDER focus assertion failed before ui_left")
        quit(2)
        return
    _action("ui_left", true)
    await process_frame
    print("EDGE left press value=%s receipts=%s label=%s" % [slider.value, value_receipts, label.text])
    _action("ui_left", false)
    await process_frame
    print("EDGE left release value=%s receipts=%s label=%s" % [slider.value, value_receipts, label.text])
    var left_value := slider.value
    if no_focus:
        print("SLIDER_NO_FOCUS values=%s,%s receipts=%s label=%s focus_owner=%s" % [right_value, left_value, value_receipts, label.text, get_root().gui_get_focus_owner()])
        if right_value != 5.0 or left_value != 5.0 or value_receipts != [] or label.text != "Value 5":
            push_error("SLIDER NO-FOCUS CONTROL ASSERTION FAILED: expected values=5,5 receipts=[] Label=Value 5")
            quit(2)
            return
        push_error("SLIDER NO-FOCUS ASSERTION FAILED: expected focus-dependent adjustment values=6,5")
        quit(2)
        return
    if disconnected:
        print("SLIDER_DISCONNECTED values=%s,%s receipts=%s label=%s" % [right_value, left_value, value_receipts, label.text])
        if right_value != 6.0 or left_value != 5.0 or value_receipts != [] or label.text != "Value 5":
            push_error("SLIDER DISCONNECTED CONTROL ASSERTION FAILED: expected numeric transitions 6,5 receipts=[] Label=Value 5")
            quit(2)
            return
        push_error("SLIDER SIGNAL ASSERTION FAILED: expected value_changed receipts [6,5] and Labels [Value 6,Value 5]")
        quit(2)
        return
    if right_value != 6.0 or right_receipts != [6.0] or right_label != "Value 6" or left_value != 5.0 or value_receipts != [6.0, 5.0] or label.text != "Value 5":
        push_error("SLIDER assertion failed: expected values=6,5 receipts=[6,5] Labels=[Value 6,Value 5]")
        quit(2)
        return
    print("PASS slider_adjust focused=true range=0..10 step=1 values=6,5 receipts=6,5 Labels=Value 6,Value 5")
    quit(0)

func _action(action: String, pressed: bool) -> void:
    var event := InputEventAction.new()
    event.action = action
    event.pressed = pressed
    Input.parse_input_event(event)

func _on_value_changed(value: float) -> void:
    value_receipts.append(value)
    label.text = "Value %d" % int(value)
