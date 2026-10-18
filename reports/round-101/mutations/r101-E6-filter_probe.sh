#!/usr/bin/env bash
# r101-E6 mutation probe v2: include/exclude export-filter semantics, DETERMINISTIC recipe.
# Recipe per arm (fresh project copy):
#   1) godot --headless --path <proj> --import            (materializes .import + .gd.uid)
#   2) godot --headless --path <proj> --export-pack <preset> out/x.pck
#   3) parse raw PCK (GDPC v4, dir-at-tail) and print the entry census
# Usage: bash r101-E6-filter_probe.sh [reps]
set -u
ROOT=/tmp/r101-E6
BASE=$ROOT/base
GODOT=${GODOT:-godot}
REPS=${1:-2}
mkdir -p "$BASE"/{scripts,assets,docs}
printf '[application]\n\nconfig/name="ExportProdS06"\nconfig/features=PackedStringArray("4.7")\n' > "$BASE/project.godot"
printf 'extends Node\nconst MARKER := "alpha"\n' > "$BASE/scripts/alpha.gd"
printf 'extends Node\nconst MARKER := "beta"\n' > "$BASE/scripts/beta.gd"
printf 's06 non-resource text\n' > "$BASE/docs/readme.txt"
printf '{"s06": true}\n' > "$BASE/docs/data.json"
python3 - <<'PY'
import base64
png = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAFklEQVR4nGP8z8DAwMDAxMDAwMDAAAANHQEDasKb6QAAAABJRU5ErkJggg==')
open('/tmp/r101-E6/base/assets/tile.png','wb').write(png)
open('/tmp/r101-E6/base/assets/icon2.png','wb').write(png)
PY
# Pinned import sidecars: the importer does not reliably regenerate texture UIDs
# (r101-E6 observed a uid flip -> 2176-byte pack), so the recipe seeds them.
cat > "$BASE/assets/tile.png.import" <<'EOF'
[remap]

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
EOF
cat > "$BASE/assets/icon2.png.import" <<'EOF'
[remap]

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
EOF

write_presets() {
cat > "$1/export_presets.cfg" <<'EOF'
[preset.0]
name="All"
platform="Linux/X11"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path=""

[preset.0.options]
binary_format/architecture="x86_64"

[preset.1]
name="IncludeGD"
platform="Linux/X11"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter="*.gd"
exclude_filter=""
export_path=""

[preset.1.options]
binary_format/architecture="x86_64"

[preset.2]
name="ExcludePNG"
platform="Linux/X11"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter="*.png"
export_path=""

[preset.2.options]
binary_format/architecture="x86_64"

[preset.3]
name="IncludeTXT"
platform="Linux/X11"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter="*.txt"
exclude_filter=""
export_path=""

[preset.3.options]
binary_format/architecture="x86_64"

[preset.4]
name="ExcludeGD"
platform="Linux/X11"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter="*.gd"
export_path=""

[preset.4.options]
binary_format/architecture="x86_64"

[preset.5]
name="IncludeXyz"
platform="Linux/X11"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter="*.xyz"
exclude_filter=""
export_path=""

[preset.5.options]
binary_format/architecture="x86_64"
EOF
}

parse() {
python3 - "$1" <<'PY'
import struct, hashlib, sys
p = sys.argv[1]
b = open(p,'rb').read()
magic=b[:4]; ver=struct.unpack_from('<I',b,4)[0]
fb=struct.unpack_from('<Q',b,0x18)[0]; doff=struct.unpack_from('<Q',b,0x20)[0]
cnt=struct.unpack_from('<I',b,doff)[0]; off=doff+4
rows=[]
for _ in range(cnt):
    pl=struct.unpack_from('<I',b,off)[0]; off+=4
    path=b[off:off+pl].rstrip(b'\x00').decode(); off+=pl
    o,s=struct.unpack_from('<QQ',b,off); off+=16
    md5=b[off:off+16]; off+=20
    data=b[fb+o:fb+o+s]
    rows.append((path,s,hashlib.sha256(data).hexdigest(),hashlib.md5(data).digest()==md5))
rows.sort()
print(f"PCK bytes={len(b)} magic={magic.decode()} ver={ver} count={cnt} md5ok_all={all(r[3] for r in rows)}")
for path,s,sha,ok in rows:
    print(f"  ENT {path:<52} size={s:<4} sha256={sha}")
print(f"  CENSUS_PATH_SHA256 {hashlib.sha256(chr(10).join(r[0] for r in rows).encode()).hexdigest()}")
print(f"  CENSUS_FULL_SHA256 {hashlib.sha256(chr(10).join(f'{r[0]}|{r[1]}|{r[2]}' for r in rows).encode()).hexdigest()}")
PY
}

for arm in All IncludeGD ExcludePNG IncludeTXT ExcludeGD IncludeXyz; do
  for rep in $(seq 1 "$REPS"); do
    run=$ROOT/v2-$arm-$rep
    rm -rf "$run"; cp -a "$BASE" "$run"; mkdir -p "$run/out"; write_presets "$run"
    ( cd "$run" && "$GODOT" --headless --path . --import > import.log 2>&1 \
        && "$GODOT" --headless --path . --export-pack "$arm" out/x.pck > export.log 2>&1 )
    echo "### ARM=$arm REP=$rep"
    parse "$run/out/x.pck"
    grep -cE "ERROR" "$run/export.log" | sed 's/^/export_error_lines=/'
    sha256sum "$run/out/x.pck" | awk '{print "pck_sha256="$1}'
    rm -rf "$run/.godot/imported" # keep disk pressure low
  done
done
