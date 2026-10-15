extends SceneTree
var slider: HSlider
var label: Label
var receipts: Array[float] = []
var arm := "connected"
func _initialize() -> void:
    var args = OS.get_cmdline_user_args()
    if args.has("--disconnect"): arm = "disconnected"
    if args.has("--no-focus"): arm = "no-focus"
    slider = HSlider.new(); slider.min_value=0; slider.max_value=10; slider.step=1; slider.value=5; slider.focus_mode=Control.FOCUS_ALL
    label=Label.new(); label.text="Value 5"
    var ui=CanvasLayer.new(); ui.add_child(slider); ui.add_child(label); root.add_child(ui)
    if arm != "disconnected": slider.value_changed.connect(_on_value_changed)
    await process_frame
    if arm != "no-focus": slider.grab_focus()
    await process_frame
    print("ARM=%s focus=%s owner=%s initial value=%s receipts=%s label=%s" % [arm,slider.has_focus(),get_root().gui_get_focus_owner()==slider,slider.value,receipts,label.text])
    await _edge("ui_right", true, 5.0 if arm=="no-focus" else 6.0, [6.0] if arm=="connected" else [], "Value 6" if arm=="connected" else "Value 5")
    await _edge("ui_right", false, 6.0 if arm != "no-focus" else 5.0, [6.0] if arm=="connected" else [], "Value 6" if arm=="connected" else "Value 5")
    await _edge("ui_left", true, 5.0 if arm != "no-focus" else 5.0, [6.0,5.0] if arm=="connected" else [], "Value 5")
    await _edge("ui_left", false, 5.0, [6.0,5.0] if arm=="connected" else [], "Value 5")
    quit(0)
func _edge(action:String, pressed:bool, expected:float, expected_receipts:Array, expected_label:String) -> void:
    var e=InputEventAction.new(); e.action=action; e.pressed=pressed; Input.parse_input_event(e)
    await process_frame
    print("EDGE action=%s pressed=%s value=%s receipts=%s label=%s focus=%s" % [action,pressed,slider.value,receipts,label.text,slider.has_focus()])
    if slider.value != expected or receipts != expected_receipts or label.text != expected_label:
        push_error("EDGE MISMATCH expected value=%s receipts=%s label=%s" % [expected,expected_receipts,expected_label]); quit(3)
func _on_value_changed(v:float) -> void:
    receipts.append(v); label.text="Value %d" % int(v)
