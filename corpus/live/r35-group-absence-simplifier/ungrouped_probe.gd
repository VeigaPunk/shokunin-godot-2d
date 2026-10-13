extends SceneTree
var receipts: Array[String] = []
var label: Label
func _initialize() -> void:
    call_deferred("run")
func _on_a_toggled(pressed: bool) -> void:
    receipts.append("A:%s" % pressed)
    if pressed: label.text = "A"
func _on_b_toggled(pressed: bool) -> void:
    receipts.append("B:%s" % pressed)
    if pressed: label.text = "B"
func _send_accept() -> void:
    var activation := InputEventAction.new(); activation.action = "ui_accept"; activation.pressed = true
    root.push_input(activation); await process_frame
    activation = InputEventAction.new(); activation.action = "ui_accept"; activation.pressed = false
    root.push_input(activation); await process_frame
func run() -> void:
    var ui := CanvasLayer.new(); var group := ButtonGroup.new(); var a := Button.new(); var b := Button.new()
    a.text = "A"; a.toggle_mode = true; b.text = "B"; b.toggle_mode = true
    a.button_group = group; a.button_pressed = true
    label = Label.new(); label.text = "A"; ui.add_child(a); ui.add_child(b); ui.add_child(label); root.add_child(ui)
    a.toggled.connect(_on_a_toggled); b.toggled.connect(_on_b_toggled)
    await process_frame
    print("setup A=%s B=%s receipts=%s label=%s" % [a.button_pressed,b.button_pressed,receipts,label.text])
    b.grab_focus(); await process_frame; await _send_accept()
    print("after_B A=%s B=%s receipts=%s label=%s" % [a.button_pressed,b.button_pressed,receipts,label.text])
    a.grab_focus(); await process_frame; await _send_accept()
    print("after_A A=%s B=%s receipts=%s label=%s" % [a.button_pressed,b.button_pressed,receipts,label.text])
    quit()
