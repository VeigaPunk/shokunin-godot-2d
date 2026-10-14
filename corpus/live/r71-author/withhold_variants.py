import os, select, subprocess, sys, time

VARIANTS = {
  # A: single big str write via sys.stdout.write
  "A_str9000": "import sys,time;print('MARK-1');time.sleep(0.10);sys.stdout.write('B'*9000);time.sleep(0.10);print('MARK-2')",
  # B: single big print
  "B_print9000": "import sys,time;print('MARK-1');time.sleep(0.10);print('B'*9000);time.sleep(0.10);print('MARK-2')",
  # C: raw buffer write of 9000 bytes
  "C_rawbytes9000": "import sys,time;print('MARK-1');time.sleep(0.10);sys.stdout.buffer.write(b'B'*9000);time.sleep(0.10);print('MARK-2')",
  # D: cumulative small writes crossing 8KB (100 x 100B)
  "D_cumul100x100": "import sys,time;print('MARK-1');time.sleep(0.10);[sys.stdout.write('C'*100) for _ in range(100)];time.sleep(0.10);print('MARK-2')",
  # E: big write then more small writes (does post-big content re-buffer?)
  "E_big_then_small": "import sys,time;sys.stdout.buffer.write(b'B'*9000);time.sleep(0.10);print('AFTER-BIG');time.sleep(0.05);print('MARK-2')",
}

def run(child):
    t0 = time.perf_counter()
    p = subprocess.Popen([sys.executable, "-c", child], stdout=subprocess.PIPE)
    fd = p.stdout.fileno()
    chunks, data = [], b""
    while True:
        r,_,_ = select.select([fd], [], [], 5.0)
        if not r: chunks.append(("TIMEOUT",0)); break
        c = os.read(fd, 65536)
        if not c: break
        chunks.append((round((time.perf_counter()-t0)*1e3,1), len(c)))
        data += c
    p.wait()
    return chunks, data

for name, child in VARIANTS.items():
    chunks, data = run(child)
    print(name, "chunks:", chunks, "total:", len(data))
