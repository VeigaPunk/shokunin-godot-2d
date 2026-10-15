extends SceneTree
var b: Button
var count := 0
func _initialize():
 b=Button.new()
 root.add_child(b)
 b.pressed.connect(func(): count += 1)
 await process_frame
 print("methods press=", b.has_method("press"), " _pressed=", b.has_method("_pressed"), " gui=", b.has_method("_gui_input"), " input=", b.has_method("_input"))
 b.press()
 print("after press count=",count," pressed=",b.button_pressed)
 quit()
