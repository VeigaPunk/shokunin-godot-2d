extends SceneTree

func _initialize() -> void:
    call_deferred("run")

func run() -> void:
    var expected := {"profile": {"name": "Ada", "level": 7.0}, "inventory": ["key", "map"], "enabled": true}
    var path := "user://r57-save.json"
    var file := FileAccess.open(path, FileAccess.WRITE)
    if file == null:
        push_error("SAVE ASSERTION FAILED: write open")
        quit(2)
        return
    file.store_string(JSON.stringify(expected))
    expected["level"] = 8.0
    file.close()
    var reopened := FileAccess.open(path, FileAccess.READ)
    if reopened == null:
        push_error("SAVE ASSERTION FAILED: reopen")
        quit(2)
        return
    var text := reopened.get_as_text()
    reopened.close()
    var parsed = JSON.parse_string(text)
    if typeof(parsed) != TYPE_DICTIONARY or parsed != expected:
        push_error("SAVE ASSERTION FAILED: structured roundtrip")
        quit(2)
        return
    if "--corrupt-negative" in OS.get_cmdline_user_args():
        var original_bytes := FileAccess.get_file_as_bytes(path)
        var copy_path := "user://r57-save-corrupt-copy.json"
        var copy := FileAccess.open(copy_path, FileAccess.WRITE)
        copy.store_buffer(original_bytes)
        copy.close()
        if FileAccess.get_file_as_bytes(copy_path) != original_bytes:
            push_error("SAVE ASSERTION FAILED: copied bytes differ before corruption")
            quit(2)
            return
        var corrupt := FileAccess.open(copy_path, FileAccess.WRITE)
        var corrupted_bytes := "{".to_utf8_buffer()
        corrupt.store_buffer(corrupted_bytes)
        corrupt.close()
        var copied_bytes := FileAccess.get_file_as_bytes(copy_path)
        if copied_bytes == original_bytes:
            push_error("SAVE ASSERTION FAILED: corrupted bytes unchanged")
            quit(2)
            return
        var bad := FileAccess.open(copy_path, FileAccess.READ)
        var bad_text := bad.get_as_text()
        bad.close()
        var parser := JSON.new()
        var error := parser.parse(bad_text)
        if error == OK:
            push_error("SAVE ASSERTION FAILED: corrupted copy accepted")
            quit(2)
            return
        if FileAccess.get_file_as_bytes(path) != original_bytes:
            push_error("SAVE ASSERTION FAILED: positive source changed")
            quit(2)
            return
        push_error("SAVE EXPECTED NEGATIVE: malformed JSON rejected signature=JSON_PARSE_ERROR")
        quit(2)
        return
    print("PASS save_roundtrip structured=true reopened=true values_match=true user_path=%s" % ProjectSettings.globalize_path(path))
    quit(0)
