extends SceneTree

func _initialize():
    var path = "user://r57-critic.json"
    var source = {"profile": {"name": "Ada", "level": 7.0}, "items": ["key", "map"], "enabled": true}
    var f = FileAccess.open(path, FileAccess.WRITE)
    f.store_string(JSON.stringify(source))
    f.close()
    var f2 = FileAccess.open(path, FileAccess.READ)
    var bytes = f2.get_as_text()
    f2.close()
    var parsed = JSON.new()
    var parse_error = parsed.parse(bytes)
    if parse_error != OK or parsed.data != source:
        print("CRITIC_POSITIVE_FAIL error=%s data=%s" % [parse_error, str(parsed.data)])
        quit(1)
    print("CRITIC_POSITIVE_PASS reopened=true structured_match=true")
    var copy = "user://r57-critic-corrupt.json"
    var cf = FileAccess.open(copy, FileAccess.WRITE)
    cf.store_string(bytes.left(bytes.length() - 1) + "!")
    cf.close()
    var rf = FileAccess.open(copy, FileAccess.READ)
    var damaged = rf.get_as_text()
    rf.close()
    var bad = JSON.new()
    var bad_error = bad.parse(damaged)
    if bad_error == OK:
        print("CRITIC_NEGATIVE_FAIL malformed bytes parsed data=%s" % str(bad.data))
        quit(2)
    print("CRITIC_NEGATIVE_PASS corrupted_copy_rejected=true error=%s" % bad_error)
    quit(0)
