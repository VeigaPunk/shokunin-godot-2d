extends SceneTree
var callbacks := 0
var button: Button
var label: Label
func _initialize() -> void:
    button = Button.new()
    button.text = "Activate"
    label = Label.new()
    label.text = "Ready"
    root.add_child(button)
    root.add_child(label)
    button.pressed.connect(_on_pressed)
    print("SETUP in_tree=", button.is_inside_tree(), ",", label.is_inside_tree(), " initial=", label.text)
    button.press()
    print("AFTER press callbacks=", callbacks, " text=", label.text)
    if callbacks != 1 or label.text != "Activated":
        push_error("ASSERT expected one pressed callback and Activated label; callbacks=%d text=%s" % [callbacks, label.text])
        quit(2)
        return
    print("PASS button_press callbacks=1 label=Activated")
    quit(0)
func _on_pressed() -> void:
    callbacks += 1
    label.text = "Activated"
