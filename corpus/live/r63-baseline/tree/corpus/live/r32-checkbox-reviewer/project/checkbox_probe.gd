extends SceneTree
var receipts: Array = []
var label: Label
func _initialize() -> void:
    call_deferred("run")
func _on_toggled(value: bool) -> void:
    receipts.append(value)
    label.text = "On" if value else "Off"
func edge(pressed: bool) -> void:
    var e := InputEventAction.new()
    e.action = "ui_accept"
    e.pressed = pressed
    root.push_input(e)
func run() -> void:
    var disconnect_signal := "--disconnected" in OS.get_cmdline_user_args()
    var ui := CanvasLayer.new()
    var box := CheckBox.new()
    box.text = "Toggle"
    label = Label.new()
    label.text = "Ready"
    ui.add_child(box)
    ui.add_child(label)
    root.add_child(ui)
    if not disconnect_signal:
        box.toggled.connect(_on_toggled)
    await process_frame
    box.grab_focus()
    await process_frame
    print("SETUP focus=%s owner=%s checked=%s label=%s receipts=%s" % [box.has_focus(), get_root().get_viewport().gui_get_focus_owner() == box, box.button_pressed, label.text, receipts])
    for i in range(2):
        await edge(true)
        await process_frame
        print("EDGE%d_PRESS checked=%s label=%s receipts=%s" % [i+1, box.button_pressed, label.text, receipts])
        await edge(false)
        await process_frame
        print("EDGE%d_RELEASE checked=%s label=%s receipts=%s" % [i+1, box.button_pressed, label.text, receipts])
    print("FINAL disconnected=%s checked=%s label=%s receipts=%s" % [disconnect_signal, box.button_pressed, label.text, receipts])
    quit()
