"""r71 reviewer scratch: buffered-writer-layer accumulation probe.

argv[1] = JSON steps like seq_probe but operates on sys.stdout.buffer.
"""
import json, sys, time
steps = json.loads(sys.argv[1])
out = sys.stdout.buffer
for st in steps:
    op = st[0]
    if op == "w":
        out.write(b"F" * int(st[1]))
    elif op == "wm":
        out.write(st[1].encode())
    elif op == "flush":
        out.flush()
    elif op == "sleep":
        time.sleep(float(st[1]) / 1000.0)
