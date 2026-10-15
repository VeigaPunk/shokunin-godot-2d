extends SceneTree
# FALSE-POSITIVE PROBE v2: signature emitted ONLY on stderr (printerr),
# then the same wrong-cause SIGABRT. Tests whether `signature in output`
# (stdout+stderr merged by run_process) is stream-blind.
func _initialize() -> void:
	_run.call_deferred()

func _run() -> void:
	printerr("R89 lineempty call=offset_polyline(empty,2.0,JOIN_ROUND,END_JOINED)")
	var bad := PackedVector2Array([Vector2(0, 0), Vector2(INF, 0), Vector2(10, 10)])
	var sq := PackedVector2Array([Vector2(0, 0), Vector2(1, 0), Vector2(1, 1)])
	var r := Geometry2D.clip_polygons(bad, sq)
	print("unreachable result=", r)
	quit()
