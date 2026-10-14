extends Node
var matching_releases := 0
func _input(event: InputEvent) -> void:
    if event is InputEventAction and event.action == "ui_left" and not event.pressed:
        matching_releases += 1
