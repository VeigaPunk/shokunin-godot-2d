#!/bin/bash
# r101-VER-10 — checker validation matrix.
# Runs reports/round-101/mutations/ver10_receipt_stability.py against real stored
# battery runs and against single-token forgeries of them. Mutants live in
# /var/tmp/r101-ver10/mut-* (scratch, never committed). Read-only on the repo.
#
# Expectations:
#   t0 self-pair ............ IDENTICAL            rc=0
#   t1 r25 true pair ........ ACCEPTED-VARIANCE    rc=0  (float_drift only)
#   t2 forged signature ..... REJECT               rc=1  (claim diff)
#   t3 forged receipt digit . REJECT               rc=1  (unclassified)
#   t4 stamp-only edit ...... ACCEPTED-VARIANCE    rc=0  (stamp_path)
#   t5 pid-only edit ........ ACCEPTED-VARIANCE    rc=0  (pid_token)
#   t6 r24 mismatched rows .. NOT-A-PAIR           rc=2
#   t7 r88 fold harness ..... NOT-A-PAIR or REJECT rc>=1 (different harness bytes)
#
#   HOST=... CHECKER=... bash ver10_mutation_matrix.sh
set -u
HOST="${HOST:-/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin}"
CHECKER="${CHECKER:-$HOST/reports/round-101/mutations/ver10_receipt_stability.py}"
WORK="${WORK:-/var/tmp/r101-ver10}"
R25A="$HOST/corpus/live/r25-export-executor/absolute/20261013T012803175660Z"
R25B="$HOST/corpus/live/r25-export-executor/absolute/20261013T012840117471Z"
R88A="$HOST/corpus/live/r88-author/runs1/20261015T181519396144Z"
R88B="$HOST/corpus/live/r88-author/runs2/20261015T181910437115Z"
R88F="$HOST/corpus/live/r88-simplifier/runs-after/20261015T183321965855Z"
R24A="$HOST/corpus/live/r24-bottom-executor/20261013T011935920849Z"
R24B="$HOST/corpus/live/r24-bottom-executor/20261013T012020522893Z"
mkdir -p "$WORK"
pass=0; fail=0

expect() { # label expected_rc command...
  local label="$1" want="$2"; shift 2
  local out; out="$("$@" 2>&1)"; local rc=$?
  local got; got="$(printf '%s\n' "$out" | head -1)"
  if [ "$rc" = "$want" ] || { [ "$want" = "ge1" ] && [ "$rc" -ge 1 ]; }; then
    echo "OK   $label  rc=$rc  | $got"
    pass=$((pass+1))
  else
    echo "FAIL $label  rc=$rc (want $want)  | $got"
    echo "$out" | head -8 | sed 's/^/       /'
    fail=$((fail+1))
  fi
}

forge_signature() { # single char in one row's pinned signature
  mkdir -p "$WORK/mut-sig"
  python3 - "$R25A/verdicts.json" "$WORK/mut-sig/verdicts.json" <<'EOF'
import json,sys
d=json.load(open(sys.argv[1]))
for r in d["results"]:
    if r["case"]=="camera_follow":
        r["signature"]=r["signature"].replace("moved=true","moved=fals",1)
json.dump(d,open(sys.argv[2],"w"),indent=2)
EOF
}
forge_receipt() { # single char in one row's receipt line
  mkdir -p "$WORK/mut-rec"
  python3 - "$R25A/verdicts.json" "$WORK/mut-rec/verdicts.json" <<'EOF'
import json,sys
d=json.load(open(sys.argv[1]))
for r in d["results"]:
    if r["case"]=="tween_flash":
        r["output"]=[l.replace("frames_observed=62","frames_observed=63",1) for l in r["output"]]
json.dump(d,open(sys.argv[2],"w"),indent=2)
EOF
}
forge_stamp() { # stamp token only (path prefix preserved)
  mkdir -p "$WORK/mut-stamp"
  python3 - "$R25A/verdicts.json" "$WORK/mut-stamp/verdicts.json" <<'EOF'
import json,re,sys
d=json.load(open(sys.argv[1]))
d["scratch"]=re.sub(r"\d{8}T\d{6}\d{6}Z","20990101T000000000000Z",d["scratch"])
json.dump(d,open(sys.argv[2],"w"),indent=2)
EOF
}
forge_pid() { # pid token only (r88 pair has pid-bearing rows)
  mkdir -p "$WORK/mut-pid"
  python3 - "$R88A/verdicts.json" "$WORK/mut-pid/verdicts.json" <<'EOF'
import json,sys
d=json.load(open(sys.argv[1]))
for r in d["results"]:
    if r["case"]=="save_process_reader":
        r["output"]=[l.replace("pid=1643675","pid=1643676",1) for l in r["output"]]
json.dump(d,open(sys.argv[2],"w"),indent=2)
EOF
}
forge_dropped_line() { # delete one receipt line -> not a masking case
  mkdir -p "$WORK/mut-drop"
  python3 - "$R25A/verdicts.json" "$WORK/mut-drop/verdicts.json" <<'EOF'
import json,sys
d=json.load(open(sys.argv[1]))
for r in d["results"]:
    if r["case"]=="camera_follow":
        r["output"]=r["output"][:-1]
json.dump(d,open(sys.argv[2],"w"),indent=2)
EOF
}
forge_swapped_lines() { # pure permutation of merged-stream lines
  mkdir -p "$WORK/mut-swap"
  python3 - "$R25A/verdicts.json" "$WORK/mut-swap/verdicts.json" <<'EOF'
import json,sys
d=json.load(open(sys.argv[1]))
done=False
for r in d["results"]:
    o=r.get("output") or []
    for i in range(min(3,len(o)-1)):
        if o[i] != o[i+1]:
            o=o[:i]+[o[i+1],o[i]]+o[i+2:]
            r["output"]=o; done=True; print("swapped",r["case"],"lines",i,i+1); break
    if done: break
assert done, "no swappable row found"
json.dump(d,open(sys.argv[2],"w"),indent=2)
EOF
}

echo "== checker validation matrix  ($(date -u +%FT%TZ)) =="
expect "t0 self-pair"            0   python3 "$CHECKER" "$R25A" "$R25A"
expect "t1 r25 true pair"        0   python3 "$CHECKER" "$R25A" "$R25B"
forge_signature
expect "t2 forged signature"     1   python3 "$CHECKER" "$R25A" "$WORK/mut-sig"
forge_receipt
expect "t3 forged receipt digit" 1   python3 "$CHECKER" "$R25A" "$WORK/mut-rec"
forge_stamp
expect "t4 stamp-only edit"      0   python3 "$CHECKER" "$R25A" "$WORK/mut-stamp"
forge_pid
expect "t5 pid-only edit"        0   python3 "$CHECKER" "$R88A" "$WORK/mut-pid"
forge_dropped_line
expect "t8 dropped receipt line" 1   python3 "$CHECKER" "$R25A" "$WORK/mut-drop"
forge_swapped_lines
expect "t9 swapped lines"        0   python3 "$CHECKER" "$R25A" "$WORK/mut-swap"
expect "t6 r24 mismatched rows"  2   python3 "$CHECKER" "$R24A" "$R24B"
expect "t7 r88 fold harness"     ge1 python3 "$CHECKER" "$R88A" "$R88F"
echo "== pass=$pass fail=$fail =="
[ "$fail" = 0 ]
