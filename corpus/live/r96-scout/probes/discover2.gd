extends SceneTree
# r96 scout DISCOVERY probe #2 — bundle dict, saver flags, cache replace, path/uid bookkeeping.
var arm := ""
const BASE := "user://r96"

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"bundle": _bundle()
		"flags": _flags()
		"replace": _replace()
		"paths": _paths()
		"dirs": _dirs()
		"editor": _editor()
		_: print("R96 discover2 unknown_arm=%s" % arm)
	quit(0)

func _sha(p: String) -> String:
	var f := FileAccess.open(p, FileAccess.READ)
	if f == null:
		return "none"
	var bytes := f.get_buffer(f.get_length())
	f.close()
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(bytes)
	return ctx.finish().hex_encode().substr(0, 16)

func _size(p: String) -> int:
	var f := FileAccess.open(p, FileAccess.READ)
	if f == null:
		return -1
	var n := f.get_length()
	f.close()
	return n

func _text(p: String) -> String:
	var f := FileAccess.open(p, FileAccess.READ)
	if f == null:
		return "<none>"
	var t := f.get_as_text()
	f.close()
	return t

func _err(code: int) -> String:
	return "%s(%d)" % [error_string(code), code]

func _pack(n: Node) -> PackedScene:
	var ps := PackedScene.new()
	var e: int = ps.pack(n)
	if e != OK:
		print("R96 pack_error=%s" % _err(e))
	return ps

func _mk_tree() -> Node2D:
	var r := Node2D.new()
	r.name = "BRoot"
	var c := Node2D.new()
	c.name = "BChild"
	c.position = Vector2(7, 8)
	r.add_child(c)
	c.owner = r
	return r

func _bundle() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var ps := _pack(_mk_tree())
	var d: Dictionary = ps._get_bundled_scene()
	var keys := PackedStringArray()
	for k in d.keys():
		keys.append(str(k))
	keys.sort()
	print("R96 bundle keys=%s" % ",".join(keys))
	for k in keys:
		print("R96 bundle %s=%s" % [k, str(d[k])])
	var p := BASE + "/bundle.tscn"
	print("R96 bundle save=%s sha=%s" % [_err(ResourceSaver.save(ps, p)), _sha(p)])
	print("R96 bundle text=%s" % _text(p).replace("\n", "|"))
	# re-set the same bundle and save: byte-identical?
	var ps2 := PackedScene.new()
	ps2._set_bundled_scene(d)
	var p2 := BASE + "/bundle2.tscn"
	print("R96 bundle resave=%s sha2=%s same=%s" % [_err(ResourceSaver.save(ps2, p2)), _sha(p2), _sha(p2) == _sha(p)])
	print("R96 bundle text2=%s" % _text(p2).replace("\n", "|"))
	# mutate node unique ids inside the bundle if present
	var nodes = d.get("nodes")
	if nodes is Array and nodes.size() > 0:
		print("R96 bundle node0_type=%s node0=%s" % [typeof(nodes[0]), str(nodes[0])])
	var variants = d.get("variants")
	if variants is Array:
		print("R96 bundle variants_n=%d" % variants.size())
		for i in variants.size():
			print("R96 bundle variant_%d=%s" % [i, str(variants[i])])
	var names = d.get("names")
	if names is Array:
		print("R96 bundle names=%s" % str(names))

func _flags() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var grad := Gradient.new()
	grad.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 1, 0, 1)])
	grad.resource_name = "FlagGrad"
	var p := BASE + "/flags.tres"
	print("R96 flags none=%s path_after=%s" % [_err(ResourceSaver.save(grad, p)), grad.resource_path])
	print("R96 flags none_text=%s" % _text(p).replace("\n", "|"))
	# CHANGE_PATH
	var g2 := Gradient.new()
	g2.colors = PackedColorArray([Color(0, 0, 1, 1), Color(1, 1, 0, 1)])
	var p2 := BASE + "/flags_change.tres"
	var e2 := ResourceSaver.save(g2, p2, ResourceSaver.FLAG_CHANGE_PATH)
	print("R96 flags change=%s path_after=%s cached_same=%s" % [_err(e2), g2.resource_path, is_same(ResourceLoader.load(p2), g2)])
	print("R96 flags change_text=%s" % _text(p2).replace("\n", "|"))
	# OMIT_EDITOR_PROPERTIES on a node property that is editor-only
	var r := Node2D.new()
	r.name = "FlagRoot"
	r.editor_description = "hello editor"
	r.position = Vector2(1, 2)
	var ps := _pack(r)
	var p3 := BASE + "/flags_editor.tscn"
	var p4 := BASE + "/flags_editor_omit.tscn"
	print("R96 flags editor_save=%s" % _err(ResourceSaver.save(ps, p3)))
	print("R96 flags editor_omit=%s" % _err(ResourceSaver.save(ps, p4, ResourceSaver.FLAG_OMIT_EDITOR_PROPERTIES)))
	print("R96 flags editor_text=%s" % _text(p3).replace("\n", "|"))
	print("R96 flags omit_text=%s" % _text(p4).replace("\n", "|"))
	# BUNDLE_RESOURCES: scene referencing an ext resource
	var ext := BASE + "/flags_ext.tres"
	print("R96 flags ext_save=%s" % _err(ResourceSaver.save(grad, ext)))
	var loaded = ResourceLoader.load(ext)
	var line := Line2D.new()
	line.name = "FlagLine"
	line.gradient = loaded
	var r2 := Node2D.new()
	r2.name = "FlagRoot2"
	r2.add_child(line)
	line.owner = r2
	var ps2 := _pack(r2)
	var p5 := BASE + "/flags_bundle.tscn"
	print("R96 flags bundle_save=%s text=%s" % [_err(ResourceSaver.save(ps2, p5, ResourceSaver.FLAG_BUNDLE_RESOURCES)), _text(p5).replace("\n", "|")])
	var p6 := BASE + "/flags_norelat.tscn"
	print("R96 flags norelat_save=%s text=%s" % [_err(ResourceSaver.save(ps2, p6)), _text(p6).replace("\n", "|")])
	var p7 := BASE + "/flags_subpaths.tscn"
	print("R96 flags subpaths_save=%s text=%s" % [_err(ResourceSaver.save(ps2, p7, ResourceSaver.FLAG_REPLACE_SUBRESOURCE_PATHS)), _text(p7).replace("\n", "|")])
	# COMPRESS + BIG_ENDIAN on binary
	var p8 := BASE + "/flags.res"
	var p9 := BASE + "/flags_comp.res"
	var p10 := BASE + "/flags_be.res"
	print("R96 flags res=%s size=%d sha=%s" % [_err(ResourceSaver.save(grad, p8)), _size(p8), _sha(p8)])
	print("R96 flags comp=%s size=%d sha=%s" % [_err(ResourceSaver.save(grad, p9, ResourceSaver.FLAG_COMPRESS)), _size(p9), _sha(p9)])
	print("R96 flags be=%s size=%d sha=%s" % [_err(ResourceSaver.save(grad, p10, ResourceSaver.FLAG_SAVE_BIG_ENDIAN)), _size(p10), _sha(p10)])
	var back = ResourceLoader.load(p9)
	print("R96 flags comp_back=%s" % str(back.colors) if back != null else "R96 flags comp_back=null")
	var back2 = ResourceLoader.load(p10)
	print("R96 flags be_back=%s" % str(back2.colors) if back2 != null else "R96 flags be_back=null")

func _replace() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var p := BASE + "/rep.tres"
	var a := Gradient.new()
	a.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 0, 0, 1)])
	print("R96 replace saveA=%s" % _err(ResourceSaver.save(a, p)))
	var cached = ResourceLoader.load(p)
	print("R96 replace cached_colors=%s" % str(cached.colors))
	var b := Gradient.new()
	b.colors = PackedColorArray([Color(0, 1, 0, 1), Color(0, 0, 0, 1)])
	print("R96 replace saveB=%s" % _err(ResourceSaver.save(b, p)))
	var reuse = ResourceLoader.load(p)
	print("R96 replace reuse_is_cached=%s colors=%s" % [is_same(reuse, cached), str(reuse.colors)])
	var repl = ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REPLACE)
	print("R96 replace replace_is_cached=%s colors=%s" % [is_same(repl, cached), str(repl.colors)])
	var after = ResourceLoader.load(p)
	print("R96 replace after_is_repl=%s colors=%s" % [is_same(after, repl), str(after.colors)])
	var ign = ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_IGNORE)
	print("R96 replace ignore_colors=%s is_cached=%s" % [str(ign.colors), is_same(ign, cached)])
	print("R96 replace cached_colors_after=%s" % str(cached.colors))

func _paths() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var p := BASE + "/paths.tres"
	var g := Gradient.new()
	print("R96 paths save=%s" % _err(ResourceSaver.save(g, p)))
	print("R96 paths saver_id_for_path=%d" % ResourceSaver.get_resource_id_for_path(p))
	print("R96 paths loader_uid=%d" % ResourceLoader.get_resource_uid(p))
	print("R96 paths uid_path_to_uid=%s ensure=%s" % [str(ResourceUID.path_to_uid(p)), str(ResourceUID.ensure_path(p))])
	print("R96 paths resource_id_after=%d" % ResourceSaver.get_resource_id_for_path(p))
	var g2 := Gradient.new()
	g2.set_path(p)
	print("R96 paths set_path=%s cached=%s" % [g2.resource_path, is_same(ResourceLoader.load(p), g2)])
	g2.set_id_for_path(p, "424242")
	print("R96 paths set_id_for_path=%s id=%s" % [g2.resource_path, g2.get_id_for_path(p)])
	print("R96 paths id_for_path_saved=%s" % Resource.new().get_id_for_path(p))
	print("R96 paths built_in=%s built_in_null=%s" % [g2.is_built_in(), Resource.new().is_built_in()])
	# res:// save: does a uid appear in the header?
	var rp := "res://r96_probe.tres"
	var e := ResourceSaver.save(g, rp)
	print("R96 paths res_save=%s exists=%s" % [_err(e), FileAccess.file_exists(rp)])
	if e == OK:
		print("R96 paths res_text=%s" % _text(rp).replace("\n", "|"))
		print("R96 paths res_id_for_path=%d uid=%d" % [ResourceSaver.get_resource_id_for_path(rp), ResourceLoader.get_resource_uid(rp)])
		print("R96 paths res_uid_text=%s" % ResourceUID.id_to_text(ResourceLoader.get_resource_uid(rp)))
		DirAccess.remove_absolute(ProjectSettings.globalize_path(rp))
	# relative save: where did it land?
	var rel := "r96_relative.tres"
	var e2 := ResourceSaver.save(Gradient.new(), rel)
	print("R96 paths rel_save=%s cwd_file=%s res_file=%s" % [_err(e2), FileAccess.file_exists(rel),
		FileAccess.file_exists("res://" + rel)])
	print("R96 paths rel_globalized=%s" % ProjectSettings.globalize_path(rel))
	if FileAccess.file_exists(rel):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(rel))
	if FileAccess.file_exists("res://" + rel):
		DirAccess.remove_absolute(ProjectSettings.globalize_path("res://" + rel))

func _dirs() -> void:
	# ResourceSaver vs FileAccess on a missing directory
	var missing := "user://r96_missing_dir_xyz/deep/file.tscn"
	DirAccess.remove_absolute(ProjectSettings.globalize_path("user://r96_missing_dir_xyz"))
	var ps := _pack(_mk_tree())
	print("R96 dirs saver_missing=%s exists_after=%s" % [_err(ResourceSaver.save(ps, missing)),
		FileAccess.file_exists(missing)])
	var f := FileAccess.open("user://r96_missing_dir_xyz/deep/file.txt", FileAccess.WRITE)
	print("R96 dirs fileaccess_null=%s" % (f == null))
	if f != null:
		f.store_string("x")
		f.close()
	print("R96 dirs fileaccess_created=%s" % FileAccess.file_exists("user://r96_missing_dir_xyz/deep/file.txt"))
	DirAccess.remove_absolute(ProjectSettings.globalize_path("user://r96_missing_dir_xyz"))
	# overwrite semantics: save to an existing file path with different content
	var p := BASE + "/ovw.tres"
	var g := Gradient.new()
	g.colors = PackedColorArray([Color(1, 1, 1, 1), Color(0, 0, 0, 1)])
	print("R96 dirs ovw1=%s size=%d" % [_err(ResourceSaver.save(g, p)), _size(p)])
	var g2 := Gradient.new()
	g2.colors = PackedColorArray([Color(1, 1, 1, 1), Color(0, 0, 0, 1), Color(0.5, 0.5, 0.5, 1)])
	print("R96 dirs ovw2=%s size=%d" % [_err(ResourceSaver.save(g2, p)), _size(p)])
	print("R96 dirs ovw_text=%s" % _text(p).replace("\n", "|"))
	# a saved file that is then deleted -> load
	DirAccess.remove_absolute(ProjectSettings.globalize_path(p))
	print("R96 dirs deleted_load=%s" % str(ResourceLoader.load(p)))
	print("R96 dirs deleted_cached=%s" % ResourceLoader.has_cached(p))

func _editor() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)
	var r := Node2D.new()
	r.name = "ERoot"
	var c := Node2D.new()
	c.name = "EChild"
	r.add_child(c)
	c.owner = r
	var ps := _pack(r)
	var p := BASE + "/editor.tscn"
	print("R96 editor save=%s" % _err(ResourceSaver.save(ps, p)))
	var back: PackedScene = ResourceLoader.load(p)
	var inst := back.instantiate()
	print("R96 editor in_tree=%s part_of_edited=%s" % [inst.is_inside_tree(), inst.is_part_of_edited_scene()])
	var kid = inst.get_child(0)
	print("R96 editor editable_default=%s placeholder=%s" % [kid.is_editable_instance(inst), kid.get_scene_instance_load_placeholder()])
	inst.set_editable_instance(kid, true)
	print("R96 editor editable_after=%s" % kid.is_editable_instance(inst))
	kid.set_scene_instance_load_placeholder(true)
	print("R96 editor placeholder_after=%s" % kid.get_scene_instance_load_placeholder())
	print("R96 editor root_placeholder=%s" % inst.get_scene_instance_load_placeholder())
	print("R96 editor scene_file_path_set=%s" % (inst.scene_file_path == p))
	var i2 := back.instantiate(PackedScene.GEN_EDIT_STATE_MAIN)
	print("R96 editor main_editable=%s placeholder=%s" % [i2.get_child(0).is_editable_instance(i2), i2.get_child(0).get_scene_instance_load_placeholder()])
	var i3 := back.instantiate(PackedScene.GEN_EDIT_STATE_MAIN_INHERITED)
	print("R96 editor main_inh_editable=%s placeholder=%s" % [i3.get_child(0).is_editable_instance(i3), i3.get_child(0).get_scene_instance_load_placeholder()])
	print("R96 editor orphan_ids=%s" % str(inst.get_orphan_node_ids()))
	print("R96 editor unique_name=%s" % kid.is_unique_name_in_owner())
	kid.set_unique_name_in_owner(true)
	print("R96 editor unique_name_after=%s" % kid.is_unique_name_in_owner())
