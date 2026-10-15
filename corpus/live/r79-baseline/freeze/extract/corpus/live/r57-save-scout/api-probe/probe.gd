extends SceneTree
func _initialize():
    var path := "user://r57-save-scout-probe.json"
    var payload := {"label": "scout", "count": 7, "nested": {"ok": true}, "items": ["a", 3]}
    var writer := FileAccess.open(path, FileAccess.WRITE)
    if writer == null:
        print("FAIL open-write ", FileAccess.get_open_error())
        quit(1); return
    writer.store_string(JSON.stringify(payload))
    writer = null
    var reader := FileAccess.open(path, FileAccess.READ)
    if reader == null:
        print("FAIL open-read ", FileAccess.get_open_error())
        quit(1); return
    var bytes := reader.get_as_text()
    reader = null
    var parsed := JSON.new()
    var err := parsed.parse(bytes)
    if err != OK:
        print("FAIL parse ", parsed.get_error_message(), " line=", parsed.get_error_line())
        quit(1); return
    var expected := {"label": "scout", "count": 7.0, "nested": {"ok": true}, "items": ["a", 3.0]}
    if parsed.data != expected:
        print("FAIL values ", parsed.data)
        quit(1); return
    print("PASS save_load reopened=true structured=true path=", path)
    var corrupt_path := "user://r57-save-scout-corrupt.json"
    var corrupt := FileAccess.open(corrupt_path, FileAccess.WRITE)
    corrupt.store_string(bytes)
    corrupt = null
    var copied := FileAccess.open(corrupt_path, FileAccess.READ)
    var copied_bytes := copied.get_as_text()
    copied = null
    var alter := FileAccess.open(corrupt_path, FileAccess.WRITE)
    alter.store_string(copied_bytes + "\n{broken")
    corrupt = null
    var reread := FileAccess.open(corrupt_path, FileAccess.READ)
    var corrupted_bytes := reread.get_as_text()
    reread = null
    var bad := JSON.new()
    var bad_err := bad.parse(corrupted_bytes)
    if bad_err == OK:
        print("FAIL corrupt accepted")
        quit(1); return
    print("EXPECTED_NEGATIVE corrupt-json-rejected parse_error=", bad.get_error_message(), " line=", bad.get_error_line())
    quit(0)
