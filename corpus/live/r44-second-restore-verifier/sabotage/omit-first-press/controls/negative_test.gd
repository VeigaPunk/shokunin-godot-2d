extends SceneTree

func _initialize() -> void:
    var deliberately_violated_condition := false
    if not deliberately_violated_condition:
        push_error("negative control: deliberate condition failed")
        quit(1)
        return
    quit(0)
