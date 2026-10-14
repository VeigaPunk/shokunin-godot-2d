extends SceneTree

var pressed_receipts := 0
var label: Label

func _initialize() -> void:
    call_deferred("run")

func _on_button_pressed() -> void:
    pressed_receipts += 1
    label.text = "Activated %d" % pressed_receipts

func _send_action(button: Button, no_focus: bool) -> void:
    var activation := InputEventAction.new()
    activation.action = "ui_accept"
    activation.pressed = true
    root.push_input(activation)
    var release := InputEventAction.new()
    release.action = "ui_accept"
    release.pressed = false
    root.push_input(release)

func run() -> void:
    var args := OS.get_cmdline_user_args()
    var disconnected := "--disconnect-signal" in args
    var no_focus := "--no-focus" in args
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
    await _send_action(button, no_focus)
    await process_frame
    var owner_after_step1 := get_root().get_viewport().gui_get_focus_owner() == button
    print("BUTTON_FOCUS step=1 focused=%s button_has_focus=%s receipts=%d text=%s" % [owner_after_step1, button.has_focus(), pressed_receipts, label.text])
    if label.text != "Activated 1" or pressed_receipts != 1:
        push_error("UI BUTTON ASSERTION FAILED: expected step1 text=Activated 1 receipts=1, got receipts=%d text=%s" % [pressed_receipts, label.text])
        quit(2)
        return
    await _send_action(button, no_focus)
    await process_frame
    var owner_after_step2 := get_root().get_viewport().gui_get_focus_owner() == button
    print("BUTTON_FOCUS step=2 focused=%s button_has_focus=%s receipts=%d text=%s" % [owner_after_step2, button.has_focus(), pressed_receipts, label.text])
    if label.text != "Activated 2" or pressed_receipts != 2:
        push_error("UI BUTTON ASSERTION FAILED: expected step2 text=Activated 2 receipts=2, got receipts=%d text=%s" % [pressed_receipts, label.text])
        quit(2)
        return
    print("PASS button_activation in_tree=true initial=Ready step_texts=[Activated 1,Activated 2] receipts=[1,2]")
    quit(0)
