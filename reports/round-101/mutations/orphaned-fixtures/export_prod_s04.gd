extends SceneTree
# r101 E4 — export_prod scenario 04: main-scene swap + `--main-pack` run receipt.
#
# Claim (C1 scenario 04): a production-shaped project can be exported headless so
# that the pack's boot main scene differs from the project's editor default, and
# `godot --headless --main-pack out.pck --quit-after N` then runs the swapped
# scene (stdout pin) with exit 0.
#
# Measured mechanics on Godot 4.7.2.stable.arch_linux.ed1daf0bf:
#   * The Linux/X11 preset option `application/run/main_scene` does NOT reach a
#     `--export-pack` PCK: the packed project.binary still carries the
#     project.godot value (observed hex: application/run/main_scene ->
#     "res://main.tscn" with the preset option asking for alt_main.tscn).
#     Arm `preset-override` pins that inertness as `preset_effective=false`.
#   * The lever that works: rewrite `application/run/main_scene` in the scratch
#     project.godot between the two states, export, then restore the editor
#     default. The already-written pack keeps the build-time main scene.
#   * `--main-pack <abs.pck> --quit-after 30` boots the pack with exit 0 and the
#     scene's stdout receipts on stdout (engine banner first), stderr empty.
#
# Launch shape (battery convention):
#   godot --headless --path <scratch-proj> --script res://export_prod_s04.gd \
#     -- [--arm=<name>] [--keep]
# Arms (exactly one PASS line on stdout for the two observation arms):
#   swap            (default) positive: swapped pack boots alt scene; restored
#                   project.godot runs main scene in a direct run.
#   preset-override observation: preset option present, project default not
#                   swapped -> pack still boots main scene.
#   forged-swap     negative control: packs the UNSWAPPED project, then applies
#                   the swap assertion; must reject (exit 2, one stderr ERROR
#                   line, no PASS line).
#
# Scratch lives under user:// (globalized), NOT /tmp: on the round-101 host a
# tmpfs quota returned EDQUOT ("tee: /tmp/r101-E4/exp_dbg.log: Disk quota
# exceeded") and silently truncated export outputs (60,751,872 B partial
# template copy of a 73,519,416 B file; a 3424 B PCK cut to 1740 B). user://
# sits on this repo's volume and is not subject to that quota.
#
# No instance ids / addresses / process tokens are printed. Pack sha256 and byte
# sizes are diagnostics `[s04] ...` lines, not part of the PASS signature.

const BASE_TAIL := "r101e4_s04"
const ALT_LINE_FMT := "[s04-alt] swapped=true frames=%d"
const MAIN_LINE_FMT := "[s04-main] default=true frames=%d"

const MAIN_SRC := "extends Node\nvar frames := 0\nfunc _process(_delta: float) -> void:\n\tframes += 1\n\tprint(\"" + MAIN_LINE_FMT + "\" % frames)\n\tif frames >= 3:\n\t\tget_tree().quit(0)\n"
const ALT_SRC := "extends Node\nvar frames := 0\nfunc _process(_delta: float) -> void:\n\tframes += 1\n\tprint(\"" + ALT_LINE_FMT + "\" % frames)\n\tif frames >= 3:\n\t\tget_tree().quit(0)\n"

var _base := ""
var _proj := ""
var _out := ""
var _godot := ""
var _keep := false

func _initialize() -> void:
	var arm := "swap"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
		elif a == "--keep":
			_keep = true
	_godot = OS.get_executable_path()
	_base = OS.get_user_data_dir() + "/" + BASE_TAIL
	_proj = _base + "/proj"
	_out = _base + "/out"
	match arm:
		"swap": _arm_swap()
		"preset-override": _arm_preset_override()
		"forged-swap": _arm_forged_swap()
		_:
			printerr("ERROR: export_prod_s04 unknown arm: %s" % arm)
			quit(2)

# -- arms ---------------------------------------------------------------------

func _arm_swap() -> void:
	_reset()
	_write_project("res://main.tscn", false)
	if not _read(_proj + "/project.godot").contains("run/main_scene=\"res://main.tscn\""):
		_fail("scratch project.godot lost the editor-default main scene")
		return
	_write_project("res://alt_main.tscn", false)
	var exported := _export_pack("swap")
	if not exported:
		return
	var packed := _run_pack("swap")
	if packed.rc != 0:
		_fail("--main-pack swapped pack exited rc=%d (want 0)" % packed.rc)
		return
	_write_project("res://main.tscn", false)
	var direct := _child("direct", "--path \"%s\" --quit-after 30" % _proj, 120)
	if direct.rc != 0:
		_fail("direct project run exited rc=%d (want 0)" % direct.rc)
		return
	var swapped := _count_prefix(packed.out, "[s04-alt] ")
	var packed_default := _count_prefix(packed.out, "[s04-main] ")
	var direct_default := _count_prefix(direct.out, "[s04-main] ")
	var direct_swapped := _count_prefix(direct.out, "[s04-alt] ")
	if swapped != 3 or packed_default != 0:
		_fail("swap assertion failed: expected 3 swapped-scene receipts from --main-pack, got swapped=%d default=%d" % [swapped, packed_default])
		return
	if direct_default != 3 or direct_swapped != 0:
		_fail("swap assertion failed: expected 3 default-scene receipts from the restored direct run, got default=%d swapped=%d" % [direct_default, direct_swapped])
		return
	if not _has_receipt_set(packed.out, ALT_LINE_FMT) or not _has_receipt_set(direct.out, MAIN_LINE_FMT):
		_fail("swap assertion failed: receipt line set is not frames=1,2,3 for both runs")
		return
	_diag("swap")
	_cleanup()
	print("PASS export_prod_s04 swap=true pck_magic=GDPC pack_rc=0 pack_swapped=3 pack_default=0 direct_rc=0 direct_default=3 direct_swapped=0")
	quit(0)

func _arm_preset_override() -> void:
	_reset()
	_write_project("res://main.tscn", true)
	var exported := _export_pack("ovr")
	if not exported:
		return
	var packed := _run_pack("ovr")
	if packed.rc != 0:
		_fail("--main-pack preset-override pack exited rc=%d (want 0)" % packed.rc)
		return
	var packed_default := _count_prefix(packed.out, "[s04-main] ")
	var packed_swapped := _count_prefix(packed.out, "[s04-alt] ")
	if packed_default != 3 or packed_swapped != 0:
		_fail("preset-override observation changed: expected the inert preset to still boot 3 default receipts, got default=%d swapped=%d" % [packed_default, packed_swapped])
		return
	_diag("ovr")
	_cleanup()
	print("PASS export_prod_s04 preset_effective=false pck_magic=GDPC pack_rc=0 pack_default=3 pack_swapped=0")
	quit(0)

func _arm_forged_swap() -> void:
	# Export the UNSWAPPED project (editor default main scene), then apply the
	# positive swap assertion: it must reject, proving the assertion is not
	# vacuous and a forged "swapped" receipt cannot pass.
	_reset()
	_write_project("res://main.tscn", false)
	var exported := _export_pack("forged")
	if not exported:
		return
	var packed := _run_pack("forged")
	if packed.rc != 0:
		_fail("--main-pack forged pack exited rc=%d (want 0)" % packed.rc)
		return
	var swapped := _count_prefix(packed.out, "[s04-alt] ")
	var packed_default := _count_prefix(packed.out, "[s04-main] ")
	_cleanup()
	if swapped != 3 or packed_default != 0:
		_fail("swap assertion failed: expected 3 swapped-scene receipts from --main-pack, got swapped=%d default=%d" % [swapped, packed_default])
		return
	print("PASS export_prod_s04 forged_swap_unrejected=true")
	quit(0)

# -- steps --------------------------------------------------------------------

func _export_pack(tag: String) -> bool:
	var pck := _out + "/" + tag + ".pck"
	var res := _child("exp_" + tag, "--path \"%s\" --export-pack \"Linux/X11\" \"%s\"" % [_proj, pck], 180)
	if res.rc != 0:
		_fail("--export-pack %s exited rc=%d (want 0)" % [tag, res.rc])
		return false
	var head := _head4(pck)
	if head != "GDPC":
		_fail("exported %s.pck magic=%s (want GDPC)" % [tag, head])
		return false
	return true

func _run_pack(tag: String) -> Dictionary:
	return _child("run_" + tag, "--main-pack \"%s\" --quit-after 30" % (_out + "/" + tag + ".pck"), 120)

func _diag(tag: String) -> void:
	var pck := _out + "/" + tag + ".pck"
	print("[s04] arm=%s pck_bytes=%d pck_sha256=%s" % [tag, _size(pck), FileAccess.get_sha256(pck)])
	print("[s04] arm=%s run_stdout_bytes=%d run_stderr_bytes=%d direct_stdout_bytes=%d" % [
		tag, _size(_base + "/run_" + tag + ".out"), _size(_base + "/run_" + tag + ".err"), _size(_base + "/direct.out")])

# -- child process plumbing ---------------------------------------------------

func _child(tag: String, godot_args: String, bound_s: int) -> Dictionary:
	var out_f := _base + "/" + tag + ".out"
	var err_f := _base + "/" + tag + ".err"
	var rc_f := _base + "/" + tag + ".rc"
	var tmp_dir := _base + "/tmp"
	DirAccess.make_dir_recursive_absolute(tmp_dir)
	# TMPDIR is redirected into the scratch tree: on the round-101 host a tmpfs
	# quota on /tmp returned EDQUOT while Godot export/import temp files were
	# being written (observed: a 1740 B truncated PCK next to a 3424 B complete
	# one, and one ovr arm with pck_bytes=3264 / child stderr=271 B). Scratch
	# on user:// is not subject to that quota.
	#
	# OS.execute wraps the call in its own `sh -c --` layer, so a bare `$?`
	# would be expanded by the WRAPPER (always 0) before the inner sh runs;
	# the escaped `\$?` survives to the inner sh and records the child's real
	# exit code (same escape as corpus/fixtures/phys2d_backends.gd).
	var cmd := "TMPDIR=\"%s\" timeout %d \"%s\" --headless %s >\"%s\" 2>\"%s\"; echo \\$? >\"%s\"" % [
		tmp_dir, bound_s, _godot, godot_args, out_f, err_f, rc_f]
	OS.execute("/bin/sh", ["-c", cmd], [], false, false)
	var rc_text := FileAccess.get_file_as_string(rc_f).strip_edges()
	return {
		"rc": rc_text.to_int() if rc_text != "" else -99,
		"out": FileAccess.get_file_as_string(out_f),
		"err": FileAccess.get_file_as_string(err_f),
	}

# -- scratch project ----------------------------------------------------------

func _write_project(main_scene: String, preset_override: bool) -> void:
	DirAccess.make_dir_recursive_absolute(_proj)
	DirAccess.make_dir_recursive_absolute(_out)
	_write(_proj + "/project.godot", "[application]\nconfig/name=\"R101E4Prod\"\nconfig/features=PackedStringArray(\"4.7\")\nrun/main_scene=\"%s\"\n" % main_scene)
	var opts := "binary_format/architecture=\"x86_64\"\n"
	if preset_override:
		opts += "application/run/main_scene=\"res://alt_main.tscn\"\n"
	_write(_proj + "/export_presets.cfg", "[preset.0]\nname=\"Linux/X11\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\ninclude_filter=\"\"\nexclude_filter=\"\"\nexport_path=\"\"\n\n[preset.0.options]\n" + opts)
	_write(_proj + "/main.gd", MAIN_SRC)
	_write(_proj + "/alt.gd", ALT_SRC)
	_write(_proj + "/main.tscn", _scene_text("MainScene", "res://main.gd"))
	_write(_proj + "/alt_main.tscn", _scene_text("AltMainScene", "res://alt.gd"))

func _scene_text(node_name: String, script_path: String) -> String:
	return "[gd_scene load_steps=2 format=3]\n\n[ext_resource type=\"Script\" path=\"%s\" id=\"1\"]\n\n[node name=\"%s\" type=\"Node\"]\nscript = ExtResource(\"1\")\n" % [script_path, node_name]

# -- io helpers ---------------------------------------------------------------

func _wipe() -> void:
	OS.execute("rm", ["-rf", _base], [], false, false)

func _reset() -> void:
	# Every arm starts from an empty scratch tree: a stale .rc/.out from a
	# previously killed child must never be re-readable as fresh evidence.
	_wipe()
	DirAccess.make_dir_recursive_absolute(_proj)
	DirAccess.make_dir_recursive_absolute(_out)

func _cleanup() -> void:
	if not _keep:
		_wipe()

func _write(path: String, text: String) -> void:
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string(text)
	f.close()

func _read(path: String) -> String:
	return FileAccess.get_file_as_string(path)

func _size(path: String) -> int:
	if not FileAccess.file_exists(path):
		return -1
	var f := FileAccess.open(path, FileAccess.READ)
	var n := f.get_length()
	f.close()
	return n

func _head4(path: String) -> String:
	if not FileAccess.file_exists(path):
		return "<missing>"
	var f := FileAccess.open(path, FileAccess.READ)
	var head := f.get_buffer(4).get_string_from_ascii()
	f.close()
	return head

func _count_prefix(text: String, prefix: String) -> int:
	var n := 0
	for line in text.split("\n"):
		if line.strip_edges().begins_with(prefix):
			n += 1
	return n

func _has_receipt_set(text: String, fmt: String) -> bool:
	for i in [1, 2, 3]:
		var needle := fmt % i
		var hit := false
		for line in text.split("\n"):
			if line.strip_edges() == needle:
				hit = true
				break
		if not hit:
			return false
	return true

func _fail(msg: String) -> void:
	printerr("ERROR: export_prod_s04 " + msg)
	quit(2)
