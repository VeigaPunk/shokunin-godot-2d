"""Scratch scan 2: bound the write-size threshold between 'absorbed past
capacity' (small writes grow the buffer) and 'flush pending' (large
writes release it). Drip chunk sizes crossing the 131072 buffer."""
import os, select, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy",
           PYGAME_HIDE_SUPPORT_PROMPT="1")


def scan(argv, label):
    t0 = time.perf_counter()
    p = subprocess.Popen([sys.executable,
                          os.path.join(HERE, "pygame_probe.py")] + argv,
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                         env=ENV)
    events = []
    while True:
        r, _, _ = select.select([p.stdout], [], [], 8.0)
        if not r:
            events.append((round((time.perf_counter()-t0)*1e3, 1), -1, "T"))
            break
        chunk = os.read(p.stdout.fileno(), 1 << 22)
        events.append((round((time.perf_counter()-t0)*1e3, 1), len(chunk), ""))
        if not chunk:
            break
    p.wait()
    fb = events[0] if events else (None, 0, "")
    tot = sum(e[1] for e in events if e[1] > 0)
    print(f"{label:30} first_byte_ms={fb[0]} first_bytes={fb[1]} "
          f"total={tot} events={[(e[0], e[1]) for e in events]}",
          flush=True)


for spec in ("512,257,4", "1024,129,4", "2048,65,6", "4096,33,8",
             "6144,22,10", "12288,11,10"):
    scan(["--wh-drip", spec], f"drip {spec}")
