extends SceneTree
# export_prod — r101 C1 capability lattice: headless export receipts for a
# production-shaped 2D project (scripts + scene + imported PNG + SVG icon +
# resource + deep subdirectory + include/exclude filters), using the nested
# Godot 4.7.2 release pipeline itself.
#
# Battery launch shape (one arm per process, 8s fixture bound):
#   godot --headless --path <fixture proj> --script res://export_prod.gd -- --arm=<arm>
#
# Arms and the CASES rows that pin their PASS lines:
#   base        -> export_prod_base_pck                 (GDPC magic, entry census,
#                  names digest, bytes, project.binary size)
#   base        -> export_prod_subdir_census            (deep-subdirectory entries)
#   base        -> export_prod_include_exclude_filter   (secret/drop.txt excluded)
#   zip         -> export_prod_zip_census               (PK0304 + central directory)
#   det_a       -> export_prod_det_a                    (export sample 1)
#   det_b       -> export_prod_det_b                    (sample 2 + byte equality;
#                  requires det_a's a.pck in the same out dir — adjacent rows)
#   swap        -> export_prod_main_scene_swap          (pack boots the pre-swap
#                  scene after the source main_scene is swapped)
#   swap        -> export_prod_mainpack_quit_after_frames (--main-pack +
#                  --quit-after N frame receipt)
#   remap       -> export_prod_resource_remap_census    (.remap + .ctex census)
#   remap       -> export_prod_icon_uid_census          (icon vs .uid stripping)
#   refusal     -> export_prod_unknown_preset_refusal   (nested exit 1, no artifact)
#   notemplates -> export_prod_templates_missing_class  (XDG_DATA_HOME override)
#
# Scratch policy: every arm builds its project under <root>/<variant>/proj and
# exports into <root>/<variant>/out, where <root> is the first candidate of
# EXPORT_PROD_ROOT, $TMPDIR/export_prod, <engine user-data dir>/export_prod and
# /tmp/export_prod that passes a 4096-byte write+readback probe. The user-data
# dir is preferred over /tmp because /tmp measurably rejects even multi-KB
# writes with EDQUOT on this host. Host paths appear only in EXPORT_PROD_DIAG
# lines, never in the pinned PASS lines.
#
# TMP isolation (measured 2026-10-18, r101 E0): the 4.7.2 packer serializes
# project.binary through a FIXED temp path /tmp/tmpproject.binary-<rand>
# (strace-verified; $TMPDIR is not honored), and under a full per-user /tmp
# quota that write(2) returns EDQUOT — the packer ignores the error and stores
# a 0-byte project.binary, so the exported pack/binary fails to load its own
# settings ("Corrupted header in binary project.binary (not ECFG)") while the
# export still exits 0. Exports therefore run inside
# `unshare -m --map-root-user sh -c 'mount -t tmpfs … /tmp; …'` (private /tmp)
# when user namespaces are available; the pbin_size receipt field pins the
# result. Without unshare the arms still run but pbin_size=0 exposes the
# environment instead of hiding it.
#
# Evidence rule: nested Godot output is never echoed — the whole nested shell
# (including the refusal / templates-missing diagnostics, which are genuine
# ERROR: lines) is redirected to <root>/<variant>/logs/*.log, and the PASS
# lines carry only derived booleans, counts, sizes and digests. Each arm
# prints one PASS line per registrable row; operational failures (export
# crash, missing artifact, unparsable pack) print FAIL and exit 1.
#
# Measured 2026-10-18 on godot 4.7.2.stable.arch_linux.ed1daf0bf (host load
# 30+): one --export-pack of this project ~3s, --main-pack launch ~0.8s,
# templates-missing refusal ~3.6s — every arm below stays under the 8s bound.

const PRESET := "Linux/X11"
const BAD_PRESET := "No Such Preset"
const PRESET_ERR := "Invalid export preset name: No Such Preset."
const TEMPLATE_ERR := "No export template found at the expected path:"
const RELEASE_TEMPLATE := "linux_release.x86_64"
const PNG_B64 := "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

# Exact pack census expected from the prod project (16 entries, measured).
const EXPECTED := [
	".godot/exported/133200997/export-3070c538c03ee49b7677ff960a3f5195-main.scn",
	".godot/exported/133200997/export-5652feaed6582d9176c7808696942b7b-mat.res",
	".godot/global_script_class_cache.cfg",
	".godot/imported/icon.svg-218a8f2b3041327d8a5756f3a245f83b.ctex",
	".godot/imported/tex.png-32a37300d93dbbbe42f0075627006368.ctex",
	".godot/uid_cache.bin",
	"data/deep/nested.txt",
	"icon.svg",
	"icon.svg.import",
	"main.gdc",
	"main.gd.remap",
	"main.tscn.remap",
	"project.binary",
	"res/mat.tres.remap",
	"res/tex.png.import",
	"secret/keep.txt",
]

const MAIN_GD := "extends Node\n\nvar frames := 0\n\nfunc _ready() -> void:\n\tprint(\"EXPORT_PROD_MAIN boot scene=main_a\")\n\nfunc _process(_delta: float) -> void:\n\tframes += 1\n\tprint(\"EXPORT_PROD_FRAME %d\" % frames)\n"
const MAIN_B_GD := "extends Node\n\nvar frames := 0\n\nfunc _ready() -> void:\n\tprint(\"EXPORT_PROD_MAIN boot scene=main_b\")\n\nfunc _process(_delta: float) -> void:\n\tframes += 1\n\tprint(\"EXPORT_PROD_FRAME %d\" % frames)\n"
const MAIN_TSCN := "[gd_scene load_steps=2 format=3]\n\n[ext_resource type=\"Script\" path=\"res://main.gd\" id=\"1\"]\n\n[node name=\"Main\" type=\"Node\"]\nscript = ExtResource(\"1\")\n"
const MAIN_B_TSCN := "[gd_scene load_steps=2 format=3]\n\n[ext_resource type=\"Script\" path=\"res://main_b.gd\" id=\"1\"]\n\n[node name=\"MainB\" type=\"Node\"]\nscript = ExtResource(\"1\")\n"
const MAT_TRES := "[gd_resource type=\"Resource\" format=3]\n\n[resource]\nmetadata/note=\"prod\"\n"
const ICON_SVG := "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"16\" height=\"16\"><rect width=\"16\" height=\"16\" fill=\"#3355ff\"/></svg>"

var arm := ""
var opt := {}
var _items: PackedStringArray = []
var _root := ""
var _unshare := false


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
		elif a.begins_with("--"):
			var kv := a.substr(2).split("=", true, 1)
			opt[kv[0]] = kv[1] if kv.size() > 1 else "1"
	call_deferred("_run")


func _run() -> void:
	_root = _pick_root()
	_diag("root", _root)
	if _root == "":
		_fail("no_writable_scratch_root")
		return
	_unshare = _probe_unshare()
	_diag("userns_tmp_isolation", _unshare)
	match arm:
		"base":
			_arm_base()
		"zip":
			_arm_zip()
		"det_a":
			_arm_det_a()
		"det_b":
			_arm_det_b()
		"swap":
			_arm_swap()
		"remap":
			_arm_remap()
		"refusal":
			_arm_refusal()
		"notemplates":
			_arm_notemplates()
		_:
			_fail("unknown_arm")


# ------------------------------------------------------------------ receipts

func _fail(reason: String) -> void:
	print("FAIL export_prod %s reason=%s" % [arm, reason])
	quit(1)


func _ok() -> void:
	print("PASS export_prod %s %s" % [arm, " ".join(_items)])
	quit(0)


func _it(key: String, value) -> void:
	_items.append("%s=%s" % [key, str(value)])


func _diag(key: String, value) -> void:
	print("EXPORT_PROD_DIAG %s %s=%s" % [arm, key, str(value)])


func _emit(kind: String, fields: PackedStringArray) -> void:
	print("PASS export_prod %s %s" % [kind, " ".join(fields)])


# ------------------------------------------------------------------- scratch

func _pick_root() -> String:
	var candidates: PackedStringArray = []
	if OS.get_environment("EXPORT_PROD_ROOT") != "":
		candidates.append(OS.get_environment("EXPORT_PROD_ROOT"))
	if OS.get_environment("TMPDIR") != "":
		candidates.append(OS.get_environment("TMPDIR").path_join("export_prod"))
	# The engine user-data dir is preferred over /tmp: on this host /tmp
	# intermittently rejects even 4 KB writes with EDQUOT (quota), which would
	# kill the pack output, while the user-data dir shares the repo filesystem.
	candidates.append(OS.get_user_data_dir().path_join("export_prod"))
	candidates.append("/tmp/export_prod")
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


func _probe_unshare() -> bool:
	var cmd := "exec > /dev/null 2>&1\nunshare -m --map-root-user /usr/bin/sh -c 'mount -t tmpfs -o size=16M tmpfs /tmp && test -w /tmp'"
	return OS.execute("/usr/bin/sh", PackedStringArray(["-c", cmd])) == 0


func _godot() -> String:
	var exe := OS.get_executable_path()
	return exe if exe != "" else "/usr/bin/godot"


func _q(s: String) -> String:
	return "'" + s.replace("'", "'\\''") + "'"


func _variant_dir(variant: String) -> String:
	return _root.path_join(variant)


func _proj_dir(variant: String) -> String:
	return _variant_dir(variant).path_join("proj")


func _out_dir(variant: String) -> String:
	return _variant_dir(variant).path_join("out")


func _log_path(variant: String, name: String) -> String:
	return _variant_dir(variant).path_join("logs").path_join(name + ".log")


func _mkdir(path: String) -> bool:
	if DirAccess.dir_exists_absolute(path):
		return true
	var err := DirAccess.make_dir_recursive_absolute(path)
	if err != OK:
		_fail("mkdir_failed:%s:%d" % [path, err])
		return false
	return true


func _write_text(path: String, text: String) -> bool:
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		_fail("write_failed:" + path)
		return false
	f.store_string(text)
	f.close()
	return true


func _write_bytes(path: String, bytes: PackedByteArray) -> bool:
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		_fail("write_failed:" + path)
		return false
	f.store_buffer(bytes)
	f.close()
	return true


func _file_size(path: String) -> int:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return -1
	var size := f.get_length()
	f.close()
	return size


func _sha256_text(text: String) -> String:
	var ctx := HashingContext.new()
	if ctx.start(HashingContext.HASH_SHA256) != OK:
		return ""
	if ctx.update(text.to_utf8_buffer()) != OK:
		return ""
	return ctx.finish().hex_encode()


func _sha256_file(path: String) -> String:
	var ctx := HashingContext.new()
	if ctx.start(HashingContext.HASH_SHA256) != OK:
		return ""
	if ctx.update(FileAccess.get_file_as_bytes(path)) != OK:
		return ""
	return ctx.finish().hex_encode()


# ------------------------------------------------------------------ projects

func _run_logged(body: String, log_path: String, isolate := false) -> int:
	_mkdir(log_path.get_base_dir())
	var script := body
	if isolate and _unshare:
		# Private /tmp for the packer's fixed tmpproject.binary temp path.
		script = "mount -t tmpfs -o size=64M tmpfs /tmp || exit 97\n" + body
		script = "unshare -m --map-root-user /usr/bin/sh -c " + _q(script)
	_diag("nested", body.replace("\n", " ; "))
	return OS.execute("/usr/bin/sh", PackedStringArray(["-c", "exec > " + _q(log_path) + " 2>&1\n" + script]))


func _export(variant: String, mode: String, out_path: String, env_prefix: String) -> int:
	var proj := _proj_dir(variant)
	var log_path := _log_path(variant, "%s_%s" % [mode, arm])
	var body := "cd " + _q(proj) + "\n" + env_prefix + _q(_godot()) + " --headless --path " + _q(proj) + " --export-" + mode + " " + _q(PRESET) + " " + _q(out_path)
	return _run_logged(body, log_path, true)


func _build_prod() -> String:
	var proj := _proj_dir("prod")
	_mkdir(proj.path_join("res"))
	_mkdir(proj.path_join("data/deep"))
	_mkdir(proj.path_join("secret"))
	_mkdir(_out_dir("prod"))
	_write_text(proj.path_join("project.godot"), "config_version=5\n\n[application]\nconfig/name=\"ExportProd\"\nrun/main_scene=\"res://main.tscn\"\nconfig/features=PackedStringArray(\"4.7\")\nconfig/icon=\"res://icon.svg\"\n\n[display]\nwindow/size/viewport_width=320\nwindow/size/viewport_height=180\n")
	_write_text(proj.path_join("export_presets.cfg"), "[preset.0]\nname=\"Linux/X11\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\ninclude_filter=\"data/*,secret/keep*\"\nexclude_filter=\"secret/drop*\"\nexport_path=\"\"\n\n[preset.0.options]\nbinary_format/architecture=\"x86_64\"\n")
	_write_text(proj.path_join("main.gd"), MAIN_GD)
	_write_text(proj.path_join("main.tscn"), MAIN_TSCN)
	_write_text(proj.path_join("icon.svg"), ICON_SVG)
	_write_text(proj.path_join("res/mat.tres"), MAT_TRES)
	_write_bytes(proj.path_join("res/tex.png"), Marshalls.base64_to_raw(PNG_B64))
	_write_text(proj.path_join("data/deep/nested.txt"), "nested-payload\n")
	_write_text(proj.path_join("secret/keep.txt"), "keep-me\n")
	_write_text(proj.path_join("secret/drop.txt"), "drop-me\n")
	return proj


func _build_swap() -> String:
	var proj := _proj_dir("swap")
	_mkdir(proj)
	_mkdir(_out_dir("swap"))
	_write_text(proj.path_join("export_presets.cfg"), "[preset.0]\nname=\"Linux/X11\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\ninclude_filter=\"\"\nexclude_filter=\"\"\nexport_path=\"\"\n\n[preset.0.options]\nbinary_format/architecture=\"x86_64\"\n")
	_write_text(proj.path_join("project.godot"), "config_version=5\n\n[application]\nconfig/name=\"ExportSwap\"\nrun/main_scene=\"res://main.tscn\"\nconfig/features=PackedStringArray(\"4.7\")\n")
	_write_text(proj.path_join("main.gd"), MAIN_GD)
	_write_text(proj.path_join("main.tscn"), MAIN_TSCN)
	_write_text(proj.path_join("main_b.gd"), MAIN_B_GD)
	_write_text(proj.path_join("main_b.tscn"), MAIN_B_TSCN)
	return proj


# ------------------------------------------------------------------- censuses

func _census_pck(path: String) -> Dictionary:
	var bytes := FileAccess.get_file_as_bytes(path)
	if bytes.size() < 0x28 or bytes.decode_u32(0) != 0x43504447:
		return {}
	var base := bytes.decode_u64(0x18)
	var dir_off := bytes.decode_u64(0x20)
	if dir_off + 4 > bytes.size():
		return {}
	var count := bytes.decode_u32(dir_off)
	var off := dir_off + 4
	var entries := {}
	for i in count:
		if off + 4 > bytes.size():
			return {}
		var plen := bytes.decode_u32(off)
		off += 4
		if off + plen + 36 > bytes.size():
			return {}
		var name_end := off
		while name_end < off + plen and bytes[name_end] != 0:
			name_end += 1
		var name := bytes.slice(off, name_end).get_string_from_utf8()
		off += plen
		off = ((off + 3) / 4) * 4
		var foff := bytes.decode_u64(off)
		var size := bytes.decode_u64(off + 8)
		var flags := bytes.decode_u32(off + 32)
		off += 36
		if base + foff + size > bytes.size():
			return {}
		entries[name] = {"size": size, "offset": foff, "flags": flags}
	return {"magic": "GDPC", "count": count, "file_base": base, "dir_offset": dir_off, "entries": entries}


func _census_zip(path: String) -> Dictionary:
	var bytes := FileAccess.get_file_as_bytes(path)
	if bytes.size() < 22 or bytes.decode_u32(0) != 0x04034b50:
		return {}
	var eocd := -1
	var i := bytes.size() - 22
	while i >= 0:
		if bytes.decode_u32(i) == 0x06054b50:
			eocd = i
			break
		i -= 1
	if eocd < 0:
		return {}
	var count := bytes.decode_u16(eocd + 10)
	var cd_off := bytes.decode_u32(eocd + 16)
	var off := cd_off
	var entries := {}
	for k in count:
		if off + 46 > bytes.size() or bytes.decode_u32(off) != 0x02014b50:
			return {}
		var nlen := bytes.decode_u16(off + 28)
		var xlen := bytes.decode_u16(off + 30)
		var clen := bytes.decode_u16(off + 32)
		if off + 46 + nlen > bytes.size():
			return {}
		var name := bytes.slice(off + 46, off + 46 + nlen).get_string_from_utf8()
		entries[name] = {"size": bytes.decode_u32(off + 24), "method": bytes.decode_u16(off + 10)}
		off += 46 + nlen + xlen + clen
	var local := 0
	for j in bytes.size() - 3:
		if bytes.decode_u32(j) == 0x04034b50:
			local += 1
	return {"magic": "PK0304", "count": count, "central_offset": cd_off, "entries": entries, "local_headers": local}


func _names_digest(entries: Dictionary) -> String:
	var names := PackedStringArray(entries.keys())
	names.sort()
	return _sha256_text("\n".join(names))


func _census_matches(entries: Dictionary) -> bool:
	if entries.size() != EXPECTED.size():
		return false
	for name in EXPECTED:
		if not entries.has(name):
			return false
	return true


# ---------------------------------------------------------------------- arms

func _arm_base() -> void:
	var proj := _build_prod()
	var out_dir := _out_dir("prod")
	var pck := out_dir.path_join("prod.pck")
	var code := _export("prod", "pack", pck, "")
	if code != 0:
		_fail("pack_export_exit:%d" % code)
		return
	if not FileAccess.file_exists(pck):
		_fail("pack_missing")
		return
	var census := _census_pck(pck)
	if census.is_empty() or census["magic"] != "GDPC":
		_fail("pck_parse_failed")
		return
	var entries: Dictionary = census["entries"]
	var dirs := _dirs_of(entries)
	var subdir := PackedStringArray()
	subdir.append("dirs=%s" % _fmt_strings(dirs))
	subdir.append("nested_path=data/deep/nested.txt")
	subdir.append("nested_size=%d" % _entry_size(entries, "data/deep/nested.txt"))
	subdir.append("file_count=%d" % entries.size())
	var filt := PackedStringArray()
	filt.append("include=data/*,secret/keep*")
	filt.append("exclude=secret/drop*")
	filt.append("nested_in=%s" % entries.has("data/deep/nested.txt"))
	filt.append("keep_in=%s" % entries.has("secret/keep.txt"))
	filt.append("drop_in=%s" % entries.has("secret/drop.txt"))
	filt.append("drop_on_disk=%s" % FileAccess.file_exists(proj.path_join("secret/drop.txt")))
	_emit("subdir", subdir)
	_emit("filter", filt)
	_it("magic", census["magic"])
	_it("entry_count", census["count"])
	_it("names_sha256", _names_digest(entries))
	_it("nested_size", _entry_size(entries, "data/deep/nested.txt"))
	_it("keep_size", _entry_size(entries, "secret/keep.txt"))
	_it("drop_in_pack", entries.has("secret/drop.txt"))
	_it("uid_entries", _count_matching(entries, ".uid"))
	_it("remap_entries", _count_matching(entries, ".remap"))
	_it("ctex_entries", _count_matching(entries, ".ctex"))
	_it("import_entries", _count_matching(entries, ".import"))
	_it("project_binary", entries.has("project.binary"))
	_it("pbin_size", _entry_size(entries, "project.binary"))
	_it("census_match", _census_matches(entries))
	_it("bytes", _file_size(pck))
	_diag("project", proj)
	_ok()


func _arm_zip() -> void:
	_build_prod()
	var out_dir := _out_dir("prod")
	var zip_path := out_dir.path_join("prod.zip")
	var code := _export("prod", "pack", zip_path, "")
	if code != 0:
		_fail("zip_export_exit:%d" % code)
		return
	if not FileAccess.file_exists(zip_path):
		_fail("zip_missing")
		return
	var census := _census_zip(zip_path)
	if census.is_empty():
		_fail("zip_parse_failed")
		return
	var entries: Dictionary = census["entries"]
	_it("magic", census["magic"])
	_it("eocd", true)
	_it("entry_count", census["count"])
	_it("local_headers", census["local_headers"])
	_it("names_sha256", _names_digest(entries))
	_it("nested_size", _entry_size(entries, "data/deep/nested.txt"))
	_it("drop_in_zip", entries.has("secret/drop.txt"))
	_it("deflate_entries", _count_method(entries, 8))
	_it("pbin_size", _entry_size(entries, "project.binary"))
	_it("census_match", _census_matches(entries))
	_it("bytes", _file_size(zip_path))
	_ok()


func _arm_det_a() -> void:
	_build_prod()
	var out_dir := _out_dir("prod")
	var a := out_dir.path_join("a.pck")
	var code := _export("prod", "pack", a, "")
	if code != 0 or not FileAccess.file_exists(a):
		_fail("sample1_export_failed")
		return
	_it("sample", 1)
	_it("bytes", _file_size(a))
	_it("sha256", _sha256_file(a))
	_ok()


func _arm_det_b() -> void:
	_build_prod()
	var out_dir := _out_dir("prod")
	var a := out_dir.path_join("a.pck")
	var b := out_dir.path_join("b.pck")
	if not FileAccess.file_exists(a):
		_fail("det_a_artifact_missing")
		return
	var code := _export("prod", "pack", b, "")
	if code != 0 or not FileAccess.file_exists(b):
		_fail("sample2_export_failed")
		return
	var sha_a := _sha256_file(a)
	var sha_b := _sha256_file(b)
	_it("sample", 2)
	_it("bytes", _file_size(b))
	_it("equal_to_sample1", sha_a == sha_b and _file_size(a) == _file_size(b))
	_it("byte_diff_count", _byte_diff_count(a, b))
	_it("samples", 2)
	_it("sha256", sha_b)
	_it("sample1_sha256", sha_a)
	_ok()


func _arm_swap() -> void:
	var proj := _build_swap()
	var pck := _out_dir("swap").path_join("swap.pck")
	var code := _export("swap", "pack", pck, "")
	if code != 0 or not FileAccess.file_exists(pck):
		_fail("swap_export_failed")
		return
	var census := _census_pck(pck)
	if census.is_empty():
		_fail("pck_parse_failed")
		return
	# Swap the SOURCE project's main scene only after the pack was written.
	_write_text(proj.path_join("project.godot"), "config_version=5\n\n[application]\nconfig/name=\"ExportSwap\"\nrun/main_scene=\"res://main_b.tscn\"\nconfig/features=PackedStringArray(\"4.7\")\n")
	var pack_log := _log_path("swap", "pack_run")
	var pack_code := _run_logged("cd /\n" + _q(_godot()) + " --headless --main-pack " + _q(pck) + " --quit-after 5", pack_log)
	var src_log := _log_path("swap", "source_run")
	var src_code := _run_logged("cd " + _q(proj) + "\n" + _q(_godot()) + " --headless --path " + _q(proj) + " --quit-after 2", src_log)
	var pack_text := FileAccess.get_file_as_string(pack_log)
	var src_text := FileAccess.get_file_as_string(src_log)
	var entries: Dictionary = census["entries"]
	var swap_fields := PackedStringArray()
	swap_fields.append("pack_boot=%s" % ("main_a" if pack_text.contains("boot scene=main_a") else "main_b" if pack_text.contains("boot scene=main_b") else "none"))
	swap_fields.append("source_boot=%s" % ("main_b" if src_text.contains("boot scene=main_b") else "main_a" if src_text.contains("boot scene=main_a") else "none"))
	swap_fields.append("pbin_size=%d" % _entry_size(entries, "project.binary"))
	swap_fields.append("pack_exit=%d" % pack_code)
	swap_fields.append("source_exit=%d" % src_code)
	_emit("swap", swap_fields)
	var frames := _frame_numbers(pack_text)
	var frame_fields := PackedStringArray()
	frame_fields.append("quit_after=5")
	frame_fields.append("frames=%s" % _fmt_ints(frames))
	frame_fields.append("extra=%s" % (_fmt_ints(frames) != "[1,2,3,4,5]"))
	frame_fields.append("exit=%d" % pack_code)
	_emit("quitframes", frame_fields)
	quit(0)


func _arm_remap() -> void:
	var proj := _build_prod()
	var out_dir := _out_dir("prod")
	var pck := out_dir.path_join("prod.pck")
	var code := _export("prod", "pack", pck, "")
	if code != 0 or not FileAccess.file_exists(pck):
		_fail("remap_export_failed")
		return
	var census := _census_pck(pck)
	if census.is_empty():
		_fail("pck_parse_failed")
		return
	var entries: Dictionary = census["entries"]
	var uid_on_disk := FileAccess.file_exists(proj.path_join("main.gd.uid"))
	var fields := PackedStringArray()
	fields.append("remap_gd=%s" % entries.has("main.gd.remap"))
	fields.append("remap_scn=%s" % entries.has("main.tscn.remap"))
	fields.append("remap_tres=%s" % entries.has("res/mat.tres.remap"))
	fields.append("raw_gd=%s" % entries.has("main.gd"))
	fields.append("raw_png=%s" % entries.has("res/tex.png"))
	fields.append("ctex_tex=%s" % _has_prefix(entries, ".godot/imported/tex.png-"))
	fields.append("ctex_icon=%s" % _has_prefix(entries, ".godot/imported/icon.svg-"))
	fields.append("import_tex=%s" % entries.has("res/tex.png.import"))
	fields.append("import_icon=%s" % entries.has("icon.svg.import"))
	_diag("disk_uid", uid_on_disk)
	_emit("remap", fields)
	var icon := PackedStringArray()
	icon.append("icon_svg=%s" % entries.has("icon.svg"))
	icon.append("icon_import=%s" % entries.has("icon.svg.import"))
	icon.append("icon_uid_in_pack=%s" % entries.has("icon.svg.uid"))
	icon.append("uid_on_disk=%s" % uid_on_disk)
	icon.append("uid_in_pack=%s" % (_count_matching(entries, ".uid") > 0))
	_emit("iconuid", icon)
	quit(0)


func _arm_refusal() -> void:
	var proj := _build_prod()
	var out_dir := _out_dir("prod")
	var none := out_dir.path_join("none.pck")
	var log_path := _log_path("prod", "refusal")
	var body := "cd " + _q(proj) + "\n" + _q(_godot()) + " --headless --path " + _q(proj) + " --export-pack " + _q(BAD_PRESET) + " " + _q(none)
	var code := _run_logged(body, log_path, true)
	var log_text := FileAccess.get_file_as_string(log_path)
	var fields := PackedStringArray()
	fields.append("nested_exit=%d" % code)
	fields.append("class=%s" % ("invalid_export_preset_name" if log_text.contains(PRESET_ERR) else "other"))
	fields.append("preset_listing=%s" % log_text.contains("\"" + PRESET + "\""))
	fields.append("artifacts=%d" % (1 if FileAccess.file_exists(none) else 0))
	fields.append("log_bytes=%d" % log_text.length())
	_emit("refusal", fields)
	quit(0)


func _arm_notemplates() -> void:
	var proj := _build_prod()
	var empty_data := _variant_dir("prod").path_join("empty-xdg-data")
	_mkdir(empty_data)
	var out_dir := _out_dir("prod")
	var exe_path := out_dir.path_join("nope.x86_64")
	var log_path := _log_path("prod", "notemplates")
	var body := "cd " + _q(proj) + "\nXDG_DATA_HOME=" + _q(empty_data) + " " + _q(_godot()) + " --headless --path " + _q(proj) + " --export-release " + _q(PRESET) + " " + _q(exe_path)
	var code := _run_logged(body, log_path, true)
	var log_text := FileAccess.get_file_as_string(log_path)
	var fields := PackedStringArray()
	fields.append("nested_exit=%d" % code)
	fields.append("class=%s" % ("no_export_template" if log_text.contains(TEMPLATE_ERR) else "other"))
	fields.append("release_template_named=%s" % log_text.contains(RELEASE_TEMPLATE))
	fields.append("artifacts=%d" % (1 if FileAccess.file_exists(exe_path) else 0))
	fields.append("log_bytes=%d" % log_text.length())
	_emit("notemplates", fields)
	quit(0)


# ------------------------------------------------------------------ analysis

func _entry_size(entries: Dictionary, name: String) -> int:
	if not entries.has(name):
		return -1
	return int(entries[name].get("size", -1))


func _count_matching(entries: Dictionary, needle: String) -> int:
	var n := 0
	for name in entries:
		if str(name).contains(needle):
			n += 1
	return n


func _count_method(entries: Dictionary, method: int) -> int:
	var n := 0
	for name in entries:
		if int(entries[name].get("method", -1)) == method:
			n += 1
	return n


func _has_prefix(entries: Dictionary, prefix: String) -> bool:
	for name in entries:
		if str(name).begins_with(prefix):
			return true
	return false


func _byte_diff_count(a: String, b: String) -> int:
	var ba := FileAccess.get_file_as_bytes(a)
	var bb := FileAccess.get_file_as_bytes(b)
	var n := absi(ba.size() - bb.size())
	var shared := mini(ba.size(), bb.size())
	for i in shared:
		if ba[i] != bb[i]:
			n += 1
	return n


func _dirs_of(entries: Dictionary) -> PackedStringArray:
	var dirs := {}
	for key in entries:
		var name := str(key)
		var parts := name.split("/")
		if parts.size() < 2:
			continue
		var d := ""
		for i in parts.size() - 1:
			d = parts[i] if d == "" else d + "/" + parts[i]
			if d.begins_with(".godot"):
				continue
			dirs[d] = true
	var out := PackedStringArray(dirs.keys())
	out.sort()
	return out


func _frame_numbers(text: String) -> PackedInt32Array:
	var out := PackedInt32Array()
	for line in text.split("\n"):
		if line.begins_with("EXPORT_PROD_FRAME "):
			out.append(line.substr(18).strip_edges().to_int())
	return out


func _fmt_ints(values: PackedInt32Array) -> String:
	var parts := PackedStringArray()
	for v in values:
		parts.append(str(v))
	return "[%s]" % ",".join(parts)


func _fmt_strings(values: PackedStringArray) -> String:
	return "[%s]" % ",".join(values)
