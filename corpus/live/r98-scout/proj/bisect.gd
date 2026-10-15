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
	for variant in ["plain", "hideshow", "texrepeat", "upm", "clip", "lightmask", "oversample", "texfilter"]:
		var t := RT.new()
		root.add_child(t)
		for i in 3: await process_frame
		match variant:
			"hideshow":
				t.hide(); await process_frame; t.show(); for i in 2: await process_frame
			"texrepeat": t.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
			"upm": t.use_parent_material = true
			"clip": t.clip_children = CanvasItem.CLIP_CHILDREN_ONLY
			"lightmask": t.light_mask = 2
			"oversample": t.set_oversampling_with_scale(CanvasItem.OVERSAMPLING_WITH_SCALE_ENABLED)
			"texfilter": t.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		for i in 3: await process_frame
		var d0 := t.draws
		t.skew = 0.2
		for i in 3: await process_frame
		print("BISECT %s skew_delta=%d" % [variant, t.draws - d0])
		t.free()
		for i in 2: await process_frame
	quit()
