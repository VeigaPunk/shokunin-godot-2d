extends SceneTree

var pressed_receipts := 0
var label: Label

func _initialize() -> void:
    call_deferred("run")

func _on_button_pressed() -> void:
    pressed_receipts += 1
    label.text = "Activated %d" % pressed_receipts

func _send_action(button: Button) -> void:
    button.grab_focus()
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
    var skip_second := "--skip-second" in OS.get_cmdline_user_args()
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
    await _send_action(button)
    await process_frame
    if label.text != "Activated 1" or pressed_receipts != 1:
        push_error("UI BUTTON ASSERTION FAILED: expected step1 text=Activated 1 receipts=1, got receipts=%d text=%s" % [pressed_receipts, label.text])
        quit(2)
        return
    # scratch mutation: second action omitted
    await process_frame
    if label.text != "Activated 2" or pressed_receipts != 2:
        push_error("UI BUTTON ASSERTION FAILED: expected step2 text=Activated 2 receipts=2, got receipts=%d text=%s" % [pressed_receipts, label.text])
        quit(2)
        return
    print("PASS button_activation in_tree=true initial=Ready step_texts=[Activated 1,Activated 2] receipts=[1,2]")
    quit(0)
