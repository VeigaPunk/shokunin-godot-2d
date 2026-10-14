extends SceneTree
var slider: HSlider
var label: Label
var receipts: Array[float] = []
func _initialize() -> void:
    var ui := CanvasLayer.new()
    slider = HSlider.new()
    slider.min_value=0.0; slider.max_value=10.0; slider.step=1.0; slider.value=5.0; slider.focus_mode=Control.FOCUS_ALL
    label=Label.new(); label.text="Value 5"
    ui.add_child(slider); ui.add_child(label); root.add_child(ui)
    slider.value_changed.connect(_on_value_changed)
    await process_frame
    print("SETUP focus_owner=%s has_focus=%s value=%s receipts=%s label=%s" % [str(get_root().gui_get_focus_owner()), slider.has_focus(), slider.value, receipts, label.text])
    for action in ["ui_right", "ui_left"]:
        var owner_before=get_root().gui_get_focus_owner()
        print("BEFORE action=%s focus_owner=%s has_focus=%s" % [action, str(owner_before), slider.has_focus()])
        _action(action, true); await process_frame; _action(action, false); await process_frame
        print("AFTER action=%s value=%s receipts=%s label=%s focus_owner=%s has_focus=%s" % [action, slider.value, receipts, label.text, str(get_root().gui_get_focus_owner()), slider.has_focus()])
    quit(0)
func _action(action: String, pressed: bool) -> void:
    var event := InputEventAction.new(); event.action=action; event.pressed=pressed; Input.parse_input_event(event)
func _on_value_changed(value: float) -> void:
    receipts.append(value); label.text="Value %d" % int(value)
