extends SceneTree
# export_div_s04 — r103 C1: PCK extended-header census via struct (seat E4).
#
# Scenario: pack the child project with the nested CLI exporter, then census
# the PCK *extended header* — everything past magic+version: flags, file_base,
# table_ofs, the zero pad up to the data region, and the directory table —
# by decoding raw bytes with PackedByteArray.decode_u32/decode_u64. No engine
# pack API is consulted and no external tool is trusted: the census is the
# fixture's own read of the bytes, and the two md5 passes plus the offset
# alignment/overlap checks are what make the header field meanings falsifiable.
#
#   arm=pck  (row export_div_s04_pck_header)
#     nested `--export-pack PckOnly` -> <vdir>/out/plain.pck (standalone pack)
#     header census + table census (7 entries). Each entry's stored md5[16] is
#     re-derived in-engine over the blob at file_base+ofs — and a second time
#     over the blob at the *bare* ofs, where the measured match count is 0/7.
#     That 0/7 is the evidence that entry offsets are file_base-relative
#     (flags bit1), not absolute: a fixture parsing offsets absolutely would
#     fail 0/7 here. Blob marks: main.gdc starts "GDSC" at ofs 0, project.binary
#     starts "ECFG" at ofs 1088 (absolute 1200) — name->bytes round trip.
#
#   arm=embed  (row export_div_s04_embed_header)
#     nested `--export-release Embed` -> <vdir>/out/embed.x86_64, then the
#     embedded pack is located from the trailing [u64 size][u32 "GDPC"] pair
#     and censused with the same code path. file_base must satisfy
#     _expected_file_base(pck_start) — with a *computed* pck_start, so a second
#     point of the same alignment law is checked instead of a pinned literal.
#
#   arm=encdir  (row export_div_s04_encdir_flag)
#     nested `--export-pack EncDir` twice: keyless, then with
#     GODOT_SCRIPT_ENCRYPTION_KEY=<64 hex> in the nested environment.
#     Measured divergence: flags bit0 (dir-encrypted) reads 3 in BOTH packs,
#     but only the keyed one has records that are not plaintext. The keyless
#     pack's records parse as a normal 7-entry table whose md5s all verify, so
#     trusting the flag alone is wrong for it; the keyed records region carries
#     no path bytes at all, so a plaintext-table reader fails on it. The count
#     u32 at table_ofs stays readable (7) in both, measured.
#
# Measured laws, hand probes 2026-10-18 on godot 4.7.2.stable.arch_linux.ed1daf0bf
# (load 1.8-10.9; exports 1.7-2.1 s each):
#   header, 100 bytes = 0x64:
#     0x00 u32 magic "GDPC"          0x04 u32 pack_format_version = 4
#     0x08 u32 major 4, 0x0C u32 minor 7, 0x10 u32 patch 2
#     0x14 u32 pack_flags (bit0 dir-encrypted, bit1 rel-filebase; 2 plain)
#     0x18 u64 file_base = data-region start, relative to the pack start
#     0x20 u64 table_ofs = directory offset, relative to the pack start
#     0x28..0x64 zero pad (measured all zero)
#   file_base == 100 + ((16 - ((pck_start + 100) % 16)) % 16): the data region
#     is 16-byte aligned in the *containing file*, so the standalone pack
#     (pck_start 0) reads file_base 112 and the embedded pack (pck_start
#     mod 16 == 8) reads 104 — both computed by that one expression.
#   table: u32 count, then records [u32 name_len (NUL-padded to a 4-byte
#     length) | name | u64 ofs | u64 size | md5[16] | u32 flags], 4+nl+36
#     bytes each; ofs relative to file_base; every (file_base+ofs) 16-aligned;
#     blobs land before table_ofs, non-overlapping; table ends at pack size
#     for a standalone pack (tail 0) and 4 bytes short of it embedded.
#   embedded trailer: last 12 bytes = u64 pck_size + u32 "GDPC"; pack starts
#     at file_size-12-pck_size (measured 73519416 of 73521368).
#   the entry set is a stable 7-row census on a cold export (main.gd,
#     main.tscn child): project.binary, main.gdc, main.gd.remap,
#     main.tscn.remap, .godot/uid_cache.bin,
#     .godot/global_script_class_cache.cfg, .godot/exported/<uid>/export-
#     <hash>-main.scn. Pack bytes are NOT byte-stable across repeated exports
#     (sha256 differs, structure identical) — never gate on artifact sha.
#   adding [editor] script_encryption_key to the child project.godot changes
#     nothing about encryption (flags still 3, records still plaintext; the
#     key string only shows up inside project.binary, +108 bytes), so the
#     keyed half below uses the environment channel, which does encrypt.
#
# Scratch: <root>/div_s04/{proj,out,logs}, <root> = first writable of
# $EXPORT_DIV_ROOT, $EXPORT_LAUNCH_ROOT, <engine user-data dir>, $TMPDIR, then
# /tmp (4096-byte write+readback probe). User-data is preferred: the export
# runs under unshare with a 64 MB tmpfs /tmp (packer temp mitigation), and the
# ~73 MB embed arm must not land under that mount. Nested engine output is
# redirected to logs; host paths appear only in EXPORT_DIV_DIAG lines and in
# the trailing unpinned `proj=` field.
#
# Battery launch shape: godot --headless --path <scratch proj> --script res://export_div_s04.gd -- --arm=<arm>

const VARIANT := "div_s04"
const PRESET_PCK := "PckOnly"
const PRESET_EMBED := "Embed"
const PRESET_ENC := "EncDir"
const TEMPLATE := "linux_release.x86_64"
const TIMEOUT_PATH := "/usr/bin/timeout"
const EXPORT_BOUND := 90
const KEY_HEX := "abababababababababababababababababababababababababababababababab"
const MAGIC_U32 := 0x43504447
const HDR_PAD_START := 0x28
const HDR_END := 0x64
const MARK_SCN := "GDSC"
const MARK_ECFG := "ECFG"
const ENC_PLAIN_MARK := "project.binary"
const ENC_PLAIN_MARK2 := "uid_cache"
const CLASSES_EXPECTED := ".godot/exported/*-main.scn,.godot/global_script_class_cache.cfg,.godot/uid_cache.bin,main.gd.remap,main.gdc,main.tscn.remap,project.binary"

const CHILD_PROJECT := "config_version=5\n\n[application]\nconfig/name=\"ExportDivS04\"\nrun/main_scene=\"res://main.tscn\"\nconfig/features=PackedStringArray(\"4.7\")\n\n[display]\nwindow/size/viewport_width=320\nwindow/size/viewport_height=180\n"
const CHILD_PRESETS := "[preset.0]\nname=\"PckOnly\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\ninclude_filter=\"\"\nexclude_filter=\"\"\nexport_path=\"\"\nencryption_include_filters=\"\"\nencryption_exclude_filters=\"\"\nencrypt_pck=false\nencrypt_directory=false\n\n[preset.0.options]\nbinary_format/architecture=\"x86_64\"\nbinary_format/embed_pck=false\n\n[preset.1]\nname=\"Embed\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\ninclude_filter=\"\"\nexclude_filter=\"\"\nexport_path=\"\"\nencryption_include_filters=\"\"\nencryption_exclude_filters=\"\"\nencrypt_pck=false\nencrypt_directory=false\n\n[preset.1.options]\nbinary_format/architecture=\"x86_64\"\nbinary_format/embed_pck=true\n\n[preset.2]\nname=\"EncDir\"\nplatform=\"Linux/X11\"\nrunnable=true\nadvanced_options=false\ndedicated_server=false\ncustom_features=\"\"\nexport_filter=\"all_resources\"\ninclude_filter=\"\"\nexclude_filter=\"\"\nexport_path=\"\"\nencryption_include_filters=\"\"\nencryption_exclude_filters=\"\"\nencrypt_pck=true\nencrypt_directory=true\n\n[preset.2.options]\nbinary_format/architecture=\"x86_64\"\nbinary_format/embed_pck=false\n"
const CHILD_MAIN := "extends Node\n\nfunc _ready() -> void:\n\tprint(\"CHILD_MAIN_READY\")\n\tget_tree().quit(0)\n"
const CHILD_TSCN := "[gd_scene load_steps=2 format=3]\n\n[ext_resource type=\"Script\" path=\"res://main.gd\" id=\"1\"]\n\n[node name=\"Main\" type=\"Node\"]\nscript = ExtResource(\"1\")\n"

var arm := ""
var _root := ""
var _unshare := false


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			arm = a.substr(6)
	if arm == "":
		arm = "pck"
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
		"pck":
			_arm_pck()
		"embed":
			_arm_embed()
		"encdir":
			_arm_encdir()
		_:
			_fail("unknown_arm")


# ------------------------------------------------------------------ receipts

func _fail(reason: String) -> void:
	print("FAIL export_div s04 arm=%s reason=%s" % [arm, reason])
	quit(1)


func _verdict(fields: PackedStringArray, bad: String) -> void:
	if bad == "":
		print("PASS export_div s04 arm=%s %s" % [arm, " ".join(fields)])
		quit(0)
	else:
		print("FAIL export_div s04 arm=%s reason=%s %s" % [arm, bad, " ".join(fields)])
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
	candidates.append(OS.get_user_data_dir().path_join("export_div_s04"))
	if OS.get_environment("TMPDIR") != "":
		candidates.append(OS.get_environment("TMPDIR").path_join("export_div_s04"))
	candidates.append("/tmp/export_div_s04")
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


func _vdir() -> String:
	return _root.path_join(VARIANT)


func _out_dir() -> String:
	return _vdir().path_join("out")


func _log_path(name: String) -> String:
	return _vdir().path_join("logs").path_join(name + ".log")


func _mkdir(path: String) -> bool:
	if DirAccess.dir_exists_absolute(path):
		return true
	var err := DirAccess.make_dir_recursive_absolute(path)
	if err != OK:
		_fail("mkdir_failed:%s:%d" % [path, err])
		return false
	return true


func _wipe_dir(dir: String) -> void:
	if not DirAccess.dir_exists_absolute(dir):
		return
	for d in DirAccess.get_directories_at(dir):
		_wipe_dir(dir.path_join(d))
	for f in DirAccess.get_files_at(dir):
		DirAccess.remove_absolute(dir.path_join(f))
	DirAccess.remove_absolute(dir)


func _write_text(path: String, text: String) -> bool:
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		_fail("write_failed:" + path)
		return false
	f.store_string(text)
	f.close()
	return true


func _run_logged(body: String, log_path: String, isolate := false) -> int:
	_mkdir(log_path.get_base_dir())
	var script := body
	if isolate and _unshare:
		# Private /tmp for the packer's fixed tmpproject.binary temp path.
		script = "mount -t tmpfs -o size=64M tmpfs /tmp || exit 97\n" + body
		script = "unshare -m --map-root-user /usr/bin/sh -c " + _q(script)
	_diag("nested", body.replace("\n", " ; "))
	return OS.execute("/usr/bin/sh", PackedStringArray(["-c", "exec > " + _q(log_path) + " 2>&1\n" + script]))


func _template_exists() -> bool:
	var v := Engine.get_version_info()
	var ver := "%d.%d.%d.%s" % [v["major"], v["minor"], v["patch"], v["status"]]
	var candidates: PackedStringArray = []
	if OS.get_environment("XDG_DATA_HOME") != "":
		candidates.append(OS.get_environment("XDG_DATA_HOME").path_join("godot/export_templates").path_join(ver).path_join(TEMPLATE))
	if OS.get_environment("HOME") != "":
		candidates.append(OS.get_environment("HOME").path_join(".local/share/godot/export_templates").path_join(ver).path_join(TEMPLATE))
	candidates.append("/usr/local/share/godot/export_templates/%s/%s" % [ver, TEMPLATE])
	candidates.append("/usr/share/godot/export_templates/%s/%s" % [ver, TEMPLATE])
	for c in candidates:
		if FileAccess.file_exists(c):
			return true
	return false


# -------------------------------------------------------------------- child

func _build_child_project() -> bool:
	var proj := _vdir().path_join("proj")
	if not _mkdir(proj) or not _mkdir(_out_dir()) or not _mkdir(_vdir().path_join("logs")):
		return false
	_write_text(proj.path_join("project.godot"), CHILD_PROJECT)
	_write_text(proj.path_join("export_presets.cfg"), CHILD_PRESETS)
	_write_text(proj.path_join("main.gd"), CHILD_MAIN)
	_write_text(proj.path_join("main.tscn"), CHILD_TSCN)
	return true


func _export(preset: String, out_path: String, mode: String, env_prefix: String, log_name: String) -> int:
	var proj := _vdir().path_join("proj")
	if FileAccess.file_exists(out_path):
		DirAccess.remove_absolute(out_path)
	var bound := ""
	if FileAccess.file_exists(TIMEOUT_PATH):
		bound = TIMEOUT_PATH + " -k 1 %d " % EXPORT_BOUND
	var body := "cd " + _q(proj) + "\n" + env_prefix + bound + _q(_godot()) + " --headless --path " + _q(proj) + " " + mode + " " + _q(preset) + " " + _q(out_path)
	return _run_logged(body, _log_path(log_name), true)


# ------------------------------------------------------------------ pck read

func _read_range(path: String, begin: int, length: int) -> PackedByteArray:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return PackedByteArray()
	var total := f.get_length()
	if length < 0:
		length = total - begin
	if begin < 0 or length < 0 or begin + length > total:
		f.close()
		return PackedByteArray()
	f.seek(begin)
	var b := f.get_buffer(length)
	f.close()
	return b


func _md5_of(blob: PackedByteArray) -> PackedByteArray:
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_MD5)
	ctx.update(blob)
	return ctx.finish()


func _expected_file_base(pck_start: int) -> int:
	return HDR_END + ((16 - ((pck_start + HDR_END) % 16)) % 16)


func _ascii(p: PackedByteArray, from: int, to: int) -> String:
	if from < 0 or to > p.size() or from > to:
		return ""
	return p.slice(from, to).get_string_from_ascii()


# Table names are NUL-padded to a 4-byte length, and a String round trip of
# those padding NULs makes the engine print a unicode parse warning per name,
# so the cut happens on the bytes.
func _name_at(p: PackedByteArray, from: int, nl: int) -> String:
	var cut := from + nl
	for j in range(from, from + nl):
		if p[j] == 0:
			cut = j
			break
	return _ascii(p, from, cut)


func _class_of(name: String) -> String:
	if name.begins_with(".godot/exported/") and name.ends_with("-main.scn"):
		return ".godot/exported/*-main.scn"
	return name


func _classes_of(names: PackedStringArray) -> String:
	var tokens := PackedStringArray()
	for n in names:
		tokens.append(_class_of(n))
	tokens.sort()
	return ",".join(tokens)


# Raw byte search: the records region of a pack carries NUL padding and, when
# the directory is encrypted, arbitrary bytes, so it never round-trips through
# a String conversion without engine warnings.
func _has_marker(hay: PackedByteArray, needle: String) -> bool:
	var nb := needle.to_ascii_buffer()
	var hn := hay.size()
	var nn := nb.size()
	if nn == 0 or hn < nn:
		return false
	for i in range(hn - nn + 1):
		var hit := true
		for j in range(nn):
			if hay[i + j] != nb[j]:
				hit = false
				break
		if hit:
			return true
	return false


# ---------------------------------------------------------------- the census

# Returns {"bad": String, "fields": [...], ...census keys}. pck_start is the
# pack's offset inside its containing file (0 for a standalone pack); every
# alignment claim is checked in that file's coordinates.
func _census(p: PackedByteArray, pck_start: int, want_entries: bool) -> Dictionary:
	var out := {"bad": "", "fields": PackedStringArray()}
	var n := p.size()
	out["bytes"] = n
	if n < HDR_END or _ascii(p, 0, 4) != "GDPC":
		out["bad"] = "pck_magic_missing"
		return out
	out["version"] = p.decode_u32(4)
	out["triple"] = "%d.%d.%d" % [p.decode_u32(8), p.decode_u32(12), p.decode_u32(16)]
	out["flags"] = p.decode_u32(0x14)
	var file_base := p.decode_u64(0x18)
	var table_ofs := p.decode_u64(0x20)
	out["file_base"] = file_base
	out["law"] = _expected_file_base(pck_start)
	out["table_ofs"] = table_ofs
	var pad_zero := true
	for o in range(HDR_PAD_START, HDR_END, 4):
		if p.decode_u32(o) != 0:
			pad_zero = false
	out["pad_zero"] = pad_zero
	if file_base < HDR_END or file_base % 4 != 0:
		out["bad"] = "file_base_out_of_range:%d" % file_base
		return out
	if table_ofs < file_base + 4 or table_ofs + 4 > n:
		out["bad"] = "table_ofs_out_of_range:%d" % table_ofs
		return out
	var count := p.decode_u32(table_ofs)
	out["count"] = count
	var records := p.slice(table_ofs + 4, n)
	out["records_bytes"] = records.size()
	out["records"] = records
	if not want_entries:
		return out
	var names := PackedStringArray()
	var rel_ok := 0
	var abs_ok := 0
	var align_ok := 0
	var flag_ok := 0
	var pos := table_ofs + 4
	var in_bounds := true
	var ranges := PackedInt32Array()
	var marks := PackedStringArray()
	for i in range(count):
		if pos + 4 > n:
			in_bounds = false
			break
		var nl := p.decode_u32(pos)
		pos += 4
		if nl == 0 or nl % 4 != 0 or pos + nl > n:
			in_bounds = false
			break
		var name := _name_at(p, pos, nl)
		pos += nl
		if pos + 36 > n:
			in_bounds = false
			break
		var ofs := p.decode_u64(pos)
		var size := p.decode_u64(pos + 8)
		var digest := p.slice(pos + 16, pos + 32)
		var eflags := p.decode_u32(pos + 32)
		pos += 36
		names.append(name)
		if eflags == 0:
			flag_ok += 1
		var lo := file_base + ofs
		if lo < file_base or ofs + size > n - file_base or lo + size > table_ofs:
			in_bounds = false
			break
		var blob := p.slice(lo, lo + size)
		if _md5_of(blob) == digest:
			rel_ok += 1
		if _md5_of(p.slice(ofs, ofs + size)) == digest:
			abs_ok += 1
		if (pck_start + lo) % 16 == 0:
			align_ok += 1
		if lo == file_base and size >= 4 and _ascii(p, lo, lo + 4) == MARK_SCN:
			marks.append(MARK_SCN)
		if name == "project.binary" and size >= 4 and _ascii(p, lo, lo + 4) == MARK_ECFG:
			marks.append(MARK_ECFG)
		ranges.append(lo)
		ranges.append(size)
	out["names"] = names
	out["classes"] = _classes_of(names)
	out["rel_ok"] = rel_ok
	out["abs_ok"] = abs_ok
	out["align_ok"] = align_ok
	out["flag_ok"] = flag_ok
	out["in_bounds"] = in_bounds
	# The table lists entries by path, not by offset, so overlap has to be a
	# pairwise range test rather than a sequential cursor.
	var overlap := false
	for a in range(0, count):
		for b in range(a + 1, count):
			if a * 2 + 1 >= ranges.size() or b * 2 + 1 >= ranges.size():
				break
			if ranges[a * 2] < ranges[b * 2] + ranges[b * 2 + 1] and ranges[b * 2] < ranges[a * 2] + ranges[a * 2 + 1]:
				overlap = true
	out["overlap"] = overlap
	out["marks"] = ",".join(marks)
	out["table_end"] = pos
	out["tail"] = n - pos
	out["table_aligned8"] = (pck_start + pos) % 8 == 0
	return out


func _common_fields(c: Dictionary) -> PackedStringArray:
	var f := PackedStringArray()
	f.append("bytes=%d" % c.get("bytes", 0))
	f.append("ver=%d" % c.get("version", -1))
	f.append("triple=%s" % c.get("triple", "?"))
	f.append("flags=%d" % c.get("flags", -1))
	f.append("file_base=%d" % c.get("file_base", -1))
	f.append("law=%d" % c.get("law", -1))
	f.append("table_ofs=%d" % c.get("table_ofs", -1))
	f.append("count=%d" % c.get("count", -1))
	f.append("pad_zero=%s" % str(c.get("pad_zero", false)))
	return f


func _common_bad(c: Dictionary) -> String:
	if c["bad"] != "":
		return c["bad"]
	var n: int = c["count"]
	if not c["pad_zero"]:
		return "header_pad_nonzero"
	if c["file_base"] != c["law"]:
		return "file_base_not_alignment_law:%d" % c["file_base"]
	if n != 7:
		return "count_not_7:%d" % n
	if not c["in_bounds"]:
		return "entry_out_of_bounds"
	if c["overlap"]:
		return "entry_blobs_overlap"
	if c["rel_ok"] != n:
		return "md5_relative_offsets_ok_%d_of_%d" % [c["rel_ok"], n]
	if c["abs_ok"] != 0:
		return "md5_absolute_offsets_ok_%d" % c["abs_ok"]
	if c["align_ok"] != n:
		return "blob_alignment_ok_%d_of_%d" % [c["align_ok"], n]
	if c["flag_ok"] != n:
		return "entry_flags_nonzero_%d_of_%d" % [c["flag_ok"], n]
	if c["classes"] != CLASSES_EXPECTED:
		return "entry_class_set_mismatch"
	if not c["table_aligned8"]:
		return "table_end_not_8_aligned"
	return ""


# ---------------------------------------------------------------------- arms

func _arm_pck() -> void:
	_wipe_dir(_vdir())
	if not _build_child_project():
		return
	var pck_path := _out_dir().path_join("plain.pck")
	var code := _export(PRESET_PCK, pck_path, "--export-pack", "", "export_pck")
	if code != 0 or not FileAccess.file_exists(pck_path):
		_fail("export_failed:%d" % code)
		return
	_diag("artifact", pck_path)
	var p := _read_range(pck_path, 0, -1)
	_diag("artifact_bytes", p.size())
	var c := _census(p, 0, true)
	_diag("classes", c.get("classes", "<none>"))
	_diag("artifact_sha_note", "not gated: packs are byte-identical only for identical project state (same arm twice: identical; warm-vs-cold probe: not)")
	var fields := _common_fields(c)
	fields.append("md5_rel=%d" % c.get("rel_ok", -1))
	fields.append("md5_abs=%d" % c.get("abs_ok", -1))
	fields.append("align16=%d" % c.get("align_ok", -1))
	fields.append("tail=%d" % c.get("tail", -1))
	fields.append("marks=%s" % c.get("marks", ""))
	fields.append("proj=" + _vdir().path_join("proj"))
	var bad := _common_bad(c)
	if bad == "" and c["flags"] != 2:
		bad = "flags_not_2:%d" % c["flags"]
	if bad == "" and c["tail"] != 0:
		bad = "standalone_tail_not_0:%d" % c["tail"]
	if bad == "" and c["marks"] != "%s,%s" % [MARK_SCN, MARK_ECFG]:
		bad = "blob_marks_missing:[%s]" % c["marks"]
	_verdict(fields, bad)


func _arm_embed() -> void:
	_wipe_dir(_vdir())
	if not _build_child_project():
		return
	if not _template_exists():
		_fail("template_binary_not_found")
		return
	var exe := _out_dir().path_join("embed.x86_64")
	var code := _export(PRESET_EMBED, exe, "--export-release", "", "export_embed")
	if code != 0 or not FileAccess.file_exists(exe):
		_fail("export_failed:%d" % code)
		return
	_diag("artifact", exe)
	var f := FileAccess.open(exe, FileAccess.READ)
	if f == null:
		_fail("artifact_unreadable")
		return
	var total := f.get_length()
	f.seek(total - 12)
	var tsize := f.get_64()
	var tmagic := f.get_32()
	f.close()
	var fields := PackedStringArray()
	if total < 32 or tmagic != MAGIC_U32 or tsize <= HDR_END or tsize > total - 12:
		fields.append("exe_bytes=%d" % total)
		fields.append("trailer_size=%d" % tsize)
		fields.append("trailer_magic=%08x" % tmagic)
		_verdict(fields, "embedded_trailer_invalid")
		return
	var pck_start := total - 12 - tsize
	_diag("pck_start", pck_start)
	var p := _read_range(exe, pck_start, tsize)
	var c := _census(p, pck_start, true)
	_diag("classes", c.get("classes", "<none>"))
	fields.append("trailer_size=%d" % tsize)
	fields.append("pck_start_mod16=%d" % (pck_start % 16))
	for x in _common_fields(c):
		fields.append(x)
	fields.append("md5_rel=%d" % c.get("rel_ok", -1))
	fields.append("md5_abs=%d" % c.get("abs_ok", -1))
	fields.append("align16=%d" % c.get("align_ok", -1))
	fields.append("tail=%d" % c.get("tail", -1))
	fields.append("marks=%s" % c.get("marks", ""))
	# exe_bytes is the host template's size, so it goes after every structural
	# field: a CASES expected substring must be able to stop before it.
	fields.append("exe_bytes=%d" % total)
	fields.append("proj=" + _vdir().path_join("proj"))
	var bad := _common_bad(c)
	if bad == "" and c["flags"] != 2:
		bad = "flags_not_2:%d" % c["flags"]
	if bad == "" and c["bytes"] != tsize:
		bad = "pck_bytes_not_trailer_size:%d" % c["bytes"]
	if bad == "" and c["tail"] >= 8:
		bad = "embedded_tail_ge_8:%d" % c["tail"]
	if bad == "" and c["file_base"] >= HDR_END + 16:
		bad = "embedded_file_base_past_one_pad:%d" % c["file_base"]
	if bad == "" and c["marks"] != "%s,%s" % [MARK_SCN, MARK_ECFG]:
		bad = "blob_marks_missing:[%s]" % c["marks"]
	_verdict(fields, bad)


func _arm_encdir() -> void:
	_wipe_dir(_vdir())
	if not _build_child_project():
		return
	var keyless := _out_dir().path_join("enc_keyless.pck")
	var code := _export(PRESET_ENC, keyless, "--export-pack", "", "export_enc_keyless")
	if code != 0 or not FileAccess.file_exists(keyless):
		_fail("keyless_export_failed:%d" % code)
		return
	var keyed := _out_dir().path_join("enc_keyed.pck")
	code = _export(PRESET_ENC, keyed, "--export-pack", "GODOT_SCRIPT_ENCRYPTION_KEY=" + KEY_HEX + " ", "export_enc_keyed")
	if code != 0 or not FileAccess.file_exists(keyed):
		_fail("keyed_export_failed:%d" % code)
		return
	_diag("keyless_artifact", keyless)
	_diag("keyed_artifact", keyed)
	var pk := _read_range(keyless, 0, -1)
	var pd := _read_range(keyed, 0, -1)
	var ck := _census(pk, 0, true)
	var cd := _census(pd, 0, false)
	_diag("keyless_classes", ck.get("classes", "<none>"))
	var keyless_plain: bool = _has_marker(ck.get("records", PackedByteArray()), ENC_PLAIN_MARK)
	var keyed_plain: bool = _has_marker(cd.get("records", PackedByteArray()), ENC_PLAIN_MARK)
	var keyed_uid: bool = _has_marker(cd.get("records", PackedByteArray()), ENC_PLAIN_MARK2)
	_diag("keyless_records_bytes", ck.get("records_bytes", -1))
	_diag("keyed_records_bytes", cd.get("records_bytes", -1))
	var fields := PackedStringArray()
	fields.append("keyless_bytes=%d" % ck.get("bytes", -1))
	fields.append("keyless_flags=%d" % ck.get("flags", -1))
	fields.append("keyless_count=%d" % ck.get("count", -1))
	fields.append("keyless_md5_rel=%d" % ck.get("rel_ok", -1))
	fields.append("keyless_records=%s" % ("plaintext" if keyless_plain else "ciphertext"))
	fields.append("keyed_bytes=%d" % cd.get("bytes", -1))
	fields.append("keyed_flags=%d" % cd.get("flags", -1))
	fields.append("keyed_count=%d" % cd.get("count", -1))
	fields.append("keyed_records=%s" % ("plaintext" if keyed_plain else "ciphertext"))
	fields.append("keyed_uid_mark=%s" % str(keyed_uid))
	fields.append("proj=" + _vdir().path_join("proj"))
	var bad := _common_bad(ck)
	if bad == "" and ck["flags"] != 3:
		bad = "keyless_flags_not_3:%d" % ck["flags"]
	if bad == "" and not keyless_plain:
		bad = "keyless_records_not_plaintext"
	if bad == "" and cd["bad"] != "":
		bad = "keyed_header:" + cd["bad"]
	if bad == "" and cd["flags"] != 3:
		bad = "keyed_flags_not_3:%d" % cd["flags"]
	if bad == "" and cd["count"] != ck["count"]:
		bad = "keyed_count_differs:%d" % cd["count"]
	if bad == "" and cd["file_base"] != cd["law"]:
		bad = "keyed_file_base_not_alignment_law:%d" % cd["file_base"]
	if bad == "" and keyed_plain:
		bad = "keyed_records_still_plaintext"
	if bad == "" and keyed_uid:
		bad = "keyed_records_carry_uid_path"
	if bad == "" and cd["records_bytes"] == ck["records_bytes"]:
		bad = "keyed_records_bytes_unchanged:%d" % cd["records_bytes"]
	_verdict(fields, bad)
