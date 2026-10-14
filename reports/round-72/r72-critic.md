# game-dev-2d round 72 — critic (pre-landing attack on the reorder arm)

Seat: critic | Lane: g2d | Round: 72 | Host: devin — CPython 3.14.7,
pygame 2.6.1 classic (SDL 2.32.72), 32 cores, compositor present.

Audit snapshot 2026-10-14T14:38:38Z: **no tracked r72 artifact had landed**
(`git rev-parse HEAD` → `44127af` = r71 report-last; `git status` shows no
`corpus/fixtures` or `reports/round-72` delta). The concrete design under
attack is therefore the briefed MOVE (`g2d-critic.txt:10-12`) plus the
xconnector X1 claim text (`.ufo/waves/shokunin-train-20261101-w11/
xconnector.md:31-69`), instrumented in the shape the in-flight sibling
seats already use (scout `reorder_selfcontained.py`, verifier
`reorder_cells.json`, boundary `capture.json`). Tracked-fixture
provenance at snapshot: `pygame_probe.py`
sha256 `4d426a3ba6098186c8ef4d6c6cdf6e4e8ecd17dc7af3828ceb91ccb510bb4738`,
`pygame_battery.py` sha256
`0a579819658ee9be9dbd3e6fb81414a036f712a5d03358c7b57a8481a2cec47f`
(`provenance.txt`). All commands from the lane repo root; scratch and
receipts in `corpus/live/r72-critic/`; no sibling artifact modified (the
patched probe/battery are copies).

## Verdict summary

**The composition is real and transfers to the pygame process — but the
briefed discriminator is falsified as worded.** 13/13 measured cells are
byte-identical between a bare CPython parent and a headless pygame parent
(`reorder_demo-matrix.json` == `pg_reorder-matrix.json`), and the
insertion-only arm shape keeps the landed battery 36/36. The spawned
descendant's buffering mode does **not** pick the topology: a `-u`
descendant under a buffered head-writer still reorders, and a buffered
descendant under a `-u` head-writer still splices midline. The variable
that flips the topology is the **fd1-owner / HEAD-writer's** stdio mode.
Landable with pin corrections: name that referent, pin the probe's own
mode against ambient `PYTHONUNBUFFERED`, add a raw-order case type + a
`-u` control run, and keep the spawn synchronous.

## F1 — HIGH: wrong referent — the descendant's mode is not the discriminator

Brief wording: "pin: buffered child -> prefix/reorder topology; flushed/-u
child -> midline splice". Measured (parent = the process that writes
HEAD/TAIL into the inherited fd1; child = the spawned descendant; capture
= pipe, the battery's `capture_output=True` path):

| HEAD-writer mode | descendant | wire bytes | topology |
|---|---|---|---|
| buffered | `sh printf` (write-through) | `CHILD\nHEAD\nTAIL\n` | **reorder** |
| buffered | buffered `python3 -c` | `CHILD\nHEAD\nTAIL\n` | **reorder** |
| buffered | `python3 -u -c` | `CHILD\nHEAD\nTAIL\n` | **reorder** |
| buffered | slow buffered `python3 -c` (sleep .3) | `CHILD\nHEAD\nTAIL\n` | **reorder** |
| `-u` | `sh printf` | `HEAD\nCHILD\nTAIL\n` | midline |
| `-u` | buffered `python3 -c` | `HEAD\nCHILD\nTAIL\n` | midline |
| `-u` | `python3 -u -c` | `HEAD\nCHILD\nTAIL\n` | midline |
| `PYTHONUNBUFFERED=1` | `sh printf` | `HEAD\nCHILD\nTAIL\n` | midline |
| buffered | backgrounded, writes at 0.3 s, flushed at ~0.05 s | `HEAD\nTAIL\nCHILD\n` | append |
| buffered | backgrounded, no intermediate flush | `CHILD\nHEAD\nTAIL\n` | reorder |

Same 13 rows for a pygame-headless parent, byte-identical (receipts:
`reorder_demo-matrix.json`, `pg_reorder-matrix.json`; drivers
`reorder_demo.py`, `pg_reorder.py`, `matrix.py`).

So, read literally (child = descendant): "flushed/-u child → midline" is
false (4 buffered-writer cells with `-u`/buffered descendants all
reorder), and "buffered child → reorder" is false (buffered descendants
under a `-u` writer all splice midline). Read as "child = the probe
process, descendant = the spawned writer" the wording is correct but
ambiguous — and that ambiguity is the defect: a future port can implement
the descendant-mode sweep and land a wrong-sign verdict. The in-flight
sibling design (scout `reorder_selfcontained.py:96-101`, verifier
`reorder_cells.json`) already varies the **writer** mode — correct; the
landed claim text and receipt keys must say so explicitly.

**Impacted axes:** depth (the pinned law would name the wrong mechanism),
calibration (referent of the variable), verdict integrity (wrong-sign
risk).

**Smallest safe correction:** state the law as "the topology is set by
the stdio mode of the fd1 owner that writes the head (the probe process
for the self arm; the spawned writer for a nested arm)"; label the
descendant as the write-through seam vehicle; any descendant-mode sweep
is a timing cell (below), not a topology cell.

## F2 — HIGH: the topology has three referents; two boundary cells and one capture trap are unpinned

1. **Capture medium.** pty capture of the same cell → **midline for both
   parent modes** (line-buffered flush on `\n`); file redirect → reorder
   (buffered) / midline (`-u`) — identical to the pipe. Receipts:
   `capture-medium.txt` (`script -qec` od dumps), `file-capture.txt`,
   `file-capture-u.txt`. The landed runner is safe by construction
   (`pygame_battery.py:108` `capture_output=True` = pipe), but the claim
   "byte ORDER is a language-layer property" is only true given a
   non-tty capture; a pty-based runner produces a false negative.
2. **Window-closed cell.** buffered writer + explicit flush after TAIL +
   backgrounded descendant writing at 0.3 s → `HEAD\nTAIL\nCHILD\n`
   (append) — the window is `[head write, first flush]`, not wall-ms and
   not `io.DEFAULT_BUFFER_SIZE`. A synchronous spawn (`os.system` /
   `subprocess.run`, the natural arm shape) is deterministic and immune;
   a gap/backgrounded shape can miss the window (the Godot/LOVE
   "offset > gap" analogue) and is load-flaky. Receipts: the two `bg`
   rows above.

**Impacted axes:** coverage (boundary cells), verdict integrity (false
negative under pty capture), calibration (window referent).

**Smallest safe correction:** pin the arm's spawn as synchronous; record
the capture medium in the battery payload (or assert it — pipe); if a
window-closed cell is added, mark it documentation-only with timing
bounds.

## F3 — HIGH: false-provenance — the probe's stdio mode is ambient, so the new pin flips on a `PYTHONUNBUFFERED` host

`pygame_battery.py:104-117` builds the probe env from `os.environ` +
`PROBE_ENV` (`:42-46`); nothing strips `PYTHONUNBUFFERED` for the probe
run. The probe strips it only for its own withhold children
(`pygame_probe.py:59`). Measured through the battery's exact capture path
with a patched probe copy (`battery_like.py` → `probe-copy-check.json`):

| probe env | topology | raw |
|---|---|---|
| clean (host: unset) | **reorder** | `REORDER-CHILD` idx 1295 < `REORDER-HEAD` 1309 |
| `PYTHONUNBUFFERED=1` | **midline** | `REORDER-HEAD` < `REORDER-CHILD` < `REORDER-TAIL` |
| `-u` | **midline** | same |

Prior keys identical in all three runs (`driver=dummy`,
`withhold_small bufsize=131072`, `pump_needed=false`). r71-critic F4
(`reports/round-71/r71-critic.md:154-176`) closed this class for the
spawned children; r72 reopens it for the probe itself. Measured env
semantics on this build: `PYTHONUNBUFFERED` ∈ {`0`,`00`,``} → buffered,
{`1`,`x`,`true`} → unbuffered — so do **not** neutralize with `0`
(the ≤3.13 "non-empty string" rule would make `0` unbuffered); strip the
variable for the buffered run.

**Impacted axes:** verdict integrity (false-provenance failure), evidence
sufficiency (env conditionality of the new pin).

**Smallest safe correction:** build the reorder-run probe env explicitly
(strip `PYTHONUNBUFFERED` for the buffered run; set it or pass `-u` for
the midline control) and record `probe_stdio=buffered|unbuffered` in
`verdicts.json`.

## F4 — MEDIUM: the CASES model cannot express an order relation; marker design trap

`pygame_battery.py:175-185` evaluates `arms.get(arm, {}).get(key)` — a
key=value model; the reorder claim is a byte-order relation on the raw
stdout, so it needs a new raw predicate (precedent: r67's
`raw_stdout.endswith` pin). Corroborated in-flight: boundary
`capture.json` shows the non-newline marker shape makes the fused line
unparseable (`arm_line_parseable:false`; delivered
`INJECTEDHEAD  TAIL\n`), while newline markers keep the ARM line
parseable. My probe copy (`pygame_probe_reorder.py`, arm inserted before
`pygame.quit()` at `pygame_probe.py:237`) shows the same: with newline
markers the reorder evidence lives only in the raw stream
(`probe-copy.clean.stdout.txt`), and the arm's own `PYGAME-ARM reorder`
line parses normally. Note the xconnector's demo shape (inline markers,
no newline) reproduces exactly as `CHILDHEAD  TAIL` (inline row in both
matrices).

**Impacted axes:** coverage (the claim would be unexpressed/untested),
verdict integrity (fused-line parse skip).

**Smallest safe correction:** add a raw-order case type — needles +
run tag, evaluated on the captured `stdout`: clean run
`find(child) < find(head)`; `-u` control run
`find(head) < find(child) < find(tail)`. Newline-terminate the reorder
markers and keep them non-ARM lines (the arm deliberately withholds; all
other emits stay `flush=True` so the ARM parse is unaffected).

## F5 — LOW: "language-layer property" is writer-side stdio buffering (libc-level)

`c_reorder.c` (same parent role in C): default fully-buffered pipe →
`CHILD\nHEAD\nTAIL\n` (reorder); `flush-head` → `HEAD\nCHILD\nTAIL\n`
(midline); 3/3 stable (`c-matrix.txt`). The topology is a property of any
fd1 writer whose stdio buffers — CPython is this lane's instance, not the
mechanism's owner. Consistent with the xconnector's own row naming
("language (stdio)", `xconnector.md:20`), but the round-72 claim text
should not imply Python-specificity (bpy's `-b -P` print path is the
already-declared risk, `xconnector.md:235-238`).

**Impacted axes:** calibration (mechanism naming), discernment/depth
(cross-runtime prediction).

## F6 — INFO: transfer and insertion-only safety confirmed

- 13/13 cells byte-identical bare CPython vs headless pygame parent.
- Patched probe copy through the battery's exact capture: clean →
  reorder; `-u` → midline; prior spot keys unchanged.
- Battery copy with the arm inserted (`pygame_battery_reorder.py`):
  **36/36 PASS** (`runs-insertion/pygame-20261014T143730775873Z/
  verdicts.json`), and **36/36 PASS** with the probe forced `-u` via a
  `--python` wrapper (`runs-unbuffered-control/
  pygame-20261014T143804184569Z/verdicts.json`; midline visible at
  `probe.stdout.txt:10-12`). Prior rows are stdio-mode invariant, so a
  second control run is safe.

## Over-strong claim audit (not falsifications, wording scopes)

- "one window family" holds only as *one withholding-interval family*:
  the splice window closes at the tail write (gap-relative wall-ms), the
  reorder window closes at the first flush (buffer lifetime/exit) — the
  xconnector text already carries the bound difference
  (`xconnector.md:38-40`); the round-72 wording must not flatten it.
- "the seam is spawn-layer" is true (fd inheritance); *observability*
  additionally requires a non-tty capture (F2).
- No new constant should be introduced for this arm: its window's closing
  edge is "first flush", not `io.DEFAULT_BUFFER_SIZE` (a crossing write
  is merely one way to flush). Keep `131072` as the r71 host-provenance
  row only; the xconnector's "carry `default_buffer_size` per receipt"
  rule (`xconnector.md:181-186`) already covers it.

## Reproduce

```
cd corpus/live/r72-critic
python3 matrix.py reorder_demo.py            # 13 cells, host parent
python3 matrix.py pg_reorder.py              # 13 cells, pygame parent
python3 probe_patch.py && python3 battery_like.py
python3 pygame_battery_reorder.py --runs runs-insertion
python3 pygame_battery_reorder.py --python "$PWD/pyu_wrapper.sh" --runs runs-unbuffered-control
gcc -O0 -o c_reorder c_reorder.c && ./c_reorder | od -c
script -qec "python3 reorder_demo.py --child printf" /dev/null | od -c   # pty capture
python3 -c "import io; print(io.DEFAULT_BUFFER_SIZE)"                    # 131072
```

Receipts: `reorder_demo-matrix.json`, `pg_reorder-matrix.json`,
`probe-copy-check.json`, `probe-copy.{clean,pythonunbuffered,u_flag}.stdout.txt`,
`runs-insertion/…/verdicts.json`, `runs-unbuffered-control/…/verdicts.json`,
`capture-medium.txt`, `c-matrix.txt`, `file-capture{,-u}.txt`,
`provenance.txt`.

## Bottom line

Fixable defects, not a reject: the composition reproduces on both
surfaces and the seam claim survives. Land the arm with (1) the
HEAD-writer/fd1-owner stdio mode as the pinned variable (not the
descendant's), (2) a raw-order predicate plus a `-u` control run for the
midline cell, (3) `PYTHONUNBUFFERED` stripped from the buffered run and
recorded, and (4) synchronous spawn + newline markers. The strongest
counterexample available on this host — a `-u` descendant under a
buffered writer still reordering (and a buffered descendant under a `-u`
writer still splicing) — is measured and holds 4/4 cells on both the bare
interpreter and the pygame process.
