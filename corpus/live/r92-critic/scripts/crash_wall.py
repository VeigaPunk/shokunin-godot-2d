#!/usr/bin/env python3
"""r92 critic seat instrument: measure WHERE the nullts crash row's wall time goes.

Launches `godot --headless --path proj --script res://tilemap_lattice.gd -- --arm=nullts`
exactly like the battery (subprocess, capture_output=True, text=True) and polls the
process tree so the wall time can be split into:
  * godot's own lifetime (crash handler prints the dump, then abort), and
  * the lifetime of any descendant the crash handler spawned (symbolizer),
    which is what keeps the capture pipes open after godot is gone.
"""
import subprocess, sys, time, pathlib, os

SEAT = pathlib.Path(__file__).resolve().parent.parent
PROJ = SEAT / "proj"
cmd = ["godot", "--headless", "--path", str(PROJ), "--script",
       "res://tilemap_lattice.gd", "--", "--arm=nullts"]


def descendants(root):
    kids = {}
    for entry in pathlib.Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            stat = (entry / "stat").read_text()
        except OSError:
            continue
        ppid = int(stat.rsplit(")", 1)[1].split()[1])
        kids.setdefault(ppid, []).append(int(entry.name))
    out, stack = [], [root]
    while stack:
        p = stack.pop()
        for k in kids.get(p, []):
            out.append(k)
            stack.append(k)
    return out


def comm(pid):
    try:
        return (pathlib.Path(f"/proc/{pid}/comm")).read_text().strip()
    except OSError:
        return "?"


t0 = time.time()
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
godot_pid = proc.pid
seen, last_alive, last_wall = set(), {}, {}
while True:
    for p in descendants(godot_pid):
        if p not in seen:
            seen.add(p)
            last_alive[p] = (comm(p), round(time.time() - t0, 3))
        else:
            last_alive[p] = (last_alive[p][0], round(time.time() - t0, 3))
    if proc.poll() is not None:
        break
    time.sleep(0.02)
godot_gone = round(time.time() - t0, 3)
# godot has exited: drain the pipes exactly like subprocess.run does
out, err = proc.communicate()
pipes_eof = round(time.time() - t0, 3)
# how long did descendants survive past godot's exit?
after = {}
for p in seen:
    if pathlib.Path(f"/proc/{p}").exists():
        after[p] = last_alive[p]
print(f"godot_exit={godot_gone}s pipes_eof={pipes_eof}s "
      f"pipe_wait={round(pipes_eof - godot_gone, 3)}s descendants={len(seen)}")
for p, (c, last) in sorted(after.items()):
    print(f"  descendant {p} {c} last_seen={last}s")
print(f"rc={proc.returncode} stdout_bytes={len(out)} stderr_bytes={len(err)}")
