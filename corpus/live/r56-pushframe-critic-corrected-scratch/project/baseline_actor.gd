extends CharacterBody2D

signal moved(count: int, x: float)
var intent := false
var receipts := 0
var moves := 0

func _input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and event.keycode == KEY_E:
        receipts += 1
        intent = true

func _physics_process(_delta: float) -> void:
    if intent:
        velocity = Vector2(600, 0)
        move_and_slide()
        moves += 1
        moved.emit(moves, position.x)
