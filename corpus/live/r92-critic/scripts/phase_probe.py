#!/usr/bin/env python3
"""r92 critic seat instrument: split a crash row's wall time into phases.

Phases (timestamps relative to spawn):
  t_arm       first stdout line ("arm=nullts")            -> engine up, script running
  t_marker    the row's arming diagnostic on stdout       -> crash call imminent
  t_header    "handle_crash: ..." on stderr               -> handler entered
  t_enddump   "-- END OF GDSCRIPT BACKTRACE --"           -> dump finished
  t_exit      process reaped                              -> abort() done
Run: python3 scripts/phase_probe.py <n> [script] [flag]
"""
import pathlib, subprocess, sys, threading, time

SEAT = pathlib.Path(__file__).resolve().parent.parent
PROJ = SEAT / "proj"
n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
script = sys.argv[2] if len(sys.argv) > 2 else "tilemap_lattice.gd"
flag = sys.argv[3] if len(sys.argv) > 3 else "--arm=nullts"

for rep in range(1, n + 1):
    t0 = time.time()
    proc = subprocess.Popen(["godot", "--headless", "--path", str(PROJ),
                             "--script", f"res://{script}", "--", flag],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    marks = {}

    def reader(stream, tag, needles):
        for line in stream:
            t = round(time.time() - t0, 3)
            for name, needle in needles:
                if name not in marks and needle in line:
                    marks[name] = t

    th_out = threading.Thread(target=reader, args=(
        proc.stdout, "out", [("t_arm", "arm="), ("t_marker", "about_to_call_tile_data")]))
    th_err = threading.Thread(target=reader, args=(
        proc.stderr, "err", [("t_header", "handle_crash:"),
                             ("t_enddump", "END OF GDSCRIPT BACKTRACE")]))
    th_out.start(); th_err.start()
    proc.wait()
    t_exit = round(time.time() - t0, 3)
    th_out.join(); th_err.join()
    print(f"rep{rep} rc={proc.returncode} " +
          " ".join(f"{k}={marks.get(k, '-')}" for k in
                   ("t_arm", "t_marker", "t_header", "t_enddump")) +
          f" t_exit={t_exit} startup={marks.get('t_marker', 0)} "
          f"crash_path={round((marks.get('t_enddump', t_exit)) - marks.get('t_marker', 0), 3)} "
          f"post_dump={round(t_exit - marks.get('t_enddump', t_exit), 3)}", flush=True)
