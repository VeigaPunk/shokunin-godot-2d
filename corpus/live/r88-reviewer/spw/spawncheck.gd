extends SceneTree
# reviewer r88: verify the spawner-refusal claim on 4.7.2
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var cont := Node.new(); cont.name = "cont"
	root.add_child(cont)
	var sp := MultiplayerSpawner.new()
	sp.spawn_path = cont.get_path()
	root.add_child(sp)
	var r0 = sp.spawn(0)
	print("SPAWNCHECK spawn(0) -> %s" % [r0])
	var r1 = sp.spawn()
	print("SPAWNCHECK spawn() -> %s" % [r1])
	sp.spawn_function = func(data): return Node2D.new()
	var r2 = sp.spawn(0)
	print("SPAWNCHECK spawn(0)+fn -> %s" % [r2])
	print("SPAWNCHECK child_count=%d" % cont.get_child_count())
	quit(0)
