extends SceneTree
# r104-W7 — independent construction (NOT a copy of E1's fixture) probing the
# ResourceLoader / ResourceUID / uid-cache lattice on Godot 4.7.2 headless.
# Launch: godot --headless --path <scratch> --script res://res_uid_w07.gd -- --arm=<arm>
# Arms: census builtin custfile cache collision mkpng importremap persist_a persist_b
var arm := ""
const BASE := "user://w07"
const PNG_PATH := "res://w07_probe.png"

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"census": _arm_census()
		"builtin": _arm_builtin()
		"custfile": _arm_custfile()
		"cache": _arm_cache()
		"cachebust": _arm_cachebust()
		"api2": _arm_api2()
		"stale": _arm_stale()
		"nouid": _arm_nouid()
		"collision": _arm_collision()
		"mkpng": _arm_mkpng()
		"importremap": _arm_importremap()
		"persist_a": _arm_persist("a")
		"persist_b": _arm_persist("b")
		_: print("FAIL res_uid_w07 arm=%s reason=unknown_arm" % arm)
	quit(0)

# ------------------------------------------------------------------ helpers

func _b(v: bool) -> String:
	return "1" if v else "0"

func _ensure() -> void:
	DirAccess.make_dir_recursive_absolute(BASE)

func _text(p: String) -> String:
	var f := FileAccess.open(p, FileAccess.READ)
	if f == null:
		return "<none>"
	var t := f.get_as_text()
	f.close()
	return t

func _p(line: String) -> void:
	print("PASS res_uid_w07 " + line)

func _file_bytes(p: String) -> int:
	var f := FileAccess.open(p, FileAccess.READ)
	if f == null:
		return -1
	var n := f.get_length()
	f.close()
	return n

# ------------------------------------------------------------------ arms

func _arm_census() -> void:
	var methods := PackedStringArray()
	for m in ClassDB.class_get_method_list("ResourceUID", true):
		methods.append("%s/%d" % [m["name"], m["args"].size()])
	var consts := PackedStringArray()
	for c in ClassDB.class_get_integer_constant_list("ResourceUID", true):
		consts.append("%s=%d" % [c, ClassDB.class_get_integer_constant("ResourceUID", c)])
	var lmethods := PackedStringArray()
	for m in ClassDB.class_get_method_list("ResourceLoader", true):
		lmethods.append(m["name"])
	var cmode := []
	for c in ["CACHE_MODE_IGNORE", "CACHE_MODE_REUSE", "CACHE_MODE_REPLACE", "CACHE_MODE_IGNORE_DEEP", "CACHE_MODE_REPLACE_DEEP"]:
		cmode.append("%s=%d" % [c, ClassDB.class_get_integer_constant("ResourceLoader", c)])
	var invalid := ResourceUID.INVALID_ID
	_p("census methods=%s consts=%s invalid=%d invalid_text=%s cache_modes=%s" % [
		",".join(methods), ",".join(consts), invalid,
		ResourceUID.id_to_text(invalid), ",".join(cmode)])
	_p("census loader_has_uid=%s loader_has_exists=%s loader_has_remap=%s" % [
		_b("get_resource_uid" in lmethods), _b("exists" in lmethods),
		_b("get_dependencies" in lmethods)])

func _arm_builtin() -> void:
	# Builtin (textual) uid round-trips on engine-generated text forms.
	var samples := PackedStringArray(["uid://bqk3m5n7qar1", "uid://cpt8ajmloovv7", "uid://b0", "uid://", "not-a-uid", ""])
	var rows := PackedStringArray()
	for s in samples:
		var id := ResourceUID.text_to_id(s)
		rows.append("%s->%d->%s" % [s, id, ResourceUID.id_to_text(id)])
	_p("builtin samples=%s" % "|".join(rows))
	var c := ResourceUID.create_id()
	var c2 := ResourceUID.create_id()
	_p("builtin create_id text=%s registered=%s unique=%s has_id=%s path=%s" % [
		ResourceUID.id_to_text(c), _b(not ResourceUID.has_id(c)),
		_b(c != c2), _b(ResourceUID.has_id(c)),
		ResourceUID.get_id_path(c)])

func _arm_custfile() -> void:
	# A committed/generated `*.gd.uid` companion file: read the text form, parse
	# it into an id, and ask ResourceLoader for the same resource's uid.
	var gd := "res://camera_follow.gd"
	var uid_path := gd + ".uid"
	var raw := _text(uid_path)
	var stripped := raw.strip_edges()
	var from_text := ResourceUID.text_to_id(stripped)
	var from_loader := ResourceLoader.get_resource_uid(gd)
	var from_loader_text := ResourceUID.id_to_text(from_loader)
	var path_of_loader := ResourceUID.get_id_path(from_loader)
	var path_of_text := ResourceUID.get_id_path(from_text)
	var uid_file_bytes := _file_bytes(uid_path)
	var cache_exists := FileAccess.file_exists("res://.godot/uid_cache.bin")
	var cache_bytes := _file_bytes("res://.godot/uid_cache.bin")
	_p("custfile uid_text=%s stripped_len=%d uid_file_bytes=%d from_text=%d loader_uid=%d text_eq_loader=%s loader_text=%s" % [
		raw.replace("\n", "\\n"), stripped.length(), uid_file_bytes, from_text,
		from_loader, _b(from_text == from_loader), from_loader_text])
	_p("custfile path_of_loader=%s path_of_text=%s loader_path_matches=%s uid_cache_exists=%s uid_cache_bytes=%d" % [
		path_of_loader, path_of_text, _b(path_of_loader == gd),
		_b(cache_exists), cache_bytes])

func _arm_cache() -> void:
	_ensure()
	var grad := Gradient.new()
	grad.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 0, 1, 1)])
	var p := BASE + "/cache.tres"
	var e := ResourceSaver.save(grad, p)
	var a = ResourceLoader.load(p)
	var b = ResourceLoader.load(p)
	var same_default := is_same(a, b)
	var ign = ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_IGNORE)
	var same_ignore := is_same(a, ign)
	var re = ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REUSE)
	var same_reuse := is_same(a, re)
	var rep = ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REPLACE)
	var same_replace := is_same(a, rep)
	var after_replace = ResourceLoader.load(p)
	var same_after_replace := is_same(rep, after_replace)
	var uid_path := ResourceLoader.get_resource_uid(p)
	var uid_text := ResourceUID.id_to_text(uid_path)
	var cache_path := ResourceUID.get_id_path(uid_path)
	_p("cache save=%d same_default=%s same_ignore=%s same_reuse=%s same_replace=%s same_after_replace=%s" % [
		e, _b(same_default), _b(same_ignore), _b(same_reuse), _b(same_replace),
		_b(same_after_replace)])
	_p("cache uid=%d uid_text=%s id_path=%s id_path_is_user=%s" % [
		uid_path, uid_text, cache_path, _b(cache_path.begins_with("user://"))])

func _arm_cachebust() -> void:
	# Byte-level cache busting: change the on-disk text between two loads and
	# observe which cache_mode surfaces the new content.
	_ensure()
	var p := BASE + "/bust.tres"
	var g1 := Gradient.new()
	g1.colors = PackedColorArray([Color(1, 0, 0, 1), Color(0, 0, 1, 1)])
	ResourceSaver.save(g1, p)
	var first = ResourceLoader.load(p)
	var first_colors := (first as Gradient).colors.size()
	var g2 := Gradient.new()
	g2.colors = PackedColorArray([Color(0, 1, 0, 1), Color(1, 1, 0, 1), Color(0, 0, 0, 1)])
	ResourceSaver.save(g2, p)
	var cached = ResourceLoader.load(p)
	var cached_n := (cached as Gradient).colors.size()
	var fresh = ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_IGNORE)
	var fresh_n := (fresh as Gradient).colors.size()
	var replaced = ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REPLACE)
	var replaced_n := (replaced as Gradient).colors.size()
	var after = ResourceLoader.load(p)
	var after_n := (after as Gradient).colors.size()
	_p("cachebust on_disk=3 first_load=%d cached_load=%d ignore_load=%d replace_load=%d after_replace=%d ignore_is_cached=%s replace_is_cached=%s" % [
		first_colors, cached_n, fresh_n, replaced_n, after_n,
		_b(is_same(fresh, cached)), _b(is_same(replaced, cached))])

func _arm_api2() -> void:
	# The ResourceUID methods scene_io_lattice.gd never touched.
	_ensure()
	var p := BASE + "/api2.tres"
	var g := Gradient.new()
	ResourceSaver.save(g, p)
	var path_uid := str(ResourceUID.path_to_uid(p))
	var uid_to_path := ResourceUID.uid_to_path(path_uid)
	var ensure_id := str(ResourceUID.ensure_path(p))
	var created_for := ResourceUID.create_id_for_path(p)
	var has_created := ResourceUID.has_id(created_for)
	var set_target := 5150002
	ResourceUID.set_id(set_target, p)
	var after_set := ResourceUID.get_id_path(set_target)
	var path_to_uid_again := str(ResourceUID.path_to_uid(p))
	_p("api2 path_to_uid=%s type_is_text=%s uid_to_path=%s ensure_path=%s create_id_for_path=%d has_created=%s" % [
		path_uid, _b(path_uid.begins_with("uid://")), uid_to_path, ensure_id,
		created_for, _b(has_created)])
	_p("api2 set_id_path=%s path_to_uid_again=%s set_equals_path_to_uid=%s" % [
		after_set, path_to_uid_again, _b(str(set_target) == path_to_uid_again)])

func _arm_stale() -> void:
	# Stale id after a path move: register an id for path A, move the file to
	# path B, then ask both directions.
	_ensure()
	var a := BASE + "/move_a.tres"
	var b := BASE + "/move_b.tres"
	var g := Gradient.new()
	ResourceSaver.save(g, a)
	ResourceUID.add_id(6260003, a)
	var path_before := ResourceUID.get_id_path(6260003)
	var dir := DirAccess.open(BASE)
	var moved := false
	if dir != null:
		moved = dir.rename(a, b) == OK
	var path_after := ResourceUID.get_id_path(6260003)
	var uid_of_b := ResourceLoader.get_resource_uid(b)
	var uid_of_a := ResourceLoader.get_resource_uid(a)
	_p("stale moved=%s path_before=%s path_after_move=%s uid_of_old_path=%d uid_of_new_path=%d same=%s" % [
		_b(moved), path_before, path_after, uid_of_a, uid_of_b, _b(uid_of_a == uid_of_b)])

func _arm_nouid() -> void:
	# `.uid`-absent class: a script with no committed companion, and a path
	# whose uid is unknown to the cache.
	var p := "res://res_uid_w07.gd"
	var companion := p + ".uid"
	var exists := FileAccess.file_exists(companion)
	var loader_uid := ResourceLoader.get_resource_uid(p)
	var unknown := ResourceUID.get_id_path(999999999999999999)
	var unknown_text := ResourceUID.id_to_text(999999999999999999)
	var bad_round := ResourceUID.text_to_id("uid://zzzzzzzzzzzz")
	_p("nouid companion_exists=%s loader_uid=%d loader_text=%s unknown_path=%s unknown_text=%s bad_round=%d" % [
		_b(exists), loader_uid, ResourceUID.id_to_text(loader_uid), unknown,
		unknown_text, bad_round])

func _arm_collision() -> void:
	# Collision classes: same id claimed by two paths, then id removed.
	_ensure()
	var p1 := BASE + "/col_a.tres"
	var p2 := BASE + "/col_b.tres"
	var g := Gradient.new()
	ResourceSaver.save(g, p1)
	ResourceSaver.save(g, p2)
	var id := 7770001
	ResourceUID.add_id(id, p1)
	var path_after_first := ResourceUID.get_id_path(id)
	ResourceUID.add_id(id, p2)
	var path_after_second := ResourceUID.get_id_path(id)
	var has := ResourceUID.has_id(id)
	ResourceUID.remove_id(id)
	var has_after_remove := ResourceUID.has_id(id)
	var path_after_remove := ResourceUID.get_id_path(id)
	var dup_path := ResourceUID.id_to_text(id)
	_p("collision id=%d first=%s second=%s has=%s after_remove=%s path_after_remove=%s text=%s" % [
		id, path_after_first, path_after_second, _b(has), _b(has_after_remove),
		path_after_remove, dup_path])

func _arm_mkpng() -> void:
	var img := Image.create(2, 2, false, Image.FORMAT_RGBA8)
	img.fill(Color(1, 0.5, 0, 1))
	var e := img.save_png(PNG_PATH)
	var bytes := _file_bytes(PNG_PATH)
	var import_exists := FileAccess.file_exists(PNG_PATH + ".import")
	_p("mkpng save=%d bytes=%d import_exists=%s path=%s" % [
		e, bytes, _b(import_exists), ProjectSettings.globalize_path(PNG_PATH)])

func _arm_importremap() -> void:
	var import_path := PNG_PATH + ".import"
	var text := _text(import_path)
	var uid_line := ""
	var path_line := ""
	for line in text.split("\n"):
		if line.begins_with("uid="):
			uid_line = line.strip_edges()
		if line.begins_with("path="):
			path_line = line.strip_edges()
	var uid_text := uid_line.replace("uid=", "").replace("\"", "")
	var id := ResourceUID.text_to_id(uid_text)
	var loader_uid := ResourceLoader.get_resource_uid(PNG_PATH)
	var loader_text := ResourceUID.id_to_text(loader_uid)
	var id_path := ResourceUID.get_id_path(loader_uid)
	var remap := ProjectSettings.localize_path(path_line.replace("path=", "").replace("\"", ""))
	var remap_exists := FileAccess.file_exists(remap)
	var remap_bytes := _file_bytes(remap)
	var loaded = ResourceLoader.load(PNG_PATH)
	_p("importremap import_exists=%s uid_line=%s path_line=%s text_to_id=%d loader_uid=%d text_eq=%s" % [
		_b(FileAccess.file_exists(import_path)), uid_line, path_line, id, loader_uid,
		_b(id == loader_uid)])
	_p("importremap loader_text=%s id_path=%s remap=%s remap_exists=%s remap_bytes=%d loaded_cls=%s loaded_path=%s" % [
		loader_text, id_path, remap, _b(remap_exists), remap_bytes,
		loaded.get_class() if loaded != null else "<null>",
		loaded.resource_path if loaded != null else "<null>"])

func _arm_persist(mode: String) -> void:
	_ensure()
	var p := BASE + "/persist.tres"
	if mode == "a":
		var g := Gradient.new()
		var e := ResourceSaver.save(g, p)
		var uid_before := ResourceLoader.get_resource_uid(p)
		ResourceUID.add_id(9100011, p)
		var path_of := ResourceUID.get_id_path(9100011)
		var cache_bytes := _file_bytes("res://.godot/uid_cache.bin")
		print("PASS res_uid_w07 persist_a save=%d uid_before=%d uid_text=%s add_ok=%s path_of=%s cache_bytes=%d" % [
			e, uid_before, ResourceUID.id_to_text(uid_before), _b(path_of == p), path_of, cache_bytes])
	else:
		var has := ResourceUID.has_id(9100011)
		var path_of := ResourceUID.get_id_path(9100011)
		var uid_now := ResourceLoader.get_resource_uid(p)
		var cache_bytes := _file_bytes("res://.godot/uid_cache.bin")
		print("PASS res_uid_w07 persist_b has=%s path_of=%s uid_now=%d uid_text=%s cache_bytes=%d" % [
			_b(has), path_of, uid_now, ResourceUID.id_to_text(uid_now), cache_bytes])
