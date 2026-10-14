extends SceneTree

func _initialize() -> void:
    call_deferred("run")

func run() -> void:
    var packed := load("res://level_collision/level_scene.tscn") as PackedScene
    var level := packed.instantiate()
    root.add_child(level)
    var ground := level.get_node("Ground") as TileMapLayer
    var without_collision := OS.get_cmdline_user_args().has("--no-collision")
    if without_collision:
        var tile_set := ground.tile_set.duplicate(true)
        var atlas := tile_set.get_source(0) as TileSetAtlasSource
        atlas.get_tile_data(Vector2i.ZERO, 0).set_collision_polygons_count(0, 0)
        ground.tile_set = tile_set
    var tile_cell := Vector2i(2, 3)
    var occupied := ground.get_cell_source_id(tile_cell) == 0
    var cell_data := ground.get_cell_tile_data(tile_cell)
    var polygon_count := cell_data.get_collision_polygons_count(0) if cell_data else -1
    var tile_center := ground.to_global(ground.map_to_local(tile_cell))
    await physics_frame
    await physics_frame
    var body := CharacterBody2D.new()
    body.collision_layer = 1
    body.collision_mask = 1
    var shape := CollisionShape2D.new()
    var rectangle := RectangleShape2D.new()
    rectangle.size = Vector2(6, 6)
    shape.shape = rectangle
    body.add_child(shape)
    level.add_child(body)
    var start := tile_center + Vector2(0, -20)
    body.global_position = start
    await physics_frame
    var motion := Vector2(0, 40)
    var collision := body.move_and_collide(motion)
    var finish := body.global_position
    var contact_point := collision.get_position() if collision != null else Vector2.ZERO
    var collider_cell := ground.local_to_map(ground.to_local(contact_point + Vector2(0, 1))) if collision != null and collision.get_collider() == ground else Vector2i(-1, -1)
    var contacted := collision != null and collision.get_collider() == ground and collider_cell == tile_cell
    var crossed := start.y < tile_center.y - 8 and finish.y > tile_center.y + 8
    var collider_name := str(collision.get_collider()) if collision != null else "null"
    body.free()
    level.free()
    await process_frame
    if not occupied:
        push_error("CONTACT FIXTURE FAILED: target tile cell=2,3 is not occupied")
        quit(3)
        return
    if without_collision:
        if collision != null:
            push_error("CONTACT FIXTURE FAILED: no-collision control unexpectedly returned collision=%s" % collision)
            quit(3)
            return
        if polygon_count != 0:
            push_error("CONTACT FIXTURE FAILED: scratch tile collision polygon count=%d expected=0" % polygon_count)
            quit(3)
            return
        if contacted or not crossed:
            push_error("CONTACT FIXTURE FAILED: control did not traverse tile region without contact start=%s end=%s collider=%s" % [start, finish, collider_name])
            quit(3)
            return
        push_error("CONTACT ASSERTION FAILED: body motion did not contact level tile at cell=2,3, start=%s end=%s contacted=false collider=null crossed=true" % [start, finish])
        quit(2)
        return
    if polygon_count <= 0:
        push_error("CONTACT FIXTURE FAILED: positive tile polygon count=%d expected>0" % polygon_count)
        quit(3)
        return
    if not contacted or finish.y >= tile_center.y:
        push_error("CONTACT ASSERTION FAILED: body motion did not contact level tile at cell=2,3, start=%s end=%s contacted=false collider=%s crossed=%s" % [start, finish, collider_name, crossed])
        quit(2)
        return
    print("PASS runtime_tile_contact=true cell=2,3, start=%s end=%s contacted=true collider=Ground collider_cell=%s" % [start, finish, collider_cell])
    quit(0)
