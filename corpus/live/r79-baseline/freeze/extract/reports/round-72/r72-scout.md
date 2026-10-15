# game-dev-2d round 72 — scout: reorder-fabrication pre-measurement (xconnector X1, composed mechanism)

Seat: scout | Lane: g2d | Round: 72 | Wave: shokunin-train-20261101-w12.
Host: devin — CPython **3.14.7** (GCC 16.1.1), pygame 2.6.1 (SDL 2.32.72),
32 cores; `io.DEFAULT_BUFFER_SIZE = 131072`; `PYTHONUNBUFFERED` unset;
`sys.stdout.isatty() = False`. Repo `~/Projects/shokunin/game-dev-2d-shokunin`
at HEAD `44127af`; tracked fixtures at r71 hashes (probe
`4d426a3ba6098186…`, battery `0a579819658ee9be…` — sha256, `sha256sum`
this seat). No tracked file touched. Scratch + receipts:
`corpus/live/r72-scout/` only.

**`lsp` disclosure.** No `lsp` device is exposed in this seat's toolset
(and none on PATH per the in-flight r72-boundary check): every trace below
is a process-level measurement plus textual `file:line` citations and a
fetched-source read — literal fallback, recorded; not presented as
semantic proof.

**Concurrency.** r72-boundary / r72-critic / r72-scribe landed in flight
while this seat ran; where they independently cover a cell it is cited as
in-flight, not as landed truth. This report's claims stand on its own
receipts.

## Headline

The briefed composition **reproduces end-to-end in the pygame process**:
a spawned descendant writing into inherited fd1 mid-window lands BEFORE
the fd1-owner's earlier buffered bytes (prefix/reorder) when the owner
block-buffers stdout, and the stream collapses to the LOVE/Godot midline
splice when the owner flushes through. Three deltas change how the arm
must be built: **D1** the discriminating variable is the **fd1-owner's**
stdio mode ("buffered child" is true only when *child* = the probe as
battery-child; the descendant's own mode does not flip topology), **D2** a
third topology class exists — **suffix** — and a non-synchronous spawn
lands there 3/3, **D3** the window's close condition is the binary
layer's fast-path branch (`len <= avail && len < buffer_size`), not
"fill ≥ 131072" (source-traced, 6/6 structure-cell model match).

## 1. Independent replication of the xconnector demo (observed)

`.ufo/waves/shokunin-train-20261101-w11/xconnector.md:46-49` reproduced
byte-for-byte on this host (`receipts/demo_replicate.txt`):

```
python3   -c '…write("HEAD "); os.system("printf INJECTED"); write(" TAIL\n")' | cat -A
   → INJECTEDHEAD  TAIL$                    (reorder)
python3 -u -c '<same>' | cat -A
   → HEAD INJECTED TAIL$                    (midline splice)
python3   -c 'print("HEAD ",end="",flush=True); …' | cat -A
   → HEAD INJECTED TAIL$                    (flush collapses the window)
```

Same byte-level shape via `subprocess` fd1 inheritance instead of
`os.system` (`receipts/c6_popen_inherit.txt`): `INJECTEDHEAD  TAIL$`.
Descendant shares the owner's pipe inode, not a private pipe
(`receipts/mechanism_cells.txt` C2):
`P-FD1=pipe:[12977349]` / `C-FD1=pipe:[12977349]`
(`readlink /proc/self/fd/1` in both processes).

## 2. Topology map — what discriminates (observed, 3/3 stable)

Scratch probe `reorder_mini.py` (pygame import + `init()` +
`set_mode` dummy, markers `PHASE0`→`R-HEAD`(unflushed)→descendant
`R-INJ`(inherited fd1)→hold 0.3 s→`R-TAIL`+flush) read by
`reorder_harness.py` (raw `os.read`+`select`, no reader-side stdio).
Receipts: `receipts/harness_core.txt`, `receipts/harness_variants.txt`,
`receipts/repetition.txt` (3/3 identical indices per cell).

| fd1-owner mode | descendant | topology | observed raw stdout |
|---|---|---|---|
| buffered (pipe/file) | `sh printf` write-through | **reorder** | `…PHASE0\nR-INJ\nR-HEAD\nR-TAIL\n` |
| buffered | `python3 -u` | **reorder** | `…R-INJ\nR-HEAD\nR-TAIL\n` |
| buffered | `python3` block-buffered | **reorder** | `…R-INJ\nR-HEAD\nR-TAIL\n` |
| buffered, `flush` before spawn | any | **splice** | `…R-HEAD\nR-INJ\nR-TAIL\n` |
| `-u` | any | **splice** | `…R-HEAD\nR-INJ\nR-TAIL\n` |
| `PYTHONUNBUFFERED=1` | any | **splice** | `…R-HEAD\nR-INJ\nR-TAIL\n` |
| buffered, descendant not waited (writes at +0.35 s) | `sh` | **suffix** | `…R-HEAD\nR-TAIL\nR-INJ\n` |
| buffered, descendant not waited (immediate) | `sh` | **suffix 3/3** | `…R-HEAD\nR-TAIL\nR-INJ\n` |

- Indices are byte-stable per cell (buffered: `head=45 inj=39 tail=52`;
  `-u`: `head=39 inj=46 tail=52`; 3 reps each, `repetition.txt`).
- The **descendant's** mode never flips the class — a flushed (`-u`) and
  a block-buffered descendant both reorder under a buffered owner; the
  descendant's buffer only moves *when* its bytes land inside the window.
- **Suffix** is the third class: a descendant writing after the owner's
  flush/exit lands after the tail (`mechanism_cells.txt` C1 exit-flush
  still reorders: `R-INJ,R-HEAD,R-TAIL`; C3 buffered-descendant-no-wait
  and C4 immediate-sh-no-wait → `R-HEAD,R-TAIL,R-INJ`, C4 3/3). An arm
  that does not wait for its descendant is a race it loses.
- Byte-level markers merge tokens into one line (`harness_variants.txt`
  V3): raw `R-INJR-HEAD  R-TAIL\n` — the xconnector shape — vs the
  newline form which keeps lines intact. `pygame_battery.py:101`
  anchors `^PYGAME-ARM`, so raw markers are invisible to `parse_arms`
  either way; a battery order assertion is required (D5).

## 3. Streaming hazard confirmed at read-event level (observed)

Buffered owner, harness timeline (`harness_core.txt`):
`[(445.45, 39), (446.21, 6), (746.32, 14)]` — the descendant's `R-INJ`
was readable at **446.21 ms while the owner was still alive**
(`alive_at_first=True`), and the owner's `R-HEAD`+`R-TAIL` only at
**746.32 ms** (its flush). A streaming consumer sees fabricated order,
not a post-exit artifact — the xconnector verdict-integrity hazard class
(`xconnector.md:66-69`), now measured at the read-event level.

## 4. Window mechanics — source-traced, model 6/6 (observed + source)

The window is the fd1-owner's stdio withholding window (same family as
r71's withhold arm, `reports/round-71/r71-scout.md:58-68`), observed via
the descendant seam. Exact close condition, CPython 3.14.7 sources
fetched from the `v3.14.7` tag (sha256 `textio.c 21d8942c200ac732…`,
`bufferedio.c f0d51b023ff00667…`; installed build = 3.14.7/GCC 16.1.1;
the model below reproduces 6/6 measured cells, so it is corroborated,
not merely cited):

- text layer: a write with `bytes_len >= chunk_size` (8192) first flushes
  the pending batch as **its own** binary write, then writeflushes the new
  data as a second one (`textio.c:1743`, `:1790`); `_textiowrapper_writeflush`
  hands the whole pending over in **one** `buffer.write()` (`textio.c:1645`).
- binary layer fast path: buffer iff `len <= avail && len < buffer_size`
  (`bufferedio.c:2103-2104`); otherwise the buffered prefix is flushed to
  the wire (`:2117`), the incoming data is direct-written in
  `buffer_size` chunks, and a `< buffer_size` tail is re-buffered (`:2173+`).
  **The released bytes are the buffered prefix — the window closes on the
  first binary write that fails the fast path.**

Structure map, same descendant observable (`receipts/boundary_pair.txt`,
`receipts/boundary_struct.txt`; E = 131072):

| structure | pending total | verdict |
|---|---|---|
| no prior, one write of E | E | released (big-first) — r71 exact-equality cell |
| no prior, one write of E-1 | E-1 | withheld |
| `R-HEAD` + one write of E-7 | E | withheld (two binary writes: 7, then E-7) |
| `R-HEAD` + one write of E-6 | E+1 | released **head-first** (prefix = HEAD; `inj_idx=7`) |
| `R-HEAD` + 60000 + (E-7-60000) | E | withheld |
| `R-HEAD` + 60000 + (E-6-60000) | E+1 | released head-first; prefix = HEAD+60000, `R-INJ` lands **between** prefix and tail (`inj_idx=60007`) |

Consequence for the arm: a small unflushed HEAD stays in the text layer
until flush/exit; a later ≥8192 text write flushes HEAD first as its own
binary write (`textio.c:1743`), while a later sub-8192 write is coalesced
with it into one binary write (`textio.c:1790`). The window
is not wall-ms and not "fill ≥ 131072" but the fast-path branch above.
The r71 lattice cells (`seg_64k_64k` withheld; withheld line released at
the crossing write; single write of exactly 131072 released) all fall out
of the same model.

## 5. Probe-context insertion pre-check (observed)

`probe_copy.py` = landed fixture + an own-fd1 reorder block (8
statements/comments + blank separators, 10 lines) inserted
before `pygame.quit()` (`corpus/fixtures/pygame_probe.py:237`) by
`make_probe_copy.py` — insertion-only; fixture sha256 unchanged. Run in
the battery's capture shape (non-tty stdout, `receipts/probe_copy.*`):

| probe mode | observed region (end of stdout) | topology |
|---|---|---|
| buffered | `…pump_needed=false\nR-INJ\nR-HEAD\nR-TAIL\nPYGAME_PROBE_DONE\n` | reorder (`inj@1298 < head@1304`) |
| `-u` | `…pump_needed=false\nR-HEAD\nR-INJ\nR-TAIL\nPYGAME_PROBE_DONE\n` | splice (`head@1296`) |
| `PYTHONUNBUFFERED=1` | `…R-HEAD\nR-INJ\nR-TAIL\n…` | splice (`head@1301`) — **env trap** |

All three runs: exit 0, `PYGAME_PROBE_DONE`, **9 `PYGAME-ARM` arms / 69
keys with identical key sets and identical non-timing values** (only
wall-clock keys differ). The insertion is additive; the reorder itself is
detectable only by a raw-order assertion (the marker lines are not ARM
lines).

## 6. Arm-shape pre-measurement (observed)

- **Self-contained shape** (`reorder_selfcontained.py`): the probe spawns
  writer copies with `stdout=PIPE` and reads their order; measured ORDER
  lines, 3× stable, identical for pygame-importing and plain writers
  (`receipts/selfcontained_v2.txt`):
  `writer=buffered topology=reorder` (`head=37 inj=31 tail=44`),
  `writer=unbuffered_u topology=splice` (`31/38/44`),
  `writer=env_unbuffered topology=splice`. Fits the battery CASES model
  (one ARM line, space-free values); no second probe invocation needed.
- **Own-fd1 shape** (brief wording; §5): matches "descendant writes into
  the probe's inherited fd1", but the probe cannot self-report its own
  fd1 order — the battery needs a raw-order assertion plus a second
  `-u` invocation (or a self-contained writer copy) for the splice
  control.
- **Env provenance**: writer copies must get a scrubbed env like the
  landed `CHILD_ENV` (`pygame_probe.py:59`) — with
  `PYTHONUNBUFFERED=1` in the parent env, the "buffered" writer cell
  collapses to splice (`receipts/env_trap.txt`). The probe's own mode is
  ambient; the battery must strip or pin it.
- **Capture medium**: non-tty required — file redirect reorders
  (`receipts/v8_fileredirect.out`), tty (`script -qec`) is line-buffered
  → splice with `isatty=1` (`receipts/env_provenance.txt`). The battery's
  `capture_output=True` pipe (`pygame_battery.py:104-117`) is the right
  medium.
- **Related, distinct mechanism** (do not conflate): text-pending +
  raw `sys.stdout.buffer.write(≥bufsize)` inverts with no spawn at all —
  `140000×B` then `X-HEAD` (`receipts/cross_layer.txt`), the r71-critic
  `mixed_invert` class (`reports/round-71/r71-critic.md:231-236`). The
  reorder arm must stay single-layer.

## 7. Deltas vs the brief

1. **D1 — referent.** "buffered child → prefix/reorder; flushed/-u child →
   midline splice": the flipping variable is the fd1-owner's stdio mode
   (§2); with *child* = the probe as battery-child the wording is exact,
   with *child* = the spawned descendant it is wrong-sign. (In-flight
   r72-critic F1 and r72-boundary F1 measured the same grid independently.)
2. **D2 — third class + determinism.** Suffix exists; an unwatched spawn
   loses the race 3/3 (§2 C3/C4). Spawn synchronously (wait for the
   descendant) or the arm is load-flaky.
3. **D3 — window close condition.** Fast-path branch, not fill (§4);
   released bytes are the buffered prefix (H2: INJ between prefix and
   tail). Pin the crossing cells by structure, not by a hardcoded total.
4. **D4 — provenance conditions.** Non-tty stdout and no ambient
   `PYTHONUNBUFFERED` (§5/§6); both flip the pin without a runtime
   difference.
5. **D5 — marker/parse.** Byte-level markers merge the descendant token
   into the neighbouring line; raw markers are invisible to the anchored
   ARM parser; an order assertion (or the self-contained ORDER line) is
   required (§2, §5; in-flight r72-boundary F6 / r72-critic F4 cover the
   battery-side variants).
6. **D6 — arm shape.** Self-contained ORDER design is env-robust and
   battery-native; own-fd1 design needs battery-side raw order + a `-u`
   control invocation (§6).
7. **D7 — scope of "language-layer".** Confirmed inside a pygame process
   (pygame import/init does not move it; plain vs pygame writers give the
   same order and indices, §6); the mechanism is writer-side stdio
   buffering — the source trace here is CPython 3.14.7, transfer to
   bpy/other runtimes remains the g3d arm's to measure.

Composition claim verdict: **CONFIRMED as composition** — seam =
spawn-layer fd1 inheritance (descendant shares the owner's pipe inode,
§1), order = writer's stdio withholding; one window family (the same
window the r71 withhold arm measured, now observed via the descendant
seam). Refinements D1–D3 above are the deltas.

## 8. Receipts + reproduce

Receipts under `corpus/live/r72-scout/`:
`receipts/demo_replicate.txt`, `c6_popen_inherit.txt`,
`harness_core.txt`, `harness_variants.txt`, `repetition.txt`,
`mechanism_cells.txt`, `boundary_pair.txt`, `boundary_struct.txt`,
`selfcontained.txt`, `selfcontained_v2.txt`, `env_trap.txt`,
`env_provenance.txt`, `v8_fileredirect.out`, `cross_layer.txt`,
`probe_copy.{buffered,unbuffered,envunbuf}.txt|.err`.
Scripts: `reorder_mini.py`, `reorder_harness.py`,
`reorder_selfcontained.py`, `boundary_pair.py`, `boundary_struct.py`,
`make_probe_copy.py`, `probe_copy.py` (scratch copy of the landed fixture;
tracked fixture untouched).

```
python3 reorder_harness.py --            # buffered  → reorder
python3 reorder_harness.py --unbuf --    # -u        → splice
python3 reorder_harness.py -- --flush-head     # splice (window collapsed)
python3 reorder_harness.py -- --child=pyu      # reorder (descendant mode irrelevant)
python3 reorder_harness.py -- --child=pyb      # reorder
python3 reorder_harness.py -- --no-wait        # suffix
python3 reorder_selfcontained.py [--writer-plain]
python3 boundary_pair.py ; python3 boundary_struct.py
python3 make_probe_copy.py && python3 probe_copy.py > out.txt        # reorder
python3 -u probe_copy.py > out.txt                                   # splice
PYTHONUNBUFFERED=1 python3 probe_copy.py > out.txt                   # splice
```

Source anchors: CPython `v3.14.7` `Modules/_io/textio.c:1645,1743,1790`,
`Modules/_io/bufferedio.c:2103-2104,2117,2173` (fetched raw, sha256 in §4);
`corpus/fixtures/pygame_probe.py:55,59,62-64,237-238`;
`corpus/fixtures/pygame_battery.py:49-99,101,104-117,120-129`;
`corpus/live/r70-critic/splice_probe/main.lua:25-30` (LOVE head flushed →
midline); `xconnector.md:31-69`; `reports/round-71/r71-critic.md:31-75`.

## 9. Confidence / remaining unknowns

- **High (own receipts, reps)**: host-demo replication; topology map and
  the owner-mode discriminator; suffix class and no-wait race; streaming
  hazard timeline; fd1 identity; window close condition (source + 6/6
  model match); probe-context insertion behavior and env/tty traps;
  self-contained ORDER shape 3/3.
- **Moderate**: the CPython source fetched from the `v3.14.7` tag matches
  the installed build only empirically (6/6 cells); the exact arm/battery
  design is the author's — both measured options are recorded here.
- **Unresolved**: bpy (`-b -P`) transfer (g3d arm); loaded-host timing
  bounds for the arm's cells (this seat used order-only observables — by
  construction load-independent, but not stress-run); whether the author
  lands the own-fd1 or self-contained shape.
