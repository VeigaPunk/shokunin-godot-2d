#!/usr/bin/env bash
# r101 mutation battery runner — executes every mutation script sequentially,
# collects verdicts. Run AFTER the official battery receipts (quiet machine).
# Usage: bash reports/round-101/mutations/run-all-mutations.sh | tee /var/tmp/r101-mutations.log
set -u
cd "$(git rev-parse --show-toplevel)"
OUT=/var/tmp/r101-mutations
mkdir -p "$OUT"
echo "load context: $(uptime | tail -1)"
echo "godot: $(godot --version)"
run() {
  local name="$1"; shift
  echo "===== $name : $* ====="
  timeout 600 "$@" > "$OUT/$name.log" 2>&1
  local rc=$?
  echo "--- exit=$rc; tail: ---"
  tail -6 "$OUT/$name.log"
  echo
}
# MUT seats (canonical 9)
run mut01 python3 reports/round-101/mutations/mut01.py --expect reject --root /var/tmp/r101-mut1
[ -f reports/round-101/mutations/mut02.py ] && run mut02 python3 reports/round-101/mutations/mut02.py --root /var/tmp/r101-mut2
[ -f reports/round-101/mutations/mut03_dead_measure.py ] && run mut03_dead python3 reports/round-101/mutations/mut03_dead_measure.py --root /var/tmp/r101-mut3d
[ -f reports/round-101/mutations/mut03_lattice_dead_measure.py ] && run mut03_lattice python3 reports/round-101/mutations/mut03_lattice_dead_measure.py --root /var/tmp/r101-mut3l
[ -f reports/round-101/mutations/mut03_s10_dead_measure.py ] && run mut03_s10 python3 reports/round-101/mutations/mut03_s10_dead_measure.py --root /var/tmp/r101-mut3s
[ -f reports/round-101/mutations/mut04_runs.sh ] && run mut04 bash reports/round-101/mutations/mut04_runs.sh
[ -f reports/round-101/mutations/mut05.py ] && run mut05 python3 reports/round-101/mutations/mut05.py --root /var/tmp/r101-mut5
[ -f reports/round-101/mutations/mut06_export_launch_timeout.py ] && run mut06 python3 reports/round-101/mutations/mut06_export_launch_timeout.py --root /var/tmp/r101-mut6
[ -f reports/round-101/mutations/mut07.py ] && run mut07 python3 reports/round-101/mutations/mut07.py --root /var/tmp/r101-mut7
[ -f reports/round-101/mutations/mut08.py ] && run mut08 python3 reports/round-101/mutations/mut08.py --root /var/tmp/r101-mut8
[ -f reports/round-101/mutations/mut09.py ] && run mut09 python3 reports/round-101/mutations/mut09.py --root /var/tmp/r101-mut9
# E12's own verify scripts (m_seq-class closure evidence)
[ -f reports/round-101/mutations/r101-E12-verify.py ] && run E12-verify python3 reports/round-101/mutations/r101-E12-verify.py
[ -f reports/round-101/mutations/r101-E12-pins.py ] && run E12-pins python3 reports/round-101/mutations/r101-E12-pins.py
echo "ALL MUTATION RUNS DONE"
