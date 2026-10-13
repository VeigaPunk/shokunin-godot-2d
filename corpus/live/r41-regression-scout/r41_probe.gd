extends SceneTree
var slider: HSlider
var other: Button
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
    other = Button.new()
    other.text = "Other"
    other.focus_mode = Control.FOCUS_ALL
    label = Label.new()
    label.text = "Value 5"
    ui.add_child(slider)
    ui.add_child(other)
    ui.add_child(label)
    root.add_child(ui)
    slider.value_changed.connect(_on_value_changed)
    await process_frame
    slider.grab_focus()
    await process_frame
    if get_root().gui_get_focus_owner() != slider:
        push_error("SETUP slider not focus owner")
        quit(2); return
    var edges := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]
    for i in range(edges.size()):
        if i == 1:
            other.grab_focus()
            await process_frame
            print("HANDOFF owner_other=%s slider_has_focus=%s" % [get_root().gui_get_focus_owner() == other, slider.has_focus()])
            if get_root().gui_get_focus_owner() != other or slider.has_focus():
                push_error("FOCUS TRANSFER DIFFERED before edge 1")
                quit(2); return
        if i == 0:
            if get_root().gui_get_focus_owner() != slider:
                push_error("first edge slider not owner")
                quit(2); return
        elif get_root().gui_get_focus_owner() != other or slider.has_focus():
            push_error("focus owner differs before edge %d" % i)
            quit(2); return
        var event := InputEventAction.new()
        event.action = edges[i][0]
        event.pressed = edges[i][1]
        Input.parse_input_event(event)
        await process_frame
        if slider.value != 6.0 or receipts != [6.0] or label.text != "Value 6":
            push_error("edge result differs at %d: value=%s receipts=%s label=%s" % [i, slider.value, receipts, label.text])
            quit(2); return
    print("R41_HANDOFF values=6,[6],[6],[6],[6],[6],[6] receipts=%s label=%s owner_other=%s" % [receipts, label.text, get_root().gui_get_focus_owner() == other])
    push_error("R41 HANDOFF EXPECTED-NEGATIVE: expected focus-dependent adjustment after transfer")
    quit(2)
func _on_value_changed(value: float) -> void:
    receipts.append(value)
    label.text = "Value %d" % int(value)
