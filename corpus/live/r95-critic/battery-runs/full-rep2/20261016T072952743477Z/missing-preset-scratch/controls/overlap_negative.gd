extends SceneTree

var signals := 0

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var pickup := (load("res://area_pickup.tscn") as PackedScene).instantiate() as Area2D
	pickup.collected.connect(_on_collected)
	pickup.collision_mask = 0
	root.add_child(pickup)
	var body := Area2D.new()
	body.collision_layer = 2
	body.collision_mask = 0
	var shape_node := CollisionShape2D.new()
	var shape := CircleShape2D.new()
	shape.radius = 8.0
	shape_node.shape = shape
	body.add_child(shape_node)
	root.add_child(body)
	for _i in range(5):
		await physics_frame
	if signals != 0 or pickup.consumed:
		print("PASS negative control: expected absence condition did not occur")
		quit(0)
		return
	push_error("negative control: expected collected signal was absent with disabled mask")
	quit(1)

func _on_collected() -> void:
	signals += 1
