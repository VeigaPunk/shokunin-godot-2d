extends SceneTree
var receipts := []
func _on(name: String) -> void:
    receipts.append(name)
func send_action() -> void:
    var e := InputEventAction.new(); e.action = "ui_accept"; e.pressed = true; root.push_input(e)
    var r := InputEventAction.new(); r.action = "ui_accept"; r.pressed = false; root.push_input(r)
func _initialize() -> void:
    call_deferred("run")
func run() -> void:
    var ui := CanvasLayer.new()
    var a := Button.new(); a.name = "target"; a.text = "target"
    var b := Button.new(); b.name = "other"; b.text = "other"
    ui.add_child(a); ui.add_child(b); root.add_child(ui)
    a.pressed.connect(_on.bind("target")); b.pressed.connect(_on.bind("other"))
    await process_frame
    a.grab_focus(); await process_frame
    print("FOCUSED owner=", get_viewport().gui_get_focus_owner().name)
    send_action(); await process_frame
    print("FOCUSED receipts=", receipts)
    receipts.clear(); b.grab_focus(); await process_frame
    print("OTHER owner=", get_viewport().gui_get_focus_owner().name)
    send_action(); await process_frame
    print("OTHER receipts=", receipts)
    receipts.clear(); a.release_focus(); b.release_focus(); await process_frame
    var owner = get_viewport().gui_get_focus_owner()
    print("NONE owner=", owner.name if owner else "null")
    send_action(); await process_frame
    print("NONE receipts=", receipts)
    receipts.clear(); a.pressed.emit(); await process_frame
    print("MANUAL pressed.emit receipts=", receipts)
    quit()
