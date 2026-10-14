import os, select, subprocess, sys, time

CHILD = ("import sys,time;"
         "print('MARK-1');"
         "time.sleep(0.10);"
         "sys.stdout.write('B'*9000);"
         "time.sleep(0.10);"
         "print('MARK-2')")

for rep in range(4):
    t0 = time.perf_counter()
    p = subprocess.Popen([sys.executable, "-c", CHILD], stdout=subprocess.PIPE)
    fd = p.stdout.fileno()
    chunks, data = [], b""
    while True:
        r,_,_ = select.select([fd], [], [], 5.0)
        if not r: print("TIMEOUT"); break
        c = os.read(fd, 65536)
        if not c: break
        ms = (time.perf_counter()-t0)*1e3
        chunks.append((round(ms,2), len(c)))
        data += c
    p.wait()
    eof = (time.perf_counter()-t0)*1e3
    def find_ms(needle):
        off = data.find(needle)
        cum = 0
        for ms, n in chunks:
            cum += n
            if off >= 0 and cum > off + len(needle) - 1:
                return ms
        return None
    print(f"rep{rep} chunks={chunks} eof={eof:.1f} mark1_ms={find_ms(b'MARK-1')} mark2_ms={find_ms(b'MARK-2')} alive_at_first={chunks and p.poll() is None or 'n/a'}")
