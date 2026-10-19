extends SceneTree
# r104-C1 attack reader: prints the UID-lattice observation a receipt would pin.
# Launch: godot --headless --path <proj> --script res://crit1_read.gd -- --arm=<arm>
# Arms: census | ident | remap | collision
var arm := ""

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"census": _census()
		"ident": _ident()
		"remap": _remap()
		"collision": _collision()
		_: print("CRIT1 arm=%s reason=unknown_arm" % arm)
	quit(0)

func _uid(p: String) -> int:
	return ResourceLoader.get_resource_uid(p)

func _census() -> void:
	var ps := ["res://alpha.gd", "res://beta.gd", "res://tex.png"]
	var parts := []
	for p in ps:
		parts.append("%s=%d" % [p.get_file(), _uid(p)])
	print("CRIT1 census ", " ".join(parts))

func _ident() -> void:
	var a := load("res://alpha.gd")
	var b := load("res://alpha.gd")
	var c := ResourceLoader.load("res://alpha.gd", "", ResourceLoader.CACHE_MODE_IGNORE)
	var d := load("res://alpha.gd")
	print("CRIT1 ident reuse_same=%d ignore_same=%d post_reuse_same=%d" % [
		int(is_same(a, b)), int(is_same(c, a)), int(is_same(d, a))])

func _remap() -> void:
	var t = ResourceLoader.load("res://tex.png")
	print("CRIT1 remap load_ok=%d class=%s path=%s exists_png=%d exists_import=%d uid=%d" % [
		int(t != null), t.get_class() if t else "<null>",
		t.resource_path if t else "<null>",
		int(ResourceLoader.exists("res://tex.png")),
		int(ResourceLoader.exists("res://tex.png.import")),
		_uid("res://tex.png")])

func _collision() -> void:
	var ua := _uid("res://alpha.gd")
	var ub := _uid("res://beta.gd")
	var same := ua != -1 and ua == ub
	print("CRIT1 collision alpha=%d beta=%d same_id=%d alpha_resolves=%s beta_resolves=%s" % [
		ua, ub, int(same),
		ResourceUID.get_id_path(ua) if ua != -1 else "<none>",
		ResourceUID.get_id_path(ub) if ub != -1 else "<none>"])
