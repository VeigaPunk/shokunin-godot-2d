import sys, time
def T(lbl): sys.stderr.write(f"W {lbl} {time.time():.4f}\n"); sys.stderr.flush()
T("start")
for i in range(16):
    T(f"pre{i}"); sys.stdout.write("x"*8192); T(f"post{i}")
T("pre16"); sys.stdout.write("x"); T("post16")
time.sleep(1.0)
T("pre-exit")
