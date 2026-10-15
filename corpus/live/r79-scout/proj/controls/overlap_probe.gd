extends SceneTree

var signals := 0

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var pickup_scene := load("res://area_pickup.tscn") as PackedScene
	if pickup_scene == null:
		return _fail("pickup PackedScene failed to load")
	var pickup := pickup_scene.instantiate() as Area2D
	if pickup == null or not pickup.get_node("CollisionShape2D").shape is CircleShape2D:
		return _fail("pickup instance/shape invalid")
	pickup.collected.connect(_on_collected)
	root.add_child(pickup)
	var body := Area2D.new()
	body.name = "OverlapArea"
	body.collision_layer = 2
	body.collision_mask = 0
	var shape_node := CollisionShape2D.new()
	var shape := CircleShape2D.new()
	shape.radius = 8.0
	shape_node.shape = shape
	body.add_child(shape_node)
	root.add_child(body)
	await physics_frame
	if signals != 0:
		return _fail("signal occurred before physics overlap observation")
	for _i in range(4):
		await physics_frame
	if signals != 1 or not pickup.consumed:
		return _fail("overlap did not consume and emit exactly once; count=" + str(signals))
	print("PASS packed_scene=true area_shape=true layers=1/2 masks=2/0 pre_overlap_signals=0 overlap_signal_count=1 consumed=true")
	quit(0)

func _on_collected() -> void:
	signals += 1

func _fail(message: String) -> void:
	push_error("overlap probe: " + message)
	quit(1)
