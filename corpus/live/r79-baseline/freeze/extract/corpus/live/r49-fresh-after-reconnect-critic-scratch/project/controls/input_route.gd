extends SceneTree

var frames := 0
var received := 0
var receiver: Node

func _initialize() -> void:
    call_deferred("_run")

func _process(_delta: float) -> bool:
    frames += 1
    if frames > 120:
        _fail("exceeded 120 process frames")
        return true
    return false

func _run() -> void:
    var receiver_script = load("res://controls/input_route_receiver.gd")
    if receiver_script == null:
        return _fail("receiver script failed to load")
    receiver = Node.new()
    receiver.set_script(receiver_script)
    receiver.set("route_owner", self)
    if receiver.get_script() != receiver_script or receiver.get("route_owner") != self:
        return _fail("receiver setup failed")
    root.add_child(receiver)
    await process_frame
    var event := InputEventKey.new()
    event.keycode = KEY_R
    event.pressed = true
    Input.parse_input_event(event)
    for _i in range(8):
        if received == 1:
            break
        await process_frame
    if received != 1:
        return _fail("dedicated Node._input did not receive synthetic R within 8 frames")
    print("PASS route=parse_input_event-to-Node._input key=R receipt_count=1 frames=%d" % frames)
    quit(0)

func _fail(message: String) -> void:
    push_error("input route: " + message)
    quit(1)

func note_input(event: InputEvent) -> void:
    if event is InputEventKey and event.keycode == KEY_R and event.pressed:
        received += 1
