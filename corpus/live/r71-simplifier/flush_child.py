"""Child writer for the flush-edge probe (r71 simplifier scratch).

Emits three lines to stdout with NO explicit flush, on a pipe:
  CH-HEAD                 at t0
  CH-BULK <n bytes>       at t0+300ms
  CH-TAIL                 at t0+600ms
then exits (exit triggers CPython's final stdout flush).

Usage: python3 flush_child.py <bulk_payload_bytes>
"""
import sys
import time

n = int(sys.argv[1]) if len(sys.argv) > 1 else 0
print("CH-HEAD")
time.sleep(0.30)
print("CH-BULK " + ("x" * n))
time.sleep(0.30)
print("CH-TAIL")
