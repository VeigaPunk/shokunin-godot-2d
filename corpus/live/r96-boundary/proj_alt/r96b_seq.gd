extends SceneTree
# r96-boundary probe A — attacks the r96 scout's ext-resource claims:
#   scout §3.5/F5: "ext_resource ids are re-minted on every save call" (measured within ONE process)
#   scout hazard 2: "a scene that references any external resource can never be byte-stable"
#   scout §3.4:    "unique_id is the ONLY source of variance in a scene with no ext resources"
# The scout's own extres diagnostic MASKS the ext id before printing (`t1.replace(id1, "#")`),
# so its 9 receipts could not see a cross-process ext-id difference.  This probe masks ONLY
# unique_id (and, in a second view, the sub-resource ids), leaving the ext id visible.
#
# Launch: godot --headless --path proj --script res://r96b_seq.gd -- --arm=<arm>
# Arms: extseq extpin extbundle extgen
var arm := ""
const BASE := "user://r96b"

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"extseq": _arm_extseq()
		"extpin": _arm_extpin()
		"extbundle": _arm_extbundle()
		"extgen": _arm_extgen()
		_: print("FAIL r96b_seq %s reason=unknown_arm" % arm)
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

func _sha_str(s: String) -> String:
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(s.to_utf8_buffer())
	return ctx.finish().hex_encode()

func _text(p: String) -> String:
	var f := FileAccess.open(p, FileAccess.READ)
	if f == null:
		return "<none>"
	var t := f.get_as_text()
	f.close()
	return t

func _ids(t: String) -> PackedStringArray:
	# every id="..." value in file order (ext_resource and sub_resource alike)
	var out := PackedStringArray()
	var pos := t.find("id=\"")
	while pos >= 0:
		var rest := t.substr(pos + 4)
		out.append(rest.substr(0, rest.find("\"")))
		pos = t.find("id=\"", pos + 4)
	return out

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

func _mask_subids(t: String) -> String:
	# mask id="X" for sub-resource style ids (not the 1_xxx ext ids)
	var out := t
	var pos := out.find("id=\"")
	while pos >= 0:
		var rest := out.substr(pos + 4)
		var val := rest.substr(0, rest.find("\""))
		if val.begins_with("1_"):
			pos = out.find("id=\"", pos + 4)
			continue
		out = out.substr(0, pos + 4) + "#" + out.substr(pos + 4 + val.length(), out.length() - pos - 4 - val.length())
		pos = out.find("id=\"", pos + 4)
	return out

func _join(a: PackedStringArray) -> String:
	return ",".join(a)

func _b(v: bool) -> String:
	return "true" if v else "false"

var _parts: PackedStringArray = []

func _p(part: String) -> void:
	_parts.append(part)

func _emit(arm_name: String) -> void:
	print("PASS r96b_seq %s %s" % [arm_name, " ".join(_parts)])
	_parts.clear()

# ------------------------------------------------------------------ construction

# byte-for-byte the scout's `_arm_extres` construction (one Gradient .tres + two identical scenes)
func _build() -> Array:
	var grad := Gradient.new()
	grad.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 1, 0, 1)])
	var ext := BASE + "/ext.tres"
	var e_ext := ResourceSaver.save(grad, ext)
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
	return [mk.call(), mk.call(), loaded, e_ext]

# ------------------------------------------------------------------ arms

func _arm_extseq() -> void:
	_ensure_base()
	var t: Array = _build()
	var ps1: PackedScene = t[0]
	var ps2: PackedScene = t[1]
	var p1 := BASE + "/x1.tscn"
	var p2 := BASE + "/x2.tscn"
	var p1b := BASE + "/x1b.tscn"
	var e1 := ResourceSaver.save(ps1, p1)
	var e2 := ResourceSaver.save(ps2, p2)
	var e1b := ResourceSaver.save(ps1, p1b)
	var t1 := _text(p1)
	var ids1 := _ids(t1)
	var ids2 := _ids(_text(p2))
	var ids1b := _ids(_text(p1b))
	var u_only := _sha_str(_mask_unique(t1))
	print("R96B seq extseq ids1=%s ids2=%s ids1b=%s" % [_join(ids1), _join(ids2), _join(ids1b)])
	print("R96B seq extseq text1_uonly=%s" % _mask_unique(t1).replace("\n", "|"))
	_p("save=%s save2=%s save_same_obj=%s ext_ids1=%s ext_ids2=%s ext_ids1b=%s sha_uonly=%s sha_usub=%s" % [
		error_string(e1), error_string(e2), error_string(e1b),
		_join(ids1), _join(ids2), _join(ids1b),
		u_only, _sha_str(_mask_subids(_mask_unique(t1)))])
	_emit("extseq")

func _arm_extpin() -> void:
	# pin the bundle node_ids, keep the ext resource; two identical builds in this process
	_ensure_base()
	var t: Array = _build()
	var ps1: PackedScene = t[0]
	var ps2: PackedScene = t[1]
	var mk_pin := func(ps: PackedScene) -> PackedScene:
		var d: Dictionary = ps._get_bundled_scene()
		d["node_ids"] = [111111, 222222]
		var out := PackedScene.new()
		out._set_bundled_scene(d)
		return out
	var a: PackedScene = mk_pin.call(ps1)
	var b: PackedScene = mk_pin.call(ps2)
	var p1 := BASE + "/pin_ext1.tscn"
	var p2 := BASE + "/pin_ext2.tscn"
	var e1 := ResourceSaver.save(a, p1)
	var e2 := ResourceSaver.save(b, p2)
	var t1 := _text(p1)
	var t2 := _text(p2)
	var ids1 := _ids(t1)
	var ids2 := _ids(t2)
	print("R96B seq extpin text1_uonly=%s" % _mask_unique(t1).replace("\n", "|"))
	print("R96B seq extpin ids1=%s ids2=%s same_process_same=%s" % [_join(ids1), _join(ids2), _b(t1 == t2)])
	_p("save=%s save2=%s ext_ids1=%s ext_ids2=%s sha_uonly=%s two_builds_same_text=%s unique_pinned=%s" % [
		error_string(e1), error_string(e2), _join(ids1), _join(ids2),
		_sha_str(_mask_unique(t1)), _b(t1 == t2),
		_b("unique_id=111111" in t1 and "unique_id=222222" in t1)])
	_emit("extpin")

func _arm_extbundle() -> void:
	# FLAG_BUNDLE_RESOURCES inlines the ext resource; pin node_ids.  Is the inlined
	# sub-resource id a deterministic sequence draw (=> cross-process byte-stable)?
	_ensure_base()
	var t: Array = _build()
	var ps1: PackedScene = t[0]
	var d: Dictionary = ps1._get_bundled_scene()
	d["node_ids"] = [111111, 222222]
	var a := PackedScene.new()
	a._set_bundled_scene(d)
	var p1 := BASE + "/bundle1.tscn"
	var e1 := ResourceSaver.save(a, p1, ResourceSaver.FLAG_BUNDLE_RESOURCES)
	var t1 := _text(p1)
	var ids1 := _ids(t1)
	print("R96B seq extbundle text1_uonly=%s" % _mask_unique(t1).replace("\n", "|"))
	print("R96B seq extbundle ids1=%s ext_line=%s sub_line=%s" % [
		_join(ids1), _b("ext_resource" in t1), _b("sub_resource" in t1)])
	_p("save=%s ids1=%s sha_uonly=%s sha_u_sub=%s ext_line=%s sub_line=%s unique_pinned=%s" % [
		error_string(e1), _join(ids1), _sha_str(_mask_unique(t1)),
		_sha_str(_mask_subids(_mask_unique(t1))), _b("ext_resource" in t1), _b("sub_resource" in t1),
		_b("unique_id=111111" in t1 and "unique_id=222222" in t1)])
	_emit("extbundle")

func _arm_extgen() -> void:
	# draw-sequence structure: interleave Resource.generate_scene_unique_id() with saves of
	# the SAME PackedScene object, twice through the block, to see how the sequence advances.
	_ensure_base()
	var t: Array = _build()
	var ps1: PackedScene = t[0]
	var loaded: Gradient = t[2]
	var out := PackedStringArray()
	for round_i in [0, 1]:
		for k in [0, 1]:
			var p := BASE + "/g%d_%d.tscn" % [round_i, k]
			var e := ResourceSaver.save(ps1, p)
			out.append("r%ds%d=%s/%s" % [round_i, k, _join(_ids(_text(p))), error_string(e)])
			out.append("g%ds%d=%s" % [round_i, k, loaded.generate_scene_unique_id()])
	print("R96B seq extgen seq=%s" % " ".join(out))
	_p("seq=%s" % " ".join(out))
	_emit("extgen")
