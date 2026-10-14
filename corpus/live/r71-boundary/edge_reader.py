import os, select, subprocess, sys, time
t0 = time.time()
p = subprocess.Popen([sys.executable, "edge_manual.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
fds = {p.stdout.fileno(): "OUT", p.stderr.fileno(): "ERR"}
open_fds = set(fds)
while open_fds:
    ready,_,_ = select.select(list(open_fds), [], [], 5.0)
    for fd in ready:
        d = os.read(fd, 1<<20)
        t = time.time() - t0
        if d:
            print(f"{t:8.4f} {fds[fd]} len={len(d)} head={d[:20]!r}")
        else:
            open_fds.discard(fd)
p.wait()
print("exit", time.time()-t0)
