extends SceneTree
func _initialize() -> void:
    var path := "user://slot.json"
    var data := {"schema": 1, "player": {"health": 7, "items": ["key", "potion"]}, "position": Vector2(12.5, -3.0)}
    var f := FileAccess.open(path, FileAccess.WRITE)
    if f == null:
        push_error("open write failed: %s" % error_string(FileAccess.get_open_error())); quit(2); return
    f.store_string(JSON.stringify(data)); f.close()
    var r := FileAccess.open(path, FileAccess.READ)
    if r == null:
        push_error("open read failed"); quit(2); return
    var text := r.get_as_text(); r.close()
    var parsed := JSON.new()
    var err := parsed.parse(text)
    if err != OK:
        push_error("parse failed: %s" % parsed.get_error_message()); quit(2); return
    print("ROUNDTRIP ", parsed.data)
    print("TYPES pos=", typeof(parsed.data.position), " items=", typeof(parsed.data.player.items))
    quit(0)
