extends SceneTree
func _initialize() -> void:
	_run.call_deferred()
class RT:
	extends Node2D
	var draws := 0
	func _draw() -> void:
		draws += 1
func _variant(ov: bool, sh: bool, sc: bool, sk: bool) -> int:
	var t := RT.new()
	root.add_child(t)
	for i in 3: await process_frame
	if ov:
		t.set_oversampling_with_scale(CanvasItem.OVERSAMPLING_WITH_SCALE_ENABLED)
	for i in 3: await process_frame
	if sh:
		t.show()
	for i in 3: await process_frame
	if sc:
		t.scale = Vector2(2, 2)
	for i in 3: await process_frame
	var d0 := t.draws
	if sk:
		t.skew = 0.2
	for i in 4: await process_frame
	var delta := t.draws - d0
	t.free()
	for i in 2: await process_frame
	return delta
func _run() -> void:
	print("MIN ov1_sh1_sc1_sk1=", await _variant(true, true, true, true))
	print("MIN ov1_sh0_sc1_sk1=", await _variant(true, false, true, true))
	print("MIN ov0_sh1_sc1_sk1=", await _variant(false, true, true, true))
	print("MIN ov1_sh1_sc0_sk1=", await _variant(true, true, false, true))
	print("MIN ov1_sh1_sc1_sk0=", await _variant(true, true, true, false))
	print("MIN ov0_sh0_sc0_sk1=", await _variant(false, false, false, true))
	quit()
