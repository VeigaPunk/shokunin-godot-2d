extends SceneTree
var n := 0
var label: Label
func _initialize() -> void: call_deferred("run")
func on_pressed() -> void:
    n += 1
    label.text = "Activated %d" % n
func action(down: bool) -> void:
    var e := InputEventAction.new()
    e.action = "ui_accept"
    e.pressed = down
    root.push_input(e)
func run() -> void:
    var ui := CanvasLayer.new()
    var b := Button.new()
    label = Label.new()
    label.text = "Ready"
    ui.add_child(b)
    ui.add_child(label)
    root.add_child(ui)
    b.pressed.connect(on_pressed)
    await process_frame
    b.grab_focus()
    action(true)
    await process_frame
    print("after press n=%d text=%s" % [n,label.text])
    action(false)
    await process_frame
    print("after release n=%d text=%s" % [n,label.text])
    action(false)
    await process_frame
    print("after duplicate release n=%d text=%s" % [n,label.text])
    quit(0)
