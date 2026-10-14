extends SceneTree
var btn: Button
var label: Label
var receipts := 0
func _initialize(): call_deferred("run")
func _pressed(): receipts += 1; label.text = "Activated %d" % receipts
func _pair():
 var e := InputEventAction.new(); e.action = "ui_accept"; e.pressed = true; root.push_input(e)
 var r := InputEventAction.new(); r.action = "ui_accept"; r.pressed = false; root.push_input(r)
func run():
 var ui := CanvasLayer.new(); btn = Button.new(); label = Label.new(); label.text="Ready"; ui.add_child(btn); ui.add_child(label); root.add_child(ui); btn.pressed.connect(_pressed); await process_frame
 btn.grab_focus(); print("FOCUSED has_focus=%s owner=%s" % [btn.has_focus(), get_root().gui_get_focus_owner() == btn]); await _pair(); await process_frame; print("FOCUSED result receipts=%d label=%s" % [receipts,label.text])
 btn.release_focus(); receipts=0; label.text="Ready"; print("UNFOCUSED has_focus=%s owner_null=%s" % [btn.has_focus(), get_root().gui_get_focus_owner() == null]); await _pair(); await process_frame; print("UNFOCUSED result receipts=%d label=%s" % [receipts,label.text]); quit()
