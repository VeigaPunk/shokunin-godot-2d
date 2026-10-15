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
func _assert_state(tag: String, expected: int) -> bool:
    var owner := get_root().get_viewport().gui_get_focus_owner()
    print("STATE %s has_focus=%s owner_button=%s receipts=%d text=%s" % [tag, button.has_focus(), owner == button, receipts, label.text])
    if receipts != expected or label.text != ("Ready" if expected == 0 else "Activated %d" % expected):
        push_error("state assertion failed: " + tag)
        return false
    return true
func run() -> void:
    var drop_focus := "--drop-focus" in OS.get_cmdline_user_args()
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
    var owner := get_root().get_viewport().gui_get_focus_owner()
    if not button.has_focus() or owner != button:
        push_error("initial focus assertion failed")
        quit(2)
        return
    await _edge(true)
    await process_frame
    if not _assert_state("pair1-press", 0): quit(2); return
    await _edge(false)
    await process_frame
    if not _assert_state("pair1-release", 1): quit(2); return
    if drop_focus:
        button.release_focus()
        await process_frame
        owner = get_root().get_viewport().gui_get_focus_owner()
        print("AFTER_DROP has_focus=%s owner_null=%s" % [button.has_focus(), owner == null])
        if button.has_focus() or owner != null:
            push_error("focus release precondition failed")
            quit(2)
            return
    await _edge(true)
    await process_frame
    if drop_focus:
        if not _assert_state("pair2-press-after-focus-loss", 1): quit(2); return
    else:
        if not _assert_state("pair2-press-focused", 1): quit(2); return
    await _edge(false)
    await process_frame
    var expected := 1 if drop_focus else 2
    if not _assert_state("pair2-release", expected): quit(2); return
    quit(0)
