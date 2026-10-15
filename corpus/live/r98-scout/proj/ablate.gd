extends SceneTree
func _initialize() -> void:
	_run.call_deferred()
class RT:
	extends Node2D
	var draws := 0
	func _draw() -> void:
		draws += 1
func _run() -> void:
	var labels := ["A_texrepeat", "B_oversample", "C_clip", "D_ysort", "E_zrel", "F_lightmask", "G_selfmod", "H_upm", "I_hide", "J_show", "K_scale"]
	var variants: Array = ["full"]
	for l in labels:
		variants.append("minus_" + l)
	for variant in variants:
		var t := RT.new()
		root.add_child(t)
		for i in 3: await process_frame
		if not (variant == "minus_A_texrepeat"):
			t.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
		if not (variant == "minus_B_oversample"):
			t.set_oversampling_with_scale(CanvasItem.OVERSAMPLING_WITH_SCALE_ENABLED)
		if not (variant == "minus_C_clip"):
			t.clip_children = CanvasItem.CLIP_CHILDREN_ONLY
		if not (variant == "minus_D_ysort"):
			t.y_sort_enabled = true
		if not (variant == "minus_E_zrel"):
			t.z_as_relative = false
		if not (variant == "minus_F_lightmask"):
			t.light_mask = 2
		if not (variant == "minus_G_selfmod"):
			t.self_modulate = Color(0.5, 0.5, 0.5, 1)
		if not (variant == "minus_H_upm"):
			t.use_parent_material = true
		if not (variant == "minus_I_hide"):
			t.hide()
		if not (variant == "minus_J_show"):
			t.show()
		if not (variant == "minus_K_scale"):
			t.scale = Vector2(2, 2)
		for i in 3: await process_frame
		var d0 := t.draws
		t.skew = 0.2
		for i in 4: await process_frame
		print("ABLATE %s skew_delta=%d" % [variant, t.draws - d0])
		t.free()
		for i in 2: await process_frame
	quit()
