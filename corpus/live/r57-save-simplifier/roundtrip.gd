extends SceneTree

func _initialize() -> void:
    var source := {"name": "Ada", "inventory": ["key", "map"], "stats": {"level": 3, "active": true}}
    var path := "user://roundtrip.json"
    var writer := FileAccess.open(path, FileAccess.WRITE)
    assert(writer != null)
    writer.store_string(JSON.stringify(source))
    writer.close()
    var reader := FileAccess.open(path, FileAccess.READ)
    assert(reader != null)
    var reopened: Variant = JSON.parse_string(reader.get_as_text())
    reader.close()
    assert(reopened == source)
    print("PASS save_round_trip reopened=true structured_values_equal=true")
    quit()
