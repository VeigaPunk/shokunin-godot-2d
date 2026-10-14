extends SceneTree
func _initialize() -> void:
    var path := "user://r57-save.json"
    if "--missing" in OS.get_cmdline_user_args():
        path = "user://r58-absent.json"
    var file := FileAccess.open(path, FileAccess.READ)
    if file == null:
        if "--missing" in OS.get_cmdline_user_args():
            push_error("EXPECTED NEGATIVE: reader rejected missing save")
            quit(2)
        else:
            push_error("READER ASSERTION FAILED: positive save absent")
            quit(2)
        return
    var data = JSON.parse_string(file.get_as_text())
    file.close()
    var expected := {"profile": {"name": "Ada", "level": 7.0}, "inventory": ["key", "map"], "enabled": true}
    if data != expected:
        push_error("READER ASSERTION FAILED: structure mismatch")
        quit(2)
        return
    if "--missing" in OS.get_cmdline_user_args():
        push_error("READER ASSERTION FAILED: missing save unexpectedly opened")
        quit(2)
        return
    print("PASS independent_reader structured=true")
    quit(0)
