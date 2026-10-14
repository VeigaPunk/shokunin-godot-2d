extends SceneTree

var receipts: Array[bool] = []
var label: Label

func _initialize() -> void:
    call_deferred("run")

func _on_toggled(value: bool) -> void:
    receipts.append(value)
    label.text = "On" if value else "Off"

func _send(pressed: bool) -> void:
    var event := InputEventAction.new()
    event.action = "ui_accept"
    event.pressed = pressed
    root.push_input(event)

func run() -> void:
    var disconnected := "--disconnect" in OS.get_cmdline_user_args()
    var ui := CanvasLayer.new()
    var checkbox := CheckBox.new()
    checkbox.name = "StateBox"
    checkbox.text = "Enable"
    var lbl := Label.new()
    lbl.name = "Status"
    lbl.text = "Off"
    label = lbl
    ui.add_child(checkbox)
    ui.add_child(lbl)
    root.add_child(ui)
    if not disconnected:
        checkbox.toggled.connect(_on_toggled)
    await process_frame
    if not checkbox.is_inside_tree() or not lbl.is_inside_tree() or checkbox.button_pressed or lbl.text != "Off":
        push_error("CHECKBOX setup assertion failed: expected in-tree unchecked CheckBox and Label Off")
        quit(2)
        return
    checkbox.grab_focus()
    await process_frame
    if not checkbox.has_focus() or get_root().get_viewport().gui_get_focus_owner() != checkbox:
        push_error("CHECKBOX focus assertion failed")
        quit(2)
        return
    var states: Array[bool] = []
    var label_states: Array[String] = []
    for i in range(2):
        await _send(true)
        await process_frame
        var pressed_state := checkbox.button_pressed
        var expected_receipts: Array = [] if disconnected else ([true] if i == 1 else [])
        print("CHECKBOX edge=press%d checked=%s receipts=%s label=%s" % [i + 1, checkbox.button_pressed, receipts, label.text])
        await _send(false)
        await process_frame
        states.append(checkbox.button_pressed)
        label_states.append(label.text)
        print("CHECKBOX edge=release%d focused=%s checked=%s receipts=%s label=%s" % [i + 1, checkbox.has_focus(), checkbox.button_pressed, receipts, label.text])
    if disconnected:
        if states != [true, false] or not receipts.is_empty() or lbl.text != "Off":
            push_error("CHECKBOX disconnected-control assertion failed: expected toggled state without signal receipts or Label update")
            quit(2)
            return
        print("PASS checkbox_disconnected states=[true,false] receipts=[] labels=[Off,Off]")
    else:
        if states != [true, false] or receipts != [true, false] or lbl.text != "Off":
            push_error("CHECKBOX ASSERTION FAILED: expected states=[true,false] toggled=[true,false] Label final=Off; got states=%s receipts=%s label=%s" % [states, receipts, lbl.text])
            quit(2)
            return
        print("PASS checkbox_toggle initial=false focus=true states=[true,false] toggled=[true,false] labels=[On,Off]")
    quit(0)
