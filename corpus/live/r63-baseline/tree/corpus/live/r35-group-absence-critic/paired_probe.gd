extends SceneTree
var receipts: Array[String] = []
var label: Label
func _on_a_toggled(pressed: bool) -> void:
    receipts.append("A:%s" % pressed)
    if pressed: label.text = "A"
func _on_b_toggled(pressed: bool) -> void:
    receipts.append("B:%s" % pressed)
    if pressed: label.text = "B"
func _send_accept() -> void:
    var e := InputEventAction.new(); e.action = "ui_accept"; e.pressed = true; root.push_input(e); await process_frame
    e = InputEventAction.new(); e.action = "ui_accept"; e.pressed = false; root.push_input(e); await process_frame
func run() -> void:
    var grouped := "--ungroup-b" not in OS.get_cmdline_user_args()
    var group := ButtonGroup.new(); var a := Button.new(); var b := Button.new()
    a.toggle_mode = true; b.toggle_mode = true; a.button_group = group
    if grouped: b.button_group = group
    a.button_pressed = true; label = Label.new(); label.text = "A"
    var ui := CanvasLayer.new(); ui.add_child(a); ui.add_child(b); ui.add_child(label); root.add_child(ui)
    a.toggled.connect(_on_a_toggled); b.toggled.connect(_on_b_toggled)
    await process_frame
    print("setup A=",a.button_pressed," B=",b.button_pressed," receipts=",receipts," label=",label.text," group_alive=",is_instance_valid(group)," members=",group.get_buttons().size())
    b.grab_focus(); await process_frame; print("focusB=",get_root().get_viewport().gui_get_focus_owner()==b)
    await _send_accept(); print("after_B A=",a.button_pressed," B=",b.button_pressed," receipts=",receipts," label=",label.text)
    a.grab_focus(); await process_frame; print("focusA=",get_root().get_viewport().gui_get_focus_owner()==a)
    await _send_accept(); print("after_A A=",a.button_pressed," B=",b.button_pressed," receipts=",receipts," label=",label.text)
    quit()
func _initialize() -> void: call_deferred("run")
