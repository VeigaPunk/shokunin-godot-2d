extends SceneTree
# r104-E2 — ResourceLoader load-cache identity + cache_mode busting + post-mutation
# reload classes on Godot 4.7.2 headless.  Owner: KEY=E2 (round 104, amended p4).
#
# Launch shape (battery convention):
#   godot --headless --path <scratch> --script res://res_uid_s02.gd -- --arm=<arm>
# Exactly ONE `PASS res_uid_s02 <arm> k=v ...` line per arm; FAIL lines name the
# first violated expectation.  No instance ids / RIDs / addresses / paths are
# printed: every token is a boolean, a small enum, or a fixed literal, so the
# receipt is byte-stable across processes and runs.
#
# Measured laws encoded here (all [M] on 4.7.2.stable.arch_linux.ed1daf0bf, see
# reports/round-104/r104-E2.md):
#   L1 CACHE_MODE_REUSE (the default, and an explicit 1) is identity-stable:
#      every load of a cached path returns the SAME object (is_same + instance id)
#   L2 CACHE_MODE_IGNORE (0) returns a fresh object that is NOT the cached one and
#      does NOT displace the cache entry; the ignored object still carries
#      resource_path, and two IGNORE loads are distinct from each other
#   L3 CACHE_MODE_REPLACE (2) returns the SAME object as the cached one and
#      refreshes its content IN PLACE — every alias of the cached object observes
#      the new content, and a later REUSE returns that refreshed object
#   L4 the _DEEP pair (IGNORE_DEEP=3 / REPLACE_DEEP=4) reproduces the plain pair's
#      top-level identity semantics on a cache hit (ignore: distinct, cache kept;
#      replace: identity-stable)
#   L5 after an external rewrite of the file, default REUSE keeps serving the STALE
#      cached content; REPLACE is the only mode that re-reads it
#   L6 after the file is DELETED under a cached entry, REUSE and REPLACE both keep
#      serving the stale cached object (REPLACE does not evict; it re-reads, fails,
#      and leaves the cache as it was) while IGNORE returns null; each failing
#      REPLACE emits a fixed 3-line engine ERROR block on stderr (declared in the
#      battery's expected_errors allowlist for the deleted_* rows)
#   L7 ResourceLoader.exists() is cache-contaminated: true for a cached path whose
#      file is gone, false for a path that was never cached and does not exist
#   L8 the cache is per-process: a second process loading the same path parses the
#      current bytes; within that process the L5/L6 laws hold again
#   L9 the identity lattice is path-scheme independent (res:// and user:// behave
#      identically for REUSE/IGNORE/REPLACE on the same content)
#
# The load-refusal classes (missing file / directory / empty path / unknown
# extension -> null, has_cached false, uid -1) are deliberately NOT an arm here:
# they belong to the res_uid_s01 id<->path round-trip claim (KEY=E1).  They were
# measured during development and are reported in r104-E2.md only.
#
# Arms: reuse ignore replace deep bust deleted resdir xproc_seed xproc_read

const BASE := "user://res_uid_s02"
const RES_ROOT := "res://r104_s02_root.tres"

var arm := ""

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	_run.call_deferred()

func _run() -> void:
	match arm:
		"reuse": _arm_reuse()
		"ignore": _arm_ignore()
		"replace": _arm_replace()
		"deep": _arm_deep()
		"bust": _arm_bust()
		"deleted": _arm_deleted()
		"resdir": _arm_resdir()
		"xproc_seed": _arm_xproc_seed()
		"xproc_read": _arm_xproc_read()
		_: print("FAIL res_uid_s02 arm=%s reason=unknown_arm" % arm)
	quit(0)

# ------------------------------------------------------------------ helpers

func _b(v: bool) -> String:
	return "true" if v else "false"

func _p(tokens: String) -> void:
	print("PASS res_uid_s02 %s %s" % [arm, tokens])

func _fail(tokens: String) -> void:
	print("FAIL res_uid_s02 %s %s" % [arm, tokens])

func _grad(v: int) -> String:
	return "[gd_resource type=\"Gradient\" format=3]\n\n[resource]\ncolors = PackedColorArray(%d, 0, 0, 1, 0, 0, 0, 1)\n" % v

func _write(path: String, text: String) -> bool:
	DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		return false
	f.store_string(text)
	f.close()
	return true

func _red(res) -> String:
	if res == null:
		return "n"
	return "v%d" % int(round(res.colors[0].r))

func _same(a, b) -> bool:
	return is_same(a, b)

# Null-safe accessors: a refused load returns null, and dereferencing it inside a
# --script SceneTree aborts _init WITHOUT reaching quit() — the process then hangs
# until killed instead of exiting non-zero.  Every receipt token must therefore be
# computable from a null object.
func _path_of(res) -> String:
	if res == null:
		return "n"
	return res.resource_path

func _iid_stable(a, b) -> bool:
	if a == null or b == null:
		return false
	return a.get_instance_id() == b.get_instance_id()

func _wipe() -> void:
	for sub in ["", "/v1.tres", "/v2.tres", "/v3.tres", "/v4.tres", "/v5.tres"]:
		DirAccess.remove_absolute(ProjectSettings.globalize_path(BASE + sub))

# ------------------------------------------------------------------ L1 L4

func _arm_reuse() -> void:
	_wipe()
	var p := BASE + "/v1.tres"
	_write(p, _grad(1))
	var a := ResourceLoader.load(p)
	var b := ResourceLoader.load(p)
	var c := ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REUSE)
	var ref := ResourceLoader.get_cached_ref(p)
	var tokens := "cached=%s has_cached=%s reuse_same=%s explicit_reuse_same=%s ref_same=%s iid_stable=%s path=%s" % [
		_b(a != null), _b(ResourceLoader.has_cached(p)), _b(_same(a, b)), _b(_same(a, c)),
		_b(_same(a, ref)), _b(_iid_stable(a, b)),
		_b(_path_of(a) == p)]
	if a == null or not _same(a, b) or not _same(a, c) or not _same(a, ref):
		_fail("reason=reuse_not_identity_stable " + tokens)
		return
	_p(tokens)

func _arm_ignore() -> void:
	_wipe()
	var p := BASE + "/v2.tres"
	_write(p, _grad(2))
	var a := ResourceLoader.load(p)
	var ig := ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_IGNORE)
	var ig2 := ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_IGNORE)
	var ref := ResourceLoader.get_cached_ref(p)
	var back := ResourceLoader.load(p)
	var tokens := "distinct=%s cache_kept=%s ref_kept=%s two_distinct=%s path_kept=%s reuse_after_is_orig=%s has_cached=%s content=%s" % [
		_b(not _same(ig, a)), _b(_same(ref, a)), _b(_same(ref, a)), _b(not _same(ig, ig2)),
		_b(_path_of(ig) == p), _b(_same(back, a)), _b(ResourceLoader.has_cached(p)),
		_red(ig)]
	if ig == null or _same(ig, a) or not _same(ref, a) or not _same(back, a):
		_fail("reason=ignore_displaced_cache " + tokens)
		return
	_p(tokens)

func _arm_replace() -> void:
	_wipe()
	var p := BASE + "/v3.tres"
	_write(p, _grad(1))
	var a := ResourceLoader.load(p)
	_write(p, _grad(2))
	var repl := ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REPLACE)
	var repl_snap := _red(repl)
	var alias_snap := _red(a)
	var after := ResourceLoader.load(p)
	var after_snap := _red(after)
	var cached_snap := _red(ResourceLoader.get_cached_ref(p))
	var tokens := "same=%s refreshed=%s alias_refreshed=%s reuse_after_same=%s cached_now=%s" % [
		_b(_same(repl, a)), repl_snap, alias_snap, _b(_same(after, a)), cached_snap]
	if not _same(repl, a) or repl_snap != "v2" or alias_snap != "v2" \
			or not _same(after, a) or after_snap != "v2" or cached_snap != "v2":
		_fail("reason=replace_not_identity_stable_refresh " + tokens)
		return
	_p(tokens)

func _arm_deep() -> void:
	_wipe()
	var p := BASE + "/v4.tres"
	_write(p, _grad(1))
	var a := ResourceLoader.load(p)
	var igd := ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_IGNORE_DEEP)
	var ref := ResourceLoader.get_cached_ref(p)
	var rpd := ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REPLACE_DEEP)
	var reuse := ResourceLoader.load(p)
	var tokens := "igd_distinct=%s igd_cache_kept=%s igd_ref_is_orig=%s rpd_same=%s reuse_is_rpd=%s" % [
		_b(not _same(igd, a)), _b(_same(ref, a)), _b(_same(ref, a)),
		_b(_same(rpd, a)), _b(_same(reuse, rpd))]
	if _same(igd, a) or not _same(ref, a) or not _same(rpd, a) or not _same(reuse, rpd):
		_fail("reason=deep_modes_diverge_from_plain_pair " + tokens)
		return
	_p(tokens)

# ------------------------------------------------------------------ L5 L6 L7

func _arm_bust() -> void:
	_wipe()
	var p := BASE + "/v5.tres"
	_write(p, _grad(1))
	var a := ResourceLoader.load(p)
	_write(p, _grad(2))
	var stale := ResourceLoader.load(p)
	# Snapshot BEFORE the REPLACE call: REPLACE refreshes the cached object in
	# place, so any alias read after it reports the refreshed content (see L3).
	var stale_snap := _red(stale)
	var stale_same := _same(stale, a)
	var repl := ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REPLACE)
	var repl_snap := _red(repl)
	var alias_snap := _red(a)
	var after := ResourceLoader.load(p)
	var after_snap := _red(after)
	var ign := ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_IGNORE)
	var ign_snap := _red(ign)
	var tokens := "stale_reuse=%s stale_same=%s repl=%s repl_same=%s alias_after_repl=%s after_reuse=%s ign_fresh=%s" % [
		stale_snap, _b(stale_same), repl_snap, _b(_same(repl, a)), alias_snap, after_snap, ign_snap]
	if stale_snap != "v1" or not stale_same or repl_snap != "v2" or alias_snap != "v2" \
			or after_snap != "v2" or ign_snap != "v2":
		_fail("reason=post_mutation_reload_class_mismatch " + tokens)
		return
	_p(tokens)

func _arm_deleted() -> void:
	_wipe()
	var p := BASE + "/v1.tres"
	_write(p, _grad(3))
	var a := ResourceLoader.load(p)
	var removed := DirAccess.remove_absolute(ProjectSettings.globalize_path(p)) == OK
	var reuse := ResourceLoader.load(p)
	var repl := ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REPLACE)
	var ign := ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_IGNORE)
	var tokens := "removed=%s reuse_stale=%s reuse_same=%s repl_stale=%s repl_same=%s repl_evicted=%s ign_null=%s cached_deleted_exists=%s never_exists=%s has_cached=%s" % [
		_b(removed), _red(reuse), _b(_same(reuse, a)), _red(repl), _b(_same(repl, a)),
		_b(not _same(repl, a)), _b(ign == null), _b(ResourceLoader.exists(p)),
		_b(ResourceLoader.exists(BASE + "/never.tres")), _b(ResourceLoader.has_cached(p))]
	if not removed or _red(reuse) != "v3" or not _same(reuse, a) or _red(repl) != "v3" or not _same(repl, a) or ign != null:
		_fail("reason=deleted_file_class_mismatch " + tokens)
		return
	_p(tokens)

func _arm_resdir() -> void:
	var p := RES_ROOT
	var wrote := _write(p, _grad(1))
	var a := ResourceLoader.load(p)
	var b := ResourceLoader.load(p)
	var ig := ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_IGNORE)
	var repl := ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REPLACE)
	_write(p, _grad(2))
	var repl2 := ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REPLACE)
	var repl2_snap := _red(repl2)
	var alias_snap := _red(a)
	var tokens := "wrote=%s reuse_same=%s ign_distinct=%s ign_path_kept=%s repl_same=%s repl_refreshed=%s alias_refreshed=%s" % [
		_b(wrote), _b(_same(a, b)), _b(not _same(ig, a)), _b(_path_of(ig) == p),
		_b(_same(repl, a)), repl2_snap, alias_snap]
	DirAccess.remove_absolute(ProjectSettings.globalize_path(p))
	if not wrote or not _same(a, b) or _same(ig, a) or not _same(repl, a) \
			or repl2_snap != "v2" or alias_snap != "v2":
		_fail("reason=res_scheme_diverges " + tokens)
		return
	_p(tokens)

# ------------------------------------------------------------------ L8

func _arm_xproc_seed() -> void:
	_wipe()
	var p := BASE + "/v1.tres"
	_write(p, _grad(1))
	var a := ResourceLoader.load(p)
	var tokens := "wrote=%s loaded=%s cached=%s" % [_red(a), _red(a), _b(ResourceLoader.has_cached(p))]
	if _red(a) != "v1":
		_fail("reason=seed_load_failed " + tokens)
		return
	_p(tokens)

func _arm_xproc_read() -> void:
	var p := BASE + "/v1.tres"
	var first := ResourceLoader.load(p)
	var first_snap := _red(first)
	var again := ResourceLoader.load(p)
	var same := _same(first, again)
	_write(p, _grad(2))
	var stale := ResourceLoader.load(p)
	var stale_snap := _red(stale)
	var repl := ResourceLoader.load(p, "", ResourceLoader.CACHE_MODE_REPLACE)
	var repl_snap := _red(repl)
	var tokens := "fresh_first=%s same_in_process=%s rewrite_reuse=%s repl=%s" % [
		first_snap, _b(same), stale_snap, repl_snap]
	if first_snap != "v1" or not same or stale_snap != "v1" or repl_snap != "v2":
		_fail("reason=cross_process_or_l5_law_mismatch " + tokens)
		return
	_p(tokens)
