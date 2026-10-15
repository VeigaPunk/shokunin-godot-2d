extends SceneTree

func _initialize() -> void:
	var out: Array = []
	for m in ClassDB.class_get_method_list("CanvasItem", true):
		var nm := str(m.get("name"))
		if nm.begins_with("draw_"):
			var sig: Array = []
			for a in m.get("args", []):
				sig.append("%s:%d" % [str(a.get("name")), int(a.get("type"))])
			out.append("%s(%s)->%d" % [nm, ",".join(sig), int(m.get("return", {}).get("type", -1))])
	print("SIGS " + "|".join(out))
	quit()
