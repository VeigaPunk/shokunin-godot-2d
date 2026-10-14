extends SceneTree

var receipts: Array[String] = []
var label: Label

func _initialize() -> void:
    call_deferred("run")

func _on_a_toggled(pressed: bool) -> void:
    receipts.append("A:%s" % pressed)
    if pressed:
        label.text = "A"

func _on_b_toggled(pressed: bool) -> void:
    receipts.append("B:%s" % pressed)
    if pressed:
        label.text = "B"

func _send_accept() -> void:
    var activation := InputEventAction.new()
    activation.action = "ui_accept"
    activation.pressed = true
    root.push_input(activation)
    await process_frame
    activation = InputEventAction.new()
    activation.action = "ui_accept"
    activation.pressed = false
    root.push_input(activation)
    await process_frame

func run() -> void:
    var disconnected := "--disconnect-signal" in OS.get_cmdline_user_args()
    var ui := CanvasLayer.new()
    var group := ButtonGroup.new()
    var a := Button.new()
    var b := Button.new()
    a.text = "A"
    a.toggle_mode = true
    b.text = "B"
    b.toggle_mode = true
    a.button_group = group
    b.button_group = group
    a.button_pressed = true
    label = Label.new()
    label.text = "A"
    ui.add_child(a)
    ui.add_child(b)
    ui.add_child(label)
    root.add_child(ui)
    if not disconnected:
        a.toggled.connect(_on_a_toggled)
        b.toggled.connect(_on_b_toggled)
    await process_frame
    if not a.is_inside_tree() or not b.is_inside_tree() or not a.button_pressed or b.button_pressed or label.text != "A":
        push_error("BUTTON_GROUP setup assertion failed: expected A selected, B unselected, Label A")
        quit(2)
        return
    b.grab_focus()
    await process_frame
    if not b.has_focus() or get_root().get_viewport().gui_get_focus_owner() != b:
        push_error("BUTTON_GROUP setup assertion failed: expected Button B focus")
        quit(2)
        return
    await _send_accept()
    if a.button_pressed or not b.button_pressed:
        push_error("BUTTON_GROUP selection assertion failed after B: expected A=false B=true")
        quit(2)
        return
    if disconnected:
        if receipts.size() != 0 or label.text != "A":
            push_error("BUTTON_GROUP disconnected assertion failed after B: expected receipts=[] Label A")
            quit(2)
            return
    else:
        if receipts != ["A:false", "B:true"] or label.text != "B":
            push_error("BUTTON_GROUP SIGNAL ASSERTION FAILED after B: expected [A:false,B:true] Label B got %s Label %s" % [receipts, label.text])
            quit(2)
            return
    print("BUTTON_GROUP after_B A=%s B=%s receipts=%s label=%s" % [a.button_pressed, b.button_pressed, receipts, label.text])
    a.grab_focus()
    await process_frame
    if not a.has_focus() or get_root().get_viewport().gui_get_focus_owner() != a:
        push_error("BUTTON_GROUP setup assertion failed: expected Button A focus")
        quit(2)
        return
    await _send_accept()
    if not a.button_pressed or b.button_pressed:
        push_error("BUTTON_GROUP selection assertion failed after A: expected A=true B=false")
        quit(2)
        return
    if disconnected:
        if receipts.size() != 0 or label.text != "A":
            push_error("BUTTON_GROUP disconnected assertion failed after A: expected receipts=[] Label A")
            quit(2)
            return
        print("BUTTON_GROUP_DISCONNECTED after_A A=true B=false receipts=[] label=A")
        push_error("BUTTON_GROUP SIGNAL ASSERTION FAILED: expected transitions [A:false,B:true,B:false,A:true], got []")
        quit(2)
        return
    if receipts != ["A:false", "B:true", "B:false", "A:true"] or label.text != "A":
        push_error("BUTTON_GROUP SIGNAL ASSERTION FAILED after A: expected [A:false,B:true,B:false,A:true] Label A got %s Label %s" % [receipts, label.text])
        quit(2)
        return
    print("BUTTON_GROUP after_A A=true B=false receipts=%s label=%s" % [receipts, label.text])
    print("PASS button_group_selection exclusive=true toggled=[A:false,B:true,B:false,A:true] labels=[B,A]")
    quit(0)
