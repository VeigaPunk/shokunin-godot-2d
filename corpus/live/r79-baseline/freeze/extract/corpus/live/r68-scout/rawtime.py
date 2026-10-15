import subprocess, time, sys, os, re, shutil
ms = sys.argv[1]; s = float(ms)/1000
src = open('proj/pristine.gd').read()
src2 = src.replace('"sleep 0.08;', f'"sleep {s};')
assert f'sleep {s};' in src2
open('proj/descendant_pipe_probe.gd','w').write(src2)
t0=time.monotonic()
p = subprocess.Popen(['/usr/bin/godot','--headless','--path','proj',
 '--script','res://descendant_pipe_probe.gd','--','--spawn-midlineforge'],
 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
os.set_blocking(p.stdout.fileno(), False)
while True:
    try: b=os.read(p.stdout.fileno(),65536)
    except BlockingIOError:
        if p.poll() is not None:
            try: b=os.read(p.stdout.fileno(),65536)
            except BlockingIOError: break
            if not b: break
            continue
        time.sleep(0.001); continue
    if not b: break
    print(f"{(time.monotonic()-t0)*1000:8.1f}ms {b!r}")
p.wait()
