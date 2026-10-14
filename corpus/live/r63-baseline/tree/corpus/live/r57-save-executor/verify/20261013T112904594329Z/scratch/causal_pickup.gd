extends Area2D
signal collected
var consumed := false
func _ready() -> void:
    body_entered.connect(_body_entered)
func _body_entered(_body: Node2D) -> void:
    if consumed:
        return
    consumed = true
    collected.emit()
