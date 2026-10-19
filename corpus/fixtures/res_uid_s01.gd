extends SceneTree
# r104-E1 fixture — ResourceUID census + id<->path round-trips (builtin + custom
# .uid sidecars), refusal/missing classes.  Seat KEY=E1, round 104.
#
# Launch (battery convention):
#   godot --headless --path <scratch> --script res://res_uid_s01.gd -- --arm=<name>
# Exactly ONE `PASS res_uid_s01 <arm> <k=v> ...` line per arm is the authorable
# signature.  No instance ids / RIDs / addresses / process-dependent tokens are
# printed; every value below is an int, a bool, a fixed string, or a path text.
#
# MEASURED LAWS (all [M], Godot 4.7.2.stable.arch_linux.ed1daf0bf, see
# reports/round-104/r104-E1.md for the exact commands and raw bytes):
#   U1 `ResourceUID.path_to_uid(path) -> String` and `ensure_path(path_or_uid)
#      -> String` RETURN STRINGS (a `uid://` text or an echo of the argument),
#      NOT ints — r96 pinned only the method NAME list, never the signatures.
#      The int-returning family is id_to_text/text_to_id/create_id/
#      create_id_for_path/has_id/get_id_path; uid_to_path takes the uid TEXT.
#   U2 `path_to_uid` on a path the engine has no uid for returns THE PATH
#      ITSELF (not "", not "uid://<invalid>") — a string-typed sentinel that a
#      caller cannot distinguish from a real answer by prefix alone.
#   U3 a hand-written `<file>.uid` sidecar is NOT honoured at runtime: with no
#      uid_cache.bin entry, `path_to_uid` still echoes the path and
#      `ResourceLoader.get_resource_uid` stays -1.  Sidecars are an EDITOR
#      artifact; the runtime authority is `.godot/uid_cache.bin`.
#   U4 `create_id_for_path(path)` for a path with no uid_cache entry is a PURE
#      deterministic hash of the path string: identical across processes and
#      identical in a cache-present and a cache-absent project (verified for
#      res:// and user:// paths).  It never registers: `has_id` stays false.
#   U5 the value U4 yields for a path that DOES have a uid_cache entry differs
#      from the entry itself and from U4's pure hash; the exact input mix is
#      UNKNOWN (see the shard's unknown class).  The fixture therefore pins U4
#      only, on a path the battery scratch never populates.
#   U6 text<->id: text_to_id("") = -1, text_to_id("uid://") = 0,
#      text_to_id("uid://x") = 23, text_to_id without the uid:// scheme = -1,
#      id_to_text(-1) = "uid://<invalid>", id_to_text(0) = "uid://a".
#   U7 registration collisions: a duplicate add_id is REFUSED (engine assert,
#      first path kept) and set_id overrides; a second id added for an
#      already-mapped path makes both ids resolve to that path while
#      path_to_uid for it stops answering with a uid.
#   U8 get_id_path on an id the engine does not know emits a diagnostic whose
#      text depends on uid_cache.bin presence: `Invalid UID.` without the
#      cache, `Unrecognized UID: "uid://<tok>".` with it.  Only the `diag` arm
#      provokes it, so only that row needs an expected_errors allowlist.

var arm := ""
const SIDECAR_RES := "res://e1_sidecar_probe.gd"
const SIDECAR_TXT := "uid://bqk3m5n7qar1"
const CFP_RES := "res://e1_selfreg_probe.gd"
const CFP_USER := "user://e1_selfreg_probe.gd"
const UNKNOWN_TOK := "uid://bqk3m5n7qar1"

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"census": _arm_census()
		"roundtrip": _arm_roundtrip()
		"pathtouid": _arm_pathtouid()
		"createid": _arm_createid()
		"collide": _arm_collide()
		"diag": _arm_diag()
		_: print("FAIL res_uid_s01 %s reason=unknown_arm" % arm)
	_wipe()
	quit(0)

# ------------------------------------------------------------------ utilities

func _b(v: bool) -> String:
	return "true" if v else "false"

func _write(p: String, text: String) -> bool:
	var f := FileAccess.open(p, FileAccess.WRITE)
	if f == null:
		return false
	f.store_string(text)
	f.close()
	return true

func _read(p: String) -> String:
	if not FileAccess.file_exists(p):
		return "<absent>"
	var f := FileAccess.open(p, FileAccess.READ)
	if f == null:
		return "<absent>"
	var t := f.get_as_text().strip_edges()
	f.close()
	return t

func _wipe() -> void:
	DirAccess.remove_absolute(ProjectSettings.globalize_path(SIDECAR_RES + ".uid"))
	DirAccess.remove_absolute(ProjectSettings.globalize_path(SIDECAR_RES))
	var da := DirAccess.open("user://")
	if da != null and da.dir_exists("r104_e1"):
		for fn in DirAccess.get_files_at("user://r104_e1"):
			DirAccess.remove_absolute(ProjectSettings.globalize_path("user://r104_e1/" + fn))

var _parts: PackedStringArray = []

func _p(part: String) -> void:
	_parts.append(part)

func _emit(arm_name: String) -> void:
	print("PASS res_uid_s01 %s %s" % [arm_name, " ".join(_parts)])
	_parts.clear()

func _sig(obj: String, names: PackedStringArray) -> String:
	var out := PackedStringArray()
	for m in ClassDB.class_get_method_list(obj, true):
		if m.name in names:
			var args := PackedStringArray()
			for a in m.args:
				args.append("%s:%s" % [a.name, type_string(a.type)])
			out.append("%s(%s)->%s" % [m.name, ",".join(args), type_string(m["return"].type)])
	return "|".join(out)

# ---------------------------------------------------------------------- arms

func _arm_census() -> void:
	# the int-returning family, the String-returning family, and the two
	# uid-adjacent ResourceLoader/ResourceSaver signatures — U1.
	_p("uid_sigs=%s" % _sig("ResourceUID", PackedStringArray([
		"id_to_text", "text_to_id", "create_id", "create_id_for_path",
		"has_id", "add_id", "set_id", "get_id_path", "remove_id",
		"uid_to_path", "path_to_uid", "ensure_path"])))
	_p("saver_sigs=%s" % _sig("ResourceSaver", PackedStringArray([
		"set_uid", "get_resource_id_for_path"])))
	_p("loader_sigs=%s" % _sig("ResourceLoader", PackedStringArray([
		"get_resource_uid", "has_cached", "get_cached_ref", "exists"])))
	_p("uid_consts=%s" % _sig_consts())
	_emit("census")

func _sig_consts() -> String:
	var out := PackedStringArray()
	for c in ClassDB.class_get_integer_constant_list("ResourceUID", true):
		out.append("%s=%d" % [c, ClassDB.class_get_integer_constant("ResourceUID", c)])
	return ",".join(out)

func _arm_roundtrip() -> void:
	# U6 — text -> id -> text, and the malformed family.  No engine diagnostic
	# is provoked here: text_to_id on a malformed text returns -1 silently.
	var tok := UNKNOWN_TOK
	var sid := ResourceUID.text_to_id(tok)
	var back := ResourceUID.id_to_text(sid)
	var rt_ok := back == tok
	var malformed := PackedStringArray()
	for t in ["", "uid://", "uid://x", "not-a-uid", "bqk3m5n7qar1", "uid://@@@@"]:
		malformed.append("%s=%d" % [t if t != "" else "<empty>", ResourceUID.text_to_id(t)])
	_p("tok=%s tok_id=%d tok_id_text=%s roundtrip=%s invalid_id=%d" % [
		tok, sid, back, _b(rt_ok), ResourceUID.INVALID_ID])
	_p("id_to_text_-1=%s id_to_text_0=%s id_to_text_1=%s id_to_text_max=%s" % [
		ResourceUID.id_to_text(-1), ResourceUID.id_to_text(0), ResourceUID.id_to_text(1),
		ResourceUID.id_to_text(9223372036854775807)])
	_p("text_to_id_empty_payload=%d text_to_id_single=%d malformed=%s" % [
		ResourceUID.text_to_id("uid://"), ResourceUID.text_to_id("uid://x"), ",".join(malformed)])
	# NB: get_id_path / uid_to_path on an unregistered id emits an engine
	# diagnostic under a uid_cache.bin-bearing project, so this arm stays on
	# the silent queries only; the refusal surface lives in the `diag` arm.
	_p("sid_unregistered=%s id_text_stable=%s" % [
		_b(not ResourceUID.has_id(sid)),
		_b(ResourceUID.id_to_text(ResourceUID.text_to_id(back)) == back)])
	_emit("roundtrip")

func _arm_pathtouid() -> void:
	# U2 + U3 — the String-returning family and the sidecar non-honouring.
	var missing := "res://zzz_absent_e1.gd"
	var no_sidecar := "res://project.godot"
	var ptu_missing := ResourceUID.path_to_uid(missing)
	var ptu_noside := ResourceUID.path_to_uid(no_sidecar)
	# write a hand-written sidecar for a path that has no uid_cache entry
	var sidecar_written := _write(SIDECAR_RES + ".uid", SIDECAR_TXT + "\n")
	var ptu_sidecar := ResourceUID.path_to_uid(SIDECAR_RES)
	var uid_sidecar := ResourceLoader.get_resource_uid(SIDECAR_RES)
	_p("ptu_missing=%s ptu_missing_is_path=%s ptu_noside=%s ptu_noside_is_path=%s" % [
		ptu_missing, _b(ptu_missing == missing), ptu_noside, _b(ptu_noside == no_sidecar)])
	_p("sidecar_written=%s sidecar_text=%s sidecar_readback=%s ptu_sidecar=%s sidecar_honoured=%s" % [
		_b(sidecar_written), SIDECAR_TXT, _read(SIDECAR_RES + ".uid"), ptu_sidecar,
		_b(ptu_sidecar == SIDECAR_TXT)])
	# NB: uid_to_path on an unknown uid emits a diagnostic under a
	# uid_cache.bin-bearing project; that surface is the `diag` arm's job.
	_p("sidecar_get_resource_uid=%d" % uid_sidecar)
	_p("ensure_plain=%s ensure_path_arg=%s ensure_missing=%s" % [
		ResourceUID.ensure_path("not-a-uid"), ResourceUID.ensure_path(no_sidecar),
		ResourceUID.ensure_path(missing)])
	_p("exists_missing=%s get_resource_uid_missing=%d" % [
		_b(ResourceLoader.exists(missing)), ResourceLoader.get_resource_uid(missing)])
	_emit("pathtouid")

func _arm_createid() -> void:
	# U4 — create_id_for_path is a pure path hash for an unregistered path and
	# never registers.  CFP_EXPECT is the measured cross-process constant.
	var a := ResourceUID.create_id_for_path(CFP_RES)
	var b := ResourceUID.create_id_for_path(CFP_RES)
	var ua := ResourceUID.create_id_for_path(CFP_USER)
	var ub := ResourceUID.create_id_for_path(CFP_USER)
	var c1 := ResourceUID.create_id()
	var c2 := ResourceUID.create_id()
	_p("cfp_res=%d cfp_res_text=%s cfp_res_matches_pinned=%s stable=%s" % [
		a, ResourceUID.id_to_text(a), _b(a == 8476142776992359011), _b(a == b)])
	_p("cfp_res_registered=%s cfp_res_path_to_uid=%s" % [
		_b(ResourceUID.has_id(a)), ResourceUID.path_to_uid(CFP_RES)])
	_p("cfp_user=%d cfp_user_matches_pinned=%s stable=%s user_registered=%s" % [
		ua, _b(ua == 4163091229239537790), _b(ua == ub), _b(ResourceUID.has_id(ua))])
	_p("create_id_distinct=%s create_id_unregistered=%s" % [
		_b(c1 != c2), _b(not ResourceUID.has_id(c1))])
	_p("cfp_text_roundtrip=%s" % ResourceUID.id_to_text(ResourceUID.text_to_id(ResourceUID.id_to_text(a))))
	_emit("createid")

func _arm_collide() -> void:
	# U7 — duplicate add is refused (one deterministic engine assert), set_id
	# overrides, and a second id for a mapped path wins path_to_uid's reverse
	# map while both ids keep answering.
	var a := 777001
	var b := 777002
	ResourceUID.add_id(a, "res://e1_x1.gd")
	var p1 := ResourceUID.get_id_path(a)
	ResourceUID.add_id(a, "res://e1_x2.gd")
	var p1_after_dup := ResourceUID.get_id_path(a)
	ResourceUID.set_id(a, "res://e1_x3.gd")
	var p1_after_set := ResourceUID.get_id_path(a)
	ResourceUID.add_id(b, "res://e1_x3.gd")
	var a_path := ResourceUID.get_id_path(a)
	var b_path := ResourceUID.get_id_path(b)
	var ptu_x3 := ResourceUID.path_to_uid("res://e1_x3.gd")
	ResourceUID.remove_id(a)
	var a_has := ResourceUID.has_id(a)
	var b_has := ResourceUID.has_id(b)
	var ptu_x3_after := ResourceUID.path_to_uid("res://e1_x3.gd")
	ResourceUID.add_id(-1, "res://e1_x4.gd")
	var neg_has := ResourceUID.has_id(-1)
	var neg_ptu := ResourceUID.path_to_uid("res://e1_x4.gd")
	_p("add=%s dup_add_refused=%s set_id_overrides=%s" % [
		p1, _b(p1_after_dup == "res://e1_x1.gd"), _b(p1_after_set == "res://e1_x3.gd")])
	_p("two_ids_same_path=%s a_path=%s b_path=%s ptu_x3=%s" % [
		_b(a_path == b_path and a_path == "res://e1_x3.gd"), a_path, b_path, ptu_x3])
	_p("remove_a_has=%s remove_b_has=%s ptu_x3_after_remove_a=%s" % [
		_b(a_has), _b(b_has), ptu_x3_after])
	_p("add_invalid_has=%s add_invalid_ptu=%s" % [_b(neg_has), neg_ptu])
	_emit("collide")

func _arm_diag() -> void:
	# U8 — the refusal diagnostic.  get_id_path(INVALID_ID) emits
	# `ERROR: Invalid UID.` in BOTH cache regimes (verified), so the row's
	# expected_errors entry is cache-independent — unlike a get_id_path on an
	# unknown-but-valid id, whose text flips to
	# `ERROR: Unrecognized UID: "uid://<tok>".` once uid_cache.bin exists.
	# This arm therefore queries the INVALID id only: one deterministic
	# diagnostic, one allowlist entry, byte-identical in both regimes.
	var sid := ResourceUID.text_to_id(UNKNOWN_TOK)
	var path_of_invalid := ResourceUID.get_id_path(ResourceUID.INVALID_ID)
	_p("diag_queried_id=%d diag_queried_tok=%s invalid_id=%d" % [
		sid, UNKNOWN_TOK, ResourceUID.INVALID_ID])
	_p("get_id_path_invalid_empty=%s invalid_has_id=%s" % [
		_b(path_of_invalid == ""), _b(ResourceUID.has_id(ResourceUID.INVALID_ID))])
	_p("has_cache=%s" % _b(FileAccess.file_exists("res://.godot/uid_cache.bin")))
	_emit("diag")
