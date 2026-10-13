extends SceneTree
var slider: HSlider
var other: Button
var receipts: Array[float] = []
var label: Label
func _initialize() -> void:
 var ui := CanvasLayer.new()
 slider = HSlider.new(); slider.min_value=0; slider.max_value=10; slider.step=1; slider.value=5; slider.focus_mode=Control.FOCUS_ALL
 other = Button.new(); other.text="Other"; other.focus_mode=Control.FOCUS_ALL
 label=Label.new(); label.text="Value 5"
 ui.add_child(slider); ui.add_child(other); ui.add_child(label); root.add_child(ui)
 slider.value_changed.connect(func(v): receipts.append(v); label.text="Value %d" % int(v))
 await process_frame
 slider.grab_focus(); await process_frame
 if get_root().gui_get_focus_owner()!=slider: fail("initial focus")
 _action("ui_right", true); await process_frame
 if slider.value!=6 or receipts != [6.0] or label.text!="Value 6": fail("first edge")
 other.grab_focus(); await process_frame
 if get_root().gui_get_focus_owner()!=other or slider.has_focus(): fail("handoff")
 var edges := [["ui_right",true],["ui_right",false],["ui_left",true],["ui_left",false],["ui_left",true],["ui_left",false]]
 for i in range(edges.size()):
  if get_root().gui_get_focus_owner()!=other or slider.has_focus(): fail("owner before %d" % i)
  _action(edges[i][0], edges[i][1]); await process_frame
  if slider.value!=6 or receipts != [6.0] or label.text!="Value 6": fail("receipt/value after %d" % i)
  if get_root().gui_get_focus_owner()!=other or slider.has_focus(): fail("owner after %d" % i)
 print("PASS first=6/[6]/Value6, handoff owner=other; six remaining edges retained 6/[6]/Value6; owner stayed other")
 quit(0)
func fail(s:String)->void:
 push_error("CRITIC FAIL: "+s+" value=%s receipts=%s label=%s owner=%s" % [slider.value, receipts, label.text, get_root().gui_get_focus_owner()])
 quit(1)
func _action(action:String, pressed:bool)->void:
 var e:=InputEventAction.new(); e.action=action; e.pressed=pressed; Input.parse_input_event(e)
