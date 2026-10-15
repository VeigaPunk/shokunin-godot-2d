"""Scratch: scan the wh-child flush edge. Times first-byte arrival at the
parent for a ladder of payload sizes + drip modes. Not part of battery."""
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
            events.append((round((time.perf_counter()-t0)*1e3, 1), -1, "TIMEOUT"))
            break
        chunk = os.read(p.stdout.fileno(), 1 << 22)
        events.append((round((time.perf_counter()-t0)*1e3, 1), len(chunk), ""))
        if not chunk:
            break
    p.wait()
    fb = events[0] if events else (None, 0, "")
    print(f"{label:28} first_byte_ms={fb[0]} first_bytes={fb[1]} "
          f"events={[(e[0], e[1]) for e in events]} ret={p.returncode}",
          flush=True)


for n in (32768, 65536, 100000, 131000, 131048, 131056, 131060, 131061,
          131062, 131064, 131072, 131080, 131100, 132000, 140000,
          262144, 1048576):
    scan(["--wh-child", str(n)], f"wh N={n}")
for n in (131060, 131061, 131072, 131100):
    scan(["--wh-child", str(n), "--wh-init"], f"wh-init N={n}")
scan(["--wh-drip", "16384,10,30"], "drip 16384x10@30ms")
scan(["--wh-drip", "16384,10,30", "--wh-init"], "drip-init 16384x10@30")
scan(["--wh-drip", "8192,17,15"], "drip 8192x17@15ms")
scan(["--wh-drip", "20000,8,30"], "drip 20000x8@30ms")
