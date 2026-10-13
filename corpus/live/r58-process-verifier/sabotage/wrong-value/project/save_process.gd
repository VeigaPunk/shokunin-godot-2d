extends SceneTree

const SAVE_PATH := "user://r58-process-save.json"
const EXPECTED := {"profile": {"name": "Wrong", "level": 7.0}, "inventory": ["key", "map"], "enabled": true}

func _initialize() -> void:
    call_deferred("run")

func run() -> void:
    var args := OS.get_cmdline_user_args()
    var missing := "--missing" in args
    var reader := "--reader" in args or missing
    var path := "user://r58-process-missing.json" if missing else SAVE_PATH
    if not reader:
        var output := FileAccess.open(path, FileAccess.WRITE)
        if output == null:
            push_error("SAVE PROCESS ASSERTION FAILED: writer open")
            quit(2)
            return
        output.store_string(JSON.stringify(EXPECTED))
        output.close()
        print("PASS save_process writer=true pid=%d path=%s" % [OS.get_process_id(), ProjectSettings.globalize_path(path)])
        quit(0)
        return
    var input := FileAccess.open(path, FileAccess.READ)
    if missing:
        if input != null:
            input.close()
            push_error("SAVE PROCESS ASSERTION FAILED: missing file existed")
            quit(2)
            return
        print("PASS save_process missing=true pid=%d path=%s" % [OS.get_process_id(), ProjectSettings.globalize_path(path)])
        push_error("SAVE PROCESS EXPECTED NEGATIVE: missing file rejected signature=FILE_NOT_FOUND,")
        quit(2)
        return
    if input == null:
        push_error("SAVE PROCESS ASSERTION FAILED: reader open")
        quit(2)
        return
    var value = JSON.parse_string(input.get_as_text())
    input.close()
    if typeof(value) != TYPE_DICTIONARY or value != EXPECTED:
        push_error("SAVE PROCESS ASSERTION FAILED: independent reader mismatch")
        quit(2)
        return
    print("PASS save_process reader=true pid=%d path=%s values_match=true" % [OS.get_process_id(), ProjectSettings.globalize_path(path)])
    quit(0)
