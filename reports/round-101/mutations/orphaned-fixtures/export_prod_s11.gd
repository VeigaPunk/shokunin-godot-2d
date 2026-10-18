extends SceneTree
# r101 export_prod scenario 11 — `--main-pack` headless launch lattice.
#
# Battery launch shape (run_battery.py:1862):
#   godot --headless --path <scratch> --script res://export_prod_s11.gd -- --arm=<name>
#
# The fixture builds a minimal production-shaped Godot project under
# user://r101e11 (override R101_E11_ROOT), exports a PCK with the CLI
# (`--export-pack`, no export templates needed), then launches the pack with
# `--main-pack` from a clean cwd and pins the exact stdout receipts.
#
# Measured laws this probe encodes (engine 4.7.2.stable.arch_linux.ed1daf0bf,
# all observed on this host; see reports/round-101/r101-E11.md):
#   L1 `--export-pack "Linux/X11" <path>` exits 0, prints `savepack` progress
#      lines on stdout and `[ DONE ] savepack`, writes GDPC magic, no templates.
#   L2 `godot --headless --main-pack <pck> --quit-after N` exits 0 and the
#      pack's main scene runs exactly N frames (`[s11] frame=1..N`), with the
#      `_exit_tree` receipt `[s11] exit frames=N`; stdout carries the receipt,
#      stderr is empty.
#   L3 the receipt is pack-borne: the same command from a cwd with no project
#      files still prints it, and a different pack's scene prints its own tag.
#   L4 `--quit-after` is an upper bound, not a frame count: a scene that quits
#      itself after 2 frames ends with frames=2 under `--quit-after 6`.
#   L5 `--quit-after 0` disables the quit (runs forever, no exit receipt).
#   L6 FAILURE IS AN EXIT-0 TRAP: a corrupt-magic or missing pack prints
#      `ERROR: Cannot open resource pack '<path>'.` on stderr and exits 0.
#      Rows must assert the stdout receipt, never the exit code alone.
#   L7 a pack whose `project.binary` entry is empty (observed under tmpfs quota
#      pressure) is readable but has no project settings: the engine falls back
#      to editor mode, prints no receipt, still exits 0.
#
# Arms (recommended battery row order: pack, launch, ladder, alt_main,
# early_quit, corrupt, hang0):
#   pack       fresh export + PCK header/dir guard (`project.binary` > 0 bytes)
#   launch     export-if-stale + `--quit-after 5`, exact receipt list pinned
#   ladder     `--quit-after` 1/2/3/4, frames == N for each
#   alt_main   variant pack whose scene prints scene=alt (pack identity)
#   early_quit variant pack whose scene self-quits at frame 2 under --quit-after 6
#   corrupt    corrupt-magic + missing-path controls (L6 exit-0 trap)
#   hang0      `--quit-after 0` bounded by `timeout 3` (L5), rc 124
#   all        pack(fresh) + launch + ladder + alt_main + early_quit + corrupt
#
# Every arm prints one `PASS export_prod_s11 <arm> k=v ...` line and exits 0;
# failures print `FAIL export_prod_s11 <arm> reasons=<a,b> evidence=...` and exit
# 2 (repo assertion convention). Child stdout/stderr are captured to files and
# never echoed on success, so the parent's own streams stay clean; failures cite
# a bounded, newline-flattened excerpt. No object ids/addresses are printed.
# Pass --keep to leave the generated projects/packs in place, --clean to remove
# the whole work root at exit (default keeps the tiny cache; capture files are
# purged per launch so stale evidence can never be re-read).

var arm := ""
var _keep := false
var _clean := false
var _fail_exit := 2
var _bad: PackedStringArray = []
var _detail := ""
var _root := ""

const PRESET := "Linux/X11"
const S11 := "[s11] "
const PROJECT_SRC := "[application]\n\nconfig/name=\"r101e11\"\nrun/main_scene=\"res://main.tscn\"\nconfig/features=PackedStringArray(\"4.7\")\n"
const PRESET_SRC := "[preset.0]\n\nname=\"Linux/X11\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\ninclude_filter=\"\"\nexclude_filter=\"\"\nexport_path=\"\"\n\n[preset.0.options]\n\nbinary_format/architecture=\"x86_64\"\n"
const SCENE_SRC := "[gd_scene load_steps=2 format=3]\n\n[ext_resource type=\"Script\" path=\"res://main.gd\" id=\"1\"]\n\n[node name=\"Main\" type=\"Node\"]\nscript = ExtResource(\"1\")\n"


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
		elif a == "--keep":
			_keep = true
		elif a == "--clean":
			_clean = true
		elif a.begins_with("--fail-exit="):
			_fail_exit = int(a.substr(12))
	_run.call_deferred()


func _run() -> void:
	# Scratch-root policy: EXPORT_PROD_ROOT (shared lattice root; isolated as
	# <root>/s11), then R101_E11_ROOT, then the engine user-data dir. Never /tmp
	# by default: this host's tmpfs was measurably quota-exhausted (EDQUOT).
	var shared_root := OS.get_environment("EXPORT_PROD_ROOT")
	var seat_root := OS.get_environment("R101_E11_ROOT")
	if shared_root != "":
		_root = shared_root + "/s11"
	elif seat_root != "":
		_root = seat_root
	else:
		_root = ProjectSettings.globalize_path("user://r101e11")
	DirAccess.make_dir_recursive_absolute(_root)
	match arm:
		"pack": _arm_pack()
		"launch": _arm_launch()
		"ladder": _arm_ladder()
		"alt_main": _arm_alt_main()
		"early_quit": _arm_early_quit()
		"corrupt": _arm_corrupt()
		"hang0": _arm_hang0()
		"all": _arm_all()
		_: _bad.append("unknown_arm")
	if _bad.size() > 0:
		print("FAIL export_prod_s11 %s reasons=%s evidence=%s" % [arm, ",".join(_bad), _flat(_detail)])
	elif _clean and not _keep:
		_rm_rf(_root)
	quit(_fail_exit if _bad.size() > 0 else 0)


# --------------------------------------------------------------- arms

func _arm_pack() -> void:
	var v := _variant("main", "main", 0, true)
	if v.is_empty():
		return
	_expect(not _pack_guard(v["pck"]).is_empty(), "pack_guard")
	if _bad.size() > 0:
		return
	print("PASS export_prod_s11 pack magic=GDPC pck_bytes=%d sha256=%s dircount=%d project_binary_bytes=%d savepack_receipt=true export_rc=0 export_stderr_bytes=0"
		% [v["bytes"], v["sha"], v["dircount"], v["pb_bytes"]])


func _arm_launch() -> void:
	var v := _variant("main", "main", 0, false)
	if v.is_empty():
		return
	var r := _launch("launch", v["pck"], 5, 20)
	var want := _receipts_want("main", 5)
	_expect(r["rc"] == 0, "rc=%s" % str(r["rc"]))
	_expect(r["stderr"].is_empty(), "stderr_nonempty")
	_expect(_receipts(r["stdout"]) == want, "receipt_mismatch")
	if _bad.size() > 0:
		_detail += " got=" + str(_receipts(r["stdout"])) + " stderr=" + r["stderr"]
		return
	print("PASS export_prod_s11 launch rc=0 quit_after=5 frames=5 exit_frames=5 exact_receipt=true ready_lines=1 stderr_bytes=0 export=%s cwd_project_files=%d"
		% [v["freshness"], _count_project_files()])


func _arm_ladder() -> void:
	var v := _variant("main", "main", 0, false)
	if v.is_empty():
		return
	var summary := ""
	for n in [1, 2, 3, 4]:
		var r := _launch("ladder%d" % n, v["pck"], n, 20)
		var frames := _frame_count(r["stdout"])
		_expect(r["rc"] == 0 and frames == n and _receipts(r["stdout"]) == _receipts_want("main", n),
			"n%d:rc=%s,frames=%d" % [n, str(r["rc"]), frames])
		summary += "n%d=%d " % [n, frames]
	if _bad.size() > 0:
		return
	print("PASS export_prod_s11 ladder %sexit_frames_match=true export=%s" % [summary, v["freshness"]])


func _arm_alt_main() -> void:
	var v := _variant("alt", "alt", 0, false)
	if v.is_empty():
		return
	var r := _launch("alt_main", v["pck"], 3, 20)
	_expect(r["rc"] == 0, "rc=%s" % str(r["rc"]))
	_expect(_receipts(r["stdout"]) == _receipts_want("alt", 3), "receipt_mismatch")
	_expect("scene=main" not in r["stdout"], "main_tag_leaked")
	if _bad.size() > 0:
		_detail += " got=" + str(_receipts(r["stdout"]))
		return
	print("PASS export_prod_s11 alt_main rc=0 scene=alt frames=3 exit_frames=3 main_tag_absent=true export=%s" % v["freshness"])


func _arm_early_quit() -> void:
	var v := _variant("early", "early", 2, false)
	if v.is_empty():
		return
	var r := _launch("early_quit", v["pck"], 6, 20)
	var frames := _frame_count(r["stdout"])
	_expect(r["rc"] == 0, "rc=%s" % str(r["rc"]))
	_expect(_receipts(r["stdout"]) == _receipts_want("early", 2), "receipt_mismatch")
	_expect(frames == 2, "frames=%d" % frames)
	if _bad.size() > 0:
		_detail += " got=" + str(_receipts(r["stdout"]))
		return
	print("PASS export_prod_s11 early_quit rc=0 quit_after=6 frames=2 exit_frames=2 cap_lt_quit_after=true export=%s" % v["freshness"])


func _arm_corrupt() -> void:
	var v := _variant("main", "main", 0, false)
	if v.is_empty():
		return
	var dir := _root + "/corrupt"
	DirAccess.make_dir_recursive_absolute(dir)
	var bad := dir + "/bad_magic.pck"
	if FileAccess.file_exists(bad):
		DirAccess.remove_absolute(bad)
	if DirAccess.copy_absolute(v["pck"], bad) != OK:
		_bad.append("copy_failed")
		return
	var f := FileAccess.open(bad, FileAccess.READ_WRITE)
	f.seek(0)
	f.store_buffer("XDPC".to_utf8_buffer())
	f.close()
	var missing := dir + "/missing.pck"
	if FileAccess.file_exists(missing):
		DirAccess.remove_absolute(missing)
	var rb := _launch("corrupt_bad", bad, 5, 20)
	var rm := _launch("corrupt_missing", missing, 5, 20)
	_expect(rb["rc"] == 0, "bad_rc=%s" % str(rb["rc"]))
	_expect(rm["rc"] == 0, "missing_rc=%s" % str(rm["rc"]))
	_expect("Cannot open resource pack" in rb["stderr"], "bad_error_absent")
	_expect("Cannot open resource pack" in rm["stderr"], "missing_error_absent")
	_expect(_receipts(rb["stdout"]).is_empty(), "bad_receipts_present")
	_expect(_receipts(rm["stdout"]).is_empty(), "missing_receipts_present")
	if _bad.size() > 0:
		_detail += " bad_stderr=" + rb["stderr"] + " missing_stderr=" + rm["stderr"]
		return
	print("PASS export_prod_s11 corrupt bad_rc=0 missing_rc=0 bad_error=true missing_error=true bad_receipts=0 missing_receipts=0 exit0_trap=true export=%s"
		% v["freshness"])


func _arm_hang0() -> void:
	var v := _variant("main", "main", 0, false)
	if v.is_empty():
		return
	var r := _launch("hang0", v["pck"], 0, 3)
	var frames := _frame_count(r["stdout"])
	_expect(r["rc"] == 124, "rc=%s" % str(r["rc"]))
	_expect(frames > 0, "frames=%d" % frames)
	_expect(not r["stdout"].contains(S11 + "exit"), "exit_receipt_present")
	if _bad.size() > 0:
		return
	print("PASS export_prod_s11 hang0 rc=124 timeout_bound_s=3 frames_gt0=true exit_receipts=0 quit_after_zero_disables=true export=%s" % v["freshness"])


func _arm_all() -> void:
	_arm_pack()
	_arm_launch()
	_arm_ladder()
	_arm_alt_main()
	_arm_early_quit()
	_arm_corrupt()


# --------------------------------------------------------------- project + export

func _main_gd(tag: String, self_quit: int) -> String:
	var src := "extends Node\n\nvar frames := 0\n\n\nfunc _ready() -> void:\n"
	src += "\tprint(\"" + S11 + "ready scene=" + tag + "\")\n"
	src += "\n\nfunc _process(_delta: float) -> void:\n\tframes += 1\n\tprint(\"" + S11 + "frame=%d\" % frames)\n"
	if self_quit > 0:
		src += "\tif frames >= " + str(self_quit) + ":\n\t\tget_tree().quit()\n"
	src += "\n\nfunc _exit_tree() -> void:\n\tprint(\"" + S11 + "exit frames=%d\" % frames)\n"
	return src


# Build (or reuse) one variant project + its exported PCK. Freshness is bound to
# the exact generated source bytes, so a stale pack can never be re-read as
# current evidence. `fresh` forces a re-export (the `pack` arm's measurement).
func _variant(tag: String, scene_tag: String, self_quit: int, fresh: bool) -> Dictionary:
	var base := _root + "/" + tag
	var proj := base + "/proj"
	var out := base + "/out"
	var pck := out + "/" + tag + ".pck"
	var stamp := out + "/src.sha256"
	var main_gd := _main_gd(scene_tag, self_quit)
	var vi := Engine.get_version_info()
	var engine_tag := str(vi.get("string", "")) + "/" + str(vi.get("hash", ""))
	var src_digest := _sha_str(engine_tag + PROJECT_SRC + PRESET_SRC + SCENE_SRC + main_gd)
	if not fresh and FileAccess.file_exists(pck) and FileAccess.file_exists(stamp) \
			and FileAccess.get_file_as_string(stamp).strip_edges() == src_digest:
		var g := _pack_guard(pck, false)
		if not g.is_empty():
			return _vresult(pck, "reused")
	DirAccess.make_dir_recursive_absolute(proj)
	if not _write(proj + "/project.godot", PROJECT_SRC):
		_bad.append("project_write")
		return {}
	if not _write(proj + "/export_presets.cfg", PRESET_SRC) or not _write(proj + "/main.tscn", SCENE_SRC) \
			or not _write(proj + "/main.gd", main_gd):
		_bad.append("source_write")
		return {}
	DirAccess.make_dir_recursive_absolute(out)
	var runs := _root + "/runs"
	DirAccess.make_dir_recursive_absolute(runs)
	var o := runs + "/export_" + tag + ".out"
	var e := runs + "/export_" + tag + ".err"
	var r := runs + "/export_" + tag + ".rc"
	var cmd := "timeout 60 \"" + OS.get_executable_path() + "\" --headless --path \"" + proj \
		+ "\" --export-pack \"" + PRESET + "\" \"" + pck + "\" >\"" + o + "\" 2>\"" + e + "\"; echo \\$? >\"" + r + "\""
	_sh(cmd)
	var rc := _rc_of(r)
	var eo := FileAccess.get_file_as_string(o)
	var ee := FileAccess.get_file_as_string(e)
	if rc != 0 or not eo.contains("savepack") or not eo.contains("[ DONE ]") or not ee.is_empty():
		_bad.append("export_rc=%s stderr=%s" % [str(rc), _flat(ee)])
		return {}
	if not _write(stamp, src_digest + "\n"):
		_bad.append("stamp_write")
		return {}
	if not _pack_guard(pck):
		return {}
	return _vresult(pck, "fresh")


func _vresult(pck: String, freshness: String) -> Dictionary:
	var g := _pack_guard(pck, false)
	return {"pck": pck, "freshness": freshness, "bytes": _size_of(pck), "sha": _sha_file(pck),
		"dircount": g["count"] if g else -1, "pb_bytes": g["pb_bytes"] if g else -1}


# Minimal PCK v4 header/directory reader (measured layout, engine 4.7.2):
# magic(4) version(4) major(4) minor(4) patch(4) flags(4) file_base(8)
# dir_offset(8), then at dir_offset: count(4) and per entry
# path_len(4) path path_len bytes offset(8) size(8) md5(16) flags(4).
# Returns {} on any structural violation; `record` controls whether the reason
# is charged to the arm (the cache-reuse probe must stay quiet and re-export).
func _pack_guard(pck: String, record: bool = true) -> Dictionary:
	var b := FileAccess.get_file_as_bytes(pck)
	if b.size() < 40:
		if record:
			_bad.append("pck_absent_or_short")
		return {}
	if b.slice(0, 4).get_string_from_utf8() != "GDPC":
		if record:
			_bad.append("pck_magic")
		return {}
	var dir_off := b.decode_u64(32)
	if dir_off + 4 > b.size():
		if record:
			_bad.append("pck_dir_offset")
		return {}
	var count := b.decode_u32(dir_off)
	var pb_bytes := -1
	var off := dir_off + 4
	for i in count:
		if off + 4 > b.size():
			if record:
				_bad.append("pck_entry_overrun")
			return {}
		var plen := b.decode_u32(off)
		off += 4
		if plen > 4096 or off + plen + 36 > b.size():
			if record:
				_bad.append("pck_entry_path_len")
			return {}
		var name := b.slice(off, off + plen).get_string_from_utf8().strip_escapes()
		off += plen
		var fsize := b.decode_u64(off + 8)
		off += 36
		if name == "project.binary":
			pb_bytes = fsize
	if count < 1 or pb_bytes <= 0:
		# an empty project.binary entry makes the pack loadable but settings-less
		if record:
			_bad.append("pck_project_binary_bytes=%d" % pb_bytes)
		return {}
	return {"count": count, "pb_bytes": pb_bytes}


# --------------------------------------------------------------- child runs

func _launch(tag: String, pck: String, quit_after: int, bound_s: int) -> Dictionary:
	var runs := _root + "/runs"
	DirAccess.make_dir_recursive_absolute(runs)
	var clean := _root + "/clean"
	DirAccess.make_dir_recursive_absolute(clean)
	var o := runs + "/" + tag + ".out"
	var e := runs + "/" + tag + ".err"
	var r := runs + "/" + tag + ".rc"
	for f in [o, e, r]:
		if FileAccess.file_exists(f):
			DirAccess.remove_absolute(f)
	var cmd := "cd \"" + clean + "\" || exit 9; timeout " + str(bound_s) + " \"" + OS.get_executable_path()
	cmd += "\" --headless --main-pack \"" + pck + "\" --quit-after " + str(quit_after)
	cmd += " >\"" + o + "\" 2>\"" + e + "\"; echo \\$? >\"" + r + "\""
	_sh(cmd)
	return {"rc": _rc_of(r), "stdout": FileAccess.get_file_as_string(o), "stderr": FileAccess.get_file_as_string(e),
		"out_path": o, "err_path": e}


func _rc_of(path: String) -> int:
	var s := FileAccess.get_file_as_string(path).strip_edges()
	return int(s) if s != "" else -1


func _sh(cmd: String) -> int:
	return OS.execute("/bin/sh", ["-c", cmd], [], false, false)


# --------------------------------------------------------------- small helpers

func _receipts(out: String) -> PackedStringArray:
	var r := PackedStringArray()
	for line in out.split("\n"):
		var s := line.strip_edges()
		if s.begins_with(S11):
			r.append(s)
	return r


func _receipts_want(tag: String, frames: int) -> PackedStringArray:
	var w := PackedStringArray([S11 + "ready scene=" + tag])
	for i in range(1, frames + 1):
		w.append(S11 + "frame=" + str(i))
	w.append(S11 + "exit frames=" + str(frames))
	return w


func _frame_count(out: String) -> int:
	var n := 0
	for line in out.split("\n"):
		if line.strip_edges().begins_with(S11 + "frame="):
			n += 1
	return n


func _count_project_files() -> int:
	var clean := _root + "/clean"
	var n := 0
	for f in ["project.godot", "main.tscn", "main.gd", "export_presets.cfg"]:
		if FileAccess.file_exists(clean + "/" + f):
			n += 1
	return n


func _write(path: String, text: String) -> bool:
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		return false
	f.store_string(text)
	f.close()
	return true


func _size_of(path: String) -> int:
	return FileAccess.get_file_as_bytes(path).size()


func _sha_str(text: String) -> String:
	return _hash(text.to_utf8_buffer())


func _sha_file(path: String) -> String:
	return _hash(FileAccess.get_file_as_bytes(path))


func _hash(b: PackedByteArray) -> String:
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(b)
	return ctx.finish().hex_encode()


func _flat(s: String) -> String:
	var one := s.replace("\n", " | ").replace("\r", " ").strip_edges()
	return one.substr(0, 300)


func _expect(cond: bool, token: String) -> void:
	if not cond:
		_bad.append(token)


func _rm_rf(path: String) -> void:
	OS.execute("rm", ["-rf", path], [], false, false)
