extends SceneTree
# export_div_s01 — r103 C1: preset-path vs CLI-pack-path divergence (seat E1).
#
# Scenario: one scratch child project, two Linux/X11 presets (Embed has
# binary_format/embed_pck=true, Stock has false), exported through BOTH CLI
# entry points and censused from the harness side:
#
#   preset path  --export-release <preset> <path>
#     - the CONTAINER is chosen by the preset's binary_format/embed_pck option
#       (embedded binary+t trailer, or template binary + <name>.pck sidecar);
#     - the OUTPUT EXTENSION is ignored: `--export-release Embed out.pck`
#       still writes the full ~73 MB embedded binary, named `out.pck`.
#
#   CLI pack path  --export-pack <preset> <path>
#     - always project-data only (no binary), and the EXTENSION selects the
#       container format: `.pck` -> PCK (`savepack`), `.zip` -> ZIP (`savezip`);
#     - the preset's embed_pck option is not consulted (a preset with
#       embed_pck=true emits no binary here).
#
# Payload identity (the measured law): the container choice never changes the
# exported project data. The `.pck` sidecar written by `--export-release` with
# embed_pck=false is byte-identical (sha256) to the `--export-pack` output, and
# the payload embedded in the binary carries the same entry table + data region
# as the standalone pack; only container framing differs (measured: file_base
# 104 vs 112, embedded payload 1972 B + 4 B pad + 12 B `<u64 size><u32 'GDPC'>`
# trailer vs 1976 B standalone).
#
# Arms (one arm per process, one PASS line per arm; battery launch shape):
#   godot --headless --path <fixture proj> --script res://export_div_s01.gd -- --arm=<arm>
#
#   pack  -> export_div_s01_cli_pack_census   (1 export,  ~2.5 s)
#   zip   -> export_div_s01_cli_zip_format    (2 exports, ~5 s)
#   ext   -> export_div_s01_preset_extension_ignored (2 exports, ~5 s)
#   ident -> export_div_s01_sidecar_equals_cli       (2 exports, ~5 s)
#   embed -> export_div_s01_embedded_payload_identity(2 exports, ~5 s)
#
# Every arm re-stages and re-exports its own artifacts: no cross-row state is
# required (artifacts are cleared per arm), so each row passes standalone.
#
# Scratch policy: <root>/div_s01/<arm>/{proj,out,logs}; <root> is the first
# candidate of $EXPORT_DIV_ROOT, $EXPORT_LAUNCH_ROOT, <engine user-data
# dir>/export_div_s01, $TMPDIR/export_div_s01, /tmp/export_div_s01 that passes
# a 4096-byte write+readback probe. Host paths appear only in EXPORT_DIV_DIAG
# lines, never inside pinned PASS text.
#
# TMP isolation: the 4.7.2 packer serializes project.binary through a fixed
# /tmp/tmpproject.binary-<rand> path ($TMPDIR not honored, r101 strace finding,
# EDQUOT under a full per-user /tmp quota) — every export runs inside
# `unshare -m --map-root-user` with a private tmpfs /tmp when user namespaces
# are available AND the chosen root is not itself under /tmp (a 64 MB tmpfs
# would truncate the ~73 MB embedded artifact).
#
# Evidence rule: nested Godot output is never echoed — every nested shell is
# redirected to <root>/div_s01/<arm>/logs/*.log and PASS lines carry only
# derived booleans, hex magics, counts and sha256 equality flags. No arm prints
# "ERROR:"/"SCRIPT ERROR:"/"Parse Error:".
#
# Measured 2026-10-18 on godot 4.7.2.stable.arch_linux.ed1daf0bf (host load
# 1.8, scratch /var/tmp/r103c-E1): export_pack 2.11-2.27 s, export_release
# 2.03 s, census < 50 ms — every arm stays under the 8 s battery bound.

const VARIANT := "div_s01"
const PRESET_EMBED := "Embed"
const PRESET_STOCK := "Stock"
const MAGIC_PCK := "47445043"  # ASCII "GDPC" in file order
const MAGIC_ZIP := "504b0304"
const MAGIC_ELF := "7f454c46"
const PBIN := "project.binary"
const NONDATA := "extra.txt"

const PROJECT_GODOT := "config_version=5\n\n[application]\nconfig/name=\"ExportDivS01\"\nrun/main_scene=\"res://main.tscn\"\nconfig/features=PackedStringArray(\"4.7\")\n\n[display]\nwindow/size/viewport_width=320\nwindow/size/viewport_height=180\n"
const PRESETS := "[preset.0]\nname=\"Embed\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\ninclude_filter=\"\"\nexclude_filter=\"\"\nexport_path=\"\"\n\n[preset.0.options]\nbinary_format/architecture=\"x86_64\"\nbinary_format/embed_pck=true\n\n[preset.1]\nname=\"Stock\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\ninclude_filter=\"\"\nexclude_filter=\"\"\nexport_path=\"\"\n\n[preset.1.options]\nbinary_format/architecture=\"x86_64\"\nbinary_format/embed_pck=false\n"
const MAIN_GD := "extends Node\n\nfunc _ready() -> void:\n\tprint(\"EXPORT_DIV_MAIN boot scene=main\")\n\tget_tree().quit(0)\n"
const MAIN_TSCN := "[gd_scene load_steps=2 format=3]\n\n[ext_resource type=\"Script\" path=\"res://main.gd\" id=\"1\"]\n\n[node name=\"Main\" type=\"Node\"]\nscript = ExtResource(\"1\")\n"

var arm := ""
var _root := ""
var _unshare := false


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	if arm == "":
		arm = "pack"
	call_deferred("_run")


func _run() -> void:
	_root = _pick_root()
	_diag("root", _root)
	if _root == "":
		_fail("no_writable_scratch_root")
		return
	_unshare = _probe_unshare() and not _root.begins_with("/tmp")
	_diag("userns_tmp_isolation", _unshare)
	match arm:
		"pack":
			_arm_pack()
		"zip":
			_arm_zip()
		"ext":
			_arm_ext()
		"ident":
			_arm_ident()
		"embed":
			_arm_embed()
		_:
			_fail("unknown_arm")


# ------------------------------------------------------------------ receipts

func _fail(reason: String) -> void:
	print("FAIL export_div s01 arm=%s reason=%s" % [arm, reason])
	quit(1)


func _verdict(fields: PackedStringArray, bad: String) -> void:
	if bad == "":
		print("PASS export_div s01 arm=%s %s" % [arm, " ".join(fields)])
		quit(0)
	else:
		print("FAIL export_div s01 arm=%s reason=%s %s" % [arm, bad, " ".join(fields)])
		quit(1)


func _diag(key: String, value) -> void:
	print("EXPORT_DIV_DIAG %s %s=%s" % [arm, key, str(value)])


# ------------------------------------------------------------------- scratch

func _pick_root() -> String:
	var candidates: PackedStringArray = []
	if OS.get_environment("EXPORT_DIV_ROOT") != "":
		candidates.append(OS.get_environment("EXPORT_DIV_ROOT"))
	if OS.get_environment("EXPORT_LAUNCH_ROOT") != "":
		candidates.append(OS.get_environment("EXPORT_LAUNCH_ROOT"))
	candidates.append(OS.get_user_data_dir().path_join(VARIANT))
	if OS.get_environment("TMPDIR") != "":
		candidates.append(OS.get_environment("TMPDIR").path_join(VARIANT))
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


func _probe_unshare() -> bool:
	var cmd := "exec > /dev/null 2>&1\nunshare -m --map-root-user /usr/bin/sh -c 'mount -t tmpfs -o size=16M tmpfs /tmp && test -w /tmp'"
	return OS.execute("/usr/bin/sh", PackedStringArray(["-c", cmd])) == 0


func _godot() -> String:
	var exe := OS.get_executable_path()
	return exe if exe != "" else "/usr/bin/godot"


func _q(s: String) -> String:
	return "'" + s.replace("'", "'\\''") + "'"


func _arm_dir() -> String:
	return _root.path_join(VARIANT).path_join(arm)


func _proj_dir() -> String:
	return _arm_dir().path_join("proj")


func _out_dir(slug: String) -> String:
	return _arm_dir().path_join("out").path_join(slug)


func _log_path(name: String) -> String:
	return _arm_dir().path_join("logs").path_join(name + ".log")


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


func _clear_dir(path: String) -> void:
	var d := DirAccess.open(path)
	if d == null:
		return
	for f in d.get_files():
		DirAccess.remove_absolute(path.path_join(f))


func _files_in(dir: String) -> PackedStringArray:
	var d := DirAccess.open(dir)
	if d == null:
		return PackedStringArray()
	return d.get_files()


func _files_matching(dir: String, ext: String) -> int:
	var n := 0
	for f in _files_in(dir):
		if f.ends_with(ext):
			n += 1
	return n


func _file_size(path: String) -> int:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return -1
	var size := f.get_length()
	f.close()
	return size


func _run_logged(body: String, log_path: String, isolate := false) -> int:
	_mkdir(log_path.get_base_dir())
	var script := body
	if isolate and _unshare:
		# Private /tmp for the packer's fixed tmpproject.binary temp path.
		script = "mount -t tmpfs -o size=64M tmpfs /tmp || exit 97\n" + body
		script = "unshare -m --map-root-user /usr/bin/sh -c " + _q(script)
	_diag("nested", body.replace("\n", " ; "))
	return OS.execute("/usr/bin/sh", PackedStringArray(["-c", "exec > " + _q(log_path) + " 2>&1\n" + script]))


# ------------------------------------------------------------------ projects

func _build_project() -> String:
	var proj := _proj_dir()
	_mkdir(proj)
	_write_text(proj.path_join("project.godot"), PROJECT_GODOT)
	_write_text(proj.path_join("export_presets.cfg"), PRESETS)
	_write_text(proj.path_join("main.gd"), MAIN_GD)
	_write_text(proj.path_join("main.tscn"), MAIN_TSCN)
	_write_text(proj.path_join(NONDATA), "ALPHA\n")
	return proj


func _export(slug: String, cli: String, name: String) -> String:
	var proj := _proj_dir()
	var out_dir := _out_dir(slug)
	_clear_dir(out_dir)
	_mkdir(out_dir)
	var out_path := out_dir.path_join(name)
	var body := "cd " + _q(proj) + "\n" + _q(_godot()) + " --headless --path " + _q(proj) + " " + cli + " " + _q(out_path)
	_diag("export_" + slug, body.replace("\n", " ; "))
	var code := _run_logged(body, _log_path("export_" + slug), true)
	_diag("export_" + slug + "_rc", code)
	return out_path


func _export_pack(slug: String, preset: String, name: String) -> String:
	return _export(slug, "--export-pack " + _q(preset), name)


func _export_release(slug: String, preset: String, name: String) -> String:
	return _export(slug, "--export-release " + _q(preset), name)


# ------------------------------------------------------------------ pck parse

func _hex4(b: PackedByteArray) -> String:
	var s := ""
	for i in range(min(4, b.size())):
		s += "%02x" % b[i]
	return s


func _head4(path: String) -> String:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return "missing"
	var b := f.get_buffer(4)
	f.close()
	return _hex4(b)


func _tail4(path: String) -> String:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return "missing"
	var total := f.get_length()
	f.seek(max(0, total - 4))
	var b := f.get_buffer(4)
	f.close()
	return _hex4(b)


# Godot 4 PCK: "GDPC" u32 fmt, u32 major/minor/patch (fmt>=2), u32 flags,
# u64 file_base, u64 dir_off, pad to file_base, data, dir: u32 count then per
# entry u32 path_len (NUL/zero padded), path, u64 off (rel file_base), u64 size,
# 16 B md5, u32 flags. Layout re-derived from measured artifacts (see shard).
func _parse_pck(path: String) -> Dictionary:
	var out := {"ok": false, "why": "", "file_base": 0, "dir_off": 0, "names": PackedStringArray(), "entries": {}, "fmt": 0}
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		out["why"] = "open_failed"
		return out
	var total := f.get_length()
	if total < 0x28:
		out["why"] = "too_short"
		f.close()
		return out
	if _hex4(f.get_buffer(4)) != MAGIC_PCK:
		out["why"] = "bad_magic"
		f.close()
		return out
	out["fmt"] = f.get_32()
	f.get_32()
	f.get_32()
	f.get_32()
	f.get_32()
	out["file_base"] = f.get_64()
	out["dir_off"] = f.get_64()
	f.seek(out["dir_off"])
	var count := f.get_32()
	if count < 0 or count > 100000:
		out["why"] = "bad_count"
		f.close()
		return out
	var names := PackedStringArray()
	var entries := {}
	for i in range(count):
		var name_len := f.get_32()
		if name_len < 0 or name_len > 4096 or f.get_position() + name_len + 36 > total:
			out["why"] = "bad_entry"
			f.close()
			return out
		var raw := f.get_buffer(name_len)
		var cut0 := raw.find(0)
		var name := raw.slice(0, cut0 if cut0 != -1 else raw.size()).get_string_from_ascii()
		var off := f.get_64()
		var size := f.get_64()
		var md5 := f.get_buffer(16)
		f.get_32()
		names.append(name)
		entries[name] = {"off": off, "size": size, "md5": md5}
	out["names"] = names
	out["entries"] = entries
	out["ok"] = true
	f.close()
	return out


func _region(path: String, from: int, to: int) -> PackedByteArray:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return PackedByteArray()
	f.seek(from)
	var b := f.get_buffer(to - from)
	f.close()
	return b


# Embedded payload of a release binary: file ends with
# <u64 payload_size><u32 'GDPC'>; payload starts payload_size bytes earlier.
# Returns {"ok":bool, "start":int, "size":int} — the caller extracts/copies it.
func _embedded_payload(path: String) -> Dictionary:
	var out := {"ok": false, "start": 0, "size": 0}
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return out
	var total := f.get_length()
	if total < 16:
		f.close()
		return out
	f.seek(total - 12)
	var size := f.get_64()
	if f.get_32() != 0x43504447:
		f.close()
		return out
	var start := total - 12 - size
	if start < 0:
		f.close()
		return out
	f.seek(start)
	var ok := _hex4(f.get_buffer(4)) == MAGIC_PCK
	f.close()
	out["ok"] = ok
	out["start"] = start
	out["size"] = size
	return out


func _copy_region(path: String, from: int, size: int, dest: String) -> bool:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return false
	f.seek(from)
	var w := FileAccess.open(dest, FileAccess.WRITE)
	if w == null:
		f.close()
		return false
	var remaining := size
	while remaining > 0:
		var chunk := f.get_buffer(min(65536, remaining))
		if chunk.size() == 0:
			break
		w.store_buffer(chunk)
		remaining -= chunk.size()
	w.close()
	f.close()
	return remaining == 0


func _sha(path: String) -> String:
	return FileAccess.get_sha256(path)


func _contains_bytes(path: String, needle: String) -> bool:
	var hay := FileAccess.get_file_as_bytes(path)
	var ndl := needle.to_utf8_buffer()
	if ndl.size() == 0 or hay.size() < ndl.size():
		return false
	for i in range(hay.size() - ndl.size() + 1):
		if hay.slice(i, i + ndl.size()) == ndl:
			return true
	return false


# ---------------------------------------------------------------------- arms

func _prelude() -> bool:
	if _root == "":
		return false
	_build_project()
	_clear_dir(_arm_dir().path_join("logs"))
	return true


func _export_ok(path: String, slug: String) -> bool:
	if not FileAccess.file_exists(path):
		return false
	var log := FileAccess.get_file_as_string(_log_path("export_" + slug))
	return log.contains("[ DONE ]")


# arm=pack: --export-pack ignores the preset's embed_pck=true and emits exactly
# one project-data artifact; extension .pck selects the PCK container.
func _arm_pack() -> void:
	if not _prelude():
		_fail("prelude_failed")
		return
	var pck := _export_pack("pack", PRESET_EMBED, "cli.pck")
	var files := _files_in(_out_dir("pack"))
	var info := _parse_pck(pck)
	var data_only: bool = files.size() == 1 and _file_size(pck) > 0 and _file_size(pck) < 1048576
	var f := PackedStringArray()
	f.append("cli_pack")
	f.append("magic=%s" % _head4(pck))
	f.append("files=%d" % files.size())
	f.append("binary=%d" % _files_matching(_out_dir("pack"), ".x86_64"))
	f.append("data_only=%s" % str(data_only).to_lower())
	f.append("hdr_ok=%s" % str(info["ok"]))
	f.append("pbin=%s" % ("yes" if info["ok"] and info["entries"].has(PBIN) else "no"))
	f.append("nondata=%s" % ("absent" if not (_contains_bytes(pck, "extra.txt") if info["ok"] else false) else "present"))
	f.append("entries=%d" % info["names"].size())
	f.append("bytes=%d" % _file_size(pck))
	var bad := ""
	if not _export_ok(pck, "pack"):
		bad = "export_failed"
	elif not info["ok"]:
		bad = "parse_" + str(info["why"])
	elif not data_only or _files_matching(_out_dir("pack"), ".x86_64") != 0:
		bad = "container_census"
	elif not info["entries"].has(PBIN):
		bad = "project_binary_missing"
	elif _contains_bytes(pck, "extra.txt"):
		bad = "nondata_exported"
	_verdict(f, bad)


# arm=zip: the same --export-pack run with a .zip path writes a ZIP container
# (savezip) instead of a PCK (savepack) — one CLI flag, two formats, neither
# reachable from the preset path. Coverage: every name in the PCK entry table
# must appear in the ZIP bytes.
func _arm_zip() -> void:
	if not _prelude():
		_fail("prelude_failed")
		return
	var pck := _export_pack("zip_pck", PRESET_EMBED, "cli.pck")
	var zip_path := _export_pack("zip_zip", PRESET_EMBED, "cli.zip")
	var info := _parse_pck(pck)
	var covered := 0
	var total := 0
	if info["ok"]:
		for n in info["names"]:
			total += 1
			if _contains_bytes(zip_path, n):
				covered += 1
	var zip_data_only: bool = _files_in(_out_dir("zip_zip")).size() == 1 and _file_size(zip_path) > 0 and _file_size(zip_path) < 1048576
	var f := PackedStringArray()
	f.append("zip_fmt")
	f.append("magic=%s" % _head4(zip_path))
	f.append("files=%d" % _files_in(_out_dir("zip_zip")).size())
	f.append("binary=%d" % _files_matching(_out_dir("zip_zip"), ".x86_64"))
	f.append("data_only=%s" % str(zip_data_only).to_lower())
	f.append("pck_magic=%s" % _head4(pck))
	f.append("names_covered=%d/%d" % [covered, total])
	f.append("pbin=%s" % ("yes" if _contains_bytes(zip_path, PBIN) else "no"))
	f.append("zip_bytes=%d" % _file_size(zip_path))
	var bad := ""
	if not _export_ok(zip_path, "zip_zip") or not _export_ok(pck, "zip_pck"):
		bad = "export_failed"
	elif _head4(zip_path) != MAGIC_ZIP:
		bad = "zip_magic"
	elif _head4(pck) != MAGIC_PCK:
		bad = "pck_magic"
	elif not zip_data_only or _files_matching(_out_dir("zip_zip"), ".x86_64") != 0:
		bad = "container_census"
	elif not info["ok"] or total == 0 or covered != total:
		bad = "zip_content_coverage"
	_verdict(f, bad)


# arm=ext: the same OUTPUT EXTENSION (.pck) through both paths. --export-release
# obeys the preset's embed_pck option and ignores the extension (ELF binary
# bytes under a .pck name, with a pack trailer at EOF); --export-pack obeys the
# extension (GDPC at offset 0, data only).
func _arm_ext() -> void:
	if not _prelude():
		_fail("prelude_failed")
		return
	var release := _export_release("ext_release", PRESET_EMBED, "release.pck")
	var cli := _export_pack("ext_cli", PRESET_EMBED, "release.pck")
	var rel_magic := _head4(release)
	var cli_magic := _head4(cli)
	var trailer := _embedded_payload(release)
	var f := PackedStringArray()
	f.append("ext_ignored")
	f.append("ext=%s" % release.get_extension())
	f.append("release_magic=%s" % rel_magic)
	f.append("cli_magic=%s" % cli_magic)
	f.append("release_trailer=%s" % str(trailer["ok"]).to_lower())
	f.append("release_bytes=%d" % _file_size(release))
	f.append("cli_bytes=%d" % _file_size(cli))
	var bad := ""
	if not _export_ok(release, "ext_release") or not _export_ok(cli, "ext_cli"):
		bad = "export_failed"
	elif rel_magic != MAGIC_ELF:
		bad = "release_not_binary"
	elif cli_magic != MAGIC_PCK:
		bad = "cli_not_pck"
	elif not trailer["ok"]:
		bad = "release_trailer_missing"
	elif _files_in(_out_dir("ext_release")).size() != 1 or _files_in(_out_dir("ext_cli")).size() != 1:
		bad = "container_census"
	_verdict(f, bad)


# arm=ident: --export-release with embed_pck=false writes binary + sidecar;
# that sidecar is byte-identical to the --export-pack artifact exported through
# a DIFFERENT preset (embed_pck=true) — the container option never reaches the
# project-data payload.
func _arm_ident() -> void:
	if not _prelude():
		_fail("prelude_failed")
		return
	var bin := _export_release("ident_stock", PRESET_STOCK, "stock.x86_64")
	var sidecar := _out_dir("ident_stock").path_join("stock.pck")
	var cli := _export_pack("ident_cli", PRESET_EMBED, "cli.pck")
	var same := FileAccess.file_exists(sidecar) and FileAccess.file_exists(cli) and _sha(sidecar) == _sha(cli)
	var f := PackedStringArray()
	f.append("sidecar_identity")
	f.append("sha256_equal=%s" % str(same).to_lower())
	f.append("files=%d" % _files_in(_out_dir("ident_stock")).size())
	f.append("sidecar=%d" % _files_matching(_out_dir("ident_stock"), ".pck"))
	f.append("cli_files=%d" % _files_in(_out_dir("ident_cli")).size())
	f.append("bin_gt_1m=%s" % str(_file_size(bin) > 1048576).to_lower())
	f.append("sidecar_bytes=%d" % _file_size(sidecar))
	f.append("cli_bytes=%d" % _file_size(cli))
	var bad := ""
	if not _export_ok(bin, "ident_stock") or not _export_ok(cli, "ident_cli"):
		bad = "export_failed"
	elif not same:
		bad = "payload_diverged"
	elif _files_in(_out_dir("ident_stock")).size() != 2 or _files_matching(_out_dir("ident_stock"), ".pck") != 1:
		bad = "sidecar_census"
	elif _files_in(_out_dir("ident_cli")).size() != 1:
		bad = "cli_census"
	_verdict(f, bad)


# arm=embed: the payload INSIDE the embedded binary vs the standalone pack.
# Same entry table, same per-entry sizes and directory MD5s, byte-identical
# data region — while the container framing differs (file_base/dir_off shifted,
# 4 B pad + 12 B trailer). Framing difference is asserted, not assumed: a
# future engine that made them byte-identical would fail this row loudly.
func _arm_embed() -> void:
	if not _prelude():
		_fail("prelude_failed")
		return
	var bin := _export_release("embed_bin", PRESET_EMBED, "embed.x86_64")
	var cli := _export_pack("embed_cli", PRESET_EMBED, "cli.pck")
	var trailer := _embedded_payload(bin)
	var extracted := _arm_dir().path_join("extracted_embedded.pck")
	var f := PackedStringArray()
	var bad := ""
	if not _export_ok(bin, "embed_bin") or not _export_ok(cli, "embed_cli"):
		_fail("export_failed")
		return
	if not trailer["ok"]:
		_fail("embedded_trailer_missing")
		return
	if not _copy_region(bin, trailer["start"], trailer["size"], extracted):
		_fail("embedded_extract_failed")
		return
	var a := _parse_pck(extracted)
	var b := _parse_pck(cli)
	if not a["ok"] or not b["ok"]:
		_fail("parse_failed:%s:%s" % [str(a["why"]), str(b["why"])])
		return
	var names_equal: bool = a["names"] == b["names"]
	var entry_equal: bool = names_equal
	if names_equal:
		for n in a["names"]:
			var ea: Dictionary = a["entries"][n]
			var eb: Dictionary = b["entries"][n]
			if ea["size"] != eb["size"] or ea["md5"] != eb["md5"]:
				entry_equal = false
	var data_equal := false
	if entry_equal:
		var ra := _region(extracted, a["file_base"], a["dir_off"])
		var rb := _region(cli, b["file_base"], b["dir_off"])
		data_equal = ra == rb and ra.size() > 0
	var framing_differs: bool = (a["file_base"] != b["file_base"]) or (a["dir_off"] != b["dir_off"]) or (_file_size(extracted) != _file_size(cli))
	f.append("payload_identity")
	f.append("entries_equal=%s" % str(names_equal).to_lower())
	f.append("entry_bytes_equal=%s" % str(entry_equal).to_lower())
	f.append("data_equal=%s" % str(data_equal).to_lower())
	f.append("framing=%s" % ("differs" if framing_differs else "same"))
	f.append("trailer=%s" % str(trailer["ok"]).to_lower())
	f.append("entries=%d" % a["names"].size())
	f.append("payload_bytes=%d" % trailer["size"])
	f.append("cli_bytes=%d" % _file_size(cli))
	f.append("file_base=%d/%d" % [a["file_base"], b["file_base"]])
	if not names_equal:
		bad = "entry_table"
	elif not entry_equal:
		bad = "entry_payload"
	elif not data_equal:
		bad = "data_region"
	elif not framing_differs:
		bad = "framing_not_distinct"
	_verdict(f, bad)
