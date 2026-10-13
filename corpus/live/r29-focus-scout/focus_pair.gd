extends SceneTree
var receipts := 0
var label: Label
func _initialize() -> void:
    call_deferred("run")
func _pressed() -> void:
    receipts += 1
    label.text = "Activated %d" % receipts
func _action() -> void:
    var down := InputEventAction.new()
    down.action = "ui_accept"
    down.pressed = true
    root.push_input(down)
    var up := InputEventAction.new()
    up.action = "ui_accept"
    up.pressed = false
    root.push_input(up)
func run() -> void:
    var ui := CanvasLayer.new()
    var button := Button.new()
    label = Label.new()
    label.text = "Ready"
    ui.add_child(button)
    ui.add_child(label)
    root.add_child(ui)
    button.pressed.connect(_pressed)
    await process_frame
    button.grab_focus()
    await process_frame
    var focused_owner = get_root().gui_get_focus_owner()
    var before_focused = {"owner": focused_owner.name if focused_owner else "<none>", "has_focus": button.has_focus()}
    await _action()
    await process_frame
    var focus_receipts = receipts
    var focus_text = label.text
    button.release_focus()
    await process_frame
    var unfocused_owner = get_root().gui_get_focus_owner()
    var before_unfocused = {"owner": unfocused_owner.name if unfocused_owner else "<none>", "has_focus": button.has_focus()}
    await _action()
    await process_frame
    print("PAIR focused=%s focus_receipts=%d focus_text=%s unfocused=%s final_receipts=%d final_text=%s" % [JSON.stringify(before_focused), focus_receipts, focus_text, JSON.stringify(before_unfocused), receipts, label.text])
    quit(0)
