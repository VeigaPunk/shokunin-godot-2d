extends SceneTree
var receipts: Array[float] = []
var slider: HSlider
func _initialize() -> void: call_deferred("run")
func _on_value(v: float) -> void: receipts.append(v)
func send_action(action: String) -> void:
 var e=InputEventAction.new(); e.action=action; e.pressed=true; root.push_input(e); await process_frame
 e=InputEventAction.new(); e.action=action; e.pressed=false; root.push_input(e); await process_frame
func run() -> void:
 var ui=CanvasLayer.new(); slider=HSlider.new(); slider.min_value=0; slider.max_value=10; slider.step=1; slider.value=5
 var label=Label.new(); label.text="Value 5"
 ui.add_child(slider); ui.add_child(label); root.add_child(ui); if not OS.get_cmdline_user_args().has("--disconnect"): slider.value_changed.connect(_on_value)
 await process_frame
 slider.grab_focus(); await process_frame
 print("setup value=%s focus=%s owner=%s" % [slider.value,slider.has_focus(),get_root().get_viewport().gui_get_focus_owner()])
 if OS.get_cmdline_user_args().has("--programmatic"): slider.value=6
 else: await send_action("ui_right")
 print("after_right value=%s receipts=%s" % [slider.value,receipts])
 if OS.get_cmdline_user_args().has("--programmatic"): slider.value=5
 else: await send_action("ui_left")
 print("after_left value=%s receipts=%s" % [slider.value,receipts])
 quit(0)
