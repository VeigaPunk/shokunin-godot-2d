extends SceneTree
func _initialize() -> void:
    var f := FileAccess.open("user://corrupt.json", FileAccess.READ)
    if f == null:
        push_error("open failed"); quit(2); return
    var bytes := f.get_buffer(f.get_length()); f.close()
    var parser := JSON.new()
    var err := parser.parse(bytes.get_string_from_utf8())
    print("CORRUPT bytes=", bytes.size(), " parse_error=", err, " line=", parser.get_error_line(), " message=", parser.get_error_message())
    if err == OK:
        push_error("corrupt data unexpectedly parsed"); quit(2); return
    quit(0)
