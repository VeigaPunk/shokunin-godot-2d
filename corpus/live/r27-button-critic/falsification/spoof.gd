extends SceneTree

var pressed_receipts := 0
var label: Label

func _initialize() -> void:
    call_deferred("run")

func _on_button_pressed() -> void:
    pressed_receipts += 1
    label.text = "Activated"

func run() -> void:
    var disconnected := "--disconnect-signal" in OS.get_cmdline_user_args()
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
    _on_button_pressed() # deliberate direct-callback spoof
    button.grab_focus()
    var activation := InputEventAction.new()
    activation.action = "ui_accept"
    activation.pressed = true
    root.push_input(activation)
    var release := InputEventAction.new()
    release.action = "ui_accept"
    release.pressed = false
    root.push_input(release)
    await process_frame
    if label.text != "Activated" or pressed_receipts != 1:
        push_error("UI BUTTON ASSERTION FAILED: expected in-tree Label text=Activated after pressed signal; receipts=%d text=%s" % [pressed_receipts, label.text])
        quit(2)
        return
    print("PASS button_activation in_tree=true initial=Ready pressed_receipts=1 final=Activated")
    quit(0)
