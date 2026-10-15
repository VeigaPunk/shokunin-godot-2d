extends SceneTree

func send_action() -> void:
    var activation := InputEventAction.new()
    activation.action = "ui_accept"
    activation.pressed = true
    root.push_input(activation)
    var release := InputEventAction.new()
    release.action = "ui_accept"
    release.pressed = false
    root.push_input(release)

func run() -> void:
    var ui := CanvasLayer.new()
    var focused := Button.new()
    focused.name = "FocusedButton"
    var unfocused := Button.new()
    unfocused.name = "UnfocusedButton"
    var label := Label.new()
    label.text = "Ready"
    ui.add_child(focused)
    ui.add_child(unfocused)
    ui.add_child(label)
    root.add_child(ui)
    await process_frame
    focused.grab_focus()
    await process_frame
    var owner_focused := get_root().get_viewport().gui_get_focus_owner() == focused
    var focused_before := focused.has_focus()
    var focused_receipts := [0]
    focused.pressed.connect(func(): focused_receipts[0] += 1)
    await send_action()
    await process_frame
    var focused_after := focused.has_focus()
    var focused_after_owner := get_root().get_viewport().gui_get_focus_owner() == focused
    var focused_first: int = focused_receipts[0]
    await send_action()
    await process_frame
    var focused_count: int = focused_receipts[0]
    focused.release_focus()
    await process_frame
    var owner_none := get_root().get_viewport().gui_get_focus_owner() == null
    var unfocused_before := unfocused.has_focus()
    var unfocused_receipts := [0]
    unfocused.pressed.connect(func(): unfocused_receipts[0] += 1)
    await send_action()
    await process_frame
    var unfocused_after := unfocused.has_focus()
    var unfocused_after_owner := get_root().get_viewport().gui_get_focus_owner() == unfocused
    var unfocused_first: int = unfocused_receipts[0]
    await send_action()
    await process_frame
    var unfocused_count: int = unfocused_receipts[0]
    print("R29_PAIR owner_focused=%s focused_before=%s focused_after=%s focused_after_owner=%s focused_first=%d focused_receipts=%d owner_none_before_unfocused=%s unfocused_before=%s unfocused_after=%s unfocused_after_owner=%s unfocused_first=%d unfocused_receipts=%d" % [owner_focused, focused_before, focused_after, focused_after_owner, focused_first, focused_count, owner_none, unfocused_before, unfocused_after, unfocused_after_owner, unfocused_first, unfocused_count])
    quit(0)

func _initialize() -> void:
    call_deferred("run")
