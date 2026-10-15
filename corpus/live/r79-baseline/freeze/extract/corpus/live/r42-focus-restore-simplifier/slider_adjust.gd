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
    if OS.get_cmdline_user_args().has("--r42"):
        var other := Button.new()
        other.text = "Other"
        other.focus_mode = Control.FOCUS_ALL
        ui.add_child(other)
        var edges := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]
        var expected_values: Array[float] = [6.0, 6.0, 6.0, 5.0, 5.0, 4.0, 4.0]
        var expected_receipts: Array = [[6.0], [6.0], [6.0], [6.0, 5.0], [6.0, 5.0], [6.0, 5.0, 4.0], [6.0, 5.0, 4.0]]
        for i in range(edges.size()):
            if i == 1:
                other.grab_focus()
                await process_frame
            if i == 3:
                slider.grab_focus()
                await process_frame
            var owner: Control = other if i == 1 or i == 2 else slider
            if get_root().gui_get_focus_owner() != owner or slider.has_focus() != (owner == slider):
                push_error("R42 owner before edge %d" % i); quit(2); return
            _action(edges[i][0], edges[i][1])
            await process_frame
            print("R42 edge=%d owner=%s value=%s receipts=%s label=%s" % [i, "slider" if get_root().gui_get_focus_owner() == slider else "other", slider.value, value_receipts, label.text])
            var exp_label := "Value %d" % int(expected_values[i])
            if slider.value != expected_values[i] or value_receipts != expected_receipts[i] or label.text != exp_label:
                push_error("R42 state mismatch after edge %d" % i); quit(2); return
        print("PASS R42 values=6,6,6,5,5,4,4 receipts=6,5,4")
        quit(0)
        return
    if OS.get_cmdline_user_args().has("--repeat-right"):
        var edges := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]
        var expected_values: Array[float] = [6.0, 7.0, 7.0, 6.0, 6.0, 5.0, 5.0]
        var expected_receipt_history: Array[float] = [6.0, 7.0, 6.0, 5.0]
        for i in range(edges.size()):
            if no_focus:
                if slider.has_focus() or get_root().gui_get_focus_owner() == slider:
                    push_error("SLIDER repeat no-focus assertion failed before edge %d" % i)
                    quit(2)
                    return
            elif not slider.has_focus() or get_root().gui_get_focus_owner() != slider:
                push_error("SLIDER repeat focus assertion failed before edge %d" % i)
                quit(2)
                return
            _action(edges[i][0], edges[i][1])
            await process_frame
            var edge_expected_value := 5.0 if no_focus else expected_values[i]
            var expected_receipts: Array[float] = []
            if not disconnected and not no_focus:
                var receipt_count: int = [1, 2, 2, 3, 3, 4, 4][i]
                expected_receipts = expected_receipt_history.slice(0, receipt_count)
            var expected_label := "Value %d" % int(expected_values[i]) if not disconnected and not no_focus else "Value 5"
            if slider.value != edge_expected_value or value_receipts != expected_receipts or label.text != expected_label:
                push_error("SLIDER repeat edge assertion failed: %s %s" % [edges[i][0], "press" if edges[i][1] else "release"])
                quit(2)
                return
        if no_focus:
            print("SLIDER_REPEAT_NO_FOCUS values=%s receipts=%s label=%s focus_owner=%s" % [[5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0], value_receipts, label.text, get_root().gui_get_focus_owner()])
            push_error("SLIDER REPEAT NO-FOCUS ASSERTION FAILED: expected focus-dependent adjustment values=6,7,7,6,6,5,5")
            quit(2)
            return
        if disconnected:
            print("SLIDER_REPEAT_DISCONNECTED values=%s receipts=%s label=%s" % [expected_values, value_receipts, label.text])
            push_error("SLIDER REPEAT SIGNAL ASSERTION FAILED: expected value_changed receipts [6,7,6,5] and Labels [Value 6,Value 7,Value 6,Value 5]")
            quit(2)
            return
        print("PASS slider_adjust_repeat focused=true range=0..10 step=1 values=6,7,7,6,6,5,5 receipts=6,7,6,5 Labels=Value 6,Value 7,Value 6,Value 5")
        quit(0)
        return
    var right_expected_value := 5.0 if no_focus else 6.0
    var right_expected_receipts: Array[float] = []
    if not disconnected and not no_focus:
        right_expected_receipts.append(6.0)
    var right_expected_label := "Value 5" if disconnected or no_focus else "Value 6"
    _action("ui_right", true)
    await process_frame
    if slider.value != right_expected_value or value_receipts != right_expected_receipts or label.text != right_expected_label:
        push_error("SLIDER edge assertion failed: ui_right press")
        quit(2)
        return
    _action("ui_right", false)
    await process_frame
    if slider.value != right_expected_value or value_receipts != right_expected_receipts or label.text != right_expected_label:
        push_error("SLIDER edge assertion failed: ui_right release")
        quit(2)
        return
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
    var left_expected_receipts: Array[float] = []
    if not disconnected and not no_focus:
        left_expected_receipts.append(6.0)
        left_expected_receipts.append(5.0)
    _action("ui_left", true)
    await process_frame
    if slider.value != 5.0 or value_receipts != left_expected_receipts or label.text != "Value 5":
        push_error("SLIDER edge assertion failed: ui_left press")
        quit(2)
        return
    _action("ui_left", false)
    await process_frame
    if slider.value != 5.0 or value_receipts != left_expected_receipts or label.text != "Value 5":
        push_error("SLIDER edge assertion failed: ui_left release")
        quit(2)
        return
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
