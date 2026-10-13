extends SceneTree

var pressed_receipts := 0
var label: Label

func _initialize() -> void:
    call_deferred("run")

func _on_button_pressed() -> void:
    pressed_receipts += 1
    label.text = "Activated %d" % pressed_receipts

func _send_action_edge(pressed: bool) -> void:
    var activation := InputEventAction.new()
    activation.action = "ui_accept"
    activation.pressed = pressed
    root.push_input(activation)

func run() -> void:
    var args := OS.get_cmdline_user_args()
    var disconnected := "--disconnect-signal" in args
    var no_focus := "--no-focus" in args
    var lose_focus := "--lose-focus-after-first" in args
    var ui := CanvasLayer.new()
    var button := Button.new()
    button.name = "ActivateButton"
    button.text = "Activate"
    label = Label.new()
    label.name = "StatusLabel"
    label.text = "Ready"
    ui.add_child(button)
    ui.add_child(label)
    root.add_child(ui)
    if not disconnected:
        button.pressed.connect(_on_button_pressed)
    await process_frame
    if not button.is_inside_tree() or not label.is_inside_tree() or label.text != "Ready":
        push_error("UI BUTTON setup assertion failed: expected in-tree Button and Label text=Ready")
        quit(2)
        return
    if no_focus:
        button.release_focus()
        await process_frame
        var focus_owner := get_root().get_viewport().gui_get_focus_owner()
        if button.has_focus() or focus_owner != null:
            push_error("UI BUTTON no-focus setup assertion failed: expected no focused Button and no focus owner")
            quit(2)
            return
    else:
        button.grab_focus()
        await process_frame
        var focus_owner := get_root().get_viewport().gui_get_focus_owner()
        if not button.has_focus() or focus_owner != button:
            push_error("UI BUTTON focused setup assertion failed: expected ActivateButton to own focus")
            quit(2)
            return
    await _send_action_edge(true)
    await process_frame
    if label.text != "Ready" or pressed_receipts != 0:
        push_error("UI BUTTON ASSERTION FAILED: expected press1 text=Ready receipts=0, got receipts=%d text=%s" % [pressed_receipts, label.text])
        quit(2)
        return
    await _send_action_edge(false)
    await process_frame
    var owner_after_release1 := get_root().get_viewport().gui_get_focus_owner() == button
    print("BUTTON_FOCUS edge=release1 focused=%s button_has_focus=%s receipts=%d text=%s" % [owner_after_release1, button.has_focus(), pressed_receipts, label.text])
    if label.text != "Activated 1" or pressed_receipts != 1 or (not no_focus and not disconnected and not owner_after_release1):
        push_error("UI BUTTON ASSERTION FAILED: expected release1 text=Activated 1 receipts=1, got focused=%s receipts=%d text=%s" % [owner_after_release1, pressed_receipts, label.text])
        quit(2)
        return
    if lose_focus:
        button.release_focus()
        await process_frame
        var lost_owner := get_root().get_viewport().gui_get_focus_owner()
        print("BUTTON_FOCUS mid_sequence focused=%s button_has_focus=%s" % [lost_owner == button, button.has_focus()])
        if button.has_focus() or lost_owner != null:
            push_error("UI BUTTON mid-sequence focus loss setup assertion failed")
            quit(2)
            return
    await _send_action_edge(true)
    await process_frame
    if lose_focus:
        var owner_after_press2 := get_root().get_viewport().gui_get_focus_owner()
        if button.has_focus() or owner_after_press2 != null:
            push_error("UI BUTTON mid-sequence press2 focus assertion failed: expected no focus owner")
            quit(2)
            return
    if label.text != "Activated 1" or pressed_receipts != 1:
        push_error("UI BUTTON ASSERTION FAILED: expected press2 text=Activated 1 receipts=1, got receipts=%d text=%s" % [pressed_receipts, label.text])
        quit(2)
        return
    await _send_action_edge(false)
    await process_frame
    var owner_after_step2 := get_root().get_viewport().gui_get_focus_owner() == button
    print("BUTTON_FOCUS step=2 focused=%s button_has_focus=%s receipts=%d text=%s" % [owner_after_step2, button.has_focus(), pressed_receipts, label.text])
    if lose_focus and (button.has_focus() or get_root().get_viewport().gui_get_focus_owner() != null):
        push_error("UI BUTTON mid-sequence release2 focus assertion failed: expected no focus owner")
        quit(2)
        return
    if lose_focus:
        if label.text != "Activated 1" or pressed_receipts != 1:
            push_error("UI BUTTON ASSERTION FAILED: expected lost-focus release2 text=Activated 1 receipts=1, got receipts=%d text=%s" % [pressed_receipts, label.text])
            quit(2)
            return
    elif label.text != "Activated 2" or pressed_receipts != 2:
        push_error("UI BUTTON ASSERTION FAILED: expected release2 text=Activated 2 receipts=2, got receipts=%d text=%s" % [pressed_receipts, label.text])
        quit(2)
        return
    if lose_focus:
        print("PASS button_activation_focus_loss initial=focused release1=Activated1 mid_sequence=no_focus release2=Activated1 receipts=1")
    else:
        print("PASS button_activation in_tree=true initial=Ready edge_texts=[Ready,Activated 1,Activated 1,Activated 2] receipts=[0,1,1,2]")
    quit(0)
