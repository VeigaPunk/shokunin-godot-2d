extends SceneTree
# res_uid_s04 - r104 C1 (seat E4): ResourceUID add/remove/persistence.
#
# Scenario: custom UID lifecycle and cross-process persistence, measured
# against a scratch child project, with every engine diagnostic confined to
# nested logs (nested Godot output is never echoed - the export_div_s01 rule:
# classify_process rejects any line carrying "ERROR:").
#
# Measured laws (godot 4.7.2.stable.arch_linux.ed1daf0bf, 2026-10-18):
#
#   * The runtime authority for uid:// resolution is the BINARY cache
#     `res://.godot/uid_cache.bin`, written by an EDITOR process
#     (`--editor --quit`). Format: u32 record count, then repeated
#     <u64 id><u32 path_len><path bytes>; ids are < 2^63. (The count header
#     was initially misread as a version - see the shard's correction row.)
#   * The text sidecar `<name>.gd.uid` (content `uid://<base32>\n`) is written
#     by the editor and is the editor's *input*: with the sidecar present but
#     the cache removed, a plain `--script` process reports has_id=false -
#     the text file alone is NOT a runtime authority. Re-running the editor
#     rebuilds the cache from the sidecar.
#   * `ResourceUID.add_id/set_id/remove_id` return void; misuse is an engine
#     ERROR (not a silent no-op): duplicate id -> resource_uid.cpp:164,
#     set_id on an unknown id -> :178, remove_id on an unknown id -> :232,
#     get_id_path/uid_to_path on an unknown id -> :214 (message
#     `Unrecognized UID: "<text>"`). A failed duplicate add leaves the FIRST
#     path bound. Two different ids bound to one path is accepted silently.
#   * Collision class (verbatim, editor scan): two sidecars carrying the same
#     UID text emit
#       `WARNING: UID duplicate detected between <pathA> and <pathB>.`
#     and the cache keeps ONE record for the contested id; the surviving
#     path is whichever the scan bound last (observed beta over alpha).
#   * `path_to_uid()` echoes its argument back when the path is unregistered
#     (it is not an error path), and `text_to_id("uid://")` is 0 while
#     `text_to_id("")` / `text_to_id("uid://<invalid>")` are -1.
#
# Arms (one arm per process, one PASS line per arm; battery launch shape):
#   godot --headless --path <fixture proj> --script res://res_uid_s04.gd -- --arm=<arm>
#
#   persist   -> res_uid_s04_persist   (editor scan + 2 reader processes)
#   classes   -> res_uid_s04_classes   (in-process lattice + 1 misuse child)
#   collision -> res_uid_s04_collision (editor scan over duplicate sidecars)
#
# Scratch policy: <root>/uid_s04/<arm>/{proj,logs}; <root> is the first
# candidate of $RES_UID_ROOT, $TMPDIR, /var/tmp/uid_s04, /tmp/uid_s04 that
# passes a 4096-byte write+readback probe (host /tmp carries an EDQUOT quota,
# so /var/tmp wins on this host). Host paths appear only in RES_UID_DIAG
# lines, never inside pinned PASS text.

const VARIANT := "uid_s04"
const ALPHA := "res://alpha.gd"
const BETA := "res://beta.gd"

const PROJECT_GODOT := "config_version=5\n\n[application]\nconfig/name=\"UidS04\"\nconfig/features=PackedStringArray(\"4.7\")\n"
const ALPHA_GD := "extends Node\n"

var arm := ""
var _root := ""


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	if arm == "":
		arm = "persist"
	call_deferred("_run")


func _run() -> void:
	_root = _pick_root()
	_diag("root", _root)
	if _root == "":
		_fail("no_writable_scratch_root")
		return
	match arm:
		"persist":
			_arm_persist()
		"classes":
			_arm_classes()
		"collision":
			_arm_collision()
		_:
			_fail("unknown_arm")


# ------------------------------------------------------------------ receipts

func _fail(reason: String) -> void:
	print("FAIL res_uid s04 arm=%s reason=%s" % [arm, reason])
	quit(1)


func _verdict(fields: PackedStringArray, bad: String) -> void:
	if bad == "":
		print("PASS res_uid s04 arm=%s %s" % [arm, " ".join(fields)])
		quit(0)
	else:
		print("FAIL res_uid s04 arm=%s reason=%s %s" % [arm, bad, " ".join(fields)])
		quit(1)


func _diag(key: String, value) -> void:
	print("RES_UID_DIAG %s %s=%s" % [arm, key, str(value)])


# ------------------------------------------------------------------- scratch

func _pick_root() -> String:
	var candidates: PackedStringArray = []
	if OS.get_environment("RES_UID_ROOT") != "":
		candidates.append(OS.get_environment("RES_UID_ROOT"))
	if OS.get_environment("TMPDIR") != "":
		candidates.append(OS.get_environment("TMPDIR").path_join(VARIANT))
	candidates.append("/var/tmp/" + VARIANT)
	candidates.append("/tmp/" + VARIANT)
	for c in candidates:
		DirAccess.make_dir_recursive_absolute(c)
		if _probe_writable(c):
			return c
	return ""


func _probe_writable(dir: String) -> bool:
	var payload := PackedByteArray()
	payload.resize(4096)
	payload.fill(65)
	var probe := dir.path_join(".probe")
	var f := FileAccess.open(probe, FileAccess.WRITE)
	if f == null:
		return false
	f.store_buffer(payload)
	f.close()
	var ok := FileAccess.get_file_as_bytes(probe).size() == payload.size()
	DirAccess.remove_absolute(probe)
	return ok


func _godot() -> String:
	var exe := OS.get_executable_path()
	return exe if exe != "" else "/usr/bin/godot"


func _q(s: String) -> String:
	return "'" + s.replace("'", "'\\''") + "'"


func _arm_dir() -> String:
	return _root.path_join(VARIANT).path_join(arm)


func _proj_dir() -> String:
	return _arm_dir().path_join("proj")


func _log_path(name: String) -> String:
	return _arm_dir().path_join("logs").path_join(name + ".log")


func _mkdir(path: String) -> void:
	DirAccess.make_dir_recursive_absolute(path)


func _write_text(path: String, text: String) -> bool:
	_mkdir(path.get_base_dir())
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		return false
	f.store_string(text)
	f.close()
	return true


func _nested(args: PackedStringArray, log_name: String) -> int:
	var log_path := _log_path(log_name)
	_mkdir(log_path.get_base_dir())
	var parts := PackedStringArray([_q(_godot())])
	for a in args:
		parts.append(_q(a))
	var body := "exec > " + _q(log_path) + " 2>&1\n" + " ".join(parts)
	_diag("nested_" + log_name, " ".join(parts))
	return OS.execute("/usr/bin/sh", PackedStringArray(["-c", body]))


func _log_text(name: String) -> String:
	return FileAccess.get_file_as_string(_log_path(name))


# ------------------------------------------------------------------ projects

func _wipe_dir(path: String) -> void:
	var d := DirAccess.open(path)
	if d == null:
		return
	for name in d.get_files():
		DirAccess.remove_absolute(path.path_join(name))
	for name in d.get_directories():
		_wipe_dir(path.path_join(name))
		DirAccess.remove_absolute(path.path_join(name))


func _stage() -> bool:
	var proj := _proj_dir()
	# A stale cache/sidecar/reader from an earlier arm run must not leak in:
	# every generated .gd gets its own sidecar + cache record, so a leftover
	# reader.gd would inflate the cache count and break row determinism.
	_wipe_dir(proj)
	_mkdir(proj)
	_mkdir(_arm_dir().path_join("logs"))
	return _write_text(proj.path_join("project.godot"), PROJECT_GODOT) \
		and _write_text(proj.path_join("alpha.gd"), ALPHA_GD)


func _editor_scan(log_name: String) -> int:
	return _nested(PackedStringArray(["--headless", "--path", _proj_dir(), "--editor", "--quit"]), log_name)


func _read_sidecar(name: String) -> String:
	var p := _proj_dir().path_join(name)
	if not FileAccess.file_exists(p):
		return ""
	return FileAccess.get_file_as_string(p).strip_edges()


# uid_cache.bin: u32 record count, then <u64 id><u32 len><path> records.
func _parse_cache(path: String) -> Dictionary:
	var out := {"ok": false, "declared": 0, "records": []}
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return out
	var total := f.get_length()
	if total < 4:
		f.close()
		return out
	out["declared"] = f.get_32()
	var recs := []
	while f.get_position() + 12 <= total:
		var id := f.get_64()
		var n := f.get_32()
		if n <= 0 or n > 4096 or f.get_position() + n > total:
			break
		recs.append({"id": id, "path": f.get_buffer(n).get_string_from_utf8()})
	f.close()
	out["records"] = recs
	out["ok"] = true
	return out


func _cache_path() -> String:
	return _proj_dir().path_join(".godot").path_join("uid_cache.bin")


func _cache_id_for(path_wanted: String) -> int:
	var c := _parse_cache(_cache_path())
	for r in c["records"]:
		if r["path"] == path_wanted:
			return r["id"]
	return -1


func _write_reader(uid_text: String) -> bool:
	var src := """extends SceneTree
func _initialize() -> void:
	var want := "%s"
	var id := ResourceUID.text_to_id(want)
	print("READ has=", ResourceUID.has_id(id), " path='", ResourceUID.get_id_path(id), "' text=", ResourceUID.id_to_text(id))
	print("READ cache=", FileAccess.file_exists("res://.godot/uid_cache.bin"), " uidfile=", FileAccess.file_exists("res://alpha.gd.uid"))
	quit(0)
""" % uid_text
	return _write_text(_proj_dir().path_join("reader.gd"), src)


func _run_reader(log_name: String) -> String:
	var rc := _nested(PackedStringArray(["--headless", "--path", _proj_dir(), "--script", "res://reader.gd"]), log_name)
	_diag(log_name + "_rc", rc)
	for line in _log_text(log_name).split("\n"):
		if line.begins_with("READ has="):
			return line
	return ""


# arm=persist: editor scan writes sidecar + cache; a NEW process reads the
# cache and resolves the UID to the same path. Removing the cache while the
# sidecar stays proves the text file alone is not a runtime authority.
func _arm_persist() -> void:
	if not _stage():
		_fail("stage_failed")
		return
	var ed_rc := _editor_scan("editor")
	var uid_text := _read_sidecar("alpha.gd.uid")
	var cache := _parse_cache(_cache_path())
	var cache_id := _cache_id_for(ALPHA)
	var tid := ResourceUID.text_to_id(uid_text)
	# uid_text is minted fresh by the editor scan, so it is diag-only: pinned
	# PASS text must carry no run-random token.
	_diag("uid_text", uid_text)
	var f := PackedStringArray()
	# alpha.gd alone is scanned: the cache holds exactly one record, so the
	# header count and the parsed record list must agree.
	f.append("cache_records=%d" % cache["records"].size())
	f.append("cache_declared=%d" % cache["declared"])
	f.append("cache_consistent=%s" % str(cache["declared"] == cache["records"].size()).to_lower())
	f.append("cache_id_match=%s" % str(cache_id != -1 and cache_id == tid).to_lower())
	f.append("roundtrip=%s" % str(ResourceUID.id_to_text(tid) == uid_text).to_lower())
	_write_reader(uid_text)
	var line_a := _run_reader("reader_cache")
	var has_a := line_a.contains("has=true") and line_a.contains("path='" + ALPHA + "'")
	f.append("reader_has=%s" % str(has_a).to_lower())
	f.append("reader_path=%s" % (ALPHA if has_a else "<other>"))
	# Same project, cache removed, sidecar kept -> new process must not resolve.
	DirAccess.remove_absolute(_cache_path())
	var line_b := _run_reader("reader_nocache")
	var has_b := line_b.contains("has=true")
	f.append("nocache_has=%s" % str(has_b).to_lower())
	f.append("uidfile_only_authority=%s" % str(has_b).to_lower())
	var bad := ""
	if ed_rc != 0:
		bad = "editor_rc"
	elif uid_text == "" or not uid_text.begins_with("uid://"):
		bad = "sidecar_missing"
	elif not cache["ok"] or cache["records"].size() == 0:
		bad = "cache_missing"
	elif cache["declared"] != cache["records"].size():
		bad = "cache_count_mismatch"
	elif cache_id != tid:
		bad = "cache_id_mismatch"
	elif ResourceUID.id_to_text(tid) != uid_text:
		bad = "text_roundtrip"
	elif not has_a:
		bad = "reader_did_not_resolve"
	elif has_b:
		bad = "sidecar_alone_resolved"
	_verdict(f, bad)


# arm=classes: in-process lattice (only the non-erroring calls) plus one
# nested misuse child whose engine diagnostics stay in its log.
func _arm_classes() -> void:
	if not _stage():
		_fail("stage_failed")
		return
	var f := PackedStringArray()
	var a := ResourceUID.create_id()
	var b := ResourceUID.create_id()
	var c := ResourceUID.create_id()
	var distinct: bool = a != b and b != c and a != c
	var positive: bool = a > 0 and b > 0 and c > 0
	f.append("create_distinct=%s" % str(distinct).to_lower())
	f.append("create_positive=%s" % str(positive).to_lower())
	var t := ResourceUID.id_to_text(a)
	f.append("text_roundtrip=%s" % str(ResourceUID.text_to_id(t) == a).to_lower())
	f.append("invalid_text=%d" % ResourceUID.text_to_id("uid://<invalid>"))
	f.append("empty_text=%d" % ResourceUID.text_to_id(""))
	f.append("uidroot_text=%d" % ResourceUID.text_to_id("uid://"))
	f.append("invalid_id_text=%s" % ResourceUID.id_to_text(-1))
	f.append("path_echo=%s" % str(ResourceUID.path_to_uid("res://unregistered.gd") == "res://unregistered.gd").to_lower())
	var cid := ResourceUID.create_id_for_path(BETA)
	var cid_again := ResourceUID.create_id_for_path(BETA)
	f.append("cidf_deterministic=%s" % str(cid > 0 and cid == cid_again).to_lower())
	f.append("cidf_pure=%s" % str(not ResourceUID.has_id(cid)).to_lower())
	# Two ids bound to one path: accepted silently (no engine error).
	ResourceUID.add_id(a, ALPHA)
	ResourceUID.add_id(b, ALPHA)
	var same_path_ok := ResourceUID.has_id(a) and ResourceUID.has_id(b)
	f.append("same_path_two_ids=%s" % str(same_path_ok).to_lower())
	# Misuse child: every ERROR-producing class, isolated in a nested process.
	var src := """extends SceneTree
func _initialize() -> void:
	var x := ResourceUID.create_id()
	var y := ResourceUID.create_id()
	ResourceUID.add_id(x, "res://alpha.gd")
	ResourceUID.add_id(x, "res://beta.gd")
	print("M dup_keeps=", ResourceUID.get_id_path(x))
	ResourceUID.set_id(999, "res://ghost.gd")
	print("M ghost_has=", ResourceUID.has_id(999))
	ResourceUID.remove_id(999)
	ResourceUID.remove_id(x)
	ResourceUID.remove_id(x)
	print("M removed_has=", ResourceUID.has_id(x))
	print("M other_still=", ResourceUID.has_id(y))
	quit(0)
"""
	_write_text(_proj_dir().path_join("misuse.gd"), src)
	var rc := _nested(PackedStringArray(["--headless", "--path", _proj_dir(), "--script", "res://misuse.gd"]), "misuse")
	_diag("misuse_rc", rc)
	var log := _log_text("misuse")
	var keeps := ""
	var ghost := "unknown"
	for line in log.split("\n"):
		if line.begins_with("M dup_keeps="):
			keeps = line.trim_prefix("M dup_keeps=").strip_edges()
		elif line.begins_with("M ghost_has="):
			ghost = line.trim_prefix("M ghost_has=").strip_edges()
	f.append("dup_add_keeps_first=%s" % str(keeps == ALPHA).to_lower())
	f.append("dup_add_err=%s" % str(log.contains("resource_uid.cpp:164")).to_lower())
	f.append("set_unknown_err=%s" % str(log.contains("resource_uid.cpp:178")).to_lower())
	f.append("remove_unknown_err=%s" % str(log.contains("resource_uid.cpp:232")).to_lower())
	f.append("ghost_has=%s" % ghost)
	var bad := ""
	if not distinct or not positive:
		bad = "create_id"
	elif ResourceUID.text_to_id(t) != a:
		bad = "text_roundtrip"
	elif ResourceUID.text_to_id("uid://<invalid>") != -1 or ResourceUID.text_to_id("") != -1:
		bad = "invalid_text_class"
	elif ResourceUID.text_to_id("uid://") != 0:
		bad = "uidroot_class"
	elif not same_path_ok:
		bad = "same_path_two_ids"
	elif keeps != ALPHA:
		bad = "dup_add_not_first_wins"
	elif not log.contains("resource_uid.cpp:164"):
		bad = "dup_add_silent"
	elif not log.contains("resource_uid.cpp:178"):
		bad = "set_unknown_silent"
	elif not log.contains("resource_uid.cpp:232"):
		bad = "remove_unknown_silent"
	elif ghost != "false":
		bad = "ghost_bound"
	_verdict(f, bad)


# arm=collision: two sidecars carrying the SAME uid text. The editor scan warns
# verbatim and the cache keeps one record for the contested id; a new process
# resolves that id to the cached winner.
func _arm_collision() -> void:
	if not _stage():
		_fail("stage_failed")
		return
	if not _write_text(_proj_dir().path_join("beta.gd"), ALPHA_GD):
		_fail("stage_beta_failed")
		return
	var dup_text := ResourceUID.id_to_text(ResourceUID.create_id())
	_write_text(_proj_dir().path_join("alpha.gd.uid"), dup_text + "\n")
	_write_text(_proj_dir().path_join("beta.gd.uid"), dup_text + "\n")
	var ed_rc := _editor_scan("editor_dup")
	var log := _log_text("editor_dup")
	var warn := ""
	for line in log.split("\n"):
		if line.contains("UID duplicate detected between"):
			warn = line.strip_edges()
	_diag("dup_warning", warn)
	var cache := _parse_cache(_cache_path())
	var winner := ""
	var hits := 0
	for r in cache["records"]:
		if r["id"] == ResourceUID.text_to_id(dup_text):
			hits += 1
			winner = r["path"]
	var sorted_pair := ALPHA + "," + BETA
	var warn_pair_ok := warn.contains(ALPHA) and warn.contains(BETA)
	_write_reader(dup_text)
	var line_a := _run_reader("reader_dup")
	var reader_winner := ""
	var m := line_a.find("path='")
	if m != -1:
		reader_winner = line_a.substr(m + 6).split("'")[0]
	var f := PackedStringArray()
	f.append("dup_warn=true")
	f.append("pair=%s" % sorted_pair)
	f.append("records=%d" % cache["records"].size())
	f.append("dup_records=%d" % hits)
	f.append("dup_text_roundtrip=%s" % str(ResourceUID.id_to_text(ResourceUID.text_to_id(dup_text)) == dup_text).to_lower())
	f.append("winner_in_pair=%s" % str(winner == ALPHA or winner == BETA).to_lower())
	f.append("reader_matches_winner=%s" % str(reader_winner != "" and reader_winner == winner).to_lower())
	var bad := ""
	if ed_rc != 0:
		bad = "editor_rc"
	elif warn == "" or not warn_pair_ok:
		bad = "duplicate_warning_missing"
	elif hits != 1:
		bad = "contested_record_count"
	elif winner != ALPHA and winner != BETA:
		bad = "winner_not_in_pair"
	elif reader_winner == "" or reader_winner != winner:
		bad = "reader_winner_mismatch"
	_verdict(f, bad)
