extends SceneTree
# export_launch_s05 — r102 C1: export_presets.cfg feature census.
#
# Scenario: read the installed Linux export templates' supported feature list
# (template dir census + ELF headers + the runtime feature-tag vector of the
# exported template binary) versus the preset features the exporter actually
# honors (custom_features, binary_format/architecture, texture_format gates),
# actual behavior only. Every nested Godot output is redirected to log files
# under <root>/<variant>/logs and never echoed; the PASS lines carry only
# derived booleans, tokens, counts and digests.
#
# Battery launch shape (one arm per process, 8s fixture bound):
#   godot --headless --path <fixture proj> --script res://export_launch_s05.gd -- --arm=<arm>
#
# Arms:
#   tmpl     -> export_launch_tmpl_census          (templates dir + version.txt
#               + 8 linux template files + ELF class/machine of the x86_64
#               release/debug, arm64, arm32, x86_32 templates + the *editor*
#               feature-tag vector digest, measured in-process)
#   tags     -> export_launch_feat_tags_release    (--export-release with
#               custom_features="r102e5cust", embed_pck=true, x86_64; run the
#               self-contained binary headless; feature vector digest + core)
#   tagsdbg  -> export_launch_feat_tags_debug      (--export-debug arm)
#   custctl  -> export_launch_feat_custom_ctl      (release arm with
#               custom_features="" — the counterfactual for the custom tag)
#   arch     -> export_launch_arch_gate            (architecture="arm64" arm:
#               product ELF + template ELF headers + the verbatim
#               Exec-format-error launch class on this x86_64 host)
#   tex_on   -> export_launch_texture_gate_on      (--export-pack, preset
#               texture_format/s3tc_bptc=true; packed .ctex present; the pack
#               boots under the editor binary with load_ok=true)
#   tex_off  -> export_launch_texture_gate_off     (same, s3tc_bptc=false: the
#               exporter drops the s3tc ctex entry and strips the remap path;
#               the pack fails to load its scene at runtime)
#   tex_etc2 -> export_launch_texture_gate_etc2    (s3tc_bptc=false,
#               etc2_astc=true: enabling the other format does NOT create an
#               on-disk etc2 variant — same empty remap as tex_off)
#
# Measured referents (r102-E5 scratch, godot 4.7.2.stable.arch_linux.ed1daf0bf):
#   editor in-process vector    sha256=95d8fa4974fa5b13dc6b8f0c1ac0af10835d2d8a19559a2c74ce0730b5b5122f
#   release template + cust     sha256=1adac65f3438278debe5439edb7347993eff28c5b7e4476115a6c808e2c96886
#   debug template + cust       sha256=15f50436d2368a3af90b9b710d3bb22d0ae18e46a6b07be7c8ffb88755de4144
#   release template no cust    sha256=8eb17bf673139dccda55c1b6725067f15338309179b1032d1f207258fc19e71b
#   arm64 product               ELF64 e_machine=0xb7; ./app.arm64 -> exit 126,
#                               "cannot execute binary file: Exec format error"
#   tex_off / tex_etc2 pack     0 .ctex entries, packed tex.png.import has no
#                               path.* line, run exit 1 "Resource file not found"
#
# Scratch policy: every arm builds its project under <root>/<variant>/proj and
# writes under <root>/<variant>/out, where <root> is the first candidate of
# EXPORT_LAUNCH_S05_ROOT, EXPORT_LAUNCH_ROOT, $TMPDIR/export_launch_s05, the
# engine user-data dir, /tmp/export_launch_s05 that passes a 4096-byte
# write+readback probe. Exports run under a user-namespace private /tmp when
# unshare is available (the 4.7.2 packer serializes project.binary through a
# fixed /tmp temp path; r101 E0 measured EDQUOT corruption there).

const PRESET := "Linux/X11"
const CUSTOM_FEATURE := "r102e5cust"
const MAIN_TSCN := "[gd_scene load_steps=2 format=3]\n\n[ext_resource type=\"Script\" path=\"res://main.gd\" id=\"1\"]\n\n[node name=\"Main\" type=\"Node\"]\nscript = ExtResource(\"1\")\n"
const TEX_TSCN := "[gd_scene load_steps=3 format=3]\n\n[ext_resource type=\"Script\" path=\"res://main.gd\" id=\"1\"]\n[ext_resource type=\"Texture2D\" path=\"res://tex.png\" id=\"2\"]\n\n[node name=\"Main\" type=\"Node\"]\nscript = ExtResource(\"1\")\n\n[node name=\"Sprite\" type=\"Sprite2D\" parent=\".\"]\ntexture = ExtResource(\"2\")\n"
const TEX_MAIN_GD := "extends Node\n\nfunc _ready() -> void:\n\tvar t := load(\"res://tex.png\")\n\tprint(\"TEXPROBE boot load_ok=%s\" % (t != null))\n\tget_tree().quit()\n"
const TEX_IMPORT_PARAMS := "[remap]\n\nimporter=\"texture\"\ntype=\"CompressedTexture2D\"\n\n[deps]\n\nsource_file=\"res://tex.png\"\n\n[params]\n\ncompress/mode=2\ncompress/lossy_quality=0.7\ncompress/hdr_compression=1\ncompress/normal_map=0\ncompress/channel_pack=0\nmipmaps/generate=true\nroughness/mode=0\nroughness/src_normal=\"\"\nprocess/fix_alpha_border=true\nprocess/premult_alpha=false\nprocess/normal_map_invert_y=false\nprocess/hdr_as_srgb=false\nprocess/hdr_clamp_exposure=false\nprocess/size_limit=0\ndetect_3d/compress_to=0\n"

# Runtime feature-tag probes, fixed order — the joined "name=bool" string is
# the referent whose sha256 the PASS lines pin.
const PROBES := [
	"android", "arm", "arm32", "arm64", "astc", "bptc", "bsd", "canvas_item",
	"compatibility", "d3d12", "debug", "dedicated_server", "deprecated", "editor",
	"etc", "etc2", "forward_plus", "html5", "ios", "javascript", "linux", "linuxbsd",
	"macos", "metal", "mobile", "opengl3", "osx", "pc", "pvrtc", "release", "riscv",
	"s3tc", "template", "tvos", "uwp", "vulkan", "web", "windows", "winrt", "x11",
	"x86", "x86_32", "x86_64", "32", "64", "r102e5cust",
]

# Curated readable subset pinned next to the digest.
const CORE := ["linux", "linuxbsd", "pc", "x86_64", "64", "template", "editor", "release", "debug"]

const LINUX_TEMPLATES := [
	"linux_debug.x86_64", "linux_release.x86_64", "linux_debug.x86_32", "linux_release.x86_32",
	"linux_debug.arm32", "linux_release.arm32", "linux_debug.arm64", "linux_release.arm64",
]

var arm := ""
var _items: PackedStringArray = []
var _root := ""
var _unshare := false


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
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
		"tmpl":
			_arm_tmpl()
		"tags":
			_arm_tags("release")
		"tagsdbg":
			_arm_tags("debug")
		"custctl":
			_arm_custctl()
		"arch":
			_arm_arch()
		"tex_on":
			_arm_tex("tex_on", true, false)
		"tex_off":
			_arm_tex("tex_off", false, false)
		"tex_etc2":
			_arm_tex("tex_etc2", false, true)
		_:
			_fail("unknown_arm")


# ------------------------------------------------------------------ receipts

func _fail(reason: String) -> void:
	print("FAIL export_launch %s reason=%s" % [arm, reason])
	quit(1)


func _it(key: String, value) -> void:
	_items.append("%s=%s" % [key, str(value)])


func _ok_kind(kind: String) -> void:
	print("PASS export_launch %s %s" % [kind, " ".join(_items)])
	quit(0)


func _diag(key: String, value) -> void:
	print("EXPORT_LAUNCH_S05_DIAG %s %s=%s" % [arm, key, str(value)])


# ------------------------------------------------------------------- scratch

func _pick_root() -> String:
	var candidates: PackedStringArray = []
	if OS.get_environment("EXPORT_LAUNCH_S05_ROOT") != "":
		candidates.append(OS.get_environment("EXPORT_LAUNCH_S05_ROOT"))
	if OS.get_environment("EXPORT_LAUNCH_ROOT") != "":
		candidates.append(OS.get_environment("EXPORT_LAUNCH_ROOT"))
	if OS.get_environment("TMPDIR") != "":
		candidates.append(OS.get_environment("TMPDIR").path_join("export_launch_s05"))
	candidates.append(OS.get_user_data_dir().path_join("export_launch_s05"))
	candidates.append("/tmp/export_launch_s05")
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


func _fresh_variant(variant: String) -> void:
	OS.execute("/usr/bin/sh", PackedStringArray(["-c", "rm -rf " + _q(_variant_dir(variant))]))
	DirAccess.make_dir_recursive_absolute(_proj_dir(variant))
	DirAccess.make_dir_recursive_absolute(_out_dir(variant))


func _write_text(path: String, text: String) -> bool:
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		return false
	f.store_string(text)
	f.close()
	return true


func _write_png(path: String) -> bool:
	var img := Image.create(64, 64, false, Image.FORMAT_RGBA8)
	for y in 64:
		for x in 64:
			img.set_pixel(x, y, Color(float(x) / 63.0, float((x * y) % 64) / 63.0, float(y) / 63.0, 1.0))
	return img.save_png(path) == OK


func _run_logged(body: String, log_path: String, isolate := false) -> int:
	DirAccess.make_dir_recursive_absolute(log_path.get_base_dir())
	var script := body
	if isolate and _unshare:
		# Private /tmp for the packer's fixed tmpproject.binary temp path.
		script = "mount -t tmpfs -o size=64M tmpfs /tmp || exit 97\n" + body
		script = "unshare -m --map-root-user /usr/bin/sh -c " + _q(script)
	_diag("nested", body.replace("\n", " ; "))
	return OS.execute("/usr/bin/sh", PackedStringArray(["-c", "exec > " + _q(log_path) + " 2>&1\n" + script]))


func _sha256_text(text: String) -> String:
	var ctx := HashingContext.new()
	if ctx.start(HashingContext.HASH_SHA256) != OK:
		return ""
	if ctx.update(text.to_utf8_buffer()) != OK:
		return ""
	return ctx.finish().hex_encode()


# --------------------------------------------------------------- referents

func _vec_string(flags: Dictionary) -> String:
	var parts: PackedStringArray = []
	for p in PROBES:
		parts.append("%s=%s" % [p, str(flags.get(p, false))])
	return " ".join(parts)


func _vec_digest(flags: Dictionary) -> String:
	return _sha256_text(_vec_string(flags))


func _core_string(flags: Dictionary) -> String:
	var parts: PackedStringArray = []
	for k in CORE:
		parts.append("%s%s" % [k, "+" if flags.get(k, false) else "-"])
	return ",".join(parts)


func _parse_vec(text: String) -> Dictionary:
	var flags := {}
	for line in text.split("\n"):
		var l := line.strip_edges()
		if not l.begins_with("FEATVEC "):
			continue
		for pair in l.substr(8).split(" ", false):
			var kv := pair.split("=")
			if kv.size() == 2:
				flags[kv[0]] = kv[1] == "true"
	return flags


func _run_class(text: String, code: int) -> String:
	if text.contains("Exec format error"):
		return "exec_format_error"
	if text.contains("Resource file not found"):
		return "resource_file_not_found"
	if code == 0:
		return "clean"
	return "other"


func _elf_token(path: String) -> String:
	var h := FileAccess.get_file_as_bytes(path)
	if h.size() < 20 or h.decode_u32(0) != 0x464c457f:
		return "none"
	var cls := "ELF32" if h[4] == 1 else ("ELF64" if h[4] == 2 else "ELF0")
	return "%s_%02x" % [cls, h.decode_u16(18)]


func _data_home() -> String:
	var xdg := OS.get_environment("XDG_DATA_HOME")
	if xdg != "":
		return xdg
	return OS.get_environment("HOME").path_join(".local/share")


func _templates_dir() -> String:
	var root := _data_home().path_join("godot").path_join("export_templates")
	var v: Dictionary = Engine.get_version_info()
	var prefix := "%d.%d.%d" % [v["major"], v["minor"], v["patch"]]
	var direct := root.path_join("%s.%s" % [prefix, v["status"]])
	if DirAccess.dir_exists_absolute(direct):
		return direct
	if DirAccess.dir_exists_absolute(root):
		for d in DirAccess.get_directories_at(root):
			if d.begins_with(prefix):
				return root.path_join(d)
	return ""


# ---------------------------------------------------------------- projects

func _preset_text(custom_features: String, arch: String, embed: bool, s3tc_bptc: bool, etc2_astc: bool) -> String:
	return ("[preset.0]\n\nname=\"Linux/X11\"\nplatform=\"Linux/X11\"\nrunnable=true\n"
		+ "advanced_options=false\ndedicated_server=false\ncustom_features=\"%s\"\n"
		+ "export_filter=\"all_resources\"\ninclude_filter=\"\"\nexclude_filter=\"\"\nexport_path=\"\"\n\n"
		+ "[preset.0.options]\nbinary_format/architecture=\"%s\"\nbinary_format/embed_pck=%s\n"
		+ "texture_format/s3tc_bptc=%s\ntexture_format/etc2_astc=%s\n") % [
			custom_features, arch, str(embed), str(s3tc_bptc), str(etc2_astc)]


func _probe_main() -> String:
	var literal: PackedStringArray = []
	for p in PROBES:
		literal.append("\"%s\"" % p)
	return ("extends Node\n\nconst PROBES := [" + ", ".join(literal) + "]\n\n\n"
		+ "func _ready() -> void:\n\tvar parts: PackedStringArray = []\n"
		+ "\tfor p in PROBES:\n\t\tparts.append(\"%s=%s\" % [p, str(OS.has_feature(p))])\n"
		+ "\tprint(\"FEATVEC \" + \" \".join(parts))\n\tget_tree().quit()\n")


func _build_probe(variant: String, custom_features: String, arch: String, embed: bool, s3tc_bptc: bool) -> String:
	_fresh_variant(variant)
	var proj := _proj_dir(variant)
	_write_text(proj.path_join("project.godot"), "config_version=5\n\n[application]\nconfig/name=\"ExportLaunchS05\"\nrun/main_scene=\"res://main.tscn\"\nconfig/features=PackedStringArray(\"4.7\")\n")
	_write_text(proj.path_join("main.gd"), _probe_main())
	_write_text(proj.path_join("main.tscn"), MAIN_TSCN)
	_write_text(proj.path_join("export_presets.cfg"), _preset_text(custom_features, arch, embed, s3tc_bptc, false))
	return proj


func _build_tex(variant: String, s3tc_bptc: bool, etc2_astc: bool) -> String:
	_fresh_variant(variant)
	var proj := _proj_dir(variant)
	_write_text(proj.path_join("project.godot"), "config_version=5\n\n[application]\nconfig/name=\"ExportLaunchS05Tex\"\nrun/main_scene=\"res://main.tscn\"\nconfig/features=PackedStringArray(\"4.7\")\n")
	_write_text(proj.path_join("main.gd"), TEX_MAIN_GD)
	_write_text(proj.path_join("main.tscn"), TEX_TSCN)
	_write_text(proj.path_join("tex.png.import"), TEX_IMPORT_PARAMS)
	if not _write_png(proj.path_join("tex.png")):
		_diag("png_write", "failed")
	_write_text(proj.path_join("export_presets.cfg"), _preset_text("", "x86_64", false, s3tc_bptc, etc2_astc))
	return proj


func _export(variant: String, mode: String, out_path: String) -> int:
	var proj := _proj_dir(variant)
	var log_path := _log_path(variant, "export_" + mode)
	var body := "cd " + _q(proj) + "\n" + _q(_godot()) + " --headless --path " + _q(proj) + " --export-" + mode + " " + _q(PRESET) + " " + _q(out_path)
	return _run_logged(body, log_path, true)


# ------------------------------------------------------------------- pack

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
		off += 36
		entries[name] = {"size": size, "offset": foff}
	return {"magic": "GDPC", "count": count, "file_base": base, "entries": entries}


func _entry_text(path: String, census: Dictionary, name: String) -> String:
	var entries: Dictionary = census["entries"]
	if not entries.has(name):
		return ""
	var bytes := FileAccess.get_file_as_bytes(path)
	var e: Dictionary = entries[name]
	var start: int = census["file_base"] + e["offset"]
	var end: int = start + e["size"]
	if end > bytes.size():
		return ""
	return bytes.slice(start, end).get_string_from_utf8()


# ---------------------------------------------------------------------- arms

func _arm_tmpl() -> void:
	var flags := {}
	for p in PROBES:
		flags[p] = OS.has_feature(p)
	_diag("edit_sha256", _vec_digest(flags))
	var tdir := _templates_dir()
	if tdir == "":
		_fail("templates_dir_missing")
		return
	_diag("templates_dir", tdir)
	var version := FileAccess.get_file_as_string(tdir.path_join("version.txt")).strip_edges()
	var present := 0
	for n in LINUX_TEMPLATES:
		if FileAccess.file_exists(tdir.path_join(n)):
			present += 1
	_it("version", version)
	_it("tmpl_dir", tdir.get_file())
	_it("linux_templates", present)
	_it("rel64", _elf_token(tdir.path_join("linux_release.x86_64")))
	_it("dbg64", _elf_token(tdir.path_join("linux_debug.x86_64")))
	_it("arm64", _elf_token(tdir.path_join("linux_release.arm64")))
	_it("arm32", _elf_token(tdir.path_join("linux_release.arm32")))
	_it("x8632", _elf_token(tdir.path_join("linux_release.x86_32")))
	_it("edit_core", _core_string(flags))
	_it("edit_sha256", _vec_digest(flags))
	_ok_kind("tmpl")


func _arm_tags(mode: String) -> void:
	var variant := "tags" if mode == "release" else "tagsdbg"
	_build_probe(variant, CUSTOM_FEATURE, "x86_64", true, true)
	var product := _out_dir(variant).path_join("app.x86_64")
	var code := _export(variant, mode, product)
	if code != 0:
		_fail("export_exit:%d" % code)
		return
	if not FileAccess.file_exists(product):
		_fail("product_missing")
		return
	var run_log := _log_path(variant, "run")
	var run_code := _run_logged("cd " + _q(_out_dir(variant)) + "\n./app.x86_64 --headless", run_log)
	var run_text := FileAccess.get_file_as_string(run_log)
	var flags := _parse_vec(run_text)
	DirAccess.remove_absolute(product)
	if flags.is_empty():
		_fail("no_featvec")
		return
	_it("export_exit", code)
	_it("run_exit", run_code)
	_it("template", flags.get("template", false))
	_it("editor", flags.get("editor", false))
	_it("release", flags.get("release", false))
	_it("debug", flags.get("debug", false))
	_it("cust", flags.get("r102e5cust", false))
	_it("core", _core_string(flags))
	_it("vec_sha256", _vec_digest(flags))
	_ok_kind("feat_rel" if mode == "release" else "feat_dbg")


func _arm_custctl() -> void:
	var variant := "custctl"
	_build_probe(variant, "", "x86_64", true, true)
	var product := _out_dir(variant).path_join("app.x86_64")
	var code := _export(variant, "release", product)
	if code != 0:
		_fail("export_exit:%d" % code)
		return
	if not FileAccess.file_exists(product):
		_fail("product_missing")
		return
	var run_log := _log_path(variant, "run")
	var run_code := _run_logged("cd " + _q(_out_dir(variant)) + "\n./app.x86_64 --headless", run_log)
	var run_text := FileAccess.get_file_as_string(run_log)
	var flags := _parse_vec(run_text)
	DirAccess.remove_absolute(product)
	if flags.is_empty():
		_fail("no_featvec")
		return
	_it("export_exit", code)
	_it("run_exit", run_code)
	_it("cust", flags.get("r102e5cust", false))
	_it("template", flags.get("template", false))
	_it("core", _core_string(flags))
	_it("vec_sha256", _vec_digest(flags))
	_ok_kind("feat_custctl")


func _arm_arch() -> void:
	var variant := "arch"
	_build_probe(variant, "", "arm64", true, true)
	var out_dir := _out_dir(variant)
	var product := out_dir.path_join("app.arm64")
	var code := _export(variant, "release", product)
	if code != 0:
		_fail("export_exit:%d" % code)
		return
	if not FileAccess.file_exists(product):
		_fail("product_missing")
		return
	var tdir := _templates_dir()
	var run_log := _log_path(variant, "run")
	var run_code := _run_logged("cd " + _q(out_dir) + "\n./app.arm64 --headless", run_log)
	var run_text := FileAccess.get_file_as_string(run_log)
	_it("export_exit", code)
	_it("product", _elf_token(product))
	_it("template_arm64", _elf_token(tdir.path_join("linux_release.arm64")) if tdir != "" else "none")
	_it("template_x64", _elf_token(tdir.path_join("linux_release.x86_64")) if tdir != "" else "none")
	_it("run_exit", run_code)
	_it("run_class", _run_class(run_text, run_code))
	DirAccess.remove_absolute(product)
	_ok_kind("arch")


func _arm_tex(variant: String, s3tc_bptc: bool, etc2_astc: bool) -> void:
	_build_tex(variant, s3tc_bptc, etc2_astc)
	var pack := _out_dir(variant).path_join("tex.pck")
	var code := _export(variant, "pack", pack)
	if code != 0:
		_fail("export_exit:%d" % code)
		return
	if not FileAccess.file_exists(pack):
		_fail("pack_missing")
		return
	var census := _census_pck(pack)
	if census.is_empty():
		_fail("pack_parse_failed")
		return
	var entries: Dictionary = census["entries"]
	var ctex := 0
	var suffix := "none"
	var names := PackedStringArray(entries.keys())
	names.sort()
	for n in names:
		if n.ends_with(".ctex"):
			ctex += 1
			suffix = n.get_file().get_basename().get_extension()
	var import_text := _entry_text(pack, census, "tex.png.import")
	var run_log := _log_path(variant, "run_pack")
	var run_code := _run_logged("cd /\n" + _q(_godot()) + " --headless --main-pack " + _q(pack) + " --quit-after 3", run_log)
	var run_text := FileAccess.get_file_as_string(run_log)
	_it("export_exit", code)
	_it("ctex_entries", ctex)
	_it("ctex_suffix", suffix)
	_it("import_path", import_text.contains("path."))
	_it("import_deps", import_text.contains("[deps]"))
	_it("run_exit", run_code)
	_it("load_ok", run_text.contains("load_ok=true"))
	_it("run_class", _run_class(run_text, run_code))
	_ok_kind(variant)
