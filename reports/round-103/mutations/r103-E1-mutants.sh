#!/usr/bin/env bash
# r103-E1 mutant replay — discrimination evidence for corpus/fixtures/export_div_s01.gd.
#
# Each mutant is a ONE-TOKEN sed over a scratch COPY of the fixture (the repo
# file is never modified) and must flip its row from PASS to FAIL:
#
#   m1 pack arm, output extension .pck -> .zip         (row 1, container law)
#   m2 pack arm, --export-pack -> --export-release     (row 1, data-only law)
#   m3 ext  arm, --export-release -> --export-pack     (row 3, extension law)
#   m4 Stock preset embed_pck=false -> true            (row 4, sidecar law)
#   m5 Embed preset embed_pck=true -> false            (row 5, trailer law)
#   m6 zip  arm, output extension .zip -> .pck         (row 2, format law)
#
# Usage: reports/round-103/mutations/r103-E1-mutants.sh [repo_root]
# Never runs run_battery.py; scratch under /var/tmp/r103c-E1 (or $E1_SCRATCH).
set -u
REPO="${1:-$(cd "$(dirname "$0")/../../.." && pwd)}"
S="${E1_SCRATCH:-/var/tmp/r103c-E1}"
FX="$REPO/corpus/fixtures"
mkdir -p "$S/mut"

mk() { mkdir -p "$S/mut/$1"; cp "$FX/export_div_s01.gd" "$FX/project.godot" "$FX/export_presets.cfg" "$S/mut/$1/"; }

mk m1; sed -i 's/"pack", PRESET_EMBED, "cli.pck"/"pack", PRESET_EMBED, "cli.zip"/'              "$S/mut/m1/export_div_s01.gd"
mk m2; sed -i 's/var pck := _export_pack("pack"/var pck := _export_release("pack"/'              "$S/mut/m2/export_div_s01.gd"
mk m3; sed -i 's/var release := _export_release("ext_release"/var release := _export_pack("ext_release"/' "$S/mut/m3/export_div_s01.gd"
mk m4; sed -i 's|binary_format/embed_pck=false|binary_format/embed_pck=true|'                    "$S/mut/m4/export_div_s01.gd"
mk m5; sed -i 's|binary_format/embed_pck=true|binary_format/embed_pck=false|'                    "$S/mut/m5/export_div_s01.gd"
mk m6; sed -i 's/"zip_zip", PRESET_EMBED, "cli.zip"/"zip_zip", PRESET_EMBED, "cli.pck"/'         "$S/mut/m6/export_div_s01.gd"

declare -A ARM=( [m1]=pack [m2]=pack [m3]=ext [m4]=ident [m5]=embed [m6]=zip )
for m in m1 m2 m3 m4 m5 m6; do
  EXPORT_DIV_ROOT="$S/mx_$m" timeout 60 "${GODOT:-godot}" --headless --path "$S/mut/$m" \
    --script res://export_div_s01.gd -- --arm="${ARM[$m]}" > "$S/mut_$m.out" 2>&1
  rc=$?
  line=$(grep -E "^(PASS|FAIL) export_div" "$S/mut_$m.out" | tail -1)
  verdict=BAD
  [ "$rc" -eq 1 ] && case "$line" in FAIL*) verdict=OK;; esac
  printf '%s arm=%-5s rc=%d %s %s\n' "$m" "${ARM[$m]}" "$rc" "$verdict" "$line"
done
