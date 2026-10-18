extends SceneTree
## export_prod_s02.gd — r101 export_prod lattice, scenario 02.
## Zip export of a production-shaped project, then a raw central-directory
## census (entry names + count) and an integrity pass.
##
## Usage (fixture is self-contained; it generates its own project):
##   godot --headless --path <scratch> --script res://export_prod_s02.gd -- [flags]
## Flags:
##   --root=<abs dir>  scratch root                 (default /var/tmp/r101-export-prod-s02)
##   --run-id=<token>  suffix for the per-run dir   (default pid+ticks)
##   --zip=<abs path>  census an existing zip instead of exporting
##   --corrupt=<kind>  forge the exported zip before the census:
##                     crc|name|count|truncate|localname
##   --keep            keep the scratch project and zip
##   --verbose         echo the child export output
##
## Exit: 0 = PASS, 2 = assertion failure, 3 = setup/IO failure.
## The scratch root defaults to /var/tmp because this host's /tmp tmpfs
## reached its quota and rejected 73 MiB template writes with EDQUOT
## (r101-E2 shard, "environment"); /var/tmp is disk-backed.

const PRESET_NAME := "Linux/X11"
const DEFAULT_ROOT := "/var/tmp/r101-export-prod-s02"

const PROJECT_GODOT := """[application]

config/name="E2ProdShape"
run/main_scene="res://scenes/main.tscn"
config/features=PackedStringArray("4.7")

[rendering]

renderer/rendering_method="gl_compatibility"
"""

const PRESET_CFG := """[preset.0]

name="Linux/X11"
platform="Linux/X11"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path=""
encryption_include_filters=""
encryption_exclude_filters=""
seed=0
encrypt_pck=false
encrypt_directory=false
script_export_mode=2

[preset.0.options]

binary_format/architecture="x86_64"
binary_format/embed_pck=false
"""

const MAIN_TSCN := """[gd_scene load_steps=3 format=3 uid="uid://e2mainscene111"]

[ext_resource type="Script" path="res://scenes/main.gd" id="1"]
[ext_resource type="Texture2D" path="res://art/icon.svg" id="2"]

[node name="Main" type="Node2D"]
script = ExtResource("1")

[node name="Sprite" type="Sprite2D" parent="."]
position = Vector2(32, 24)
texture = ExtResource("2")
"""

const MAIN_GD := """extends Node2D


func _ready() -> void:
	print("E2_PROD_MAIN_READY")
"""

const ICON_SVG := """<svg xmlns="http://www.w3.org/2000/svg" width="8" height="8"><rect width="8" height="8" fill="#3a7"/></svg>
"""

## Frozen census: measured on a byte-fresh project, single first export
## (Godot 4.7.2.stable.arch_linux.ed1daf0bf). Order is the archive order.
const EXPECTED_NAMES := [
	".godot/imported/icon.svg-2ffe2e9772a318535303737ea3c29287.ctex",
	"art/icon.svg.import",
	"scenes/main.gdc",
	".godot/exported/133200997/export-3ad5c15c4f3250da0cc7c1af1770d85f-main.scn",
	"scenes/main.gd.remap",
	"scenes/main.tscn.remap",
	".godot/global_script_class_cache.cfg",
	".godot/uid_cache.bin",
	"project.binary",
]
const EXPECTED_US := [94, 193, 177, 842, 38, 97, 8, 100, 243]
## The converted binary scene (entry 3) is byte-unstable across runs, but the
## variance is confined to one 8-byte field: across four consecutive runs,
## bytes [662, 670) differed (random-looking per-run value) and all other 834
## bytes were identical (prefix/suffix sha256 equal in all four). So entry 3
## is pinned by a mask -- sha256 of [0, 662) and [670, 842) -- plus its
## uncompressed length. The other 8 entries are pinned whole.
const UNSTABLE_INDEX := 3
const SCN_VARY_START := 662
const SCN_VARY_END := 670
const EXPECTED_SCN_PREFIX_SHA256 := "8fe707df771764ffcb43dadb1720dd329ad3e7a939e27f1fecc49a31af362c33"
const EXPECTED_SCN_SUFFIX_SHA256 := "e608aa0c800ffe8fb3c8c302ebfda2f2d7b2b0970dd7a838e979bddaae6258fb"
const EXPECTED_SHA256 := [
	"c81cb9b20236a9bdf56c853369ca60b870e84bf0887f04a122e12647fc4e06e5",
	"6e9839183c5b43b1020adfb5db76ae6c1539e67b3325db65ac0b4e7eef44d39e",
	"93f9444bc629555d6ffcb0f7445f66d10d83b0de9e2c5f40acfeecf0fdf76508",
	"",
	"6c5f29fcbf5b793053bfc5c20c6749ecd117b6709324edd5270096379cc8e35f",
	"e06953e0896a129b556ff2dc6ee7ab070f7032689d0d08ce8bba6f62ed084668",
	"f61aa7ad3097022d6a9d110ca3f73fa7bb348ec2cf9a6e7c9523574dc75f5a16",
	"7887b73201d4bbcbaf799cb20f2938f17225a39f263a8543fc5255b635b2ce8e",
	"715d968941a4f198223a8f6fefcdf16863aea03dc3efd4608894b9f5bd2945ba",
]

var _root := DEFAULT_ROOT
var _run_id := ""
var _zip_override := ""
var _corrupt := ""
var _keep := false
var _verbose := false
var _fail_reason := ""


func _crc32(data: PackedByteArray) -> int:
	var crc := 0xFFFFFFFF
	for byte in data:
		crc ^= byte
		for _bit in 8:
			crc = (crc >> 1) ^ (0xEDB88320 if (crc & 1) == 1 else 0)
	return crc ^ 0xFFFFFFFF


func _rfind_sig(raw: PackedByteArray, sig: PackedByteArray, upto: int) -> int:
	var limit: int = mini(upto, raw.size() - sig.size())
	for start in range(limit, -1, -1):
		var hit := true
		for k in sig.size():
			if raw[start + k] != sig[k]:
				hit = false
				break
		if hit:
			return start
	return -1


func _parse_args() -> void:
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--root="):
			_root = argument.trim_prefix("--root=")
		elif argument.begins_with("--run-id="):
			_run_id = argument.trim_prefix("--run-id=")
		elif argument.begins_with("--zip="):
			_zip_override = argument.trim_prefix("--zip=")
		elif argument.begins_with("--corrupt="):
			_corrupt = argument.trim_prefix("--corrupt=")
		elif argument == "--keep":
			_keep = true
		elif argument == "--verbose":
			_verbose = true


func _write(path: String, content: String) -> bool:
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		return false
	file.store_string(content)
	file.close()
	return true


func _delete_tree(path: String) -> void:
	var dir := DirAccess.open(path)
	if dir == null:
		return
	dir.list_dir_begin()
	var entry := dir.get_next()
	while entry != "":
		var full := path.path_join(entry)
		if dir.current_is_dir():
			_delete_tree(full)
		else:
			dir.remove(entry)
		entry = dir.get_next()
	dir.list_dir_end()
	DirAccess.remove_absolute(path)


func _build_project(project_dir: String, export_dir: String) -> String:
	for relative in ["scenes", "art"]:
		var made := DirAccess.make_dir_recursive_absolute(project_dir.path_join(relative))
		if made != OK and made != ERR_ALREADY_EXISTS:
			return "mkdir failed for %s (err=%d)" % [relative, made]
	var writes := {
		"project.godot": PROJECT_GODOT,
		"export_presets.cfg": PRESET_CFG,
		"scenes/main.tscn": MAIN_TSCN,
		"scenes/main.gd": MAIN_GD,
		"art/icon.svg": ICON_SVG,
	}
	for relative in writes:
		if not _write(project_dir.path_join(relative), writes[relative]):
			return "write failed for %s" % relative
	if DirAccess.make_dir_recursive_absolute(export_dir) != OK:
		return "mkdir failed for export dir %s" % export_dir
	return ""


func _export(project_dir: String, zip_path: String) -> PackedStringArray:
	var output: Array = []
	var args := PackedStringArray([
		"--headless", "--path", project_dir, "--export-pack", PRESET_NAME, zip_path,
	])
	var code := OS.execute(OS.get_executable_path(), args, output, true)
	var captured: String = output[0] if output.size() > 0 else ""
	_report("EXPORT_PROD_S02 export_command=%s %s rc=%d output_bytes=%d"
			% [OS.get_executable_path(), " ".join(args), code, captured.length()])
	if _verbose:
		for line in captured.split("\n"):
			if line.strip_edges() != "":
				_report("EXPORT_PROD_S02 child: %s" % line)
	if code != 0:
		_fail_reason = "export_failed rc=%d" % code
	elif not FileAccess.file_exists(zip_path):
		_fail_reason = "export_produced_no_zip"
	return PackedStringArray([str(code), captured])


func _forge(raw: PackedByteArray, kind: String) -> Array:
	# Returns [note, forged_bytes]; the forgery must be rejected by the census.
	var out := raw.duplicate()
	match kind:
		"crc":
			# Flip one byte of the first CD entry's stored CRC (offset 16 in CD).
			var cd := _rfind_sig(out, PackedByteArray([0x50, 0x4b, 0x01, 0x02]), out.size() - 1)
			if cd < 0:
				return ["no_central_directory", raw]
			out[cd + 16] = out[cd + 16] ^ 0x01
			return ["flipped_cd_crc_bit_of_entry_0", out]
		"count":
			# Claim one more entry than exists in the EOCD.
			var eocd := _rfind_sig(out, PackedByteArray([0x50, 0x4b, 0x05, 0x06]), out.size() - 1)
			if eocd < 0:
				return ["no_eocd", raw]
			var entries := out.decode_u16(eocd + 10)
			out.encode_u16(eocd + 8, entries + 1)
			out.encode_u16(eocd + 10, entries + 1)
			return ["eocd_entry_count_bumped", out]
		"truncate":
			# Chop the end of central directory: keep half of the CD.
			var eocd2 := _rfind_sig(out, PackedByteArray([0x50, 0x4b, 0x05, 0x06]), out.size() - 1)
			if eocd2 < 0:
				return ["no_eocd", raw]
			var cd_offset := out.decode_u32(eocd2 + 16)
			var cut := cd_offset + int((eocd2 - cd_offset) / 2)
			return ["central_directory_truncated", out.slice(0, cut)]
		"name":
			# Rename the first central-directory entry only (local name kept).
			var cd3 := _rfind_sig(out, PackedByteArray([0x50, 0x4b, 0x01, 0x02]), out.size() - 1)
			if cd3 < 0:
				return ["no_central_directory", raw]
			out[cd3 + 46] = out[cd3 + 46] ^ 0x20
			return ["cd_name_byte_flipped_entry_0", out]
		"localname":
			# Rename the first local header only (central name kept).
			var local := _rfind_sig(out, PackedByteArray([0x50, 0x4b, 0x03, 0x04]), 0)
			if local < 0 or local != 0:
				return ["no_local_header_at_zero", raw]
			out[30] = out[30] ^ 0x20
			return ["local_name_byte_flipped_entry_0", out]
	return ["unknown_corruption_kind", raw]


func _census(zip_path: String, corrupt_note: String, export_seconds: float) -> int:
	var raw := FileAccess.get_file_as_bytes(zip_path)
	if raw.size() == 0:
		return _fail("zip_empty path=%s" % zip_path)
	_report("EXPORT_PROD_S02 zip_bytes=%d zip_sha256=%s export_seconds=%.3f"
			% [raw.size(), _sha256_bytes(raw), export_seconds])
	var eocd := _rfind_sig(raw, PackedByteArray([0x50, 0x4b, 0x05, 0x06]), raw.size() - 1)
	if eocd < 0:
		return _fail("integrity no_eocd_signature")
	var disk_number := raw.decode_u16(eocd + 4)
	var cd_disk := raw.decode_u16(eocd + 6)
	var cd_entries := raw.decode_u16(eocd + 8)
	var cd_total := raw.decode_u16(eocd + 10)
	var cd_size := raw.decode_u32(eocd + 12)
	var cd_offset := raw.decode_u32(eocd + 16)
	var comment_len := raw.decode_u16(eocd + 20)
	_report("EXPORT_PROD_S02 eocd offset=%d tail_bytes=%d disks=%d/%d entries=%d/%d cd_offset=%d cd_size=%d comment_len=%d"
			% [eocd, raw.size() - (eocd + 22), disk_number, cd_disk, cd_entries, cd_total, cd_offset, cd_size, comment_len])
	if disk_number != 0 or cd_disk != 0:
		return _fail("integrity multi_disk_archive disks=%d/%d" % [disk_number, cd_disk])
	if cd_entries != cd_total:
		return _fail("integrity eocd_entry_count_mismatch %d/%d" % [cd_entries, cd_total])
	if comment_len != 0:
		return _fail("integrity unexpected_archive_comment len=%d" % comment_len)
	if cd_offset + cd_size != eocd:
		return _fail("integrity central_directory_not_contiguous cd_end=%d eocd=%d" % [cd_offset + cd_size, eocd])
	if cd_offset != _rfind_sig(raw, PackedByteArray([0x50, 0x4b, 0x01, 0x02]), cd_offset + 3):
		return _fail("integrity central_directory_offset_wrong cd_offset=%d" % cd_offset)

	var names: PackedStringArray = []
	var sizes: Array = []
	var local_offsets: Array = []
	var cd_cursors: Array = []
	var mismatches: PackedStringArray = []
	var payload_sha: PackedStringArray = []
	var scn_crc := 0
	var scn_cs := 0
	var cursor := cd_offset
	for index in int(cd_entries):
		if cursor + 46 > raw.size():
			return _fail("integrity central_directory_overrun at_entry=%d" % index)
		if raw.slice(cursor, cursor + 4) != PackedByteArray([0x50, 0x4b, 0x01, 0x02]):
			return _fail("integrity missing_central_header_signature at_entry=%d offset=%d" % [index, cursor])
		cd_cursors.append(cursor)
		var flags := raw.decode_u16(cursor + 8)
		var method := raw.decode_u16(cursor + 10)
		var dos_time := raw.decode_u16(cursor + 12)
		var dos_date := raw.decode_u16(cursor + 14)
		var crc := raw.decode_u32(cursor + 16)
		var csize := raw.decode_u32(cursor + 20)
		var usize := raw.decode_u32(cursor + 24)
		var name_len := raw.decode_u16(cursor + 28)
		var extra_len := raw.decode_u16(cursor + 30)
		var comment := raw.decode_u16(cursor + 32)
		var make_version := raw.decode_u16(cursor + 4)
		var extract_version := raw.decode_u16(cursor + 6)
		var ext_attr := raw.decode_u32(cursor + 38)
		var local_offset := raw.decode_u32(cursor + 42)
		names.append(raw.slice(cursor + 46, cursor + 46 + name_len).get_string_from_utf8())
		sizes.append([usize, csize])
		local_offsets.append(local_offset)
		if index == UNSTABLE_INDEX:
			scn_crc = crc
			scn_cs = csize
		if flags != 0:
			mismatches.append("flags=%d@%d" % [flags, index])
		if method != 8:
			mismatches.append("method=%d@%d" % [method, index])
		if make_version != 0:
			mismatches.append("create_version=%d@%d" % [make_version, index])
		if extract_version != 20:
			mismatches.append("extract_version=%d@%d" % [extract_version, index])
		if dos_time != 0 or dos_date != 0:
			mismatches.append("dos_timestamp=%d/%d@%d" % [dos_time, dos_date, index])
		if extra_len != 0 or comment != 0:
			mismatches.append("extra=%d/comment=%d@%d" % [extra_len, comment, index])
		if ext_attr != 0:
			mismatches.append("ext_attr=%d@%d" % [ext_attr, index])
		# Local header must agree with the central directory entry.
		if local_offset + 30 > raw.size():
			return _fail("integrity local_header_out_of_range at_entry=%d" % index)
		if raw.slice(local_offset, local_offset + 4) != PackedByteArray([0x50, 0x4b, 0x03, 0x04]):
			return _fail("integrity missing_local_header_signature at_entry=%d offset=%d" % [index, local_offset])
		var l_name_len := raw.decode_u16(local_offset + 26)
		var l_extra_len := raw.decode_u16(local_offset + 28)
		var l_name := raw.slice(local_offset + 30, local_offset + 30 + l_name_len).get_string_from_utf8()
		if l_name != names[index]:
			mismatches.append("name_local_vs_cd@%d %s!=%s" % [index, l_name, names[index]])
		for pair in [[14, 16, "crc"], [18, 20, "csize"], [22, 24, "usize"]]:
			var local_value: int = raw.decode_u32(local_offset + pair[0])
			var cd_value: int = raw.decode_u32(cursor + pair[1])
			if cd_value != local_value:
				mismatches.append("%s_local_vs_cd@%d %d!=%d" % [pair[2], index, local_value, cd_value])
		var payload_start := local_offset + 30 + l_name_len + l_extra_len
		if payload_start + csize > raw.size():
			return _fail("integrity payload_out_of_range at_entry=%d" % index)
		cursor += 46 + name_len + extra_len + comment
		if cursor > cd_offset + cd_size:
			return _fail("integrity central_directory_size_overrun at_entry=%d" % index)

	# Payload integrity via the engine's inflater, then our own CRC32.
	var reader := ZIPReader.new()
	if reader.open(zip_path) != OK:
		return _fail("integrity zip_reader_open_failed")
	var listed := reader.get_files()
	if listed.size() != int(cd_entries):
		reader.close()
		return _fail("integrity zip_reader_entry_count %d!=%d" % [listed.size(), cd_entries])
	var crc_mismatch := 0
	var payload_bytes := 0
	var scn_vary_hex := ""
	var scn_prefix_ok := false
	var scn_suffix_ok := false
	for index in names.size():
		var payload := reader.read_file(names[index])
		payload_bytes += payload.size()
		if payload.size() != int(sizes[index][0]):
			crc_mismatch += 1
			mismatches.append("inflated_size@%d %d!=%d" % [index, payload.size(), sizes[index][0]])
		var cursor_cd: int = cd_cursors[index]
		if _crc32(payload) != raw.decode_u32(cursor_cd + 16):
			crc_mismatch += 1
			mismatches.append("crc32@%d" % index)
		payload_sha.append(_sha256_bytes(payload))
		if index == UNSTABLE_INDEX and payload.size() == int(EXPECTED_US[UNSTABLE_INDEX]):
			scn_vary_hex = payload.slice(SCN_VARY_START, SCN_VARY_END).hex_encode()
			scn_prefix_ok = _sha256_bytes(payload.slice(0, SCN_VARY_START)) == EXPECTED_SCN_PREFIX_SHA256
			scn_suffix_ok = _sha256_bytes(payload.slice(SCN_VARY_END, payload.size())) == EXPECTED_SCN_SUFFIX_SHA256
			if not scn_prefix_ok:
				mismatches.append("scn_prefix_sha@%d" % index)
			if not scn_suffix_ok:
				mismatches.append("scn_suffix_sha@%d" % index)
		_report("EXPORT_PROD_S02 entry index=%d name=%s us=%d cs=%d crc=%08x sha256=%s"
				% [index, names[index], sizes[index][0], sizes[index][1], raw.decode_u32(cursor_cd + 16), payload_sha[index]])
	reader.close()

	var names_exact := names.size() == EXPECTED_NAMES.size()
	if names_exact:
		for index in names.size():
			if names[index] != EXPECTED_NAMES[index]:
				names_exact = false
				mismatches.append("name@%d %s!=%s" % [index, names[index], EXPECTED_NAMES[index]])
	var sizes_exact := sizes.size() == EXPECTED_US.size()
	if sizes_exact:
		for index in sizes.size():
			if int(sizes[index][0]) != int(EXPECTED_US[index]):
				sizes_exact = false
				mismatches.append("us@%d %d!=%d" % [index, sizes[index][0], EXPECTED_US[index]])
	var hashes_pinned := 0
	for index in EXPECTED_SHA256.size():
		if EXPECTED_SHA256[index] != "":
			hashes_pinned += 1
			if index < payload_sha.size() and payload_sha[index] != EXPECTED_SHA256[index]:
				mismatches.append("sha256@%d" % index)
	_report("EXPORT_PROD_S02 integrity entries=%d payload_bytes=%d crc_mismatches=%d local_header_mismatches=%d"
			% [names.size(), payload_bytes, crc_mismatch, mismatches.size()])
	_report("EXPORT_PROD_S02 census names=%s" % "|".join(names))
	_report("EXPORT_PROD_S02 sizes us=%s cs=%s"
			% [_join_ints(sizes, 0), _join_ints(sizes, 1)])
	_report("EXPORT_PROD_S02 variance unstable_entry=%d varying_region=%d:%d scn_vary_hex=%s scn_crc=%08x scn_cs=%d prefix_ok=%s suffix_ok=%s"
			% [UNSTABLE_INDEX, SCN_VARY_START, SCN_VARY_END, scn_vary_hex, scn_crc, scn_cs, scn_prefix_ok, scn_suffix_ok])
	if corrupt_note != "":
		_report("EXPORT_PROD_S02 forgery=%s" % corrupt_note)
	if mismatches.size() > 0:
		return _fail("integrity mismatches=%d %s" % [mismatches.size(), ";".join(mismatches)])
	if crc_mismatch > 0:
		return _fail("integrity crc_mismatches=%d" % crc_mismatch)
	if not names_exact:
		return _fail("census names_differ from_pinned_set")
	if not sizes_exact:
		return _fail("census uncompressed_sizes_differ from_pinned_vector")
	if not scn_prefix_ok or not scn_suffix_ok:
		return _fail("integrity scn_mask_unpinned prefix_ok=%s suffix_ok=%s" % [scn_prefix_ok, scn_suffix_ok])
	_report("PASS export_prod_s02 entries=%d names_exact=true sizes_exact=true integrity=true eocd=true cd_local_consistency=true payload_hashes=%d/%d scn_masked=%d/%d"
			% [names.size(), hashes_pinned, EXPECTED_SHA256.size(), SCN_VARY_START + (int(EXPECTED_US[UNSTABLE_INDEX]) - SCN_VARY_END), int(EXPECTED_US[UNSTABLE_INDEX])])
	return 0


func _join_ints(rows: Array, column: int) -> String:
	var parts: PackedStringArray = []
	for row in rows:
		parts.append(str(row[column]))
	return ",".join(parts)


func _sha256_bytes(bytes: PackedByteArray) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	var chunk := 4096
	var offset := 0
	while offset < bytes.size():
		context.update(bytes.slice(offset, mini(offset + chunk, bytes.size())))
		offset += chunk
	return context.finish().hex_encode()


func _report(line: String) -> void:
	print(line)


func _fail(reason: String) -> int:
	print("EXPORT_PROD_S02 FAIL %s" % reason)
	if _fail_reason != "":
		print("EXPORT_PROD_S02 FAIL cause=%s" % _fail_reason)
	quit(2)
	return 2


func _run() -> int:
	var started := Time.get_ticks_msec()
	var run_id := _run_id if _run_id != "" else "%d-%d" % [OS.get_process_id(), Time.get_ticks_msec()]
	var run_dir := _root.path_join(run_id)
	var project_dir := run_dir.path_join("proj")
	var zip_path := _zip_override if _zip_override != "" else run_dir.path_join("out/prod.zip")
	_report("EXPORT_PROD_S02 start run_id=%s root=%s zip=%s preset=%s" % [run_id, _root, zip_path, PRESET_NAME])
	if _zip_override == "":
		var setup := _build_project(project_dir, zip_path.get_base_dir())
		if setup != "":
			print("EXPORT_PROD_S02 FAIL setup %s" % setup)
			quit(3)
			return 3
		var export_started := Time.get_ticks_msec()
		var outcome := _export(project_dir, zip_path)
		var export_seconds := float(Time.get_ticks_msec() - export_started) / 1000.0
		if int(outcome[0]) != 0 or not FileAccess.file_exists(zip_path):
			print("EXPORT_PROD_S02 FAIL export_failed rc=%s zip_exists=%s" % [outcome[0], FileAccess.file_exists(zip_path)])
			if not _keep:
				_delete_tree(run_dir)
			quit(3)
			return 3
		var corrupt_note := ""
		if _corrupt != "":
			var forged: Array = _forge(FileAccess.get_file_as_bytes(zip_path), _corrupt)
			var forged_path := zip_path + ".forged"
			var forged_bytes: PackedByteArray = forged[1]
			var handle := FileAccess.open(forged_path, FileAccess.WRITE)
			if handle == null:
				print("EXPORT_PROD_S02 FAIL setup cannot_write_forgery")
				quit(3)
				return 3
			handle.store_buffer(forged_bytes)
			handle.close()
			corrupt_note = str(forged[0])
			_report("EXPORT_PROD_S02 forgery note=%s forged_bytes=%d written_bytes=%d"
					% [corrupt_note, forged_bytes.size(), FileAccess.get_file_as_bytes(forged_path).size()])
			zip_path = forged_path
		var code := _census(zip_path, corrupt_note, export_seconds)
		_report("EXPORT_PROD_S02 total_seconds=%.3f" % (float(Time.get_ticks_msec() - started) / 1000.0))
		if not _keep:
			_delete_tree(run_dir)
		quit(code)
		return code
	var code := _census(zip_path, "", 0.0)
	quit(code)
	return code


func _initialize() -> void:
	_parse_args()
	_run()
