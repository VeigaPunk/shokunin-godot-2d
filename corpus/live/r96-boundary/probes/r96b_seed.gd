extends SceneTree
# r96-boundary probe G — mechanism: is Resource.generate_scene_unique_id() seeded by the
# resource's path?  (the r96 scout modelled the ids as a "deterministic per-process
# generator sequence"; probe C showed the SAVED ids are a function of the output path.)
# Launch: godot --headless --path proj --script res://r96b_seed.gd -- --arm=seedcheck
var arm := ""
const BASE := "user://r96b"

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	match arm:
		"seedcheck": _arm_seedcheck()
		"fresh2": _arm_fresh2()
		_: print("FAIL r96b_seed %s reason=unknown_arm" % arm)
	for f in DirAccess.get_files_at(BASE):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(BASE + "/" + f))
	quit(0)

func _draws(res: Resource, n: int) -> String:
	var out := PackedStringArray()
	for i in n:
		out.append(str(res.generate_scene_unique_id()))
	return ",".join(out)

func _mkgrad(p: String, c: Color) -> void:
	var g := Gradient.new()
	g.colors = PackedColorArray([c, Color(0, 0, 0, 1)])
	ResourceSaver.save(g, p)

func _arm_seedcheck() -> void:
	_mkgrad(BASE + "/seed.tres", Color(1, 0, 0, 1))
	_mkgrad(BASE + "/seed2.tres", Color(0, 1, 0, 1))
	var a: Gradient = ResourceLoader.load(BASE + "/seed.tres")
	var ga := _draws(a, 4)
	var b: Gradient = ResourceLoader.load(BASE + "/seed.tres")
	var gb := _draws(b, 4)
	var c: Gradient = ResourceLoader.load(BASE + "/seed2.tres")
	var gc := _draws(c, 4)
	var d := Gradient.new()
	var gd := _draws(d, 4)
	print("R96B seed seedcheck A=%s B=%s C=%s D=%s" % [ga, gb, gc, gd])
	print("PASS r96b_seed seedcheck A=%s B=%s C=%s D=%s A_eq_B=%s A_eq_C=%s A_eq_D=%s" % [
		ga, gb, gc, gd, str(ga == gb), str(ga == gc), str(ga == gd)])
	a = null
	b = null
	c = null
	d = null

func _arm_fresh2() -> void:
	var d1 := Gradient.new()
	var g1 := _draws(d1, 4)
	var d2 := Gradient.new()
	var g2 := _draws(d2, 4)
	print("R96B seed fresh2 g1=%s g2=%s" % [g1, g2])
	print("PASS r96b_seed fresh2 g1=%s g2=%s eq=%s" % [g1, g2, str(g1 == g2)])
	d1 = null
	d2 = null
