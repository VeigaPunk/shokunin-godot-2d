#!/bin/bash
# r103 W9 second-root independent repro: preset export (--export-release) vs CLI
# pack (--export-pack). Runs the packer under unshare+64M tmpfs /tmp (r101-E0
# EDQUOT mitigation); logs nested output to files; records rc + wall secs.
# Usage: r103-w9-repro.sh <root>   (default /var/tmp/r103c-w9)
BASE=${1:-/var/tmp/r103c-w9}
PROJ=$BASE/proj
OUT=$BASE/out
LOGS=$BASE/logs
rm -rf "$PROJ/.godot" "$OUT"
mkdir -p "$OUT" "$LOGS"
: > "$BASE/results.txt"

RUN() {
  local name=$1; shift
  local t0 t1 rc
  t0=$(date +%s.%N)
  unshare -m --map-root-user /usr/bin/bash -c '
    mount -t tmpfs -o size=64M tmpfs /tmp || exit 97
    cd "$1" || exit 96; shift
    exec "$@"
  ' _ "$PROJ" /usr/bin/godot --headless --path "$PROJ" "$@" >"$LOGS/$name.log" 2>&1
  rc=$?
  t1=$(date +%s.%N)
  printf '%s rc=%d secs=%s\n' "$name" "$rc" "$(awk "BEGIN{printf \"%.2f\", $t1-$t0}")" >> "$BASE/results.txt"
}

RUNCHILD() { # name binary [args...]
  local name=$1; shift
  local t0 t1 rc
  t0=$(date +%s.%N)
  env -u XDG_DATA_HOME HOME="$BASE/homeR" /usr/bin/timeout -k 1 8 "$@" --headless --quit-after 3 >"$LOGS/$name.log" 2>&1
  rc=$?
  t1=$(date +%s.%N)
  printf '%s rc=%d secs=%s\n' "$name" "$rc" "$(awk "BEGIN{printf \"%.2f\", $t1-$t0}")" >> "$BASE/results.txt"
}

mkdir -p "$BASE/homeR"
ls -la "$OUT" > "$LOGS/out_before.txt" 2>&1

RUN s_release_bin   --export-release WDivStock "$OUT/s_bin.x86_64"
RUN s_release_pck   --export-release WDivStock "$OUT/s_pck.pck"
RUN s_cli_pack      --export-pack    WDivStock "$OUT/s_cli.pck"
RUN e_release_bin   --export-release WDivEmbed "$OUT/e_bin.x86_64"
RUN e_release_pck   --export-release WDivEmbed "$OUT/e_pck.pck"
RUN e_cli_pack      --export-pack    WDivEmbed "$OUT/e_cli.pck"
RUN s_cli_as_bin    --export-pack    WDivStock "$OUT/x_bin.x86_64"
RUN s_release_bin2  --export-release WDivStock "$OUT/s_bin2.x86_64"

ls -la "$OUT" > "$LOGS/out_after_all.txt" 2>&1
cat "$BASE/results.txt"
