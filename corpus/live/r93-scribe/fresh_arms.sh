#!/usr/bin/env bash
# r93-scribe fresh-arm receipts on committed bytes.
# Launch shape = production battery: godot --headless --path <proj> --script res://<fixture> -- --arm=<a>
# with an isolated XDG_DATA_HOME. 17 arms x 3 reps.
set -u
REPO=/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
OUT=$REPO/corpus/live/r93-scribe/fresh
PROJ=/home/vgpnk/r93-fresh-proj
mkdir -p "$OUT" "$PROJ"
cp -f /home/vgpnk/r93-committed-extract/corpus/fixtures/anim_lattice.gd "$PROJ/"
cp -f /home/vgpnk/r93-committed-extract/corpus/fixtures/r93b_anim.gd "$PROJ/"
cp -f /home/vgpnk/r93-committed-extract/corpus/fixtures/project.godot "$PROJ/"
mkdir -p "$OUT/xdg-data"
export XDG_DATA_HOME="$OUT/xdg-data"

ARMS_ANIM="census tweenval tweenval_grid animtrack tweenstep tweenchain tweenproc animseek animmethod animblend animproc"
ARMS_R93B="clock manual_inv frame deferred purity blend"

run_one() {
  local fixture=$1 arm=$2 rep=$3
  local tag="$fixture.$arm.rep$rep"
  timeout -s KILL 25 /usr/bin/godot --headless --path "$PROJ" \
      --script "res://$fixture.gd" -- --arm="$arm" \
      > "$OUT/$tag.out" 2> "$OUT/$tag.err"
  echo $? > "$OUT/$tag.rc"
}

for rep in 1 2 3; do
  for arm in $ARMS_ANIM; do run_one anim_lattice "$arm" "$rep"; done
  for arm in $ARMS_R93B; do run_one r93b_anim "$arm" "$rep"; done
done
echo "fresh arms done: $(ls "$OUT"/*.out | wc -l) out files"
