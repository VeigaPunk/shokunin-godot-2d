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
    var other := Button.new()
    other.text = "Other"
    other.focus_mode = Control.FOCUS_ALL
    ui.add_child(slider)
    ui.add_child(label)
    ui.add_child(other)
    root.add_child(ui)
    slider.value_changed.connect(_on_value_changed)
    await process_frame
    slider.grab_focus()
    await process_frame
    if not slider.is_inside_tree() or slider.value != 5.0 or receipts != [] or label.text != "Value 5" or get_root().gui_get_focus_owner() != slider:
        push_error("setup failed")
        quit(2)
        return
    var edges := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]
    var values: Array[float] = [6.0, 6.0, 6.0, 5.0, 5.0, 5.0, 5.0]
    var histories: Array = [[6.0], [6.0], [6.0], [6.0,5.0], [6.0,5.0], [6.0,5.0], [6.0,5.0]]
    for i in range(edges.size()):
        if i == 1 or i == 5:
            other.grab_focus()
            await process_frame
        elif i == 3:
            slider.grab_focus()
            await process_frame
        var expected_owner: Control = other if i in [1,2,5,6] else slider
        if get_root().gui_get_focus_owner() != expected_owner or slider.has_focus() != (expected_owner == slider):
            push_error("owner assertion failed before edge %d" % i)
            quit(2)
            return
        var before_count := receipts.size()
        var edge: Array = edges[i]
        var ev := InputEventAction.new()
        ev.action = edge[0]
        ev.pressed = edge[1]
        Input.parse_input_event(ev)
        await process_frame
        var expected_receipts: Array = histories[i]
        var expected_label := "Value %d" % int(values[i])
        if slider.value != values[i] or receipts != expected_receipts or label.text != expected_label:
            push_error("edge state failed edge=%d action=%s pressed=%s value=%s receipts=%s label=%s" % [i, edge[0], edge[1], slider.value, receipts, label.text])
            quit(2)
            return
        print("EDGE %d owner=%s action=%s pressed=%s value=%s receipts=%s label=%s new_receipt=%s" % [i, expected_owner.name, edge[0], edge[1], slider.value, receipts, label.text, receipts.size() > before_count])
    print("R43_SECOND_FOCUS_LOSS values=6,6,6,5,5,5,5 receipts=[6.0,5.0] label=Value 5 owner_button=true")
    push_error("EXPECTED NEGATIVE: second focus loss prevents final adjustment; expected positive r42 final=4 receipts=[6,5,4]")
    quit(2)

func _on_value_changed(value: float) -> void:
    receipts.append(value)
    label.text = "Value %d" % int(value)
