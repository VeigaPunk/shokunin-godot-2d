"""r71 simplifier scratch: chunk-level controls for the flush-edge probe.

Answers, with raw chunk sizes + timestamps:
  1. `-u` child (unbuffered): does the parent see each line at its own slot?
  2. unflushed child, 1MB single write: does a >>buffer write surface early?
  3. child using os.write(1, ...) (raw fd): early visibility control.
"""
import os
import select
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

CASES = [
    ("u_flag_small", [sys.executable, "-u", "-c",
                      "import time;print('A1');time.sleep(0.3);print('A2');"
                      "time.sleep(0.3);print('A3')"]),
    ("buf_small", [sys.executable, "-c",
                   "import time;print('A1');time.sleep(0.3);print('A2');"
                   "time.sleep(0.3);print('A3')"]),
    ("buf_1MB_one_print", [sys.executable, "-c",
                           "import time;print('A1');time.sleep(0.3);"
                           "print('B'*1048576);time.sleep(0.3);print('A3')"]),
    ("buf_9KB_one_print", [sys.executable, "-c",
                           "import time;print('A1');time.sleep(0.3);"
                           "print('B'*9216);time.sleep(0.3);print('A3')"]),
    ("raw_os_write_9B", [sys.executable, "-c",
                         "import os,time;os.write(1,b'A1\\n');time.sleep(0.3);"
                         "os.write(1,b'B'*9216+b'\\n');time.sleep(0.3);"
                         "os.write(1,b'A3\\n')"]),
]


def run(argv):
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)
    t0 = time.perf_counter()
    chunks = []
    fd = proc.stdout
    while True:
        ready, _, _ = select.select([fd], [], [], 5.0)
        if not ready:
            break
        data = os.read(fd.fileno(), 1 << 20)
        if not data:
            break
        chunks.append(((time.perf_counter() - t0) * 1e3, len(data),
                       data[:24]))
    proc.wait()
    exit_ms = (time.perf_counter() - t0) * 1e3
    return chunks, exit_ms, proc.returncode


def main():
    for name, argv in CASES:
        chunks, exit_ms, rc = run(argv)
        print(f"== {name}: chunks={len(chunks)} exit_ms={exit_ms:.1f} rc={rc}")
        for ms, size, head in chunks:
            print(f"   t={ms:8.1f}ms size={size:>8} head={head!r}")


if __name__ == "__main__":
    main()
