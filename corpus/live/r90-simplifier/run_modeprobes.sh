#!/usr/bin/env bash
# r90-simplifier independent boundary-fold probes on the LANDED fixture (ee20575).
#   mode tps30 : real 30 tps via project setting [physics] common/physics_ticks_per_second=30
#   mode dummy : real Dummy engine via [physics] 2d/physics_engine="Dummy"
# Launch shape = battery shape (timeout -s KILL 25, --headless, --path proj, --script res://rb_lattice.gd -- --arm=...).
# 2 fresh reps per cell. Receipts under corpus/live/r90-simplifier/.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
FIX="/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/fixtures"

for mode in tps30 dummy; do
  dir="$HERE/proj_$mode"
  rm -rf "$dir"; mkdir -p "$dir"
  {
    printf '%s\n' '[application]' 'config/name="MechanicOneShotTest"' \
      'config/features=PackedStringArray("4.7")' '' '[physics]'
    [ "$mode" = tps30 ] && printf 'common/physics_ticks_per_second=30\n'
    [ "$mode" = dummy ] && printf '2d/physics_engine="Dummy"\n'
  } > "$dir/project.godot"
  cp -f "$FIX/rb_lattice.gd" "$FIX/rb_watch.gd" "$dir/"
  mkdir -p "$HERE/runs-$mode"
done

run() { # mode arm [extra flags...]
  local mode="$1" arm="$2"; shift 2
  for k in 1 2; do
    timeout -s KILL 25 godot --headless --path "$HERE/proj_$mode" \
      --script res://rb_lattice.gd -- "--arm=$arm" "$@" \
      > "$HERE/runs-$mode/$arm.rep$k.out" 2> "$HERE/runs-$mode/$arm.rep$k.err"
    echo $? > "$HERE/runs-$mode/$arm.rep$k.rc"
  done
}

for mode in tps30 dummy; do
  for a in props comread comrefuse gravity damp order write impulse impedge contacts; do
    run "$mode" "$a"
  done
  run "$mode" freezelock --frames=120
  run "$mode" lag --frames=30
done
echo "DONE: $(ls "$HERE"/runs-tps30/*.out | wc -l) tps30 + $(ls "$HERE"/runs-dummy/*.out | wc -l) dummy receipts"
