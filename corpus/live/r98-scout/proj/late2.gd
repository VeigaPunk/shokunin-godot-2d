extends SceneTree
func _initialize() -> void:
	_run.call_deferred()
class RT:
	extends Node2D
	var draws := 0
	var ev: Array = []
	func _draw() -> void:
		draws += 1
		ev.append("d@pf%d" % Engine.get_process_frames())
func _run() -> void:
	for variant in ["noop", "skew", "scale", "rot", "pos"]:
		var t := RT.new()
		root.add_child(t)
		for i in 3: await process_frame
		var steps := [
			["texture_repeat", func(): t.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED],
			["oversampling", func(): t.set_oversampling_with_scale(CanvasItem.OVERSAMPLING_WITH_SCALE_ENABLED)],
			["clip_children", func(): t.clip_children = CanvasItem.CLIP_CHILDREN_ONLY],
			["y_sort", func(): t.y_sort_enabled = true],
			["z_as_relative", func(): t.z_as_relative = false],
			["light_mask", func(): t.light_mask = 2],
			["self_modulate", func(): t.self_modulate = Color(0.5, 0.5, 0.5, 1)],
			["use_parent_material", func(): t.use_parent_material = true],
			["hide", func(): t.hide()],
			["show", func(): t.show()],
			["scale", func(): t.scale = Vector2(2, 2)],
		]
		for s in steps:
			var f: Callable = s[1]
			f.call()
			for i in 3: await process_frame
		t.ev.clear()
		var d0 := t.draws
		match variant:
			"skew": t.skew = 0.2
			"scale": t.scale = Vector2(3, 3)
			"rot": t.rotation = 0.3
			"pos": t.position = Vector2(4, 4)
			"noop": pass
		for i in 4: await process_frame
		print("LATE2 %s delta=%d ev=%s" % [variant, t.draws - d0, t.ev])
		t.free()
		for i in 2: await process_frame
	quit()
