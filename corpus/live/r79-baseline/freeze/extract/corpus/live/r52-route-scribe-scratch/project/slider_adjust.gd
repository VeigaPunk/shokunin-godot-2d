extends SceneTree
var slider: HSlider
var label: Label
var value_receipts: Array[float] = []
var disconnected := OS.get_cmdline_user_args().has("--disconnect-signal")
var no_focus := OS.get_cmdline_user_args().has("--no-focus")
var parsed_release_observer: ParsedReleaseObserver

class ParsedReleaseObserver extends Node:
    var ui_left_releases: int = 0
    func _input(event: InputEvent) -> void:
        if event is InputEventAction and event.action == "ui_left" and not event.pressed:
            ui_left_releases += 1


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
    if OS.get_cmdline_user_args().has("--observe-parsed-release"):
        parsed_release_observer = ParsedReleaseObserver.new()
        root.add_child(parsed_release_observer)
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
    if OS.get_cmdline_user_args().has("--repeat-right") and OS.get_cmdline_user_args().has("--second-focus-loss"):
        var other := Button.new()
        other.text = "Other"
        other.focus_mode = Control.FOCUS_ALL
        ui.add_child(other)
        var edges := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]
        var expected_values: Array[float] = [6.0, 6.0, 6.0, 5.0, 5.0, 5.0, 5.0]
        var expected_receipts: Array[float] = [6.0, 5.0]
        var prior_receipt_counts: Array[int] = [1, 1, 1, 2, 2, 2, 2]
        for i in range(edges.size()):
            if i == 1 or i == 5:
                other.grab_focus()
                await process_frame
            elif i == 3:
                slider.grab_focus()
                await process_frame
            var expected_owner: Control = other if i in [1, 2, 5, 6] else slider
            if get_root().gui_get_focus_owner() != expected_owner or slider.has_focus() != (expected_owner == slider):
                push_error("SLIDER second-focus-loss owner assertion failed before edge %d" % i)
                quit(2)
                return
            _action(edges[i][0], edges[i][1])
            await process_frame
            var edge_receipts: Array[float] = []
            if not disconnected:
                edge_receipts = expected_receipts.slice(0, prior_receipt_counts[i])
            var edge_label := "Value %d" % int(expected_values[i]) if not disconnected else "Value 5"
            if slider.value != expected_values[i] or value_receipts != edge_receipts or label.text != edge_label:
                push_error("SLIDER second-focus-loss edge assertion failed: edge=%d action=%s %s" % [i, edges[i][0], "press" if edges[i][1] else "release"])
                quit(2)
                return
        print("SLIDER_REPEAT_SECOND_FOCUS_LOSS values=6,6,6,5,5,5,5 receipts=6,5 Labels=Value 6,Value 5")
        push_error("SLIDER REPEAT SECOND-FOCUS-LOSS ASSERTION FAILED: expected final restored-focus adjustment after seven checks")
        quit(2)
        return
    if OS.get_cmdline_user_args().has("--repeat-right") and OS.get_cmdline_user_args().has("--second-focus-restore") and OS.get_cmdline_user_args().has("--release-after-late-reconnect-press"):
        var other := Button.new()
        other.text = "Other"
        other.focus_mode = Control.FOCUS_ALL
        ui.add_child(other)
        var edges := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]
        var expected_values: Array[float] = [6.0, 6.0, 6.0, 5.0, 5.0, 5.0, 5.0, 4.0, 4.0, 3.0, 3.0]
        var expected_receipts: Array[float] = [6.0, 3.0]
        var receipt_counts: Array[int] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2]
        for i in range(edges.size()):
            if i == 1 or i == 5:
                other.grab_focus()
                await process_frame
            elif i == 3 or i == 7:
                slider.grab_focus()
                await process_frame
            var expected_owner: Control = other if i in [1, 2, 5, 6] else slider
            if get_root().gui_get_focus_owner() != expected_owner or slider.has_focus() != (expected_owner == slider):
                push_error("SLIDER release-after-reconnect owner assertion failed before edge %d" % i)
                quit(2)
                return
            var should_connect := i == 0 or i >= 8
            if slider.value_changed.is_connected(_on_value_changed) != should_connect:
                push_error("SLIDER release-after-reconnect callback assertion failed before edge %d" % i)
                quit(2)
                return
            if i == 10 and not Input.is_action_pressed("ui_left"):
                push_error("SLIDER input-state pre-release assertion failed: ui_left not pressed")
                quit(2)
                return
            _action(edges[i][0], edges[i][1])
            await process_frame
            if i == 10 and Input.is_action_pressed("ui_left"):
                push_error("SLIDER input-state post-release assertion failed: ui_left remains pressed")
                quit(2)
                return
            var expected_edge_receipts: Array[float] = expected_receipts.slice(0, receipt_counts[i])
            var expected_edge_label := "Value %d" % int(expected_values[i]) if i >= 9 else "Value 6"
            if slider.value != expected_values[i] or value_receipts != expected_edge_receipts or label.text != expected_edge_label:
                push_error("SLIDER release-after-reconnect edge assertion failed: edge=%d action=%s %s" % [i, edges[i][0], "press" if edges[i][1] else "release"])
                quit(2)
                return
            if i == 0:
                slider.value_changed.disconnect(_on_value_changed)
                if slider.value_changed.is_connected(_on_value_changed):
                    push_error("SLIDER release-after-reconnect disconnect assertion failed after edge0")
                    quit(2)
                    return
            elif i == 7:
                slider.value_changed.connect(_on_value_changed)
                if not slider.value_changed.is_connected(_on_value_changed):
                    push_error("SLIDER release-after-reconnect connect assertion failed after edge7")
                    quit(2)
                    return
        print("SLIDER_RELEASE_AFTER_LATE_RECONNECT_PRESS values=6,6,6,5,5,5,5,4,4,3,3 receipts=6,3 Labels=Value 6,Value 3 callback_connected=true")
        push_error("SLIDER RELEASE AFTER LATE-RECONNECT PRESS ASSERTION FAILED: expected no new receipt after eleven checks")
        quit(2)
        return
    if OS.get_cmdline_user_args().has("--repeat-right") and OS.get_cmdline_user_args().has("--second-focus-restore") and OS.get_cmdline_user_args().has("--observe-parsed-release"):
        var other := Button.new()
        other.text = "Other"
        other.focus_mode = Control.FOCUS_ALL
        ui.add_child(other)
        var edges := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]
        var expected_values: Array[float] = [6.0, 6.0, 6.0, 5.0, 5.0, 5.0, 5.0, 4.0, 4.0, 3.0, 3.0]
        var expected_receipts: Array[float] = [6.0, 3.0]
        var receipt_counts: Array[int] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2]
        for i in range(edges.size()):
            if i == 1 or i == 5:
                other.grab_focus()
                await process_frame
            elif i == 3 or i == 7:
                slider.grab_focus()
                await process_frame
            var expected_owner: Control = other if i in [1, 2, 5, 6] else slider
            if get_root().gui_get_focus_owner() != expected_owner or slider.has_focus() != (expected_owner == slider):
                push_error("SLIDER observe-parsed-release owner assertion failed before edge %d" % i)
                quit(2)
                return
            var should_connect := i == 0 or i >= 8
            if slider.value_changed.is_connected(_on_value_changed) != should_connect:
                push_error("SLIDER observe-parsed-release callback assertion failed before edge %d" % i)
                quit(2)
                return
            if i == 10 and not Input.is_action_pressed("ui_left"):
                push_error("SLIDER input-state pre-release assertion failed: ui_left not pressed")
                quit(2)
                return
            var release_count_before: int = parsed_release_observer.ui_left_releases
            _action(edges[i][0], edges[i][1])
            await process_frame
            if i == 10 and parsed_release_observer.ui_left_releases != release_count_before + 1:
                push_error("SLIDER parsed ui_left release observer failed: expected exactly one delivered release")
                quit(2)
                return
            if i == 10 and Input.is_action_pressed("ui_left"):
                push_error("SLIDER input-state post-release assertion failed: ui_left remains pressed")
                quit(2)
                return
            var expected_edge_receipts: Array[float] = expected_receipts.slice(0, receipt_counts[i])
            var expected_edge_label := "Value %d" % int(expected_values[i]) if i >= 9 else "Value 6"
            if slider.value != expected_values[i] or value_receipts != expected_edge_receipts or label.text != expected_edge_label:
                push_error("SLIDER observe-parsed-release edge assertion failed: edge=%d action=%s %s" % [i, edges[i][0], "press" if edges[i][1] else "release"])
                quit(2)
                return
            if i == 0:
                slider.value_changed.disconnect(_on_value_changed)
                if slider.value_changed.is_connected(_on_value_changed):
                    push_error("SLIDER observe-parsed-release disconnect assertion failed after edge0")
                    quit(2)
                    return
            elif i == 7:
                slider.value_changed.connect(_on_value_changed)
                if not slider.value_changed.is_connected(_on_value_changed):
                    push_error("SLIDER observe-parsed-release connect assertion failed after edge7")
                    quit(2)
                    return
        print("SLIDER_PARSED_RELEASE_OBSERVER values=6,6,6,5,5,5,5,4,4,3,3 receipts=6,3 Labels=Value 6,Value 3 callback_connected=true")
        push_error("SLIDER PARSED RELEASE OBSERVER ASSERTION FAILED: expected no new receipt after eleven checks")
        quit(2)
        return
    if OS.get_cmdline_user_args().has("--repeat-right") and OS.get_cmdline_user_args().has("--second-focus-restore") and OS.get_cmdline_user_args().has("--observe-push-input-release"):
        var other := Button.new()
        other.text = "Other"
        other.focus_mode = Control.FOCUS_ALL
        ui.add_child(other)
        var edges := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]
        var expected_values: Array[float] = [6.0, 6.0, 6.0, 5.0, 5.0, 5.0, 5.0, 4.0, 4.0, 3.0, 3.0]
        var expected_receipts: Array[float] = [6.0, 3.0]
        var receipt_counts: Array[int] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2]
        for i in range(edges.size()):
            if i == 1 or i == 5:
                other.grab_focus()
                await process_frame
            elif i == 3 or i == 7:
                slider.grab_focus()
                await process_frame
            var expected_owner: Control = other if i in [1, 2, 5, 6] else slider
            if get_root().gui_get_focus_owner() != expected_owner or slider.has_focus() != (expected_owner == slider):
                push_error("SLIDER observe-push-input-release owner assertion failed before edge %d" % i)
                quit(2)
                return
            var should_connect := i == 0 or i >= 8
            if slider.value_changed.is_connected(_on_value_changed) != should_connect:
                push_error("SLIDER observe-push-input-release callback assertion failed before edge %d" % i)
                quit(2)
                return
            if i == 10 and not Input.is_action_pressed("ui_left"):
                push_error("SLIDER input-state pre-release assertion failed: ui_left not pressed")
                quit(2)
                return
            var release_count_before: int = parsed_release_observer.ui_left_releases
            if i == 10:
                var pushed := InputEventAction.new()
                pushed.action = "ui_left"
                pushed.pressed = false
                root.push_input(pushed)
            else:
                _action(edges[i][0], edges[i][1])
            await process_frame
            if i == 10 and parsed_release_observer.ui_left_releases != release_count_before + 1:
                push_error("SLIDER pushed ui_left release observer failed: expected exactly one delivered release")
                quit(2)
                return
            if i == 10 and Input.is_action_pressed("ui_left"):
                push_error("SLIDER pushed ui_left release action-state assertion failed: remains pressed")
                quit(2)
                return
            var expected_edge_receipts: Array[float] = expected_receipts.slice(0, receipt_counts[i])
            var expected_edge_label := "Value %d" % int(expected_values[i]) if i >= 9 else "Value 6"
            if slider.value != expected_values[i] or value_receipts != expected_edge_receipts or label.text != expected_edge_label:
                push_error("SLIDER observe-push-input-release edge assertion failed: edge=%d action=%s %s" % [i, edges[i][0], "press" if edges[i][1] else "release"])
                quit(2)
                return
            if i == 0:
                slider.value_changed.disconnect(_on_value_changed)
                if slider.value_changed.is_connected(_on_value_changed):
                    push_error("SLIDER observe-push-input-release disconnect assertion failed after edge0")
                    quit(2)
                    return
            elif i == 7:
                slider.value_changed.connect(_on_value_changed)
                if not slider.value_changed.is_connected(_on_value_changed):
                    push_error("SLIDER observe-push-input-release connect assertion failed after edge7")
                    quit(2)
                    return
        print("SLIDER_PARSED_RELEASE_OBSERVER values=6,6,6,5,5,5,5,4,4,3,3 receipts=6,3 Labels=Value 6,Value 3 callback_connected=true")
        push_error("SLIDER PUSHED RELEASE ASSERTION FAILED: expected no new receipt after eleven checks")
        quit(2)
        return
    if OS.get_cmdline_user_args().has("--repeat-right") and OS.get_cmdline_user_args().has("--second-focus-restore") and OS.get_cmdline_user_args().has("--press-after-late-reconnect"):
        var other := Button.new()
        other.text = "Other"
        other.focus_mode = Control.FOCUS_ALL
        ui.add_child(other)
        var edges := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false], ["ui_left", true]]
        var expected_values: Array[float] = [6.0, 6.0, 6.0, 5.0, 5.0, 5.0, 5.0, 4.0, 4.0, 3.0]
        var expected_receipts: Array[float] = [6.0, 3.0]
        var receipt_counts: Array[int] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 2]
        for i in range(edges.size()):
            if i == 1 or i == 5:
                other.grab_focus()
                await process_frame
            elif i == 3 or i == 7:
                slider.grab_focus()
                await process_frame
            var expected_owner: Control = other if i in [1, 2, 5, 6] else slider
            if get_root().gui_get_focus_owner() != expected_owner or slider.has_focus() != (expected_owner == slider):
                push_error("SLIDER fresh reconnect owner assertion failed before edge %d" % i)
                quit(2)
                return
            if i == 0 and not slider.value_changed.is_connected(_on_value_changed):
                push_error("SLIDER fresh reconnect expected callback connected before edge0")
                quit(2)
                return
            if i == 8 and not slider.value_changed.is_connected(_on_value_changed):
                push_error("SLIDER fresh reconnect edge9 expected callback connected")
                quit(2)
                return
            _action(edges[i][0], edges[i][1])
            await process_frame
            var expected_edge_receipts: Array[float] = expected_receipts.slice(0, receipt_counts[i])
            var expected_edge_label := "Value %d" % int(expected_values[i]) if i == 9 else "Value 6"
            if slider.value != expected_values[i] or value_receipts != expected_edge_receipts or label.text != expected_edge_label:
                push_error("SLIDER fresh reconnect edge assertion failed: edge=%d action=%s %s" % [i, edges[i][0], "press" if edges[i][1] else "release"])
                quit(2)
                return
            if i == 0:
                slider.value_changed.disconnect(_on_value_changed)
                if slider.value_changed.is_connected(_on_value_changed):
                    push_error("SLIDER fresh reconnect disconnect assertion failed after edge0")
                    quit(2)
                    return
            elif i == 7:
                if slider.value_changed.is_connected(_on_value_changed):
                    push_error("SLIDER fresh reconnect remained connected before edge7 reconnect")
                    quit(2)
                    return
                slider.value_changed.connect(_on_value_changed)
                if not slider.value_changed.is_connected(_on_value_changed):
                    push_error("SLIDER fresh reconnect connect assertion failed after edge7")
                    quit(2)
                    return
        print("PASS slider_adjust_repeat_second_focus_restore_press_after_late_reconnect values=6,6,6,5,5,5,5,4,4,3 receipts=6,3 Labels=Value 6,Value 3")
        quit(0)
        return
    if OS.get_cmdline_user_args().has("--repeat-right") and OS.get_cmdline_user_args().has("--second-focus-restore") and OS.get_cmdline_user_args().has("--reconnect-after-final-left"):
        var other := Button.new()
        other.text = "Other"
        other.focus_mode = Control.FOCUS_ALL
        ui.add_child(other)
        var edges := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]
        var expected_values: Array[float] = [6.0, 6.0, 6.0, 5.0, 5.0, 5.0, 5.0, 4.0, 4.0]
        for i in range(edges.size()):
            if i == 1 or i == 5:
                other.grab_focus()
                await process_frame
            elif i == 3 or i == 7:
                slider.grab_focus()
                await process_frame
            var expected_owner: Control = other if i in [1, 2, 5, 6] else slider
            if get_root().gui_get_focus_owner() != expected_owner or slider.has_focus() != (expected_owner == slider):
                push_error("SLIDER late-reconnect owner assertion failed before edge %d" % i)
                quit(2)
                return
            if i == 0 and not slider.value_changed.is_connected(_on_value_changed):
                push_error("SLIDER late-reconnect expected connected before edge0")
                quit(2)
                return
            _action(edges[i][0], edges[i][1])
            await process_frame
            if i == 0:
                if slider.value != 6.0 or value_receipts != [6.0] or label.text != "Value 6":
                    push_error("SLIDER late-reconnect edge0 assertion failed before disconnect")
                    quit(2)
                    return
                slider.value_changed.disconnect(_on_value_changed)
                if slider.value_changed.is_connected(_on_value_changed):
                    push_error("SLIDER late-reconnect disconnect assertion failed")
                    quit(2)
                    return
            elif i == 7:
                if slider.value != 4.0 or value_receipts != [6.0] or label.text != "Value 6" or slider.value_changed.is_connected(_on_value_changed):
                    push_error("SLIDER late-reconnect edge7 assertion failed before reconnect")
                    quit(2)
                    return
                slider.value_changed.connect(_on_value_changed)
                if not slider.value_changed.is_connected(_on_value_changed):
                    push_error("SLIDER late-reconnect edge7 reconnect assertion failed")
                    quit(2)
                    return
            else:
                if slider.value != expected_values[i] or value_receipts != [6.0] or label.text != "Value 6":
                    push_error("SLIDER late-reconnect edge assertion failed: edge=%d action=%s %s" % [i, edges[i][0], "press" if edges[i][1] else "release"])
                    quit(2)
                    return
                if i < 7 and slider.value_changed.is_connected(_on_value_changed):
                    push_error("SLIDER late-reconnect remained-disconnected assertion failed edge=%d" % i)
                    quit(2)
                    return
                if i == 8 and not slider.value_changed.is_connected(_on_value_changed):
                    push_error("SLIDER late-reconnect edge8 expected connected assertion failed")
                    quit(2)
                    return
        if not slider.value_changed.is_connected(_on_value_changed) or slider.value != 4.0 or value_receipts != [6.0] or label.text != "Value 6":
            push_error("SLIDER late-reconnect final state assertion failed")
            quit(2)
            return
        print("SLIDER_LATE_RECONNECT values=6,6,6,5,5,5,5,4,4 receipts=[6] Label=Value 6 connected=true")
        push_error("SLIDER LATE-RECONNECT ASSERTION FAILED: expected no retroactive receipt after nine checks")
        quit(2)
        return
    if OS.get_cmdline_user_args().has("--repeat-right") and OS.get_cmdline_user_args().has("--second-focus-restore") and OS.get_cmdline_user_args().has("--reconnect-after-first-left"):
        var other := Button.new()
        other.text = "Other"
        other.focus_mode = Control.FOCUS_ALL
        ui.add_child(other)
        var edges := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]
        var expected_values: Array[float] = [6.0, 6.0, 6.0, 5.0, 5.0, 5.0, 5.0, 4.0, 4.0]
        var expected_receipts: Array[float] = [6.0, 4.0]
        var receipt_counts: Array[int] = [1, 1, 1, 1, 1, 1, 1, 2, 2]
        for i in range(edges.size()):
            if i == 1 or i == 5:
                other.grab_focus()
                await process_frame
            elif i == 3 or i == 7:
                slider.grab_focus()
                await process_frame
            var expected_owner: Control = other if i in [1, 2, 5, 6] else slider
            if get_root().gui_get_focus_owner() != expected_owner or slider.has_focus() != (expected_owner == slider):
                push_error("SLIDER reconnect owner assertion failed before edge %d" % i)
                quit(2)
                return
            _action(edges[i][0], edges[i][1])
            await process_frame
            if i == 0:
                if slider.value != 6.0 or value_receipts != [6.0] or label.text != "Value 6" or not slider.value_changed.is_connected(_on_value_changed):
                    push_error("SLIDER reconnect edge0 assertion failed before disconnect")
                    quit(2)
                    return
                slider.value_changed.disconnect(_on_value_changed)
                if slider.value_changed.is_connected(_on_value_changed):
                    push_error("SLIDER reconnect disconnect transition assertion failed")
                    quit(2)
                    return
            elif i == 3:
                if slider.value != expected_values[i] or value_receipts != [6.0] or label.text != "Value 6" or slider.value_changed.is_connected(_on_value_changed):
                    push_error("SLIDER reconnect edge3 assertion failed before reconnect")
                    quit(2)
                    return
                slider.value_changed.connect(_on_value_changed)
                if not slider.value_changed.is_connected(_on_value_changed):
                    push_error("SLIDER reconnect connect transition assertion failed")
                    quit(2)
                    return
            else:
                var expected_edge_receipts: Array[float] = expected_receipts.slice(0, receipt_counts[i])
                var expected_edge_label := "Value 4" if i >= 7 else "Value 6"
                if slider.value != expected_values[i] or value_receipts != expected_edge_receipts or label.text != expected_edge_label:
                    push_error("SLIDER reconnect edge assertion failed: edge=%d action=%s %s" % [i, edges[i][0], "press" if edges[i][1] else "release"])
                    quit(2)
                    return
        print("PASS slider_adjust_repeat_second_focus_restore_reconnect values=6,6,6,5,5,5,5,4,4 receipts=6,4 Labels=Value 6,Value 4")
        quit(0)
        return
    if OS.get_cmdline_user_args().has("--repeat-right") and OS.get_cmdline_user_args().has("--second-focus-restore") and OS.get_cmdline_user_args().has("--disconnect-after-first"):
        var other := Button.new()
        other.text = "Other"
        other.focus_mode = Control.FOCUS_ALL
        ui.add_child(other)
        var edges := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]
        var expected_values: Array[float] = [6.0, 6.0, 6.0, 5.0, 5.0, 5.0, 5.0, 4.0, 4.0]
        var expected_receipts: Array[float] = [6.0]
        for i in range(edges.size()):
            if i == 1 or i == 5:
                other.grab_focus()
                await process_frame
            elif i == 3 or i == 7:
                slider.grab_focus()
                await process_frame
            var expected_owner: Control = other if i in [1, 2, 5, 6] else slider
            if get_root().gui_get_focus_owner() != expected_owner or slider.has_focus() != (expected_owner == slider):
                push_error("SLIDER mid-disconnect owner assertion failed before edge %d" % i)
                quit(2)
                return
            _action(edges[i][0], edges[i][1])
            await process_frame
            if i == 0:
                if slider.value != 6.0 or value_receipts != [6.0] or label.text != "Value 6":
                    push_error("SLIDER mid-disconnect first-edge assertion failed")
                    quit(2)
                    return
                slider.value_changed.disconnect(_on_value_changed)
            elif slider.value != expected_values[i] or value_receipts != expected_receipts or label.text != "Value 6":
                push_error("SLIDER mid-disconnect edge assertion failed: edge=%d action=%s %s" % [i, edges[i][0], "press" if edges[i][1] else "release"])
                quit(2)
                return
        print("SLIDER_MID_DISCONNECT values=6,6,6,5,5,5,5,4,4 receipts=[6] Label=Value 6")
        push_error("SLIDER MID-DISCONNECT ASSERTION FAILED: expected cumulative callback history to stay [6]")
        quit(2)
        return
    if OS.get_cmdline_user_args().has("--repeat-right") and OS.get_cmdline_user_args().has("--second-focus-restore") and OS.get_cmdline_user_args().has("--disconnect-signal"):
        var other := Button.new()
        other.text = "Other"
        other.focus_mode = Control.FOCUS_ALL
        ui.add_child(other)
        var edges := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]
        var expected_values: Array[float] = [6.0, 6.0, 6.0, 5.0, 5.0, 5.0, 5.0, 4.0, 4.0]
        for i in range(edges.size()):
            if i == 1 or i == 5:
                other.grab_focus()
                await process_frame
            elif i == 3 or i == 7:
                slider.grab_focus()
                await process_frame
            var expected_owner: Control = other if i in [1, 2, 5, 6] else slider
            if get_root().gui_get_focus_owner() != expected_owner or slider.has_focus() != (expected_owner == slider):
                push_error("SLIDER double-restore-disconnect owner assertion failed before edge %d" % i)
                quit(2)
                return
            _action(edges[i][0], edges[i][1])
            await process_frame
            if slider.value != expected_values[i] or value_receipts != [] or label.text != "Value 5":
                push_error("SLIDER double-restore-disconnect edge assertion failed: edge=%d action=%s %s" % [i, edges[i][0], "press" if edges[i][1] else "release"])
                quit(2)
                return
        print("SLIDER_DOUBLE_RESTORE_DISCONNECTED values=6,6,6,5,5,5,5,4,4 receipts=[] Label=Value 5")
        push_error("SLIDER DOUBLE-RESTORE DISCONNECTED ASSERTION FAILED: expected signal-consumer updates")
        quit(2)
        return
    if OS.get_cmdline_user_args().has("--repeat-right") and OS.get_cmdline_user_args().has("--second-focus-restore"):
        var other := Button.new()
        other.text = "Other"
        other.focus_mode = Control.FOCUS_ALL
        ui.add_child(other)
        var edges := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]
        var expected_values: Array[float] = [6.0, 6.0, 6.0, 5.0, 5.0, 5.0, 5.0, 4.0, 4.0]
        var expected_receipts: Array[float] = [6.0, 5.0, 4.0]
        var prior_receipt_counts: Array[int] = [1, 1, 1, 2, 2, 2, 2, 3, 3]
        for i in range(edges.size()):
            if i == 1 or i == 5:
                other.grab_focus()
                await process_frame
            elif i == 3 or i == 7:
                slider.grab_focus()
                await process_frame
            var expected_owner: Control = other if i in [1, 2, 5, 6] else slider
            if get_root().gui_get_focus_owner() != expected_owner or slider.has_focus() != (expected_owner == slider):
                push_error("SLIDER second-focus-restore owner assertion failed before edge %d" % i)
                quit(2)
                return
            _action(edges[i][0], edges[i][1])
            await process_frame
            var edge_receipts: Array[float] = []
            if not disconnected:
                edge_receipts = expected_receipts.slice(0, prior_receipt_counts[i])
            var edge_label := "Value %d" % int(expected_values[i]) if not disconnected else "Value 5"
            if slider.value != expected_values[i] or value_receipts != edge_receipts or label.text != edge_label:
                push_error("SLIDER second-focus-restore edge assertion failed: edge=%d action=%s %s" % [i, edges[i][0], "press" if edges[i][1] else "release"])
                quit(2)
                return
        print("PASS slider_adjust_repeat_second_focus_restore focused=true values=6,6,6,5,5,5,5,4,4 receipts=6,5,4 Labels=Value 6,Value 5,Value 4")
        quit(0)
        return
    if OS.get_cmdline_user_args().has("--repeat-right") and OS.get_cmdline_user_args().has("--focus-restore"):
        var other := Button.new()
        other.text = "Other"
        other.focus_mode = Control.FOCUS_ALL
        ui.add_child(other)
        var edges := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]
        var expected_values: Array[float] = [6.0, 6.0, 6.0, 5.0, 5.0, 4.0, 4.0]
        var expected_receipts: Array[float] = [6.0, 5.0, 4.0]
        var prior_receipt_counts: Array[int] = [1, 1, 1, 2, 2, 3, 3]
        for i in range(edges.size()):
            if i == 1:
                other.grab_focus()
                await process_frame
            elif i == 3:
                slider.grab_focus()
                await process_frame
            var expected_owner: Control = other if i in [1, 2] else slider
            if get_root().gui_get_focus_owner() != expected_owner or slider.has_focus() != (expected_owner == slider):
                push_error("SLIDER focus-restore owner assertion failed before edge %d" % i)
                quit(2)
                return
            _action(edges[i][0], edges[i][1])
            await process_frame
            var edge_receipts: Array[float] = []
            if not disconnected:
                edge_receipts = expected_receipts.slice(0, prior_receipt_counts[i])
            var edge_label := "Value %d" % int(expected_values[i]) if not disconnected else "Value 5"
            if slider.value != expected_values[i] or value_receipts != edge_receipts or label.text != edge_label:
                push_error("SLIDER focus-restore edge assertion failed: edge=%d action=%s %s" % [i, edges[i][0], "press" if edges[i][1] else "release"])
                quit(2)
                return
        if disconnected:
            print("SLIDER_REPEAT_FOCUS_RESTORE_DISCONNECTED values=%s receipts=%s label=%s" % [expected_values, value_receipts, label.text])
            push_error("SLIDER REPEAT FOCUS-RESTORE SIGNAL ASSERTION FAILED: expected receipts [6,5,4] and Labels [Value 6,Value 5,Value 4]")
            quit(2)
            return
        print("PASS slider_adjust_repeat_focus_restore focused=true range=0..10 step=1 values=6,6,6,5,5,4,4 receipts=6,5,4 Labels=Value 6,Value 5,Value 4")
        quit(0)
        return
    if OS.get_cmdline_user_args().has("--repeat-right") and OS.get_cmdline_user_args().has("--focus-handoff"):
        var other := Button.new()
        other.text = "Other"
        other.focus_mode = Control.FOCUS_ALL
        ui.add_child(other)
        var edges := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]
        for i in range(edges.size()):
            if i == 1:
                other.grab_focus()
                await process_frame
            var expected_owner: Control = slider if i == 0 else other
            if get_root().gui_get_focus_owner() != expected_owner or slider.has_focus() != (i == 0):
                push_error("SLIDER focus-handoff owner assertion failed before edge %d" % i)
                quit(2)
                return
            _action(edges[i][0], edges[i][1])
            await process_frame
            var expected_receipts: Array[float] = []
            if not disconnected:
                expected_receipts.append(6.0)
            var expected_label := "Value 6" if not disconnected else "Value 5"
            if slider.value != 6.0 or value_receipts != expected_receipts or label.text != expected_label:
                push_error("SLIDER focus-handoff edge assertion failed: edge=%d action=%s %s" % [i, edges[i][0], "press" if edges[i][1] else "release"])
                quit(2)
                return
        print("SLIDER_REPEAT_FOCUS_HANDOFF values=6,6,6,6,6,6,6 receipts=%s label=%s owner_other=%s" % [value_receipts, label.text, get_root().gui_get_focus_owner() == other])
        push_error("SLIDER REPEAT FOCUS-HANDOFF ASSERTION FAILED: expected post-handoff adjustment after seven checks")
        quit(2)
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
