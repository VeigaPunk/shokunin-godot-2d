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
    receiver.process_mode = Node.PROCESS_MODE_DISABLED
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
            return _fail("queued/wrong-route event unexpectedly reached disabled receiver")
        await process_frame
    if received != 0:
        return _fail("control did not discriminate; receipt_count=" + str(received))
    print("PASS negative_route=disabled_node receipt_count=0 frames=%d expected_exit=1 (intentional negative-control status)" % frames)
    quit(1)

func _fail(message: String) -> void:
    push_error("input route negative: " + message)
    quit(1)

func note_input(event: InputEvent) -> void:
    if event is InputEventKey and event.keycode == KEY_R and event.pressed:
        received += 1
