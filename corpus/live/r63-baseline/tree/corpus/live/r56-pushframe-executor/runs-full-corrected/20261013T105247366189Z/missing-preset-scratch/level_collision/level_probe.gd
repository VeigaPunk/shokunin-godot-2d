extends SceneTree

func _initialize() -> void:
    call_deferred("run")

func run() -> void:
    var packed := load("res://level_collision/level_scene.tscn") as PackedScene
    var level := packed.instantiate()
    root.add_child(level)
    var ground := level.get_node("Ground") as TileMapLayer
    if OS.get_cmdline_user_args().has("--no-collision"):
        var ts := ground.tile_set.duplicate(true)
        var atlas := ts.get_source(0) as TileSetAtlasSource
        atlas.get_tile_data(Vector2i.ZERO, 0).set_collision_polygons_count(0, 0)
        ground.tile_set = ts
    var source_id := ground.get_cell_source_id(Vector2i(2, 3))
    var cell := ground.get_cell_tile_data(Vector2i(2, 3))
    var count := cell.get_collision_polygons_count(0) if cell else 0
    var points := cell.get_collision_polygon_points(0, 0) if count > 0 else PackedVector2Array()
    var valid := source_id == 0 and cell != null and count == 1 and points.size() >= 3
    var vertices := points.size()
    level.queue_free()
    await process_frame
    if not valid:
        push_error("LEVEL ASSERTION FAILED: loaded level cell lacks collision geometry")
        quit(2)
        return
    print("PASS level_packed_scene=true cell=2,3 collision_vertices=%d" % vertices)
    quit(0)
