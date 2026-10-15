# game-dev-2d round 72 — author (seat: author; host: devin)

## Declared move (verbatim)

"MOVE (depth): add `reorder` arm to pygame_probe + battery cases — a
spawned descendant writing into inherited fd1 mid-window; pin: buffered
child -> prefix/reorder topology; flushed/-u child -> midline splice
(Godot/LOVE topology). Claim: the fabricated byte ORDER is a
language-layer property (buffering mode), the seam is spawn-layer —
composition, two mechanisms, one window family."

"AUTHOR: implement in tracked fixture(s), self-verify, author report.
Insertion-only; prior rows byte-stable."

## Landed changes

- `corpus/fixtures/pygame_probe.py` (+103/-1: +102 new reorder lines + the reviewer-fold `env=CHILD_ENV` line on popen_arm):
  `reorder_arm()` + three child-program constants + five spawned cells
  + one self cell, appended after `pump` before `pygame.quit()`:
  - `reorder_buf` — buffered `python3 -c` child: writes `HEAD `
    (withheld), `os.system('printf INJECTED >&1')` descendant into
    inherited fd1, ` TAIL\n` (withheld), exit.
  - `reorder_unbuf` — same source under `-u`.
  - `reorder_flush` — HEAD write + explicit `sys.stdout.flush()` before
    the spawn (window closed by hand).
  - `reorder_env` — buffered source under `PYTHONUNBUFFERED=1` env.
  - `reorder_late` — backgrounded descendant `(sleep 0.30; printf
    INJECTED >&1) &` writes ~300ms after the parent's flush closed the
    window at ~t=0 (parent held to 600ms); the inside-vs-after-window
    axis of the xconnector arm shape.
  - `reorder_self` — raw `REORDER-HEAD\n` / `REORDER-CHILD\n` /
    `REORDER-TAIL\n` markers on the probe's OWN fd1 plus a metadata ARM
    line (`fd1_isatty`, `bufsize`, `descendant`). The wire topology
    itself is only visible downstream, so the battery judges it from
    the captured stdout.
  - Children are plain `python3`, same rule as `withhold_*`: the claim
    is language-layer, the subject must not import pygame. `CHILD_ENV`
    (PYTHONUNBUFFERED-stripped) is reused for the buffered cells.
- `corpus/fixtures/pygame_battery.py` (+71 lines, insertion-only):
  - r72 lattice paragraph in the docstring.
  - 18 appended CASES rows (`rord_*`, `self_*`) — exact pins on
    `topology`, `head_at`, `injected_at`, `tail_at`, `wire_bytes`,
    `ret`, `bufsize`; no prior row touched (0 removed case lines in
    `git diff`).
  - `RAW_CASES` + a raw-wire check: marker order is measured on the
    captured stdout itself (`reorder_self` key `wire_topology`) because
    the fabricated order is invisible to the post-exit ARM parser.
  - `run_process` now pops `PYTHONUNBUFFERED` from the probe env — the
    self-wire pin requires the probe block-buffered on our pipe; same
    hygiene `CHILD_ENV` already applies to spawned children. No effect
    on prior rows (ARM lines were always `flush=True`; only jittered
    timing keys could shift, all bound-pinned).

## Measured result (55/55 PASS, 3 stable reps)

Verdict on the claim — **CONFIRMED, and the composition reproduces on
the fixture's own wire**:

| cell | delivered wire | topology |
|---|---|---|
| `reorder_buf` | `INJECTEDHEAD  TAIL\n` | **prefix_reorder** (inj=0 < head=8) |
| `reorder_unbuf` (`-u`) | `HEAD INJECTED TAIL\n` | midline_splice |
| `reorder_flush` | `HEAD INJECTED TAIL\n` | midline_splice |
| `reorder_env` (`PYTHONUNBUFFERED=1`) | `HEAD INJECTED TAIL\n` | midline_splice |
| `reorder_late` | `HEAD  TAIL\nINJECTED` | append |
| `reorder_self` (probe's own fd1) | `REORDER-CHILD` before `REORDER-HEAD` before `REORDER-TAIL` | **prefix_reorder** |

- Same 19 bytes on every spawned wire — only the order moves
  (`wire_bytes=19` pinned on all cells). The fabricated ORDER is the
  language layer's (buffering mode); the seam is the spawn layer's
  (fd1 inheritance). Composition of two already-landed mechanisms, one
  window family — as claimed.
- `reorder_late` pins the window's temporal bound: a descendant landing
  after the flush appends honestly — fabrication requires the write to
  arrive while bytes are withheld.
- The `reorder_self` wire demonstrates the xconnector-flagged hazard on
  the real capture path: `probe.stdout.txt` lines 15–17 read
  `REORDER-CHILD`, `REORDER-HEAD`, `REORDER-TAIL`. Any *streaming*
  consumer of these ARM lines sees reordered bytes; the post-exit
  parser cannot — hence the `RAW_CASES` check.
- Consistent with sibling scratch: r72-critic's matrix measured the
  identical reorder inside a real pygame parent
  (`corpus/live/r72-critic/pg_reorder-matrix.json`), and r72-boundary's
  edge cells put the reorder→splice flip at the 131072 buffer-fill
  boundary (`corpus/live/r72-boundary/cells.json`) — our HEAD is 5
  bytes, far inside the window.

## Evidence

- `python3 corpus/fixtures/pygame_battery.py --runs
  corpus/live/r72-author/runs` → `totals: cases=55 pass=55 fail=0
  launch_ok=True done_marker=True exit=0`, exit 0, ~11s wall. Three
  reps: `corpus/live/r72-author/runs/pygame-20261014T144428465749Z/`,
  `...T144447211038Z/`, `...T144456346523Z/` — all 55/55; every
  `rord_*`/`self_*` key byte-identical across reps.
- Standalone pre-landing dry run of all five child programs (commands
  and raw wires preserved in
  `corpus/live/r72-author/evidence-notes.md`).
- Prior-row byte-stability: `git diff corpus/fixtures/` shows +173/-1
  (the -1 is the popen_arm env=CHILD_ENV fold; 0 removed CASES rows). Prior-arm key sets and
  stable values identical to r71 receipt
  `corpus/live/runs/pygame-20261014T143255328754Z/probe.stdout.txt`;
  all 36 prior cases still PASS under their original pins — only
  jittered timing fields moved, within pinned bounds.
- Dev-run honesty note: the first authored `reorder_flush` child used
  `sys.stdout.write('HEAD ',flush=True)` — `write()` takes no `flush`
  kwarg; the dry run caught it (`ret=1`, empty wire). Fixed to
  `write()+flush()`; the dry-run discipline is why it never reached a
  battery rep.

## Remaining unknowns / risks

- `rord_bufsize`/`self_bufsize` pin `131072` exactly — this build's
  `io.DEFAULT_BUFFER_SIZE` (py3.14.7); ≤3.13 builds (8192) would fail
  those two keys. Per-build pin, same convention as `whs_bufsize`.
- `reorder_late` is timing-bound: descendant lands ~300ms after the
  ~0ms window close (300ms margin). A >300ms parent stall between
  spawn and flush would flip it to midline — stable 3/3 here, but it
  is the one cell a loaded host could flake.
- The self cell is regime-honest rather than regime-pinned at the
  source: under a tty the probe's own wire would legitimately show
  midline (line-buffered). The battery always captures via pipe, so
  `self_wire_reorders` + `self_fd1_piped=False` pin the pipe regime;
  `fd1_isatty` is emitted precisely to record which regime ran.
- Hybrid "descendant lands between flushed chunks of a crossing write"
  (xconnector prediction iii) is not pinned: interleaving the spawn
  inside a >131072B flush is nondeterministic at fixture level;
  r72-boundary's `paced2`/`cross_after_child` cells already measured
  the infix shape in scratch.
- Godot/LOVE batteries untouched; no git mutations; commits remain
  operator-owned.
