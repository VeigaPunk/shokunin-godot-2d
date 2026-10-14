extends SceneTree
var receipts := 0
var label: Label
func _initialize() -> void:
    call_deferred("run")
func _on_pressed() -> void:
    receipts += 1
    label.text = "Activated %d" % receipts
func send_action(is_pressed: bool) -> void:
    var event := InputEventAction.new()
    event.action = "ui_accept"
    event.pressed = is_pressed
    root.push_input(event)
func run() -> void:
    var ui := CanvasLayer.new()
    var button := Button.new()
    label = Label.new()
    label.text = "Ready"
    ui.add_child(button)
    ui.add_child(label)
    root.add_child(ui)
    button.pressed.connect(_on_pressed)
    await process_frame
    button.grab_focus()
    send_action(true)
    await process_frame
    print("STEP1 pressed receipts=%d label=%s" % [receipts,label.text])
    send_action(false)
    await process_frame
    print("STEP1 release receipts=%d label=%s" % [receipts,label.text])
    await process_frame
    send_action(true)
    await process_frame
    print("STEP2 pressed receipts=%d label=%s" % [receipts,label.text])
    send_action(false)
    await process_frame
    print("STEP2 release receipts=%d label=%s" % [receipts,label.text])
    quit(0 if receipts == 2 and label.text == "Activated 2" else 2)
