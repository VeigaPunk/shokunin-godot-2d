extends SceneTree
# r96-boundary probe E — tick-phase / scheduler attack (the r95 lesson: anything claimed
# stable must be re-checked at other tick phases).  Saves the same two constructions at
# 0/1/2/5/30 physics frames and at 0/1/2/5/30 process frames, and prints the ext id,
# sub id, the global generate_scene_unique_id() fingerprint and the pinned sha.
#
# Launch: godot --headless --path proj --script res://r96b_phase.gd -- --arm=ph5
# Arms: ph0 ph1 ph2 ph5 ph30 (physics frames) | pph0 pph1 pph2 pph5 pph30 (process frames)
var arm := ""
var k := 0
var use_process := false
const BASE := "user://r96b"

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	if arm.begins_with("pph"):
		use_process = true
		k = int(arm.substr(3))
	elif arm.begins_with("ph"):
		k = int(arm.substr(2))
	_run.call_deferred()

func _run() -> void:
	for i in k:
		if use_process:
			await process_frame
		else:
			await physics_frame
	DirAccess.make_dir_recursive_absolute(BASE)
	# --- ext scene, saved at this tick phase
	var grad := Gradient.new()
	grad.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 1, 0, 1)])
	ResourceSaver.save(grad, BASE + "/phext.tres")
	var loaded: Gradient = ResourceLoader.load(BASE + "/phext.tres")
	var root := Node2D.new()
	root.name = "PhaseRoot"
	var line := Line2D.new()
	line.name = "PhaseLine"
	line.gradient = loaded
	root.add_child(line)
	line.owner = root
	var ps := PackedScene.new()
	ps.pack(root)
	root.free()
	var p := BASE + "/ph.tscn"
	var e := ResourceSaver.save(ps, p)
	var text := _text(p)
	var ext_id := _ids(text)
	# --- sub scene, saved at this tick phase
	var root2 := Node2D.new()
	root2.name = "PhaseSub"
	var line2 := Line2D.new()
	line2.name = "PhaseSubLine"
	var g2 := Gradient.new()
	g2.colors = PackedColorArray([Color(0.1, 0.2, 0.3, 1), Color(0.4, 0.5, 0.6, 1)])
	line2.gradient = g2
	root2.add_child(line2)
	line2.owner = root2
	var ps2 := PackedScene.new()
	ps2.pack(root2)
	root2.free()
	var p2 := BASE + "/ph2.tscn"
	var e2 := ResourceSaver.save(ps2, p2)
	var sub_id := _ids(_text(p2))
	# --- global id fingerprint at this tick phase
	var gen1 := str(loaded.generate_scene_unique_id())
	# --- pinned-bundle save (the scout's recipe) at this tick phase
	var d: Dictionary = ps._get_bundled_scene()
	d["node_ids"] = [111111, 222222]
	var pin := PackedScene.new()
	pin._set_bundled_scene(d)
	var p3 := BASE + "/phpin.tscn"
	var e3 := ResourceSaver.save(pin, p3)
	var pinned := _text(p3)
	print("R96B phase %s k=%d use_process=%s ext_id=%s sub_id=%s gen1=%s pinned_sha=%s" % [
		arm, k, _b(use_process), ext_id, sub_id, gen1, _sha_str(pinned)])
	print("PASS r96b_phase %s k=%d use_process=%s ext_id=%s sub_id=%s gen1=%s save=%s save2=%s save3=%s uonly_sha=%s pinned_sha=%s pinned_uonly=%s" % [
		arm, k, _b(use_process), ext_id, sub_id, gen1, error_string(e), error_string(e2), error_string(e3),
		_sha_str(_mask_unique(text)), _sha_str(pinned), _sha_str(_mask_unique(pinned))])
	for f in DirAccess.get_files_at(BASE):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(BASE + "/" + f))
	quit(0)

func _b(v: bool) -> String:
	return "true" if v else "false"

func _text(p: String) -> String:
	var f := FileAccess.open(p, FileAccess.READ)
	if f == null:
		return "<none>"
	var t := f.get_as_text()
	f.close()
	return t

func _ids(t: String) -> String:
	var out := PackedStringArray()
	var pos := t.find("id=\"")
	while pos >= 0:
		var rest := t.substr(pos + 4)
		out.append(rest.substr(0, rest.find("\"")))
		pos = t.find("id=\"", pos + 4)
	return ",".join(out)

func _mask_unique(t: String) -> String:
	var out := t
	var pos := out.find("unique_id=")
	while pos >= 0:
		var end := pos + 10
		while end < out.length() and out[end] >= "0" and out[end] <= "9":
			end += 1
		out = out.substr(0, pos + 10) + "#" + out.substr(end, out.length() - end)
		pos = out.find("unique_id=", pos + 11)
	return out

func _sha_str(s: String) -> String:
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(s.to_utf8_buffer())
	return ctx.finish().hex_encode()
