extends SceneTree
# r96-boundary probe C — mechanism/falsification probe for the ext_resource id and the
# sub-resource id generator, and for the node unique_id range.
#   The scout's F5 ("ext ids are path-derived and stable" -> REFUTED) tested only
#   *stability within one process*; it never varied the output path, so "path-derived"
#   was never tested at all.  These arms vary exactly that.
# Launch: godot --headless --path proj --script res://r96b_id.gd -- --arm=<arm>
# Arms: finger0 fingerB seqA2 seqAB2 seqAA3 seq2obj extshift
var arm := ""
const BASE := "user://r96b"

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"finger0": _arm_finger0()
		"fingerB": _arm_fingerB()
		"seqA2": _arm_seq(["a"], 2)
		"seqAB2": _arm_seq(["a", "b", "a"], 1)
		"seqAA3": _arm_seq(["a"], 3)
		"seq2obj": _arm_seq2obj()
		"extshift": _arm_extshift()
		"subsame": _arm_subsame()
		"subpath": _arm_subpath()
		"subextra0": _arm_subextra(0)
		"subextra1": _arm_subextra(1)
		"subextra3": _arm_subextra(3)
		"twoext": _arm_twoext()
		"mint_two": _arm_mint_two()
		"subsamepath": _arm_subsamepath()
		"subcontent": _arm_subcontent()
		"extother": _arm_extother()
		_: print("FAIL r96b_id %s reason=unknown_arm" % arm)
	_wipe()
	quit(0)

# ------------------------------------------------------------------ utilities

func _ensure_base() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)

func _wipe() -> void:
	if not DirAccess.dir_exists_absolute(BASE):
		return
	for f in DirAccess.get_files_at(BASE):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(BASE + "/" + f))

func _text(p: String) -> String:
	var f := FileAccess.open(p, FileAccess.READ)
	if f == null:
		return "<none>"
	var t := f.get_as_text()
	f.close()
	return t

func _ids(t: String) -> PackedStringArray:
	var out := PackedStringArray()
	var pos := t.find("id=\"")
	while pos >= 0:
		var rest := t.substr(pos + 4)
		out.append(rest.substr(0, rest.find("\"")))
		pos = t.find("id=\"", pos + 4)
	return out

func _sha_str(s: String) -> String:
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(s.to_utf8_buffer())
	return ctx.finish().hex_encode()

var _parts: PackedStringArray = []

func _p(part: String) -> void:
	_parts.append(part)

func _emit(arm_name: String) -> void:
	print("PASS r96b_id %s %s" % [arm_name, " ".join(_parts)])
	_parts.clear()

# the scout's exact extres construction
func _build() -> Array:
	var grad := Gradient.new()
	grad.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 1, 0, 1)])
	var ext := BASE + "/ext.tres"
	ResourceSaver.save(grad, ext)
	var loaded: Gradient = ResourceLoader.load(ext)
	var mk := func() -> PackedScene:
		var root := Node2D.new()
		root.name = "ExtRoot"
		var line := Line2D.new()
		line.name = "ExtLine"
		line.gradient = loaded
		root.add_child(line)
		line.owner = root
		var ps := PackedScene.new()
		ps.pack(root)
		root.free()
		return ps
	return [mk.call(), mk.call(), loaded]

# ------------------------------------------------------------------ arms

func _arm_finger0() -> void:
	# global sequence fingerprint with NO other work in the process
	var g := Gradient.new()
	var vals := PackedStringArray()
	for i in 8:
		vals.append(str(g.generate_scene_unique_id()))
	print("R96B id finger0 vals=%s" % ",".join(vals))
	_p("vals=%s" % ",".join(vals))
	_emit("finger0")

func _arm_fingerB() -> void:
	_ensure_base()
	var t: Array = _build()
	var loaded: Gradient = t[2]
	var vals := PackedStringArray()
	for i in 8:
		vals.append(str(loaded.generate_scene_unique_id()))
	print("R96B id fingerB vals=%s" % ",".join(vals))
	_p("vals=%s" % ",".join(vals))
	_emit("fingerB")

# save the same PackedScene object along the given path plan (a=pa.tscn, b=pb.tscn)
func _arm_seq(plan: Array, reps: int) -> void:
	_ensure_base()
	var t: Array = _build()
	var ps1: PackedScene = t[0]
	var out := PackedStringArray()
	for r in reps:
		for key in plan:
			var p := BASE + "/p%s.tscn" % key
			var e := ResourceSaver.save(ps1, p)
			out.append("%s:%s/%s" % [key, ",".join(_ids(_text(p))), error_string(e)])
	print("R96B id %s seq=%s" % [arm, " ".join(out)])
	_p("seq=%s" % " ".join(out))
	_emit(arm)

func _arm_seq2obj() -> void:
	# two DIFFERENT PackedScene objects, both saved to the same path A
	_ensure_base()
	var t: Array = _build()
	var ps1: PackedScene = t[0]
	var ps2: PackedScene = t[1]
	var p := BASE + "/pa.tscn"
	var e1 := ResourceSaver.save(ps1, p)
	var id1 := ",".join(_ids(_text(p)))
	var e2 := ResourceSaver.save(ps2, p)
	var id2 := ",".join(_ids(_text(p)))
	print("R96B id seq2obj obj1=%s/%s obj2=%s/%s" % [id1, error_string(e1), id2, error_string(e2)])
	_p("obj1=%s obj2=%s" % [id1, id2])
	_emit("seq2obj")

func _arm_extshift() -> void:
	# draw 3 global ids first, then save: does the ext id shift with the global draw count?
	_ensure_base()
	var t: Array = _build()
	var ps1: PackedScene = t[0]
	var loaded: Gradient = t[2]
	var pre := PackedStringArray()
	for i in 3:
		pre.append(str(loaded.generate_scene_unique_id()))
	var p := BASE + "/pa.tscn"
	var e := ResourceSaver.save(ps1, p)
	var id := ",".join(_ids(_text(p)))
	print("R96B id extshift pre=%s ext_id=%s/%s" % [",".join(pre), id, error_string(e)])
	_p("pre=%s ext_id=%s" % [",".join(pre), id])
	_emit("extshift")

# ---------------------------------------------------------------- sub-id arms

func _mk_scene() -> PackedScene:
	var root := Node2D.new()
	root.name = "SubRoot"
	var line := Line2D.new()
	line.name = "SubLine"
	var g := Gradient.new()
	g.colors = PackedColorArray([Color(0.1, 0.2, 0.3, 1), Color(0.4, 0.5, 0.6, 1)])
	line.gradient = g
	root.add_child(line)
	line.owner = root
	var ps := PackedScene.new()
	ps.pack(root)
	root.free()
	return ps

func _arm_subsame() -> void:
	_ensure_base()
	var ps: PackedScene = _mk_scene()
	var p := BASE + "/pa.tscn"
	var e1 := ResourceSaver.save(ps, p)
	var id1 := ",".join(_ids(_text(p)))
	var e2 := ResourceSaver.save(ps, p)
	var id2 := ",".join(_ids(_text(p)))
	print("R96B id subsame id1=%s id2=%s" % [id1, id2])
	_p("id1=%s id2=%s" % [id1, id2])
	_emit("subsame")

func _arm_subpath() -> void:
	_ensure_base()
	var ps: PackedScene = _mk_scene()
	var out := PackedStringArray()
	for key in ["a", "b", "a"]:
		var p := BASE + "/p%s.tscn" % key
		ResourceSaver.save(ps, p)
		out.append("%s:%s" % [key, ",".join(_ids(_text(p)))])
	print("R96B id subpath seq=%s" % " ".join(out))
	_p("seq=%s" % " ".join(out))
	_emit("subpath")

func _arm_subextra(extra: int) -> void:
	_ensure_base()
	for i in extra:
		var _unused := Gradient.new()
	var ps: PackedScene = _mk_scene()
	var p := BASE + "/sp.tscn"
	ResourceSaver.save(ps, p)
	var id := ",".join(_ids(_text(p)))
	print("R96B id subextra extra=%d id=%s" % [extra, id])
	_p("extra=%d id=%s" % [extra, id])
	_emit("subextra%d" % extra)

func _arm_twoext() -> void:
	_ensure_base()
	var g1 := Gradient.new()
	g1.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 1, 0, 1)])
	var g2 := Gradient.new()
	g2.colors = PackedColorArray([Color(0, 0, 1, 1), Color(1, 1, 0, 1)])
	ResourceSaver.save(g1, BASE + "/ex1.tres")
	ResourceSaver.save(g2, BASE + "/ex2.tres")
	var l1: Gradient = ResourceLoader.load(BASE + "/ex1.tres")
	var l2: Gradient = ResourceLoader.load(BASE + "/ex2.tres")
	var root := Node2D.new()
	root.name = "TwoRoot"
	var a := Line2D.new()
	a.name = "A"
	a.gradient = l1
	root.add_child(a)
	a.owner = root
	var b := Line2D.new()
	b.name = "B"
	b.gradient = l2
	root.add_child(b)
	b.owner = root
	var ps := PackedScene.new()
	ps.pack(root)
	root.free()
	var out := PackedStringArray()
	for key in ["a", "b", "a"]:
		var p := BASE + "/tw%s.tscn" % key
		ResourceSaver.save(ps, p)
		out.append("%s:%s" % [key, ",".join(_ids(_text(p)))])
	print("R96B id twoext seq=%s" % " ".join(out))
	print("R96B id twoext text=%s" % _text(BASE + "/twa.tscn").replace("\n", "|"))
	_p("seq=%s" % " ".join(out))
	_emit("twoext")

# ------------------------------------------------- mint-law arms (path vs sequence)

func _mk_scene_col(c: Color) -> PackedScene:
	var root := Node2D.new()
	root.name = "SubRoot"
	var line := Line2D.new()
	line.name = "SubLine"
	var g := Gradient.new()
	g.colors = PackedColorArray([c, Color(0, 0, 0, 1)])
	line.gradient = g
	root.add_child(line)
	line.owner = root
	var ps := PackedScene.new()
	ps.pack(root)
	root.free()
	return ps

func _arm_mint_two() -> void:
	_ensure_base()
	var out := PackedStringArray()
	var plan := [["pa", Color(0.1, 0.2, 0.3, 1)], ["sp", Color(0.1, 0.2, 0.3, 1)],
		["pa", Color(0.1, 0.2, 0.3, 1)], ["sp", Color(0.1, 0.2, 0.3, 1)]]
	for step in plan:
		var ps: PackedScene = _mk_scene_col(step[1])
		var p := BASE + "/%s.tscn" % step[0]
		ResourceSaver.save(ps, p)
		out.append("%s:%s" % [step[0], ",".join(_ids(_text(p)))])
	print("R96B id mint_two seq=%s" % " ".join(out))
	_p("seq=%s" % " ".join(out))
	_emit("mint_two")

func _arm_subsamepath() -> void:
	_ensure_base()
	var out := PackedStringArray()
	for i in 2:
		var ps: PackedScene = _mk_scene()
		var p := BASE + "/sp.tscn"
		ResourceSaver.save(ps, p)
		out.append("m%d:%s" % [i, ",".join(_ids(_text(p)))])
	print("R96B id subsamepath seq=%s" % " ".join(out))
	_p("seq=%s" % " ".join(out))
	_emit("subsamepath")

func _arm_subcontent() -> void:
	_ensure_base()
	var ps: PackedScene = _mk_scene_col(Color(0.9, 0.8, 0.7, 1))
	var p := BASE + "/sp.tscn"
	ResourceSaver.save(ps, p)
	var id := ",".join(_ids(_text(p)))
	print("R96B id subcontent id=%s" % id)
	_p("id=%s" % id)
	_emit("subcontent")

func _arm_extother() -> void:
	# same OUTPUT path (pa.tscn) as the seqA2/seq2obj arms, but the referenced external
	# resource is a different .tres file with different content
	_ensure_base()
	var g := Gradient.new()
	g.colors = PackedColorArray([Color(0.9, 0.1, 0.9, 1), Color(0.2, 0.2, 0.2, 1)])
	ResourceSaver.save(g, BASE + "/other.tres")
	var loaded: Gradient = ResourceLoader.load(BASE + "/other.tres")
	var root := Node2D.new()
	root.name = "ExtRoot"
	var line := Line2D.new()
	line.name = "ExtLine"
	line.gradient = loaded
	root.add_child(line)
	line.owner = root
	var ps := PackedScene.new()
	ps.pack(root)
	root.free()
	var p := BASE + "/pa.tscn"
	ResourceSaver.save(ps, p)
	var id := ",".join(_ids(_text(p)))
	print("R96B id extother id=%s text=%s" % [id, _text(p).replace("\n", "|")])
	_p("id=%s" % id)
	_emit("extother")
