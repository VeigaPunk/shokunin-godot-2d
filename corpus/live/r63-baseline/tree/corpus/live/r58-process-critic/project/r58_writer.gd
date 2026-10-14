extends SceneTree
func _initialize():
 var f=FileAccess.open("user://r58.json", FileAccess.WRITE)
 f.store_string(JSON.stringify({"profile":{"name":"Ada","level":7.0},"inventory":["key","map"],"enabled":true}))
 f.close()
 print("WRITER pid=%s path=%s" % [OS.get_process_id(), ProjectSettings.globalize_path("user://r58.json")])
 quit(0)
