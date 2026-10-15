#!/usr/bin/env bash
# r92-boundary positive control.
#
# The r91 boundary seat proved the r91 scout's `nav_lattice.gd` frame-count row is
# --fixed-fps-sensitive (its "2-4 frame" change law becomes "never within 24 frames").
# This seat's harness must be able to SEE such a difference; otherwise the
# byte-identity of the 13 r92 rows across fixed-fps modes would be a dead-probe
# artifact. So: run the r91 scout's frozen `sync` arm (sha256 efb496e5…) through the
# same launcher shape, default vs --fixed-fps 120 / 30.
#
# Launch: godot --headless [--fixed-fps N] --path proj --script res://r91scout_nav_lattice.gd -- --arm=sync
set -u
cd "$(dirname "$0")"
GODOT=${GODOT:-godot}
BOUND=${BOUND:-25}
mkdir -p runs/control
cp -f ../r91-scout/probes/nav_lattice.gd proj/r91scout_nav_lattice.gd
sha256sum ../r91-scout/probes/nav_lattice.gd | tee runs/control/control_probe.sha256

run() { # name ff... reps
  local name="$1" reps="$2"; shift 2
  local i rc
  for i in $(seq 1 "$reps"); do
    timeout -s KILL "$BOUND" "$GODOT" --headless "$@" --path proj \
      --script res://r91scout_nav_lattice.gd -- --arm=sync \
      > "runs/control/$name.rep$i.out" 2> "runs/control/$name.rep$i.err"
    rc=$?
    echo "$rc" > "runs/control/$name.rep$i.rc"
    echo "$name rep$i rc=$rc $(grep -h '^PASS' runs/control/$name.rep$i.out | head -c 200)"
  done
}

run ctl_def 3
run ctl_ff120 3 --fixed-fps 120
run ctl_ff30 3 --fixed-fps 30
echo "loadavg=$(cat /proc/loadavg)"
