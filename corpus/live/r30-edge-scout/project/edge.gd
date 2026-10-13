extends SceneTree
var receipts := 0
var label: Label
var button: Button
func _initialize() -> void:
    call_deferred("run")
func _pressed() -> void:
    receipts += 1
    label.text = "Activated %d" % receipts
func _edge(pressed: bool) -> void:
    var event := InputEventAction.new()
    event.action = "ui_accept"
    event.pressed = pressed
    root.push_input(event)
func _state(tag: String) -> void:
    var owner := get_root().get_viewport().gui_get_focus_owner()
    print("EDGE %s focused=%s owner_button=%s receipts=%d text=%s" % [tag, button.has_focus(), owner == button, receipts, label.text])
func run() -> void:
    var ui := CanvasLayer.new()
    button = Button.new()
    button.name = "ActivateButton"
    button.text = "Activate"
    label = Label.new()
    label.text = "Ready"
    ui.add_child(button)
    ui.add_child(label)
    root.add_child(ui)
    button.pressed.connect(_pressed)
    await process_frame
    button.grab_focus()
    await process_frame
    _state("setup")
    for i in range(1, 3):
        await _edge(true)
        await process_frame
        _state("%d-press-only" % i)
        await _edge(false)
        await process_frame
        _state("%d-after-release" % i)
    quit(0)
