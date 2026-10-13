extends CharacterBody2D

signal moved(count: int, x: float)
var intent := false
var receipts := 0
var releases := 0
var moves := 0

func _input(event: InputEvent) -> void:
    if event is InputEventKey and (event.keycode == KEY_E or (not event.pressed and OS.get_cmdline_user_args().has("--any-key-up-mutant"))):
        if event.pressed:
            receipts += 1
            intent = true
        else:
            releases += 1
            intent = false

func _physics_process(_delta: float) -> void:
    if intent:
        velocity = Vector2(600, 0)
        move_and_slide()
        moves += 1
        moved.emit(moves, position.x)
    else:
        velocity = Vector2.ZERO
