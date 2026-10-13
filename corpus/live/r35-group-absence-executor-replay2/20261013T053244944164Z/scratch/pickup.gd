extends Area2D

signal collected

func _ready() -> void:
	area_entered.connect(_on_area_entered)

func _on_area_entered(_area: Area2D) -> void:
	collect()

var consumed := false

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_E:
		collect()

func collect() -> bool:
	if consumed:
		return false
	consumed = true
	collected.emit()
	return true
