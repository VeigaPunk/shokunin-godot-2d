extends SceneTree
## export_prod_s06.gd — r101 export_prod lattice, scenario 06.
## Include/exclude export FILTER semantics, proven by a raw PCK census.
##
## Self-contained: the fixture materializes a production-shaped scratch project
## (2 scripts, 2 imported PNGs, a JSON resource, a non-resource .txt), runs the
## export templates, then parses the emitted PCK byte-for-byte.
##
## Launch shape:
##   godot --headless --path <scratch> --script res://export_prod_s06.gd -- \
##         [--arm=<name>] [--work=<dir>] [--keep] [--verbose]
##
## Arms (one export each; --arm=all runs the six filter arms):
##   baseline     no include/exclude filter            -> 12-entry reference pack
##   include-gd   include_filter="*.gd"                -> byte-identical to baseline
##   include-txt  include_filter="*.txt"               -> +docs/readme.txt (mechanism control)
##   include-xyz  include_filter="*.xyz" (no match)    -> byte-identical to baseline
##   exclude-png  exclude_filter="*.png"               -> 4 PNG import entries dropped
##   exclude-gd   exclude_filter="*.gd"                -> 4 script entries dropped
##   tamper       baseline export + 3 in-memory PCK forgeries; each must be rejected
##
## RECIPE (measured; see r101-E6 shard): a *virgin* project's first export can
## race the resource importer and emit a 0-byte PCK with remap-section ERRORs
## under host load. Every arm therefore runs `--import` first, which materializes
## .import/.gd.uid sidecars; the subsequent `--export-pack` is then byte-stable
## (two fresh copies per arm produced identical sha256 in the r101-E6 probe).
##
## Exit: 0 = PASS, 2 = assertion failure, 3 = setup/IO failure.

const MAGIC := "GDPC"
const FORMAT_VERSION := 4
const ENGINE := "4.7.2"
const FLAGS := 2
const FILE_BASE := 112
const DEFAULT_WORK := "/var/tmp/r101-export-prod-s06"

const PROJECT_GODOT := """[application]

config/name="ExportProdS06"
config/features=PackedStringArray("4.7")
"""

const ALPHA_GD := """extends Node
const MARKER := "alpha"
"""

const BETA_GD := """extends Node
const MARKER := "beta"
"""

const README_TXT := """s06 non-resource text
"""

const DATA_JSON := """{"s06": true}
"""

const PNG_B64 := "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAFklEQVR4nGP8z8DAwMDAxMDAwMDAAAANHQEDasKb6QAAAABJRU5ErkJggg=="

## Pinned import sidecars. The imported-texture UID is not reliably regenerated
## by the importer (one r101-E6 run produced a different uid:// and a 2176-byte
## pack), so the fixture seeds the .import files with the measured UIDs; the
## importer keeps them and the exported pack is then byte-stable.
const TILE_IMPORT := """[remap]

importer="texture"
type="CompressedTexture2D"
uid="uid://e36scniavtjw"
path="res://.godot/imported/tile.png-455dd1073ac41712b0ee435e5393be66.ctex"
metadata={
"vram_texture": false
}

[deps]

source_file="res://assets/tile.png"
dest_files=["res://.godot/imported/tile.png-455dd1073ac41712b0ee435e5393be66.ctex"]

[params]

compress/mode=0
compress/high_quality=false
compress/lossy_quality=0.7
compress/uastc_level=0
compress/rdo_quality_loss=0.0
compress/hdr_compression=1
compress/normal_map=0
compress/channel_pack=0
mipmaps/generate=false
mipmaps/limit=-1
roughness/mode=0
roughness/src_normal=""
process/channel_remap/red=0
process/channel_remap/green=1
process/channel_remap/blue=2
process/channel_remap/alpha=3
process/fix_alpha_border=true
process/premult_alpha=false
process/normal_map_invert_y=false
process/hdr_as_srgb=false
process/hdr_clamp_exposure=false
process/size_limit=0
detect_3d/compress_to=1
"""

const ICON2_IMPORT := """[remap]

importer="texture"
type="CompressedTexture2D"
uid="uid://bicai3ec6m0a3"
path="res://.godot/imported/icon2.png-2b6439a0200a65cfd84819fc8d4704be.ctex"
metadata={
"vram_texture": false
}

[deps]

source_file="res://assets/icon2.png"
dest_files=["res://.godot/imported/icon2.png-2b6439a0200a65cfd84819fc8d4704be.ctex"]

[params]

compress/mode=0
compress/high_quality=false
compress/lossy_quality=0.7
compress/uastc_level=0
compress/rdo_quality_loss=0.0
compress/hdr_compression=1
compress/normal_map=0
compress/channel_pack=0
mipmaps/generate=false
mipmaps/limit=-1
roughness/mode=0
roughness/src_normal=""
process/channel_remap/red=0
process/channel_remap/green=1
process/channel_remap/blue=2
process/channel_remap/alpha=3
process/fix_alpha_border=true
process/premult_alpha=false
process/normal_map_invert_y=false
process/hdr_as_srgb=false
process/hdr_clamp_exposure=false
process/size_limit=0
detect_3d/compress_to=1
"""

## Pre-export input census: the PCK pins below are only meaningful if the
## project inputs are byte-identical to the measured ones.
const INPUT_SHA := {
	"project.godot": "0c3f05b870e20afee0d78af4464d8b54ecfa802d4a04818334dde20025cfd277",
	"scripts/alpha.gd": "4a2154b6dae5f0a67bedafc695eedbda3947c561b5ef59de41dce0b96aa537e2",
	"scripts/beta.gd": "d6906c19ed96fdda274bf9f343e04363fbd282dec56e33569f0d0f8829f73f36",
	"docs/readme.txt": "f84aa3d660bb656a854ac50b3991a346ea789981d69956d87481db3829822e5a",
	"docs/data.json": "a29f8a1de2c831bcec65214b4db85046108cd9387720508c39c12f34762e0060",
	"assets/tile.png": "be21aef17f0baf04b1bf148f8a23bda4e879b346a64637fdd711bea012e646a8",
	"assets/icon2.png": "be21aef17f0baf04b1bf148f8a23bda4e879b346a64637fdd711bea012e646a8",
	"assets/tile.png.import": "a83c3558015e71e39477666948ac673681655d3ded4783ebb2f0fc299788d521",
	"assets/icon2.png.import": "73eb4df1373a2ba24a8f8a0b3e3f7c2a6a1014d3a7e90cea06de6f16add3faf9",
}

## Per-arm pins: preset name, filters, and the exact census of the emitted PCK.
## `entries` is the sorted canonical replay "path|size|sha256"; `path_sha` and
## `full_sha` are sha256 over "\n".join(paths) and "\n".join(canonical) so an
## injected, dropped or reordered ENT row changes a digest the battery pins.
const ARMS := {
	"baseline": {
		"preset": "All", "include": "", "exclude": "",
		"count": 12, "bytes": 2160, "dir_offset": 1328, "stored_lines": 12,
		"pck_sha256": "22defedba9461cf79dda1d72a2b8db0996e62a92ea663b8f0c0c894d9f4e2881",
		"path_sha256": "7943db8e2d36b58364ca10003db6ae80a508583ec367b24986b730d1b85e8641",
		"full_sha256": "343bb3ba8d8208cff4415a11b98b0b64f65a5e483bec2521005e7412b0266c26",
		"entries": [
			".godot/global_script_class_cache.cfg|8|f61aa7ad3097022d6a9d110ca3f73fa7bb348ec2cf9a6e7c9523574dc75f5a16",
			".godot/imported/icon2.png-2b6439a0200a65cfd84819fc8d4704be.ctex|92|3fcf2b22126e86b1cbc9ec53eee5cfe7f5a11f97a7e6aeeaa0259600718dd7cc",
			".godot/imported/tile.png-455dd1073ac41712b0ee435e5393be66.ctex|92|3fcf2b22126e86b1cbc9ec53eee5cfe7f5a11f97a7e6aeeaa0259600718dd7cc",
			".godot/uid_cache.bin|138|adb02ddab4a7a282a6f480f03e288f255265049420a101a3ffad597148f7939b",
			"assets/icon2.png.import|194|c60118bdb6275cf8931b2026321075d4eec6a68ebd3b446dec92b2ca04be2f11",
			"assets/tile.png.import|192|7cc6ab408be9f7ecce451b3295f1d4ce66f8f8d94105332f3cd6663cb0ef89cd",
			"docs/data.json|14|a29f8a1de2c831bcec65214b4db85046108cd9387720508c39c12f34762e0060",
			"project.binary|114|b07db2520088beeff631e34d5e7ad4647a424a211556e6c880c91f43475a855a",
			"scripts/alpha.gd.remap|40|448c50cfbccedc157b727cb547868bf746359ccfa098af8753b79b7617c489be",
			"scripts/alpha.gdc|111|ee60c4ae37798db7557379172b837d375d13ed52c54195a759f88a9fd5f48eb5",
			"scripts/beta.gd.remap|39|914646cd285b41352af41ee7aeb3f176e65cd31e88028afaef2bb5171472ceff",
			"scripts/beta.gdc|109|ccf4a04f92ed900a68613e5958626ef057bd07df2d6898db274fefc8842eee67",
		],
	},
	"include-gd": {
		"preset": "IncludeGD", "include": "*.gd", "exclude": "",
		"count": 12, "bytes": 2160, "dir_offset": 1328, "stored_lines": 12,
		"pck_sha256": "22defedba9461cf79dda1d72a2b8db0996e62a92ea663b8f0c0c894d9f4e2881",
		"path_sha256": "7943db8e2d36b58364ca10003db6ae80a508583ec367b24986b730d1b85e8641",
		"full_sha256": "343bb3ba8d8208cff4415a11b98b0b64f65a5e483bec2521005e7412b0266c26",
		"entries": [],   # identical to baseline; filled at run time from the baseline pin
	},
	"include-txt": {
		"preset": "IncludeTXT", "include": "*.txt", "exclude": "",
		"count": 13, "bytes": 2248, "dir_offset": 1360, "stored_lines": 13,
		"pck_sha256": "8db147ef5eaa5f88125ca2b48c8f2b92b65fe304ba0e858370a0f551e1e28d39",
		"path_sha256": "ba5bcc655d71303150c8a59d231d9a8dbc8b41cf7b4bd000d3ffe750458bb5a5",
		"full_sha256": "4ace078dea6f05ad72b3bdd6cf2a9cd20c9fc0e517c75dddb33d4587125da39f",
		"entries": [
			".godot/global_script_class_cache.cfg|8|f61aa7ad3097022d6a9d110ca3f73fa7bb348ec2cf9a6e7c9523574dc75f5a16",
			".godot/imported/icon2.png-2b6439a0200a65cfd84819fc8d4704be.ctex|92|3fcf2b22126e86b1cbc9ec53eee5cfe7f5a11f97a7e6aeeaa0259600718dd7cc",
			".godot/imported/tile.png-455dd1073ac41712b0ee435e5393be66.ctex|92|3fcf2b22126e86b1cbc9ec53eee5cfe7f5a11f97a7e6aeeaa0259600718dd7cc",
			".godot/uid_cache.bin|138|adb02ddab4a7a282a6f480f03e288f255265049420a101a3ffad597148f7939b",
			"assets/icon2.png.import|194|c60118bdb6275cf8931b2026321075d4eec6a68ebd3b446dec92b2ca04be2f11",
			"assets/tile.png.import|192|7cc6ab408be9f7ecce451b3295f1d4ce66f8f8d94105332f3cd6663cb0ef89cd",
			"docs/data.json|14|a29f8a1de2c831bcec65214b4db85046108cd9387720508c39c12f34762e0060",
			"docs/readme.txt|22|f84aa3d660bb656a854ac50b3991a346ea789981d69956d87481db3829822e5a",
			"project.binary|114|b07db2520088beeff631e34d5e7ad4647a424a211556e6c880c91f43475a855a",
			"scripts/alpha.gd.remap|40|448c50cfbccedc157b727cb547868bf746359ccfa098af8753b79b7617c489be",
			"scripts/alpha.gdc|111|ee60c4ae37798db7557379172b837d375d13ed52c54195a759f88a9fd5f48eb5",
			"scripts/beta.gd.remap|39|914646cd285b41352af41ee7aeb3f176e65cd31e88028afaef2bb5171472ceff",
			"scripts/beta.gdc|109|ccf4a04f92ed900a68613e5958626ef057bd07df2d6898db274fefc8842eee67",
		],
	},
	"include-xyz": {
		"preset": "IncludeXyz", "include": "*.xyz", "exclude": "",
		"count": 12, "bytes": 2160, "dir_offset": 1328, "stored_lines": 12,
		"pck_sha256": "22defedba9461cf79dda1d72a2b8db0996e62a92ea663b8f0c0c894d9f4e2881",
		"path_sha256": "7943db8e2d36b58364ca10003db6ae80a508583ec367b24986b730d1b85e8641",
		"full_sha256": "343bb3ba8d8208cff4415a11b98b0b64f65a5e483bec2521005e7412b0266c26",
		"entries": [],
	},
	"exclude-png": {
		"preset": "ExcludePNG", "include": "", "exclude": "*.png",
		"count": 8, "bytes": 1168, "dir_offset": 672, "stored_lines": 8,
		"pck_sha256": "03521f45e3f380ec4fa0e47c0674dec70184213c9ce3d232327af1c1fb621fb3",
		"path_sha256": "e428bc39a98c456496b164ce892f3250b76975f3dcfd11632b8df71db246701a",
		"full_sha256": "5c92c425da909bc7c58c1007a2301ebfad5929d074758911fce24064a102a468",
		"entries": [
			".godot/global_script_class_cache.cfg|8|f61aa7ad3097022d6a9d110ca3f73fa7bb348ec2cf9a6e7c9523574dc75f5a16",
			".godot/uid_cache.bin|71|8f55f49823622ec5c8d6cb170a902abfcb0a6e21433cc164f15d482c5295d561",
			"docs/data.json|14|a29f8a1de2c831bcec65214b4db85046108cd9387720508c39c12f34762e0060",
			"project.binary|114|b07db2520088beeff631e34d5e7ad4647a424a211556e6c880c91f43475a855a",
			"scripts/alpha.gd.remap|40|448c50cfbccedc157b727cb547868bf746359ccfa098af8753b79b7617c489be",
			"scripts/alpha.gdc|111|ee60c4ae37798db7557379172b837d375d13ed52c54195a759f88a9fd5f48eb5",
			"scripts/beta.gd.remap|39|914646cd285b41352af41ee7aeb3f176e65cd31e88028afaef2bb5171472ceff",
			"scripts/beta.gdc|109|ccf4a04f92ed900a68613e5958626ef057bd07df2d6898db274fefc8842eee67",
		],
	},
	"exclude-gd": {
		"preset": "ExcludeGD", "include": "", "exclude": "*.gd",
		"count": 8, "bytes": 1532, "dir_offset": 944, "stored_lines": 8,
		"pck_sha256": "d24940dd441055e4da09fcaa9fab533717a25022b80a192ba9f931c5479ec77d",
		"path_sha256": "aaf94ac702bd8cda688a55076d36afd60daf0a097551bf10bd912510e6c80f54",
		"full_sha256": "d32ab0bd4fe1856a7637a9651638c43cb783479650443f162321a6f7a6e0dbf7",
		"entries": [
			".godot/global_script_class_cache.cfg|8|f61aa7ad3097022d6a9d110ca3f73fa7bb348ec2cf9a6e7c9523574dc75f5a16",
			".godot/imported/icon2.png-2b6439a0200a65cfd84819fc8d4704be.ctex|92|3fcf2b22126e86b1cbc9ec53eee5cfe7f5a11f97a7e6aeeaa0259600718dd7cc",
			".godot/imported/tile.png-455dd1073ac41712b0ee435e5393be66.ctex|92|3fcf2b22126e86b1cbc9ec53eee5cfe7f5a11f97a7e6aeeaa0259600718dd7cc",
			".godot/uid_cache.bin|71|ee0cb5ff2e5b46612baeef718e220ec685de097c2101d9cd3d9d4a6fd284b57b",
			"assets/icon2.png.import|194|c60118bdb6275cf8931b2026321075d4eec6a68ebd3b446dec92b2ca04be2f11",
			"assets/tile.png.import|192|7cc6ab408be9f7ecce451b3295f1d4ce66f8f8d94105332f3cd6663cb0ef89cd",
			"docs/data.json|14|a29f8a1de2c831bcec65214b4db85046108cd9387720508c39c12f34762e0060",
			"project.binary|114|b07db2520088beeff631e34d5e7ad4647a424a211556e6c880c91f43475a855a",
		],
	},
}

const FILTER_ARMS := ["baseline", "include-gd", "include-txt", "include-xyz", "exclude-png", "exclude-gd"]

var _arm := "all"
var _work := DEFAULT_WORK
var _keep := false
var _verbose := false
var _replay: Array[String] = []
var _census_entries: Array = []
var _census_paths: Array = []

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--arm="):
			_arm = a.substr(6)
		elif a.begins_with("--work="):
			_work = a.substr(7)
		elif a == "--keep":
			_keep = true
		elif a == "--verbose":
			_verbose = true
	_run.call_deferred()

func _run() -> void:
	var code := 0
	if _arm == "all":
		for arm in FILTER_ARMS:
			if not _run_arm(arm):
				code = 2
				break
	elif _arm == "tamper":
		if not _run_tamper():
			code = 2
	elif ARMS.has(_arm):
		if not _run_arm(_arm):
			code = 2
	else:
		_row("unknown_arm=%s" % _arm)
		code = 3
	quit(code)

# ------------------------------------------------------------------- arms

func _run_arm(arm: String) -> bool:
	var pin: Dictionary = ARMS[arm]
	_row("arm=%s preset=%s include=%s exclude=%s" % [arm, pin["preset"], pin["include"], pin["exclude"]])
	var project := _prepare(arm, pin)
	if project == "":
		return false
	var imp := _child(["--headless", "--path", project, "--import"])
	_row("R1 import_rc=%d" % imp["rc"])
	if imp["rc"] != 0:
		return _fail("import_rc=%d" % imp["rc"])
	var pck := project.path_join("out/export.pck")
	var exp := _child(["--headless", "--path", project, "--export-pack", pin["preset"], pck])
	_row("R2 export_rc=%d stored_lines=%d" % [exp["rc"], exp["stored"]])
	if exp["rc"] != 0:
		return _fail("export_rc=%d" % exp["rc"])
	if not FileAccess.file_exists(pck):
		return _fail("export_produced_no_pck")
	var raw := FileAccess.get_file_as_bytes(pck)
	if raw.size() == 0:
		return _fail("pck_empty")
	var c := _census(raw)
	if c["fail"] != "":
		return _fail("census_fail=%s" % c["fail"])
	_emit_census(c)
	var reason := _verify_arm(arm, c)
	if reason != "":
		return _fail(reason)
	_row("R8 pin_ok=1 canonical_entries=%d" % _census_entries.size())
	var replay := _replay_sha()
	print("S06 REPLAY_SHA256 %s" % replay)
	print("PASS export_prod_s06 arm=%s pck_sha256=%s bytes=%d count=%d path_sha256=%s full_sha256=%s arm_checks_ok=1 replay_sha256=%s" % [
		arm, c["pck_sha256"], c["bytes"], c["count"], c["path_sha256"], c["full_sha256"], replay])
	return true

func _verify_arm(arm: String, c: Dictionary) -> String:
	var pin: Dictionary = ARMS[arm]
	if c["count"] != pin["count"]:
		return "count=%d expected %d" % [c["count"], pin["count"]]
	var expected: Array = pin["entries"]
	if expected.is_empty():
		expected = ARMS["baseline"]["entries"]
	if c["canonical"] != expected:
		for i in range(min(c["canonical"].size(), expected.size())):
			if c["canonical"][i] != expected[i]:
				return "entry_row_%d got=%s expected=%s" % [i, c["canonical"][i], expected[i]]
		return "entry_count_mismatch got=%d expected=%d" % [c["canonical"].size(), expected.size()]
	if c["md5_ok"] != c["count"]:
		return "md5_ok=%d/%d" % [c["md5_ok"], c["count"]]
	if c["dir_end"] != c["bytes"]:
		return "dir_end=%d bytes=%d" % [c["dir_end"], c["bytes"]]
	if c["pck_sha256"] != pin["pck_sha256"]:
		return "pck_sha256=%s expected=%s" % [c["pck_sha256"], pin["pck_sha256"]]
	if c["bytes"] != pin["bytes"] or c["dir_offset"] != pin["dir_offset"]:
		return "bytes/dir_offset=%d/%d expected=%d/%d" % [c["bytes"], c["dir_offset"], pin["bytes"], pin["dir_offset"]]
	if c["path_sha256"] != pin["path_sha256"] or c["full_sha256"] != pin["full_sha256"]:
		return "census_digest_mismatch"
	var reason := _semantics(arm, c)
	if reason != "":
		return reason
	_row("R7 semantics=%s" % _semantics_row)
	return ""

var _semantics_row := ""

## Arm-specific claims. These are the rows the lattice cites; the canonical
## pin above already makes them byte-exact, but each prints its own evidence.
func _semantics(arm: String, c: Dictionary) -> String:
	var paths: Array[String] = c["paths"]
	var raw_gd := _count_suffix(paths, ".gd")
	var gdc := _count_suffix(paths, ".gdc")
	var remap := _count_suffix(paths, ".gd.remap")
	var txt := _count_suffix(paths, ".txt")
	var imp := _count_suffix(paths, ".png.import")
	var ctex := _count_suffix(paths, ".ctex")
	var baseline: Array = ARMS["baseline"]["entries"]
	match arm:
		"baseline":
			_semantics_row = "baseline raw_gd=%d gdc=%d remap=%d png_import=%d ctex=%d txt=%d" % [raw_gd, gdc, remap, imp, ctex, txt]
			if raw_gd != 0 or gdc != 2 or remap != 2 or imp != 2 or ctex != 2 or txt != 0:
				return "baseline composition mismatch"
		"include-gd":
			_semantics_row = "include_gd raw_gd=%d gdc=%d remap=%d txt=%d byte_identical_to_baseline=%d" % [
				raw_gd, gdc, remap, txt, int(c["pck_sha256"] == ARMS["baseline"]["pck_sha256"])]
			if raw_gd != 0 or txt != 0:
				return "include_gd admitted a non-resource source file"
			if c["pck_sha256"] != ARMS["baseline"]["pck_sha256"]:
				return "include_gd is not byte-identical to baseline"
		"include-xyz":
			_semantics_row = "include_xyz added=%d byte_identical_to_baseline=%d" % [
				c["count"] - 12, int(c["pck_sha256"] == ARMS["baseline"]["pck_sha256"])]
			if c["pck_sha256"] != ARMS["baseline"]["pck_sha256"]:
				return "include_xyz is not byte-identical to baseline"
		"include-txt":
			var added := _set_diff(paths, _paths_of(baseline))
			_semantics_row = "include_txt added=%s added_count=%d byte_identical_to_baseline=%d" % [
				",".join(PackedStringArray(added)), added.size(), int(c["pck_sha256"] == ARMS["baseline"]["pck_sha256"])]
			if added != ["docs/readme.txt"]:
				return "include_txt added=%s expected docs/readme.txt only" % ",".join(PackedStringArray(added))
			if c["pck_sha256"] == ARMS["baseline"]["pck_sha256"]:
				return "include_txt did not change the pack"
		"exclude-png":
			var dropped := _set_diff(_paths_of(baseline), paths)
			var png_paths := 0
			for p in paths:
				if p.contains(".png"):
					png_paths += 1
			_semantics_row = "exclude_png png_paths=%d ctex=%d dropped=%s dropped_count=%d" % [
				png_paths, ctex, ",".join(PackedStringArray(dropped)), dropped.size()]
			if png_paths != 0 or ctex != 0:
				return "exclude_png left PNG-derived entries in the pack"
			var want := [
				".godot/imported/icon2.png-2b6439a0200a65cfd84819fc8d4704be.ctex",
				".godot/imported/tile.png-455dd1073ac41712b0ee435e5393be66.ctex",
				"assets/icon2.png.import",
				"assets/tile.png.import",
			]
			if dropped != want:
				return "exclude_png dropped=%s expected the 4 PNG entries" % ",".join(dropped)
		"exclude-gd":
			var dropped2 := _set_diff(_paths_of(baseline), paths)
			_semantics_row = "exclude_gd gdc=%d remap=%d dropped=%s dropped_count=%d" % [
				gdc, remap, ",".join(PackedStringArray(dropped2)), dropped2.size()]
			if gdc != 0 or remap != 0:
				return "exclude_gd left compiled/remapped script entries in the pack"
			var want2 := [
				"scripts/alpha.gdc",
				"scripts/alpha.gd.remap",
				"scripts/beta.gdc",
				"scripts/beta.gd.remap",
			]
			if dropped2 != want2:
				return "exclude-gd dropped=%s expected the 4 script entries" % ",".join(dropped2)
	return ""

# ----------------------------------------------------------------- tamper

func _run_tamper() -> bool:
	_row("arm=tamper source=baseline")
	var pin: Dictionary = ARMS["baseline"]
	var project := _prepare("tamper", pin)
	if project == "":
		return false
	var imp := _child(["--headless", "--path", project, "--import"])
	if imp["rc"] != 0:
		return _fail("tamper_import_rc=%d" % imp["rc"])
	var pck := project.path_join("out/export.pck")
	var exp := _child(["--headless", "--path", project, "--export-pack", pin["preset"], pck])
	if exp["rc"] != 0:
		return _fail("tamper_export_rc=%d" % exp["rc"])
	var raw := FileAccess.get_file_as_bytes(pck)
	var control := _census(raw)
	var control_reason := _verify_arm("baseline", control)
	if control_reason != "":
		return _fail("tamper_control_rejected=%s" % control_reason)
	_row("R9 tamper_control accepted=1")
	var rejected := 0
	var kinds := ["path", "size", "extra"]
	for kind in kinds:
		var forged := _forge(raw, kind)
		var c := _census(forged)
		var reason := ""
		if c["fail"] != "":
			reason = "census_fail=%s" % c["fail"]
		else:
			reason = _verify_arm("baseline", c)
		if reason == "":
			_row("MUT %s accepted=true" % kind)
		else:
			rejected += 1
			_row("MUT %s rejected=true fail=%s" % [kind, reason.split(" ")[0]])
	if rejected != kinds.size():
		return _fail("mutations_rejected=%d/%d" % [rejected, kinds.size()])
	_row("R9 mutations_rejected=%d/%d" % [rejected, kinds.size()])
	var replay := _replay_sha()
	print("S06 REPLAY_SHA256 %s" % replay)
	print("PASS export_prod_s06 arm=tamper control_accepted=1 mutations_rejected=%d/%d replay_sha256=%s" % [
		rejected, kinds.size(), replay])
	return true

func _forge(raw: PackedByteArray, kind: String) -> PackedByteArray:
	var out := raw.duplicate()
	var c := _census(raw)
	if c["fail"] != "":
		return out
	var dir_offset := int(c["dir_offset"])
	var count := int(c["count"])
	match kind:
		"path":
			# Flip the last byte of docs/data.json's directory path.
			for e in c["entries"]:
				if e["path"] == "docs/data.json":
					out[e["path_offset"] + e["path_length"] - 1] = 0x6d  # 'n' -> 'm'
					break
		"size":
			# Over-declare one entry by one byte: payload sha / md5 no longer match.
			for e in c["entries"]:
				if e["path"] == "docs/data.json":
					out.encode_u64(e["size_field_offset"], int(e["size"]) + 1)
					break
		"extra":
			# Claim one more directory entry than exists.
			out.encode_u32(dir_offset, count + 1)
			var pad := PackedByteArray()
			pad.resize(56)
			out.append_array(pad)
	return out

# -------------------------------------------------------------- census core

func _census(b: PackedByteArray) -> Dictionary:
	var res := {"fail": "", "bytes": b.size(), "count": 0, "entries": [], "paths": [],
		"canonical": [], "md5_ok": 0, "dir_offset": 0, "file_base": 0, "flags": 0,
		"format": 0, "magic": "", "engine": "", "dir_end": 0,
		"pck_sha256": _sha(b), "path_sha256": "", "full_sha256": ""}
	if b.size() < 48:
		res["fail"] = "size=%d too small" % b.size()
		return res
	res["magic"] = b.slice(0, 4).get_string_from_ascii()
	res["format"] = b.decode_u32(4)
	var engine := "%d.%d.%d" % [b.decode_u32(8), b.decode_u32(12), b.decode_u32(16)]
	res["engine"] = engine
	res["flags"] = b.decode_u32(20)
	res["file_base"] = b.decode_u64(24)
	res["dir_offset"] = b.decode_u64(32)
	if res["magic"] != MAGIC:
		res["fail"] = "magic=%s" % res["magic"]
		return res
	if res["format"] != FORMAT_VERSION or engine != ENGINE or res["flags"] != FLAGS or res["file_base"] != FILE_BASE:
		res["fail"] = "header format=%d engine=%s flags=%d file_base=%d" % [res["format"], engine, res["flags"], res["file_base"]]
		return res
	var dir_offset := int(res["dir_offset"])
	if dir_offset + 4 > b.size():
		res["fail"] = "dir_offset_beyond_size"
		return res
	var count := b.decode_u32(dir_offset)
	res["count"] = count
	if count > 4096:
		res["fail"] = "count=%d implausible" % count
		return res
	var off := dir_offset + 4
	for _i in range(count):
		if off + 4 > b.size():
			res["fail"] = "directory_truncated"
			return res
		var path_len := b.decode_u32(off)
		var path_offset := off + 4
		off += 4
		if path_len > 2048 or path_offset + path_len > b.size():
			res["fail"] = "path_len=%d out_of_bounds" % path_len
			return res
		var path := _trim_nul(b.slice(path_offset, path_offset + path_len)).get_string_from_utf8()
		off = path_offset + path_len
		if off + 36 > b.size():
			res["fail"] = "entry_truncated path=%s" % path
			return res
		var data_offset := b.decode_u64(off)
		var size_field_offset := off + 8
		var size := b.decode_u64(size_field_offset)
		off = size_field_offset + 8
		var md5 := b.slice(off, off + 16)
		off += 16
		var flags := b.decode_u32(off)
		off += 4
		var start := int(res["file_base"]) + int(data_offset)
		var stop := start + int(size)
		if stop > b.size():
			res["fail"] = "payload_out_of_bounds path=%s" % path
			return res
		var payload := b.slice(start, stop)
		var sha := _sha(payload)
		var md5_ok := _md5(payload) == md5.hex_encode()
		if md5_ok:
			res["md5_ok"] = int(res["md5_ok"]) + 1
		res["entries"].append({
			"path": path, "path_offset": path_offset, "path_length": path_len,
			"size": int(size), "size_field_offset": size_field_offset, "flags": flags,
			"sha256": sha, "md5_ok": md5_ok,
		})
		res["paths"].append(path)
		res["canonical"].append("%s|%d|%s" % [path, int(size), sha])
	res["dir_end"] = off
	res["paths"].sort()
	res["canonical"].sort()
	res["path_sha256"] = _sha("\n".join(res["paths"]).to_utf8_buffer())
	res["full_sha256"] = _sha("\n".join(res["canonical"]).to_utf8_buffer())
	return res

func _emit_census(c: Dictionary) -> void:
	_census_entries = c["canonical"]
	_census_paths = c["paths"]
	_row("R3 pck_bytes=%d pck_sha256=%s" % [c["bytes"], c["pck_sha256"]])
	_row("R4 header magic=%s format=%d engine=%s flags=%d file_base=%d dir_offset=%d" % [
		c["magic"], c["format"], c["engine"], c["flags"], c["file_base"], c["dir_offset"]])
	_row("R5 count=%d md5_ok=%d/%d dir_end=%d dir_end_eq_size=%d" % [
		c["count"], c["md5_ok"], c["count"], c["dir_end"], int(c["dir_end"] == c["bytes"])])
	for line in c["canonical"]:
		_row("ENT %s" % line)
	_row("R6 path_sha256=%s full_sha256=%s" % [c["path_sha256"], c["full_sha256"]])

# --------------------------------------------------------------- utilities

func _prepare(arm: String, pin: Dictionary) -> String:
	var project := _work.path_join(arm)
	if DirAccess.dir_exists_absolute(project):
		_rm_rf(project)
	for d in ["", "scripts", "assets", "docs", "out"]:
		var err := DirAccess.make_dir_recursive_absolute(project.path_join(d))
		if err != OK:
			_fail("mkdir %s err=%s" % [project.path_join(d), error_string(err)])
			return ""
	var png := Marshalls.base64_to_raw(PNG_B64)
	var files := {
		"project.godot": PROJECT_GODOT,
		"scripts/alpha.gd": ALPHA_GD,
		"scripts/beta.gd": BETA_GD,
		"docs/readme.txt": README_TXT,
		"docs/data.json": DATA_JSON,
		"assets/tile.png.import": TILE_IMPORT,
		"assets/icon2.png.import": ICON2_IMPORT,
	}
	for rel in files:
		if not _write_text(project.path_join(rel), files[rel]):
			return ""
	for rel in ["assets/tile.png", "assets/icon2.png"]:
		var f := FileAccess.open(project.path_join(rel), FileAccess.WRITE)
		if f == null:
			_fail("write %s err=%s" % [rel, error_string(FileAccess.get_open_error())])
			return ""
		f.store_buffer(png)
		f.close()
	var preset := """[preset.0]

name="%s"
platform="Linux/X11"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter="%s"
exclude_filter="%s"
export_path=""

[preset.0.options]

binary_format/architecture="x86_64"
""" % [pin["preset"], pin["include"], pin["exclude"]]
	if not _write_text(project.path_join("export_presets.cfg"), preset):
		return ""
	# Input census: the pins only hold if these bytes match the measured ones.
	for rel in INPUT_SHA:
		var bytes := FileAccess.get_file_as_bytes(project.path_join(rel))
		var got := _sha(bytes)
		if got != INPUT_SHA[rel]:
			_fail("input_sha %s got=%s expected=%s" % [rel, got, INPUT_SHA[rel]])
			return ""
	_row("R0 inputs=%d input_sha_ok=1 png_bytes=%d" % [INPUT_SHA.size(), png.size()])
	return project

func _write_text(path: String, text: String) -> bool:
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		_fail("write %s err=%s" % [path, error_string(FileAccess.get_open_error())])
		return false
	f.store_string(text)
	f.close()
	return true

func _child(args: Array) -> Dictionary:
	var out: Array = []
	var started := Time.get_ticks_msec()
	var rc := OS.execute(OS.get_executable_path(), args, out, true)
	var captured := ""
	for chunk in out:
		captured += String(chunk)
		if not captured.ends_with("\n"):
			captured += "\n"
	var stored := 0
	for line in captured.split("\n"):
		if line.contains("Storing File:"):
			stored += 1
	if _verbose:
		for line in captured.split("\n"):
			if not line.strip_edges().is_empty():
				print("S06 child: %s" % line)
	return {"rc": rc, "stored": stored, "bytes": captured.length(), "ms": Time.get_ticks_msec() - started}

func _row(text: String) -> void:
	_replay.append(text)
	print("S06 %s" % text)

func _replay_sha() -> String:
	return _sha("\n".join(_replay).to_utf8_buffer())

func _fail(reason: String) -> bool:
	print("S06 FAIL reason=%s" % reason)
	var replay := _replay_sha()
	print("S06 REPLAY_SHA256 %s" % replay)
	print("ERROR: EXPORT_PROD_S06 ASSERTION FAILED: %s" % reason)
	quit(2)
	return false

func _trim_nul(bytes: PackedByteArray) -> PackedByteArray:
	var n := bytes.size()
	while n > 0 and bytes[n - 1] == 0:
		n -= 1
	return bytes.slice(0, n)

func _sha(bytes: PackedByteArray) -> String:
	var h := HashingContext.new()
	h.start(HashingContext.HASH_SHA256)
	h.update(bytes)
	return h.finish().hex_encode()

func _md5(bytes: PackedByteArray) -> String:
	var h := HashingContext.new()
	h.start(HashingContext.HASH_MD5)
	h.update(bytes)
	return h.finish().hex_encode()

func _count_suffix(paths: Array, suffix: String) -> int:
	var n := 0
	for p in paths:
		if String(p).ends_with(suffix):
			n += 1
	return n

func _paths_of(canonical: Array) -> Array:
	var out: Array = []
	for line in canonical:
		out.append(String(line).split("|")[0])
	out.sort()
	return out

func _set_diff(a: Array, b: Array) -> Array:
	var out: Array = []
	for x in a:
		if not b.has(x):
			out.append(x)
	out.sort()
	return out

func _rm_rf(p: String) -> void:
	if not DirAccess.dir_exists_absolute(p):
		return
	for f in DirAccess.get_files_at(p):
		DirAccess.remove_absolute(p.path_join(f))
	for d in DirAccess.get_directories_at(p):
		_rm_rf(p.path_join(d))
	DirAccess.remove_absolute(p)
