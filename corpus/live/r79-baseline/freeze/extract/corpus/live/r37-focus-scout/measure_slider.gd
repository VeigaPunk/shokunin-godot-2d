extends SceneTree
var s: HSlider
var label: Label
var rec: Array[float] = []
func action(name: String, down: bool) -> void:
    var e := InputEventAction.new()
    e.action = name
    e.pressed = down
    Input.parse_input_event(e)
    await process_frame
func run_case(connected: bool) -> void:
    s = HSlider.new()
    s.min_value = 0
    s.max_value = 10
    s.step = 1
    s.value = 5
    s.focus_mode = Control.FOCUS_ALL
    label = Label.new()
    label.text = "Value 5"
    root.add_child(s)
    root.add_child(label)
    if connected:
        s.value_changed.connect(func(v):
            rec.append(v)
            label.text = "Value %d" % int(v)
        )
    await process_frame
    s.grab_focus()
    await process_frame
    print("CASE connected=%s BEFORE focus=%s value=%s label=%s rec=%s" % [connected, s.has_focus(), s.value, label.text, rec])
    await action("ui_right", true)
    print("RIGHT_PRESS value=%s label=%s rec=%s" % [s.value, label.text, rec])
    await action("ui_right", false)
    print("RIGHT_RELEASE value=%s label=%s rec=%s" % [s.value, label.text, rec])
    await action("ui_left", true)
    print("LEFT_PRESS value=%s label=%s rec=%s" % [s.value, label.text, rec])
    await action("ui_left", false)
    print("LEFT_RELEASE value=%s label=%s rec=%s" % [s.value, label.text, rec])
    s.queue_free()
    label.queue_free()
    await process_frame
    rec.clear()
func _initialize() -> void:
    await run_case(true)
    await run_case(false)
    quit()
