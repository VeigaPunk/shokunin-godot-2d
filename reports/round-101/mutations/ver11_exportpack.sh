#!/usr/bin/env bash
# VER-11 C1 export-artifact probe: real PCK + executable export on a scratch
# production-shaped project, magic/size/sha256 census, and a --main-pack receipt.
# Deviation note (as ver11_seqforgery.sh): scratch lives in the repo's gitignored
# corpus/live/r101-ver11/ because /tmp returns EDQUOT on this host.
set -u
REPO=/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
SCR=$REPO/corpus/live/r101-ver11/scratch/exportproj
OUT=$REPO/corpus/live/r101-ver11/receipts
GODOT=${GODOT:-godot}
mkdir -p "$SCR/out" "$OUT"

cat >"$SCR/project.godot" <<'EOF'
config_version=5

[application]

config/name="r101-ver11-prod"
run/main_scene="res://main.tscn"
config/features=PackedStringArray("4.7")
EOF
cat >"$SCR/main.tscn" <<'EOF'
[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://main.gd" id="1"]

[node name="Main" type="Node" id="1_main"]
script = ExtResource("1")
EOF
cat >"$SCR/main.gd" <<'EOF'
extends Node

func _ready() -> void:
	print("VER11_PACK_STARTED scene=main")
EOF
sed -e 's/^export_filter=.*/export_filter="all_resources"/' \
    "$REPO/corpus/fixtures/export_presets.cfg" >"$SCR/export_presets.cfg"

{
  date -Is; echo "load: $(uptime)"
  echo "--- export-pack (PCK) run 1"
  "$GODOT" --headless --path "$SCR" --export-pack "Linux/X11" "$SCR/out/prod1.pck" >"$OUT/exp_pack1.out" 2>&1 </dev/null; echo "rc=$?"
  echo "--- export-pack (PCK) run 2 (determinism)"
  "$GODOT" --headless --path "$SCR" --export-pack "Linux/X11" "$SCR/out/prod2.pck" >"$OUT/exp_pack2.out" 2>&1 </dev/null; echo "rc=$?"
  echo "--- export-release (executable+embedded pack) run 1"
  "$GODOT" --headless --path "$SCR" --export-release "Linux/X11" "$SCR/out/prod.x86_64" >"$OUT/exp_exe1.out" 2>&1 </dev/null; echo "rc=$?"
  echo "--- census"
  for f in prod1.pck prod2.pck prod.x86_64; do
    p="$SCR/out/$f"
    if [ -f "$p" ]; then
      printf "%-12s bytes=%-10s sha256=%s magic=%s\n" "$f" "$(stat -c%s "$p")" \
        "$(sha256sum "$p" | cut -d' ' -f1)" "$(head -c4 "$p" | tr -d '\0' | cat -v)"
    else
      printf "%-12s ABSENT\n" "$f"
    fi
  done
  echo "--- pck determinism (cmp prod1 vs prod2)"
  cmp "$SCR/out/prod1.pck" "$SCR/out/prod2.pck" && echo "cmp=identical" || echo "cmp=differ"
  echo "--- main-pack launch receipt"
  "$GODOT" --headless --main-pack "$SCR/out/prod1.pck" --quit-after 3 >"$OUT/exp_launch.out" 2>&1 </dev/null; echo "rc=$?"
  grep -n "VER11_PACK_STARTED" "$OUT/exp_launch.out" || echo "no receipt line"
  echo "--- export output tail (row predicate tokens)"
  grep -n "\[ DONE \]\|savepack" "$OUT/exp_pack1.out" | tail -3
  date -Is
} 2>&1 | tee "$OUT/manifest3.txt"
