# r72-author scratch — reorder arm landing notes

Host: python3.14.7, pygame 2.6.1 / SDL 2.32.72, io.DEFAULT_BUFFER_SIZE=131072.

## Pre-landing dry run (standalone child-program check)

```
buf    wire=b'INJECTEDHEAD  TAIL\n'  head=8  inj=0  tail=14 bytes=19 ret=0   # prefix_reorder
unbuf  wire=b'HEAD INJECTED TAIL\n'  head=0  inj=5  tail=14 bytes=19 ret=0   # midline_splice
env    wire=b'HEAD INJECTED TAIL\n'  head=0  inj=5  tail=14 bytes=19 ret=0   # midline_splice
late   wire=b'HEAD  TAIL\nINJECTED'  head=0  inj=11 tail=6  bytes=19 ret=0   # append
flush  wire=b'' ret=1  -> DEV BUG: sys.stdout.write takes no flush kwarg;
        fixed to write()+flush() -> wire=b'HEAD INJECTED TAIL\n' ret=0        # midline_splice
```

## Battery receipts (all under corpus/live/r72-author/runs/)

- pygame-20261014T144428465749Z/verdicts.json — 55/55 (first landed run)
- pygame-20261014T144447211038Z/verdicts.json — 55/55
- pygame-20261014T144456346523Z/verdicts.json — 55/55

probe.stdout.txt of each run carries the fabricated order on the probe's
OWN fd1 (lines 15-17): `REORDER-CHILD` precedes `REORDER-HEAD` precedes
`REORDER-TAIL` — the reorder the post-exit ARM parser cannot see, pinned
by the raw-wire case `self_wire_reorders`.

## Prior-row byte-stability

- `git diff corpus/fixtures/` = +171 lines, 0 removed/modified lines;
  0 removed CASES rows (checked via diff of case-tuple lines).
- Prior-arm key sets identical to r71 receipt
  corpus/live/runs/pygame-20261014T143255328754Z/probe.stdout.txt;
  only jittered numeric fields differ (dt_*, *_ms, fps/hz) — all 36
  prior cases still PASS under their original pins, 3/3 reps.
