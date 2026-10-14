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
    var disconnected := "--disconnect-signal" in OS.get_cmdline_user_args()
    var ui := CanvasLayer.new()
    var box := CheckBox.new()
    label = Label.new()
    label.text = "Ready"
    ui.add_child(box)
    ui.add_child(label)
    root.add_child(ui)
    if not disconnected:
        box.toggled.connect(_on_toggled)
    await process_frame
    if not box.is_inside_tree() or box.button_pressed or label.text != "Ready":
        push_error("setup state mismatch"); quit(2); return
    box.grab_focus()
    await process_frame
    if not box.has_focus() or get_root().get_viewport().gui_get_focus_owner() != box:
        push_error("setup focus mismatch"); quit(2); return
    var prior := false
    for i in range(2):
        await _send(true)
        await process_frame
        if box.button_pressed != prior or receipts.size() != (0 if disconnected else i) or label.text != ("Ready" if disconnected else ("Ready" if i == 0 else "On")):
            push_error("press%d assertion failed checked=%s receipts=%s label=%s" % [i+1, box.button_pressed, receipts, label.text]); quit(2); return
        print("EDGE press%d checked=%s receipts=%s label=%s" % [i+1, box.button_pressed, receipts, label.text])
        var next := not prior
        await _send(false)
        await process_frame
        if box.button_pressed != next:
            push_error("release%d state assertion failed expected=%s got=%s" % [i+1,next,box.button_pressed]); quit(2); return
        if disconnected:
            if not receipts.is_empty() or label.text != "Ready":
                push_error("release%d disconnected assertion failed" % [i+1]); quit(2); return
        elif receipts.size() != i+1 or receipts[-1] != next or label.text != ("On" if next else "Off"):
            push_error("release%d signal assertion failed checked=%s receipts=%s label=%s" % [i+1,box.button_pressed,receipts,label.text]); quit(2); return
        print("EDGE release%d checked=%s receipts=%s label=%s" % [i+1,box.button_pressed,receipts,label.text])
        prior = next
    if disconnected:
        push_error("expected missing toggled signal receipt [true,false], got []"); quit(2); return
    print("PASS connected press-only/release-only checks")
    quit(0)
