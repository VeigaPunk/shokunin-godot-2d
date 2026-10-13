extends Node
var releases := 0
func _input(event: InputEvent) -> void:
    if event is InputEventAction:
        print("OBS", event.action, " pressed=", event.pressed, " echo=", event.is_echo())
        if event.action == "ui_left" and not event.pressed:
            releases += 1
