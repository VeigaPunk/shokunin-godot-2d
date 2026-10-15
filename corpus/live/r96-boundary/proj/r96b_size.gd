extends SceneTree
# r96-boundary probe F — quantifies the scout row key `size_in_190_200` in
# r96_scene_io_pack_basic (2-node scene, random unique_id digit widths).
# Launch: godot --headless --path proj --script res://r96b_size.gd -- --arm=size
var arm := ""
const BASE := "user://r96b"

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var p := BASE + "/sz.tscn"
	var n := 400
	var sizes := {}
	var lens := {}
	var out_of_range := 0
	var smin := 1 << 30
	var smax := -1
	var short_ids := 0
	for i in n:
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
		root.free()
		ResourceSaver.save(ps, p)
		var f := FileAccess.open(p, FileAccess.READ)
		var size := f.get_length()
		var text := f.get_as_text()
		f.close()
		var ids := PackedStringArray()
		var pos := text.find("unique_id=")
		while pos >= 0:
			var end := pos + 10
			while end < text.length() and text[end] >= "0" and text[end] <= "9":
				end += 1
			ids.append(text.substr(pos + 10, end - pos - 10))
			pos = text.find("unique_id=", pos + 11)
		sizes[size] = int(sizes.get(size, 0)) + 1
		var l1 := ids[0].length() if ids.size() > 0 else -1
		var l2 := ids[1].length() if ids.size() > 1 else -1
		lens["%d,%d" % [l1, l2]] = int(lens.get("%d,%d" % [l1, l2], 0)) + 1
		if ids.size() != 2:
			short_ids += 1
		if size < 190 or size > 200:
			out_of_range += 1
		smin = mini(smin, size)
		smax = maxi(smax, size)
	var size_keys := PackedStringArray()
	var ks := sizes.keys()
	ks.sort()
	for k in ks:
		size_keys.append("%d:%d" % [k, sizes[k]])
	var len_keys := PackedStringArray()
	var lk := lens.keys()
	lk.sort()
	for k in lk:
		len_keys.append("%s:%d" % [k, lens[k]])
	print("R96B size n=%d out_of_range=%d min=%d max=%d short_ids=%d" % [n, out_of_range, smin, smax, short_ids])
	print("R96B size sizes=%s" % ",".join(size_keys))
	print("R96B size lens=%s" % ",".join(len_keys))
	print("PASS r96b_size %s n=%d out_of_range=%d min=%d max=%d sizes=%s lens=%s" % [
		arm, n, out_of_range, smin, smax, ",".join(size_keys), ",".join(len_keys)])
	for f in DirAccess.get_files_at(BASE):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(BASE + "/" + f))
	quit(0)
