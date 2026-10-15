extends SceneTree
# FALSE-POSITIVE PROBE for geo2d_lattice_lineempty:
# emit the pinned signature verbatim on stdout, then die by a *different*
# SIGABRT (INF-vertex clip -> bare abort, boundary §4.1 bool_inf_clip),
# proving the row cannot attribute the abort to the named call.
func _initialize() -> void:
	_run.call_deferred()

func _run() -> void:
	print("R89 lineempty call=offset_polyline(empty,2.0,JOIN_ROUND,END_JOINED)")
	var bad := PackedVector2Array([Vector2(0, 0), Vector2(INF, 0), Vector2(10, 10)])
	var sq := PackedVector2Array([Vector2(0, 0), Vector2(1, 0), Vector2(1, 1)])
	var r := Geometry2D.clip_polygons(bad, sq)
	print("unreachable result=", r)
	quit()
