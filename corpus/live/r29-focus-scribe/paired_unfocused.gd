extends SceneTree
var receipts := 0
var label: Label
func _initialize(): call_deferred("run")
func _pressed():
    receipts += 1
    label.text = "Activated %d" % receipts
func run():
    var ui := CanvasLayer.new()
    var b := Button.new()
    b.name = "ActivateButton"
    var focus_mode := true
    label = Label.new()
    label.text = "Ready"
    ui.add_child(b); ui.add_child(label); root.add_child(ui)
    b.pressed.connect(_pressed)
    await process_frame
    if not focus_mode: b.grab_focus()
    var owner_before := get_root().gui_get_focus_owner()
    print("BEFORE mode=%s owner=%s is_focused=%s" % ["unfocused" if focus_mode else "focused", owner_before, b.has_focus()])
    for i in range(2):
        for pressed in [true, false]:
            var e := InputEventAction.new(); e.action = "ui_accept"; e.pressed = pressed; root.push_input(e)
        await process_frame
        print("STEP mode=%s step=%d receipts=%d label=%s focused=%s" % ["unfocused" if focus_mode else "focused", i+1, receipts, label.text, b.has_focus()])
    quit(0)
