import os, select, subprocess, sys, time

# 200000 > 131072 (io.DEFAULT_BUFFER_SIZE on this build)
CHILD = ("import sys,time;"
         "print('MARK-1');"
         "time.sleep(0.10);"
         "sys.stdout.write('B'*200000);"
         "time.sleep(0.10);"
         "print('MARK-2')")

for rep in range(3):
    t0 = time.perf_counter()
    p = subprocess.Popen([sys.executable, "-c", CHILD], stdout=subprocess.PIPE)
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
    def find_ms(needle):
        off = data.find(needle); cum = 0
        for ms, n in chunks:
            cum += n
            if off >= 0 and cum > off + len(needle) - 1: return ms
        return None
    print(f"rep{rep} chunks={chunks} mark1_ms={find_ms(b'MARK-1')} mark2_ms={find_ms(b'MARK-2')} total={len(data)}")
