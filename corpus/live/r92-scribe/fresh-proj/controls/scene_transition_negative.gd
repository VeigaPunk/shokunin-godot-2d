extends SceneTree

var frames := 0

func _initialize() -> void:
    _run.call_deferred()

func _process(_delta: float) -> bool:
    frames += 1
    if frames > 120:
        push_error("negative transition probe exceeded 120 frames")
        quit(1)
        return true
    return false

func _run() -> void:
    var first := load("res://scene_a.tscn") as PackedScene
    if first == null or change_scene_to_packed(first) != OK:
        _fail("could not establish starting scene")
        return
    await process_frame
    var old_id := current_scene.get_instance_id()
    # Deliberately omit a valid destination: API reports ERR_INVALID_PARAMETER.
    var err := change_scene_to_packed(null)
    await process_frame
    if err == OK or current_scene == null or current_scene.get_instance_id() != old_id or not is_instance_id_valid(old_id):
        _fail("invalid destination did not preserve current scene")
        return
    print("PASS invalid_destination_rejected=true current_scene_preserved=true old_scene_alive=true frames=%d" % frames)
    push_error("negative control: deliberately invalid scene destination rejected")
    quit(1)

func _fail(message: String) -> void:
    push_error("negative transition probe: " + message)
    quit(1)
