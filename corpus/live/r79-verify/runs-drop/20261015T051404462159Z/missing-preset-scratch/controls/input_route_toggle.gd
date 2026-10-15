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
    if receiver.get_script() != receiver_script or receiver.get("route_owner") != self or receiver.process_mode != Node.PROCESS_MODE_DISABLED:
        return _fail("disabled receiver setup failed")
    root.add_child(receiver)
    await process_frame
    _dispatch_r()
    for _i in range(8):
        await process_frame
        if received != 0:
            return _fail("disabled receiver received first R; receipt_count=" + str(received))
    receiver.process_mode = Node.PROCESS_MODE_INHERIT
    if receiver.process_mode != Node.PROCESS_MODE_INHERIT:
        return _fail("receiver did not reenable")
    for _i in range(2):
        await process_frame
        if received != 0:
            return _fail("queued first R reached reenabled receiver; receipt_count=" + str(received))
    _dispatch_r()
    for _i in range(8):
        await process_frame
        if received > 1:
            return _fail("duplicate or queued R receipt; receipt_count=" + str(received))
        if received == 1:
            break
    if received != 1:
        return _fail("reenabled receiver did not receive second R within 8 frames; receipt_count=" + str(received))
    for _i in range(2):
        await process_frame
        if received != 1:
            return _fail("late duplicate or queued R receipt; receipt_count=" + str(received))
    print("PASS toggle=disabled-to-inherit first_receipts=0 second_receipts=1 late_receipts=0 frames=%d" % frames)
    quit(0)

func _dispatch_r() -> void:
    var event := InputEventKey.new()
    event.keycode = KEY_R
    event.pressed = true
    Input.parse_input_event(event)

func note_input(event: InputEvent) -> void:
    if event is InputEventKey and event.keycode == KEY_R and event.pressed:
        received += 1

func _fail(message: String) -> void:
    push_error("input route toggle: " + message)
    quit(1)
