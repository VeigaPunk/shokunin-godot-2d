#!/bin/bash
# r102-crit1-attack.sh — reproducible C1 critic probes (round 102, seat KEY=C1).
# Read-only wrt the lane repo: everything happens under $R102C1_ROOT
# (default /var/tmp/r102-crit1-attack; /tmp is EDQUOT-prone on this host).
#
# Probes (each prints an [A]..[E] label + observed bytes):
#   A  refusal subject-tail census in the stock template binary (strings)
#   B  launch matrix: embed vs stock export, bare-binary error class, refusals,
#      forged wrapper artifacts (marker + refusal)
#   C  forged-trailer artifact vs the pinned census fields (size-bound vacuity)
#   D  bare-binary linger: bounded run + PATH-neutral control + zenity census
#   E  filter case ground truth: artifact/engine-side pack listing
#
# Requirements: godot 4.7.2 on PATH or $GODOT_BIN, linux_release.x86_64 template
# (or $GODOT_TEMPLATE), unshare with user namespaces for the EDQUOT-safe exports.
set -u

ROOT="${R102C1_ROOT:-/var/tmp/r102-crit1-attack}"
GODOT="${GODOT_BIN:-/usr/bin/godot}"
TPL="${GODOT_TEMPLATE:-$HOME/.local/share/godot/export_templates/4.7.2.stable/linux_release.x86_64}"
mkdir -p "$ROOT/proj/res" "$ROOT/out" "$ROOT/iso" "$ROOT/iso2" "$ROOT/forge" "$ROOT/logs" "$ROOT/nobin"

echo "[A] refusal subject variants in template (count) and editor (must be 0)"
for b in "$TPL" /usr/bin/godot; do
  printf '%s: ' "$b"
  grep -ac "compiled without support for path overrides" "$b" || true
done
echo "[A] same-tail subjects in template:"
strings -n 8 "$TPL" | grep "was specified on the command line, but this Godot binary was compiled without support" || true

cat > "$ROOT/proj/project.godot" <<'EOF'
config_version=5

[application]

config/name="Crit1Probe"
run/main_scene="res://main.tscn"
config/features=PackedStringArray("4.7")
EOF
cat > "$ROOT/proj/main.gd" <<'EOF'
extends Node


func _ready() -> void:
	print("CRIT1_MARKER=1 pid=%d" % OS.get_process_id())
	print("CRIT1_EXE=%s" % OS.get_executable_path())
	print("CRIT1_EXISTS up.TXT=%s down.txt=%s" % [FileAccess.file_exists("res://up.TXT"), FileAccess.file_exists("res://down.txt")])
	print("CRIT1_ROOTFILES %s" % ",".join(DirAccess.get_files_at("res://")))


var _frame := 0


func _process(_delta: float) -> void:
	_frame += 1
	print("CRIT1 frame=%d" % _frame)
EOF
cat > "$ROOT/proj/main.tscn" <<'EOF'
[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://main.gd" id="1_main"]

[node name="Main" type="Node"]
script = ExtResource("1_main")
EOF
cat > "$ROOT/proj/export_presets.cfg" <<'EOF'
[preset.0]
name="plain"
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
binary_format/embed_pck=false

[preset.1]
name="emb"
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
binary_format/architecture="x86_64"
binary_format/embed_pck=true

[preset.2]
name="casep"
platform="Linux/X11"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter="*.txt"
exclude_filter=""
export_path=""

[preset.2.options]
binary_format/architecture="x86_64"
binary_format/embed_pck=false
EOF
printf 'UPPER-CASE-TXT\n' > "$ROOT/proj/up.TXT"
printf 'lower-case-txt\n' > "$ROOT/proj/down.txt"

echo "[B] exports (unshare + private /tmp to dodge the packer's EDQUOT temp write)"
unshare -m --map-root-user /bin/sh -c "mount -t tmpfs -o size=64M tmpfs /tmp || exit 97
cd $ROOT
$GODOT --headless --path proj --import > logs/import.log 2>&1; echo import_rc=\$?
$GODOT --headless --path proj --export-release plain $ROOT/out/plain.x86_64 > logs/exp_plain.log 2>&1; echo plain_rc=\$?
$GODOT --headless --path proj --export-release emb $ROOT/out/emb.x86_64 > logs/exp_emb.log 2>&1; echo emb_rc=\$?
$GODOT --headless --path proj --export-pack casep $ROOT/out/casep.pck > logs/exp_casep.log 2>&1; echo casep_rc=\$?"
stat -c '%n %s' "$ROOT/out"/* 2>/dev/null
cmp -s "$ROOT/out/plain.x86_64" "$TPL" && echo "[B] plain.x86_64 == template byte-identical" || echo "[B] plain != template"
sha256sum "$ROOT/out/plain.x86_64" "$TPL" | awk '{print $1}' | uniq -c

cp "$ROOT/out/emb.x86_64" "$ROOT/iso/" && cp "$ROOT/out/plain.x86_64" "$ROOT/iso2/"
run() { local n="$1"; shift; "$@" > "$ROOT/logs/$n.out" 2> "$ROOT/logs/$n.err"; local rc=$?; echo "[B] $n rc=$rc out=$(head -1 "$ROOT/logs/$n.out")"; }
( cd "$ROOT/iso" && run emb_q3 ./emb.x86_64 --headless --quit-after 3 )
( cd "$ROOT/iso2" && run bare_q2 /usr/bin/timeout 2 ./plain.x86_64 --headless --quit-after 2 )
( cd "$ROOT/out" && run sidecar ./plain.x86_64 --headless --quit-after 2 )
( cd "$ROOT/out" && run mainpack ./plain.x86_64 --headless --main-pack "$ROOT/out/plain.pck" --quit-after 2 )
( cd "$ROOT/out" && run pathrefuse ./plain.x86_64 --headless --path "$ROOT/proj" --quit-after 2 )
( cd / && run editor_mainpack "$GODOT" --headless --main-pack "$ROOT/out/plain.pck" --quit-after 2 )
echo "[B] mainpack stderr first line:"; head -1 "$ROOT/logs/mainpack.err"
echo "[B] pathrefuse stderr first line:"; head -1 "$ROOT/logs/pathrefuse.err"

cat > "$ROOT/forge/fake_marker.x86_64" <<'EOF'
#!/bin/sh
echo "CRIT1_MARKER=1 pid=$$"
echo "CRIT1_EXE=$0"
echo "CRIT1 frame=1"
echo "CRIT1 frame=2"
echo "CRIT1 frame=3"
exit 0
EOF
cat > "$ROOT/forge/fake_refusal.x86_64" <<'EOF'
#!/bin/sh
echo 'ERROR: --main-pack was specified on the command line, but this Godot binary was compiled without support for path overrides. Aborting.' >&2
echo 'To be able to use it, use the `disable_path_overrides=no` SCons option when compiling Godot.' >&2
exit 1
EOF
chmod +x "$ROOT/forge/fake_marker.x86_64" "$ROOT/forge/fake_refusal.x86_64"
run forge_marker "$ROOT/forge/fake_marker.x86_64"
run forge_refusal "$ROOT/forge/fake_refusal.x86_64"

echo "[C] forged trailer: template + 'GDPC' (passes tail-magic census, cannot boot)"
cat "$TPL" > "$ROOT/forge/trailer_fake.x86_64" && printf 'GDPC' >> "$ROOT/forge/trailer_fake.x86_64" && chmod +x "$ROOT/forge/trailer_fake.x86_64"
stat -c '%n %s' "$ROOT/forge/trailer_fake.x86_64"
S=$(date +%s%N); /usr/bin/timeout 3 "$ROOT/forge/trailer_fake.x86_64" --headless --quit-after 2 > "$ROOT/logs/fake_boot.out" 2> "$ROOT/logs/fake_boot.err"; RC=$?; E=$(date +%s%N)
echo "[C] forged boot rc=$RC ms=$(( (E-S)/1000000 )) stdout_bytes=$(wc -c < "$ROOT/logs/fake_boot.out") marker=$(grep -c CRIT1_MARKER "$ROOT/logs/fake_boot.out" || true)"
python3 - "$ROOT/forge/trailer_fake.x86_64" "$TPL" <<'PYEOF'
import struct, sys
d = open(sys.argv[1],'rb').read(); tpl = open(sys.argv[2],'rb').read()
t12 = d[-12:]
pack_size = struct.unpack('<Q', t12[0:8])[0]
gdpc = struct.unpack('<I', t12[8:12])[0] == 0x43504447
print("[C] census fields: artifacts=1 sidecar_pck=0 tail_magic=%s binary_bytes=%d" % (d[-4:].hex(), len(d)))
print("[C] s02 algebra: trailer_gdpc=%s pack_size=%d size_consistent=%s" % (gdpc, pack_size, len(d)-12-pack_size == len(tpl)))
PYEOF

echo "[D] bare-binary linger mechanism (zenity alert child) + PATH-neutral control"
S=$(date +%s%N); env PATH="$ROOT/nobin" /usr/bin/timeout 6 "$ROOT/iso2/plain.x86_64" --headless --quit-after 2 > "$ROOT/logs/pathneutral.out" 2> "$ROOT/logs/pathneutral.err"; RC=$?; E=$(date +%s%N)
echo "[D] PATH-neutral rc=$RC ms=$(( (E-S)/1000000 )) first_stderr=$(head -1 "$ROOT/logs/pathneutral.err")"
echo "[D] zenity census after probes (orphans from the raw bare run):"
ps -eo pid,ppid,etime,args | grep -x ".*/zenity .*" | grep -v grep || echo "[D] none"
pgrep -x zenity | while read -r z; do kill -9 "$z" && echo "[D] pruned orphan zenity pid=$z"; done

echo "[E] filter case ground truth via engine-side pack listing"
/usr/bin/timeout 30 "$GODOT" --headless --main-pack "$ROOT/out/casep.pck" --quit-after 3 > "$ROOT/logs/casep_run.out" 2> "$ROOT/logs/casep_run.err"; echo "[E] casep run rc=$?"
grep -E "CRIT1_(EXISTS|ROOTFILES)" "$ROOT/logs/casep_run.out" || true
grep -aq "res://up.TXT" "$ROOT/out/casep.pck" && echo "[E] raw bytes: res://up.TXT present" || echo "[E] raw bytes: no res://up.TXT run (extra-file entries are stored bare; res://-grep censuses miss them)"
grep -aq "up.TXT" "$ROOT/out/casep.pck" && echo "[E] raw bytes: bare up.TXT entry present" || echo "[E] raw bytes: bare up.TXT absent"
echo "done."
