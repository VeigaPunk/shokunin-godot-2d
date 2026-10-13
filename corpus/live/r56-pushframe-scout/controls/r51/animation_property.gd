extends SceneTree

func _initialize() -> void:
    var stuck := "--stuck" in OS.get_cmdline_user_args()
    var target := Node2D.new()
    target.name = "Target"
    root.add_child(target)

    var animation := Animation.new()
    animation.length = 1.0
    var track := animation.add_track(Animation.TYPE_VALUE)
    animation.track_set_path(track, NodePath(".:position:x"))
    animation.track_insert_key(track, 0.0, 0.0)
    animation.track_insert_key(track, 1.0, 120.0)
    var library := AnimationLibrary.new()
    library.add_animation("move", animation)
    var player := AnimationPlayer.new()
    target.add_child(player)
    player.add_animation_library("", library)

    await process_frame
    if not is_zero_approx(target.position.x):
        push_error("ANIMATION ASSERTION FAILED: initial property was not x=0")
        quit(2)
        return
    player.play("move")
    if stuck:
        player.speed_scale = 0.0
    player.advance(0.5)
    if not is_equal_approx(target.position.x, 60.0):
        push_error("ANIMATION ASSERTION FAILED: expected animated property x=60 after bounded advance, got %s" % target.position.x)
        quit(2)
        return
    print("PASS animation_property_changed=true started=true x=%s" % target.position.x)
    quit(0)
