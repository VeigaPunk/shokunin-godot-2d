import subprocess, time, sys, os, re
ms = sys.argv[1]
s = float(ms)/1000
src = open('proj/descendant_pipe_probe.gd').read()
src2 = re.sub(r'sleep [0-9.]+;', f'sleep {s};', src, count=1)
open('proj/descendant_pipe_probe.gd','w').write(src2)
t0 = time.monotonic()
p = subprocess.Popen(['/usr/bin/godot','--headless','--path','proj',
    '--script','res://descendant_pipe_probe.gd','--','--spawn-midlineforge'],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
os.set_blocking(p.stdout.fileno(), False)
buf=b''
while True:
    try:
        b = os.read(p.stdout.fileno(), 65536)
    except BlockingIOError:
        time.sleep(0.002); 
        if p.poll() is not None:
            try:
                b = os.read(p.stdout.fileno(), 65536)
            except BlockingIOError:
                b=b''
            if not b: break
            continue
        continue
    if not b: break
    buf+=b
    print(f"{(time.monotonic()-t0)*1000:8.1f}ms  {b!r}")
p.wait()
