extends SceneTree

var pressed_receipts := 0
var label: Label

func _initialize() -> void:
    call_deferred("run")

func _on_button_pressed() -> void:
    pressed_receipts += 1
    label.text = "Activated %d" % pressed_receipts

func _send_action(button: Button) -> void:
    var activation := InputEventAction.new()
    activation.action = "ui_accept"
    activation.pressed = true
    root.push_input(activation)
    var release := InputEventAction.new()
    release.action = "ui_accept"
    release.pressed = false
    root.push_input(release)

func run() -> void:
    var disconnected := "--disconnect-signal" in OS.get_cmdline_user_args()
    var no_focus := "--no-focus" in OS.get_cmdline_user_args()
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
    if not no_focus:
        button.grab_focus()
    await process_frame
    var focus_before: bool = button.has_focus() and get_root().gui_get_focus_owner() == button
    if (not no_focus and not focus_before) or (no_focus and (button.has_focus() or get_root().gui_get_focus_owner() == button)):
        push_error("FOCUS setup assertion failed: no_focus=%s has_focus=%s owner_is_button=%s" % [no_focus, button.has_focus(), get_root().gui_get_focus_owner() == button])
        quit(2)
        return
    if not button.is_inside_tree() or not label.is_inside_tree() or label.text != "Ready":
        push_error("UI BUTTON setup assertion failed: expected in-tree Button and Label text=Ready")
        quit(2)
        return
    await _send_action(button)
    await process_frame
    print("RECEIPT step=1 count=%d text=%s focus=%s owner_is_button=%s owner=%s" % [pressed_receipts, label.text, button.has_focus(), get_root().gui_get_focus_owner() == button, str(get_root().gui_get_focus_owner())])
    if label.text != "Activated 1" or pressed_receipts != 1:
        push_error("UI BUTTON ASSERTION FAILED: expected step1 text=Activated 1 receipts=1, got receipts=%d text=%s" % [pressed_receipts, label.text])
        quit(2)
        return
    await _send_action(button)
    await process_frame
    print("RECEIPT step=2 count=%d text=%s focus=%s owner_is_button=%s owner=%s" % [pressed_receipts, label.text, button.has_focus(), get_root().gui_get_focus_owner() == button, str(get_root().gui_get_focus_owner())])
    if label.text != "Activated 2" or pressed_receipts != 2:
        push_error("UI BUTTON ASSERTION FAILED: expected step2 text=Activated 2 receipts=2, got receipts=%d text=%s" % [pressed_receipts, label.text])
        quit(2)
        return
    print("PASS button_activation mode=%s focus=%s owner_is_button=%s step_texts=[Activated 1,Activated 2] receipts=[1,2]" % ["no_focus" if no_focus else "focused", button.has_focus(), get_root().gui_get_focus_owner() == button])
    quit(0)
