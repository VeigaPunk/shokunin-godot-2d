extends SceneTree
# r93-reviewer claim probe (NOT part of the landing): prints the STATIC
# Tween.interpolate_value values for the exact (initial, delta, t, trans, ease)
# points the r93_anim_overshoot row pins at runtime. Note Godot's second
# parameter is the DELTA (final = initial + delta); the runtime tween 1.0 -> 10.0
# is therefore interpolate_value(1.0, 9.0, ...). Read-only w.r.t. the fixtures.

func _initialize() -> void:
	var pts := [
		["back_io_025_1to10", Tween.interpolate_value(1.0, 9.0, 0.25, 1.0, Tween.TRANS_BACK, Tween.EASE_IN_OUT)],
		["back_io_050_1to10", Tween.interpolate_value(1.0, 9.0, 0.5, 1.0, Tween.TRANS_BACK, Tween.EASE_IN_OUT)],
		["spr_out_050_0to10", Tween.interpolate_value(0.0, 10.0, 0.5, 1.0, Tween.TRANS_SPRING, Tween.EASE_OUT)],
		["spr_out_100_0to10", Tween.interpolate_value(0.0, 10.0, 1.0, 1.0, Tween.TRANS_SPRING, Tween.EASE_OUT)],
		["ela_out_025_0to10", Tween.interpolate_value(0.0, 10.0, 0.25, 1.0, Tween.TRANS_ELASTIC, Tween.EASE_OUT)],
		["bac_io_025_0to10", Tween.interpolate_value(0.0, 10.0, 0.25, 1.0, Tween.TRANS_BACK, Tween.EASE_IN_OUT)],
		["lin_neg_050", Tween.interpolate_value(0.0, 10.0, -0.5, 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN)],
		["lin_over_150", Tween.interpolate_value(0.0, 10.0, 1.5, 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN)],
	]
	var parts: Array[String] = []
	for p in pts:
		parts.append("%s=%s" % [p[0], p[1]])
	print("PASS r93r_static ", ",".join(parts))
	quit(0)
