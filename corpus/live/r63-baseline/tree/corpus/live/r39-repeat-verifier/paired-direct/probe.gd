extends SceneTree
var slider: HSlider
var label: Label
var receipts: Array[float] = []
var disconnected := OS.get_cmdline_user_args().has("--disconnect-signal")
var expv: Array[float] = [6,7,7,6,6,5,5]
var expr: Array = [[6.0],[6.0,7.0],[6.0,7.0],[6.0,7.0,6.0],[6.0,7.0,6.0],[6.0,7.0,6.0,5.0],[6.0,7.0,6.0,5.0]]
func _initialize() -> void:
 var ui := CanvasLayer.new()
 slider=HSlider.new(); slider.min_value=0; slider.max_value=10; slider.step=1; slider.value=5; slider.focus_mode=Control.FOCUS_ALL
 label=Label.new(); label.text="Value 5"; ui.add_child(slider); ui.add_child(label); root.add_child(ui)
 if not disconnected: slider.value_changed.connect(_changed)
 await process_frame; slider.grab_focus(); await process_frame
 var edges=[["ui_right",true],["ui_right",true],["ui_right",false],["ui_left",true],["ui_left",false],["ui_left",true],["ui_left",false]]
 for i in range(7):
  if get_root().gui_get_focus_owner()!=slider: push_error("focus lost %d" % i); quit(1); return
  var event=InputEventAction.new(); event.action=edges[i][0]; event.pressed=edges[i][1]; Input.parse_input_event(event); await process_frame
  var wantr=expr[i] if not disconnected else []
  var wantlabel="Value %d" % int(expv[i]) if not disconnected else "Value 5"
  print("edge=%d action=%s pressed=%s value=%s receipts=%s label=%s focus=%s" % [i,edges[i][0],edges[i][1],slider.value,receipts,label.text,get_root().gui_get_focus_owner()==slider])
  if slider.value!=expv[i] or receipts!=wantr or label.text!=wantlabel: push_error("edge assertion %d" % i); quit(1); return
 if disconnected: print("DISCONNECTED COMPLETE exit2 after all seven"); quit(2)
 else: print("CONNECTED COMPLETE"); quit(0)
func _changed(v:float)->void: receipts.append(v); label.text="Value %d" % int(v)
