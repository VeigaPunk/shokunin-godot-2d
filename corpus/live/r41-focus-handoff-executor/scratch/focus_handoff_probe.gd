extends SceneTree
var slider: HSlider
var label: Label
var other: Button
var receipts: Array[float] = []
func _initialize() -> void:
 var ui := CanvasLayer.new()
 slider = HSlider.new(); slider.min_value=0.0; slider.max_value=10.0; slider.step=1.0; slider.value=5.0; slider.focus_mode=Control.FOCUS_ALL
 label = Label.new(); label.text="Value 5"
 other = Button.new(); other.text="Other"; other.focus_mode=Control.FOCUS_ALL
 ui.add_child(slider); ui.add_child(label); ui.add_child(other); root.add_child(ui)
 slider.value_changed.connect(_on_value_changed)
 await process_frame
 slider.grab_focus(); await process_frame
 print("SETUP slider_tree=%s value=%s owner_slider=%s other_tree=%s" % [slider.is_inside_tree(),slider.value,get_root().gui_get_focus_owner()==slider,other.is_inside_tree()])
 _action("ui_right",true); await process_frame
 print("EDGE0 value=%s receipts=%s label=%s owner_slider=%s" % [slider.value,receipts,label.text,get_root().gui_get_focus_owner()==slider])
 other.grab_focus(); await process_frame
 print("HANDOFF owner_other=%s slider_focus=%s slider_value=%s receipts=%s label=%s" % [get_root().gui_get_focus_owner()==other,slider.has_focus(),slider.value,receipts,label.text])
 var edges := [["ui_right",true],["ui_right",false],["ui_left",true],["ui_left",false],["ui_left",true],["ui_left",false]]
 for i in range(edges.size()):
  _action(edges[i][0],edges[i][1]); await process_frame
  print("EDGE%d action=%s pressed=%s value=%s receipts=%s label=%s owner_other=%s slider_focus=%s" % [i+1,edges[i][0],edges[i][1],slider.value,receipts,label.text,get_root().gui_get_focus_owner()==other,slider.has_focus()])
 quit(0)
func _action(action: String, pressed: bool) -> void:
 var event := InputEventAction.new(); event.action=action; event.pressed=pressed; Input.parse_input_event(event)
func _on_value_changed(value: float) -> void:
 receipts.append(value); label.text="Value %d" % int(value)
