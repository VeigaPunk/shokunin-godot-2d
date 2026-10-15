extends SceneTree

var receipts: Array[bool] = []
var label: Label

func _initialize() -> void:
    call_deferred("run")

func _on_checkbox_toggled(checked: bool) -> void:
    receipts.append(checked)
    label.text = "On" if checked else "Off"

func _send_action_edge(pressed: bool) -> void:
    var activation := InputEventAction.new()
    activation.action = "ui_accept"
    activation.pressed = pressed
    root.push_input(activation)

func run() -> void:
    var disconnected := "--disconnect-signal" in OS.get_cmdline_user_args()
    var ui := CanvasLayer.new()
    var checkbox := CheckBox.new()
    checkbox.text = "Enabled"
    label = Label.new()
    label.text = "Ready"
    ui.add_child(checkbox)
    ui.add_child(label)
    root.add_child(ui)
    if not disconnected:
        checkbox.toggled.connect(_on_checkbox_toggled)
    await process_frame
    if not checkbox.is_inside_tree() or checkbox.button_pressed or label.text != "Ready":
        push_error("CHECKBOX setup assertion failed: expected in-tree unchecked CheckBox and Ready label")
        quit(2)
        return
    checkbox.grab_focus()
    await process_frame
    if not checkbox.has_focus() or get_root().get_viewport().gui_get_focus_owner() != checkbox:
        push_error("CHECKBOX setup assertion failed: expected CheckBox focus")
        quit(2)
        return
    for expected in [true, false]:
        await _send_action_edge(true)
        await process_frame
        await _send_action_edge(false)
        await process_frame
        if checkbox.button_pressed != expected:
            push_error("CHECKBOX state assertion failed: expected checked=%s got=%s" % [expected, checkbox.button_pressed])
            quit(2)
            return
        if disconnected:
            if receipts.size() != 0 or label.text != "Ready":
                push_error("CHECKBOX disconnected control assertion failed: expected no signal receipt and Ready label")
                quit(2)
                return
            if expected:
                print("CHECKBOX_DISCONNECTED state=true receipts=0 label=Ready")
                push_error("CHECKBOX SIGNAL ASSERTION FAILED: expected toggled receipt true")
                quit(2)
                return
        else:
            if receipts.size() != (1 if expected else 2) or receipts[-1] != expected or label.text != ("On" if expected else "Off"):
                push_error("CHECKBOX SIGNAL ASSERTION FAILED: expected toggled=%s receipts=%s label=%s" % [expected, receipts, label.text])
                quit(2)
                return
            print("CHECKBOX state=%s receipts=%s label=%s" % [checkbox.button_pressed, receipts, label.text])
    print("PASS checkbox_toggle states=[true,false] toggled=[true,false] labels=[On,Off]")
    quit(0)
