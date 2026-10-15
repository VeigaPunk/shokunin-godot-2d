extends SceneTree
func _initialize():
 var p="user://boundary.json"
 if not FileAccess.file_exists(p):
  push_error("READER_MISSING " + ProjectSettings.globalize_path(p))
  quit(2)
  return
 var f=FileAccess.open(p, FileAccess.READ)
 var t=f.get_as_text()
 f.close()
 print("READER content=" + t + " path=" + ProjectSettings.globalize_path(p))
 quit(0 if t == "{\"run\":\"writer\"}" else 3)
