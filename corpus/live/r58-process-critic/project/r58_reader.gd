extends SceneTree
func _initialize():
 var p="user://r58.json"
 if "--missing" in OS.get_cmdline_user_args(): p="user://missing.json"
 var f=FileAccess.open(p, FileAccess.READ)
 if f==null:
  push_error("R58 REJECT missing=%s" % p)
  quit(2); return
 var parsed=JSON.parse_string(f.get_as_text()); f.close()
 var want={"profile":{"name":"Ada","level":7.0},"inventory":["key","map"],"enabled":true}
 if parsed != want:
  push_error("R58 REJECT structure mismatch")
  quit(2); return
 print("READER pid=%s path=%s structure=true" % [OS.get_process_id(), ProjectSettings.globalize_path(p)])
 quit(0)
