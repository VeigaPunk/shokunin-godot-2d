extends SceneTree
# r96 scout DISCOVERY probe #9 — node unique_id variance across fresh processes
# (same frozen construction as the pack_basic cell, raw values printed on purpose).
var arm := ""
const BASE := "user://r96"

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var root := Node2D.new()
	root.name = "Root"
	root.position = Vector2(10, 20)
	var child := Node2D.new()
	child.name = "Child"
	child.position = Vector2(3, 4)
	root.add_child(child)
	child.owner = root
	var ps := PackedScene.new()
	ps.pack(root)
	var p := BASE + "/uidvar.tscn"
	var e := ResourceSaver.save(ps, p)
	var f := FileAccess.open(p, FileAccess.READ)
	var text := f.get_as_text()
	f.close()
	var ids := PackedStringArray()
	var pos := text.find("unique_id=")
	while pos >= 0:
		var end := pos + 10
		while end < text.length() and text[end] >= "0" and text[end] <= "9":
			end += 1
		ids.append(text.substr(pos + 10, end - pos - 10))
		pos = text.find("unique_id=", end)
	print("R96 uidvar save=%s size=%d bytes ids=%s widths=%s" % [
		error_string(e), text.length(), ",".join(ids),
		"%d,%d" % [ids[0].length(), ids[1].length()]])
	root.free()
	for g in DirAccess.get_files_at(BASE):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(BASE + "/" + g))
	quit(0)
