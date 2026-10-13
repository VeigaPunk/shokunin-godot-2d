extends SceneTree
var receipts: Array[String] = []
var label: Label
func _initialize() -> void:
    call_deferred("run")
func _on_a(value: bool) -> void:
    receipts.append("A:%s" % value)
    if value: label.text = "A"
func _on_b(value: bool) -> void:
    receipts.append("B:%s" % value)
    if value: label.text = "B"
func edge(pressed: bool) -> void:
    var e := InputEventAction.new()
    e.action = "ui_accept"
    e.pressed = pressed
    root.push_input(e)
func run() -> void:
    var disconnected := "--disconnect" in OS.get_cmdline_user_args()
    var ui := CanvasLayer.new()
    var group := ButtonGroup.new()
    var a := Button.new()
    var b := Button.new()
    label = Label.new()
    a.text = "A"
    b.text = "B"
    a.toggle_mode = true
    a.button_group = group
    b.toggle_mode = true
    b.button_group = group
    a.button_pressed = true
    label.text = "Ready"
    ui.add_child(a)
    ui.add_child(b)
    ui.add_child(label)
    root.add_child(ui)
    if not disconnected:
        a.toggled.connect(_on_a)
        b.toggled.connect(_on_b)
    await process_frame
    print("SETUP A=%s B=%s receipts=%s label=%s" % [a.button_pressed,b.button_pressed,receipts,label.text])
    b.grab_focus()
    await process_frame
    for target in [b, a]:
        target.grab_focus()
        await process_frame
        edge(true)
        await process_frame
        print("PRESS target=%s A=%s B=%s receipts=%s label=%s" % [target.text,a.button_pressed,b.button_pressed,receipts,label.text])
        edge(false)
        await process_frame
        print("RELEASE target=%s A=%s B=%s receipts=%s label=%s" % [target.text,a.button_pressed,b.button_pressed,receipts,label.text])
    quit(0)
