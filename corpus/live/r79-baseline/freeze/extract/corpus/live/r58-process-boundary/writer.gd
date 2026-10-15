extends SceneTree
func _initialize():
 var f=FileAccess.open("user://boundary.json", FileAccess.WRITE)
 f.store_string("{\"run\":\"writer\"}")
 f.close()
 print("WRITER wrote=" + ProjectSettings.globalize_path("user://boundary.json"))
 quit(0)
