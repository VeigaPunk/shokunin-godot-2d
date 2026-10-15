"""r72-reviewer: probe-level reorder ground truth.

Simulates the probe-level design: a process whose stdout is captured by a
subprocess.run(capture_output=True) parent writes HEAD unflushed, spawns a
descendant writing into inherited fd1, writes TAIL flushed. The captured
byte order is the observable.
"""
import subprocess
import sys

SNIP = (
    "import sys,os;"
    "sys.stdout.write('R72-HEAD ');"
    "{flush}"
    "os.system(\"printf 'R72-INJ '>>/dev/null; printf 'R72-INJ'\");"
    "sys.stdout.write('R72-TAIL');"
    "print()"
)


def run(extra, flush_stmt):
    src = SNIP.format(flush=flush_stmt)
    p = subprocess.run([sys.executable] + extra + ["-c", src],
                       capture_output=True, text=True, timeout=10)
    out = p.stdout
    return (out, out.find("R72-HEAD"), out.find("R72-INJ"), out.find("R72-TAIL"),
            p.returncode)


for name, extra, flush_stmt in [
        ("buffered", [], ""),
        ("u", ["-u"], ""),
        ("flushed", [], "sys.stdout.flush();")]:
    out, h, i, t, rc = run(extra, flush_stmt)
    topo = "reorder" if (i >= 0 and h >= 0 and i < h) else "splice"
    print(f"PROBE-LEVEL {name:9s} | out={out!r} head={h} inj={i} tail={t} "
          f"topology={topo} ret={rc}")
