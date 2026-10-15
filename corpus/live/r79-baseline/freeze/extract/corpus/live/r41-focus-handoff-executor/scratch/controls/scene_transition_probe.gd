extends SceneTree

var frames := 0

func _initialize() -> void:
    _run.call_deferred()

func _process(_delta: float) -> bool:
    frames += 1
    if frames > 120:
        push_error("scene transition probe exceeded 120 frames")
        quit(1)
        return true
    return false

func _run() -> void:
    var first := load("res://scene_a.tscn") as PackedScene
    var next := load("res://scene_b.tscn") as PackedScene
    if first == null or next == null:
        _fail("PackedScene load failed")
        return
    var err := change_scene_to_packed(first)
    if err != OK:
        _fail("initial change_scene_to_packed failed: %s" % err)
        return
    await process_frame
    var old := current_scene
    if old == null or old.get("marker") != "A":
        _fail("initial current_scene identity/marker mismatch")
        return
    var old_id := old.get_instance_id()
    err = change_scene_to_packed(next)
    if err != OK:
        _fail("valid change_scene_to_packed failed: %s" % err)
        return
    await process_frame
    await process_frame
    if current_scene == null or current_scene.get("marker") != "B" or current_scene.get_instance_id() == old_id:
        _fail("current_scene replacement identity/marker mismatch")
        return
    if is_instance_id_valid(old_id):
        _fail("old scene was not freed")
        return
    print("PASS valid_transition=true current_scene_replaced=true marker=B old_scene_freed=true frames=%d" % frames)
    quit(0)

func _fail(message: String) -> void:
    push_error("scene transition probe: " + message)
    quit(1)
