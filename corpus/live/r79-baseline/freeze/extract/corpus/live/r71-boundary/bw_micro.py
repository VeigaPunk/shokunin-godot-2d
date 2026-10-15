"""micro-test: does BufferedWriter flush when a write arrives at a full buffer?"""
import io, os, sys, time, threading

def run(B, first, second, label):
    r, w = os.pipe()
    raw = io.FileIO(w, "wb", closefd=False)
    bw = io.BufferedWriter(raw, buffer_size=B)
    t0 = time.time()
    events = []
    def reader():
        while True:
            d = os.read(r, 1 << 20)
            events.append((round((time.time()-t0)*1e3, 3), len(d)))
            if not d: break
    th = threading.Thread(target=reader, daemon=True); th.start()
    bw.write(b"x" * first)
    t1 = time.time()
    bw.write(b"y" * second)
    t2 = time.time()
    time.sleep(0.4)
    t3 = time.time()
    bw.flush()
    t4 = time.time()
    time.sleep(0.1)
    os.close(w); os.close(r)
    print(f"{label}: B={B} first={first} second={second} events={events} "
          f"t1-t0={ (t1-t0)*1e3:.2f} t2-t1={(t2-t1)*1e3:.2f} "
          f"t4-t2={(t4-t2)*1e3:.2f}")

run(131072, 131072, 1, "exact-then-1")
run(131072, 65536, 65537, "half-then-over")
run(131072, 131071, 1, "lo-then-1")
run(8192, 8192, 1, "8k-exact-then-1")
run(8192, 8191, 1, "8k-lo-then-1")
