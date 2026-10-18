#!/usr/bin/env bash
# VER-11 arm-2/3 probes: PASS-dialect extra line, and pinned-line substitution.
# Same deviation note as ver11_seqforgery.sh (/tmp EDQUOT -> repo gitignored scratch).
set -u
REPO=/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
SCR=$REPO/corpus/live/r101-ver11/scratch
OUT=$REPO/corpus/live/r101-ver11/receipts
GODOT=${GODOT:-godot}

run() {
  local name=$1; shift; local dir=$1; shift
  "$GODOT" --headless --path "$dir" --script "res://$1" -- "${@:2}" \
     >"$OUT/$name.out" 2>"$OUT/$name.err" </dev/null
  local rc=$?
  echo "$name rc=$rc stdout_sha=$(sha256sum <"$OUT/$name.out" | cut -d' ' -f1) stderr_sha=$(sha256sum <"$OUT/$name.err" | cut -d' ' -f1)"
}

{
  date -Is; echo "load: $(uptime)"
  echo "--- arm extra_pass: extra PASS-dialect cell line (mut01 forged_cell dialect)"
  run seq_extra_pass_clean0 "$SCR/extra_pass" r100b_seq.gd --clean=0
  echo "--- arm substitute: pinned cursor line replaced by a forged value"
  run seq_subst_clean1 "$SCR/subst" r100b_seq.gd --clean=1
  date -Is
} 2>&1 | tee "$OUT/manifest2.txt"
