#!/usr/bin/env bash
# r96-boundary matrix driver.
#   bash run_matrix.sh quiet|load|ff1|ff30|ff120
# Runs (a) the r96 scout's FROZEN 13 arms and (b) the r96b_* boundary arms under one
# condition family.  Every launch is `timeout -s KILL 25` (brief: timeouts <= 25 s KILL).
# Hogs: `load` starts 16 own `yes` processes and kills only those PIDs (never pkill).
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-25}
BATCH=${1:?batch}
FF=""
HOGS=0
SREPS=3   # scout-arm reps
PREPS=2   # boundary-arm reps
CORE=0    # 1 = boundary CORE subset only (ff1/ff120)
case "$BATCH" in
  quiet)  FF="";              HOGS=0;  SREPS=3; PREPS=2; CORE=0 ;;
  load)   FF="";              HOGS=16; SREPS=2; PREPS=2; CORE=0 ;;
  ff1)    FF="--fixed-fps 1"; HOGS=0;  SREPS=1; PREPS=1; CORE=1 ;;
  ff30)   FF="--fixed-fps 30";HOGS=0;  SREPS=1; PREPS=1; CORE=0 ;;
  ff120)  FF="--fixed-fps 120";HOGS=0; SREPS=1; PREPS=1; CORE=1 ;;
  *) echo "unknown batch $BATCH"; exit 2 ;;
esac
mkdir -p "runs/$BATCH"
cp -f probes/*.gd proj/

SCENE_ARMS="census pack_basic ownership formats det uid takeover cache subres extres editstate refuse edges"

# boundary arms: script:arm
ALL_ARMS="r96b_seq:extseq r96b_seq:extpin r96b_seq:extbundle r96b_seq:extgen r96b_seq:minimal \
r96b_var:rich r96b_var:conn r96b_var:groups r96b_var:meta r96b_var:lever r96b_var:idstat \
r96b_id:finger0 r96b_id:fingerB r96b_id:seqA2 r96b_id:seqAB2 r96b_id:seqAA3 r96b_id:seq2obj \
r96b_id:extshift r96b_id:subsame r96b_id:subpath r96b_id:subextra0 r96b_id:subextra3 \
r96b_id:twoext r96b_id:mint_two r96b_id:subsamepath r96b_id:subcontent r96b_id:extother \
r96b_cache:deep_reuse r96b_cache:deep_replace r96b_cache:deep_ignore r96b_cache:deep_repl_deep \
r96b_cache:deep_ign_deep r96b_cache:repl_uncached r96b_cache:reuse_delete r96b_cache:reuse_delay \
r96b_cache:ignoredeep r96b_cache:threaded \
r96b_phase:ph0 r96b_phase:ph1 r96b_phase:ph2 r96b_phase:ph5 r96b_phase:ph30 \
r96b_phase:pph0 r96b_phase:pph1 r96b_phase:pph2 r96b_phase:pph5 r96b_phase:pph30"

# the decisive subset (ff1/ff120): the three attacked claims + the tick-phase probe
CORE_ARMS="r96b_seq:extseq r96b_seq:extpin r96b_seq:extbundle r96b_seq:minimal \
r96b_var:rich r96b_var:conn \
r96b_id:seqA2 r96b_id:seqAB2 r96b_id:seq2obj r96b_id:extshift r96b_id:mint_two \
r96b_id:subsame r96b_id:subpath r96b_id:twoext r96b_id:extother \
r96b_cache:deep_reuse r96b_cache:deep_replace r96b_cache:deep_ignore \
r96b_cache:deep_repl_deep r96b_cache:deep_ign_deep \
r96b_phase:ph0 r96b_phase:ph5 r96b_phase:pph5"

note() { printf '%s\n' "$1" >> "runs/$BATCH/summary.txt"; }
: > "runs/$BATCH/summary.txt"
note "batch=$BATCH ff='$FF' hogs=$HOGS scout_reps=$SREPS probe_reps=$PREPS core=$CORE godot=$(timeout 20 "$GODOT" --version 2>&1 | tail -1) started=$(date -u +%Y-%m-%dT%H:%M:%SZ) loadavg=$(cat /proc/loadavg | cut -d' ' -f1-3)"

HOG_PIDS=""
if [ "$HOGS" -gt 0 ]; then
  for i in $(seq 1 "$HOGS"); do yes > /dev/null & HOG_PIDS="$HOG_PIDS $!"; done
  note "own_hogs_started=$HOGS pids=$(echo $HOG_PIDS | tr ' ' ',')"
  sleep 2
fi

for arm in $SCENE_ARMS; do
  for i in $(seq 1 "$SREPS"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless $FF --path proj --script res://scene_io_lattice.gd -- \
      "--arm=$arm" > "runs/$BATCH/scout_$arm.rep$i.out" 2> "runs/$BATCH/scout_$arm.rep$i.err"
    echo "$?" > "runs/$BATCH/scout_$arm.rep$i.rc"
  done
  note "scout_$arm rc=[$(cat runs/$BATCH/scout_$arm.rep*.rc | tr '\n' ' ')]"
done

ARMS="$ALL_ARMS"
[ "$CORE" = "1" ] && ARMS="$CORE_ARMS"
for spec in $ARMS; do
  script="${spec%%:*}"; arm="${spec##*:}"
  for i in $(seq 1 "$PREPS"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless $FF --path proj --script "res://$script.gd" -- \
      "--arm=$arm" > "runs/$BATCH/${script}_$arm.rep$i.out" 2> "runs/$BATCH/${script}_$arm.rep$i.err"
    echo "$?" > "runs/$BATCH/${script}_$arm.rep$i.rc"
  done
done
note "probe_arms_done=$(echo $ARMS | wc -w) reps=$PREPS"

if [ -n "$HOG_PIDS" ]; then
  killed=0
  for pid in $HOG_PIDS; do kill -9 "$pid" 2>/dev/null && killed=$((killed+1)); done
  note "own_hogs_killed=$killed"
fi
note "finished=$(date -u +%Y-%m-%dT%H:%M:%SZ) loadavg=$(cat /proc/loadavg | cut -d' ' -f1-3)"
cat "runs/$BATCH/summary.txt"
echo "--- stray own launches ---"
pgrep -fa "r96b_|scene_io_lattice" || echo none
