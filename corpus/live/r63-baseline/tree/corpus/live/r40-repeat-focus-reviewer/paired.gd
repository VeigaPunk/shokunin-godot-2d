extends SceneTree
var slider: HSlider
var label: Label
var receipts: Array[float] = []
var no_focus := OS.get_cmdline_user_args().has("--no-focus")
func _initialize() -> void:
    var ui := CanvasLayer.new()
    slider = HSlider.new()
    slider.min_value = 0.0
    slider.max_value = 10.0
    slider.step = 1.0
    slider.value = 5.0
    slider.focus_mode = Control.FOCUS_ALL
    label = Label.new()
    label.text = "Value 5"
    ui.add_child(slider)
    ui.add_child(label)
    root.add_child(ui)
    slider.value_changed.connect(_on_value_changed)
    await process_frame
    if not no_focus:
        slider.grab_focus()
    await process_frame
    var edges := [["ui_right", true], ["ui_right", true], ["ui_right", false], ["ui_left", true], ["ui_left", false], ["ui_left", true], ["ui_left", false]]
    var expv: Array[float] = [5,5,5,5,5,5,5]
    if not no_focus:
        expv = [6,7,7,6,6,5,5]
    var expr: Array[float] = []
    if not no_focus:
        expr = [6,7,6,5]
    for i in range(edges.size()):
        var owner = get_root().gui_get_focus_owner()
        if no_focus and (slider.has_focus() or owner == slider):
            push_error("unexpected slider focus before edge %d" % i); quit(3); return
        if not no_focus and (not slider.has_focus() or owner != slider):
            push_error("missing slider focus before edge %d" % i); quit(3); return
        var e := InputEventAction.new()
        e.action = edges[i][0]
        e.pressed = edges[i][1]
        Input.parse_input_event(e)
        await process_frame
        var n: int = [1,2,2,3,3,4,4][i] if not no_focus else 0
        var want: Array[float] = expr.slice(0,n)
        var lbl := "Value %d" % int(expv[i]) if not no_focus else "Value 5"
        print("EDGE %d %s %s value=%s receipts=%s label=%s owner_is_slider=%s" % [i, edges[i][0], edges[i][1], slider.value, receipts, label.text, get_root().gui_get_focus_owner()==slider])
        if slider.value != expv[i] or receipts != want or label.text != lbl:
            push_error("mismatch at edge %d" % i); quit(4); return
    if no_focus:
        push_error("EXPECTED NEGATIVE: no-focus retained value=5 receipts=[] Label=Value 5 after seven edges")
        quit(2); return
    print("PASS focused seven-edge sequence"); quit(0)
func _on_value_changed(value: float) -> void:
    receipts.append(value)
    label.text = "Value %d" % int(value)
