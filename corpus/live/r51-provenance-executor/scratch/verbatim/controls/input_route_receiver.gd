extends Node

var route_owner: SceneTree

func _input(event: InputEvent) -> void:
    route_owner.note_input(event)
