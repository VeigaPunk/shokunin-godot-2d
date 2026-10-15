extends SceneTree
var receipts: Array[String] = []
var label: Label
func _initialize() -> void:
    call_deferred("run")
func _on_a(v: bool) -> void:
    receipts.append("A:%s" % v)
    label.text = "A" if v else "none"
func _on_b(v: bool) -> void:
    receipts.append("B:%s" % v)
    label.text = "B" if v else "none"
func edge(v: bool) -> void:
    var e := InputEventAction.new()
    e.action = "ui_accept"
    e.pressed = v
    root.push_input(e)
func run() -> void:
    var ui := CanvasLayer.new()
    var a := Button.new()
    var b := Button.new()
    var group := ButtonGroup.new()
    group.allow_unpress = false
    a.toggle_mode = true
    a.button_group = group
    b.toggle_mode = true
    b.button_group = group
    a.text = "A"
    b.text = "B"
    a.button_pressed = true
    label = Label.new()
    label.text = "Ready"
    ui.add_child(a)
    ui.add_child(b)
    ui.add_child(label)
    root.add_child(ui)
    a.toggled.connect(_on_a)
    b.toggled.connect(_on_b)
    await process_frame
    print("SETUP in_tree=%s/%s group_same=%s group=%s/%s pressed=%s/%s focus=%s" % [a.is_inside_tree(), b.is_inside_tree(), a.button_group == b.button_group, a.button_group, b.button_group, a.button_pressed, b.button_pressed, get_root().get_viewport().gui_get_focus_owner()])
    b.grab_focus()
    await process_frame
    print("FOCUS B has=%s owner=%s" % [b.has_focus(), get_root().get_viewport().gui_get_focus_owner()])
    await edge(true); await process_frame
    await edge(false); await process_frame
    print("B_ACTION %s/%s cb=%s label=%s" % [a.button_pressed,b.button_pressed,receipts,label.text])
    await edge(false); await process_frame
    b.release_focus(); a.grab_focus(); await process_frame
    print("FOCUS A has=%s owner=%s" % [a.has_focus(), get_root().get_viewport().gui_get_focus_owner()])
    await edge(true); await process_frame
    await edge(false); await process_frame
    print("A_ACTION %s/%s cb=%s label=%s" % [a.button_pressed,b.button_pressed,receipts,label.text])
    quit(0)
