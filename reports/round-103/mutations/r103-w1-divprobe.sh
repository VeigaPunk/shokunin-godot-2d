#!/bin/bash
# r103-W1 / C1 — reproducible divergence probe: `--export-pack` (CLI pack-only) vs
# preset export (`--export-release`) on ONE scratch project, Godot 4.7.2.stable.
#
# Regenerates the W1 shard's observation table (reports/round-103/r103-w1.md) from scratch.
# Usage:  bash r103-w1-divprobe.sh [/var/tmp/r103c-w1probe]
# Never touches the repo project, never runs run_battery.py, never /tmp (EDQUOT).
set -u
ROOT="${1:-/var/tmp/r103c-w1probe}"
G="${GODOT:-/usr/bin/godot}"
P="$ROOT/proj"; O="$ROOT/out"; L="$ROOT/logs"; E="$ROOT/emptyhome"
rm -rf "$ROOT"; mkdir -p "$P" "$O" "$L" "$E"

cat > "$P/project.godot" <<'EOF'
config_version=5
[application]
config/name="w1probe"
run/main_scene="res://main.tscn"
config/features=PackedStringArray("4.7")
EOF
cat > "$P/main.tscn" <<'EOF'
[gd_scene format=3 uid="uid://bw1probe0001"]
[node name="Main" type="Node"]
EOF
mkdir -p "$P/res/sub"; printf 'w1 note\n' > "$P/res/sub/note.txt"
cat > "$P/export_presets.cfg" <<'EOF'
[preset.0]
name="P0"
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
binary_format/embed_pck=false
binary_format/architecture="x86_64"

[preset.1]
name="P1Emb"
platform="Linux/X11"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path=""
[preset.1.options]
binary_format/embed_pck=true
binary_format/architecture="x86_64"

[preset.2]
name="PFilt"
platform="Linux/X11"
runnable=false
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="resources"
include_filter="res/sub/*"
exclude_filter=""
export_path=""
[preset.2.options]
binary_format/embed_pck=false
binary_format/architecture="x86_64"
EOF
"$G" --headless --path "$P" --import >"$L/import.log" 2>&1

arm() { local tag="$1"; shift; "$@" >"$L/$tag.log" 2>&1; printf '%s\trc=%d\n' "$tag" "$?"; }
NOTPL=(env HOME="$E" XDG_DATA_HOME="$E/.local/share" XDG_CONFIG_HOME="$E/.config" "$G")

arm a1_pack_pck      "$G" --headless --path "$P" --export-pack "P0" "$O/a1.pck"
arm a2_pack_zip      "$G" --headless --path "$P" --export-pack "P0" "$O/a2.zip"
arm a3_pack_badext   "$G" --headless --path "$P" --export-pack "P0" "$O/a3.bin"
arm a4_pack_nopreset "$G" --headless --path "$P" --export-pack "NoSuchPreset" "$O/a4.pck"
arm a5_pack_notpl    "${NOTPL[@]}" --headless --path "$P" --export-pack "P0" "$O/a5.pck"
arm a6_pack_embed    "$G" --headless --path "$P" --export-pack "P1Emb" "$O/a6.pck"
arm c1_pack_filt     "$G" --headless --path "$P" --export-pack "PFilt" "$O/c1.pck"
arm b1_rel_full      "$G" --headless --path "$P" --export-release "P0" "$O/b1.x86_64"
arm b2_rel_nopreset  "$G" --headless --path "$P" --export-release "NoSuchPreset" "$O/b2.x86_64"
arm b3_rel_notpl     "${NOTPL[@]}" --headless --path "$P" --export-release "P0" "$O/b3.x86_64"
arm b4_rel_embed     "$G" --headless --path "$P" --export-release "P1Emb" "$O/b4.x86_64"
arm c2_rel_filt      "$G" --headless --path "$P" --export-release "PFilt" "$O/c2.x86_64"

echo "--- artifacts ---"; ls -l "$O"
echo "--- sha256 ---"; ( cd "$O" && sha256sum * 2>/dev/null )

python3 - "$O" <<'PY'
import sys, os, struct, hashlib
O = sys.argv[1]
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()
def parse(d):
    magic, ver, vmaj, vmin, flags, extra = struct.unpack_from("<6I", d, 0)
    fb, do = struct.unpack_from("<QQ", d, 24)
    n, = struct.unpack_from("<I", d, do)
    p = do + 4; ents = []
    for _ in range(n):
        ln, = struct.unpack_from("<I", d, p); p += 4
        nm = d[p:p+ln].split(b'\0')[0].decode(); p += ln
        off, size = struct.unpack_from("<QQ", d, p); p += 16
        md5 = d[p:p+16].hex(); p += 16
        fl, = struct.unpack_from("<I", d, p); p += 4
        ents.append((nm, off, size, fl, md5))
    return dict(magic=magic, ver=ver, vmaj=vmaj, vmin=vmin, flags=flags, extra=extra,
                fb=fb, do=do, n=n, ents=ents, end=p, size=len(d))
for name in sorted(os.listdir(O)):
    p = os.path.join(O, name); d = open(p, 'rb').read()
    head = d[:4]
    if head == b"GDPC":
        r = parse(d)
        print(f"{name} {r['size']}B packfmt={r['ver']} ver={r['vmaj']}.{r['vmin']} flags={r['flags']} extra={r['extra']}"
              f" file_base={r['fb']} dir_off={r['do']} count={r['n']} dir_end={r['end']} entries={sorted(e[0] for e in r['ents'])}")
    elif head == b"PK\x03\x04":
        import zipfile
        z = zipfile.ZipFile(p)
        print(f"{name} {d.__len__()}B ZIP fmt={ver if False else ''} entries={sorted(z.namelist())}")
    else:
        print(f"{name} {len(d)}B head={head.hex()} sha={sha(p)[:16]} last4={d[-4:]!r}")
        if d[-4:] == b"GDPC":
            fsz, = struct.unpack_from("<Q", d, len(d) - 12)
            print(f"   embedded trailer: pack_size={fsz} pack_start={len(d) - fsz - 12} template_end_expected")
print("identity a1==a5:", sha(os.path.join(O, "a1.pck")) == sha(os.path.join(O, "a5.pck")),
      "a1==a6:", sha(os.path.join(O, "a1.pck")) == sha(os.path.join(O, "a6.pck")),
      "a1==b1.pck:", sha(os.path.join(O, "a1.pck")) == sha(os.path.join(O, "b1.pck")),
      "c1==c2.pck:", sha(os.path.join(O, "c1.pck")) == sha(os.path.join(O, "c2.pck")))
PY
echo "--- key error lines ---"
grep -h -E "ERROR:|Invalid export preset|doesn't end with|No export template" "$L"/a3*.log "$L"/a4*.log "$L"/b3*.log | sort -u | head -12
