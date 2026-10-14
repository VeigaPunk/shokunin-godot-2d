extends SceneTree

const Actor = preload("res://causal_actor.gd")
var ticks := 0
var collections := 0
var transition_requested := false
var moved_observed := false
var move_count := 0

func _initialize() -> void:
    _run.call_deferred()

func _process(_delta: float) -> bool:
    ticks += 1
    if ticks > 180:
        push_error("process bound exceeded")
        quit(2)
    return false

func _moved(count: int, x: float) -> void:
    move_count = count
    moved_observed = x > 0

func _collected() -> void:
    collections += 1
    if not transition_requested:
        transition_requested = true
        call_deferred("_transition")

func _transition() -> void:
    var next := load("res://scene_b.tscn") as PackedScene
    if change_scene_to_packed(next) != OK:
        push_error("transition failed")
        quit(2)

func _run() -> void:
    var negative := OS.get_cmdline_user_args().has("--negative")
    if change_scene_to_packed(load("res://scene_a.tscn")) != OK:
        push_error("scene A failed")
        quit(2)
        return
    await process_frame
    var old := current_scene
    var old_id := old.get_instance_id()
    var pickup := load("res://area_pickup.tscn").instantiate() as Area2D
    pickup.set_script(load("res://causal_pickup.gd"))
    pickup.position = Vector2(100, 0)
    if negative or OS.get_cmdline_user_args().has("--release-test") or OS.get_cmdline_user_args().has("--baseline-release-test") or OS.get_cmdline_user_args().has("--keyup-test"):
        pickup.collision_mask = 0
    pickup.collected.connect(_collected)
    old.add_child(pickup)
    var baseline_release_test := OS.get_cmdline_user_args().has("--baseline-release-test")
    var actor := CharacterBody2D.new()
    actor.set_script(load("res://baseline_actor.gd") if baseline_release_test else Actor)
    actor.position = Vector2.ZERO
    actor.collision_layer = 2
    actor.collision_mask = 0
    var shape := CollisionShape2D.new()
    var circle := CircleShape2D.new()
    circle.radius = 8
    shape.shape = circle
    actor.add_child(shape)
    old.add_child(actor)
    actor.moved.connect(_moved)
    await process_frame
    var args := OS.get_cmdline_user_args()
    var release_test := args.has("--release-test") or args.has("--baseline-release-test") or args.has("--keyup-test")
    var keyup_test := args.has("--keyup-test")
    var wrong_key_negative := args.has("--wrong-key-negative")
    var event := InputEventKey.new()
    event.keycode = KEY_F if wrong_key_negative else KEY_E
    event.pressed = true
    Input.parse_input_event(event)
    if release_test:
        for i in range(20):
            await process_frame
            if actor.receipts > 0:
                break
        if actor.receipts != 1 or not actor.intent:
            push_error("press callback missing")
            quit(2)
            return
        for i in range(4):
            await physics_frame
        var held_moves: int = actor.moves
        if held_moves < 3:
            push_error("held press did not continue moving")
            quit(2)
            return
        if keyup_test:
            var f_up := InputEventKey.new()
            f_up.keycode = KEY_F
            f_up.pressed = false
            Input.parse_input_event(f_up)
            for i in range(20):
                await process_frame
                if OS.get_cmdline_user_args().has("--any-key-up-mutant") or actor.releases > 0:
                    break
            if actor.releases != 0 or not actor.intent:
                push_error("unrelated F release cleared E intent")
                quit(2)
                return
            var before_f_up_frames: int = actor.moves
            for i in range(6):
                await physics_frame
            if actor.moves <= before_f_up_frames:
                push_error("movement stopped after unrelated F release")
                quit(2)
                return
            event = InputEventKey.new()
            event.keycode = KEY_E
            event.pressed = false
            Input.parse_input_event(event)
            for i in range(20):
                await process_frame
                if actor.releases > 0:
                    break
            if actor.releases != 1 or actor.intent:
                push_error("matching E release callback missing or intent remained set")
                quit(2)
                return
            var after_e_up_moves: int = actor.moves
            for i in range(10):
                await physics_frame
            if actor.moves != after_e_up_moves:
                push_error("movement continued after matching E release")
                quit(2)
                return
            print("PASS keyup E_press_receipts=1 F_release_receipts=0 E_release_receipts=1 unrelated_release_moves=6 post_E_release_moves=0 scene=A")
            quit(0)
            return
        event = InputEventKey.new()
        event.keycode = KEY_E
        event.pressed = false
        Input.parse_input_event(event)
        if baseline_release_test:
            var baseline_moves: int = actor.moves
            for i in range(10):
                await physics_frame
            if actor.moves == baseline_moves:
                push_error("baseline unexpectedly stopped after release")
                quit(2)
                return
            push_error("movement continued after release; expected baseline failure")
            quit(2)
            return
        for i in range(20):
            await process_frame
            if actor.releases > 0:
                break
        if actor.releases != 1 or actor.intent:
            push_error("release callback missing or intent remained set")
            quit(2)
            return
        var stopped_moves: int = actor.moves
        for i in range(10):
            await physics_frame
        if actor.moves != stopped_moves:
            push_error("movement continued after release")
            quit(2)
            return
        print("PASS release press_receipts=1 release_receipts=1 held_moves=%d post_release_moves=0 scene=A" % held_moves)
        quit(0)
        return
    if wrong_key_negative:
        event = InputEventKey.new()
        event.keycode = KEY_F
        event.pressed = false
        Input.parse_input_event(event)
        for i in range(20):
            await process_frame
        if actor.receipts != 0 or actor.intent:
            push_error("wrong-key input produced receipt or intent")
            quit(2)
            return
        for i in range(30):
            await physics_frame
        if actor.moves != 0 or collections != 0 or current_scene != old or not is_instance_id_valid(old_id):
            push_error("wrong-key negative moved/collected/transitioned")
            quit(2)
            return
        print("PASS wrong_key=F receipts=0 intent=false physics_moves=0 collections=0 scene=A old_alive=true frames=30")
        quit(1)
        return
    for i in range(20):
        await process_frame
        if actor.receipts > 0:
            break
    if actor.receipts != 1:
        push_error("input callback missing")
        quit(2)
        return
    for i in range(30):
        await physics_frame
        if not is_instance_valid(actor):
            break
        if not negative and collections > 0:
            break
    if not moved_observed:
        push_error("physics movement missing")
        quit(2)
        return
    if negative:
        if collections != 0 or current_scene != old or not is_instance_id_valid(old_id):
            push_error("negative collected/transitioned")
            quit(2)
            return
        print("PASS negative input=1 moves=%d x=%f collections=0 scene=A old_alive=true" % [actor.moves, actor.position.x])
        quit(1)
        return
    for i in range(10):
        await process_frame
        if current_scene != null and current_scene.get("marker") == "B":
            break
    if collections != 1 or current_scene == null or current_scene.get("marker") != "B" or is_instance_id_valid(old_id):
        push_error("chain incomplete collections=%d scene=%s old_alive=%s" % [collections, current_scene, is_instance_id_valid(old_id)])
        quit(2)
        return
    print("PASS positive input=1 physics_moves=%d collections=1 scene=B old_freed=true" % move_count)
    quit(0)
