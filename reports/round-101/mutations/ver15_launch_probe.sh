#!/usr/bin/env bash
# ver15_launch_probe.sh — r101 VER-15 distillation: `--main-pack` launch probes with
# fail-closed rc guards, settings preflight and load-safe timeouts.
#
# Usage:  bash ver15_launch_probe.sh [SCRATCH]      (default /var/tmp/r101-ver15)
# Env:    GODOT=godot
# Needs:  godot 4.7.2.stable + installed export templates (linux_release.x86_64).
#
# Why this shape (all measured in reports/round-101/r101-ver15.md):
#   * rc=0 does NOT mean the pack booted: a settings-less pack (project.binary size 0),
#     a missing/zero/bad-magic/dir pack and even a runtime script error all exit 0.
#   * a pack whose scene calls get_tree().quit(7) makes the process exit rc=7.
#   * `--quit-after N` yields exactly N TICK lines (+1 BOOT) — usable as a frame receipt.
#   * `--quit-after 0`/`abc` never quits: every launch below is timeout-bounded (rc 137 = FAIL).
#   * exports are intermittently settings-less on this host; every pack is preflighted
#     (and re-exported, max 4 tries) before any launch receipt is trusted.
#   * receipts carry OS.get_process_id(); pins must normalize `pid=<N>` or omit pid.
set -u
B=${1:-/var/tmp/r101-ver15}
case "$B" in /var/tmp/r101-*|/tmp/r101-*) ;; *) echo "refusing scratch dir '$B' (must match /{,var/}tmp/r101-*)"; exit 2;; esac
G=${GODOT:-godot}
HERE="$(cd "$(dirname "$0")" && pwd)"
PREFLIGHT="$HERE/ver15_pack_preflight.py"
PROJ=$B/proj; PACKS=$B/packs; O=$B/runs/probe; CONC=$B/runs/conc
rm -rf "$B"; mkdir -p "$PROJ" "$PACKS" "$O" "$CONC"                     # fresh scratch every run
FAILS=0; PASSES=0
say() { printf '%s\n' "$*"; }

mk_proj() { # $1 dir, $2 name, $3 main scene, $4 scene script (heredoc body via file below)
  local d=$1
  mkdir -p "$d"
  cat > "$d/export_presets.cfg" <<'CFG'
[preset.0]
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
encrypt_pck=false
encrypt_directory=false
[preset.0.options]
binary_format/architecture="x86_64"
CFG
  printf 'config_version=5\n\n[application]\nconfig/name="%s"\nrun/main_scene="%s"\n\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n' "$2" "$3" > "$d/project.godot"
}
mk_scene() { # $1 dir, $2 stem, $3 extra-quit-code (0|7)
  cat > "$1/$2.gd" <<EOF
extends Node
var frames := 0
func _ready() -> void:
	print("[ver15] BOOT")
func _process(_delta: float) -> void:
	frames += 1
	print("[ver15] TICK frame=%d" % frames)
	if $3 > 0 and frames >= 3:
		get_tree().quit($3)
EOF
  cat > "$1/$2.tscn" <<EOF
[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://$2.gd" id="1_s"]

[node name="Main" type="Node"]
script = ExtResource("1_s")
EOF
}
export_preflighted() { # $1 projdir, $2 out.pck ; retry until preflight passes (max 4)
  local t
  for t in 1 2 3 4; do
    timeout -s KILL 120 "$G" --headless --path "$1" --export-pack "Linux/X11" "$2" \
      > "$O/export_$(basename "$2" .pck)_$t.out" 2> "$O/export_$(basename "$2" .pck)_$t.err"
    if python3 "$PREFLIGHT" "$2" 2>/dev/null | grep -q '^PASS'; then
      say "  export $(basename "$2"): preflight PASS on try $t"
      return 0
    fi
    say "  export $(basename "$2"): try $t produced a settings-less pack, retrying"
  done
  say "  export $(basename "$2"): FAILED preflight 4x"; FAILS=$((FAILS+1)); return 1
}
norm() { sed -E 's/pid=[0-9]+/pid=<N>/'; }
launch() { # $1 tag $2 cwd ; rest = args ; writes $O/<tag>.{out,err,rc,ms,norm}
  local tag=$1 cwd=$2; shift 2
  local t0 rc
  t0=$(date +%s%N)
  ( cd "$cwd" && timeout -s KILL 25 "$G" "$@" > "$O/$tag.out" 2> "$O/$tag.err" ); rc=$?
  echo "$rc" > "$O/$tag.rc"
  echo $(( ($(date +%s%N) - t0) / 1000000 )) > "$O/$tag.ms"
  norm < "$O/$tag.out" > "$O/$tag.norm"
}
judge() { # $1 tag $2 expected_rc $3 expected_boot_lines $4 boot_min (>=)
  local tag=$1 erc=$2 ebl=$3 rc bl
  rc=$(cat "$O/$tag.rc")
  bl=$(grep -c '\[ver15\]' "$O/$tag.norm" || true)
  if [ "$rc" != "$erc" ]; then say "FAIL $tag rc=$rc expected=$erc"; FAILS=$((FAILS+1)); return 1; fi
  if [ "$bl" -lt "$ebl" ]; then say "FAIL $tag boot_lines=$bl expected>=$ebl"; FAILS=$((FAILS+1)); return 1; fi
  if grep -q 'Corrupted header in binary project.binary' "$O/$tag.err"; then
    say "FAIL $tag settings-less pack banner on stderr"; FAILS=$((FAILS+1)); return 1; fi
  say "PASS $tag rc=$rc boot=$bl ms=$(cat "$O/$tag.ms")"; PASSES=$((PASSES+1))
}

say "== host: load=$(cut -d' ' -f1-3 /proc/loadavg) godot=$($G --version 2>&1 | tail -1)"
mk_proj "$PROJ" "ver15-probe" "res://main.tscn"; mk_scene "$PROJ" main 0
mk_proj "$B/proj_quit7" "ver15-quit7" "res://self7.tscn"; mk_scene "$B/proj_quit7" self7 7
export_preflighted "$PROJ" "$PACKS/ok.pck" || true
export_preflighted "$B/proj_quit7" "$PACKS/quit7.pck" || true
: > "$PACKS/zero.pck"; head -c 900 /dev/urandom > "$PACKS/badmagic.pck"
head -c $(( $(stat -c%s "$PACKS/ok.pck") - 1036 )) "$PACKS/ok.pck" > "$PACKS/trunc.pck"

say "== happy path / frame receipts"
launch q1 "$B" --headless --main-pack "$PACKS/ok.pck" --quit-after 1; judge q1 0 2
launch q3 "$B" --headless --main-pack "$PACKS/ok.pck" --quit-after 3; judge q3 0 4
launch q10 "$B" --headless --main-pack "$PACKS/ok.pck" --quit-after 10; judge q10 0 11
launch ff30 "$B" --headless --main-pack "$PACKS/ok.pck" --fixed-fps 30 --quit-after 3; judge ff30 0 4
launch unk "$B" --headless --main-pack "$PACKS/ok.pck" --ver15-nonsense --quit-after 3; judge unk 0 4

say "== pack-controlled exit code (no --quit-after)"
launch self7 "$B" --headless --main-pack "$PACKS/quit7.pck"; judge self7 7 4

say "== malformed inputs: rc=0, no receipt (must not be read as success)"
launch miss "$B" --headless --main-pack "$PACKS/NOPE.pck" --quit-after 3; judge miss 0 0
launch zero "$B" --headless --main-pack "$PACKS/zero.pck" --quit-after 3; judge zero 0 0
launch magic "$B" --headless --main-pack "$PACKS/badmagic.pck" --quit-after 3; judge magic 0 0
launch dir "$B" --headless --main-pack "$PACKS" --quit-after 3; judge dir 0 0
launch trunc "$B" --headless --main-pack "$PACKS/trunc.pck" --quit-after 3; judge trunc 0 0

say "== timeout envelope: a never-quitting pack is killed (rc=137), receipt still present"
launch hang "$B" --headless --main-pack "$PACKS/ok.pck" --quit-after 0; judge hang 137 1

say "== CLI guard"
launch noarg "$B" --headless --main-pack; judge noarg 1 0

say "== concurrency: 8 parallel launches, receipts must stay exact"
pids=""
for i in 1 2 3 4 5 6 7 8; do
  ( launch "conc_$i" "$B" --headless --main-pack "$PACKS/ok.pck" --quit-after 3 ) & pids="$pids $!"
done
wait $pids 2>/dev/null || true
for i in 1 2 3 4 5 6 7 8; do judge "conc_$i" 0 4; done

say "== preflight negative fixture: hand-made settings-less pack is refused"
python3 "$PREFLIGHT" "$PACKS/zero.pck" "$PACKS/trunc.pck" | sed 's/^/  /'
if python3 "$PREFLIGHT" "$PACKS/zero.pck" >/dev/null 2>&1; then say "FAIL preflight accepted zero.pck"; FAILS=$((FAILS+1)); else say "PASS preflight refuses zero.pck"; PASSES=$((PASSES+1)); fi
if python3 "$PREFLIGHT" "$PACKS/ok.pck" >/dev/null 2>&1; then say "PASS preflight accepts ok.pck"; PASSES=$((PASSES+1)); else say "FAIL preflight rejected ok.pck"; FAILS=$((FAILS+1)); fi

say "== done: $PASSES PASS, $FAILS FAIL | load=$(cut -d' ' -f1-3 /proc/loadavg)"
[ "$FAILS" -eq 0 ] || exit 1
