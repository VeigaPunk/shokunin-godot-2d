extends SceneTree
var receipts := 0
var label: Label
func _initialize() -> void:
    call_deferred("run")
func _on_pressed() -> void:
    receipts += 1
    label.text = "Activated %d" % receipts
func send_edge(down: bool) -> void:
    var ev := InputEventAction.new()
    ev.action = "ui_accept"
    ev.pressed = down
    root.push_input(ev)
func state(tag: String, expected: int, text: String) -> bool:
    var owner := get_root().get_viewport().gui_get_focus_owner()
    print("EDGE %s focus=%s has_focus=%s receipts=%d text=%s" % [tag, str(owner), str(owner != null and owner.name == "B"), receipts, label.text])
    return owner != null and owner.name == "B" and receipts == expected and label.text == text
func run() -> void:
    var ui := CanvasLayer.new()
    var b := Button.new()
    b.name = "B"
    label = Label.new()
    label.text = "Ready"
    ui.add_child(b)
    ui.add_child(label)
    root.add_child(ui)
    b.pressed.connect(_on_pressed)
    await process_frame
    b.grab_focus()
    await process_frame
    if not state("setup", 0, "Ready"):
        push_error("setup invalid")
        quit(2); return
    for i in range(2):
        send_edge(true)
        await process_frame
        var before := receipts
        print("PRESS_ONLY index=%d receipts_before=%d receipts_after=%d text=%s" % [i+1, before, receipts, label.text])
        if receipts != i or label.text != ("Ready" if i == 0 else "Activated 1"):
            push_error("unexpected press edge")
            quit(2); return
        send_edge(false)
        await process_frame
        if not state("release_%d" % (i+1), i+1, "Activated %d" % (i+1)):
            push_error("release assertion failed")
            quit(2); return
    print("PASS edge split")
    quit(0)
