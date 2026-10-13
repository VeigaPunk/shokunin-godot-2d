extends SceneTree
var label: Label
var receipts := 0
func _initialize() -> void:
    var root_control := Control.new()
    var button := Button.new()
    button.text = "Activate"
    label = Label.new()
    label.text = "Idle"
    root_control.add_child(button)
    root_control.add_child(label)
    root.add_child(root_control)
    button.pressed.connect(_on_pressed)
    await process_frame
    print("setup tree=%s button=%s label=%s text=%s" % [root_control.is_inside_tree(), button.is_inside_tree(), label.is_inside_tree(), label.text])
    button.button_pressed = true
    await process_frame
    print("after button_pressed setter receipts=%d text=%s" % [receipts, label.text])
    button.call("_pressed")
    print("after emit_signal receipts=%d text=%s" % [receipts, label.text])
    quit()
func _on_pressed() -> void:
    receipts += 1
    label.text = "Activated"
