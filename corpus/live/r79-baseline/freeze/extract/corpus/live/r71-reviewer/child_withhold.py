"""r71 reviewer scratch: piped-stdout withholding child (CPython stdio).

Modes (argv[1]):
  flush    : W1 flushed at t0; sleep 120ms; W2 flushed
  buf      : W1 unflushed at t0; sleep 120ms; W2 unflushed (both withheld)
  big      : W1 flushed; single 10KiB unflushed write; sleep 300ms; W2
             unflushed -> tests whether a >8KB mid-run write surfaces early
  edge     : W1 flushed; 8192B unflushed; W2 unflushed; exit -> flush-edge
             boundary check (exactly at default buffer size)

No print(flush=...) sugar: raw sys.stdout.write to control buffering.
"""
import sys
import time


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "buf"
    t0 = time.monotonic()

    def ts():
        return "%.3f" % ((time.monotonic() - t0) * 1000.0)

    out = sys.stdout
    if mode == "flush":
        out.write("W1 t=%s\n" % ts())
        out.flush()
        time.sleep(0.120)
        out.write("W2 t=%s\n" % ts())
        out.flush()
    elif mode == "buf":
        out.write("W1 t=%s\n" % ts())
        time.sleep(0.120)
        out.write("W2 t=%s\n" % ts())
    elif mode == "big":
        out.write("W1 t=%s\n" % ts())
        out.flush()
        out.write("F" * (10 * 1024))
        time.sleep(0.300)
        out.write("\nW2 t=%s\n" % ts())
    elif mode == "edge":
        out.write("W1 t=%s\n" % ts())
        out.flush()
        out.write("F" * 8192)
        out.write("\nW2 t=%s\n" % ts())
    else:
        out.write("UNKNOWN-MODE %s\n" % mode)
    sys.exit(0)


main()
